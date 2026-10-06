#!/usr/bin/env python3
"""
Tithika Panchang decision utilities.

Implements:
- Tarabalam from Janma Nakshatra and current Nakshatra (9-Tara cycle).
- Chandrabalam from Janma Rashi and current Moon Rashi.
- Panchak interval detection (Moon from Dhanishtha latter half through Revati).
- Bhadra / Vishti Karana exact intervals.

All timelines use the local Hindu day: sunrise -> next sunrise.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import panchang

ENGINE_VERSION = "0.1.0"

TARA_NAMES = {
    1: ("Janma", "neutral"),
    2: ("Sampat", "good"),
    3: ("Vipat", "avoid"),
    4: ("Kshema", "good"),
    5: ("Pratyari", "avoid"),
    6: ("Sadhaka", "good"),
    7: ("Naidhana", "avoid"),
    8: ("Mitra", "good"),
    9: ("Parama Mitra", "good"),
}
GOOD_TARA = {2, 4, 6, 8, 9}
GOOD_CHANDRA_HOUSES = {1, 3, 6, 7, 10, 11}


def hindu_day(d, lat, lon, tz):
    sunrise = panchang.rise_set(
        d, lat, lon, tz,
        panchang.astronomy.Body.Sun,
        panchang.astronomy.Direction.Rise,
    )
    next_sunrise = panchang.rise_set(
        d + timedelta(days=1), lat, lon, tz,
        panchang.astronomy.Body.Sun,
        panchang.astronomy.Direction.Rise,
    )
    if not sunrise or not next_sunrise:
        raise ValueError("Sunrise unavailable for this latitude/date")
    if next_sunrise <= sunrise:
        next_sunrise += timedelta(days=1)
    return sunrise, next_sunrise


def tara_position(birth_id, current_id):
    count = ((current_id - birth_id) % 27) + 1
    position = ((count - 1) % 9) + 1
    name, quality = TARA_NAMES[position]
    return {
        "count": count,
        "position": position,
        "tara": name,
        "quality": quality,
        "good": position in GOOD_TARA,
    }


def chandra_house(birth_rashi_id, current_rashi_id):
    house = ((current_rashi_id - birth_rashi_id) % 12) + 1
    return {
        "house": house,
        "good": house in GOOD_CHANDRA_HOUSES,
        "ashtama_chandra": house == 8,
    }


def sequence(start, end, key, name_key):
    rows = []
    cursor = start
    while cursor < end:
        state = panchang.state_at(cursor)
        sid = state[key]
        transition = panchang.find_transition(cursor, end, key, sid)
        stop = transition or end
        rows.append((cursor, stop, state))
        if not transition:
            break
        cursor = transition + timedelta(seconds=1)
    return rows


def tarabalam(start, end, birth_nakshatra, hour24):
    try:
        birth_id = panchang.NAKSHATRA_NAMES.index(birth_nakshatra)
    except ValueError as exc:
        raise ValueError("Invalid birth Nakshatra") from exc

    rows = []
    for a, b, state in sequence(start, end, "nakshatra_id", "nakshatra"):
        current_id = state["nakshatra_id"]
        relation = tara_position(birth_id, current_id)
        good_birth = []
        for idx, name in enumerate(panchang.NAKSHATRA_NAMES):
            if tara_position(idx, current_id)["good"]:
                good_birth.append(name)
        rows.append({
            "start": a.isoformat(),
            "end": b.isoformat(),
            "start_label": panchang.transition_label(a, start.date(), hour24),
            "end_label": panchang.transition_label(b, start.date(), hour24),
            "current_nakshatra": state["nakshatra"],
            "birth_nakshatra": birth_nakshatra,
            **relation,
            "good_birth_nakshatras": good_birth,
        })
    return rows


def chandrabalam(start, end, birth_rashi, hour24):
    try:
        birth_id = panchang.RASHI_NAMES.index(birth_rashi)
    except ValueError as exc:
        raise ValueError("Invalid birth Rashi") from exc

    rows = []
    for a, b, state in sequence(start, end, "moon_rashi_id", "moon_rashi"):
        current_id = state["moon_rashi_id"]
        relation = chandra_house(birth_id, current_id)
        good_birth = []
        for idx, name in enumerate(panchang.RASHI_NAMES):
            if chandra_house(idx, current_id)["good"]:
                good_birth.append(name)
        ashtama_birth = panchang.RASHI_NAMES[(current_id - 7) % 12]
        rows.append({
            "start": a.isoformat(),
            "end": b.isoformat(),
            "start_label": panchang.transition_label(a, start.date(), hour24),
            "end_label": panchang.transition_label(b, start.date(), hour24),
            "current_moon_rashi": state["moon_rashi"],
            "birth_rashi": birth_rashi,
            **relation,
            "good_birth_rashis": good_birth,
            "ashtama_chandra_birth_rashi": ashtama_birth,
        })
    return rows


def panchak_active(moment):
    # Dhanishtha latter half starts at 300° sidereal Moon longitude and Panchak
    # continues through Shatabhisha, both Bhadrapadas and Revati until 360°.
    return panchang.state_at(moment)["moon_longitude"] >= 300.0


def refine_boolean_boundary(left, right, left_value, predicate):
    lo, hi = left, right
    for _ in range(34):
        mid = lo + (hi - lo) / 2
        if predicate(mid) == left_value:
            lo = mid
        else:
            hi = mid
    return hi


def boolean_intervals(start, end, predicate):
    rows = []
    step = timedelta(minutes=30)
    left = start
    left_value = predicate(left)
    active_start = start if left_value else None
    probe = min(end, left + step)

    while left < end:
        value = predicate(probe)
        if value != left_value:
            boundary = refine_boolean_boundary(left, probe, left_value, predicate)
            if left_value and active_start:
                rows.append((active_start, boundary))
                active_start = None
            elif value:
                active_start = boundary
            left_value = value
        if probe >= end:
            break
        left = probe
        probe = min(end, probe + step)

    if left_value and active_start and active_start < end:
        rows.append((active_start, end))
    return rows


def panchak(start, end, hour24):
    rows = []
    for a, b in boolean_intervals(start, end, panchak_active):
        state = panchang.state_at(a + timedelta(seconds=1))
        rows.append({
            "start": a.isoformat(),
            "end": b.isoformat(),
            "start_label": panchang.transition_label(a, start.date(), hour24),
            "end_label": panchang.transition_label(b, start.date(), hour24),
            "start_nakshatra": state["nakshatra"],
            "rule": "Moon longitude 300°–360°: latter half Dhanishtha through Revati",
        })
    return rows


def bhadra(start, end, hour24):
    rows = []
    for a, b, state in sequence(start, end, "karana_id", "karana"):
        if state["karana"] != "Vishti":
            continue
        mid = a + (b - a) / 2
        moon = panchang.state_at(mid)
        rows.append({
            "start": a.isoformat(),
            "end": b.isoformat(),
            "start_label": panchang.transition_label(a, start.date(), hour24),
            "end_label": panchang.transition_label(b, start.date(), hour24),
            "karana": "Vishti",
            "paksha": moon["paksha"],
            "tithi": moon["tithi"],
            "moon_rashi": moon["moon_rashi"],
            "rule": "Bhadra is the Vishti Karana interval",
        })
    return rows


def main():
    payload = json.loads(sys.stdin.read() or "{}")
    mode = str(payload.get("mode") or "tarabalam").lower()
    if mode not in ("tarabalam", "chandrabalam", "panchak", "bhadra", "all"):
        raise ValueError("Unsupported Panchang utility mode")

    lat = float(payload.get("lat", 19.0760))
    lon = float(payload.get("lon", 72.8777))
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
    sunrise, next_sunrise = hindu_day(selected, lat, lon, tz)

    out = {
        "ok": True,
        "mode": mode,
        "date": selected.isoformat(),
        "engine": {
            "name": "tithika-panchang-utilities",
            "version": ENGINE_VERSION,
            "ayanamsha": "Lahiri / Chitrapaksha",
            "hindu_day": "local sunrise to next sunrise",
        },
        "location": {
            "city": (payload.get("city") or "Current location").strip()[:120],
            "lat": lat,
            "lon": lon,
            "timezone": timezone_name,
        },
        "sunrise": sunrise.isoformat(),
        "next_sunrise": next_sunrise.isoformat(),
    }

    if mode in ("tarabalam", "all"):
        birth_nak = str(payload.get("birth_nakshatra") or "Ashwini")
        out["tarabalam"] = {
            "birth_nakshatra": birth_nak,
            "good_positions": sorted(GOOD_TARA),
            "timeline": tarabalam(sunrise, next_sunrise, birth_nak, hour24),
        }
    if mode in ("chandrabalam", "all"):
        birth_rashi = str(payload.get("birth_rashi") or "Mesha")
        out["chandrabalam"] = {
            "birth_rashi": birth_rashi,
            "good_houses": sorted(GOOD_CHANDRA_HOUSES),
            "timeline": chandrabalam(sunrise, next_sunrise, birth_rashi, hour24),
        }
    if mode in ("panchak", "all"):
        out["panchak"] = {
            "active": panchak_active(sunrise),
            "intervals": panchak(sunrise, next_sunrise, hour24),
        }
    if mode in ("bhadra", "all"):
        intervals = bhadra(sunrise, next_sunrise, hour24)
        out["bhadra"] = {
            "active": bool(intervals and intervals[0]["start"] <= sunrise.isoformat() < intervals[0]["end"]),
            "intervals": intervals,
        }

    print(json.dumps(out, ensure_ascii=False))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(json.dumps({
            "ok": False,
            "error": str(exc),
            "code": "PANCHANG_UTILITY_FAILED",
        }))
        sys.exit(1)
