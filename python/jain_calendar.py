#!/usr/bin/env python3
"""
Tithika Jain calendar adapter.

Implements a transparent Kartikadi Amanta Jain/Gujarati-style civil-religious
calendar profile on top of Tithika's Lahiri Panchang. Jain traditions can vary;
the response identifies this convention instead of presenting it as universal.
"""
from __future__ import annotations

import calendar
import json
import sys
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import festival_rules
import panchang

ENGINE_VERSION = "0.1.0"

JAIN_MONTHS = {
    "Chaitra": "Chaitra",
    "Vaishakha": "Vaishakh",
    "Jyeshtha": "Jeth",
    "Ashadha": "Ashadh",
    "Shravana": "Shravan",
    "Bhadrapada": "Bhadarvo",
    "Ashwina": "Aaso",
    "Kartika": "Kartak",
    "Margashirsha": "Magsar",
    "Pausha": "Posh",
    "Magha": "Maha",
    "Phalguna": "Fagan",
}


def canonical_month(value: str | None) -> tuple[str, bool]:
    raw = str(value or "")
    adhika = raw.startswith("Adhika ")
    return raw.replace("Adhika ", ""), adhika


def jain_new_year(year: int, lat: float, lon: float, tz: ZoneInfo, hour24: bool) -> date:
    diwali = festival_rules.calculate_event("diwali", year, lat, lon, tz, hour24)
    start = date.fromisoformat(diwali["date"])
    for offset in range(1, 5):
        candidate = start + timedelta(days=offset)
        sunrise = panchang.rise_set(
            candidate, lat, lon, tz,
            panchang.astronomy.Body.Sun,
            panchang.astronomy.Direction.Rise,
        )
        if not sunrise:
            continue
        state = panchang.state_at(sunrise)
        if state["paksha"] == "Shukla Paksha" and state["tithi"] == "Pratipada":
            return candidate
    raise ValueError("Unable to resolve Kartika Shukla Pratipada after Diwali")


def kartikadi_year(d: date, lat: float, lon: float, tz: ZoneInfo, hour24: bool) -> int:
    # Before Kartika Shukla Pratipada the Kartikadi Vikram year is CE + 56;
    # from the Jain/Gujarati New Year onward it becomes CE + 57.
    return d.year + (57 if d >= jain_new_year(d.year, lat, lon, tz, hour24) else 56)


def calculate_month(selected: date, lat: float, lon: float, tz: ZoneInfo, hour24: bool):
    _, count = calendar.monthrange(selected.year, selected.month)
    new_year_cache = {}
    rows = []
    for day in range(1, count + 1):
        d = selected.replace(day=day)
        sunrise = panchang.rise_set(
            d, lat, lon, tz,
            panchang.astronomy.Body.Sun,
            panchang.astronomy.Direction.Rise,
        )
        sunset = panchang.rise_set(
            d, lat, lon, tz,
            panchang.astronomy.Body.Sun,
            panchang.astronomy.Direction.Set,
        )
        if not sunrise or not sunset:
            rows.append({"date": d.isoformat(), "day": day, "available": False})
            continue

        state = panchang.state_at(sunrise)
        month_info = panchang.lunar_month_info(sunrise, state)
        base, adhika = canonical_month(month_info.get("amanta"))
        local = JAIN_MONTHS.get(base, base)

        if d.year not in new_year_cache:
            new_year_cache[d.year] = jain_new_year(d.year, lat, lon, tz, hour24)
        vikram = d.year + (57 if d >= new_year_cache[d.year] else 56)
        vir = vikram + 470

        rows.append({
            "date": d.isoformat(),
            "day": day,
            "weekday": d.strftime("%A"),
            "weekday_short": d.strftime("%a"),
            "available": True,
            "sunrise": sunrise.isoformat(),
            "sunrise_label": panchang.fmt(sunrise, hour24),
            "sunset": sunset.isoformat(),
            "sunset_label": panchang.fmt(sunset, hour24),
            "tithi": state["tithi"],
            "tithi_number": state["tithi_number"],
            "paksha": state["paksha"],
            "nakshatra": state["nakshatra"],
            "nakshatra_pada": state["nakshatra_pada"],
            "moon_rashi": state["moon_rashi"],
            "regional_month": ("Adhika " if adhika else "") + local,
            "canonical_month": month_info.get("amanta"),
            "regional_day": state["tithi_number"],
            "regional_year": vikram,
            "vir_samvat": vir,
            "calendar_basis": "kartikadi-amanta-jain",
            "jain_observance": {
                "aatham": state["tithi_number"] == 8,
                "chaudas": state["tithi_number"] == 14,
                "amavasya": state["tithi"] == "Amavasya",
            },
        })
    return rows


def main():
    payload = json.loads(sys.stdin.read() or "{}")
    lat = float(payload.get("lat", 22.3072))
    lon = float(payload.get("lon", 73.1812))
    if not (-90 <= lat <= 90 and -180 <= lon <= 180):
        raise ValueError("Invalid latitude/longitude")

    timezone_name = payload.get("timezone") or "Asia/Kolkata"
    try:
        tz = ZoneInfo(timezone_name)
    except ZoneInfoNotFoundError:
        timezone_name = "Asia/Kolkata"
        tz = ZoneInfo(timezone_name)

    selected = datetime.strptime(
        payload.get("date") or datetime.now(tz).strftime("%Y-%m-%d"),
        "%Y-%m-%d",
    ).date()
    hour24 = bool(payload.get("hour24", False))
    rows = calculate_month(selected, lat, lon, tz, hour24)

    print(json.dumps({
        "ok": True,
        "variant": "jain",
        "year": selected.year,
        "month": selected.month,
        "month_name": selected.strftime("%B"),
        "first_weekday": calendar.monthrange(selected.year, selected.month)[0],
        "engine": {
            "name": "tithika-jain-calendar",
            "version": ENGINE_VERSION,
            "basis": "kartikadi-amanta-jain",
            "panchang_version": panchang.ENGINE_VERSION,
            "ayanamsha": "Lahiri / Chitrapaksha",
            "year_systems": ["Kartikadi Vikram Samvat", "Vir Nirvana Samvat"],
        },
        "location": {
            "city": (payload.get("city") or "Current location").strip()[:120],
            "lat": lat,
            "lon": lon,
            "timezone": timezone_name,
        },
        "days": rows,
        "note": (
            "This adapter uses a Kartikadi Amanta Jain/Gujarati-style convention: "
            "the year turns on the sunrise observance of Kartika Shukla Pratipada after Diwali. Vir Samvat is "
            "shown alongside Vikram Samvat. Jain sect, region and published Sangh "
            "calendars can apply additional observance rules."
        ),
    }, ensure_ascii=False))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(json.dumps({
            "ok": False,
            "error": str(exc),
            "code": "JAIN_CALENDAR_FAILED",
        }))
        sys.exit(1)
