#!/usr/bin/env python3
"""
Tithika location-sensitive Vrat observance engine.

Supported observances
---------------------
- Pradosh: Trayodashi overlapping local Pradosh Kaal after sunset.
- Sankashti Chaturthi: Krishna Chaturthi prevailing at local moonrise.
- Masik Shivaratri: Krishna Chaturdashi prevailing during local Nishita Kaal.

The engine intentionally consumes the shared astronomical Panchang core and
keeps observance selection separate from raw Tithi occurrence.
"""
from __future__ import annotations

import json
import sys
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import panchang

WEEKDAY_PRADOSH = {
    0: "Soma Pradosh",
    1: "Bhauma Pradosh",
    2: "Budha Pradosh",
    3: "Guru Pradosh",
    4: "Shukra Pradosh",
    5: "Shani Pradosh",
    6: "Ravi Pradosh",
}

RULES = {
    "pradosh_shukla": {
        "tithi_id": 12,
        "start_angle": 144.0,
        "end_angle": 156.0,
        "paksha": "Shukla Paksha",
    },
    "pradosh_krishna": {
        "tithi_id": 27,
        "start_angle": 324.0,
        "end_angle": 336.0,
        "paksha": "Krishna Paksha",
    },
    "sankashti": {
        "tithi_id": 18,
        "start_angle": 216.0,
        "end_angle": 228.0,
        "paksha": "Krishna Paksha",
    },
    "shivaratri": {
        "tithi_id": 28,
        "start_angle": 336.0,
        "end_angle": 348.0,
        "paksha": "Krishna Paksha",
    },
}


def iter_dates(start_dt: datetime, end_dt: datetime):
    d = start_dt.date() - timedelta(days=1)
    last = end_dt.date() + timedelta(days=1)
    while d <= last:
        yield d
        d += timedelta(days=1)


def phase_window(cursor: panchang.astronomy.Time, rule: dict):
    start_event = panchang.astronomy.SearchMoonPhase(rule["start_angle"], cursor, 40.0)
    if start_event is None:
        return None, None
    end_event = panchang.astronomy.SearchMoonPhase(rule["end_angle"], start_event, 3.0)
    return start_event, end_event


def window_payload(start: datetime, end: datetime, anchor: date, hour24: bool) -> dict:
    return {
        "start": start.isoformat(),
        "end": end.isoformat(),
        "start_label": panchang.transition_label(start, anchor, hour24),
        "end_label": panchang.transition_label(end, anchor, hour24),
        "duration_minutes": round((end - start).total_seconds() / 60.0, 2),
    }


def lunar_month_at(moment: datetime) -> dict:
    state = panchang.state_at(moment)
    return panchang.lunar_month_info(moment, state)


def pradosh_candidate(
    d: date,
    tithi_start: datetime,
    tithi_end: datetime,
    lat: float,
    lon: float,
    tz: ZoneInfo,
    hour24: bool,
):
    sunset = panchang.rise_set(
        d, lat, lon, tz, panchang.astronomy.Body.Sun, panchang.astronomy.Direction.Set
    )
    next_sunrise = panchang.rise_set(
        d + timedelta(days=1),
        lat,
        lon,
        tz,
        panchang.astronomy.Body.Sun,
        panchang.astronomy.Direction.Rise,
    )
    if sunset is None or next_sunrise is None:
        return None
    if next_sunrise <= sunset:
        next_sunrise += timedelta(days=1)

    # Traditional Pradosh Kaal is the opening three Muhurtas of the night.
    # With 15 Muhurtas in the sunset->next-sunrise span, that is 1/5 night.
    pradosh_end = sunset + (next_sunrise - sunset) / 5
    overlap_start = max(sunset, tithi_start)
    overlap_end = min(pradosh_end, tithi_end)
    if overlap_start >= overlap_end:
        return None

    return {
        "date": d,
        "sunset": sunset,
        "next_sunrise": next_sunrise,
        "pradosh_start": sunset,
        "pradosh_end": pradosh_end,
        "puja_start": overlap_start,
        "puja_end": overlap_end,
        "overlap_seconds": (overlap_end - overlap_start).total_seconds(),
        "puja": window_payload(overlap_start, overlap_end, d, hour24),
    }


