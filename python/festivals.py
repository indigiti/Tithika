#!/usr/bin/env python3
"""
Tithika major-festival rule engine, batch 1.

This engine promotes only festival rules that can be selected from the verified
Tithika Lahiri Panchang + local solar/lunar events without hiding unresolved
exceptions.

Implemented:
- Ganesh Chaturthi: Bhadrapada Shukla Chaturthi, Madhyahna overlap.
- Raksha Bandhan: Shravana Purnima, sunrise/Purnima window with Bhadra guard.
- Shardiya Navratri: Ashwina Shukla Pratipada, first third of day.
- Vijayadashami: Ashwina Shukla Dashami, Aparahna/Vijay Muhurta.
- Holika Dahan / Holi: Phalguna Purnima, Pradosh; Rangwali Holi next day.
- Karwa Chauth: Kartika Krishna Chaturthi prevailing at moonrise.
- Diwali: Kartika Amavasya overlapping Pradosh; Vrishabha Lagna refinement is
  intentionally left pending until the Lagna engine is verified.
"""
from __future__ import annotations

import json
import sys
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import panchang
import lagna

KINDS = {
    "ganesh-chaturthi": {
        "title": "Ganesh Chaturthi",
        "month": "Bhadrapada",
        "paksha": "Shukla Paksha",
        "tithi_id": 3,
        "start_angle": 36.0,
        "end_angle": 48.0,
        "selector": "madhyahna",
    },
    "raksha-bandhan": {
        "title": "Raksha Bandhan",
        "month": "Shravana",
        "paksha": "Shukla Paksha",
        "tithi_id": 14,
        "start_angle": 168.0,
        "end_angle": 180.0,
        "selector": "purnima-sunrise",
    },
    "navratri": {
        "title": "Shardiya Navratri",
        "month": "Ashwina",
        "paksha": "Shukla Paksha",
        "tithi_id": 0,
        "start_angle": 0.0,
        "end_angle": 12.0,
        "selector": "ghatasthapana",
    },
    "dussehra": {
        "title": "Vijayadashami",
        "month": "Ashwina",
        "paksha": "Shukla Paksha",
        "tithi_id": 9,
        "start_angle": 108.0,
        "end_angle": 120.0,
        "selector": "aparahna",
    },
    "holi": {
        "title": "Holika Dahan",
        "month": "Phalguna",
        "paksha": "Shukla Paksha",
        "tithi_id": 14,
        "start_angle": 168.0,
        "end_angle": 180.0,
        "selector": "pradosh",
    },
    "karwa-chauth": {
        "title": "Karwa Chauth",
        "month": "Kartika",
        "paksha": "Krishna Paksha",
        "tithi_id": 18,
        "start_angle": 216.0,
        "end_angle": 228.0,
        "selector": "moonrise",
    },
    "janmashtami": {
        "title": "Krishna Janmashtami",
        "month": "Bhadrapada",
        "paksha": "Krishna Paksha",
        "tithi_id": 22,
        "start_angle": 264.0,
        "end_angle": 276.0,
        "selector": "nishita",
    },
    "diwali": {
        "title": "Diwali / Lakshmi Puja",
        "month": "Kartika",
        "paksha": "Krishna Paksha",
        "tithi_id": 29,
        "start_angle": 348.0,
        "end_angle": 0.0,
        "selector": "pradosh",
    },
}


def rise(d, lat, lon, tz, body=panchang.astronomy.Body.Sun):
    return panchang.rise_set(d, lat, lon, tz, body, panchang.astronomy.Direction.Rise)


def set_(d, lat, lon, tz, body=panchang.astronomy.Body.Sun):
    return panchang.rise_set(d, lat, lon, tz, body, panchang.astronomy.Direction.Set)


def overlap(a0, a1, b0, b1):
    start = max(a0, b0)
    end = min(a1, b1)
    return (start, end) if start < end else None


def window(start, end, anchor, hour24):
    if not start or not end or start >= end:
        return None
    return {
        "start": start.isoformat(),
        "end": end.isoformat(),
        "start_label": panchang.transition_label(start, anchor, hour24),
        "end_label": panchang.transition_label(end, anchor, hour24),
        "duration_minutes": round((end - start).total_seconds() / 60.0, 2),
    }


