#!/usr/bin/env python3
"""
Tithika Month Panchang engine.

Builds a compact sunrise-state Panchang for each civil date in the selected
local month, reusing the verified Daily Panchang astronomy core.
"""
from __future__ import annotations

import calendar
import json
import sys
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import panchang

def main() -> None:
    payload = json.loads(sys.stdin.read() or "{}")
    lat = float(payload.get("lat", 19.0760))
    lon = float(payload.get("lon", 72.8777))
    if not (-90 <= lat <= 90 and -180 <= lon <= 180):
        raise ValueError("Invalid latitude/longitude")

    date_text = payload.get("date") or datetime.now().strftime("%Y-%m-%d")
    selected = datetime.strptime(date_text, "%Y-%m-%d").date()

    timezone_name = payload.get("timezone") or "Asia/Kolkata"
    try:
        tz = ZoneInfo(timezone_name)
    except ZoneInfoNotFoundError:
        timezone_name = "Asia/Kolkata"
        tz = ZoneInfo(timezone_name)

    city = (payload.get("city") or "Current location").strip()[:120]
    hour24 = bool(payload.get("hour24", False))

    _, days_in_month = calendar.monthrange(selected.year, selected.month)
    rows = []

    for day in range(1, days_in_month + 1):
        d = selected.replace(day=day)
        sunrise = panchang.rise_set(
            d, lat, lon, tz, panchang.astronomy.Body.Sun, panchang.astronomy.Direction.Rise
        )
        sunset = panchang.rise_set(
            d, lat, lon, tz, panchang.astronomy.Body.Sun, panchang.astronomy.Direction.Set
        )
        next_sunrise = panchang.rise_set(
            d + timedelta(days=1), lat, lon, tz,
            panchang.astronomy.Body.Sun, panchang.astronomy.Direction.Rise
        )
        if sunrise is None or sunset is None or next_sunrise is None:
            rows.append({"date": d.isoformat(), "day": day, "available": False})
            continue

        state = panchang.state_at(sunrise)
        next_tithi = panchang.find_transition(sunrise, next_sunrise, "tithi_id", state["tithi_id"])
        next_nak = panchang.find_transition(sunrise, next_sunrise, "nakshatra_id", state["nakshatra_id"])

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
            "tithi_id": state["tithi_id"],
            "tithi_number": state["tithi_number"],
            "paksha": state["paksha"],
            "tithi_end": next_tithi.isoformat() if next_tithi else None,
            "tithi_end_label": panchang.transition_label(next_tithi, d, hour24) if next_tithi else None,
            "nakshatra": state["nakshatra"],
            "nakshatra_id": state["nakshatra_id"],
            "nakshatra_pada": state["nakshatra_pada"],
            "nakshatra_end": next_nak.isoformat() if next_nak else None,
            "nakshatra_end_label": panchang.transition_label(next_nak, d, hour24) if next_nak else None,
            "yoga": state["yoga"],
            "karana": state["karana"],
            "moon_rashi": state["moon_rashi"],
        })

    first_available = next((row for row in rows if row.get("available")), None)
    month_info = None
    if first_available:
        first_date = datetime.fromisoformat(first_available["sunrise"])
        month_info = panchang.lunar_month_info(first_date, panchang.state_at(first_date))

    print(json.dumps({
        "ok": True,
        "engine": {
            "name": "tithika-panchang-month",
            "version": panchang.ENGINE_VERSION,
            "source": "shared Daily Panchang astronomy core",
            "ayanamsha": "Lahiri / Chitrapaksha",
        },
        "location": {
            "city": city,
            "lat": lat,
            "lon": lon,
            "timezone": timezone_name,
        },
        "year": selected.year,
        "month": selected.month,
        "month_name": selected.strftime("%B"),
        "days_in_month": days_in_month,
        "first_weekday": calendar.monthrange(selected.year, selected.month)[0],
        "lunar_month_at_start": month_info,
        "days": rows,
    }, ensure_ascii=False))

if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(json.dumps({
            "ok": False,
            "error": str(exc),
            "code": "PANCHANG_MONTH_CALCULATION_FAILED",
        }))
        sys.exit(1)
