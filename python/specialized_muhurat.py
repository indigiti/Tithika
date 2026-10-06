#!/usr/bin/env python3
"""
Tithika specialized Muhurat profiles.

Builds ceremony-specific location-aware candidate windows on top of the shared
muhurat_rules.py substrate. The engine is intentionally evidence-first: every
accepted/rejected day exposes the weekday, lunar month, Tithi/Nakshatra filters,
common blocked intervals and optional Guru/Shukra combustion checks.

The profiles are Tithika's documented traditional rule profiles, not a claim
that every regional Sampradaya uses the same shortlist. They can be versioned
without changing the shared astronomy core.
"""
from __future__ import annotations

import calendar
import json
import sys
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import muhurat_rules
import panchang
import planetary

ENGINE_VERSION = "0.1.0"

COMMON_BLOCKED_YOGAS = ["Vyatipata", "Vaidhriti"]

PROFILES = {
    "vivah": {
        "title": "Vivah Muhurat",
        "allowed_weekdays": ["Monday", "Wednesday", "Thursday", "Friday"],
        "allowed_tithis": ["Dwitiya", "Tritiya", "Panchami", "Saptami", "Dashami", "Ekadashi", "Trayodashi"],
        "allowed_nakshatras": [
            "Rohini", "Mrigashira", "Magha", "Uttara Phalguni", "Hasta",
            "Swati", "Anuradha", "Mula", "Uttara Ashadha",
            "Uttara Bhadrapada", "Revati",
        ],
        "blocked_yogas": COMMON_BLOCKED_YOGAS,
        "block_adhika": True,
        "block_combust_planets": ["Jupiter", "Venus"],
        "minimum_minutes": 24,
    },
    "griha-pravesh": {
        "title": "Griha Pravesh Muhurat",
        "allowed_weekdays": ["Monday", "Wednesday", "Thursday", "Friday", "Saturday"],
        "allowed_tithis": ["Dwitiya", "Tritiya", "Panchami", "Saptami", "Dashami", "Ekadashi", "Dwadashi", "Trayodashi"],
        "allowed_nakshatras": [
            "Ashwini", "Rohini", "Mrigashira", "Punarvasu", "Pushya",
            "Uttara Phalguni", "Chitra", "Anuradha", "Uttara Ashadha",
            "Shravana", "Uttara Bhadrapada", "Revati",
        ],
        "blocked_yogas": COMMON_BLOCKED_YOGAS,
        "block_adhika": True,
        "block_combust_planets": ["Jupiter", "Venus"],
        "minimum_minutes": 24,
    },
    "property": {
        "title": "Property Purchase / Registration Muhurat",
        "allowed_weekdays": ["Thursday", "Friday"],
        "allowed_tithis": [
            "Pratipada", "Dwitiya", "Tritiya", "Chaturthi", "Panchami",
            "Shashthi", "Saptami", "Ashtami", "Navami", "Dashami",
            "Ekadashi", "Dwadashi", "Trayodashi",
        ],
        "allowed_nakshatras": [
            "Punarvasu", "Ashlesha", "Magha", "Purva Phalguni",
            "Vishakha", "Anuradha", "Mula", "Purva Ashadha",
            "Purva Bhadrapada", "Revati",
        ],
        "blocked_yogas": COMMON_BLOCKED_YOGAS,
        "block_adhika": True,
        "block_combust_planets": [],
        "minimum_minutes": 24,
    },
    "vehicle": {
        "title": "Vehicle Purchase Muhurat",
        "allowed_weekdays": ["Sunday", "Monday", "Wednesday", "Thursday", "Friday"],
        "blocked_tithis": ["Chaturthi", "Navami", "Chaturdashi", "Amavasya"],
        "allowed_nakshatras": [
            "Ashwini", "Rohini", "Mrigashira", "Punarvasu", "Pushya",
            "Hasta", "Chitra", "Swati", "Anuradha", "Shravana",
            "Dhanishtha", "Shatabhisha", "Revati",
        ],
        "blocked_yogas": COMMON_BLOCKED_YOGAS,
        "block_adhika": True,
        "block_combust_planets": [],
        "minimum_minutes": 24,
    },
    "namakarana": {
        "title": "Namakarana Sanskar Muhurat",
        "allowed_weekdays": ["Monday", "Wednesday", "Thursday", "Friday"],
        "blocked_tithis": ["Chaturthi", "Navami", "Chaturdashi", "Amavasya"],
        "allowed_nakshatras": [
            "Ashwini", "Rohini", "Mrigashira", "Punarvasu", "Pushya",
            "Hasta", "Chitra", "Swati", "Anuradha", "Shravana",
            "Dhanishtha", "Shatabhisha", "Revati",
        ],
        "blocked_yogas": COMMON_BLOCKED_YOGAS,
        "block_adhika": False,
        "block_combust_planets": [],
        "minimum_minutes": 24,
    },
    "annaprashana": {
        "title": "Annaprashana Sanskar Muhurat",
        "allowed_weekdays": ["Monday", "Wednesday", "Thursday", "Friday"],
        "blocked_tithis": ["Chaturthi", "Navami", "Chaturdashi", "Amavasya"],
        "allowed_nakshatras": [
            "Ashwini", "Rohini", "Mrigashira", "Punarvasu", "Pushya",
            "Hasta", "Chitra", "Swati", "Anuradha", "Shravana",
            "Dhanishtha", "Shatabhisha", "Revati",
        ],
        "blocked_yogas": COMMON_BLOCKED_YOGAS,
        "block_adhika": False,
        "block_combust_planets": [],
        "minimum_minutes": 24,
    },
    "mundana": {
        "title": "Mundana Sanskar Muhurat",
        "allowed_weekdays": ["Monday", "Wednesday", "Thursday", "Friday"],
        "blocked_tithis": ["Chaturthi", "Navami", "Chaturdashi", "Amavasya"],
        "allowed_nakshatras": [
            "Mrigashira", "Punarvasu", "Pushya", "Hasta", "Chitra",
            "Swati", "Shravana", "Dhanishtha", "Shatabhisha", "Revati",
        ],
        "blocked_yogas": COMMON_BLOCKED_YOGAS,
        "block_adhika": False,
        "block_combust_planets": [],
        "minimum_minutes": 24,
    },
}


