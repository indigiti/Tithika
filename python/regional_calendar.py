#!/usr/bin/env python3
"""
Tithika regional calendar engine.

One astronomy core, explicit regional conventions:
- Solar: Tamil, Malayalam, Bengali, Odia, Assamese.
- Amanta lunar: Telugu, Kannada, Gujarati, Marathi.
- Purnimanta lunar: Hindi.
- Gaudiya/ISKCON: Purnimanta lunar month with Vishnu month names.

Solar month/day is derived from exact Lahiri Nirayana Sankranti ingress dates.
Lunar variants reuse the shared sunrise Panchang and lunar_month_info contract.
"""
from __future__ import annotations

import calendar
import json
import sys
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import panchang
import sankranti

ENGINE_VERSION = "0.2.0"

SOLAR_MONTHS = {
    "tamil": [
        "Chithirai", "Vaikasi", "Aani", "Aadi", "Avani", "Purattasi",
        "Aippasi", "Karthigai", "Margazhi", "Thai", "Maasi", "Panguni",
    ],
    "malayalam": [
        "Medam", "Edavam", "Mithunam", "Karkidakam", "Chingam", "Kanni",
        "Thulam", "Vrischikam", "Dhanu", "Makaram", "Kumbham", "Meenam",
    ],
    "bengali": [
        "Boishakh", "Joishtho", "Asharh", "Srabon", "Bhadro", "Ashwin",
        "Kartik", "Ogrohayon", "Poush", "Magh", "Falgun", "Choitro",
    ],
    "odia": [
        "Baisakha", "Jyestha", "Ashadha", "Shrabana", "Bhadraba", "Ashwina",
        "Kartika", "Margasira", "Pausha", "Magha", "Phalguna", "Chaitra",
    ],
    "assamese": [
        "Bohag", "Jeth", "Ahar", "Sawan", "Bhad", "Ahin",
        "Kati", "Aghun", "Puh", "Magh", "Phagun", "Chot",
    ],
}

LUNAR_VARIANTS = {
    "hindi": {"month_type": "purnimanta"},
    "telugu": {"month_type": "amanta"},
    "kannada": {"month_type": "amanta"},
    "gujarati": {"month_type": "amanta"},
    "marathi": {"month_type": "amanta"},
    "iskcon": {"month_type": "purnimanta"},
}

LUNAR_MONTH_LOCAL = {
    "telugu": {
        "Chaitra":"Chaitramu","Vaishakha":"Vaishakhamu","Jyeshtha":"Jyeshthamu",
        "Ashadha":"Ashadhamu","Shravana":"Shravanamu","Bhadrapada":"Bhadrapadamu",
        "Ashwina":"Ashwayujamu","Kartika":"Kartikamu","Margashirsha":"Margashiramu",
        "Pausha":"Pushyamu","Magha":"Maghamu","Phalguna":"Phalgunamu",
    },
    "kannada": {
        "Chaitra":"Chaitra","Vaishakha":"Vaishakha","Jyeshtha":"Jyeshtha",
        "Ashadha":"Ashadha","Shravana":"Shravana","Bhadrapada":"Bhadrapada",
        "Ashwina":"Ashwayuja","Kartika":"Kartika","Margashirsha":"Margashira",
        "Pausha":"Pushya","Magha":"Magha","Phalguna":"Phalguna",
    },
    "gujarati": {
        "Chaitra":"Chaitra","Vaishakha":"Vaishakh","Jyeshtha":"Jeth",
        "Ashadha":"Ashadh","Shravana":"Shravan","Bhadrapada":"Bhadarvo",
        "Ashwina":"Aso","Kartika":"Kartik","Margashirsha":"Magshar",
        "Pausha":"Posh","Magha":"Maha","Phalguna":"Fagan",
    },
    "marathi": {
        "Chaitra":"Chaitra","Vaishakha":"Vaishakh","Jyeshtha":"Jyeshtha",
        "Ashadha":"Ashadh","Shravana":"Shravan","Bhadrapada":"Bhadrapad",
        "Ashwina":"Ashwin","Kartika":"Kartik","Margashirsha":"Margashirsha",
        "Pausha":"Paush","Magha":"Magh","Phalguna":"Phalgun",
    },
    "hindi": {},
}

