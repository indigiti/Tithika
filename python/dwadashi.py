#!/usr/bin/env python3
"""
Tithika Dwadashi observance engine.

Builds a location-aware Dwadashi year calendar from exact Lahiri Tithi windows.

Rules implemented
-----------------
- Select the civil/Hindu day with the greatest Dwadashi overlap between one
  local sunrise and the next.
- Name the observance from the Purnimanta lunar month.
- Ordinary Parana is next-day sunrise through end of Pratahkal (first fifth of
  daylight), capped by Dwadashi end when Dwadashi survives sunrise.
- Vishnushrinkhala / Mahadwadashi-special Parana exceptions remain flagged
  instead of being guessed.
"""
from __future__ import annotations

import json
import sys
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import panchang
import vrat_rules

RULES = [
    {
        "paksha": "Shukla Paksha",
        "tithi_id": 11,
        "start_angle": 132.0,
        "end_angle": 144.0,
    },
    {
        "paksha": "Krishna Paksha",
        "tithi_id": 26,
        "start_angle": 312.0,
        "end_angle": 324.0,
    },
]

SHUKLA_NAMES = {
    "Pausha": "Kurma Dwadashi",
    "Magha": "Bhishma Dwadashi",
    "Phalguna": "Narasimha Dwadashi",
    "Chaitra": "Vamana Dwadashi",
    "Vaishakha": "Parashurama Dwadashi",
    "Jyeshtha": "Ramalakshmana Dwadashi",
    "Ashadha": "Vasudeva Dwadashi",
    "Shravana": "Damodara Dwadashi",
    "Bhadrapada": "Kalki Dwadashi",
    "Ashwina": "Padmanabha Dwadashi",
    "Kartika": "Yogeshwara Dwadashi",
    "Margashirsha": "Matsya Dwadashi",
}

