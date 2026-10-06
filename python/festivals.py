#!/usr/bin/env python3
"""
Tithika major-festival adapter.

All date-selection mechanics now live in festival_rules.py. This adapter keeps
API/CLI compatibility for existing festival pages.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import festival_rules
import panchang

KINDS = festival_rules.FESTIVAL_RULES


def festival_event(kind, year, lat, lon, tz, hour24):
    return festival_rules.calculate_event(
        kind, year, lat, lon, tz, hour24
    )


def main():
    payload = json.loads(sys.stdin.read() or "{}")
    kind = str(payload.get("kind") or "ganesh-chaturthi").lower()
    if kind not in festival_rules.SUPPORTED_KINDS:
        raise ValueError("Unsupported festival kind")

    lat = float(payload.get("lat", 19.0760))
    lon = float(payload.get("lon", 72.8777))
    if not (-90 <= lat <= 90 and -180 <= lon <= 180):
        raise ValueError("Invalid latitude/longitude")

    selected = datetime.strptime(
        payload.get("date") or datetime.now().strftime("%Y-%m-%d"),
        "%Y-%m-%d",
    ).date()
    timezone_name = payload.get("timezone") or "Asia/Kolkata"
    try:
        tz = ZoneInfo(timezone_name)
    except ZoneInfoNotFoundError:
        timezone_name = "Asia/Kolkata"
        tz = ZoneInfo(timezone_name)

    hour24 = bool(payload.get("hour24", False))
    city = (payload.get("city") or "Current location").strip()[:120]
    event = festival_rules.calculate_event(
        kind, selected.year, lat, lon, tz, hour24
    )

    print(json.dumps({
        "ok": True,
        "kind": kind,
        "year": selected.year,
        "location": {
            "city": city,
            "lat": lat,
            "lon": lon,
            "timezone": timezone_name,
        },
        "engine": {
            "name": "tithika-festival-rules",
            "version": festival_rules.ENGINE_VERSION,
            "panchang_version": panchang.ENGINE_VERSION,
            "status": "declarative-rule-selected",
        },
        "event": event,
        "note": (
            "Festival date selection is delegated to the shared declarative "
            "festival rule engine. Each event exposes its selector/profile so "
            "the chosen date and Muhurat evidence remain auditable."
        ),
    }, ensure_ascii=False))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(json.dumps({
            "ok": False,
            "error": str(exc),
            "code": "FESTIVAL_CALCULATION_FAILED",
        }))
        sys.exit(1)