ISKCON_MONTHS = {
    "Chaitra":"Vishnu",
    "Vaishakha":"Madhusudana",
    "Jyeshtha":"Trivikrama",
    "Ashadha":"Vamana",
    "Shravana":"Sridhara",
    "Bhadrapada":"Hrishikesha",
    "Ashwina":"Padmanabha",
    "Kartika":"Damodara",
    "Margashirsha":"Keshava",
    "Pausha":"Narayana",
    "Magha":"Madhava",
    "Phalguna":"Govinda",
}

SUPPORTED = tuple(list(SOLAR_MONTHS) + list(LUNAR_VARIANTS))


def ingress_index(year, lat, lon, tz, hour24):
    events = (
        sankranti.find_year(year - 1, lat, lon, tz, hour24)
        + sankranti.find_year(year, lat, lon, tz, hour24)
        + sankranti.find_year(year + 1, lat, lon, tz, hour24)
    )
    events.sort(key=lambda row: row["datetime"])
    return events


def latest_ingress(moment, events, sign_id):
    candidates = [
        row for row in events
        if row["rashi_id"] == sign_id
        and datetime.fromisoformat(row["datetime"]) <= moment
    ]
    return candidates[-1] if candidates else None


def solar_era(variant, d, sign_id):
    if variant == "malayalam":
        # Kollam Era increments when Chingam/Simha begins, normally in August.
        return {
            "name": "Kollavarsham",
            "year": d.year - 824 if (d.month >= 8 and sign_id >= 4) else d.year - 825,
        }
    if variant == "bengali":
        # Bengali year turns with Mesha/Boishakh; Makara..Meena belong to the
        # pre-Boishakh part of the Gregorian year.
        return {
            "name": "Bengali Era",
            "year": d.year - 593 if sign_id <= 8 else d.year - 594,
        }
    return None


def solar_day_row(variant, d, sunrise, state, events, lat, lon, tz):
    sign_id = state["sun_rashi_id"]
    ingress = latest_ingress(sunrise, events, sign_id)
    if ingress:
        ingress_dt = datetime.fromisoformat(ingress["datetime"])
        ingress_date = ingress_dt.date()

        # Bengali and Assamese Suryasiddhanta-style day numbering rolls the
        # solar month at the first sunrise after Sankranti when the ingress
        # occurs after that civil day's sunrise. Tamil/Odia/Malayalam keep
        # the Sankranti civil date as day 1 in Tithika's current profiles.
        if variant in ("bengali", "assamese"):
            ingress_sunrise = panchang.rise_set(
                ingress_date, lat, lon, tz,
                panchang.astronomy.Body.Sun,
                panchang.astronomy.Direction.Rise,
            )
            if ingress_sunrise and ingress_dt > ingress_sunrise:
                ingress_date += timedelta(days=1)

        day_number = (d - ingress_date).days + 1
    else:
        day_number = None

    return {
        "regional_month": SOLAR_MONTHS[variant][sign_id],
        "regional_day": day_number,
        "calendar_basis": "nirayana-solar",
        "solar_rashi": state["sun_rashi"],
        "solar_ingress": ingress["datetime"] if ingress else None,
        "era": solar_era(variant, d, sign_id),
    }


def base_lunar_name(value):
    return str(value or "").replace("Adhika ", "")


def lunar_day_row(variant, sunrise, state):
    month_info = panchang.lunar_month_info(sunrise, state)
    month_type = LUNAR_VARIANTS[variant]["month_type"]
    canonical = (
        month_info.get("purnimanta")
        if month_type == "purnimanta"
        else month_info.get("amanta")
    )
    canonical_base = base_lunar_name(canonical)
    if variant == "iskcon":
        local = ISKCON_MONTHS.get(canonical_base, canonical_base)
        if canonical and canonical.startswith("Adhika "):
            local = "Purushottama (" + local + ")"
    else:
        local = LUNAR_MONTH_LOCAL.get(variant, {}).get(
            canonical_base, canonical_base
        )
        if canonical and canonical.startswith("Adhika "):
            local = "Adhika " + local

    return {
        "regional_month": local,
        "canonical_month": canonical,
        "regional_day": state["tithi_number"],
        "calendar_basis": month_type + "-lunar",
        "adhika": bool(month_info.get("adhika")),
        "paksha": state["paksha"],
        "tithi": state["tithi"],
    }



