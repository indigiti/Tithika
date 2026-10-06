#!/usr/bin/env python3
"""
Reusable Vrat recurrence engine.

This layer deliberately reuses Tithika's verified Panchang/Vrat substrate and
keeps observance selectors explicit. It currently supports:

- Satyanarayana Puja: Purnima occurrence calendar
- Masik Durgashtami: Shukla Ashtami at local sunrise
- Skanda Sashti: documented Panchami-Sashti conjunction rule
- Karthigai: Krittika Nakshatra prevailing at local sunset
- Rohini Vrat: Rohini Nakshatra prevailing after local sunrise
- Sawan Somwar: Mondays inside Shravana, both Purnimanta and Amanta profiles
- Mangala Gauri: Tuesdays inside Shravana, both Purnimanta and Amanta profiles
- ISKCON Ekadashi: GCal-compatible Vaishnava dates with Mahadwadashi overrides
- Kalashtami: Krishna Ashtami qualified in the evening/night
- Chandra Darshan: first post-Amavasya sunset with Moon above horizon
- Masik Janmashtami: Krishna Ashtami selected by Nishita overlap
- Ishti/Anvadhan: Purnima/Amavasya observance pairings
- Shraddha: Pitru Paksha Tithi selected by Aparahna overlap
- Purushottam Maas: contiguous Adhika lunar-month spans
- Chaturmasa: Devshayani to Devutthana boundaries by fasting profile

No database or third-party runtime calendar package is used.
"""
from __future__ import annotations

import json
import sys
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import lunar_occurrences
import panchang

ENGINE_VERSION = "0.2.0"

MODE_TITLES = {
    "satyanarayana": "Satyanarayana Puja",
    "durgashtami": "Masik Durgashtami",
    "skanda-sashti": "Skanda Sashti",
    "karthigai": "Karthigai",
    "rohini": "Rohini Vrat",
    "sawan-somwar": "Sawan Somwar",
    "mangala-gauri": "Mangala Gauri",
    "iskcon-ekadashi": "ISKCON Ekadashi",
    "kalashtami": "Kalashtami",
    "chandra-darshan": "Chandra Darshan",
    "masik-janmashtami": "Masik Krishna Janmashtami",
    "ishti-anvadhan": "Ishti & Anvadhan",
    "shraddha": "Shraddha Dates",
    "purushottam-maas": "Purushottam Maas",
    "chaturmasa": "Chaturmasa",
}


def sunrise_for(d: date, lat: float, lon: float, tz: ZoneInfo):
    return panchang.rise_set(
        d, lat, lon, tz,
        panchang.astronomy.Body.Sun,
        panchang.astronomy.Direction.Rise,
    )


def sunset_for(d: date, lat: float, lon: float, tz: ZoneInfo):
    return panchang.rise_set(
        d, lat, lon, tz,
        panchang.astronomy.Body.Sun,
        panchang.astronomy.Direction.Set,
    )


def month_info_at(moment: datetime, state: dict | None = None) -> dict:
    state = state or panchang.state_at(moment)
    return panchang.lunar_month_info(moment, state)


def normalize_month(value) -> str:
    return str(value or "").replace("Adhika ", "").strip()


def display_day(
    d: date,
    sunrise: datetime,
    state: dict,
    month_info: dict,
    hour24: bool,
) -> dict:
    return {
        "date": d.isoformat(),
        "date_label": d.strftime("%B %d, %Y").replace(" 0", " "),
        "weekday": d.strftime("%A"),
        "sunrise": sunrise.isoformat(),
        "sunrise_label": panchang.fmt(sunrise, hour24),
        "tithi": state["tithi"],
        "tithi_number": state["tithi_number"],
        "paksha": state["paksha"],
        "nakshatra": state["nakshatra"],
        "amanta_month": month_info.get("amanta"),
        "purnimanta_month": month_info.get("purnimanta"),
        "adhika_month": bool(month_info.get("adhika")),
    }


def scan_sunrise_days(
    year: int,
    lat: float,
    lon: float,
    tz: ZoneInfo,
    hour24: bool,
    predicate,
) -> list[dict]:
    rows = []
    d = date(year, 1, 1)
    while d.year == year:
        sunrise = sunrise_for(d, lat, lon, tz)
        if sunrise:
            state = panchang.state_at(sunrise + timedelta(seconds=1))
            months = month_info_at(sunrise, state)
            if predicate(d, sunrise, state, months):
                rows.append(display_day(d, sunrise, state, months, hour24))
        d += timedelta(days=1)
    return rows


