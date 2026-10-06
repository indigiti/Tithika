#!/usr/bin/env python3
"""
Tithika Mahadwadashi detector.

This module classifies the eight traditional Mahadwadashi combinations using
the shared Lahiri Panchang core. It is intentionally a detector first: multiple
Mahadwadashi yogas may coexist on one Dwadashi, and the detector does not yet
override the base Ekadashi/Parana selector.

Primary rule profile used by Tithika
------------------------------------
- Unmilini: preceding Ekadashi spans two local sunrises.
- Vanjuli: an extended Dwadashi remains Shuddha from sunrise through sunset.
- Trisparsha: Ekadashi ends during Arunodaya, Dwadashi prevails at sunrise/daytime
  and Trayodashi prevails by the following sunrise.
- Pakshavarddhini: the Purnima/Amavasya ending that fortnight spans two sunrises.
- Jaya: Dwadashi day with Pushya Nakshatra from sunrise to sunset.
- Vijaya: Shukla Dwadashi day with Shravana Nakshatra from sunrise to sunset.
- Jayanti: Dwadashi day with Punarvasu Nakshatra from sunrise to sunset.
- Papanashini: Dwadashi day with Rohini Nakshatra from sunrise to sunset.
"""
from __future__ import annotations

import json
import sys
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import panchang

DWADASHI_RULES = [
    {
        "paksha": "Shukla Paksha",
        "tithi_id": 11,
        "start_angle": 132.0,
        "end_angle": 144.0,
        "ekadashi_start_angle": 120.0,
        "final_start_angle": 168.0,
        "final_end_angle": 180.0,
        "final_tithi": "Purnima",
    },
    {
        "paksha": "Krishna Paksha",
        "tithi_id": 26,
        "start_angle": 312.0,
        "end_angle": 324.0,
        "ekadashi_start_angle": 300.0,
        "final_start_angle": 348.0,
        "final_end_angle": 0.0,
        "final_tithi": "Amavasya",
    },
]

NAKSHATRA_YOGAS = [
    ("Jaya Mahadwadashi", "Pushya", None),
    ("Vijaya Mahadwadashi", "Shravana", "Shukla Paksha"),
    ("Jayanti Mahadwadashi", "Punarvasu", None),
    ("Papanashini Mahadwadashi", "Rohini", None),
]


def local_sunrise(d: date, lat: float, lon: float, tz: ZoneInfo):
    return panchang.rise_set(
        d, lat, lon, tz, panchang.astronomy.Body.Sun, panchang.astronomy.Direction.Rise
    )


def local_sunset(d: date, lat: float, lon: float, tz: ZoneInfo):
    return panchang.rise_set(
        d, lat, lon, tz, panchang.astronomy.Body.Sun, panchang.astronomy.Direction.Set
    )


def sunrises_between(start: datetime, end: datetime, lat: float, lon: float, tz: ZoneInfo):
    rows = []
    d = start.date() - timedelta(days=1)
    last = end.date() + timedelta(days=1)
    while d <= last:
        sunrise = local_sunrise(d, lat, lon, tz)
        if sunrise is not None and start <= sunrise < end:
            rows.append(sunrise)
        d += timedelta(days=1)
    return rows


def search_phase_after(angle: float, start_dt: datetime, days: float):
    return panchang.astronomy.SearchMoonPhase(
        angle, panchang.astronomy_time(start_dt), days
    )


def previous_ekadashi_start(rule: dict, dwadashi_start: datetime, tz: ZoneInfo):
    search_from = dwadashi_start - timedelta(days=2)
    found = search_phase_after(rule["ekadashi_start_angle"], search_from, 3.0)
    return panchang.datetime_from_astronomy(found, tz) if found else None


def final_tithi_window(rule: dict, dwadashi_end: datetime, tz: ZoneInfo):
    start_event = search_phase_after(rule["final_start_angle"], dwadashi_end, 5.0)
    if start_event is None:
        return None, None
    end_event = panchang.astronomy.SearchMoonPhase(
        rule["final_end_angle"], start_event, 3.0
    )
    if end_event is None:
        return None, None
    return (
        panchang.datetime_from_astronomy(start_event, tz),
        panchang.datetime_from_astronomy(end_event, tz),
    )


def ordinary_dwadashi_date(start_dt: datetime, end_dt: datetime, lat, lon, tz):
    d = start_dt.date() - timedelta(days=1)
    last = end_dt.date() + timedelta(days=1)
    while d <= last:
        sunrise = local_sunrise(d, lat, lon, tz)
        if sunrise is not None and start_dt <= sunrise < end_dt:
            return d
        d += timedelta(days=1)
    return start_dt.date()


def trisparsha_date(rule: dict, start_dt: datetime, end_dt: datetime, lat, lon, tz):
    next_id = (rule["tithi_id"] + 1) % 30
    d = start_dt.date() - timedelta(days=1)
    last = end_dt.date() + timedelta(days=1)
    while d <= last:
        sunrise = local_sunrise(d, lat, lon, tz)
        next_sunrise = local_sunrise(d + timedelta(days=1), lat, lon, tz)
        if sunrise and next_sunrise:
            arunodaya = sunrise - timedelta(minutes=96)
            sunrise_state = panchang.state_at(sunrise + timedelta(seconds=1))
            next_state = panchang.state_at(next_sunrise + timedelta(seconds=1))
            if (
                arunodaya <= start_dt <= sunrise
                and sunrise < end_dt < next_sunrise
                and sunrise_state["tithi_id"] == rule["tithi_id"]
                and next_state["tithi_id"] == next_id
            ):
                return d
        d += timedelta(days=1)
    return None


