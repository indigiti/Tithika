#!/usr/bin/env python3
"""
Tithika Daily Panchang astronomy engine.

Calculation contract
--------------------
- Apparent geocentric true-ecliptic Sun/Moon positions: Astronomy Engine.
- Sidereal conversion: Lahiri / Chitrapaksha ayanamsha.
- Ayanamsha accrual: J2000 anchor + IAU 2006 general precession.
- True ayanamsha includes IAU 2000B nutation in longitude.
- Hindu day: local sunrise -> next local sunrise.
- Tithi/Nakshatra/Yoga/Karana boundaries: scan + binary refinement.

Input: JSON on stdin.
Output: JSON on stdout.

Astronomy Engine is vendored under python/vendor/astronomy.py and is MIT licensed.
"""
from __future__ import annotations

import json
import math
import os
import sys
from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

VENDOR_DIR = os.path.join(os.path.dirname(__file__), "vendor")
if VENDOR_DIR not in sys.path:
    sys.path.insert(0, VENDOR_DIR)

try:
    import astronomy
except ImportError:
    print(json.dumps({
        "ok": False,
        "error": "Vendored Astronomy Engine is unavailable",
        "code": "PANCHANG_DEPENDENCY_MISSING"
    }))
    sys.exit(2)

ENGINE_VERSION = "0.2.0"
ASTRONOMY_ENGINE_BLOB = "1a48fdf620540df22fcf421d0df0c2c016999e52"

TITHI_NAMES = [
    "Pratipada", "Dwitiya", "Tritiya", "Chaturthi", "Panchami", "Shashthi", "Saptami",
    "Ashtami", "Navami", "Dashami", "Ekadashi", "Dwadashi", "Trayodashi", "Chaturdashi", "Purnima",
    "Pratipada", "Dwitiya", "Tritiya", "Chaturthi", "Panchami", "Shashthi", "Saptami",
    "Ashtami", "Navami", "Dashami", "Ekadashi", "Dwadashi", "Trayodashi", "Chaturdashi", "Amavasya",
]

NAKSHATRA_NAMES = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra", "Punarvasu", "Pushya",
    "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni", "Hasta", "Chitra", "Swati",
    "Vishakha", "Anuradha", "Jyeshtha", "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana",
    "Dhanishtha", "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada", "Revati",
]

YOGA_NAMES = [
    "Vishkambha", "Priti", "Ayushman", "Saubhagya", "Shobhana", "Atiganda", "Sukarma", "Dhriti",
    "Shula", "Ganda", "Vriddhi", "Dhruva", "Vyaghata", "Harshana", "Vajra", "Siddhi", "Vyatipata",
    "Variyana", "Parigha", "Shiva", "Siddha", "Sadhya", "Shubha", "Shukla", "Brahma", "Indra", "Vaidhriti",
]

RASHI_NAMES = [
    "Mesha", "Vrishabha", "Mithuna", "Karka", "Simha", "Kanya",
    "Tula", "Vrishchika", "Dhanu", "Makara", "Kumbha", "Meena",
]

LUNAR_MONTH_NAMES = [
    "Chaitra", "Vaishakha", "Jyeshtha", "Ashadha", "Shravana", "Bhadrapada",
    "Ashwina", "Kartika", "Margashirsha", "Pausha", "Magha", "Phalguna",
]

KARANA_CYCLE = ["Bava", "Balava", "Kaulava", "Taitila", "Garaja", "Vanija", "Vishti"]

# Lahiri mean ayanamsha at J2000 (23°51'25.53") in arcseconds.
LAHIRI_J2000_ARCSEC = 85885.53


def norm(value: float, modulus: float = 360.0) -> float:
    return value % modulus


def astronomy_time(dt: datetime) -> astronomy.Time:
    utc = dt.astimezone(timezone.utc)
    sec = utc.second + utc.microsecond / 1_000_000.0
    return astronomy.Time.Make(utc.year, utc.month, utc.day, utc.hour, utc.minute, sec)