def exact_tithi_intervals(
    year: int,
    target_tithi_id: int,
    lat: float,
    lon: float,
    tz: ZoneInfo,
) -> list[tuple[datetime, datetime]]:
    start = datetime(year - 1, 12, 30, 0, 0, tzinfo=tz)
    end = datetime(year + 1, 1, 3, 0, 0, tzinfo=tz)
    rows = []
    cursor = start

    while cursor < end:
        state = panchang.state_at(cursor)
        current_id = state["tithi_id"]
        transition = panchang.find_transition(
            cursor, end, "tithi_id", current_id, step_minutes=180
        )
        stop = transition or end
        if current_id == target_tithi_id:
            rows.append((cursor, stop))
        if transition is None:
            break
        cursor = transition + timedelta(seconds=1)
    return rows


def skanda_sashti(
    year: int, lat: float, lon: float, tz: ZoneInfo, hour24: bool
) -> list[dict]:
    rows = []
    seen = set()
    # Shukla Shashthi = tithi_id 5.
    for start, end in exact_tithi_intervals(year, 5, lat, lon, tz):
        civil = start.date()
        sunrise = sunrise_for(civil, lat, lon, tz)
        sunset = sunset_for(civil, lat, lon, tz)
        if not sunrise or not sunset:
            continue

        # Dharmasindhu/Nirnayasindhu selector:
        # if Panchami ends / Sashti starts between sunrise and sunset, select
        # that civil day; if Sashti starts after sunset, use the next civil day.
        selected = civil if start < sunset else civil + timedelta(days=1)
        if selected.year != year or selected in seen:
            continue
        selected_sunrise = sunrise_for(selected, lat, lon, tz)
        if not selected_sunrise:
            continue

        mid = start + (end - start) / 2
        state = panchang.state_at(mid)
        months = month_info_at(mid, state)
        row = display_day(
            selected,
            selected_sunrise,
            panchang.state_at(selected_sunrise + timedelta(seconds=1)),
            month_info_at(
                selected_sunrise,
                panchang.state_at(selected_sunrise + timedelta(seconds=1)),
            ),
            hour24,
        )
        row.update({
            "name": "Skanda Sashti",
            "tithi_start": start.isoformat(),
            "tithi_end": end.isoformat(),
            "tithi_start_label": panchang.transition_label(start, selected, hour24),
            "tithi_end_label": panchang.transition_label(end, selected, hour24),
            "rule_month": months.get("purnimanta"),
            "selection_rule": (
                "select the civil day when Shukla Sashti begins before sunset; "
                "if it begins after sunset, select the next civil day"
            ),
            "panchami_sashti_conjunction": bool(start >= sunrise and start < sunset),
        })
        rows.append(row)
        seen.add(selected)

    rows.sort(key=lambda row: row["date"])
    return rows


def satyanarayana(
    year: int, lat: float, lon: float, tz: ZoneInfo, hour24: bool
) -> list[dict]:
    rule = lunar_occurrences.KINDS["purnima"][0]
    events = lunar_occurrences.events_for_rule(
        year, rule, lat, lon, tz, hour24
    )
    rows = []
    for event in events:
        candidates = [
            row for row in event.get("sunrise_candidates", [])
            if int(row["date"][:4]) == year
        ]
        if not candidates:
            # Preserve exact Purnima occurrence even when no sunrise falls
            # inside it; select the local civil date containing the midpoint.
            start = datetime.fromisoformat(event["start"])
            end = datetime.fromisoformat(event["end"])
            d = (start + (end - start) / 2).date()
            if d.year != year:
                continue
            sunrise = sunrise_for(d, lat, lon, tz)
            if not sunrise:
                continue
            candidates = [{
                "date": d.isoformat(),
                "weekday": d.strftime("%A"),
                "sunrise": sunrise.isoformat(),
                "sunrise_label": panchang.fmt(sunrise, hour24),
            }]

        selected = candidates[0]
        d = date.fromisoformat(selected["date"])
        rows.append({
            "name": "Satyanarayana Puja / Purnima",
            "date": selected["date"],
            "date_label": d.strftime("%B %d, %Y").replace(" 0", " "),
            "weekday": selected["weekday"],
            "sunrise": selected.get("sunrise"),
            "sunrise_label": selected.get("sunrise_label"),
            "amanta_month": event.get("amanta_month"),
            "purnimanta_month": event.get("purnimanta_month"),
            "tithi_start": event["start"],
            "tithi_end": event["end"],
            "selection_rule": "Purnima Tithi occurrence calendar",
        })
    return rows


