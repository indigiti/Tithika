#!/usr/bin/env python3
"""
Tithika sidereal Lagna / Ascendant engine.

Astronomical contract
---------------------
1. Greenwich apparent sidereal time comes from the vendored Astronomy Engine.
2. Local apparent sidereal angle = GAST + east-positive geographic longitude.
3. Tropical ascendant is the eastern ecliptic/horizon intersection using local
   latitude and the true obliquity of date.
4. Lahiri/Chitrapaksha ayanamsha is subtracted to obtain Nirayana Lagna.
5. Sign boundaries are scan-bracketed and binary-refined.
"""
from __future__ import annotations

import json
import math
import sys
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import panchang

ENGINE_VERSION = "0.1.0"


def true_obliquity_deg(t: panchang.astronomy.Time) -> float:
    return float(t._etilt().tobl)


def tropical_ascendant_deg(moment: datetime, lat: float, lon: float) -> float:
    t = panchang.astronomy_time(moment)
    theta = math.radians((panchang.astronomy.SiderealTime(t) * 15.0 + lon) % 360.0)
    eps = math.radians(true_obliquity_deg(t))
    phi = math.radians(lat)
    y = math.cos(theta)
    x = -(math.sin(theta) * math.cos(eps) + math.tan(phi) * math.sin(eps))
    return math.degrees(math.atan2(y, x)) % 360.0


def sidereal_ascendant_deg(moment: datetime, lat: float, lon: float) -> tuple[float, float, float]:
    tropical = tropical_ascendant_deg(moment, lat, lon)
    t = panchang.astronomy_time(moment)
    ayanamsha = panchang.lahiri_ayanamsha_deg(t, True)
    sidereal = (tropical - ayanamsha) % 360.0
    return sidereal, tropical, ayanamsha


def lagna_state(moment: datetime, lat: float, lon: float) -> dict:
    sidereal, tropical, ayanamsha = sidereal_ascendant_deg(moment, lat, lon)
    sign_id = int(sidereal // 30.0) % 12
    degree = sidereal - sign_id * 30.0
    return {
        "lagna_id": sign_id,
        "lagna": panchang.RASHI_NAMES[sign_id],
        "sidereal_longitude": round(sidereal, 8),
        "tropical_longitude": round(tropical, 8),
        "ayanamsha": round(ayanamsha, 8),
        "degree_in_sign": round(degree, 8),
    }


def refine_transition(left: datetime, right: datetime, old_id: int, lat: float, lon: float) -> datetime:
    lo, hi = left, right
    for _ in range(42):
        mid = lo + (hi - lo) / 2
        if lagna_state(mid, lat, lon)["lagna_id"] == old_id:
            lo = mid
        else:
            hi = mid
    return hi


def timeline(start: datetime, end: datetime, lat: float, lon: float, hour24: bool) -> list[dict]:
    if end <= start:
        return []
    rows = []
    cursor = start
    current_id = lagna_state(cursor, lat, lon)["lagna_id"]
    segment_start = cursor
    probe = cursor + timedelta(minutes=5)

    while probe <= end:
        probe_id = lagna_state(probe, lat, lon)["lagna_id"]
        if probe_id != current_id:
            boundary = refine_transition(probe - timedelta(minutes=5), probe, current_id, lat, lon)
            row_state = lagna_state(segment_start + timedelta(seconds=1), lat, lon)
            rows.append({
                **row_state,
                "start": segment_start.isoformat(),
                "end": boundary.isoformat(),
                "start_label": panchang.transition_label(segment_start, start.date(), hour24),
                "end_label": panchang.transition_label(boundary, start.date(), hour24),
                "duration_minutes": round((boundary - segment_start).total_seconds() / 60.0, 2),
            })
            segment_start = boundary
            current_id = lagna_state(boundary + timedelta(seconds=1), lat, lon)["lagna_id"]
        probe += timedelta(minutes=5)

    if segment_start < end:
        row_state = lagna_state(segment_start + timedelta(seconds=1), lat, lon)
        rows.append({
            **row_state,
            "start": segment_start.isoformat(),
            "end": end.isoformat(),
            "start_label": panchang.transition_label(segment_start, start.date(), hour24),
            "end_label": panchang.transition_label(end, start.date(), hour24),
            "duration_minutes": round((end - segment_start).total_seconds() / 60.0, 2),
        })
    return rows


def main() -> None:
    payload = json.loads(sys.stdin.read() or "{}")
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

    selected = datetime.strptime(
        payload.get("date") or datetime.now(tz).strftime("%Y-%m-%d"), "%Y-%m-%d"
    ).date()
    hour24 = bool(payload.get("hour24", False))
    city = (payload.get("city") or "Current location").strip()[:120]
    start = datetime(selected.year, selected.month, selected.day, 0, 0, tzinfo=tz)
    end = start + timedelta(days=1)
    rows = timeline(start, end, lat, lon, hour24)

    instant_state = None
    instant_text = payload.get("datetime")
    if instant_text:
        instant = datetime.fromisoformat(instant_text)
        instant = instant.replace(tzinfo=tz) if instant.tzinfo is None else instant.astimezone(tz)
        instant_state = {
            **lagna_state(instant, lat, lon),
            "datetime": instant.isoformat(),
            "label": panchang.transition_label(instant, instant.date(), hour24),
        }

    print(json.dumps({
        "ok": True,
        "date": selected.isoformat(),
        "location": {
            "city": city,
            "lat": lat,
            "lon": lon,
            "timezone": timezone_name,
        },
        "engine": {
            "name": "tithika-lagna",
            "version": ENGINE_VERSION,
            "panchang_version": panchang.ENGINE_VERSION,
            "astronomy": "Astronomy Engine GAST + true obliquity",
            "ayanamsha": "Lahiri / Chitrapaksha",
            "status": "verified-geometry",
        },
        "timeline": rows,
        "instant": instant_state,
        "note": (
            "Lagna is the sidereal eastern ecliptic-horizon intersection. Sign lengths "
            "are unequal and location-dependent; Tithika does not assume two hours per sign."
        ),
    }, ensure_ascii=False))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(json.dumps({
            "ok": False,
            "error": str(exc),
            "code": "LAGNA_CALCULATION_FAILED",
        }))
        sys.exit(1)
