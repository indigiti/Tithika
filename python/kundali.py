#!/usr/bin/env python3
"""
Tithika Janma Kundali foundation.

Outputs:
- D1 Rashi chart using whole-sign houses from Janma Lagna
- D9 Navamsha chart
- classical Graha positions with selectable mean/true Rahu-Ketu
- exact birth Panchang factors
- mutual aspect snapshot
- natal Graha Yuddha detection

This is a calculation/chart foundation, not an interpretive prediction engine.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import aspects
import lagna
import panchang
import planetary

ENGINE_VERSION = "0.1.0"

MOVABLE = {0, 3, 6, 9}
FIXED = {1, 4, 7, 10}
DUAL = {2, 5, 8, 11}


def parse_birth(payload: dict, tz: ZoneInfo) -> datetime:
    text = str(payload.get("datetime") or "").strip()
    if not text:
        date_text = payload.get("date") or datetime.now(tz).strftime("%Y-%m-%d")
        time_text = payload.get("time") or "12:00:00"
        text = f"{date_text}T{time_text}"
    dt = datetime.fromisoformat(text)
    return dt.replace(tzinfo=tz) if dt.tzinfo is None else dt.astimezone(tz)


def navamsha_sign(longitude: float) -> dict:
    rashi_id = int(longitude // 30.0) % 12
    degree = longitude - rashi_id * 30.0
    segment = min(8, int(degree // (30.0 / 9.0)))

    if rashi_id in MOVABLE:
        start = rashi_id
    elif rashi_id in FIXED:
        start = (rashi_id + 8) % 12
    else:
        start = (rashi_id + 4) % 12

    nav_id = (start + segment) % 12
    nav_degree = (degree % (30.0/9.0)) * 9.0
    return {
        "rashi_id": nav_id,
        "rashi": panchang.RASHI_NAMES[nav_id],
        "degree_in_rashi": round(nav_degree, 8),
        "navamsha_index": segment + 1,
    }


def chart_cells(lagna_sign_id: int, placements: list[dict]) -> list[dict]:
    cells = []
    for sign_id, rashi in enumerate(panchang.RASHI_NAMES):
        house = ((sign_id - lagna_sign_id) % 12) + 1
        planets = [p for p in placements if p["rashi_id"] == sign_id]
        cells.append({
            "rashi_id": sign_id,
            "rashi": rashi,
            "house": house,
            "planets": planets,
        })
    return cells


def main():
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

    birth = parse_birth(payload, tz)
    city = (payload.get("city") or "Current location").strip()[:120]
    node_model = str(payload.get("node_model") or "mean").lower()
    if node_model not in ("mean", "true"):
        raise ValueError("node_model must be mean or true")
    modern = bool(payload.get("modern", False))

    asc = lagna.lagna_state(birth, lat, lon)
    planets = planetary.positions(birth, modern, node_model)

    d1_placements = []
    d9_placements = []
    for row in planets:
        house = ((row["rashi_id"] - asc["lagna_id"]) % 12) + 1
        d1_placements.append({
            "name": row["name"],
            "rashi_id": row["rashi_id"],
            "rashi": row["rashi"],
            "house": house,
            "longitude": row["longitude"],
            "degree_in_rashi": row["degree_in_rashi"],
            "nakshatra": row["nakshatra"],
            "pada": row["pada"],
            "retrograde": row["retrograde"],
            "combust": row["combust"],
        })
        nav = navamsha_sign(row["longitude"])
        d9_placements.append({
            "name": row["name"],
            **nav,
            "retrograde": row["retrograde"],
        })

    lagna_nav = navamsha_sign(asc["sidereal_longitude"])
    d1_lagna_sign = asc["lagna_id"]
    d9_lagna_sign = lagna_nav["rashi_id"]

    birth_state = panchang.state_at(birth)
    lunar_month = panchang.lunar_month_info(birth, birth_state)

    d1_lagna = {
        "name": "Lagna",
        "rashi_id": d1_lagna_sign,
        "rashi": asc["lagna"],
        "house": 1,
        "longitude": asc["sidereal_longitude"],
        "degree_in_rashi": asc["degree_in_sign"],
    }
    d9_lagna = {
        "name": "Lagna",
        **lagna_nav,
        "house": 1,
    }

    result = {
        "ok": True,
        "birth_datetime": birth.isoformat(),
        "location": {
            "city": city,
            "lat": lat,
            "lon": lon,
            "timezone": timezone_name,
        },
        "engine": {
            "name": "tithika-kundali",
            "version": ENGINE_VERSION,
            "ayanamsha": "Lahiri / Chitrapaksha",
            "rahu_ketu": f"{node_model} nodes",
            "house_system": "whole-sign",
            "d1": "Rashi",
            "d9": "Navamsha",
        },
        "node_model": node_model,
        "lagna": d1_lagna,
        "panchang": {
            "tithi": birth_state["tithi"],
            "paksha": birth_state["paksha"],
            "nakshatra": birth_state["nakshatra"],
            "nakshatra_pada": birth_state["nakshatra_pada"],
            "yoga": birth_state["yoga"],
            "karana": birth_state["karana"],
            "moon_rashi": birth_state["moon_rashi"],
            "sun_rashi": birth_state["sun_rashi"],
            "amanta_month": lunar_month.get("amanta"),
            "purnimanta_month": lunar_month.get("purnimanta"),
        },
        "d1": {
            "lagna": d1_lagna,
            "placements": d1_placements,
            "cells": chart_cells(d1_lagna_sign, d1_placements),
        },
        "d9": {
            "lagna": d9_lagna,
            "placements": d9_placements,
            "cells": chart_cells(d9_lagna_sign, d9_placements),
        },
        "aspects": aspects.snapshot(birth),
        "graha_yuddha": aspects.graha_yuddha_snapshot(birth),
        "note": (
            "D1 uses whole-sign houses from Janma Lagna. D9 is Navamsha. "
            "This stage calculates the chart; prediction, Dasha and strength systems "
            "remain separate layers."
        ),
    }

    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(json.dumps({"ok": False, "error": str(exc), "code": "KUNDALI_CALCULATION_FAILED"}))
        sys.exit(1)
