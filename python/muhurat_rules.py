#!/usr/bin/env python3
"""
Shared Tithika Muhurat rule engine foundation.

This module does not decide Vivah, Griha Pravesh, vehicle, property or Sanskar
Muhurtas. Those specialized profiles belong to the next stage.

It provides the reusable mechanics they all need:
- local sunrise/sunset and core daily Muhurta periods,
- Rahu Kaal / Yamaganda / Gulika exclusion,
- Vishti (Bhadra) Karana exclusion,
- interval subtraction and merging,
- midpoint Panchang evidence,
- configurable allow/block constraints for weekday, Tithi, Nakshatra, Yoga,
  Karana and minimum duration,
- auditable pass/reject reasons for every candidate window.
"""
from __future__ import annotations

import json
import sys
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import panchang

ENGINE_VERSION = "0.1.0"

DEFAULT_PROFILE = {
    "name": "foundation",
    "minimum_minutes": 24,
    "exclude_periods": ["rahu_kaal", "yamaganda", "gulika"],
    "blocked_karanas": ["Vishti"],
    "allowed_weekdays": [],
    "blocked_weekdays": [],
    "allowed_tithis": [],
    "blocked_tithis": [],
    "allowed_nakshatras": [],
    "blocked_nakshatras": [],
    "allowed_yogas": [],
    "blocked_yogas": [],
    "allowed_karanas": [],
}

PROFILE_SCHEMA = {
    "minimum_minutes": "positive integer",
    "exclude_periods": ["rahu_kaal", "yamaganda", "gulika"],
    "allowed_weekdays": "Monday..Sunday",
    "blocked_weekdays": "Monday..Sunday",
    "allowed_tithis": "Tithi display names",
    "blocked_tithis": "Tithi display names",
    "allowed_nakshatras": "Nakshatra names",
    "blocked_nakshatras": "Nakshatra names",
    "allowed_yogas": "Yoga names",
    "blocked_yogas": "Yoga names",
    "allowed_karanas": "Karana names",
    "blocked_karanas": "Karana names",
}


def parse_dt(value):
    return datetime.fromisoformat(value) if isinstance(value, str) else value


def overlap(a0, a1, b0, b1):
    start = max(a0, b0)
    end = min(a1, b1)
    return (start, end) if start < end else None


def merge_intervals(rows):
    valid = sorted(
        [(parse_dt(a), parse_dt(b), label) for a, b, label in rows if a and b and parse_dt(a) < parse_dt(b)],
        key=lambda row: row[0],
    )
    merged = []
    for start, end, label in valid:
        if not merged or start > merged[-1][1]:
            merged.append([start, end, {label}])
        else:
            merged[-1][1] = max(merged[-1][1], end)
            merged[-1][2].add(label)
    return [(a, b, sorted(labels)) for a, b, labels in merged]


def subtract_intervals(start, end, blocks):
    clean = [(start, end)]
    for b0, b1, _labels in merge_intervals(blocks):
        next_rows = []
        for a0, a1 in clean:
            ov = overlap(a0, a1, b0, b1)
            if not ov:
                next_rows.append((a0, a1))
                continue
            if a0 < ov[0]:
                next_rows.append((a0, ov[0]))
            if ov[1] < a1:
                next_rows.append((ov[1], a1))
        clean = next_rows
    return clean


def state_intervals(start, end, key, name_key, wanted):
    rows = []
    cursor = start
    while cursor < end:
        state = panchang.state_at(cursor)
        state_id = state[key]
        transition = panchang.find_transition(cursor, end, key, state_id)
        stop = transition or end
        if state[name_key] == wanted:
            rows.append((cursor, stop, wanted))
        if not transition:
            break
        cursor = transition + timedelta(seconds=1)
    return rows


def daily_context(d: date, lat, lon, tz, hour24=False):
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
    next_sunrise = panchang.rise_set(
        d + timedelta(days=1), lat, lon, tz,
        panchang.astronomy.Body.Sun,
        panchang.astronomy.Direction.Rise,
    )
    if not sunrise or not sunset or not next_sunrise:
        raise ValueError("Sunrise/sunset unavailable for this latitude/date")
    if sunset <= sunrise:
        sunset += timedelta(days=1)
    if next_sunrise <= sunset:
        next_sunrise += timedelta(days=1)

    muhurtas = panchang.daily_muhurtas(
        d, sunrise, sunset, next_sunrise, lat, lon, tz, hour24
    )
    return sunrise, sunset, next_sunrise, muhurtas


def normalized_profile(raw):
    profile = {**DEFAULT_PROFILE}
    if isinstance(raw, dict):
        for key in PROFILE_SCHEMA:
            if key in raw:
                profile[key] = raw[key]
        if raw.get("name"):
            profile["name"] = str(raw["name"])[:80]

    profile["minimum_minutes"] = max(1, int(profile["minimum_minutes"]))
    for key in (
        "exclude_periods", "blocked_karanas", "allowed_weekdays",
        "blocked_weekdays", "allowed_tithis", "blocked_tithis",
        "allowed_nakshatras", "blocked_nakshatras",
        "allowed_yogas", "blocked_yogas", "allowed_karanas",
    ):
        value = profile.get(key) or []
        if not isinstance(value, list):
            raise ValueError(f"{key} must be a list")
        profile[key] = [str(x) for x in value]
    return profile


