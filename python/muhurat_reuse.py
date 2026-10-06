#!/usr/bin/env python3
"""
Tithika reusable Muhurat utilities.

Implements deterministic, auditable reuse of the existing Lahiri Panchang and
verified sidereal Lagna engines for:
- Shubha Hora / planetary Hora
- Panchaka Rahita
- Sarvartha Siddhi Yoga
- Amrit Siddhi Yoga
- Guru Pushya Yoga
- Ravi Pushya Yoga
- Dwipushkar Yoga
- Tripushkar Yoga
- Ravi Yoga
- aggregate Auspicious Yoga calendar

All weekday-sensitive intervals use the Hindu weekday from local sunrise to the
next sunrise. No fixed 06:00/18:00 approximation is used.
"""
from __future__ import annotations

import json
import sys
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import lagna
import panchang

ENGINE_VERSION = "0.1.0"

HORA_SEQUENCE = ["Sun", "Venus", "Mercury", "Moon", "Saturn", "Jupiter", "Mars"]
WEEKDAY_LORD = {
    0: "Moon", 1: "Mars", 2: "Mercury", 3: "Jupiter",
    4: "Venus", 5: "Saturn", 6: "Sun",
}
HORA_BENEFIC = {"Jupiter", "Venus", "Mercury", "Moon"}

SARVARTHA = {
    6: {"Ashwini", "Pushya", "Uttara Phalguni", "Hasta", "Mula", "Uttara Ashadha", "Uttara Bhadrapada"},
    0: {"Rohini", "Mrigashira", "Pushya", "Anuradha", "Shravana"},
    1: {"Ashwini", "Krittika", "Ashlesha", "Uttara Bhadrapada"},
    2: {"Krittika", "Rohini", "Mrigashira", "Hasta", "Anuradha"},
    3: {"Ashwini", "Punarvasu", "Pushya", "Anuradha", "Revati"},
    4: {"Ashwini", "Punarvasu", "Anuradha", "Shravana", "Revati"},
    5: {"Rohini", "Swati", "Shravana"},
}

AMRIT_SIDDHI = {
    6: "Hasta",
    0: "Mrigashira",
    1: "Ashwini",
    2: "Anuradha",
    3: "Pushya",
    4: "Revati",
    5: "Rohini",
}

PUSHKAR_WEEKDAYS = {6, 1, 5}  # Sunday, Tuesday, Saturday
PUSHKAR_TITHIS = {2, 7, 12}
DWI_NAKSHATRAS = {"Mrigashira", "Chitra", "Dhanishta"}
TRI_NAKSHATRAS = {
    "Krittika", "Punarvasu", "Uttara Phalguni",
    "Vishakha", "Uttara Ashadha", "Purva Bhadrapada",
}
RAVI_DISTANCES = {4, 6, 9, 10, 13, 20}

PANCHAKA_BAD = {
    1: ("Mrityu", "danger / hazard"),
    2: ("Agni", "fire-related risk"),
    4: ("Raja", "unfavourable administrative results"),
    6: ("Chora", "theft / loss"),
    8: ("Roga", "illness / disease"),
}

YOGA_TITLES = {
    "sarvartha-siddhi": "Sarvartha Siddhi Yoga",
    "amrit-siddhi": "Amrit Siddhi Yoga",
    "guru-pushya": "Guru Pushya Yoga",
    "ravi-pushya": "Ravi Pushya Yoga",
    "dwipushkar": "Dwipushkar Yoga",
    "tripushkar": "Tripushkar Yoga",
    "ravi-yoga": "Ravi Yoga",
}


def hindu_day(d: date, lat: float, lon: float, tz: ZoneInfo):
    sunrise = panchang.rise_set(
        d, lat, lon, tz,
        panchang.astronomy.Body.Sun, panchang.astronomy.Direction.Rise,
    )
    sunset = panchang.rise_set(
        d, lat, lon, tz,
        panchang.astronomy.Body.Sun, panchang.astronomy.Direction.Set,
    )
    next_sunrise = panchang.rise_set(
        d + timedelta(days=1), lat, lon, tz,
        panchang.astronomy.Body.Sun, panchang.astronomy.Direction.Rise,
    )
    if not sunrise or not sunset or not next_sunrise:
        raise ValueError("Sunrise/sunset unavailable for this latitude/date")
    if sunset <= sunrise:
        sunset += timedelta(days=1)
    if next_sunrise <= sunset:
        next_sunrise += timedelta(days=1)
    return sunrise, sunset, next_sunrise


