#!/usr/bin/env python3
"""
Shared Tithika Ekadashi / Dwadashi / Mahadwadashi observance rules.

This module is the single fasting-rule contract used by lunar_occurrences.py,
dwadashi.py and future Vaishnava/ISKCON calendar surfaces.

Profiles implemented
--------------------
- Smarta: first eligible Ekadashi day; alternate day exposed when applicable.
- Vaishnava: Arunodaya purity + Vriddhi handling; Mahadwadashi overrides Ekadashi.
- ISKCON-compatible base profile: Mahadwadashi prevails over Ekadashi and Parana
  honours Hari Vasara for ordinary Ekadashi.

Mahadwadashi classification is delegated to the verified detector in
mahadwadashi.py. Shravana/Vishnushrinkhala Parana handling is explicit instead
of being left as a pending flag.
"""
from __future__ import annotations

from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

import mahadwadashi
import panchang

ARUNODAYA_MINUTES = 96
MIN_SHRAVANA_YOGA_MINUTES = 48

MAHA_NAKSHATRA = {
    "Jaya Mahadwadashi": "Pushya",
    "Vijaya Mahadwadashi": "Shravana",
    "Jayanti Mahadwadashi": "Punarvasu",
    "Papanashini Mahadwadashi": "Rohini",
}


def rise(d: date, lat: float, lon: float, tz: ZoneInfo):
    return panchang.rise_set(
        d, lat, lon, tz,
        panchang.astronomy.Body.Sun,
        panchang.astronomy.Direction.Rise,
    )


def set_(d: date, lat: float, lon: float, tz: ZoneInfo):
    return panchang.rise_set(
        d, lat, lon, tz,
        panchang.astronomy.Body.Sun,
        panchang.astronomy.Direction.Set,
    )


def day_parts(d: date, lat: float, lon: float, tz: ZoneInfo):
    sunrise = rise(d, lat, lon, tz)
    sunset = set_(d, lat, lon, tz)
    if not sunrise or not sunset:
        return None
    daylight = sunset - sunrise
    return {
        "sunrise": sunrise,
        "sunset": sunset,
        "pratah_end": sunrise + daylight / 5,
        "sangava_start": sunrise + daylight / 5,
        "sangava_end": sunrise + daylight * 2 / 5,
    }


def label_window(start, end, anchor: date, hour24: bool):
    return {
        "start": start.isoformat() if start else None,
        "end": end.isoformat() if end else None,
        "start_label": panchang.transition_label(start, anchor, hour24) if start else None,
        "end_label": panchang.transition_label(end, anchor, hour24) if end else None,
    }


def hari_vasara_end(dwadashi_start: datetime, dwadashi_end: datetime):
    return dwadashi_start + (dwadashi_end - dwadashi_start) / 4


def named_intervals(start: datetime, end: datetime, key: str, name_key: str, wanted: str):
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


def nakshatra_end_after(moment: datetime, wanted: str):
    state = panchang.state_at(moment + timedelta(seconds=1))
    if state["nakshatra"] != wanted:
        return None
    end = moment + timedelta(days=2)
    transition = panchang.find_transition(
        moment, end, "nakshatra_id", state["nakshatra_id"]
    )
    return transition


def shravana_profile(
    dwadashi_start: datetime,
    dwadashi_end: datetime,
    obs_date: date,
    lat: float,
    lon: float,
    tz: ZoneInfo,
):
    intervals = named_intervals(
        dwadashi_start, dwadashi_end, "nakshatra_id", "nakshatra", "Shravana"
    )
    overlap_minutes = sum(
        (b - a).total_seconds() / 60.0 for a, b in intervals
    )
    sunrise = rise(obs_date, lat, lon, tz)
    ekadashi_at_sunrise = False
    if sunrise:
        state = panchang.state_at(sunrise + timedelta(seconds=1))
        ekadashi_at_sunrise = state["tithi_id"] in (10, 25)

    return {
        "shravana_yoga": overlap_minutes >= MIN_SHRAVANA_YOGA_MINUTES,
        "vishnushrinkhala": (
            overlap_minutes >= MIN_SHRAVANA_YOGA_MINUTES
            and ekadashi_at_sunrise
            and dwadashi_start > sunrise
            if sunrise else False
        ),
        "overlap_minutes": round(overlap_minutes, 2),
        "intervals": [
            {"start": a.isoformat(), "end": b.isoformat()} for a, b in intervals
        ],
    }


