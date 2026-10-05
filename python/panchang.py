#!/usr/bin/env python3
"""
Tithika Daily Panchang astronomy engine.

Uses Swiss Ephemeris (pyswisseph) with Lahiri ayanamsha for sidereal
Sun/Moon positions. The engine calculates sunrise-state and transition
times for Tithi, Nakshatra, Yoga, Karana and Paksha.

Input: JSON on stdin
Output: JSON on stdout
"""
import sys
import json
import math
from datetime import datetime, date, timedelta, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

try:
    import swisseph as swe
except ImportError:
    print(json.dumps({
        "ok": False,
        "error": "pyswisseph is required for the Panchang engine",
        "code": "PANCHAANG_DEPENDENCY_MISSING"
    }))
    sys.exit(2)

TITHI_NAMES = [
    "Pratipada","Dwitiya","Tritiya","Chaturthi","Panchami","Shashthi","Saptami",
    "Ashtami","Navami","Dashami","Ekadashi","Dwadashi","Trayodashi","Chaturdashi","Purnima",
    "Pratipada","Dwitiya","Tritiya","Chaturthi","Panchami","Shashthi","Saptami",
    "Ashtami","Navami","Dashami","Ekadashi","Dwadashi","Trayodashi","Chaturdashi","Amavasya"
]
NAKSHATRA_NAMES = [
    "Ashwini","Bharani","Krittika","Rohini","Mrigashira","Ardra","Punarvasu","Pushya",
    "Ashlesha","Magha","Purva Phalguni","Uttara Phalguni","Hasta","Chitra","Swati",
    "Vishakha","Anuradha","Jyeshtha","Mula","Purva Ashadha","Uttara Ashadha","Shravana",
    "Dhanishtha","Shatabhisha","Purva Bhadrapada","Uttara Bhadrapada","Revati"
]
YOGA_NAMES = [
    "Vishkambha","Priti","Ayushman","Saubhagya","Shobhana","Atiganda","Sukarma","Dhriti",
    "Shula","Ganda","Vriddhi","Dhruva","Vyaghata","Harshana","Vajra","Siddhi","Vyatipata",
    "Variyana","Parigha","Shiva","Siddha","Sadhya","Shubha","Shukla","Brahma","Indra","Vaidhriti"
]
RASHI_NAMES = [
    "Mesha","Vrishabha","Mithuna","Karka","Simha","Kanya",
    "Tula","Vrishchika","Dhanu","Makara","Kumbha","Meena"
]
LUNAR_MONTH_BY_NEW_MOON_SUN_SIGN = [
    "Vaishakha","Jyeshtha","Ashadha","Shravana","Bhadrapada","Ashwina",
    "Kartika","Margashirsha","Pausha","Magha","Phalguna","Chaitra"
]
KARANA_CYCLE = ["Bava","Balava","Kaulava","Taitila","Garaja","Vanija","Vishti"]

def norm(v, m=360.0):
    return v % m

def solar_event(local_date: date, lat: float, lon: float, tz: ZoneInfo, sunrise: bool):
    n = local_date.timetuple().tm_yday
    lng_hour = lon / 15.0
    t = n + (((6 if sunrise else 18) - lng_hour) / 24.0)
    m = (0.9856 * t) - 3.289
    l = norm(m + (1.916 * math.sin(math.radians(m))) + (0.020 * math.sin(math.radians(2*m))) + 282.634)
    ra = math.degrees(math.atan(0.91764 * math.tan(math.radians(l))))
    ra = norm(ra)
    lq = math.floor(l / 90) * 90
    raq = math.floor(ra / 90) * 90
    ra = (ra + (lq - raq)) / 15.0
    sin_dec = 0.39782 * math.sin(math.radians(l))
    cos_dec = math.cos(math.asin(sin_dec))
    cos_h = (math.cos(math.radians(90.833)) - sin_dec * math.sin(math.radians(lat))) / (cos_dec * math.cos(math.radians(lat)))
    if not -1 <= cos_h <= 1:
        return None
    h = (360 - math.degrees(math.acos(cos_h))) if sunrise else math.degrees(math.acos(cos_h))
    h /= 15.0
    local_mean = h + ra - (0.06571 * t) - 6.622
    ut_hours = norm(local_mean - lng_hour, 24)
    hh = int(ut_hours)
    mmf = (ut_hours - hh) * 60
    mm = int(mmf)
    ss = int(round((mmf - mm) * 60))
    if ss == 60:
        ss = 0; mm += 1
    if mm == 60:
        mm = 0; hh = (hh + 1) % 24
    utc_dt = datetime(local_date.year, local_date.month, local_date.day, hh, mm, ss, tzinfo=timezone.utc)
    local_dt = utc_dt.astimezone(tz)
    while local_dt.date() < local_date:
        utc_dt += timedelta(days=1); local_dt = utc_dt.astimezone(tz)
    while local_dt.date() > local_date:
        utc_dt -= timedelta(days=1); local_dt = utc_dt.astimezone(tz)
    return local_dt

