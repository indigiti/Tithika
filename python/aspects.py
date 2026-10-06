#!/usr/bin/env python3
"""
Tithika planetary aspects and Graha Yuddha engine.

Mutual aspects:
- exact geocentric sidereal longitude aspects at 0, 60, 90, 120, 180 degrees
- classical visible planets; optional Moon-only filter for lunar aspects
- exact events are scan-bracketed and binary refined

Graha Yuddha profile:
- Mars, Mercury, Jupiter, Venus, Saturn only
- same Rashi
- longitudinal separation <= 1 degree
- lower degree in that Rashi is victorious at a given instant

The Yuddha rule matches the explicit rule used by the reference product.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timedelta
from itertools import combinations
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import panchang
import planetary

ENGINE_VERSION = "0.1.0"

ASPECTS = {
    0.0: "Conjunction",
    60.0: "Sextile",
    90.0: "Square",
    120.0: "Trine",
    180.0: "Opposition",
}

ASPECT_PLANETS = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"]
YUDDHA_PLANETS = ["Mars", "Mercury", "Jupiter", "Venus", "Saturn"]


def separation(a: float, b: float) -> float:
    return abs(planetary.signed_delta(a, b))


def pair_separation(a: str, b: str, moment: datetime) -> float:
    la = planetary.sidereal_coordinates(a, moment)[0]
    lb = planetary.sidereal_coordinates(b, moment)[0]
    return separation(la, lb)


def refine_aspect(a: str, b: str, target: float, left: datetime, right: datetime) -> datetime:
    lo, hi = left, right
    vlo = pair_separation(a, b, lo) - target
    for _ in range(45):
        mid = lo + (hi - lo) / 2
        vm = pair_separation(a, b, mid) - target
        if (vlo <= 0) == (vm <= 0):
            lo = mid
            vlo = vm
        else:
            hi = mid
    return hi


def aspect_events(year: int, tz: ZoneInfo, lunar_only: bool = False, conjunction_only: bool = False):
    start = datetime(year, 1, 1, 0, 0, tzinfo=tz)
    end = datetime(year + 1, 1, 1, 0, 0, tzinfo=tz)
    step = timedelta(hours=3)

    pairs = []
    for a, b in combinations(ASPECT_PLANETS, 2):
        if lunar_only and "Moon" not in (a, b):
            continue
        pairs.append((a, b))

    targets = {0.0: "Conjunction"} if conjunction_only else ASPECTS
    rows = []

    for a, b in pairs:
        left = start - step
        sep_left = pair_separation(a, b, left)
        probe = left + step
        while probe <= end + step:
            sep_now = pair_separation(a, b, probe)
            for target, label in targets.items():
                v0 = sep_left - target
                v1 = sep_now - target
                # Exact crossings; conjunction uses a small minimum detector below.
                if target > 0 and (v0 == 0 or v1 == 0 or (v0 < 0) != (v1 < 0)):
                    event = refine_aspect(a, b, target, probe-step, probe)
                    if start <= event < end:
                        pa = planetary.planet_state(a, event)
                        pb = planetary.planet_state(b, event)
                        rows.append({
                            "datetime": event.isoformat(),
                            "date": event.date().isoformat(),
                            "planet1": a,
                            "planet2": b,
                            "aspect": label,
                            "angle": target,
                            "separation_deg": round(pair_separation(a, b, event), 8),
                            "planet1_rashi": pa["rashi"],
                            "planet2_rashi": pb["rashi"],
                            "planet1_longitude": pa["longitude"],
                            "planet2_longitude": pb["longitude"],
                        })
            # Conjunction cannot be found by sign crossing of absolute separation around zero.
            if 0.0 in targets and sep_now > sep_left:
                before = probe - 2*step
                if before >= start-step:
                    sep_before = pair_separation(a, b, before)
                    if sep_left <= sep_before and sep_left <= sep_now and sep_left < 3.0:
                        event = minimize_separation(a, b, before, probe)
                        sep_event = pair_separation(a, b, event)
                        if sep_event < 0.03 and start <= event < end:
                            pa = planetary.planet_state(a, event)
                            pb = planetary.planet_state(b, event)
                            rows.append({
                                "datetime": event.isoformat(),
                                "date": event.date().isoformat(),
                                "planet1": a,
                                "planet2": b,
                                "aspect": "Conjunction",
                                "angle": 0.0,
                                "separation_deg": round(sep_event, 8),
                                "planet1_rashi": pa["rashi"],
                                "planet2_rashi": pb["rashi"],
                                "planet1_longitude": pa["longitude"],
                                "planet2_longitude": pb["longitude"],
                            })
            sep_left = sep_now
            probe += step

    dedup = {}
    for row in rows:
        key = (row["planet1"], row["planet2"], row["aspect"], row["datetime"][:16])
        dedup[key] = row
    return sorted(dedup.values(), key=lambda x: x["datetime"])


def minimize_separation(a: str, b: str, left: datetime, right: datetime) -> datetime:
    lo, hi = left, right
    # Ternary minimization is stable within a bracket around a close approach.
    for _ in range(55):
        span = hi - lo
        m1 = lo + span / 3
        m2 = hi - span / 3
        if pair_separation(a, b, m1) <= pair_separation(a, b, m2):
            hi = m2
        else:
            lo = m1
    return lo + (hi-lo)/2


def yuddha_condition(a: str, b: str, moment: datetime) -> tuple[bool, dict, dict]:
    pa = planetary.planet_state(a, moment)
    pb = planetary.planet_state(b, moment)
    same = pa["rashi_id"] == pb["rashi_id"]
    sep = abs(pa["degree_in_rashi"] - pb["degree_in_rashi"]) if same else 999.0
    return same and sep <= 1.0, pa, pb


def refine_yuddha_boundary(a: str, b: str, left: datetime, right: datetime, left_inside: bool) -> datetime:
    lo, hi = left, right
    for _ in range(45):
        mid = lo + (hi-lo)/2
        inside, _, _ = yuddha_condition(a, b, mid)
        if inside == left_inside:
            lo = mid
        else:
            hi = mid
    return hi


def yuddha_winner(pa: dict, pb: dict) -> str | None:
    if pa["rashi_id"] != pb["rashi_id"]:
        return None
    if abs(pa["degree_in_rashi"] - pb["degree_in_rashi"]) < 1e-7:
        return None
    return pa["name"] if pa["degree_in_rashi"] < pb["degree_in_rashi"] else pb["name"]


def graha_yuddha_events(year: int, tz: ZoneInfo):
    start = datetime(year, 1, 1, 0, 0, tzinfo=tz)
    end = datetime(year + 1, 1, 1, 0, 0, tzinfo=tz)
    step = timedelta(hours=1)
    rows = []

    for a, b in combinations(YUDDHA_PLANETS, 2):
        left = start - step
        inside, _, _ = yuddha_condition(a, b, left)
        period_start = left if inside else None
        probe = left + step

        while probe <= end + step:
            now_inside, _, _ = yuddha_condition(a, b, probe)
            if now_inside != inside:
                boundary = refine_yuddha_boundary(a, b, probe-step, probe, inside)
                if now_inside:
                    period_start = boundary
                elif period_start is not None:
                    period_end = boundary
                    if period_end > start and period_start < end:
                        clipped_start = max(period_start, start)
                        clipped_end = min(period_end, end)
                        peak = minimize_separation(a, b, clipped_start, clipped_end)
                        entry_a = planetary.planet_state(a, clipped_start + timedelta(seconds=2))
                        entry_b = planetary.planet_state(b, clipped_start + timedelta(seconds=2))
                        exit_a = planetary.planet_state(a, clipped_end - timedelta(seconds=2))
                        exit_b = planetary.planet_state(b, clipped_end - timedelta(seconds=2))
                        peak_a = planetary.planet_state(a, peak)
                        rows.append({
                            "planet1": a,
                            "planet2": b,
                            "start": clipped_start.isoformat(),
                            "end": clipped_end.isoformat(),
                            "date": clipped_start.date().isoformat(),
                            "rashi": peak_a["rashi"],
                            "closest": peak.isoformat(),
                            "closest_separation_deg": round(pair_separation(a, b, peak), 8),
                            "entry_winner": yuddha_winner(entry_a, entry_b),
                            "exit_winner": yuddha_winner(exit_a, exit_b),
                            "rule": "same-rashi-within-1-degree-lower-degree-wins",
                        })
                    period_start = None
                inside = now_inside
            probe += step

    return sorted(rows, key=lambda x: x["start"])


def snapshot(moment: datetime):
    states = {name: planetary.planet_state(name, moment) for name in ASPECT_PLANETS}
    rows = []
    for a, b in combinations(ASPECT_PLANETS, 2):
        sep = separation(states[a]["longitude"], states[b]["longitude"])
        closest = min(ASPECTS.keys(), key=lambda angle: abs(sep-angle))
        orb = abs(sep-closest)
        if orb <= 8.0:
            rows.append({
                "planet1": a,
                "planet2": b,
                "aspect": ASPECTS[closest],
                "exact_angle": closest,
                "separation_deg": round(sep, 5),
                "orb_deg": round(orb, 5),
            })
    return sorted(rows, key=lambda x: x["orb_deg"])


def graha_yuddha_snapshot(moment: datetime):
    rows = []
    states = {name: planetary.planet_state(name, moment) for name in YUDDHA_PLANETS}
    for a, b in combinations(YUDDHA_PLANETS, 2):
        pa, pb = states[a], states[b]
        if pa["rashi_id"] != pb["rashi_id"]:
            continue
        sep = abs(pa["degree_in_rashi"] - pb["degree_in_rashi"])
        if sep <= 1.0:
            rows.append({
                "planet1": a,
                "planet2": b,
                "rashi": pa["rashi"],
                "separation_deg": round(sep, 8),
                "winner": yuddha_winner(pa, pb),
                "loser": (
                    b if yuddha_winner(pa, pb) == a
                    else a if yuddha_winner(pa, pb) == b
                    else None
                ),
                "rule": "same-rashi-within-1-degree-lower-degree-wins",
            })
    return rows


def main():
    payload = json.loads(sys.stdin.read() or "{}")
    mode = str(payload.get("mode") or "mutual").lower()
    timezone_name = payload.get("timezone") or "Asia/Kolkata"
    try:
        tz = ZoneInfo(timezone_name)
    except ZoneInfoNotFoundError:
        timezone_name = "Asia/Kolkata"
        tz = ZoneInfo(timezone_name)

    d = datetime.strptime(
        payload.get("date") or datetime.now(tz).strftime("%Y-%m-%d"), "%Y-%m-%d"
    ).date()
    year = d.year

    if mode == "mutual":
        events = aspect_events(year, tz)
    elif mode == "lunar":
        events = aspect_events(year, tz, lunar_only=True)
    elif mode == "conjunctions":
        events = aspect_events(year, tz, conjunction_only=True)
    elif mode == "graha-yuddha":
        events = graha_yuddha_events(year, tz)
    else:
        raise ValueError("Unsupported aspects mode")

    print(json.dumps({
        "ok": True,
        "mode": mode,
        "year": year,
        "timezone": timezone_name,
        "engine": {
            "name": "tithika-aspects",
            "version": ENGINE_VERSION,
            "ayanamsha": "Lahiri / Chitrapaksha",
            "coordinates": "sidereal geocentric longitude",
        },
        "events": events,
        "note": (
            "Graha Yuddha uses same Rashi, <=1° longitude separation among Mars, "
            "Mercury, Jupiter, Venus and Saturn; lower degree is victorious."
            if mode == "graha-yuddha"
            else "Aspect events are exact sidereal geocentric longitude angles."
        ),
    }, ensure_ascii=False))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(json.dumps({"ok": False, "error": str(exc), "code": "ASPECT_CALCULATION_FAILED"}))
        sys.exit(1)
