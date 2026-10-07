#!/usr/bin/env python3
"""
Shared Tithika festival rule engine.

Festival definitions are declarative. Selection mechanics (sunrise, Madhyahna,
Pradosh, Nishita, moonrise, Sandhi, Aparahna, etc.) live in reusable selector
functions, so new festivals can be added without extending one giant branch tree.

This module intentionally separates:
1. astronomical occurrence search,
2. lunar-month qualification,
3. local day-part selection,
4. festival-specific enrichments.
"""
from __future__ import annotations

from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

import choghadiya
import lagna
import panchang

ENGINE_VERSION = "0.2.0"

FESTIVAL_RULES = {
    "rama-navami": {
        "title": "Rama Navami",
        "month": "Chaitra", "paksha": "Shukla Paksha",
        "tithi_id": 8, "start_angle": 96.0, "end_angle": 108.0,
        "selector": "madhyahna", "profile": "rama-navami",
    },
    "hanuman-jayanti": {
        "title": "Hanuman Jayanti",
        "month": "Chaitra", "paksha": "Shukla Paksha",
        "tithi_id": 14, "start_angle": 168.0, "end_angle": 180.0,
        "selector": "sunrise", "profile": "sunrise",
    },
    "akshaya-tritiya": {
        "title": "Akshaya Tritiya",
        "month": "Vaishakha", "paksha": "Shukla Paksha",
        "tithi_id": 2, "start_angle": 24.0, "end_angle": 36.0,
        "selector": "auspicious-choghadiya", "profile": "akshaya-tritiya",
    },
    "vat-savitri": {
        "title": "Vat Savitri Vrat",
        "month": "Jyeshtha", "paksha": "Krishna Paksha",
        "tithi_id": 29, "start_angle": 348.0, "end_angle": 0.0,
        "selector": "sunrise", "profile": "sunrise",
    },
    "durga-puja": {
        "title": "Durga Puja / Mahashtami",
        "month": "Ashwina", "paksha": "Shukla Paksha",
        "tithi_id": 7, "start_angle": 84.0, "end_angle": 96.0,
        "selector": "sandhi", "profile": "durga-sandhi",
    },
    "ganesh-chaturthi": {
        "title": "Ganesh Chaturthi",
        "month": "Bhadrapada", "paksha": "Shukla Paksha",
        "tithi_id": 3, "start_angle": 36.0, "end_angle": 48.0,
        "selector": "madhyahna", "profile": "ganesh-chaturthi",
    },
    "raksha-bandhan": {
        "title": "Raksha Bandhan",
        "month": "Shravana", "paksha": "Shukla Paksha",
        "tithi_id": 14, "start_angle": 168.0, "end_angle": 180.0,
        "selector": "purnima-sunrise", "profile": "raksha-bandhan",
    },
    "navratri": {
        "title": "Shardiya Navratri",
        "month": "Ashwina", "paksha": "Shukla Paksha",
        "tithi_id": 0, "start_angle": 0.0, "end_angle": 12.0,
        "selector": "ghatasthapana", "profile": "navratri",
    },
    "dussehra": {
        "title": "Vijayadashami",
        "month": "Ashwina", "paksha": "Shukla Paksha",
        "tithi_id": 9, "start_angle": 108.0, "end_angle": 120.0,
        "selector": "aparahna", "profile": "dussehra",
    },
    "holi": {
        "title": "Holika Dahan",
        "month": "Phalguna", "paksha": "Shukla Paksha",
        "tithi_id": 14, "start_angle": 168.0, "end_angle": 180.0,
        "selector": "pradosh", "profile": "holi",
    },
    "karwa-chauth": {
        "title": "Karwa Chauth",
        "month": "Kartika", "paksha": "Krishna Paksha",
        "tithi_id": 18, "start_angle": 216.0, "end_angle": 228.0,
        "selector": "moonrise", "profile": "karwa-chauth",
    },
    "janmashtami": {
        "title": "Krishna Janmashtami",
        "month": "Bhadrapada", "paksha": "Krishna Paksha",
        "tithi_id": 22, "start_angle": 264.0, "end_angle": 276.0,
        "selector": "nishita", "profile": "janmashtami",
    },
    "diwali": {
        "title": "Diwali / Lakshmi Puja",
        "month": "Kartika", "paksha": "Krishna Paksha",
        "tithi_id": 29, "start_angle": 348.0, "end_angle": 0.0,
        "selector": "pradosh", "profile": "diwali",
    },
}
SUPPORTED_KINDS = tuple(FESTIVAL_RULES)


def rise(d, lat, lon, tz, body=panchang.astronomy.Body.Sun):
    return panchang.rise_set(
        d, lat, lon, tz, body, panchang.astronomy.Direction.Rise
    )