def ordinary_ekadashi_parana(
    fasting_date: date,
    dwadashi_start: datetime,
    dwadashi_end: datetime,
    lat: float,
    lon: float,
    tz: ZoneInfo,
    hour24: bool,
):
    parana_date = fasting_date + timedelta(days=1)
    parts = day_parts(parana_date, lat, lon, tz)
    if not parts:
        return None

    sunrise = parts["sunrise"]
    hv_end = hari_vasara_end(dwadashi_start, dwadashi_end)
    start = max(sunrise, hv_end)
    if dwadashi_end > sunrise:
        end = min(parts["pratah_end"], dwadashi_end)
    else:
        end = parts["pratah_end"]

    status = "preferred-pratah"
    if start >= end:
        if dwadashi_end > start:
            end = dwadashi_end
            status = "late-within-dwadashi"
        else:
            # Dwadashi/Hari Vasara geometry can leave no Pratah interval.
            # Surface the earliest lawful instant and a short advisory window.
            end = start + timedelta(minutes=1)
            status = "instant-after-hari-vasara"

    return {
        "date": parana_date.isoformat(),
        **label_window(start, end, parana_date, hour24),
        "sunrise": sunrise.isoformat(),
        "sunrise_label": panchang.transition_label(sunrise, parana_date, hour24),
        "hari_vasara_end": hv_end.isoformat(),
        "hari_vasara_end_label": panchang.transition_label(hv_end, parana_date, hour24),
        "dwadashi_end": dwadashi_end.isoformat(),
        "dwadashi_end_label": panchang.transition_label(dwadashi_end, parana_date, hour24),
        "pratah_end": parts["pratah_end"].isoformat(),
        "status": status,
        "rule": "after-sunrise-and-hari-vasara; prefer-pratah; within-dwadashi-when-available",
    }


def shravana_special_parana(
    fasting_date: date,
    dwadashi_end: datetime,
    lat: float,
    lon: float,
    tz: ZoneInfo,
    hour24: bool,
):
    parana_date = fasting_date + timedelta(days=1)
    parts = day_parts(parana_date, lat, lon, tz)
    if not parts:
        return None

    sunrise = parts["sunrise"]
    shravana_end = nakshatra_end_after(sunrise, "Shravana")

    # Preferred path: after Shravana ends; if that falls in Sangava, wait until
    # Sangava ends. This mirrors the common Shravana-Dwadashi Parana profile.
    preferred = sunrise
    if shravana_end and shravana_end > preferred:
        preferred = shravana_end
    if parts["sangava_start"] <= preferred < parts["sangava_end"]:
        preferred = parts["sangava_end"]

    deadline = dwadashi_end if dwadashi_end > sunrise else None
    status = "shravana-cleared"

    if deadline and preferred < deadline:
        start = preferred
        end = deadline
    elif deadline:
        # If waiting for Shravana/Sangava would miss Dwadashi, use the available
        # morning window before Sangava as the conservative fallback.
        start = sunrise
        end = min(parts["sangava_start"], deadline)
        status = "fallback-before-sangava"
        if start >= end:
            start = min(preferred, deadline)
            end = deadline
            status = "deadline-constrained"
    else:
        start = preferred
        end = preferred + timedelta(minutes=1)
        status = "after-shravana-dwadashi-ended"

    return {
        "date": parana_date.isoformat(),
        **label_window(start, end, parana_date, hour24),
        "sunrise": sunrise.isoformat(),
        "dwadashi_end": dwadashi_end.isoformat(),
        "shravana_end": shravana_end.isoformat() if shravana_end else None,
        "sangava_start": parts["sangava_start"].isoformat(),
        "sangava_end": parts["sangava_end"].isoformat(),
        "status": status,
        "rule": "Shravana/Vishnushrinkhala: prefer after Shravana and outside Sangava; preserve Dwadashi deadline",
    }


def mahadwadashi_parana(
    fasting_date: date,
    dwadashi_end: datetime,
    yogas: list[str],
    lat: float,
    lon: float,
    tz: ZoneInfo,
    hour24: bool,
):
    if "Vijaya Mahadwadashi" in yogas:
        return shravana_special_parana(
            fasting_date, dwadashi_end, lat, lon, tz, hour24
        )

    parana_date = fasting_date + timedelta(days=1)
    parts = day_parts(parana_date, lat, lon, tz)
    if not parts:
        return None
    start = parts["sunrise"]
    waited_for = []

    for yoga in yogas:
        target = MAHA_NAKSHATRA.get(yoga)
        if not target:
            continue
        target_end = nakshatra_end_after(start, target)
        if target_end and target_end > start:
            start = target_end
            waited_for.append({"yoga": yoga, "nakshatra": target, "end": target_end.isoformat()})

    if parts["sangava_start"] <= start < parts["sangava_end"]:
        start = parts["sangava_end"]

    deadline = dwadashi_end if dwadashi_end > parts["sunrise"] else None
    if deadline and start < deadline:
        end = deadline
        status = "mahadwadashi-within-dwadashi"
    elif deadline:
        # Protect the Dwadashi deadline if a Nakshatra wait would otherwise pass it.
        start = parts["sunrise"]
        end = min(parts["sangava_start"], deadline)
        status = "mahadwadashi-deadline-fallback"
    else:
        end = start + timedelta(minutes=1)
        status = "mahadwadashi-next-morning"

    return {
        "date": parana_date.isoformat(),
        **label_window(start, end, parana_date, hour24),
        "sunrise": parts["sunrise"].isoformat(),
        "dwadashi_end": dwadashi_end.isoformat(),
        "waited_for": waited_for,
        "status": status,
        "rule": "Mahadwadashi fast breaks next day; Nakshatra-bound Mahadwadashi waits for its Nakshatra when compatible with Dwadashi deadline",
    }