def durgashtami(
    year: int, lat: float, lon: float, tz: ZoneInfo, hour24: bool
) -> list[dict]:
    rows = scan_sunrise_days(
        year, lat, lon, tz, hour24,
        lambda _d, _sunrise, state, _months:
            state["tithi_id"] == 7 and state["paksha"] == "Shukla Paksha",
    )
    for row in rows:
        row["name"] = "Masik Durgashtami"
        row["selection_rule"] = "Shukla Ashtami prevailing at local sunrise"
    return rows


def karthigai_days(
    year: int, lat: float, lon: float, tz: ZoneInfo, hour24: bool
) -> list[dict]:
    rows = []
    d = date(year, 1, 1)
    while d.year == year:
        sunrise = sunrise_for(d, lat, lon, tz)
        sunset = sunset_for(d, lat, lon, tz)
        if sunrise and sunset:
            evening_state = panchang.state_at(sunset - timedelta(seconds=1))
            if evening_state["nakshatra"] == "Krittika":
                morning_state = panchang.state_at(sunrise + timedelta(seconds=1))
                months = month_info_at(sunrise, morning_state)
                row = display_day(d, sunrise, morning_state, months, hour24)
                row.update({
                    "name": "Karthigai",
                    "sunset": sunset.isoformat(),
                    "sunset_label": panchang.fmt(sunset, hour24),
                    "evening_nakshatra": evening_state["nakshatra"],
                    "selection_rule": "Krittika Nakshatra prevailing at local sunset",
                })
                rows.append(row)
        d += timedelta(days=1)
    return rows


def nakshatra_vrat(
    year: int,
    lat: float,
    lon: float,
    tz: ZoneInfo,
    hour24: bool,
    wanted: str,
    title: str,
) -> list[dict]:
    rows = scan_sunrise_days(
        year, lat, lon, tz, hour24,
        lambda _d, _sunrise, state, _months: state["nakshatra"] == wanted,
    )
    for row in rows:
        row["name"] = title
        row["selection_rule"] = f"{wanted} Nakshatra prevailing after local sunrise"
    return rows


def shravana_weekdays(
    year: int,
    lat: float,
    lon: float,
    tz: ZoneInfo,
    hour24: bool,
    weekday: int,
    title: str,
) -> dict:
    profiles = {"purnimanta": [], "amanta": []}
    d = date(year, 1, 1)
    while d.year == year:
        if d.weekday() != weekday:
            d += timedelta(days=1)
            continue
        sunrise = sunrise_for(d, lat, lon, tz)
        if not sunrise:
            d += timedelta(days=1)
            continue
        state = panchang.state_at(sunrise + timedelta(seconds=1))
        months = month_info_at(sunrise, state)
        base = display_day(d, sunrise, state, months, hour24)
        base["name"] = title
        for profile in ("purnimanta", "amanta"):
            if normalize_month(months.get(profile)) == "Shravana":
                row = {**base}
                row["profile"] = profile
                row["selection_rule"] = (
                    f"{d.strftime('%A')} whose local sunrise is inside "
                    f"{profile.title()} Shravana"
                )
                profiles[profile].append(row)
        d += timedelta(days=1)
    return profiles



def overlap_seconds(a_start: datetime, a_end: datetime, b_start: datetime, b_end: datetime) -> float:
    return max(0.0, (min(a_end, b_end) - max(a_start, b_start)).total_seconds())


def civil_days_around(start: datetime, end: datetime):
    d = start.date() - timedelta(days=1)
    last = end.date() + timedelta(days=1)
    while d <= last:
        yield d
        d += timedelta(days=1)