def evidence_at(moment):
    state = panchang.state_at(moment)
    return {
        "tithi": state["tithi"],
        "tithi_id": state["tithi_id"],
        "paksha": state["paksha"],
        "nakshatra": state["nakshatra"],
        "nakshatra_id": state["nakshatra_id"],
        "nakshatra_pada": state["nakshatra_pada"],
        "yoga": state["yoga"],
        "yoga_id": state["yoga_id"],
        "karana": state["karana"],
        "karana_id": state["karana_id"],
        "moon_rashi": state["moon_rashi"],
        "sun_rashi": state["sun_rashi"],
    }


def list_rule(value, allowed, blocked, label):
    reasons = []
    passed = True
    if allowed and value not in allowed:
        passed = False
        reasons.append(f"{label} {value} is not in allowed set")
    if blocked and value in blocked:
        passed = False
        reasons.append(f"{label} {value} is blocked")
    return passed, reasons


def evaluate_window(
    d,
    start,
    end,
    profile,
    muhurtas,
    excluded_labels,
    hour24=False,
):
    midpoint = start + (end - start) / 2
    ev = evidence_at(midpoint)
    reasons = []
    passed = True
    weekday = d.strftime("%A")

    checks = [
        list_rule(weekday, profile["allowed_weekdays"], profile["blocked_weekdays"], "weekday"),
        list_rule(ev["tithi"], profile["allowed_tithis"], profile["blocked_tithis"], "Tithi"),
        list_rule(ev["nakshatra"], profile["allowed_nakshatras"], profile["blocked_nakshatras"], "Nakshatra"),
        list_rule(ev["yoga"], profile["allowed_yogas"], profile["blocked_yogas"], "Yoga"),
        list_rule(ev["karana"], profile["allowed_karanas"], profile["blocked_karanas"], "Karana"),
    ]
    for ok, detail in checks:
        passed = passed and ok
        reasons.extend(detail)

    duration = (end - start).total_seconds() / 60.0
    if duration < profile["minimum_minutes"]:
        passed = False
        reasons.append(
            f"duration {duration:.1f}m is below minimum {profile['minimum_minutes']}m"
        )

    positive = []
    for key in ("abhijit", "vijaya"):
        row = muhurtas.get(key)
        if row and overlap(start, end, parse_dt(row["start"]), parse_dt(row["end"])):
            positive.append(key)

    return {
        "start": start.isoformat(),
        "end": end.isoformat(),
        "start_label": panchang.transition_label(start, d, hour24),
        "end_label": panchang.transition_label(end, d, hour24),
        "duration_minutes": round(duration, 2),
        "midpoint": midpoint.isoformat(),
        "weekday": weekday,
        "panchang": ev,
        "positive_overlaps": positive,
        "excluded_periods_removed": excluded_labels,
        "accepted": passed,
        "reasons": reasons,
    }


def calculate_day(d, lat, lon, tz, profile, hour24=False):
    sunrise, sunset, next_sunrise, muhurtas = daily_context(
        d, lat, lon, tz, hour24
    )

    blocks = []
    excluded_labels = []
    for key in profile["exclude_periods"]:
        row = muhurtas.get(key)
        if not row:
            continue
        blocks.append((row["start"], row["end"], key))
        excluded_labels.append(key)

    if "Vishti" in profile["blocked_karanas"]:
        blocks.extend(
            state_intervals(
                sunrise, sunset, "karana_id", "karana", "Vishti"
            )
        )
        excluded_labels.append("Vishti/Bhadra")

    clean = subtract_intervals(sunrise, sunset, blocks)
    windows = [
        evaluate_window(
            d, start, end, profile, muhurtas,
            sorted(set(excluded_labels)), hour24
        )
        for start, end in clean
    ]

    return {
        "date": d.isoformat(),
        "weekday": d.strftime("%A"),
        "sunrise": sunrise.isoformat(),
        "sunset": sunset.isoformat(),
        "next_sunrise": next_sunrise.isoformat(),
        "muhurtas": muhurtas,
        "blocked_intervals": [
            {
                "start": a.isoformat(),
                "end": b.isoformat(),
                "labels": labels,
            }
            for a, b, labels in merge_intervals(blocks)
        ],
        "windows": windows,
        "accepted_windows": [row for row in windows if row["accepted"]],
    }


def main():
    payload = json.loads(sys.stdin.read() or "{}")
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
    profile = normalized_profile(payload.get("profile"))
    day = calculate_day(selected, lat, lon, tz, profile, hour24)

    print(json.dumps({
        "ok": True,
        "engine": {
            "name": "tithika-muhurat-rules",
            "version": ENGINE_VERSION,
            "status": "shared-foundation",
        },
        "location": {
            "city": (payload.get("city") or "Current location").strip()[:120],
            "lat": lat,
            "lon": lon,
            "timezone": timezone_name,
        },
        "profile": profile,
        "profile_schema": PROFILE_SCHEMA,
        "day": day,
        "note": (
            "This is the common Muhurat filtering substrate. It removes shared "
            "inauspicious intervals and exposes Panchang evidence. Specialized "
            "Vivah, Griha Pravesh, property, vehicle and Sanskar acceptance rules "
            "are intentionally layered on top in the next stage."
        ),
    }, ensure_ascii=False))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(json.dumps({
            "ok": False,
            "error": str(exc),
            "code": "MUHURAT_RULE_CALCULATION_FAILED",
        }))
        sys.exit(1)