def sankashti_candidate(
    d: date,
    tithi_start: datetime,
    tithi_end: datetime,
    lat: float,
    lon: float,
    tz: ZoneInfo,
    hour24: bool,
):
    moonrise = panchang.rise_set(
        d, lat, lon, tz, panchang.astronomy.Body.Moon, panchang.astronomy.Direction.Rise
    )
    sunrise = panchang.rise_set(
        d, lat, lon, tz, panchang.astronomy.Body.Sun, panchang.astronomy.Direction.Rise
    )
    if moonrise is None or not (tithi_start <= moonrise < tithi_end):
        return None
    return {
        "date": d,
        "sunrise": sunrise,
        "moonrise": moonrise,
        "moonrise_label": panchang.transition_label(moonrise, d, hour24),
    }


def shivaratri_candidate(
    d: date,
    tithi_start: datetime,
    tithi_end: datetime,
    lat: float,
    lon: float,
    tz: ZoneInfo,
    hour24: bool,
):
    sunset = panchang.rise_set(
        d, lat, lon, tz, panchang.astronomy.Body.Sun, panchang.astronomy.Direction.Set
    )
    next_sunrise = panchang.rise_set(
        d + timedelta(days=1),
        lat,
        lon,
        tz,
        panchang.astronomy.Body.Sun,
        panchang.astronomy.Direction.Rise,
    )
    if sunset is None or next_sunrise is None:
        return None
    if next_sunrise <= sunset:
        next_sunrise += timedelta(days=1)

    night_muhurta = (next_sunrise - sunset) / 15
    nishita_start = sunset + night_muhurta * 7
    nishita_end = sunset + night_muhurta * 8
    overlap_start = max(nishita_start, tithi_start)
    overlap_end = min(nishita_end, tithi_end)
    if overlap_start >= overlap_end:
        return None

    return {
        "date": d,
        "sunset": sunset,
        "next_sunrise": next_sunrise,
        "nishita_start": nishita_start,
        "nishita_end": nishita_end,
        "puja_start": overlap_start,
        "puja_end": overlap_end,
        "overlap_seconds": (overlap_end - overlap_start).total_seconds(),
        "nishita": window_payload(nishita_start, nishita_end, d, hour24),
        "puja": window_payload(overlap_start, overlap_end, d, hour24),
    }


def build_event(kind: str, rule: dict, start_dt: datetime, end_dt: datetime, lat, lon, tz, hour24):
    candidates = []

    for d in iter_dates(start_dt, end_dt):
        if kind == "pradosh":
            row = pradosh_candidate(d, start_dt, end_dt, lat, lon, tz, hour24)
        elif kind == "sankashti":
            row = sankashti_candidate(d, start_dt, end_dt, lat, lon, tz, hour24)
        elif kind == "shivaratri":
            row = shivaratri_candidate(d, start_dt, end_dt, lat, lon, tz, hour24)
        else:
            raise ValueError("Unsupported observance kind")
        if row:
            candidates.append(row)

    if not candidates:
        return None

    if kind in ("pradosh", "shivaratri"):
        chosen = max(candidates, key=lambda row: row.get("overlap_seconds", 0))
    else:
        chosen = min(candidates, key=lambda row: row["moonrise"])

    d = chosen["date"]
    month = lunar_month_at(start_dt + (end_dt - start_dt) / 2)

    event = {
        "date": d.isoformat(),
        "weekday": d.strftime("%A"),
        "tithi_start": start_dt.isoformat(),
        "tithi_end": end_dt.isoformat(),
        "tithi_start_label": panchang.transition_label(start_dt, d, hour24),
        "tithi_end_label": panchang.transition_label(end_dt, d, hour24),
        "paksha": rule["paksha"],
        "amanta_month": month.get("amanta"),
        "purnimanta_month": month.get("purnimanta"),
        "adhika": bool(month.get("adhika")),
    }

    if kind == "pradosh":
        event.update({
            "name": WEEKDAY_PRADOSH[d.weekday()] + " Vrat",
            "observance": "Pradosh",
            "puja": chosen["puja"],
            "sunset": chosen["sunset"].isoformat(),
            "sunset_label": panchang.fmt(chosen["sunset"], hour24),
            "pradosh_kaal": window_payload(
                chosen["pradosh_start"], chosen["pradosh_end"], d, hour24
            ),
        })
    elif kind == "sankashti":
        event.update({
            "name": "Sankashti Chaturthi",
            "observance": "Sankashti Chaturthi",
            "moonrise": chosen["moonrise"].isoformat(),
            "moonrise_label": chosen["moonrise_label"],
            "sunrise": chosen["sunrise"].isoformat() if chosen["sunrise"] else None,
            "sunrise_label": panchang.fmt(chosen["sunrise"], hour24),
            "angarki": d.weekday() == 1,
        })
        if event["angarki"]:
            event["name"] = "Angarki Sankashti Chaturthi"
    else:
        is_maha = str(month.get("amanta") or "").replace("Adhika ", "") == "Magha"
        event.update({
            "name": "Maha Shivaratri" if is_maha else (
                "Adhika Masik Shivaratri" if event["adhika"] else "Masik Shivaratri"
            ),
            "observance": "Masik Shivaratri",
            "maha_shivaratri": is_maha,
            "nishita": chosen["nishita"],
            "puja": chosen["puja"],
            "sunset": chosen["sunset"].isoformat(),
            "sunset_label": panchang.fmt(chosen["sunset"], hour24),
        })

    return event