def solar_day_parts(d, lat, lon, tz):
    sunrise = rise(d, lat, lon, tz)
    sunset = set_(d, lat, lon, tz)
    if not sunrise or not sunset:
        return None
    day = sunset - sunrise
    return {
        "sunrise": sunrise,
        "sunset": sunset,
        "pratah": (sunrise, sunrise + day / 5),
        "sangava": (sunrise + day / 5, sunrise + day * 2 / 5),
        "madhyahna": (sunrise + day * 2 / 5, sunrise + day * 3 / 5),
        "aparahna": (sunrise + day * 3 / 5, sunrise + day * 4 / 5),
        "sayahna": (sunrise + day * 4 / 5, sunset),
        "first_third": (sunrise, sunrise + day / 3),
        "vijay": (sunrise + day * 10 / 15, sunrise + day * 11 / 15),
    }


def pradosh_window(d, lat, lon, tz):
    sunset = set_(d, lat, lon, tz)
    next_sunrise = rise(d + timedelta(days=1), lat, lon, tz)
    if not sunset or not next_sunrise:
        return None
    return sunset, sunset + (next_sunrise - sunset) / 5


def intervals_for_name(start, end, key, name_key, wanted):
    rows = []
    cursor = start
    while cursor < end:
        state = panchang.state_at(cursor)
        state_id = state[key]
        transition = panchang.find_transition(cursor, end, key, state_id)
        stop = transition or end
        if state[name_key] == wanted:
            rows.append((cursor, stop))
        if not transition:
            break
        cursor = transition + timedelta(seconds=1)
    return rows


def month_info_for(start_dt, end_dt):
    ref = start_dt + (end_dt - start_dt) / 2
    state = panchang.state_at(ref)
    return panchang.lunar_month_info(ref, state)


def search_windows(year, rule, tz):
    cursor = panchang.astronomy_time(datetime(year - 1, 12, 1, tzinfo=tz))
    rows = []
    for _ in range(18):
        start_event = panchang.astronomy.SearchMoonPhase(rule["start_angle"], cursor, 40.0)
        if start_event is None:
            break
        end_event = panchang.astronomy.SearchMoonPhase(rule["end_angle"], start_event, 3.0)
        if end_event is None:
            break
        start_dt = panchang.datetime_from_astronomy(start_event, tz)
        end_dt = panchang.datetime_from_astronomy(end_event, tz)
        month = month_info_for(start_dt, end_dt)
        rows.append((start_dt, end_dt, month))
        if start_dt.year > year and start_dt.month > 1:
            break
        cursor = panchang.astronomy_time(start_dt + timedelta(days=2))
    return rows


def candidate_dates(start_dt, end_dt):
    d = start_dt.date() - timedelta(days=1)
    last = end_dt.date() + timedelta(days=1)
    while d <= last:
        yield d
        d += timedelta(days=1)


def choose_by_period(start_dt, end_dt, period_getter):
    best = None
    for d in candidate_dates(start_dt, end_dt):
        period = period_getter(d)
        if not period:
            continue
        ov = overlap(start_dt, end_dt, period[0], period[1])
        if not ov:
            continue
        score = (ov[1] - ov[0]).total_seconds()
        if best is None or score > best["score"]:
            best = {"date": d, "period": period, "overlap": ov, "score": score}
    return best


def choose_sunrise(start_dt, end_dt, lat, lon, tz):
    rows = []
    for d in candidate_dates(start_dt, end_dt):
        sunrise = rise(d, lat, lon, tz)
        if sunrise and start_dt <= sunrise < end_dt:
            rows.append((d, sunrise))
    return rows[-1] if rows else None


