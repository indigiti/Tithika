#!/usr/bin/env python3
"""
Tithika Nepali Bikram Sambat calendar adapter.

Conversion is deterministic and offline. Tithika vendors the upstream MIT
calendar facts table, while conversion and Panchang integration are implemented
here. The embedded table marks 2000-2099 BS as official lookup and outer ranges
as Sankranti-estimated, so responses expose the source quality.
"""
from __future__ import annotations

import calendar
import json
import os
import sys
from bisect import bisect_right
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import panchang

ENGINE_VERSION = "0.2.0"
DATA_PATH = os.path.join(os.path.dirname(__file__), "vendor", "nepali_bs_calendar.json")

MONTHS_EN = [
    "Baisakh", "Jestha", "Ashadh", "Shrawan", "Bhadra", "Ashwin",
    "Kartik", "Mangsir", "Poush", "Magh", "Falgun", "Chaitra",
]
MONTHS_NP = [
    "वैशाख", "जेठ", "असार", "साउन", "भदौ", "असोज",
    "कात्तिक", "मंसिर", "पुस", "माघ", "फागुन", "चैत",
]
NEPALI_DIGITS = str.maketrans("0123456789", "०१२३४५६७८९")


def nepali_number(value: int | str) -> str:
    return str(value).translate(NEPALI_DIGITS)


with open(DATA_PATH, "r", encoding="utf-8") as fh:
    DATA = json.load(fh)

START_YEAR = int(DATA["start_year"])
END_YEAR = int(DATA["end_year"])
MONTH_LENGTHS = {int(y): list(map(int, row)) for y, row in DATA["month_lengths"].items()}
BAISAKH_1 = {
    int(y): date.fromisoformat(v) for y, v in DATA.get("baisakh_1_ad", {}).items()
}

_MONTH_STARTS: list[tuple[date, int, int]] = []
for year in range(START_YEAR, END_YEAR + 1):
    start = BAISAKH_1.get(year)
    lengths = MONTH_LENGTHS.get(year)
    if not start or not lengths or len(lengths) != 12:
        continue
    cursor = start
    for month, days in enumerate(lengths, start=1):
        _MONTH_STARTS.append((cursor, year, month))
        cursor += timedelta(days=days)

_MONTH_START_DATES = [x[0] for x in _MONTH_STARTS]


def data_quality(bs_year: int) -> str:
    return "official-lookup" if 2000 <= bs_year <= 2099 else "sankranti-estimated"


def ad_to_bs(d: date) -> dict:
    if not _MONTH_STARTS or d < _MONTH_STARTS[0][0]:
        raise ValueError("Gregorian date is before the embedded Bikram Sambat range")

    idx = bisect_right(_MONTH_START_DATES, d) - 1
    if idx < 0 or idx >= len(_MONTH_STARTS):
        raise ValueError("Gregorian date is outside the embedded Bikram Sambat range")

    start, year, month = _MONTH_STARTS[idx]
    length = MONTH_LENGTHS[year][month - 1]
    day = (d - start).days + 1
    if day > length:
        raise ValueError("Gregorian date is beyond the embedded Bikram Sambat range")

    return {
        "year": year,
        "month": month,
        "day": day,
        "month_name": MONTHS_EN[month - 1],
        "month_name_nepali": MONTHS_NP[month - 1],
        "date_nepali": f"{nepali_number(year)}-{nepali_number(f'{month:02d}')}-{nepali_number(f'{day:02d}')}",
        "data_quality": data_quality(year),
    }


def bs_to_ad(year: int, month: int, day: int) -> date:
    if year not in MONTH_LENGTHS or not 1 <= month <= 12:
        raise ValueError("Unsupported Bikram Sambat year/month")
    length = MONTH_LENGTHS[year][month - 1]
    if not 1 <= day <= length:
        raise ValueError("Invalid Bikram Sambat day")
    start = BAISAKH_1.get(year)
    if not start:
        raise ValueError("Baisakh 1 anchor unavailable")
    return start + timedelta(days=sum(MONTH_LENGTHS[year][:month - 1]) + day - 1)



