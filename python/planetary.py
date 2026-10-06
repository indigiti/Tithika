#!/usr/bin/env python3
"""
Tithika planetary ephemeris foundation.

Provides:
- Lahiri/Chitrapaksha sidereal geocentric planetary positions.
- Rashi, Nakshatra and Pada classification.
- Apparent daily longitude speed and retrograde state.
- Classical angular-separation combustion status.
- Yearly Rashi ingress events.
- Retrograde/direct station events.
- Mean Rahu/Ketu nodes.

Astronomy comes from the vendored MIT Astronomy Engine. Planet vectors are
apparent geocentric J2000 vectors rotated to the true ecliptic of date, then
converted to Nirayana longitude with Tithika's shared Lahiri model.
"""
from __future__ import annotations

import json
import math
import sys
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import panchang

ENGINE_VERSION = "0.1.0"
NAK_SPAN = 360.0 / 27.0

PLANETS = {
    "Sun": panchang.astronomy.Body.Sun,
    "Moon": panchang.astronomy.Body.Moon,
    "Mercury": panchang.astronomy.Body.Mercury,
    "Venus": panchang.astronomy.Body.Venus,
    "Mars": panchang.astronomy.Body.Mars,
    "Jupiter": panchang.astronomy.Body.Jupiter,
    "Saturn": panchang.astronomy.Body.Saturn,
    "Uranus": panchang.astronomy.Body.Uranus,
    "Neptune": panchang.astronomy.Body.Neptune,
    "Pluto": panchang.astronomy.Body.Pluto,
}

CLASSICAL_ORDER = [
    "Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"
]
TRANSIT_ORDER = [
    "Sun", "Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Rahu", "Ketu"
]
RETROGRADE_ORDER = ["Mercury", "Venus", "Mars", "Jupiter", "Saturn"]

# Classical Surya-Siddhanta-style angular limits. Mercury/Venus use narrower
# limits while retrograde. These are exposed as the rule profile in output;
# they are not presented as a location-specific optical visibility model.
COMBUSTION_LIMITS = {
    "Moon": (12.0, 12.0),
    "Mars": (17.0, 17.0),
    "Mercury": (14.0, 12.0),
    "Jupiter": (11.0, 11.0),
    "Venus": (10.0, 8.0),
    "Saturn": (15.0, 15.0),
}


def signed_delta(new: float, old: float) -> float:
    return ((new - old + 180.0) % 360.0) - 180.0


def mean_node_tropical(t: panchang.astronomy.Time) -> float:
    """Mean ascending lunar node, tropical true-ecliptic longitude of date."""
    tc = t.tt / 36525.0
    omega = (
        125.04455501
        - 1934.1361849 * tc
        + 0.0020762 * tc * tc
        + (tc ** 3) / 467410.0
        - (tc ** 4) / 60616000.0
    )
    return panchang.norm(omega)


def tropical_coordinates(name: str, moment: datetime) -> tuple[float, float, float]:
    t = panchang.astronomy_time(moment)
    if name == "Sun":
        sun = panchang.astronomy.SunPosition(t)
        return panchang.norm(sun.elon), float(sun.elat), float(sun.dist)
    if name == "Moon":
        moon = panchang.astronomy.EclipticGeoMoon(t)
        return panchang.norm(moon.lon), float(moon.lat), float(moon.dist)
    if name in ("Rahu", "Ketu"):
        lon = mean_node_tropical(t)
        if name == "Ketu":
            lon = panchang.norm(lon + 180.0)
        return lon, 0.0, 1.0

    body = PLANETS[name]
    vec = panchang.astronomy.GeoVector(body, t, True)
    ecl = panchang.astronomy.Ecliptic(vec)
    return panchang.norm(ecl.elon), float(ecl.elat), float(ecl.ecdist)


def sidereal_coordinates(name: str, moment: datetime) -> tuple[float, float, float, float]:
    t = panchang.astronomy_time(moment)
    lon, lat, dist = tropical_coordinates(name, moment)
    aya = panchang.lahiri_ayanamsha_deg(t, True)
    return panchang.norm(lon - aya), lat, dist, aya


def longitude_speed(name: str, moment: datetime, hours: float = 6.0) -> float:
    if name in ("Rahu", "Ketu"):
        # Mean nodes are always retrograde; numerical evaluation keeps the
        # same frame/ayanamsha treatment as other bodies.
        pass
    before = moment - timedelta(hours=hours)
    after = moment + timedelta(hours=hours)
    a = sidereal_coordinates(name, before)[0]
    b = sidereal_coordinates(name, after)[0]
    return signed_delta(b, a) / ((2.0 * hours) / 24.0)