def base_ekadashi_dates(
    start_dt: datetime,
    end_dt: datetime,
    lat: float,
    lon: float,
    tz: ZoneInfo,
):
    solar = []
    d = start_dt.date() - timedelta(days=1)
    last = end_dt.date() + timedelta(days=2)
    while d <= last:
        sunrise = rise(d, lat, lon, tz)
        if sunrise:
            solar.append((d, sunrise))
        d += timedelta(days=1)

    contained = [(d, sr) for d, sr in solar if start_dt <= sr < end_dt]

    if contained:
        smarta_date = contained[0][0]
        smarta_basis = "ekadashi-at-sunrise"
    else:
        same_day = next((sr for d, sr in solar if d == start_dt.date()), None)
        smarta_date = (
            start_dt.date()
            if same_day and start_dt >= same_day
            else start_dt.date() - timedelta(days=1)
        )
        smarta_basis = "sunrise-skipped-ekadashi"

    if len(contained) >= 2:
        vaishnava_date = contained[1][0]
        vaishnava_basis = "vriddhi-later-day"
    else:
        smarta_sunrise = next((sr for d, sr in solar if d == smarta_date), None)
        arunodaya = (
            smarta_sunrise - timedelta(minutes=ARUNODAYA_MINUTES)
            if smarta_sunrise else None
        )
        if arunodaya and start_dt <= arunodaya < end_dt:
            vaishnava_date = smarta_date
            vaishnava_basis = "shuddha-at-arunodaya"
        else:
            vaishnava_date = smarta_date + timedelta(days=1)
            vaishnava_basis = "gauna-after-dashami-arunodaya"

    return {
        "smarta_date": smarta_date,
        "smarta_basis": smarta_basis,
        "vaishnava_date": vaishnava_date,
        "vaishnava_basis": vaishnava_basis,
        "sunrise_count": len(contained),
    }


def integrated_ekadashi_observance(
    rule: dict,
    start_dt: datetime,
    end_dt: datetime,
    dwadashi_end: datetime,
    lat: float,
    lon: float,
    tz: ZoneInfo,
    hour24: bool,
):
    base = base_ekadashi_dates(start_dt, end_dt, lat, lon, tz)

    md_rule = next(
        row for row in mahadwadashi.DWADASHI_RULES
        if row["paksha"] == rule["paksha"]
    )
    maha_date, yogas, evidence = mahadwadashi.classify_window(
        md_rule, end_dt, dwadashi_end, lat, lon, tz
    )
    valid_maha = (
        bool(yogas)
        and base["smarta_date"] <= maha_date <= base["smarta_date"] + timedelta(days=2)
    )

    smarta = {
        "date": base["smarta_date"].isoformat(),
        "weekday": base["smarta_date"].strftime("%A"),
        "basis": base["smarta_basis"],
        "parana": ordinary_ekadashi_parana(
            base["smarta_date"], end_dt, dwadashi_end, lat, lon, tz, hour24
        ),
    }

    if valid_maha:
        vaish_date = maha_date
        vaish_basis = "mahadwadashi-override"
        vaish_parana = mahadwadashi_parana(
            vaish_date, dwadashi_end, yogas, lat, lon, tz, hour24
        )
    else:
        vaish_date = base["vaishnava_date"]
        vaish_basis = base["vaishnava_basis"]
        vaish_parana = ordinary_ekadashi_parana(
            vaish_date, end_dt, dwadashi_end, lat, lon, tz, hour24
        )

    vaishnava = {
        "date": vaish_date.isoformat(),
        "weekday": vaish_date.strftime("%A"),
        "basis": vaish_basis,
        "parana": vaish_parana,
    }

    return {
        "smarta": smarta,
        "vaishnava": vaishnava,
        "iskcon": {
            **vaishnava,
            "basis": (
                "iskcon-mahadwadashi-override"
                if valid_maha else "iskcon-" + vaish_basis
            ),
        },
        "arunodaya_minutes_before_sunrise": ARUNODAYA_MINUTES,
        "mahadwadashi": {
            "active": valid_maha,
            "date": maha_date.isoformat() if valid_maha else None,
            "yogas": yogas if valid_maha else [],
            "evidence": evidence if valid_maha else {},
            "priority": "Mahadwadashi prevails over ordinary Vaishnava/ISKCON Ekadashi",
        },
    }