def fmt_row(start: datetime, end: datetime, anchor: date, hour24: bool) -> dict:
    return {
        "start": start.isoformat(),
        "end": end.isoformat(),
        "start_label": panchang.transition_label(start, anchor, hour24),
        "end_label": panchang.transition_label(end, anchor, hour24),
        "duration_minutes": round((end - start).total_seconds() / 60.0, 2),
    }


def hora_day(d: date, lat: float, lon: float, tz: ZoneInfo, hour24: bool) -> dict:
    sunrise, sunset, next_sunrise = hindu_day(d, lat, lon, tz)
    first = WEEKDAY_LORD[d.weekday()]
    offset = HORA_SEQUENCE.index(first)
    rulers = [HORA_SEQUENCE[(offset + i) % 7] for i in range(24)]
    rows = []

    day_span = (sunset - sunrise) / 12
    night_span = (next_sunrise - sunset) / 12
    for i in range(12):
        start = sunrise + day_span * i
        end = sunset if i == 11 else sunrise + day_span * (i + 1)
        rows.append({
            **fmt_row(start, end, d, hour24),
            "index": i + 1,
            "half": "day",
            "planet": rulers[i],
            "generally_benefic": rulers[i] in HORA_BENEFIC,
        })
    for i in range(12):
        start = sunset + night_span * i
        end = next_sunrise if i == 11 else sunset + night_span * (i + 1)
        rows.append({
            **fmt_row(start, end, d, hour24),
            "index": i + 13,
            "half": "night",
            "planet": rulers[i + 12],
            "generally_benefic": rulers[i + 12] in HORA_BENEFIC,
        })

    return {
        "date": d.isoformat(),
        "weekday": d.strftime("%A"),
        "weekday_lord": first,
        "sunrise": sunrise.isoformat(),
        "sunrise_label": panchang.fmt(sunrise, hour24),
        "sunset": sunset.isoformat(),
        "sunset_label": panchang.fmt(sunset, hour24),
        "next_sunrise": next_sunrise.isoformat(),
        "next_sunrise_label": panchang.fmt(next_sunrise, hour24),
        "horas": rows,
        "note": (
            "Day and night are independently divided into twelve equal Horas. "
            "The first Hora is the weekday lord and rulers continue in Chaldean order."
        ),
    }


def refine_boolean(left: datetime, right: datetime, old: bool, predicate) -> datetime:
    lo, hi = left, right
    for _ in range(36):
        mid = lo + (hi - lo) / 2
        if bool(predicate(mid)) == old:
            lo = mid
        else:
            hi = mid
    return hi


def boolean_intervals(
    start: datetime,
    end: datetime,
    predicate,
    step_minutes: int = 20,
) -> list[tuple[datetime, datetime]]:
    rows = []
    left = start
    current = bool(predicate(left))
    active = left if current else None
    probe = min(end, left + timedelta(minutes=step_minutes))

    while left < end:
        value = bool(predicate(probe))
        if value != current:
            boundary = refine_boolean(left, probe, current, predicate)
            if current and active is not None:
                rows.append((active, boundary))
                active = None
            elif value:
                active = boundary
            current = value
        if probe >= end:
            break
        left = probe
        probe = min(end, probe + timedelta(minutes=step_minutes))

    if current and active is not None and active < end:
        rows.append((active, end))
    return rows


def ravi_distance(state: dict) -> int:
    return ((state["nakshatra_id"] - state["sun_nakshatra_id"]) % 27) + 1