def set_(d, lat, lon, tz, body=panchang.astronomy.Body.Sun):
    return panchang.rise_set(
        d, lat, lon, tz, body, panchang.astronomy.Direction.Set
    )


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
        start_event = panchang.astronomy.SearchMoonPhase(
            rule["start_angle"], cursor, 40.0
        )
        if start_event is None:
            break
        end_event = panchang.astronomy.SearchMoonPhase(
            rule["end_angle"], start_event, 3.0
        )
        if end_event is None:
            break
        start_dt = panchang.datetime_from_astronomy(start_event, tz)
        end_dt = panchang.datetime_from_astronomy(end_event, tz)
        rows.append((start_dt, end_dt, month_info_for(start_dt, end_dt)))
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


def select_madhyahna(ctx):
    start_dt, end_dt = ctx["start"], ctx["end"]
    lat, lon, tz, hour24 = ctx["lat"], ctx["lon"], ctx["tz"], ctx["hour24"]
    selected = choose_by_period(
        start_dt, end_dt,
        lambda d: (solar_day_parts(d, lat, lon, tz) or {}).get("madhyahna"),
    )
    extra = {}
    if selected:
        full_period = ctx["kind"] == "rama-navami"
        extra["puja"] = window(
            selected["period"][0] if full_period else selected["overlap"][0],
            selected["period"][1] if full_period else selected["overlap"][1],
            selected["date"], hour24,
        )
        if ctx["kind"] == "rama-navami":
            next_day = selected["date"] + timedelta(days=1)
            next_sunrise = rise(next_day, lat, lon, tz)
            extra["vaishnava_date"] = (
                next_day.isoformat()
                if next_sunrise and start_dt <= next_sunrise < end_dt
                else selected["date"].isoformat()
            )
    return selected, extra


def select_sunrise(ctx):
    sr = choose_sunrise(
        ctx["start"], ctx["end"], ctx["lat"], ctx["lon"], ctx["tz"]
    )
    if not sr:
        return None, {}
    d, sunrise = sr
    return {"date": d, "score": 1}, {
        "sunrise": sunrise.isoformat(),
        "sunrise_label": panchang.transition_label(
            sunrise, d, ctx["hour24"]
        ),
    }


def select_auspicious_choghadiya(ctx):
    start_dt, end_dt = ctx["start"], ctx["end"]
    lat, lon, tz, hour24 = ctx["lat"], ctx["lon"], ctx["tz"], ctx["hour24"]
    best = None
    for d in candidate_dates(start_dt, end_dt):
        sunrise = choghadiya.solar_event(d, lat, lon, tz, True)
        sunset = choghadiya.solar_event(d, lat, lon, tz, False)
        if not sunrise or not sunset:
            continue
        rows = choghadiya.period_rows(
            sunrise, sunset, choghadiya.DAY_SEQUENCES[d.weekday()], hour24
        )
        good = {"Chara", "Labh", "Amrit", "Shubh"}
        active_start = active_end = None
        for row in rows:
            a = datetime.fromisoformat(row["start"])
            b = datetime.fromisoformat(row["end"])
            ov = overlap(start_dt, end_dt, a, b)
            if row["name"] in good and ov:
                if active_start is None:
                    active_start, active_end = ov
                elif ov[0] <= active_end + timedelta(seconds=2):
                    active_end = max(active_end, ov[1])
                else:
                    break
            elif active_start is not None:
                break
        if active_start and active_end:
            score = (active_end - active_start).total_seconds()
            if best is None or score > best["score"]:
                best = {
                    "date": d, "start": active_start,
                    "end": active_end, "score": score,
                }
    if not best:
        return None, {}
    return best, {
        "puja": window(best["start"], best["end"], best["date"], hour24),
        "choghadiya_basis": "Chara/Labh/Amrit/Shubh overlap",
    }


def select_sandhi(ctx):
    d = ctx["end"].date()
    return {"date": d, "score": 1}, {
        "sandhi_puja": window(
            ctx["end"] - timedelta(minutes=24),
            ctx["end"] + timedelta(minutes=24),
            d, ctx["hour24"],
        ),
        "mahashtami_date": d.isoformat(),
        "maha_navami_date": d.isoformat(),
        "navami_start": ctx["end"].isoformat(),
    }