def local_night(d: date, lat: float, lon: float, tz: ZoneInfo):
    sunset = sunset_for(d, lat, lon, tz)
    next_sunrise = sunrise_for(d + timedelta(days=1), lat, lon, tz)
    if sunset and next_sunrise and next_sunrise > sunset:
        return sunset, next_sunrise
    return None, None


def iskcon_ekadashi(year: int, lat: float, lon: float, tz: ZoneInfo, hour24: bool) -> list[dict]:
    rows = []
    seen = set()
    for rule in lunar_occurrences.KINDS["ekadashi"]:
        for event in lunar_occurrences.events_for_rule(year, rule, lat, lon, tz, hour24):
            obs = (event.get("observance") or {}).get("iskcon") or {}
            date_text = obs.get("date")
            if not date_text or not date_text.startswith(f"{year:04d}-") or date_text in seen:
                continue
            d = date.fromisoformat(date_text)
            sunrise = sunrise_for(d, lat, lon, tz)
            state = panchang.state_at(sunrise + timedelta(seconds=1)) if sunrise else panchang.state_at(datetime.fromisoformat(event["start"]))
            row = {
                "name": event.get("name") or "ISKCON Ekadashi",
                "date": date_text,
                "date_label": d.strftime("%B %d, %Y").replace(" 0", " "),
                "weekday": d.strftime("%A"),
                "sunrise": sunrise.isoformat() if sunrise else None,
                "sunrise_label": panchang.fmt(sunrise, hour24) if sunrise else None,
                "paksha": event.get("paksha"),
                "tithi": state.get("tithi"),
                "tithi_start": event.get("start"),
                "tithi_end": event.get("end"),
                "amanta_month": event.get("amanta_month"),
                "purnimanta_month": event.get("purnimanta_month"),
                "basis": obs.get("basis"),
                "parana": obs.get("parana"),
                "mahadwadashi": (event.get("observance") or {}).get("mahadwadashi"),
                "selection_rule": "GCal-compatible ISKCON profile: Arunodaya/Vriddhi selection with verified Mahadwadashi override",
            }
            rows.append(row)
            seen.add(date_text)
    rows.sort(key=lambda row: row["date"])
    return rows


def kalashtami(year: int, lat: float, lon: float, tz: ZoneInfo, hour24: bool) -> list[dict]:
    rows = []
    for start, end in exact_tithi_intervals(year, 22, lat, lon, tz):
        candidates = []
        for d in civil_days_around(start, end):
            sunset, next_sunrise = local_night(d, lat, lon, tz)
            if not sunset or not next_sunrise:
                continue
            one_ghati = sunset + timedelta(minutes=24)
            qualified = start <= one_ghati < end
            overlap = overlap_seconds(start, end, sunset, next_sunrise)
            if overlap > 0:
                candidates.append((qualified, overlap, d, sunset, next_sunrise))
        if not candidates:
            continue
        qualified = [x for x in candidates if x[0]]
        chosen = max(qualified or candidates, key=lambda x: x[1])
        _, overlap, d, sunset, next_sunrise = chosen
        if d.year != year:
            continue
        sunrise = sunrise_for(d, lat, lon, tz)
        state = panchang.state_at(max(start, sunset) + timedelta(seconds=1))
        months = month_info_at(max(start, sunset), state)
        rows.append({
            "name": "Kalashtami",
            "date": d.isoformat(),
            "date_label": d.strftime("%B %d, %Y").replace(" 0", " "),
            "weekday": d.strftime("%A"),
            "sunrise": sunrise.isoformat() if sunrise else None,
            "sunrise_label": panchang.fmt(sunrise, hour24) if sunrise else None,
            "sunset": sunset.isoformat(),
            "sunset_label": panchang.fmt(sunset, hour24),
            "tithi": "Krishna Ashtami",
            "paksha": "Krishna Paksha",
            "tithi_start": start.isoformat(),
            "tithi_end": end.isoformat(),
            "amanta_month": months.get("amanta"),
            "purnimanta_month": months.get("purnimanta"),
            "basis": "ashtami-one-ghati-after-sunset" if chosen[0] else "maximum-night-overlap",
            "night_overlap_minutes": round(overlap / 60.0, 2),
            "selection_rule": "Krishna Ashtami prevailing one Ghati after local sunset; otherwise choose the civil night with maximum Ashtami overlap",
        })
    rows.sort(key=lambda row: row["date"])
    return rows