def calculate_day(selected: date, lat: float, lon: float, tz: ZoneInfo, hour24: bool):
    bs = ad_to_bs(selected)
    sunrise = panchang.rise_set(
        selected, lat, lon, tz,
        panchang.astronomy.Body.Sun,
        panchang.astronomy.Direction.Rise,
    )
    sunset = panchang.rise_set(
        selected, lat, lon, tz,
        panchang.astronomy.Body.Sun,
        panchang.astronomy.Direction.Set,
    )
    next_sunrise = panchang.rise_set(
        selected + timedelta(days=1), lat, lon, tz,
        panchang.astronomy.Body.Sun,
        panchang.astronomy.Direction.Rise,
    )
    if not sunrise or not sunset or not next_sunrise:
        raise ValueError("Sunrise/sunset unavailable for this latitude/date")

    state = panchang.state_at(sunrise)
    moonrise = panchang.rise_set(
        selected, lat, lon, tz,
        panchang.astronomy.Body.Moon,
        panchang.astronomy.Direction.Rise,
    )
    moonset = panchang.rise_set(
        selected, lat, lon, tz,
        panchang.astronomy.Body.Moon,
        panchang.astronomy.Direction.Set,
    )
    muhurtas = panchang.daily_muhurtas(
        selected, sunrise, sunset, next_sunrise,
        lat, lon, tz, hour24,
    )
    tithi_end = panchang.find_transition(
        sunrise, next_sunrise, "tithi_id", state["tithi_id"]
    )
    nakshatra_end = panchang.find_transition(
        sunrise, next_sunrise, "nakshatra_id", state["nakshatra_id"]
    )
    yoga_end = panchang.find_transition(
        sunrise, next_sunrise, "yoga_id", state["yoga_id"]
    )
    karana_end = panchang.find_transition(
        sunrise, next_sunrise, "karana_id", state["karana_id"]
    )

    return {
        "date": selected.isoformat(),
        "weekday": selected.strftime("%A"),
        "available": True,
        "sunrise": sunrise.isoformat(),
        "sunrise_label": panchang.fmt(sunrise, hour24),
        "sunset": sunset.isoformat(),
        "sunset_label": panchang.fmt(sunset, hour24),
        "moonrise": moonrise.isoformat() if moonrise else None,
        "moonrise_label": panchang.fmt(moonrise, hour24),
        "moonset": moonset.isoformat() if moonset else None,
        "moonset_label": panchang.fmt(moonset, hour24),
        "tithi": state["tithi"],
        "tithi_number": state["tithi_number"],
        "paksha": state["paksha"],
        "tithi_end": tithi_end.isoformat() if tithi_end else None,
        "tithi_end_label": (
            panchang.transition_label(tithi_end, selected, hour24)
            if tithi_end else None
        ),
        "nakshatra": state["nakshatra"],
        "nakshatra_pada": state["nakshatra_pada"],
        "nakshatra_end": nakshatra_end.isoformat() if nakshatra_end else None,
        "nakshatra_end_label": (
            panchang.transition_label(nakshatra_end, selected, hour24)
            if nakshatra_end else None
        ),
        "yoga": state["yoga"],
        "yoga_end_label": (
            panchang.transition_label(yoga_end, selected, hour24)
            if yoga_end else None
        ),
        "karana": state["karana"],
        "karana_end_label": (
            panchang.transition_label(karana_end, selected, hour24)
            if karana_end else None
        ),
        "moon_rashi": state["moon_rashi"],
        "sun_rashi": state["sun_rashi"],
        "sun_nakshatra": state["sun_nakshatra"],
        "regional_month": bs["month_name"],
        "regional_month_native": bs["month_name_nepali"],
        "regional_day": bs["day"],
        "regional_year": bs["year"],
        "regional_date_native": bs["date_nepali"],
        "calendar_basis": "bikram-sambat-civil",
        "data_quality": bs["data_quality"],
        "muhurtas": muhurtas,
    }

def calculate_month(selected: date, lat: float, lon: float, tz: ZoneInfo, hour24: bool):
    _, count = calendar.monthrange(selected.year, selected.month)
    rows = []
    for day in range(1, count + 1):
        d = selected.replace(day=day)
        bs = ad_to_bs(d)
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
            rows.append({"date": d.isoformat(), "day": day, "available": False, **bs})
            continue
        state = panchang.state_at(sunrise)
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
            "regional_month": bs["month_name"],
            "regional_month_native": bs["month_name_nepali"],
            "regional_day": bs["day"],
            "regional_year": bs["year"],
            "regional_date_native": bs["date_nepali"],
            "calendar_basis": "bikram-sambat-civil",
            "data_quality": bs["data_quality"],
        })
    return rows


def main():
    payload = json.loads(sys.stdin.read() or "{}")
    lat = float(payload.get("lat", 27.7172))
    lon = float(payload.get("lon", 85.3240))
    if not (-90 <= lat <= 90 and -180 <= lon <= 180):
        raise ValueError("Invalid latitude/longitude")

    timezone_name = payload.get("timezone") or "Asia/Kathmandu"
    try:
        tz = ZoneInfo(timezone_name)
    except ZoneInfoNotFoundError:
        timezone_name = "Asia/Kathmandu"
        tz = ZoneInfo(timezone_name)

    selected = datetime.strptime(
        payload.get("date") or datetime.now(tz).strftime("%Y-%m-%d"),
        "%Y-%m-%d",
    ).date()
    hour24 = bool(payload.get("hour24", False))
    view = str(payload.get("view") or "month").lower()
    if view not in ("day", "month"):
        raise ValueError("Unsupported Nepali calendar view")
    rows = calculate_month(selected, lat, lon, tz, hour24) if view == "month" else []
    day = calculate_day(selected, lat, lon, tz, hour24) if view == "day" else None

    qualities = sorted({
        row.get("data_quality")
        for row in (rows + ([day] if day else []))
        if row and row.get("data_quality")
    })
    print(json.dumps({
        "ok": True,
        "variant": "nepali",
        "view": view,
        "date": selected.isoformat(),
        "year": selected.year,
        "month": selected.month,
        "month_name": selected.strftime("%B"),
        "first_weekday": calendar.monthrange(selected.year, selected.month)[0],
        "engine": {
            "name": "tithika-nepali-bikram-sambat",
            "version": ENGINE_VERSION,
            "basis": "bikram-sambat-civil",
            "panchang_version": panchang.ENGINE_VERSION,
            "ayanamsha": "Lahiri / Chitrapaksha",
            "data_quality": qualities,
            "supported_bs_years": [START_YEAR, END_YEAR],
            "official_lookup_bs_years": [2000, 2099],
        },
        "location": {
            "city": (payload.get("city") or "Current location").strip()[:120],
            "lat": lat,
            "lon": lon,
            "timezone": timezone_name,
        },
        "day": day,
        "days": rows,
        "note": (
            "Bikram Sambat civil dates use a bundled offline month-length table. "
            "BS 2000-2099 uses the upstream official lookup range; outer years are "
            "marked Sankranti-estimated. Panchang limbs are calculated independently "
            "from Tithika's Lahiri astronomy engine at local sunrise."
        ),
    }, ensure_ascii=False))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(json.dumps({
            "ok": False,
            "error": str(exc),
            "code": "NEPALI_CALENDAR_FAILED",
        }))
        sys.exit(1)