def full_day_nakshatra(d: date, target: str, lat, lon, tz):
    sunrise = local_sunrise(d, lat, lon, tz)
    sunset = local_sunset(d, lat, lon, tz)
    if not sunrise or not sunset:
        return False
    start_state = panchang.state_at(sunrise + timedelta(seconds=1))
    end_state = panchang.state_at(sunset - timedelta(seconds=1))
    return (
        start_state["nakshatra"] == target
        and end_state["nakshatra"] == target
    )


def classify_window(rule: dict, start_dt: datetime, end_dt: datetime, lat, lon, tz):
    yogas = []
    evidence = {}
    ordinary_date = ordinary_dwadashi_date(start_dt, end_dt, lat, lon, tz)

    ekadashi_start = previous_ekadashi_start(rule, start_dt, tz)
    if ekadashi_start:
        eka_sunrises = sunrises_between(ekadashi_start, start_dt, lat, lon, tz)
        evidence["ekadashi_sunrises"] = [x.isoformat() for x in eka_sunrises]
        if len(eka_sunrises) >= 2:
            yogas.append("Unmilini Mahadwadashi")
            ordinary_date = eka_sunrises[-1].date()

    dwa_sunrises = sunrises_between(start_dt, end_dt, lat, lon, tz)
    evidence["dwadashi_sunrises"] = [x.isoformat() for x in dwa_sunrises]
    duration_hours = (end_dt - start_dt).total_seconds() / 3600.0
    evidence["dwadashi_duration_hours"] = round(duration_hours, 4)

    # GCAL Vyanjuli rule: Dwadashi must prevail at local sunrise on
    # two consecutive civil days. A merely long Dwadashi that covers one
    # sunrise-to-sunset interval is not sufficient and must not override a
    # Shuddha Ekadashi fast.
    vanjuli_date = None
    if len(dwa_sunrises) >= 2:
        first, second = dwa_sunrises[0], dwa_sunrises[1]
        if second.date() == first.date() + timedelta(days=1):
            vanjuli_date = first.date()
    evidence["vanjuli_two_sunrises"] = (
        [x.isoformat() for x in dwa_sunrises[:2]]
        if vanjuli_date is not None else []
    )
    if vanjuli_date is not None:
        yogas.append("Vanjuli Mahadwadashi")
        ordinary_date = vanjuli_date

    tri_date = trisparsha_date(rule, start_dt, end_dt, lat, lon, tz)
    if tri_date is not None:
        yogas.append("Trisparsha Mahadwadashi")
        ordinary_date = tri_date
        evidence["trisparsha"] = True

    final_start, final_end = final_tithi_window(rule, end_dt, tz)
    if final_start and final_end:
        final_sunrises = sunrises_between(final_start, final_end, lat, lon, tz)
        evidence["fortnight_end"] = {
            "name": rule["final_tithi"],
            "start": final_start.isoformat(),
            "end": final_end.isoformat(),
            "sunrises": [x.isoformat() for x in final_sunrises],
        }
        if len(final_sunrises) >= 2:
            yogas.append("Pakshavarddhini Mahadwadashi")

    sunrise = local_sunrise(ordinary_date, lat, lon, tz)
    sunset = local_sunset(ordinary_date, lat, lon, tz)
    if sunrise:
        evidence["observance_sunrise"] = sunrise.isoformat()
    if sunset:
        evidence["observance_sunset"] = sunset.isoformat()

    if sunrise and panchang.state_at(sunrise)["tithi_id"] == rule["tithi_id"]:
        for yoga_name, nakshatra, required_paksha in NAKSHATRA_YOGAS:
            if required_paksha and required_paksha != rule["paksha"]:
                continue
            if full_day_nakshatra(ordinary_date, nakshatra, lat, lon, tz):
                yogas.append(yoga_name)

    return ordinary_date, list(dict.fromkeys(yogas)), evidence


def events_for_rule(year: int, rule: dict, lat, lon, tz, hour24):
    cursor = panchang.astronomy_time(datetime(year - 1, 12, 1, tzinfo=tz))
    events = []

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
        obs_date, yogas, evidence = classify_window(
            rule, start_dt, end_dt, lat, lon, tz
        )

        if yogas and obs_date.year == year:
            state = panchang.state_at(
                local_sunrise(obs_date, lat, lon, tz) or start_dt
            )
            month = panchang.lunar_month_info(start_dt + (end_dt - start_dt) / 2, state)
            events.append({
                "date": obs_date.isoformat(),
                "weekday": obs_date.strftime("%A"),
                "paksha": rule["paksha"],
                "dwadashi_start": start_dt.isoformat(),
                "dwadashi_end": end_dt.isoformat(),
                "dwadashi_start_label": panchang.transition_label(start_dt, obs_date, hour24),
                "dwadashi_end_label": panchang.transition_label(end_dt, obs_date, hour24),
                "amanta_month": month.get("amanta"),
                "purnimanta_month": month.get("purnimanta"),
                "yogas": yogas,
                "evidence": evidence,
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
    for rule in DWADASHI_RULES:
        rows.extend(events_for_rule(selected.year, rule, lat, lon, tz, hour24))
    rows.sort(key=lambda row: (row["date"], row["dwadashi_start"]))

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
            "name": "tithika-mahadwadashi",
            "version": "0.2.0",
            "panchang_version": panchang.ENGINE_VERSION,
            "status": "integrated-classifier",
        },
        "events": rows,
        "note": (
            "Mahadwadashi yogas are classified from Tithi, local sunrise/sunset "
            "and Nakshatra evidence. The shared vrat_rules engine consumes these "
            "classifications for Vaishnava/ISKCON fasting-date override and Parana."
        ),
    }, ensure_ascii=False))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(json.dumps({
            "ok": False,
            "error": str(exc),
            "code": "MAHADWADASHI_CALCULATION_FAILED",
        }))
        sys.exit(1)