def calculate_day(variant, selected, lat, lon, tz, hour24):
    sunrise = panchang.rise_set(
        selected, lat, lon, tz,
        panchang.astronomy.Body.Sun,
        panchang.astronomy.Direction.Rise,
    )
    sunset = panchang.rise_set(
        selected, lat, lon, tz,
        panchang.astronomy.Body.Sun,
        panchang.astronomy.Direction.Set,
    )
    next_sunrise = panchang.rise_set(
        selected + timedelta(days=1), lat, lon, tz,
        panchang.astronomy.Body.Sun,
        panchang.astronomy.Direction.Rise,
    )
    if not sunrise or not sunset or not next_sunrise:
        raise ValueError("Sunrise/sunset unavailable for this latitude/date")

    state = panchang.state_at(sunrise)
    ingresses = (
        ingress_index(selected.year, lat, lon, tz, hour24)
        if variant in SOLAR_MONTHS else []
    )
    regional = (
        solar_day_row(
            variant, selected, sunrise, state, ingresses, lat, lon, tz
        )
        if variant in SOLAR_MONTHS
        else lunar_day_row(variant, sunrise, state)
    )

    moonrise = panchang.rise_set(
        selected, lat, lon, tz,
        panchang.astronomy.Body.Moon,
        panchang.astronomy.Direction.Rise,
    )
    moonset = panchang.rise_set(
        selected, lat, lon, tz,
        panchang.astronomy.Body.Moon,
        panchang.astronomy.Direction.Set,
    )
    muhurtas = panchang.daily_muhurtas(
        selected, sunrise, sunset, next_sunrise,
        lat, lon, tz, hour24,
    )
    tithi_end = panchang.find_transition(
        sunrise, next_sunrise, "tithi_id", state["tithi_id"]
    )
    nakshatra_end = panchang.find_transition(
        sunrise, next_sunrise, "nakshatra_id", state["nakshatra_id"]
    )
    yoga_end = panchang.find_transition(
        sunrise, next_sunrise, "yoga_id", state["yoga_id"]
    )
    karana_end = panchang.find_transition(
        sunrise, next_sunrise, "karana_id", state["karana_id"]
    )

    return {
        "date": selected.isoformat(),
        "weekday": selected.strftime("%A"),
        "available": True,
        "sunrise": sunrise.isoformat(),
        "sunrise_label": panchang.fmt(sunrise, hour24),
        "sunset": sunset.isoformat(),
        "sunset_label": panchang.fmt(sunset, hour24),
        "moonrise": moonrise.isoformat() if moonrise else None,
        "moonrise_label": panchang.fmt(moonrise, hour24),
        "moonset": moonset.isoformat() if moonset else None,
        "moonset_label": panchang.fmt(moonset, hour24),
        "tithi": state["tithi"],
        "tithi_number": state["tithi_number"],
        "paksha": state["paksha"],
        "tithi_end": tithi_end.isoformat() if tithi_end else None,
        "tithi_end_label": (
            panchang.transition_label(tithi_end, selected, hour24)
            if tithi_end else None
        ),
        "nakshatra": state["nakshatra"],
        "nakshatra_pada": state["nakshatra_pada"],
        "nakshatra_end": nakshatra_end.isoformat() if nakshatra_end else None,
        "nakshatra_end_label": (
            panchang.transition_label(nakshatra_end, selected, hour24)
            if nakshatra_end else None
        ),
        "yoga": state["yoga"],
        "yoga_end_label": (
            panchang.transition_label(yoga_end, selected, hour24)
            if yoga_end else None
        ),
        "karana": state["karana"],
        "karana_end_label": (
            panchang.transition_label(karana_end, selected, hour24)
            if karana_end else None
        ),
        "moon_rashi": state["moon_rashi"],
        "sun_rashi": state["sun_rashi"],
        "sun_nakshatra": state["sun_nakshatra"],
        "muhurtas": muhurtas,
        **regional,
    }