def intersect_rows(left, right):
    out = []
    for a0, a1 in left:
        for b0, b1 in right:
            ov = muhurat_rules.overlap(a0, a1, b0, b1)
            if ov:
                out.append(ov)
    return out


def allowed_state_intervals(start, end, key, name_key, allowed=None, blocked=None):
    allowed = set(allowed or [])
    blocked = set(blocked or [])
    rows = []
    cursor = start
    while cursor < end:
        state = panchang.state_at(cursor)
        state_id = state[key]
        transition = panchang.find_transition(cursor, end, key, state_id)
        stop = transition or end
        name = state[name_key]
        good = (not allowed or name in allowed) and name not in blocked
        if good:
            rows.append((cursor, stop))
        if not transition:
            break
        cursor = transition + timedelta(seconds=1)
    return rows


def blocked_state_intervals(start, end, key, name_key, blocked):
    blocked = set(blocked or [])
    if not blocked:
        return []
    rows = []
    cursor = start
    while cursor < end:
        state = panchang.state_at(cursor)
        state_id = state[key]
        transition = panchang.find_transition(cursor, end, key, state_id)
        stop = transition or end
        if state[name_key] in blocked:
            rows.append((cursor, stop, state[name_key]))
        if not transition:
            break
        cursor = transition + timedelta(seconds=1)
    return rows


def window_payload(start, end, d, hour24):
    mid = start + (end - start) / 2
    st = panchang.state_at(mid)
    return {
        "start": start.isoformat(),
        "end": end.isoformat(),
        "start_label": panchang.transition_label(start, d, hour24),
        "end_label": panchang.transition_label(end, d, hour24),
        "duration_minutes": round((end - start).total_seconds() / 60.0, 2),
        "evidence": {
            "tithi": st["tithi"],
            "paksha": st["paksha"],
            "nakshatra": st["nakshatra"],
            "yoga": st["yoga"],
            "karana": st["karana"],
            "moon_rashi": st["moon_rashi"],
        },
    }


