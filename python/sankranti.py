#!/usr/bin/env python3
"""
Tithika Nirayana Sankranti / solar-ingress engine.

Finds the exact local instant when the Lahiri/Chitrapaksha sidereal Sun crosses
each 30-degree Rashi boundary. This is the astronomical substrate for Sankranti
calendars and later Punya Kaal/festival rule layers.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import panchang

SANKRANTI_NAMES = [
    "Mesha Sankranti",
    "Vrishabha Sankranti",
    "Mithuna Sankranti",
    "Karka Sankranti",
    "Simha Sankranti",
    "Kanya Sankranti",
    "Tula Sankranti",
    "Vrishchika Sankranti",
    "Dhanu Sankranti",
    "Makara Sankranti",
    "Kumbha Sankranti",
    "Meena Sankranti",
]


def sun_sign(dt: datetime) -> int:
    sun, _, _ = panchang.sidereal_longitudes(dt)
    return int(sun // 30.0) % 12


def refine_ingress(left: datetime, right: datetime, old_sign: int) -> datetime:
    """Binary-refine a Sun sign change to sub-second precision."""
    lo, hi = left, right
    for _ in range(46):
        mid = lo + (hi - lo) / 2
        if sun_sign(mid) == old_sign:
            lo = mid
        else:
            hi = mid
    return hi


def event_payload(moment: datetime, new_sign: int, lat: float, lon: float, tz: ZoneInfo, hour24: bool) -> dict:
    old_sign = (new_sign - 1) % 12
    sunrise = panchang.rise_set(
        moment.date(), lat, lon, tz,
        panchang.astronomy.Body.Sun, panchang.astronomy.Direction.Rise
    )
    sunset = panchang.rise_set(
        moment.date(), lat, lon, tz,
        panchang.astronomy.Body.Sun, panchang.astronomy.Direction.Set
    )
    sun, _, ayanamsha = panchang.sidereal_longitudes(moment)

    return {
        "name": SANKRANTI_NAMES[new_sign],
        "rashi": panchang.RASHI_NAMES[new_sign],
        "from_rashi": panchang.RASHI_NAMES[old_sign],
        "to_rashi": panchang.RASHI_NAMES[new_sign],
        "rashi_id": new_sign,
        "datetime": moment.isoformat(),
        "date": moment.date().isoformat(),
        "date_label": moment.strftime("%B %d, %Y").replace(" 0", " "),
        "weekday": moment.strftime("%A"),
        "time_label": panchang.fmt(moment, hour24),
        "sun_sidereal_longitude": round(sun, 8),
        "ayanamsha": round(ayanamsha, 8),
        "sunrise": sunrise.isoformat() if sunrise else None,
        "sunrise_label": panchang.fmt(sunrise, hour24),
        "sunset": sunset.isoformat() if sunset else None,
        "sunset_label": panchang.fmt(sunset, hour24),
        "daylight_ingress": bool(sunrise and sunset and sunrise <= moment <= sunset),
    }


def find_year(year: int, lat: float, lon: float, tz: ZoneInfo, hour24: bool) -> list[dict]:
    # Wide margins ensure January and December ingresses are bracketed locally.
    cursor = datetime(year - 1, 12, 1, 0, 0, tzinfo=tz)
    end = datetime(year + 1, 2, 1, 0, 0, tzinfo=tz)
    step = timedelta(hours=12)

    previous = cursor
    previous_sign = sun_sign(previous)
    rows = []

    while previous < end:
        current = min(previous + step, end)
        current_sign = sun_sign(current)

        if current_sign != previous_sign:
            moment = refine_ingress(previous, current, previous_sign)
            new_sign = sun_sign(moment)
            if moment.year == year:
                rows.append(event_payload(moment, new_sign, lat, lon, tz, hour24))
            previous_sign = current_sign

        previous = current

    rows.sort(key=lambda row: row["datetime"])
    return rows


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

    hour24 = bool(payload.get("hour24", False))
    city = (payload.get("city") or "Current location").strip()[:120]
    events = find_year(selected.year, lat, lon, tz, hour24)

    print(json.dumps({
        "ok": True,
        "year": selected.year,
        "location": {
            "city": city,
            "lat": lat,
            "lon": lon,
            "timezone": timezone_name,
        },
        "engine": {
            "name": "tithika-sankranti",
            "version": panchang.ENGINE_VERSION,
            "source": "Astronomy Engine Sun position + Tithika Lahiri sidereal conversion",
            "ayanamsha": "Lahiri / Chitrapaksha",
            "scope": "Nirayana solar ingress",
        },
        "events": events,
        "rule_status": "astronomical-ingress",
        "note": (
            "These are exact Nirayana solar-ingress moments. Location-specific "
            "Sankranti Punya Kaal and festival observance rules are a separate layer."
        ),
    }, ensure_ascii=False))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(json.dumps({
            "ok": False,
            "error": str(exc),
            "code": "SANKRANTI_CALCULATION_FAILED",
        }))
        sys.exit(1)