def masik_janmashtami(year: int, lat: float, lon: float, tz: ZoneInfo, hour24: bool) -> list[dict]:
    rows = []
    for start, end in exact_tithi_intervals(year, 22, lat, lon, tz):
        candidates = []
        for d in civil_days_around(start, end):
            sunset, next_sunrise = local_night(d, lat, lon, tz)
            if not sunset or not next_sunrise:
                continue
            muhurta = (next_sunrise - sunset) / 15
            nishita_start = sunset + muhurta * 7
            nishita_end = sunset + muhurta * 8
            overlap = overlap_seconds(start, end, nishita_start, nishita_end)
            if overlap > 0:
                candidates.append((overlap, d, sunset, next_sunrise, nishita_start, nishita_end))
        if not candidates:
            continue
        overlap, d, sunset, next_sunrise, nishita_start, nishita_end = max(candidates, key=lambda x: x[0])
        if d.year != year:
            continue
        sunrise = sunrise_for(d, lat, lon, tz)
        state = panchang.state_at(max(start, nishita_start) + timedelta(seconds=1))
        months = month_info_at(max(start, nishita_start), state)
        rows.append({
            "name": "Masik Krishna Janmashtami",
            "date": d.isoformat(),
            "date_label": d.strftime("%B %d, %Y").replace(" 0", " "),
            "weekday": d.strftime("%A"),
            "sunrise": sunrise.isoformat() if sunrise else None,
            "sunrise_label": panchang.fmt(sunrise, hour24) if sunrise else None,
            "tithi": "Krishna Ashtami",
            "paksha": "Krishna Paksha",
            "tithi_start": start.isoformat(),
            "tithi_end": end.isoformat(),
            "amanta_month": months.get("amanta"),
            "purnimanta_month": months.get("purnimanta"),
            "nishita_start": nishita_start.isoformat(),
            "nishita_end": nishita_end.isoformat(),
            "basis": "maximum-nishita-overlap",
            "nishita_overlap_minutes": round(overlap / 60.0, 2),
            "selection_rule": "Krishna Ashtami selected on the civil night where it overlaps local Nishita Kaal",
        })
    rows.sort(key=lambda row: row["date"])
    return rows


def chandra_darshan(year: int, lat: float, lon: float, tz: ZoneInfo, hour24: bool) -> list[dict]:
    rows = []
    for _start, end in exact_tithi_intervals(year, 29, lat, lon, tz):
        selected = None
        for offset in range(0, 3):
            d = end.date() + timedelta(days=offset)
            if d.year not in (year, year + 1):
                continue
            sunset = sunset_for(d, lat, lon, tz)
            moonset = panchang.rise_set(d, lat, lon, tz, panchang.astronomy.Body.Moon, panchang.astronomy.Direction.Set)
            if not sunset or not moonset or moonset <= sunset:
                continue
            state = panchang.state_at(sunset + timedelta(seconds=1))
            if state["paksha"] == "Shukla Paksha" and state["tithi_number"] <= 2:
                selected = (d, sunset, moonset, state)
                break
        if not selected:
            continue
        d, sunset, moonset, state = selected
        if d.year != year:
            continue
        sunrise = sunrise_for(d, lat, lon, tz)
        months = month_info_at(sunset, state)
        rows.append({
            "name": "Chandra Darshan",
            "date": d.isoformat(),
            "date_label": d.strftime("%B %d, %Y").replace(" 0", " "),
            "weekday": d.strftime("%A"),
            "sunrise": sunrise.isoformat() if sunrise else None,
            "sunrise_label": panchang.fmt(sunrise, hour24) if sunrise else None,
            "sunset": sunset.isoformat(),
            "sunset_label": panchang.fmt(sunset, hour24),
            "moonset": moonset.isoformat(),
            "moonset_label": panchang.fmt(moonset, hour24),
            "tithi": state["tithi"],
            "paksha": state["paksha"],
            "amanta_month": months.get("amanta"),
            "purnimanta_month": months.get("purnimanta"),
            "basis": "first-post-amavasya-sunset-with-moonset-after-sunset",
            "visibility_minutes": round((moonset - sunset).total_seconds() / 60.0, 2),
            "selection_rule": "First post-Amavasya local sunset with the young Moon setting after sunset",
        })
    rows.sort(key=lambda row: row["date"])
    return rows


