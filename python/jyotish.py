#!/usr/bin/env python3
"""
Tithika birth/Jyotish calculator foundation.

Modes:
- birthstar: Janma Nakshatra + Pada + Janma Rashi.
- janma-lagna: Lahiri sidereal ascendant.
- moonsign: Janma Rashi.
- sunsign: Nirayana Surya Rashi.

Birth time is interpreted in the selected IANA timezone. The caller must supply
an accurate birth time for Lagna; no location/time guessing is performed here.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import lagna
import planetary


def parse_birth(payload: dict, tz: ZoneInfo) -> datetime:
    text = str(payload.get("datetime") or "").strip()
    if not text:
        date_text = payload.get("date") or datetime.now(tz).strftime("%Y-%m-%d")
        time_text = payload.get("time") or "12:00"
        text = f"{date_text}T{time_text}"
    dt = datetime.fromisoformat(text)
    return dt.replace(tzinfo=tz) if dt.tzinfo is None else dt.astimezone(tz)


def main() -> None:
    payload = json.loads(sys.stdin.read() or "{}")
    mode = str(payload.get("mode") or "birthstar").lower()
    if mode not in ("birthstar", "janma-lagna", "moonsign", "sunsign"):
        raise ValueError("Unsupported Jyotish mode")

    lat = float(payload.get("lat", 19.0760))
    lon = float(payload.get("lon", 72.8777))
    if not (-89.999 <= lat <= 89.999 and -180 <= lon <= 180):
        raise ValueError("Invalid latitude/longitude")

    timezone_name = payload.get("timezone") or "Asia/Kolkata"
    try:
        tz = ZoneInfo(timezone_name)
    except ZoneInfoNotFoundError:
        timezone_name = "Asia/Kolkata"
        tz = ZoneInfo(timezone_name)

    birth = parse_birth(payload, tz)
    city = (payload.get("city") or "Current location").strip()[:120]

    moon = planetary.planet_state("Moon", birth)
    sun = planetary.planet_state("Sun", birth)
    asc = lagna.lagna_state(birth, lat, lon)

    result = {
        "birth_datetime": birth.isoformat(),
        "location": {
            "city": city,
            "lat": lat,
            "lon": lon,
            "timezone": timezone_name,
        },
        "moon": {
            "longitude": moon["longitude"],
            "rashi": moon["rashi"],
            "degree_in_rashi": moon["degree_in_rashi"],
            "nakshatra": moon["nakshatra"],
            "pada": moon["pada"],
        },
        "sun": {
            "longitude": sun["longitude"],
            "rashi": sun["rashi"],
            "degree_in_rashi": sun["degree_in_rashi"],
            "nakshatra": sun["nakshatra"],
            "pada": sun["pada"],
        },
        "lagna": {
            "longitude": asc["sidereal_longitude"],
            "rashi": asc["lagna"],
            "degree_in_rashi": asc["degree_in_sign"],
        },
    }

    if mode == "birthstar":
        primary = {
            "title": "Janma Nakshatra",
            "value": moon["nakshatra"],
            "pada": moon["pada"],
            "rashi": moon["rashi"],
        }
    elif mode == "janma-lagna":
        primary = {
            "title": "Janma Lagna",
            "value": asc["lagna"],
            "degree_in_rashi": asc["degree_in_sign"],
        }
    elif mode == "moonsign":
        primary = {
            "title": "Janma Rashi",
            "value": moon["rashi"],
            "degree_in_rashi": moon["degree_in_rashi"],
        }
    else:
        primary = {
            "title": "Surya Rashi",
            "value": sun["rashi"],
            "degree_in_rashi": sun["degree_in_rashi"],
        }

    print(json.dumps({
        "ok": True,
        "mode": mode,
        "engine": {
            "name": "tithika-jyotish",
            "version": "0.1.0",
            "ayanamsha": "Lahiri / Chitrapaksha",
            "rahu_ketu": "mean nodes",
            "sidereal": True,
        },
        "primary": primary,
        "result": result,
        "note": (
            "Janma Lagna is highly birth-time and location sensitive. Birthstar and "
            "Janma Rashi are derived from the Moon's Nirayana longitude."
        ),
    }, ensure_ascii=False))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(json.dumps({
            "ok": False,
            "error": str(exc),
            "code": "JYOTISH_CALCULATION_FAILED",
        }))
        sys.exit(1)