def festival_event(kind, year, lat, lon, tz, hour24):
    rule = KINDS[kind]
    target = None
    for start_dt, end_dt, month in search_windows(year, rule, tz):
        # Purnimanta is the common month label for the rules in this batch.
        if month.get("purnimanta") != rule["month"]:
            continue
        if start_dt.year > year + 1 or end_dt.year < year - 1:
            continue
        target = (start_dt, end_dt, month)
        break
    if not target:
        return None

    start_dt, end_dt, month = target
    selector = rule["selector"]
    selected = None
    extra = {}

    if selector == "madhyahna":
        selected = choose_by_period(
            start_dt, end_dt,
            lambda d: (solar_day_parts(d, lat, lon, tz) or {}).get("madhyahna"),
        )
        if selected:
            extra["puja"] = window(selected["overlap"][0], selected["overlap"][1], selected["date"], hour24)

    elif selector == "purnima-sunrise":
        sr = choose_sunrise(start_dt, end_dt, lat, lon, tz)
        if sr:
            d, sunrise = sr
            selected = {"date": d, "score": 1}
            parts = solar_day_parts(d, lat, lon, tz)
            ceremony_end = min(end_dt, parts["sunset"]) if parts else end_dt
            bhadra = intervals_for_name(sunrise, ceremony_end, "karana_id", "karana", "Vishti")
            ceremony_start = sunrise
            if bhadra and bhadra[0][0] <= sunrise + timedelta(seconds=2):
                ceremony_start = bhadra[0][1]
            if ceremony_start < ceremony_end:
                extra["thread_ceremony"] = window(ceremony_start, ceremony_end, d, hour24)
            extra["bhadra_intervals"] = [
                window(a, b, d, hour24) for a, b in bhadra
            ]
            extra["bhadra_status"] = "clear-at-sunrise" if not bhadra else "review-bhadra"

    elif selector == "ghatasthapana":
        selected = choose_by_period(
            start_dt, end_dt,
            lambda d: (solar_day_parts(d, lat, lon, tz) or {}).get("first_third"),
        )
        if selected:
            d = selected["date"]
            extra["ghatasthapana"] = window(selected["overlap"][0], selected["overlap"][1], d, hour24)
            mid = selected["overlap"][0] + (selected["overlap"][1] - selected["overlap"][0]) / 2
            state = panchang.state_at(mid)
            extra["warnings"] = {
                "chitra_nakshatra": state["nakshatra"] == "Chitra",
                "vaidhriti_yoga": state["yoga"] == "Vaidhriti",
            }

    elif selector == "aparahna":
        selected = choose_by_period(
            start_dt, end_dt,
            lambda d: (solar_day_parts(d, lat, lon, tz) or {}).get("aparahna"),
        )
        if selected:
            d = selected["date"]
            parts = solar_day_parts(d, lat, lon, tz)
            extra["aparahna"] = window(parts["aparahna"][0], parts["aparahna"][1], d, hour24)
            v = overlap(start_dt, end_dt, parts["vijay"][0], parts["vijay"][1])
            extra["vijay_muhurat"] = window(v[0], v[1], d, hour24) if v else None

    elif selector == "pradosh":
        selected = choose_by_period(
            start_dt, end_dt,
            lambda d: pradosh_window(d, lat, lon, tz),
        )
        if selected:
            d = selected["date"]
            extra["pradosh"] = window(selected["period"][0], selected["period"][1], d, hour24)
            extra["tithi_pradosh_overlap"] = window(selected["overlap"][0], selected["overlap"][1], d, hour24)
            bhadra = intervals_for_name(
                selected["period"][0], selected["period"][1],
                "karana_id", "karana", "Vishti"
            )
            extra["bhadra_intervals"] = [window(a, b, d, hour24) for a, b in bhadra]
            if kind == "holi":
                extra["rangwali_holi_date"] = (d + timedelta(days=1)).isoformat()
            if kind == "diwali":
                lagna_rows = lagna.timeline(
                    selected["period"][0], selected["period"][1], lat, lon, hour24
                )
                vrishabha = next((row for row in lagna_rows if row["lagna"] == "Vrishabha"), None)
                if vrishabha:
                    lagna_start = datetime.fromisoformat(vrishabha["start"])
                    lagna_end = datetime.fromisoformat(vrishabha["end"])
                    puja_overlap = overlap(
                        max(start_dt, selected["period"][0]),
                        min(end_dt, selected["period"][1]),
                        lagna_start,
                        lagna_end,
                    )
                    extra["vrishabha_lagna"] = window(lagna_start, lagna_end, d, hour24)
                    extra["lakshmi_puja"] = (
                        window(puja_overlap[0], puja_overlap[1], d, hour24)
                        if puja_overlap else None
                    )
                extra["vrishabha_lagna_status"] = "verified"

    elif selector == "nishita":
        selected = choose_by_period(
            start_dt, end_dt,
            lambda d: (
                (lambda sunset, next_sunrise: (
                    sunset + (next_sunrise - sunset) * 7 / 15,
                    sunset + (next_sunrise - sunset) * 8 / 15,
                ))(
                    set_(d, lat, lon, tz),
                    rise(d + timedelta(days=1), lat, lon, tz),
                )
                if set_(d, lat, lon, tz) and rise(d + timedelta(days=1), lat, lon, tz)
                else None
            ),
        )
        if selected:
            d = selected["date"]
            extra["nishita"] = window(selected["period"][0], selected["period"][1], d, hour24)
            extra["nishita_tithi_overlap"] = window(selected["overlap"][0], selected["overlap"][1], d, hour24)
            rohini = intervals_for_name(
                start_dt - timedelta(days=1), end_dt + timedelta(days=1),
                "nakshatra_id", "nakshatra", "Rohini"
            )
            extra["rohini_intervals"] = [window(a, b, d, hour24) for a, b in rohini]
            next_sunrise = rise(d + timedelta(days=1), lat, lon, tz)
            parana = max(
                [x for x in [next_sunrise, end_dt] + [b for _, b in rohini] if x is not None]
            )
            extra["parana"] = {
                "after": parana.isoformat(),
                "after_label": panchang.transition_label(parana, d + timedelta(days=1), hour24),
                "basis": "after-sunrise-ashtami-rohini-complete",
            }
            extra["dahi_handi_date"] = (d + timedelta(days=1)).isoformat()
            extra["selection_status"] = "base-nishita-rule"

    elif selector == "moonrise":
        for d in candidate_dates(start_dt, end_dt):
            moonrise = rise(d, lat, lon, tz, panchang.astronomy.Body.Moon)
            if moonrise and start_dt <= moonrise < end_dt:
                selected = {"date": d, "score": 1}
                sunrise = rise(d, lat, lon, tz)
                extra["moonrise"] = moonrise.isoformat()
                extra["moonrise_label"] = panchang.transition_label(moonrise, d, hour24)
                extra["upavasa"] = window(sunrise, moonrise, d, hour24) if sunrise else None
                extra["puja_muhurat_status"] = "evening-rule-refinement-pending"
                break

    if not selected:
        return None

    d = selected["date"]
    event = {
        "kind": kind,
        "title": rule["title"],
        "date": d.isoformat(),
        "weekday": d.strftime("%A"),
        "month": rule["month"],
        "paksha": rule["paksha"],
        "tithi_start": start_dt.isoformat(),
        "tithi_end": end_dt.isoformat(),
        "tithi_start_label": panchang.transition_label(start_dt, d, hour24),
        "tithi_end_label": panchang.transition_label(end_dt, d, hour24),
        "amanta_month": month.get("amanta"),
        "purnimanta_month": month.get("purnimanta"),
        "adhika": bool(month.get("adhika")),
    }
    event.update(extra)
    return event


