#!/usr/bin/env python3
"""
Reusable Vrat recurrence engine.

This layer deliberately reuses Tithika's verified Panchang/Vrat substrate and
keeps observance selectors explicit. It currently supports:

- Satyanarayana Puja: Purnima occurrence calendar
- Masik Durgashtami: Shukla Ashtami at local sunrise
- Skanda Sashti: documented Panchami-Sashti conjunction rule
- Karthigai: Krittika Nakshatra at local sunrise
- Rohini Vrat: Rohini Nakshatra prevailing after local sunrise
- Sawan Somwar: Mondays inside Shravana, both Purnimanta and Amanta profiles
- Mangala Gauri: Tuesdays inside Shravana, both Purnimanta and Amanta profiles

No database or third-party runtime calendar package is used.
"""
from __future__ import annotations

import json
import sys
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import lunar_occurrences
import panchang

ENGINE_VERSION = "0.1.0"

MODE_TITLES = {
    "satyanarayana": "Satyanarayana Puja",
    "durgashtami": "Masik Durgashtami",
    "skanda-sashti": "Skanda Sashti",
    "karthigai": "Karthigai",
    "rohini": "Rohini Vrat",
    "sawan-somwar": "Sawan Somwar",
    "mangala-gauri": "Mangala Gauri",
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
        result = {
            "events": nakshatra_vrat(
                year, lat, lon, tz, hour24, "Krittika", "Karthigai"
            )
        }
    elif mode == "rohini":
        result = {
            "events": nakshatra_vrat(
                year, lat, lon, tz, hour24, "Rohini", "Rohini Vrat"
            )
        }
    elif mode == "sawan-somwar":
        result = {
            "profiles": shravana_weekdays(
                year, lat, lon, tz, hour24, 0, "Sawan Somwar"
            )
        }
    else:
        result = {
            "profiles": shravana_weekdays(
                year, lat, lon, tz, hour24, 1, "Mangala Gauri"
            )
        }

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