def evaluate_day(d, lat, lon, tz, profile, hour24):
    sunrise, sunset, next_sunrise, core_muhurtas = muhurat_rules.daily_context(
        d, lat, lon, tz, hour24
    )
    state = panchang.state_at(sunrise)
    month = panchang.lunar_month_info(sunrise, state)
    reasons = []

    if d.strftime("%A") not in profile["allowed_weekdays"]:
        reasons.append("prohibited-weekday")

    if profile.get("block_adhika") and month.get("adhika"):
        reasons.append("adhika-month")

    base = [(sunrise, next_sunrise)]

    tithi_rows = allowed_state_intervals(
        sunrise, next_sunrise,
        "tithi_id", "tithi",
        profile.get("allowed_tithis"),
        profile.get("blocked_tithis"),
    )
    nak_rows = allowed_state_intervals(
        sunrise, next_sunrise,
        "nakshatra_id", "nakshatra",
        profile.get("allowed_nakshatras"),
        [],
    )
    candidate = intersect_rows(base, tithi_rows)
    candidate = intersect_rows(candidate, nak_rows)

    blocks = []
    for key in ("rahu_kaal", "yamaganda", "gulika"):
        row = core_muhurtas.get(key)
        if row:
            blocks.append((row["start"], row["end"], key))
    blocks.extend(
        muhurat_rules.state_intervals(
            sunrise, next_sunrise, "karana_id", "karana", "Vishti"
        )
    )
    blocks.extend(
        blocked_state_intervals(
            sunrise, next_sunrise,
            "yoga_id", "yoga",
            profile.get("blocked_yogas", []),
        )
    )

    clean = []
    for a0, a1 in candidate:
        clean.extend(muhurat_rules.subtract_intervals(a0, a1, blocks))

    windows = []
    for start, end in clean:
        if (end - start).total_seconds() < profile["minimum_minutes"] * 60:
            continue
        mid = start + (end - start) / 2
        combust = []
        for name in profile.get("block_combust_planets", []):
            ps = planetary.planet_state(name, mid)
            if ps.get("combust"):
                combust.append({
                    "planet": name,
                    "separation_deg": ps.get("sun_separation_deg"),
                    "limit_deg": ps.get("combustion_limit_deg"),
                })
        if combust:
            continue
        row = window_payload(start, end, d, hour24)
        row["positive_overlaps"] = [
            key for key in ("abhijit", "vijaya")
            if core_muhurtas.get(key) and muhurat_rules.overlap(
                start, end,
                datetime.fromisoformat(core_muhurtas[key]["start"]),
                datetime.fromisoformat(core_muhurtas[key]["end"]),
            )
        ]
        row["combustion_clear"] = True
        windows.append(row)

    if not tithi_rows:
        reasons.append("auspicious-tithi-unavailable")
    if not nak_rows:
        reasons.append("auspicious-nakshatra-unavailable")
    if not windows and not reasons:
        reasons.append("no-clean-window")

    eligible = not reasons and bool(windows)
    return {
        "date": d.isoformat(),
        "weekday": d.strftime("%A"),
        "eligible": eligible,
        "reasons": reasons,
        "lunar_month": month.get("amanta"),
        "purnimanta_month": month.get("purnimanta"),
        "adhika": bool(month.get("adhika")),
        "sunrise": sunrise.isoformat(),
        "next_sunrise": next_sunrise.isoformat(),
        "windows": windows if eligible else [],
    }


def calculate_month(profile_key, selected, lat, lon, tz, hour24):
    profile = PROFILES[profile_key]
    _, count = calendar.monthrange(selected.year, selected.month)
    days = [
        evaluate_day(
            selected.replace(day=day), lat, lon, tz, profile, hour24
        )
        for day in range(1, count + 1)
    ]
    auspicious = [row for row in days if row["eligible"]]
    return {
        "profile": profile_key,
        "title": profile["title"],
        "profile_version": ENGINE_VERSION,
        "year": selected.year,
        "month": selected.month,
        "month_name": selected.strftime("%B"),
        "rule_profile": profile,
        "auspicious_days": auspicious,
        "days": days,
    }


def main():
    payload = json.loads(sys.stdin.read() or "{}")
    profile_key = str(payload.get("profile") or "vivah").lower()
    if profile_key not in PROFILES:
        raise ValueError("Unsupported Muhurat profile")

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

    result = calculate_month(
        profile_key, selected, lat, lon, tz, hour24
    )

    print(json.dumps({
        "ok": True,
        "engine": {
            "name": "tithika-specialized-muhurat",
            "version": ENGINE_VERSION,
            "base_engine": muhurat_rules.ENGINE_VERSION,
            "ayanamsha": "Lahiri / Chitrapaksha",
            "status": "profile-rule-selected",
        },
        "location": {
            "city": (payload.get("city") or "Current location").strip()[:120],
            "lat": lat,
            "lon": lon,
            "timezone": timezone_name,
        },
        **result,
        "note": (
            "Candidate windows use a versioned Tithika traditional Muhurat profile "
            "on the shared Panchang engine. Regional/customary rules can differ; "
            "each accepted window exposes its Tithi/Nakshatra/Yoga evidence."
        ),
    }, ensure_ascii=False))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(json.dumps({
            "ok": False,
            "error": str(exc),
            "code": "SPECIALIZED_MUHURAT_FAILED",
        }))
        sys.exit(1)