def yoga_predicate(kind: str, weekday: int, state: dict) -> bool:
    nak = state["nakshatra"]
    tithi = state["tithi_number"]

    if kind == "sarvartha-siddhi":
        return nak in SARVARTHA[weekday]
    if kind == "amrit-siddhi":
        return nak == AMRIT_SIDDHI[weekday]
    if kind == "guru-pushya":
        return weekday == 3 and nak == "Pushya"
    if kind == "ravi-pushya":
        return weekday == 6 and nak == "Pushya"
    if kind == "dwipushkar":
        return weekday in PUSHKAR_WEEKDAYS and tithi in PUSHKAR_TITHIS and nak in DWI_NAKSHATRAS
    if kind == "tripushkar":
        return weekday in PUSHKAR_WEEKDAYS and tithi in PUSHKAR_TITHIS and nak in TRI_NAKSHATRAS
    if kind == "ravi-yoga":
        return ravi_distance(state) in RAVI_DISTANCES
    raise ValueError("Unsupported auspicious Yoga")


def yoga_day(
    kind: str, d: date, lat: float, lon: float, tz: ZoneInfo, hour24: bool
) -> list[dict]:
    sunrise, _sunset, next_sunrise = hindu_day(d, lat, lon, tz)
    weekday = d.weekday()
    intervals = boolean_intervals(
        sunrise,
        next_sunrise,
        lambda moment: yoga_predicate(kind, weekday, panchang.state_at(moment)),
    )
    rows = []
    for start, end in intervals:
        mid = start + (end - start) / 2
        state = panchang.state_at(mid)
        rows.append({
            "kind": kind,
            "name": YOGA_TITLES[kind],
            "date": d.isoformat(),
            "date_label": d.strftime("%B %d, %Y").replace(" 0", " "),
            "weekday": d.strftime("%A"),
            **fmt_row(start, end, d, hour24),
            "nakshatra": state["nakshatra"],
            "tithi": state["tithi"],
            "tithi_number": state["tithi_number"],
            "paksha": state["paksha"],
            "sun_nakshatra": state["sun_nakshatra"],
            "ravi_distance": ravi_distance(state),
        })
    return rows


def yoga_year(
    kind: str, year: int, lat: float, lon: float, tz: ZoneInfo, hour24: bool
) -> list[dict]:
    rows = []
    d = date(year, 1, 1)
    while d.year == year:
        rows.extend(yoga_day(kind, d, lat, lon, tz, hour24))
        d += timedelta(days=1)
    return rows


def aggregate_yogas(
    year: int, lat: float, lon: float, tz: ZoneInfo, hour24: bool
) -> dict:
    kinds = list(YOGA_TITLES)
    by_kind = {
        kind: yoga_year(kind, year, lat, lon, tz, hour24)
        for kind in kinds
    }
    events = []
    for kind, rows in by_kind.items():
        events.extend(rows)
    events.sort(key=lambda row: row["start"])
    return {
        "year": year,
        "by_kind": by_kind,
        "events": events,
        "counts": {kind: len(rows) for kind, rows in by_kind.items()},
    }


def panchaka_remainder(moment: datetime, weekday: int, lat: float, lon: float) -> dict:
    state = panchang.state_at(moment)
    rising = lagna.lagna_state(moment, lat, lon)
    tithi_index = state["tithi_id"] + 1
    vara_index = ((weekday + 1) % 7) + 1  # Sunday=1 ... Saturday=7
    nak_index = state["nakshatra_id"] + 1
    lagna_index = rising["lagna_id"] + 1
    total = tithi_index + vara_index + nak_index + lagna_index
    remainder = total % 9

    if remainder in PANCHAKA_BAD:
        name, caution = PANCHAKA_BAD[remainder]
        good = False
    else:
        name, caution = "Rahita", "free from the five Panchaka blemishes"
        good = True

    return {
        "tithi_index": tithi_index,
        "vara_index": vara_index,
        "nakshatra_index": nak_index,
        "lagna_index": lagna_index,
        "sum": total,
        "remainder": remainder,
        "classification": name,
        "caution": caution,
        "good": good,
        "tithi": state["tithi"],
        "paksha": state["paksha"],
        "nakshatra": state["nakshatra"],
        "lagna": rising["lagna"],
    }