def select_tithi_observance_date(start: datetime, end: datetime, lat: float, lon: float, tz: ZoneInfo) -> date:
    candidates = []
    for d in civil_days_around(start, end):
        sunrise = sunrise_for(d, lat, lon, tz)
        if sunrise and start <= sunrise < end:
            candidates.append(d)
    if candidates:
        return candidates[0]
    return (start + (end - start) / 2).date()


def ishti_anvadhan(year: int, lat: float, lon: float, tz: ZoneInfo, hour24: bool) -> list[dict]:
    rows = []
    for tithi_id, lunar_name in ((14, "Purnima"), (29, "Amavasya")):
        for start, end in exact_tithi_intervals(year, tithi_id, lat, lon, tz):
            anvadhan_date = select_tithi_observance_date(start, end, lat, lon, tz)
            if anvadhan_date.year != year:
                continue
            mid = start + (end - start) / 2
            state = panchang.state_at(mid)
            months = month_info_at(mid, state)
            for name, d, basis in (
                (f"{lunar_name} Anvadhan", anvadhan_date, f"{lunar_name.lower()}-observance-day"),
                (f"{lunar_name} Ishti", anvadhan_date + timedelta(days=1), "day-after-anvadhan"),
            ):
                if d.year != year:
                    continue
                sunrise = sunrise_for(d, lat, lon, tz)
                rows.append({
                    "name": name,
                    "date": d.isoformat(),
                    "date_label": d.strftime("%B %d, %Y").replace(" 0", " "),
                    "weekday": d.strftime("%A"),
                    "sunrise": sunrise.isoformat() if sunrise else None,
                    "sunrise_label": panchang.fmt(sunrise, hour24) if sunrise else None,
                    "tithi": lunar_name,
                    "tithi_start": start.isoformat(),
                    "tithi_end": end.isoformat(),
                    "amanta_month": months.get("amanta"),
                    "purnimanta_month": months.get("purnimanta"),
                    "basis": basis,
                    "selection_rule": "Anvadhan follows the Purnima/Amavasya observance day; Ishti is the following civil day",
                })
    rows.sort(key=lambda row: (row["date"], row["name"]))
    return rows


def purushottam_maas(year: int, lat: float, lon: float, tz: ZoneInfo, hour24: bool) -> list[dict]:
    days = []
    d = date(year, 1, 1)
    while d.year == year:
        sunrise = sunrise_for(d, lat, lon, tz)
        if sunrise:
            state = panchang.state_at(sunrise + timedelta(seconds=1))
            months = month_info_at(sunrise, state)
            if months.get("adhika"):
                days.append((d, sunrise, state, months))
        d += timedelta(days=1)
    rows = []
    if not days:
        return rows
    groups = []
    current = [days[0]]
    for item in days[1:]:
        if item[0] == current[-1][0] + timedelta(days=1):
            current.append(item)
        else:
            groups.append(current)
            current = [item]
    groups.append(current)
    for group in groups:
        start_day, sunrise, state, months = group[0]
        end_day = group[-1][0]
        month_name = months.get("amanta") or "Adhika Maas"
        rows.append({
            "name": f"Purushottam Maas · {month_name}",
            "date": start_day.isoformat(),
            "date_label": start_day.strftime("%B %d, %Y").replace(" 0", " "),
            "weekday": start_day.strftime("%A"),
            "sunrise": sunrise.isoformat(),
            "sunrise_label": panchang.fmt(sunrise, hour24),
            "tithi": state.get("tithi"),
            "paksha": state.get("paksha"),
            "amanta_month": month_name,
            "purnimanta_month": months.get("purnimanta"),
            "basis": f"through-{end_day.isoformat()} · {len(group)} sunrise days",
            "span_start": start_day.isoformat(),
            "span_end": end_day.isoformat(),
            "day_count": len(group),
            "selection_rule": "Contiguous civil dates whose local sunrise belongs to an Adhika lunar month",
        })
    return rows