def select_purnima_sunrise(ctx):
    start_dt, end_dt = ctx["start"], ctx["end"]
    lat, lon, tz, hour24 = ctx["lat"], ctx["lon"], ctx["tz"], ctx["hour24"]
    sr = choose_sunrise(start_dt, end_dt, lat, lon, tz)
    if not sr:
        return None, {}
    d, sunrise = sr
    parts = solar_day_parts(d, lat, lon, tz)
    ceremony_end = min(end_dt, parts["sunset"]) if parts else end_dt
    bhadra = intervals_for_name(
        sunrise, ceremony_end, "karana_id", "karana", "Vishti"
    )
    ceremony_start = sunrise
    if bhadra and bhadra[0][0] <= sunrise + timedelta(seconds=2):
        ceremony_start = bhadra[0][1]
    extra = {
        "bhadra_intervals": [
            window(a, b, d, hour24) for a, b in bhadra
        ],
        "bhadra_status": "clear-at-sunrise" if not bhadra else "review-bhadra",
    }
    if ceremony_start < ceremony_end:
        extra["thread_ceremony"] = window(
            ceremony_start, ceremony_end, d, hour24
        )
    return {"date": d, "score": 1}, extra


def select_ghatasthapana(ctx):
    selected = choose_by_period(
        ctx["start"], ctx["end"],
        lambda d: (
            solar_day_parts(d, ctx["lat"], ctx["lon"], ctx["tz"]) or {}
        ).get("first_third"),
    )
    if not selected:
        return None, {}
    d = selected["date"]
    mid = selected["overlap"][0] + (
        selected["overlap"][1] - selected["overlap"][0]
    ) / 2
    state = panchang.state_at(mid)
    return selected, {
        "ghatasthapana": window(
            selected["overlap"][0], selected["overlap"][1],
            d, ctx["hour24"],
        ),
        "warnings": {
            "chitra_nakshatra": state["nakshatra"] == "Chitra",
            "vaidhriti_yoga": state["yoga"] == "Vaidhriti",
        },
    }


def select_aparahna(ctx):
    selected = choose_by_period(
        ctx["start"], ctx["end"],
        lambda d: (
            solar_day_parts(d, ctx["lat"], ctx["lon"], ctx["tz"]) or {}
        ).get("aparahna"),
    )
    if not selected:
        return None, {}
    d = selected["date"]
    parts = solar_day_parts(d, ctx["lat"], ctx["lon"], ctx["tz"])
    vijay_overlap = overlap(
        ctx["start"], ctx["end"],
        parts["vijay"][0], parts["vijay"][1]
    )
    return selected, {
        "aparahna": window(
            parts["aparahna"][0], parts["aparahna"][1],
            d, ctx["hour24"],
        ),
        "vijay_muhurat": (
            window(vijay_overlap[0], vijay_overlap[1], d, ctx["hour24"])
            if vijay_overlap else None
        ),
    }


def select_pradosh(ctx):
    selected = choose_by_period(
        ctx["start"], ctx["end"],
        lambda d: pradosh_window(d, ctx["lat"], ctx["lon"], ctx["tz"]),
    )
    if not selected:
        return None, {}
    d = selected["date"]
    extra = {
        "pradosh": window(
            selected["period"][0], selected["period"][1],
            d, ctx["hour24"],
        ),
        "tithi_pradosh_overlap": window(
            selected["overlap"][0], selected["overlap"][1],
            d, ctx["hour24"],
        ),
    }
    bhadra = intervals_for_name(
        selected["period"][0], selected["period"][1],
        "karana_id", "karana", "Vishti"
    )
    extra["bhadra_intervals"] = [
        window(a, b, d, ctx["hour24"]) for a, b in bhadra
    ]

    if ctx["kind"] == "holi":
        extra["rangwali_holi_date"] = (d + timedelta(days=1)).isoformat()

    if ctx["kind"] == "diwali":
        lagna_rows = lagna.timeline(
            selected["period"][0], selected["period"][1],
            ctx["lat"], ctx["lon"], ctx["hour24"]
        )
        vrishabha = next(
            (row for row in lagna_rows if row["lagna"] == "Vrishabha"), None
        )
        if vrishabha:
            lagna_start = datetime.fromisoformat(vrishabha["start"])
            lagna_end = datetime.fromisoformat(vrishabha["end"])
            puja_overlap = overlap(
                max(ctx["start"], selected["period"][0]),
                min(ctx["end"], selected["period"][1]),
                lagna_start, lagna_end,
            )
            extra["vrishabha_lagna"] = window(
                lagna_start, lagna_end, d, ctx["hour24"]
            )
            extra["lakshmi_puja"] = (
                window(
                    puja_overlap[0], puja_overlap[1],
                    d, ctx["hour24"]
                )
                if puja_overlap else None
            )
        extra["vrishabha_lagna_status"] = "calculated-from-lagna-timeline"

    return selected, extra