def events_for_rule(year: int, kind: str, rule: dict, lat, lon, tz, hour24):
    cursor = panchang.astronomy_time(datetime(year - 1, 12, 1, 0, 0, tzinfo=tz))
    events = []

    for _ in range(16):
        start_event, end_event = phase_window(cursor, rule)
        if start_event is None or end_event is None:
            break

        start_dt = panchang.datetime_from_astronomy(start_event, tz)
        end_dt = panchang.datetime_from_astronomy(end_event, tz)
        event = build_event(kind, rule, start_dt, end_dt, lat, lon, tz, hour24)
        if event and int(event["date"][:4]) == year:
            events.append(event)

        if start_dt.year > year and start_dt.month > 1:
            break
        cursor = panchang.astronomy_time(start_dt + timedelta(days=2))

    return events


def calculate(kind: str, year: int, lat: float, lon: float, tz: ZoneInfo, hour24: bool):
    if kind == "pradosh":
        rows = []
        rows.extend(events_for_rule(year, kind, RULES["pradosh_shukla"], lat, lon, tz, hour24))
        rows.extend(events_for_rule(year, kind, RULES["pradosh_krishna"], lat, lon, tz, hour24))
    elif kind == "sankashti":
        rows = events_for_rule(year, kind, RULES["sankashti"], lat, lon, tz, hour24)
    elif kind == "shivaratri":
        rows = events_for_rule(year, kind, RULES["shivaratri"], lat, lon, tz, hour24)
    else:
        raise ValueError("Unsupported observance kind")

    rows.sort(key=lambda row: row["date"])
    return rows


def main() -> None:
    payload = json.loads(sys.stdin.read() or "{}")
    kind = str(payload.get("kind") or "pradosh").lower()
    if kind not in ("pradosh", "sankashti", "shivaratri"):
        raise ValueError("Unsupported observance kind")

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
    events = calculate(kind, selected.year, lat, lon, tz, hour24)

    notes = {
        "pradosh": (
            "Pradosh is selected where Trayodashi overlaps local Pradosh Kaal "
            "after sunset; the displayed Puja window is the exact overlap."
        ),
        "sankashti": (
            "Sankashti is selected where Krishna Chaturthi prevails at local "
            "moonrise; fasting traditionally ends after moon sighting."
        ),
        "shivaratri": (
            "Masik Shivaratri is selected where Krishna Chaturdashi overlaps "
            "local Nishita Kaal; the Puja window is the exact overlap."
        ),
    }

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
            "name": "tithika-observances",
            "version": "0.1.0",
            "panchang_version": panchang.ENGINE_VERSION,
            "source": "Tithika Lahiri Panchang + local sunrise/sunset/moonrise selection rules",
            "status": "rule-selected",
        },
        "events": events,
        "note": notes[kind],
    }, ensure_ascii=False))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(json.dumps({
            "ok": False,
            "error": str(exc),
            "code": "OBSERVANCE_CALCULATION_FAILED",
        }))
        sys.exit(1)
