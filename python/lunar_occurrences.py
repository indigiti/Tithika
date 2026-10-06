#!/usr/bin/env python3
"""
Tithika lunar occurrence engine.

Finds exact Tithi windows using Astronomy Engine's arbitrary Moon-phase search.
This is the astronomical substrate for Vrat/festival rules. It intentionally
separates Tithi occurrence from religious observance selection.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import panchang
import vrat_rules

KINDS = {
    "ekadashi": [
        {"name": "Shukla Ekadashi", "tithi_id": 10, "start_angle": 120.0, "end_angle": 132.0, "dwadashi_end_angle": 144.0, "paksha": "Shukla Paksha"},
        {"name": "Krishna Ekadashi", "tithi_id": 25, "start_angle": 300.0, "end_angle": 312.0, "dwadashi_end_angle": 324.0, "paksha": "Krishna Paksha"},
    ],
    "purnima": [
        {"name": "Purnima", "tithi_id": 14, "start_angle": 168.0, "end_angle": 180.0, "paksha": "Shukla Paksha"},
    ],
    "amavasya": [
        {"name": "Amavasya", "tithi_id": 29, "start_angle": 348.0, "end_angle": 0.0, "paksha": "Krishna Paksha"},
    ],
}

def candidate_sunrises(start_dt, end_dt, target_id, lat, lon, tz):
    d = (start_dt - timedelta(days=1)).date()
    last = (end_dt + timedelta(days=1)).date()
    rows = []
    while d <= last:
        sunrise = panchang.rise_set(
            d, lat, lon, tz, panchang.astronomy.Body.Sun, panchang.astronomy.Direction.Rise
        )
        if sunrise is not None:
            state = panchang.state_at(sunrise)
            if state["tithi_id"] == target_id:
                rows.append({
                    "date": d.isoformat(),
                    "weekday": d.strftime("%A"),
                    "sunrise": sunrise.isoformat(),
                    "sunrise_label": panchang.fmt(sunrise, False),
                    "tithi": state["tithi"],
                    "paksha": state["paksha"],
                })
        d += timedelta(days=1)
    return rows

def add_ekadashi_parana(candidates, dwadashi_start, dwadashi_end, lat, lon, tz, hour24):
    """Attach astronomical Parana constraints without selecting a sectarian fasting date."""
    hari_vasara_end = dwadashi_start + (dwadashi_end - dwadashi_start) / 4

    for row in candidates:
        fasting_date = datetime.strptime(row["date"], "%Y-%m-%d").date()
        parana_date = fasting_date + timedelta(days=1)
        next_sunrise = panchang.rise_set(
            parana_date, lat, lon, tz,
            panchang.astronomy.Body.Sun, panchang.astronomy.Direction.Rise
        )
        if next_sunrise is None:
            row["parana"] = None
            continue

        earliest = max(next_sunrise, hari_vasara_end)
        dwadashi_after_sunrise = dwadashi_end > next_sunrise
        deadline = dwadashi_end if dwadashi_after_sunrise else None
        valid_window = deadline is None or earliest < deadline

        row["parana"] = {
            "date": parana_date.isoformat(),
            "next_sunrise": next_sunrise.isoformat(),
            "next_sunrise_label": panchang.transition_label(next_sunrise, parana_date, hour24),
            "hari_vasara_end": hari_vasara_end.isoformat(),
            "hari_vasara_end_label": panchang.transition_label(hari_vasara_end, parana_date, hour24),
            "earliest": earliest.isoformat(),
            "earliest_label": panchang.transition_label(earliest, parana_date, hour24),
            "dwadashi_end": dwadashi_end.isoformat(),
            "dwadashi_end_label": panchang.transition_label(dwadashi_end, parana_date, hour24),
            "deadline": deadline.isoformat() if deadline else None,
            "deadline_label": (
                panchang.transition_label(deadline, parana_date, hour24) if deadline else None
            ),
            "status": (
                "candidate-window"
                if valid_window and deadline
                else "dwadashi-ended-before-sunrise"
                if deadline is None
                else "requires-special-rule"
            ),
        }

    return candidates

def events_for_rule(year, rule, lat, lon, tz, hour24):
    search_local = datetime(year - 1, 12, 10, 0, 0, tzinfo=tz)
    cursor = panchang.astronomy_time(search_local)
    events = []

    for _ in range(16):
        start_event = panchang.astronomy.SearchMoonPhase(rule["start_angle"], cursor, 40.0)
        if start_event is None:
            break
        start_dt = panchang.datetime_from_astronomy(start_event, tz)
        end_event = panchang.astronomy.SearchMoonPhase(rule["end_angle"], start_event, 3.0)
        if end_event is None:
            cursor = panchang.astronomy_time(start_dt + timedelta(days=2))
            continue
        end_dt = panchang.datetime_from_astronomy(end_event, tz)

        candidates = candidate_sunrises(start_dt, end_dt, rule["tithi_id"], lat, lon, tz)

        observance = None
        if "dwadashi_end_angle" in rule:
            dwadashi_end_event = panchang.astronomy.SearchMoonPhase(
                rule["dwadashi_end_angle"], end_event, 3.0
            )
            if dwadashi_end_event is not None:
                dwadashi_end_dt = panchang.datetime_from_astronomy(dwadashi_end_event, tz)
                candidates = add_ekadashi_parana(
                    candidates, end_dt, dwadashi_end_dt, lat, lon, tz, hour24
                )
                observance = vrat_rules.integrated_ekadashi_observance(
                    rule, start_dt, end_dt, dwadashi_end_dt,
                    lat, lon, tz, hour24
                )

        intersects_year = (
            start_dt.year == year or end_dt.year == year or
            any(int(row["date"][:4]) == year for row in candidates)
        )
        if intersects_year:
            state = panchang.state_at(start_dt + timedelta(minutes=2))
            month_info = panchang.lunar_month_info(start_dt + timedelta(hours=2), state)
            events.append({
                "name": rule["name"],
                "tithi_id": rule["tithi_id"],
                "paksha": rule["paksha"],
                "start": start_dt.isoformat(),
                "start_label": panchang.transition_label(start_dt, start_dt.date(), hour24),
                "end": end_dt.isoformat(),
                "end_label": panchang.transition_label(end_dt, start_dt.date(), hour24),
                "amanta_month": month_info.get("amanta"),
                "purnimanta_month": month_info.get("purnimanta"),
                "sunrise_candidates": candidates,
                "observance": observance,
            })

        if start_dt.year > year and start_dt.month > 1:
            break
        cursor = panchang.astronomy_time(start_dt + timedelta(days=2))

    return events

def main():
    payload = json.loads(sys.stdin.read() or "{}")
    kind = str(payload.get("kind") or "ekadashi").lower()
    if kind not in KINDS:
        raise ValueError("Unsupported lunar occurrence kind")

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

    events = []
    for rule in KINDS[kind]:
        events.extend(events_for_rule(selected.year, rule, lat, lon, tz, hour24))
    events.sort(key=lambda row: row["start"])

    print(json.dumps({
        "ok": True,
        "kind": kind,
        "year": selected.year,
        "location": {"city": city, "lat": lat, "lon": lon, "timezone": timezone_name},
        "engine": {
            "name": "tithika-lunar-occurrences",
            "version": panchang.ENGINE_VERSION,
            "source": "Astronomy Engine Moon phase search + Tithika sunrise state",
            "status": "astronomical-occurrence",
        },
        "events": events,
        "observance_status": (
            "smarta-vaishnava-iskcon-mahadwadashi-integrated"
            if kind == "ekadashi" else "astronomical-occurrence"
        ),
        "note": (
            "Ekadashi events include Smarta, Vaishnava and ISKCON-compatible fasting-date profiles, Arunodaya/Vriddhi selection, Mahadwadashi override and explicit Parana constraints."
            if kind == "ekadashi"
            else "These are exact Tithi occurrence windows with local sunrise candidates; festival-specific rules may choose a date differently."
        ),
    }, ensure_ascii=False))

if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(json.dumps({"ok": False, "error": str(exc), "code": "LUNAR_OCCURRENCE_FAILED"}))
        sys.exit(1)