def aparahna_window(d: date, lat: float, lon: float, tz: ZoneInfo):
    sunrise = sunrise_for(d, lat, lon, tz)
    sunset = sunset_for(d, lat, lon, tz)
    if not sunrise or not sunset:
        return None, None, None, None
    fifth = (sunset - sunrise) / 5
    return sunrise + fifth * 3, sunrise + fifth * 4, sunrise, sunset


def shraddha(year: int, lat: float, lon: float, tz: ZoneInfo, hour24: bool) -> list[dict]:
    rows = []
    tithi_names = {
        14: "Purnima Shraddha", 15: "Pratipada Shraddha", 16: "Dwitiya Shraddha",
        17: "Tritiya Shraddha", 18: "Chaturthi Shraddha", 19: "Panchami Shraddha",
        20: "Shashthi Shraddha", 21: "Saptami Shraddha", 22: "Ashtami Shraddha",
        23: "Navami Shraddha", 24: "Dashami Shraddha", 25: "Ekadashi Shraddha",
        26: "Dwadashi Shraddha", 27: "Trayodashi Shraddha", 28: "Chaturdashi Shraddha",
        29: "Sarva Pitru Amavasya",
    }
    for tithi_id in range(14, 30):
        for start, end in exact_tithi_intervals(year, tithi_id, lat, lon, tz):
            mid = start + (end - start) / 2
            mid_state = panchang.state_at(mid)
            months = month_info_at(mid, mid_state)
            amanta = normalize_month(months.get("amanta"))
            purnimanta = normalize_month(months.get("purnimanta"))
            in_pitru_month = (
                (tithi_id == 14 and amanta == "Bhadrapada")
                or (tithi_id >= 15 and (amanta == "Bhadrapada" or purnimanta == "Ashwina"))
            )
            if not in_pitru_month:
                continue
            candidates = []
            for d in civil_days_around(start, end):
                a_start, a_end, sunrise, sunset = aparahna_window(d, lat, lon, tz)
                if not a_start:
                    continue
                overlap = overlap_seconds(start, end, a_start, a_end)
                if overlap > 0:
                    candidates.append((overlap, d, a_start, a_end, sunrise, sunset))
            if not candidates:
                continue
            overlap, d, a_start, a_end, sunrise, sunset = max(candidates, key=lambda x: x[0])
            if d.year != year:
                continue
            state = panchang.state_at(max(start, a_start) + timedelta(seconds=1))
            rows.append({
                "name": tithi_names[tithi_id],
                "date": d.isoformat(),
                "date_label": d.strftime("%B %d, %Y").replace(" 0", " "),
                "weekday": d.strftime("%A"),
                "sunrise": sunrise.isoformat(),
                "sunrise_label": panchang.fmt(sunrise, hour24),
                "tithi": state.get("tithi"),
                "paksha": state.get("paksha"),
                "tithi_start": start.isoformat(),
                "tithi_end": end.isoformat(),
                "amanta_month": months.get("amanta"),
                "purnimanta_month": months.get("purnimanta"),
                "aparahna_start": a_start.isoformat(),
                "aparahna_end": a_end.isoformat(),
                "basis": "maximum-aparahna-overlap",
                "aparahna_overlap_minutes": round(overlap / 60.0, 2),
                "selection_rule": "Pitru Paksha Tithi selected on the civil day where it has maximum overlap with local Aparahna",
            })
    rows.sort(key=lambda row: row["date"])
    return rows