def datetime_from_astronomy(t: astronomy.Time, tz: ZoneInfo) -> datetime:
    y, m, d, hh, mm, ss = t.Calendar()
    whole = int(math.floor(ss))
    micro = int(round((ss - whole) * 1_000_000))
    if micro >= 1_000_000:
        whole += 1
        micro -= 1_000_000
    utc = datetime(y, m, d, hh, mm, whole, micro, tzinfo=timezone.utc)
    return utc.astimezone(tz)


def nutation_longitude_arcsec(t: astronomy.Time) -> float:
    """IAU 2000B 5-term nutation in longitude, matching Astronomy Engine's ECT frame."""
    tc = t.tt / 36525.0
    arcsec360 = 360.0 * 60.0 * 60.0
    asec2rad = math.radians(1.0 / 3600.0)

    elp = math.fmod(1287104.79305 + tc * 129596581.0481, arcsec360) * asec2rad
    f = math.fmod(335779.526232 + tc * 1739527262.8478, arcsec360) * asec2rad
    d = math.fmod(1072260.70369 + tc * 1602961601.2090, arcsec360) * asec2rad
    om = math.fmod(450160.398036 - tc * 6962890.5431, arcsec360) * asec2rad

    sarg = math.sin(om)
    carg = math.cos(om)
    dp = (-172064161.0 - 174666.0 * tc) * sarg + 33386.0 * carg

    arg = 2.0 * (f - d + om)
    sarg, carg = math.sin(arg), math.cos(arg)
    dp += (-13170906.0 - 1675.0 * tc) * sarg - 13696.0 * carg

    arg = 2.0 * (f + om)
    sarg, carg = math.sin(arg), math.cos(arg)
    dp += (-2276413.0 - 234.0 * tc) * sarg + 2796.0 * carg

    arg = 2.0 * om
    sarg, carg = math.sin(arg), math.cos(arg)
    dp += (2074554.0 + 207.0 * tc) * sarg - 698.0 * carg

    sarg, carg = math.sin(elp), math.cos(elp)
    dp += (1475877.0 - 3633.0 * tc) * sarg + 11817.0 * carg

    return -0.000135 + dp * 1.0e-7


def lahiri_ayanamsha_deg(t: astronomy.Time, true_frame: bool = True) -> float:
    """Lahiri/Chitrapaksha ayanamsha using an IAU 2006 general-precession polynomial."""
    tc = t.tt / 36525.0
    arcsec = (
        LAHIRI_J2000_ARCSEC
        + 5028.796195 * tc
        + 1.1054348 * tc * tc
        + 0.00007964 * tc ** 3
        - 0.000023857 * tc ** 4
        - 0.0000000383 * tc ** 5
    )
    if true_frame:
        arcsec += nutation_longitude_arcsec(t)
    return arcsec / 3600.0


def tropical_longitudes(dt: datetime) -> tuple[float, float, astronomy.Time]:
    t = astronomy_time(dt)
    sun = norm(astronomy.SunPosition(t).elon)
    moon = norm(astronomy.EclipticGeoMoon(t).lon)
    return sun, moon, t


def sidereal_longitudes(dt: datetime) -> tuple[float, float, float]:
    sun_tropical, moon_tropical, t = tropical_longitudes(dt)
    ayanamsha = lahiri_ayanamsha_deg(t, True)
    return norm(sun_tropical - ayanamsha), norm(moon_tropical - ayanamsha), ayanamsha


def karana_name(half_tithi_index: int) -> str:
    index = half_tithi_index % 60
    if index == 0:
        return "Kimstughna"
    if 1 <= index <= 56:
        return KARANA_CYCLE[(index - 1) % 7]
    if index == 57:
        return "Shakuni"
    if index == 58:
        return "Chatushpada"
    return "Naga"