ALIASES = {
    ("Chaitra", "Shukla Paksha"): ["Madana Dwadashi"],
    ("Jyeshtha", "Shukla Paksha"): ["Champaka Dwadashi"],
    ("Kartika", "Shukla Paksha"): ["Garuda Dwadashi"],
    ("Kartika", "Krishna Paksha"): ["Govatsa Dwadashi"],
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


def overlap_seconds(a0, a1, b0, b1):
    return max(0.0, (min(a1, b1) - max(a0, b0)).total_seconds())


def select_date(start_dt: datetime, end_dt: datetime, lat, lon, tz):
    d = start_dt.date() - timedelta(days=1)
    last = end_dt.date() + timedelta(days=1)
    best = None
    while d <= last:
        sunrise = rise(d, lat, lon, tz)
        next_sunrise = rise(d + timedelta(days=1), lat, lon, tz)
        if sunrise and next_sunrise:
            score = overlap_seconds(start_dt, end_dt, sunrise, next_sunrise)
            if score > 0 and (best is None or score > best["overlap_seconds"]):
                best = {
                    "date": d,
                    "sunrise": sunrise,
                    "next_sunrise": next_sunrise,
                    "overlap_seconds": score,
                }
        d += timedelta(days=1)

    if best:
        return best

    # Polar / missing-rise fallback: use civil date containing most of the Tithi.
    return {
        "date": start_dt.date(),
        "sunrise": None,
        "next_sunrise": None,
        "overlap_seconds": (end_dt - start_dt).total_seconds(),
    }


def parana_for_observance(obs_date: date, dwadashi_end: datetime, lat, lon, tz, hour24):
    parana_date = obs_date + timedelta(days=1)
    sunrise = rise(parana_date, lat, lon, tz)
    sunset = set_(parana_date, lat, lon, tz)
    if sunrise is None or sunset is None:
        return None

    pratah_end = sunrise + (sunset - sunrise) / 5
    dwadashi_after_sunrise = dwadashi_end > sunrise
    end = min(pratah_end, dwadashi_end) if dwadashi_after_sunrise else pratah_end
    status = "within-dwadashi" if dwadashi_after_sunrise else "dwadashi-ended-before-sunrise"

    return {
        "date": parana_date.isoformat(),
        "start": sunrise.isoformat(),
        "end": end.isoformat(),
        "start_label": panchang.transition_label(sunrise, parana_date, hour24),
        "end_label": panchang.transition_label(end, parana_date, hour24),
        "pratah_end": pratah_end.isoformat(),
        "pratah_end_label": panchang.transition_label(pratah_end, parana_date, hour24),
        "dwadashi_end": dwadashi_end.isoformat(),
        "dwadashi_end_label": panchang.transition_label(dwadashi_end, parana_date, hour24),
        "status": status,
        "special_rule_pending": False,
    }


def month_and_name(start_dt, end_dt, selected_date, rule, lat, lon, tz):
    sunrise = rise(selected_date, lat, lon, tz)
    reference = sunrise or (start_dt + (end_dt - start_dt) / 2)
    state = panchang.state_at(reference)
    month = panchang.lunar_month_info(reference, state)
    purnimanta = month.get("purnimanta")
    adhika = bool(month.get("adhika"))

    if rule["paksha"] == "Shukla Paksha":
        base = SHUKLA_NAMES.get(purnimanta, f"{purnimanta or ''} Dwadashi".strip())
    else:
        # Krishna Dwadashi carries the previous Shukla Dwadashi's deity/name.
        names = list(SHUKLA_NAMES.keys())
        if purnimanta in names:
            previous_month = names[(names.index(purnimanta) - 1) % len(names)]
            deity_name = SHUKLA_NAMES.get(previous_month, "Dwadashi").replace(" Dwadashi", "")
            base = f"Krishna {deity_name} Dwadashi"
        else:
            base = "Krishna Dwadashi"

    if adhika:
        base = "Adhika " + base

    aliases = ALIASES.get((purnimanta, rule["paksha"]), [])
    return month, base, aliases


def shraavana_special(start_dt, end_dt, obs_date, lat, lon, tz):
    """Flag Shravana/Dwadashi combinations that need Vishnushrinkhala Parana rules."""
    sunrise = rise(obs_date, lat, lon, tz)
    sunset = set_(obs_date, lat, lon, tz)
    if not sunrise or not sunset:
        return False
    s0 = panchang.state_at(sunrise + timedelta(seconds=1))
    s1 = panchang.state_at(sunset - timedelta(seconds=1))
    return s0["nakshatra"] == "Shravana" or s1["nakshatra"] == "Shravana"


def events_for_rule(year, rule, lat, lon, tz, hour24):
    cursor = panchang.astronomy_time(datetime(year - 1, 12, 1, tzinfo=tz))
    events = []

    for _ in range(18):
        start_event = panchang.astronomy.SearchMoonPhase(rule["start_angle"], cursor, 40.0)
        if start_event is None:
            break
        end_event = panchang.astronomy.SearchMoonPhase(rule["end_angle"], start_event, 3.0)
        if end_event is None:
            break

        start_dt = panchang.datetime_from_astronomy(start_event, tz)
        end_dt = panchang.datetime_from_astronomy(end_event, tz)
        selected = select_date(start_dt, end_dt, lat, lon, tz)
        obs_date = selected["date"]

        if obs_date.year == year:
            month, name, aliases = month_and_name(
                start_dt, end_dt, obs_date, rule, lat, lon, tz
            )
            shravana = vrat_rules.shravana_profile(
                start_dt, end_dt, obs_date, lat, lon, tz
            )
            if shravana["shravana_yoga"]:
                parana = vrat_rules.shravana_special_parana(
                    obs_date, end_dt, lat, lon, tz, hour24
                )
            else:
                parana = parana_for_observance(
                    obs_date, end_dt, lat, lon, tz, hour24
                )

            events.append({
                "date": obs_date.isoformat(),
                "weekday": obs_date.strftime("%A"),
                "name": name,
                "aliases": aliases,
                "paksha": rule["paksha"],
                "tithi_start": start_dt.isoformat(),
                "tithi_end": end_dt.isoformat(),
                "tithi_start_label": panchang.transition_label(start_dt, obs_date, hour24),
                "tithi_end_label": panchang.transition_label(end_dt, obs_date, hour24),
                "amanta_month": month.get("amanta"),
                "purnimanta_month": month.get("purnimanta"),
                "adhika": bool(month.get("adhika")),
                "selected_overlap_minutes": round(selected["overlap_seconds"] / 60.0, 2),
                "parana": parana,
                "shravana_yoga": shravana["shravana_yoga"],
                "vishnushrinkhala_yoga": shravana["vishnushrinkhala"],
                "shravana_evidence": shravana,
            })

        if start_dt.year > year and start_dt.month > 1:
            break
        cursor = panchang.astronomy_time(start_dt + timedelta(days=2))

    return events


def main():
    payload = json.loads(sys.stdin.read() or "{}")
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

    rows = []
    for rule in RULES:
        rows.extend(events_for_rule(selected.year, rule, lat, lon, tz, hour24))
    rows.sort(key=lambda row: (row["date"], row["tithi_start"]))

    print(json.dumps({
        "ok": True,
        "year": selected.year,
        "location": {
            "city": city,
            "lat": lat,
            "lon": lon,
            "timezone": timezone_name,
        },
        "engine": {
            "name": "tithika-dwadashi",
            "version": "0.2.0",
            "panchang_version": panchang.ENGINE_VERSION,
            "status": "rule-selected",
        },
        "events": rows,
        "note": (
            "Dwadashi dates use exact Lahiri Tithi windows and local sunrise-day overlap. "
            "Ordinary next-day Parana uses sunrise through Pratahkal, capped by Dwadashi end. "
            "Shravana Yoga and Vishnushrinkhala cases use the shared special-Parana rule profile rather than a pending flag."
        ),
    }, ensure_ascii=False))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(json.dumps({
            "ok": False,
            "error": str(exc),
            "code": "DWADASHI_CALCULATION_FAILED",
        }))
        sys.exit(1)