def chaturmasa(year: int, lat: float, lon: float, tz: ZoneInfo, hour24: bool) -> list[dict]:
    events = []
    for rule in lunar_occurrences.KINDS["ekadashi"]:
        if rule["paksha"] != "Shukla Paksha":
            continue
        events.extend(lunar_occurrences.events_for_rule(year, rule, lat, lon, tz, hour24))
    start_event = next((e for e in events if normalize_month(e.get("purnimanta_month")) == "Ashadha"), None)
    end_event = next((e for e in events if normalize_month(e.get("purnimanta_month")) == "Kartika"), None)
    if not start_event or not end_event:
        return []
    rows = []
    for profile, label in (("smarta", "Smarta"), ("vaishnava", "Vaishnava"), ("iskcon", "ISKCON")):
        start_obs = (start_event.get("observance") or {}).get(profile) or {}
        end_obs = (end_event.get("observance") or {}).get(profile) or {}
        if not start_obs.get("date") or not end_obs.get("date"):
            continue
        d = date.fromisoformat(start_obs["date"])
        rows.append({
            "name": f"{label} Chaturmasa",
            "date": start_obs["date"],
            "date_label": d.strftime("%B %d, %Y").replace(" 0", " "),
            "weekday": d.strftime("%A"),
            "tithi": "Shukla Ekadashi",
            "paksha": "Shukla Paksha",
            "amanta_month": start_event.get("amanta_month"),
            "purnimanta_month": start_event.get("purnimanta_month"),
            "basis": f"Devshayani {start_obs['date']} → Devutthana {end_obs['date']}",
            "span_start": start_obs["date"],
            "span_end": end_obs["date"],
            "parana": start_obs.get("parana"),
            "selection_rule": f"{label} Ekadashi profile from Ashadha Shukla Devshayani through Kartika Shukla Devutthana",
        })
    return rows

def main():
    payload = json.loads(sys.stdin.read() or "{}")
    mode = str(payload.get("mode") or "durgashtami").strip().lower()
    if mode not in MODE_TITLES:
        raise ValueError("Unsupported Vrat recurrence mode")

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
        payload.get("date") or datetime.now(tz).strftime("%Y-%m-%d"),
        "%Y-%m-%d",
    ).date()
    hour24 = bool(payload.get("hour24", False))
    year = selected.year

    if mode == "satyanarayana":
        result = {"events": satyanarayana(year, lat, lon, tz, hour24)}
    elif mode == "durgashtami":
        result = {"events": durgashtami(year, lat, lon, tz, hour24)}
    elif mode == "skanda-sashti":
        result = {"events": skanda_sashti(year, lat, lon, tz, hour24)}
    elif mode == "karthigai":
        result = {"events": karthigai_days(year, lat, lon, tz, hour24)}
    elif mode == "rohini":
        result = {"events": nakshatra_vrat(year, lat, lon, tz, hour24, "Rohini", "Rohini Vrat")}
    elif mode == "sawan-somwar":
        result = {"profiles": shravana_weekdays(year, lat, lon, tz, hour24, 0, "Sawan Somwar")}
    elif mode == "mangala-gauri":
        result = {"profiles": shravana_weekdays(year, lat, lon, tz, hour24, 1, "Mangala Gauri")}
    elif mode == "iskcon-ekadashi":
        result = {"events": iskcon_ekadashi(year, lat, lon, tz, hour24)}
    elif mode == "kalashtami":
        result = {"events": kalashtami(year, lat, lon, tz, hour24)}
    elif mode == "chandra-darshan":
        result = {"events": chandra_darshan(year, lat, lon, tz, hour24)}
    elif mode == "masik-janmashtami":
        result = {"events": masik_janmashtami(year, lat, lon, tz, hour24)}
    elif mode == "ishti-anvadhan":
        result = {"events": ishti_anvadhan(year, lat, lon, tz, hour24)}
    elif mode == "shraddha":
        result = {"events": shraddha(year, lat, lon, tz, hour24)}
    elif mode == "purushottam-maas":
        result = {"events": purushottam_maas(year, lat, lon, tz, hour24)}
    else:
        result = {"events": chaturmasa(year, lat, lon, tz, hour24)}

    events = result.get("events")
    print(json.dumps({
        "ok": True,
        "mode": mode,
        "title": MODE_TITLES[mode],
        "year": year,
        "engine": {
            "name": "tithika-vrat-recurrence",
            "version": ENGINE_VERSION,
            "panchang_version": panchang.ENGINE_VERSION,
            "ayanamsha": "Lahiri / Chitrapaksha",
        },
        "location": {
            "city": (payload.get("city") or "Current location").strip()[:120],
            "lat": lat,
            "lon": lon,
            "timezone": timezone_name,
        },
        "count": len(events) if isinstance(events, list) else sum(
            len(v) for v in result.get("profiles", {}).values()
        ),
        **result,
    }, ensure_ascii=False))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(json.dumps({
            "ok": False,
            "error": str(exc),
            "code": "VRAT_RECURRENCE_FAILED",
        }))
        sys.exit(1)