def state_at(dt: datetime) -> dict:
    sun, moon, ayanamsha = sidereal_longitudes(dt)
    elongation = norm(moon - sun)

    tithi_id = int(elongation // 12.0)
    nak_span = 360.0 / 27.0
    nak_id = int(moon // nak_span)
    nak_offset = moon - nak_id * nak_span
    nak_pada = min(4, int(nak_offset // (nak_span / 4.0)) + 1)
    yoga_id = int(norm(sun + moon) // nak_span)
    karana_id = int(elongation // 6.0)

    sun_rashi_id = int(sun // 30.0)
    moon_rashi_id = int(moon // 30.0)
    sun_nak_id = int(sun // nak_span)

    paksha = "Shukla Paksha" if tithi_id < 15 else "Krishna Paksha"
    paksha_tithi_number = tithi_id + 1 if tithi_id < 15 else tithi_id - 14

    return {
        "sun_longitude": round(sun, 8),
        "moon_longitude": round(moon, 8),
        "ayanamsha": round(ayanamsha, 8),
        "elongation": round(elongation, 8),
        "tithi_id": tithi_id,
        "tithi_number": paksha_tithi_number,
        "tithi": TITHI_NAMES[tithi_id],
        "paksha": paksha,
        "nakshatra_id": nak_id,
        "nakshatra": NAKSHATRA_NAMES[nak_id],
        "nakshatra_pada": nak_pada,
        "yoga_id": yoga_id,
        "yoga": YOGA_NAMES[yoga_id],
        "karana_id": karana_id,
        "karana": karana_name(karana_id),
        "moon_rashi_id": moon_rashi_id,
        "moon_rashi": RASHI_NAMES[moon_rashi_id],
        "sun_rashi_id": sun_rashi_id,
        "sun_rashi": RASHI_NAMES[sun_rashi_id],
        "sun_nakshatra_id": sun_nak_id,
        "sun_nakshatra": NAKSHATRA_NAMES[sun_nak_id],
    }


def local_midnight(d: date, tz: ZoneInfo) -> datetime:
    return datetime(d.year, d.month, d.day, 0, 0, 0, tzinfo=tz)


def rise_set(
    d: date,
    lat: float,
    lon: float,
    tz: ZoneInfo,
    body: astronomy.Body,
    direction: astronomy.Direction,
) -> datetime | None:
    observer = astronomy.Observer(lat, lon, 0.0)
    start = astronomy_time(local_midnight(d, tz))
    found = astronomy.SearchRiseSet(body, observer, direction, start, 1.5)
    if found is None:
        return None
    local = datetime_from_astronomy(found, tz)
    # A 1.5-day search can technically reach the next local date; constrain to the requested date.
    if local.date() != d:
        return None
    return local


def fmt(dt: datetime | None, hour24: bool = False) -> str | None:
    if dt is None:
        return None
    rounded = (dt + timedelta(seconds=30)).replace(second=0, microsecond=0)
    return rounded.strftime("%H:%M" if hour24 else "%I:%M %p").lstrip("0")


def transition_label(dt: datetime, anchor_date: date, hour24: bool = False) -> str:
    label = fmt(dt, hour24) or ""
    if dt.date() != anchor_date:
        return f"{label}, {dt.strftime('%b %d').replace(' 0', ' ')}"
    return label


def find_transition(
    start: datetime,
    end: datetime,
    key: str,
    start_id: int,
    step_minutes: int = 30,
) -> datetime | None:
    """Find the first discrete Panchang-state boundary after start."""
    left = start
    probe = start + timedelta(minutes=step_minutes)

    while probe <= end:
        if state_at(probe)[key] != start_id:
            lo, hi = left, probe
            # Refine to well below one second. The final display is rounded to minutes.
            for _ in range(34):
                mid = lo + (hi - lo) / 2
                if state_at(mid)[key] == start_id:
                    lo = mid
                else:
                    hi = mid
            return hi
        left = probe
        probe += timedelta(minutes=step_minutes)
    return None


def sequence_for(
    start: datetime,
    end: datetime,
    key: str,
    name_key: str,
    hour24: bool = False,
    max_items: int = 5,
    enrich=None,
) -> list[dict]:
    output = []
    cursor = start

    for _ in range(max_items):
        state = state_at(cursor)
        item = {
            "id": state[key],
            "name": state[name_key],
            "start": cursor.isoformat(),
            "start_label": transition_label(cursor, start.date(), hour24),
        }
        if enrich:
            item.update(enrich(state))

        transition = find_transition(cursor, end, key, state[key])
        if transition is None:
            item.update({
                "end": end.isoformat(),
                "end_label": transition_label(end, start.date(), hour24),
                "continues": True,
            })
            output.append(item)
            break

        item.update({
            "end": transition.isoformat(),
            "end_label": transition_label(transition, start.date(), hour24),
            "continues": False,
        })
        output.append(item)
        cursor = transition + timedelta(seconds=1)
        if cursor >= end:
            break

    return output


def lunar_month_info(reference: datetime, sunrise_state: dict) -> dict:
    """Compute basic Amanta/Purnimanta month names and detect Adhika month."""
    t = astronomy_time(reference)
    prev_new = astronomy.SearchMoonPhase(0.0, t, -35.0)
    next_new = astronomy.SearchMoonPhase(0.0, t, +35.0)
    if prev_new is None or next_new is None:
        return {"amanta": None, "purnimanta": None, "adhika": False}

    prev_dt = datetime_from_astronomy(prev_new, reference.tzinfo)
    next_dt = datetime_from_astronomy(next_new, reference.tzinfo)
    prev_sun_sid, _, _ = sidereal_longitudes(prev_dt)
    next_sun_sid, _, _ = sidereal_longitudes(next_dt)

    prev_sign = int(prev_sun_sid // 30.0)
    next_sign = int(next_sun_sid // 30.0)
    amanta_index = (prev_sign + 1) % 12
    adhika = prev_sign == next_sign

    # In Purnimanta tradition, the month changes at full moon.
    purnimanta_index = amanta_index
    if sunrise_state["paksha"] == "Krishna Paksha":
        purnimanta_index = (amanta_index + 1) % 12

    amanta = LUNAR_MONTH_NAMES[amanta_index]
    purnimanta = LUNAR_MONTH_NAMES[purnimanta_index]
    if adhika:
        amanta = f"Adhika {amanta}"

    return {
        "amanta": amanta,
        "purnimanta": purnimanta,
        "adhika": adhika,
        "previous_new_moon": prev_dt.isoformat(),
        "next_new_moon": next_dt.isoformat(),
    }


def main() -> None:
    payload = json.loads(sys.stdin.read() or "{}")
    lat = float(payload.get("lat", 19.0760))
    lon = float(payload.get("lon", 72.8777))
    if not (-90 <= lat <= 90 and -180 <= lon <= 180):
        raise ValueError("Invalid latitude/longitude")

    date_text = payload.get("date") or datetime.now().strftime("%Y-%m-%d")
    selected_date = datetime.strptime(date_text, "%Y-%m-%d").date()

    timezone_name = payload.get("timezone") or "Asia/Kolkata"
    try:
        tz = ZoneInfo(timezone_name)
    except ZoneInfoNotFoundError:
        timezone_name = "Asia/Kolkata"
        tz = ZoneInfo(timezone_name)

    city = (payload.get("city") or "Current location").strip()[:120]
    hour24 = bool(payload.get("hour24", False))

    sunrise = rise_set(selected_date, lat, lon, tz, astronomy.Body.Sun, astronomy.Direction.Rise)
    sunset = rise_set(selected_date, lat, lon, tz, astronomy.Body.Sun, astronomy.Direction.Set)
    next_sunrise = rise_set(selected_date + timedelta(days=1), lat, lon, tz, astronomy.Body.Sun, astronomy.Direction.Rise)
    moonrise = rise_set(selected_date, lat, lon, tz, astronomy.Body.Moon, astronomy.Direction.Rise)
    moonset = rise_set(selected_date, lat, lon, tz, astronomy.Body.Moon, astronomy.Direction.Set)

    if sunrise is None or sunset is None or next_sunrise is None:
        raise ValueError("Sunrise/sunset unavailable for this latitude/date")

    if sunset <= sunrise:
        sunset += timedelta(days=1)
    if next_sunrise <= sunrise:
        next_sunrise += timedelta(days=1)

    sunrise_state = state_at(sunrise)
    now_local = datetime.now(tz)
    current_reference = now_local if selected_date == now_local.date() else sunrise
    current_state = state_at(current_reference)

    tithis = sequence_for(
        sunrise, next_sunrise, "tithi_id", "tithi", hour24, 4,
        enrich=lambda s: {"paksha": s["paksha"], "number": s["tithi_number"]},
    )
    nakshatras = sequence_for(
        sunrise, next_sunrise, "nakshatra_id", "nakshatra", hour24, 4,
        enrich=lambda s: {"pada": s["nakshatra_pada"]},
    )
    yogas = sequence_for(sunrise, next_sunrise, "yoga_id", "yoga", hour24, 4)
    karanas = sequence_for(sunrise, next_sunrise, "karana_id", "karana", hour24, 6)
    lunar_month = lunar_month_info(sunrise, sunrise_state)

    output = {
        "ok": True,
        "engine": {
            "name": "tithika-panchang",
            "version": ENGINE_VERSION,
            "astronomy": "Astronomy Engine (MIT, vendored)",
            "astronomy_blob": ASTRONOMY_ENGINE_BLOB,
            "coordinates": "apparent geocentric true ecliptic of date",
            "ayanamsha": "Lahiri / Chitrapaksha",
            "ayanamsha_model": "J2000 anchor + IAU 2006 precession + IAU 2000B nutation",
            "sidereal": True,
        },
        "location": {
            "city": city,
            "lat": lat,
            "lon": lon,
            "timezone": timezone_name,
        },
        "date": selected_date.isoformat(),
        "weekday": selected_date.strftime("%A"),
        "date_label": selected_date.strftime("%B %d, %Y").replace(" 0", " "),
        "sunrise": sunrise.isoformat(),
        "sunrise_label": fmt(sunrise, hour24),
        "sunset": sunset.isoformat(),
        "sunset_label": fmt(sunset, hour24),
        "next_sunrise": next_sunrise.isoformat(),
        "next_sunrise_label": transition_label(next_sunrise, selected_date, hour24),
        "moonrise": moonrise.isoformat() if moonrise else None,
        "moonrise_label": fmt(moonrise, hour24),
        "moonset": moonset.isoformat() if moonset else None,
        "moonset_label": fmt(moonset, hour24),
        "sunrise_state": sunrise_state,
        "current_state": current_state,
        "tithi": tithis,
        "nakshatra": nakshatras,
        "yoga": yogas,
        "karana": karanas,
        "paksha": sunrise_state["paksha"],
        "moon_rashi": sunrise_state["moon_rashi"],
        "sun_rashi": sunrise_state["sun_rashi"],
        "sun_nakshatra": sunrise_state["sun_nakshatra"],
        "lunar_month": lunar_month,
        "generated_at": now_local.isoformat(),
        "method": (
            "Astronomy Engine apparent Sun/Moon true-ecliptic positions converted to "
            "Lahiri sidereal longitude; Panchang states evaluated from local sunrise "
            "to the next sunrise and transition times refined by binary search."
        ),
    }
    print(json.dumps(output, ensure_ascii=False))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(json.dumps({
            "ok": False,
            "error": str(exc),
            "code": "PANCHANG_CALCULATION_FAILED",
        }))
        sys.exit(1)