def julian_day(dt: datetime) -> float:
    u = dt.astimezone(timezone.utc)
    hour = u.hour + u.minute / 60.0 + (u.second + u.microsecond / 1_000_000) / 3600.0
    return swe.julday(u.year, u.month, u.day, hour, swe.GREG_CAL)

def sidereal_longitudes(dt: datetime):
    jd = julian_day(dt)
    flags = swe.FLG_MOSEPH | swe.FLG_SIDEREAL
    sun = swe.calc_ut(jd, swe.SUN, flags)[0][0] % 360.0
    moon = swe.calc_ut(jd, swe.MOON, flags)[0][0] % 360.0
    return sun, moon

def karana_index(half_tithi_index: int):
    i = half_tithi_index % 60
    if i == 0:
        return "Kimstughna"
    if 1 <= i <= 56:
        return KARANA_CYCLE[(i - 1) % 7]
    if i == 57:
        return "Shakuni"
    if i == 58:
        return "Chatushpada"
    return "Naga"

def state_at(dt: datetime):
    sun, moon = sidereal_longitudes(dt)
    elong = norm(moon - sun)
    tithi_index = int(elong // 12.0)
    nak_index = int(moon // (360.0 / 27.0))
    yoga_index = int(norm(sun + moon) // (360.0 / 27.0))
    half_tithi_index = int(elong // 6.0)
    paksha = "Shukla Paksha" if tithi_index < 15 else "Krishna Paksha"
    tithi_num = tithi_index + 1 if tithi_index < 15 else tithi_index - 14
    return {
        "sun_longitude": sun,
        "moon_longitude": moon,
        "elongation": elong,
        "tithi_id": tithi_index,
        "tithi_number": tithi_num,
        "tithi": TITHI_NAMES[tithi_index],
        "paksha": paksha,
        "nakshatra_id": nak_index,
        "nakshatra": NAKSHATRA_NAMES[nak_index],
        "yoga_id": yoga_index,
        "yoga": YOGA_NAMES[yoga_index],
        "karana_id": half_tithi_index,
        "karana": karana_index(half_tithi_index),
        "moon_rashi_id": int(moon // 30.0),
        "moon_rashi": RASHI_NAMES[int(moon // 30.0)],
        "sun_rashi_id": int(sun // 30.0),
        "sun_rashi": RASHI_NAMES[int(sun // 30.0)],
    }

def datetime_from_jd(jd_value: float, tz: ZoneInfo):
    y, m, d, hour = swe.revjul(jd_value, swe.GREG_CAL)
    utc_dt = datetime(y, m, d, tzinfo=timezone.utc) + timedelta(hours=hour)
    return utc_dt.astimezone(tz)

def moon_event(start: datetime, lat: float, lon: float, tz: ZoneInfo, rise: bool):
    mode = swe.CALC_RISE if rise else swe.CALC_SET
    result, times = swe.rise_trans(
        julian_day(start), swe.MOON, mode,
        (lon, lat, 0.0), 0.0, 15.0, swe.FLG_MOSEPH
    )
    if result != 0:
        return None
    return datetime_from_jd(times[0], tz)

def previous_new_moon(before: datetime):
    scan_start = before - timedelta(days=35)
    prev_dt = scan_start
    prev_id = state_at(prev_dt)["tithi_id"]
    probe = prev_dt + timedelta(hours=3)
    boundary = None
    while probe <= before:
        probe_id = state_at(probe)["tithi_id"]
        if prev_id == 29 and probe_id == 0:
            lo, hi = prev_dt, probe
            for _ in range(32):
                mid = lo + (hi - lo) / 2
                if state_at(mid)["tithi_id"] == 29:
                    lo = mid
                else:
                    hi = mid
            boundary = hi
        prev_dt, prev_id = probe, probe_id
        probe += timedelta(hours=3)
    return boundary

def lunar_months(at_sunrise: datetime, paksha: str):
    new_moon = previous_new_moon(at_sunrise)
    if not new_moon:
        return {"amanta": None, "purnimanta": None, "new_moon": None}
    sun, _ = sidereal_longitudes(new_moon + timedelta(minutes=2))
    sign = int(sun // 30.0)
    amanta = LUNAR_MONTH_BY_NEW_MOON_SUN_SIGN[sign]
    month_index = LUNAR_MONTH_BY_NEW_MOON_SUN_SIGN.index(amanta)
    purnimanta = LUNAR_MONTH_BY_NEW_MOON_SUN_SIGN[(month_index + 1) % 12] if paksha == "Krishna Paksha" else amanta
    return {
        "amanta": amanta,
        "purnimanta": purnimanta,
        "new_moon": new_moon.isoformat(),
        "basis_sun_rashi": RASHI_NAMES[sign]
    }

def fmt(dt: datetime, hour24=False):
    rounded = (dt + timedelta(seconds=30)).replace(second=0, microsecond=0)
    return rounded.strftime("%H:%M" if hour24 else "%I:%M %p").lstrip("0")

def transition_label(dt: datetime, anchor_date: date, hour24=False):
    base = fmt(dt, hour24)
    if dt.date() != anchor_date:
        return f"{base}, {dt.strftime('%b %d').replace(' 0',' ')}"
    return base

def find_transition(start: datetime, end: datetime, key: str, start_id, step_minutes=12):
    """Find first state boundary after start using scan + binary search."""
    left = start
    probe = start + timedelta(minutes=step_minutes)
    while probe <= end:
        probe_id = state_at(probe)[key]
        if probe_id != start_id:
            lo, hi = left, probe
            for _ in range(28):
                mid = lo + (hi - lo) / 2
                if state_at(mid)[key] == start_id:
                    lo = mid
                else:
                    hi = mid
            return hi
        left = probe
        probe += timedelta(minutes=step_minutes)
    return None

def sequence_for(start: datetime, end: datetime, key: str, name_key: str, hour24=False, max_items=4):
    out = []
    cursor = start
    for _ in range(max_items):
        st = state_at(cursor)
        item = {
            "id": st[key],
            "name": st[name_key],
            "start": cursor.isoformat(),
            "start_label": transition_label(cursor, start.date(), hour24),
        }
        transition = find_transition(cursor, end, key, st[key])
        if transition is None:
            item["end"] = end.isoformat()
            item["end_label"] = transition_label(end, start.date(), hour24)
            item["continues"] = True
            out.append(item)
            break
        item["end"] = transition.isoformat()
        item["end_label"] = transition_label(transition, start.date(), hour24)
        item["continues"] = False
        out.append(item)
        cursor = transition + timedelta(seconds=2)
        if cursor >= end:
            break
    return out

def main():
    payload = json.loads(sys.stdin.read() or "{}")
    lat = float(payload.get("lat", 19.0760))
    lon = float(payload.get("lon", 72.8777))
    if not (-90 <= lat <= 90 and -180 <= lon <= 180):
        raise ValueError("Invalid latitude/longitude")

    date_s = payload.get("date") or datetime.now().strftime("%Y-%m-%d")
    d = datetime.strptime(date_s, "%Y-%m-%d").date()
    tz_name = payload.get("timezone") or "Asia/Kolkata"
    try:
        tz = ZoneInfo(tz_name)
    except ZoneInfoNotFoundError:
        tz_name = "Asia/Kolkata"; tz = ZoneInfo(tz_name)
    city = (payload.get("city") or "Current location").strip()[:120]
    hour24 = bool(payload.get("hour24", False))

    swe.set_sid_mode(swe.SIDM_LAHIRI, 0.0, 0.0)

    sunrise = solar_event(d, lat, lon, tz, True)
    next_sunrise = solar_event(d + timedelta(days=1), lat, lon, tz, True)
    sunset = solar_event(d, lat, lon, tz, False)
    if not sunrise or not sunset or not next_sunrise:
        raise ValueError("Solar events unavailable for this latitude/date")
    if sunset <= sunrise:
        sunset += timedelta(days=1)
    if next_sunrise <= sunrise:
        next_sunrise += timedelta(days=1)

    sunrise_state = state_at(sunrise)
    months = lunar_months(sunrise, sunrise_state["paksha"])
    moonrise = moon_event(sunrise, lat, lon, tz, True)
    moonset = moon_event(sunrise, lat, lon, tz, False)
    if moonrise and moonrise > next_sunrise:
        moonrise = None
    if moonset and moonset > next_sunrise:
        moonset = None

    now_local = datetime.now(tz)
    reference = now_local if d == now_local.date() else sunrise
    current_state = state_at(reference)

    tithis = sequence_for(sunrise, next_sunrise, "tithi_id", "tithi", hour24, 3)
    nakshatras = sequence_for(sunrise, next_sunrise, "nakshatra_id", "nakshatra", hour24, 3)
    yogas = sequence_for(sunrise, next_sunrise, "yoga_id", "yoga", hour24, 3)
    karanas = sequence_for(sunrise, next_sunrise, "karana_id", "karana", hour24, 5)

    output = {
        "ok": True,
        "engine": {
            "name": "tithika-panchang",
            "version": "0.2.0",
            "ephemeris": "Swiss Ephemeris / Moshier",
            "ayanamsha": "Lahiri",
            "sidereal": True
        },
        "location": {"city": city, "lat": lat, "lon": lon, "timezone": tz_name},
        "date": d.isoformat(),
        "weekday": d.strftime("%A"),
        "date_label": d.strftime("%B %d, %Y").replace(" 0", " "),
        "sunrise": sunrise.isoformat(),
        "sunrise_label": fmt(sunrise, hour24),
        "sunset": sunset.isoformat(),
        "sunset_label": fmt(sunset, hour24),
        "next_sunrise": next_sunrise.isoformat(),
        "next_sunrise_label": transition_label(next_sunrise, d, hour24),
        "sunrise_state": sunrise_state,
        "current_state": current_state,
        "tithi": tithis,
        "nakshatra": nakshatras,
        "yoga": yogas,
        "karana": karanas,
        "paksha": sunrise_state["paksha"],
        "lunar_month": months,
        "moon_rashi": sunrise_state["moon_rashi"],
        "sun_rashi": sunrise_state["sun_rashi"],
        "moonrise": moonrise.isoformat() if moonrise else None,
        "moonrise_label": transition_label(moonrise, d, hour24) if moonrise else None,
        "moonset": moonset.isoformat() if moonset else None,
        "moonset_label": transition_label(moonset, d, hour24) if moonset else None,
        "generated_at": now_local.isoformat(),
        "method": "Sidereal Sun/Moon positions from Swiss Ephemeris with Lahiri ayanamsha; Hindu day evaluated sunrise to next sunrise."
    }
    print(json.dumps(output, ensure_ascii=False))

if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(json.dumps({"ok": False, "error": str(exc)}))
        sys.exit(1)