def nishita_period(d, lat, lon, tz):
    sunset = set_(d, lat, lon, tz)
    next_sunrise = rise(d + timedelta(days=1), lat, lon, tz)
    if not sunset or not next_sunrise:
        return None
    return (
        sunset + (next_sunrise - sunset) * 7 / 15,
        sunset + (next_sunrise - sunset) * 8 / 15,
    )


def select_nishita(ctx):
    selected = choose_by_period(
        ctx["start"], ctx["end"],
        lambda d: nishita_period(d, ctx["lat"], ctx["lon"], ctx["tz"]),
    )
    if not selected:
        return None, {}
    d = selected["date"]
    rohini = intervals_for_name(
        ctx["start"] - timedelta(days=1),
        ctx["end"] + timedelta(days=1),
        "nakshatra_id", "nakshatra", "Rohini"
    )
    next_sunrise = rise(d + timedelta(days=1), ctx["lat"], ctx["lon"], ctx["tz"])
    parana = max(
        [x for x in [next_sunrise, ctx["end"]] + [b for _, b in rohini] if x]
    )
    return selected, {
        "nishita": window(
            selected["period"][0], selected["period"][1],
            d, ctx["hour24"]
        ),
        "nishita_tithi_overlap": window(
            selected["overlap"][0], selected["overlap"][1],
            d, ctx["hour24"]
        ),
        "rohini_intervals": [
            window(a, b, d, ctx["hour24"]) for a, b in rohini
        ],
        "parana": {
            "after": parana.isoformat(),
            "after_label": panchang.transition_label(
                parana, d + timedelta(days=1), ctx["hour24"]
            ),
            "basis": "after-sunrise-ashtami-rohini-complete",
        },
        "dahi_handi_date": (d + timedelta(days=1)).isoformat(),
        "selection_status": "base-nishita-rule",
    }


def select_moonrise(ctx):
    for d in candidate_dates(ctx["start"], ctx["end"]):
        moonrise = rise(
            d, ctx["lat"], ctx["lon"], ctx["tz"],
            panchang.astronomy.Body.Moon
        )
        if moonrise and ctx["start"] <= moonrise < ctx["end"]:
            sunrise = rise(d, ctx["lat"], ctx["lon"], ctx["tz"])
            return {"date": d, "score": 1}, {
                "moonrise": moonrise.isoformat(),
                "moonrise_label": panchang.transition_label(
                    moonrise, d, ctx["hour24"]
                ),
                "upavasa": (
                    window(sunrise, moonrise, d, ctx["hour24"])
                    if sunrise else None
                ),
                "puja_muhurat_status": "evening-window-selected-by-moonrise",
            }
    return None, {}


SELECTORS = {
    "madhyahna": select_madhyahna,
    "sunrise": select_sunrise,
    "auspicious-choghadiya": select_auspicious_choghadiya,
    "sandhi": select_sandhi,
    "purnima-sunrise": select_purnima_sunrise,
    "ghatasthapana": select_ghatasthapana,
    "aparahna": select_aparahna,
    "pradosh": select_pradosh,
    "nishita": select_nishita,
    "moonrise": select_moonrise,
}


def qualified_occurrence(kind, year, tz):
    rule = FESTIVAL_RULES[kind]
    for start_dt, end_dt, month in search_windows(year, rule, tz):
        if month.get("purnimanta") != rule["month"]:
            continue
        if start_dt.year > year + 1 or end_dt.year < year - 1:
            continue
        return start_dt, end_dt, month
    return None


def calculate_event(kind, year, lat, lon, tz, hour24):
    if kind not in FESTIVAL_RULES:
        raise ValueError("Unsupported festival kind")
    rule = FESTIVAL_RULES[kind]
    occurrence = qualified_occurrence(kind, year, tz)
    if not occurrence:
        return None
    start_dt, end_dt, month = occurrence

    selector = SELECTORS[rule["selector"]]
    selected, extra = selector({
        "kind": kind,
        "rule": rule,
        "start": start_dt,
        "end": end_dt,
        "month": month,
        "lat": lat,
        "lon": lon,
        "tz": tz,
        "hour24": hour24,
    })
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
        "tithi_start_label": panchang.transition_label(
            start_dt, d, hour24
        ),
        "tithi_end_label": panchang.transition_label(
            end_dt, d, hour24
        ),
        "amanta_month": month.get("amanta"),
        "purnimanta_month": month.get("purnimanta"),
        "adhika": bool(month.get("adhika")),
        "rule": {
            "selector": rule["selector"],
            "profile": rule["profile"],
            "engine_version": ENGINE_VERSION,
        },
    }
    event.update(extra)
    return event