def calculate_month(variant, selected, lat, lon, tz, hour24):
    _, count = calendar.monthrange(selected.year, selected.month)
    dates = [selected.replace(day=x) for x in range(1, count + 1)]
    next_date = dates[-1] + timedelta(days=1)

    sunrises = {
        d: panchang.rise_set(
            d, lat, lon, tz,
            panchang.astronomy.Body.Sun,
            panchang.astronomy.Direction.Rise,
        )
        for d in dates + [next_date]
    }
    sunsets = {
        d: panchang.rise_set(
            d, lat, lon, tz,
            panchang.astronomy.Body.Sun,
            panchang.astronomy.Direction.Set,
        )
        for d in dates
    }
    ingresses = (
        ingress_index(selected.year, lat, lon, tz, hour24)
        if variant in SOLAR_MONTHS else []
    )

    rows = []
    for d in dates:
        sunrise = sunrises.get(d)
        sunset = sunsets.get(d)
        next_sunrise = sunrises.get(d + timedelta(days=1))
        if not sunrise or not sunset or not next_sunrise:
            rows.append({"date": d.isoformat(), "available": False})
            continue
        state = panchang.state_at(sunrise)
        regional = (
            solar_day_row(
                variant, d, sunrise, state, ingresses, lat, lon, tz
            )
            if variant in SOLAR_MONTHS
            else lunar_day_row(variant, sunrise, state)
        )
        rows.append({
            "date": d.isoformat(),
            "day": d.day,
            "weekday": d.strftime("%A"),
            "weekday_short": d.strftime("%a"),
            "available": True,
            "sunrise": sunrise.isoformat(),
            "sunrise_label": panchang.fmt(sunrise, hour24),
            "sunset": sunset.isoformat(),
            "sunset_label": panchang.fmt(sunset, hour24),
            "tithi": state["tithi"],
            "tithi_number": state["tithi_number"],
            "paksha": state["paksha"],
            "nakshatra": state["nakshatra"],
            "nakshatra_pada": state["nakshatra_pada"],
            "moon_rashi": state["moon_rashi"],
            **regional,
        })
    return rows


def main():
    payload = json.loads(sys.stdin.read() or "{}")
    variant = str(payload.get("variant") or "hindi").lower()
    if variant not in SUPPORTED:
        raise ValueError("Unsupported regional calendar variant")

    lat = float(payload.get("lat", 19.0760))
    lon = float(payload.get("lon", 72.8777))
    if not (-90 <= lat <= 90 and -180 <= lon <= 180):
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
    view = str(payload.get("view") or "month").lower()
    if view not in ("day", "month"):
        raise ValueError("Unsupported regional calendar view")

    rows = calculate_month(
        variant, selected, lat, lon, tz, hour24
    ) if view == "month" else None
    day = calculate_day(
        variant, selected, lat, lon, tz, hour24
    ) if view == "day" else None

    basis = (
        "nirayana-solar" if variant in SOLAR_MONTHS
        else LUNAR_VARIANTS[variant]["month_type"] + "-lunar"
    )
    print(json.dumps({
        "ok": True,
        "variant": variant,
        "view": view,
        "date": selected.isoformat(),
        "year": selected.year,
        "month": selected.month,
        "month_name": selected.strftime("%B"),
        "first_weekday": calendar.monthrange(
            selected.year, selected.month
        )[0],
        "engine": {
            "name": "tithika-regional-calendar",
            "version": ENGINE_VERSION,
            "panchang_version": panchang.ENGINE_VERSION,
            "ayanamsha": "Lahiri / Chitrapaksha",
            "basis": basis,
        },
        "location": {
            "city": (payload.get("city") or "Current location").strip()[:120],
            "lat": lat,
            "lon": lon,
            "timezone": timezone_name,
        },
        "day": day,
        "days": rows or [],
        "note": (
            "Regional labels share one Lahiri astronomy core while preserving "
            "the calendar's solar, Amanta or Purnimanta month convention."
        ),
    }, ensure_ascii=False))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(json.dumps({
            "ok": False,
            "error": str(exc),
            "code": "REGIONAL_CALENDAR_FAILED",
        }))
        sys.exit(1)