def classify_longitude(longitude: float) -> dict:
    rashi_id = int(longitude // 30.0) % 12
    degree = longitude - rashi_id * 30.0
    nak_id = int(longitude // NAK_SPAN) % 27
    nak_offset = longitude - nak_id * NAK_SPAN
    pada = min(4, int(nak_offset // (NAK_SPAN / 4.0)) + 1)
    return {
        "rashi_id": rashi_id,
        "rashi": panchang.RASHI_NAMES[rashi_id],
        "degree_in_rashi": round(degree, 8),
        "nakshatra_id": nak_id,
        "nakshatra": panchang.NAKSHATRA_NAMES[nak_id],
        "pada": pada,
    }


def planet_state(name: str, moment: datetime) -> dict:
    lon, lat, dist, aya = sidereal_coordinates(name, moment)
    speed = longitude_speed(name, moment)
    retrograde = speed < -0.0005
    classification = classify_longitude(lon)

    state = {
        "name": name,
        "longitude": round(lon, 8),
        "latitude": round(lat, 8),
        "distance_au": round(dist, 10),
        "ayanamsha": round(aya, 8),
        "speed_deg_day": round(speed, 8),
        "retrograde": retrograde,
        "motion": "retrograde" if retrograde else "direct",
        **classification,
    }

    if name in COMBUSTION_LIMITS:
        sun_lon = sidereal_coordinates("Sun", moment)[0]
        sep = abs(signed_delta(lon, sun_lon))
        direct_limit, retro_limit = COMBUSTION_LIMITS[name]
        limit = retro_limit if retrograde else direct_limit
        state.update({
            "sun_separation_deg": round(sep, 8),
            "combustion_limit_deg": limit,
            "combust": sep <= limit,
            "combustion_profile": "classical-angular-separation",
        })
    elif name in ("Rahu", "Ketu"):
        state.update({
            "motion": "mean-node-retrograde",
            "retrograde": True,
            "node_model": "mean",
            "combust": False,
        })
    else:
        state["combust"] = False

    return state


def positions(moment: datetime, modern: bool = False) -> list[dict]:
    names = list(CLASSICAL_ORDER)
    if modern:
        names.extend(["Uranus", "Neptune", "Pluto"])
    return [planet_state(name, moment) for name in names]


def refine_sign_change(
    name: str, left: datetime, right: datetime, old_sign: int
) -> datetime:
    lo, hi = left, right
    for _ in range(45):
        mid = lo + (hi - lo) / 2
        sign = classify_longitude(sidereal_coordinates(name, mid)[0])["rashi_id"]
        if sign == old_sign:
            lo = mid
        else:
            hi = mid
    return hi


def transit_events(year: int, tz: ZoneInfo) -> list[dict]:
    rows = []
    year_start = datetime(year, 1, 1, 0, 0, tzinfo=tz)
    year_end = datetime(year + 1, 1, 1, 0, 0, tzinfo=tz)

    for name in TRANSIT_ORDER:
        step = timedelta(hours=6 if name in ("Sun", "Mercury", "Venus", "Mars") else 12)
        if name in ("Rahu", "Ketu"):
            step = timedelta(days=1)

        cursor = year_start - step
        old_lon = sidereal_coordinates(name, cursor)[0]
        old_sign = classify_longitude(old_lon)["rashi_id"]
        probe = cursor + step

        while probe <= year_end + step:
            lon = sidereal_coordinates(name, probe)[0]
            sign = classify_longitude(lon)["rashi_id"]
            if sign != old_sign:
                event = refine_sign_change(name, probe - step, probe, old_sign)
                if year_start <= event < year_end:
                    before = planet_state(name, event - timedelta(seconds=5))
                    after = planet_state(name, event + timedelta(seconds=5))
                    rows.append({
                        "planet": name,
                        "datetime": event.isoformat(),
                        "date": event.date().isoformat(),
                        "from_rashi": before["rashi"],
                        "to_rashi": after["rashi"],
                        "direction": "retrograde" if after["speed_deg_day"] < 0 else "direct",
                        "longitude": after["longitude"],
                    })
                old_sign = sign
            else:
                old_sign = sign
            probe += step

    rows.sort(key=lambda row: row["datetime"])
    return rows


def speed_value(name: str, moment: datetime) -> float:
    return longitude_speed(name, moment, 3.0)


def refine_station(name: str, left: datetime, right: datetime, left_negative: bool) -> datetime:
    lo, hi = left, right
    for _ in range(45):
        mid = lo + (hi - lo) / 2
        neg = speed_value(name, mid) < 0.0
        if neg == left_negative:
            lo = mid
        else:
            hi = mid
    return hi


def retrograde_events(year: int, tz: ZoneInfo) -> list[dict]:
    rows = []
    start = datetime(year, 1, 1, 0, 0, tzinfo=tz)
    end = datetime(year + 1, 1, 1, 0, 0, tzinfo=tz)
    scan_start = start - timedelta(days=3)
    scan_end = end + timedelta(days=3)

    for name in RETROGRADE_ORDER:
        step = timedelta(hours=6)
        left = scan_start
        left_speed = speed_value(name, left)
        probe = left + step

        while probe <= scan_end:
            speed = speed_value(name, probe)
            if (left_speed < 0.0) != (speed < 0.0):
                event = refine_station(name, probe - step, probe, left_speed < 0.0)
                if start <= event < end:
                    state = planet_state(name, event)
                    rows.append({
                        "planet": name,
                        "datetime": event.isoformat(),
                        "date": event.date().isoformat(),
                        "event": "retrograde" if speed < 0.0 else "direct",
                        "rashi": state["rashi"],
                        "longitude": state["longitude"],
                    })
            left_speed = speed
            probe += step

    rows.sort(key=lambda row: row["datetime"])
    return rows


def combustion_margin(name: str, moment: datetime) -> float:
    state = planet_state(name, moment)
    if name not in COMBUSTION_LIMITS:
        return 999.0
    return state["sun_separation_deg"] - state["combustion_limit_deg"]


def refine_combustion_boundary(
    name: str, left: datetime, right: datetime, left_inside: bool
) -> datetime:
    lo, hi = left, right
    for _ in range(45):
        mid = lo + (hi - lo) / 2
        inside = combustion_margin(name, mid) <= 0.0
        if inside == left_inside:
            lo = mid
        else:
            hi = mid
    return hi


def combustion_events(year: int, tz: ZoneInfo) -> list[dict]:
    rows = []
    start = datetime(year, 1, 1, 0, 0, tzinfo=tz)
    end = datetime(year + 1, 1, 1, 0, 0, tzinfo=tz)
    names = ["Mercury", "Venus", "Mars", "Jupiter", "Saturn"]

    for name in names:
        step = timedelta(hours=6)
        left = start - timedelta(days=20)
        left_inside = combustion_margin(name, left) <= 0.0
        probe = left + step

        while probe <= end + timedelta(days=20):
            inside = combustion_margin(name, probe) <= 0.0
            if inside != left_inside:
                event = refine_combustion_boundary(name, probe - step, probe, left_inside)
                if start <= event < end:
                    state = planet_state(name, event)
                    rows.append({
                        "planet": name,
                        "datetime": event.isoformat(),
                        "date": event.date().isoformat(),
                        "event": "asta_start" if inside else "udaya_end",
                        "sun_separation_deg": state.get("sun_separation_deg"),
                        "limit_deg": state.get("combustion_limit_deg"),
                        "rashi": state["rashi"],
                        "profile": "classical-angular-separation",
                    })
                left_inside = inside
            else:
                left_inside = inside
            probe += step

    rows.sort(key=lambda row: row["datetime"])
    return rows


def main() -> None:
    payload = json.loads(sys.stdin.read() or "{}")
    mode = str(payload.get("mode") or "positions").lower()
    timezone_name = payload.get("timezone") or "Asia/Kolkata"
    try:
        tz = ZoneInfo(timezone_name)
    except ZoneInfoNotFoundError:
        timezone_name = "Asia/Kolkata"
        tz = ZoneInfo(timezone_name)

    selected_date = datetime.strptime(
        payload.get("date") or datetime.now(tz).strftime("%Y-%m-%d"), "%Y-%m-%d"
    ).date()
    dt_text = payload.get("datetime")
    if dt_text:
        moment = datetime.fromisoformat(dt_text)
        moment = moment.replace(tzinfo=tz) if moment.tzinfo is None else moment.astimezone(tz)
    else:
        # Noon avoids ambiguity on date-only planetary-position pages.
        moment = datetime(
            selected_date.year, selected_date.month, selected_date.day, 12, 0, tzinfo=tz
        )

    output = {
        "ok": True,
        "mode": mode,
        "date": selected_date.isoformat(),
        "datetime": moment.isoformat(),
        "timezone": timezone_name,
        "engine": {
            "name": "tithika-planetary",
            "version": ENGINE_VERSION,
            "astronomy": "Astronomy Engine (MIT, vendored)",
            "coordinates": "apparent geocentric true ecliptic of date",
            "ayanamsha": "Lahiri / Chitrapaksha",
            "rahu_ketu": "mean nodes",
            "sidereal": True,
        },
    }

    if mode == "positions":
        output["planets"] = positions(moment, bool(payload.get("modern", False)))
    elif mode == "transit":
        output["year"] = selected_date.year
        output["events"] = transit_events(selected_date.year, tz)
    elif mode == "retrograde":
        output["year"] = selected_date.year
        output["events"] = retrograde_events(selected_date.year, tz)
    elif mode == "combustion":
        output["year"] = selected_date.year
        output["events"] = combustion_events(selected_date.year, tz)
        output["note"] = (
            "Combustion intervals use the classical angular-separation profile exposed "
            "per planet; they are not a location-specific optical visibility model."
        )
    else:
        raise ValueError("Unsupported planetary mode")

    print(json.dumps(output, ensure_ascii=False))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(json.dumps({
            "ok": False,
            "error": str(exc),
            "code": "PLANETARY_CALCULATION_FAILED",
        }))
        sys.exit(1)