def panchaka_rahita_day(
    d: date, lat: float, lon: float, tz: ZoneInfo, hour24: bool
) -> dict:
    sunrise, sunset, next_sunrise = hindu_day(d, lat, lon, tz)
    weekday = d.weekday()
    intervals = []
    start = sunrise
    current = panchaka_remainder(start + timedelta(seconds=1), weekday, lat, lon)

    # Panchaka changes only when Tithi, Nakshatra or Lagna changes. A short
    # scan detects the next classification boundary and binary-refines it.
    while start < next_sunrise:
        old_key = (
            current["tithi_index"],
            current["nakshatra_index"],
            current["lagna_index"],
        )
        probe = min(next_sunrise, start + timedelta(minutes=5))
        boundary = None
        while probe <= next_sunrise:
            check = panchaka_remainder(probe, weekday, lat, lon)
            key = (check["tithi_index"], check["nakshatra_index"], check["lagna_index"])
            if key != old_key:
                lo = probe - timedelta(minutes=5)
                hi = probe
                for _ in range(38):
                    mid = lo + (hi - lo) / 2
                    m = panchaka_remainder(mid, weekday, lat, lon)
                    mk = (m["tithi_index"], m["nakshatra_index"], m["lagna_index"])
                    if mk == old_key:
                        lo = mid
                    else:
                        hi = mid
                boundary = hi
                break
            if probe >= next_sunrise:
                break
            probe = min(next_sunrise, probe + timedelta(minutes=5))

        end = boundary or next_sunrise
        mid = start + (end - start) / 2
        evidence = panchaka_remainder(mid, weekday, lat, lon)
        intervals.append({
            **fmt_row(start, end, d, hour24),
            **evidence,
        })
        if boundary is None:
            break
        start = boundary
        current = panchaka_remainder(start + timedelta(seconds=1), weekday, lat, lon)

    return {
        "date": d.isoformat(),
        "weekday": d.strftime("%A"),
        "sunrise": sunrise.isoformat(),
        "sunrise_label": panchang.fmt(sunrise, hour24),
        "sunset": sunset.isoformat(),
        "sunset_label": panchang.fmt(sunset, hour24),
        "next_sunrise": next_sunrise.isoformat(),
        "next_sunrise_label": panchang.fmt(next_sunrise, hour24),
        "intervals": intervals,
        "good_intervals": [row for row in intervals if row["good"]],
        "formula": "(Tithi + Vara + Nakshatra + Udaya Lagna) mod 9",
        "good_remainders": [0, 3, 5, 7],
        "bad_remainders": {
            "1": "Mrityu", "2": "Agni", "4": "Raja", "6": "Chora", "8": "Roga"
        },
    }


def main():
    payload = json.loads(sys.stdin.read() or "{}")
    mode = str(payload.get("mode") or "hora").strip().lower()
    supported = {"hora", "panchaka-rahita", "auspicious-yoga", *YOGA_TITLES.keys()}
    if mode not in supported:
        raise ValueError("Unsupported Muhurat reuse mode")

    lat = float(payload.get("lat", 18.5204))
    lon = float(payload.get("lon", 73.8567))
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

    if mode == "hora":
        result = hora_day(selected, lat, lon, tz, hour24)
    elif mode == "panchaka-rahita":
        result = panchaka_rahita_day(selected, lat, lon, tz, hour24)
    elif mode == "auspicious-yoga":
        result = aggregate_yogas(selected.year, lat, lon, tz, hour24)
    else:
        result = {
            "year": selected.year,
            "kind": mode,
            "name": YOGA_TITLES[mode],
            "events": yoga_year(mode, selected.year, lat, lon, tz, hour24),
        }

    print(json.dumps({
        "ok": True,
        "mode": mode,
        "engine": {
            "name": "tithika-muhurat-reuse",
            "version": ENGINE_VERSION,
            "panchang_version": panchang.ENGINE_VERSION,
            "lagna_version": lagna.ENGINE_VERSION,
            "ayanamsha": "Lahiri / Chitrapaksha",
            "hindu_weekday": "local sunrise to next sunrise",
        },
        "location": {
            "city": (payload.get("city") or "Current location").strip()[:120],
            "lat": lat,
            "lon": lon,
            "timezone": timezone_name,
        },
        **result,
    }, ensure_ascii=False))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(json.dumps({
            "ok": False,
            "error": str(exc),
            "code": "MUHURAT_REUSE_FAILED",
        }))
        sys.exit(1)