def main():
    payload = json.loads(sys.stdin.read() or "{}")
    kind = str(payload.get("kind") or "ganesh-chaturthi").lower()
    if kind not in KINDS:
        raise ValueError("Unsupported festival kind")

    lat = float(payload.get("lat", 19.0760))
    lon = float(payload.get("lon", 72.8777))
    if not (-90 <= lat <= 90 and -180 <= lon <= 180):
        raise ValueError("Invalid latitude/longitude")

    selected = datetime.strptime(
        payload.get("date") or datetime.now().strftime("%Y-%m-%d"), "%Y-%m-%d"
    ).date()
    timezone_name = payload.get("timezone") or "Asia/Kolkata"
    try:
        tz = ZoneInfo(timezone_name)
    except ZoneInfoNotFoundError:
        timezone_name = "Asia/Kolkata"
        tz = ZoneInfo(timezone_name)

    hour24 = bool(payload.get("hour24", False))
    city = (payload.get("city") or "Current location").strip()[:120]
    event = festival_event(kind, selected.year, lat, lon, tz, hour24)

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
            "name": "tithika-major-festivals",
            "version": "0.1.0",
            "panchang_version": panchang.ENGINE_VERSION,
            "status": "rule-selected",
        },
        "event": event,
        "note": (
            "Festival date selection uses exact Lahiri Tithi windows plus the local "
            "day-part/moonrise rule shown for this festival. Fields explicitly marked "
            "pending are not presented as final Muhurat calculations."
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
