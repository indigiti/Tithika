#!/usr/bin/env python3
"""
Reusable Panchang utilities built directly on Tithika's verified Lahiri core.

Modes:
- sunrise: local Hindu-day sunrise context
- nakshatra: exact Nakshatra intervals for the selected Gregorian month
- ganda-moola: yearly intervals for the six Ganda Moola Nakshatras
- abhijit-nakshatra: yearly Moon passages through the intercalary Abhijit span
- vinchudo: yearly Moon passages through Vrishchika/Scorpio
- jwalamukhi: yearly exact overlaps of five Tithi/Nakshatra combinations
- creation-days: yearly Manvadi/Yugadi/Kalpadi dates by sunrise Panchang
- sankalpa: structured Sankalpa context at selected local time
- vedic-clock: 60-Ghati Ishtakala and 30+30 Ghati ritual clock
"""
from __future__ import annotations

import calendar
import json
import sys
from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import panchang

ENGINE_VERSION = "0.1.0"

GANDA_MOOLA = {"Ashwini", "Ashlesha", "Magha", "Jyeshtha", "Mula", "Revati"}

# Abhijit: 6°40' to 10°53'20" Makara = 276°40' to 280°53'20".
ABHIJIT_START = 270.0 + 6.0 + 40.0 / 60.0
ABHIJIT_END = 270.0 + 10.0 + 53.0 / 60.0 + 20.0 / 3600.0

JWALAMUKHI_COMBINATIONS = {
    (1, "Mula"): "Pratipada + Mula",
    (5, "Bharani"): "Panchami + Bharani",
    (8, "Krittika"): "Ashtami + Krittika",
    (9, "Rohini"): "Navami + Rohini",
    (10, "Ashlesha"): "Dashami + Ashlesha",
}

MANVADI_RULES = [
    ("Brahma Savarni Manvadi", "Magha", "Shukla Paksha", 7),
    ("Savarni Manvadi", "Phalguna", "Shukla Paksha", 15),
    ("Swayambhuva Manvadi", "Chaitra", "Shukla Paksha", 3),
    ("Swarochisha Manvadi", "Chaitra", "Shukla Paksha", 15),
    ("Vaivaswata Manvadi", "Jyeshtha", "Shukla Paksha", 15),
    ("Raivata Manvadi", "Ashadha", "Shukla Paksha", 10),
    ("Chakshusha Manvadi", "Ashadha", "Shukla Paksha", 15),
    ("Indra Savarni Manvadi", "Bhadrapada", "Krishna Paksha", 8),
    ("Daiva Savarni Manvadi", "Bhadrapada", "Krishna Paksha", 15),
    ("Rudra Savarni Manvadi", "Bhadrapada", "Shukla Paksha", 3),
    ("Daksha Savarni Manvadi", "Ashwina", "Shukla Paksha", 9),
    ("Tamasa Manvadi", "Kartika", "Shukla Paksha", 12),
    ("Uttama Manvadi", "Kartika", "Shukla Paksha", 15),
    ("Dharma Savarni Manvadi", "Pausha", "Shukla Paksha", 11),
]

YUGADI_RULES = [
    ("Dwapara Yuga Diwas", "Phalguna", "Krishna Paksha", 15),
    ("Treta Yuga Diwas", "Vaishakha", "Shukla Paksha", 3),
    ("Kali Yuga Diwas", "Ashwina", "Krishna Paksha", 13),
    ("Satya Yuga Diwas", "Kartika", "Shukla Paksha", 9),
]

KALPADI_RULES = [
    ("Varaha Kalpadi", "Magha", "Shukla Paksha", 13),
    ("Brahma Kalpadi", "Chaitra", "Krishna Paksha", 3),
    ("Kurma Kalpadi First", "Chaitra", "Shukla Paksha", 1),
    ("Kurma Kalpadi Second", "Chaitra", "Shukla Paksha", 5),
    ("Parthiva Kalpadi", "Vaishakha", "Shukla Paksha", 3),
    ("Savitri Kalpadi", "Kartika", "Shukla Paksha", 7),
    ("Pralaya Kalpadi", "Margashirsha", "Shukla Paksha", 9),
]

SAMVATSARA_NAMES = [
    "Prabhava","Vibhava","Shukla","Pramoda","Prajotpatti","Angirasa",
    "Srimukha","Bhava","Yuva","Dhata","Ishvara","Bahudhanya",
    "Pramathi","Vikrama","Vrisha","Chitrabhanu","Subhanu","Tarana",
    "Parthiva","Vyaya","Sarvajit","Sarvadhari","Virodhi","Vikriti",
    "Khara","Nandana","Vijaya","Jaya","Manmatha","Durmukhi",
    "Hevilambi","Vilambi","Vikari","Sharvari","Plava","Shubhakrit",
    "Shobhakrit","Krodhi","Vishvavasu","Parabhava","Plavanga","Kilaka",
    "Saumya","Sadharana","Virodhikrit","Paridhavi","Pramadicha","Ananda",
    "Rakshasa","Nala","Pingala","Kalayukti","Siddharthi","Raudra",
    "Durmati","Dundubhi","Rudhirodgari","Raktakshi","Krodhana","Akshaya",
]

WEEKDAY_SANSKRIT = {
    0:"Somawara",1:"Mangalawara",2:"Budhawara",3:"Guruwara",
    4:"Shukrawara",5:"Shaniwara",6:"Raviwara",
}


def month_bounds(selected: date, tz: ZoneInfo) -> tuple[datetime, datetime]:
    start = datetime(selected.year, selected.month, 1, tzinfo=tz)
    if selected.month == 12:
        end = datetime(selected.year + 1, 1, 1, tzinfo=tz)
    else:
        end = datetime(selected.year, selected.month + 1, 1, tzinfo=tz)
    return start, end


def year_bounds(year: int, tz: ZoneInfo) -> tuple[datetime, datetime]:
    return datetime(year, 1, 1, tzinfo=tz), datetime(year + 1, 1, 1, tzinfo=tz)


def fmt_interval(start: datetime, end: datetime, hour24: bool) -> dict:
    return {
        "start": start.isoformat(),
        "end": end.isoformat(),
        "start_label": panchang.transition_label(start, start.date(), hour24),
        "end_label": panchang.transition_label(end, start.date(), hour24),
        "date": start.date().isoformat(),
        "date_label": start.strftime("%B %d, %Y").replace(" 0", " "),
    }


def state_intervals(
    start: datetime,
    end: datetime,
    key: str,
    name_key: str,
    hour24: bool,
    step_minutes: int = 360,
) -> list[dict]:
    rows = []
    cursor = start
    while cursor < end:
        state = panchang.state_at(cursor)
        transition = panchang.find_transition(
            cursor, end, key, state[key], step_minutes=step_minutes
        )
        stop = transition or end
        row = fmt_interval(cursor, stop, hour24)
        row.update({
            "id": state[key],
            "name": state[name_key],
            "state": state,
        })
        rows.append(row)
        if transition is None:
            break
        cursor = transition + timedelta(seconds=1)
    return rows


def nakshatra_intervals(start: datetime, end: datetime, hour24: bool) -> list[dict]:
    rows = state_intervals(start, end, "nakshatra_id", "nakshatra", hour24)
    for row in rows:
        row["pada_at_start"] = row["state"]["nakshatra_pada"]
        row.pop("state", None)
    return rows


def tithi_intervals(start: datetime, end: datetime, hour24: bool) -> list[dict]:
    rows = state_intervals(start, end, "tithi_id", "tithi", hour24)
    for row in rows:
        state = row.pop("state")
        row["number"] = state["tithi_number"]
        row["paksha"] = state["paksha"]
    return rows


def rashi_intervals(start: datetime, end: datetime, hour24: bool) -> list[dict]:
    rows = state_intervals(start, end, "moon_rashi_id", "moon_rashi", hour24)
    for row in rows:
        row.pop("state", None)
    return rows


def boolean_intervals(
    start: datetime,
    end: datetime,
    predicate,
    hour24: bool,
    step_minutes: int = 120,
) -> list[dict]:
    rows = []
    cursor = start
    current = bool(predicate(panchang.state_at(cursor)))
    active_start = cursor if current else None
    probe = cursor + timedelta(minutes=step_minutes)

    while probe <= end:
        value = bool(predicate(panchang.state_at(probe)))
        if value != current:
            lo = probe - timedelta(minutes=step_minutes)
            hi = probe
            for _ in range(34):
                mid = lo + (hi - lo) / 2
                mid_value = bool(predicate(panchang.state_at(mid)))
                if mid_value == current:
                    lo = mid
                else:
                    hi = mid
            boundary = hi
            if current and active_start is not None:
                rows.append(fmt_interval(active_start, boundary, hour24))
                active_start = None
            else:
                active_start = boundary
            current = value
        probe += timedelta(minutes=step_minutes)

    if current and active_start is not None:
        rows.append(fmt_interval(active_start, end, hour24))
    return rows


def yearly_ganda_moola(year: int, tz: ZoneInfo, hour24: bool) -> list[dict]:
    start, end = year_bounds(year, tz)
    rows = []
    for row in nakshatra_intervals(start, end, hour24):
        if row["name"] in GANDA_MOOLA:
            row["classification"] = "Ganda Moola"
            rows.append(row)
    return rows


def yearly_abhijit(year: int, tz: ZoneInfo, hour24: bool) -> list[dict]:
    start, end = year_bounds(year, tz)
    rows = boolean_intervals(
        start,
        end,
        lambda s: ABHIJIT_START <= s["moon_longitude"] < ABHIJIT_END,
        hour24,
        step_minutes=120,
    )
    for row in rows:
        row["name"] = "Abhijit Nakshatra"
        row["longitude_span"] = [round(ABHIJIT_START, 8), round(ABHIJIT_END, 8)]
    return rows


def yearly_vinchudo(year: int, tz: ZoneInfo, hour24: bool) -> list[dict]:
    start, end = year_bounds(year, tz)
    rows = []
    for row in rashi_intervals(start, end, hour24):
        if row["id"] == 7:
            row["name"] = "Vinchudo"
            row["moon_rashi"] = "Vrishchika"
            rows.append(row)
    return rows


def overlap(a_start: datetime, a_end: datetime, b_start: datetime, b_end: datetime):
    start = max(a_start, b_start)
    end = min(a_end, b_end)
    return (start, end) if start < end else None


def yearly_jwalamukhi(year: int, tz: ZoneInfo, hour24: bool) -> list[dict]:
    start, end = year_bounds(year, tz)
    tithis = tithi_intervals(start, end, hour24)
    naks = nakshatra_intervals(start, end, hour24)
    rows = []
    j = 0
    for tithi in tithis:
        ts, te = datetime.fromisoformat(tithi["start"]), datetime.fromisoformat(tithi["end"])
        while j < len(naks) and datetime.fromisoformat(naks[j]["end"]) <= ts:
            j += 1
        k = j
        while k < len(naks):
            nak = naks[k]
            ns, ne = datetime.fromisoformat(nak["start"]), datetime.fromisoformat(nak["end"])
            if ns >= te:
                break
            combo = JWALAMUKHI_COMBINATIONS.get((tithi["number"], nak["name"]))
            if combo:
                common = overlap(ts, te, ns, ne)
                if common:
                    row = fmt_interval(common[0], common[1], hour24)
                    row.update({
                        "name": "Jwalamukhi Yoga",
                        "combination": combo,
                        "tithi": tithi["name"],
                        "tithi_number": tithi["number"],
                        "paksha": tithi["paksha"],
                        "nakshatra": nak["name"],
                    })
                    rows.append(row)
            k += 1
    return rows


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


def lunar_rule_day(d: date, lat: float, lon: float, tz: ZoneInfo):
    sunrise = sunrise_for(d, lat, lon, tz)
    if not sunrise:
        return None
    state = panchang.state_at(sunrise)
    month = panchang.lunar_month_info(sunrise, state).get("purnimanta")
    if not month:
        return None
    return sunrise, state, str(month).replace("Adhika ", "")


def creation_days(year: int, lat: float, lon: float, tz: ZoneInfo, hour24: bool):
    registries = {
        "manvadi": MANVADI_RULES,
        "yugadi": YUGADI_RULES,
        "kalpadi": KALPADI_RULES,
    }
    lookup = {
        kind: {(month, paksha, number): name for name, month, paksha, number in rules}
        for kind, rules in registries.items()
    }
    output = {kind: [] for kind in registries}

    # A target Tithi may touch two local sunrises. These creation-day lists
    # represent one occurrence, not one row per sunrise. Resolve the exact
    # Tithi span and assign its local civil date from the interval midpoint;
    # this also matches the 2026 Phalguna Amavasya / Vaishakha Tritiya
    # benchmark behavior.
    scan_start = datetime(year, 1, 1, tzinfo=tz) - timedelta(days=2)
    scan_end = datetime(year + 1, 1, 1, tzinfo=tz) + timedelta(days=2)
    seen = {kind: set() for kind in registries}

    for interval_row in tithi_intervals(scan_start, scan_end, hour24):
        begin = datetime.fromisoformat(interval_row["start"])
        finish = datetime.fromisoformat(interval_row["end"])
        midpoint = begin + (finish - begin) / 2
        display_date = midpoint.date()
        if display_date.year != year:
            continue

        state = panchang.state_at(midpoint)
        month_info = panchang.lunar_month_info(midpoint, state)
        month = str(month_info.get("purnimanta") or "").replace("Adhika ", "")
        key = (month, state["paksha"], state["tithi_number"])

        for kind in registries:
            name = lookup[kind].get(key)
            if not name or name in seen[kind]:
                continue
            sunrise = sunrise_for(display_date, lat, lon, tz)
            output[kind].append({
                "name": name,
                "date": display_date.isoformat(),
                "date_label": display_date.strftime("%B %d, %Y").replace(" 0", " "),
                "weekday": display_date.strftime("%A"),
                "sunrise": sunrise.isoformat() if sunrise else None,
                "sunrise_label": panchang.fmt(sunrise, hour24) if sunrise else None,
                "tithi_start": begin.isoformat(),
                "tithi_end": finish.isoformat(),
                "tithi_start_label": panchang.transition_label(begin, display_date, hour24),
                "tithi_end_label": panchang.transition_label(finish, display_date, hour24),
                "lunar_month": month,
                "paksha": state["paksha"],
                "tithi": state["tithi"],
                "tithi_number": state["tithi_number"],
                "date_rule": "local civil date containing exact Tithi midpoint",
            })
            seen[kind].add(name)

    for kind in output:
        output[kind].sort(key=lambda row: row["date"])
    return output


def chaitra_new_year(year: int, lat: float, lon: float, tz: ZoneInfo) -> date:
    for month in (3, 4):
        _, count = calendar.monthrange(year, month)
        for day in range(1, count + 1):
            d = date(year, month, day)
            item = lunar_rule_day(d, lat, lon, tz)
            if not item:
                continue
            _, state, lunar_month = item
            if (
                lunar_month == "Chaitra"
                and state["paksha"] == "Shukla Paksha"
                and state["tithi_number"] == 1
            ):
                return d
    raise ValueError("Unable to resolve Chaitra Shukla Pratipada")


def samvat_context(d: date, lat: float, lon: float, tz: ZoneInfo) -> dict:
    new_year = chaitra_new_year(d.year, lat, lon, tz)
    after = d >= new_year
    vikram = d.year + (57 if after else 56)
    shaka = d.year - (78 if after else 79)
    return {
        "vikrama": vikram,
        "shaka": shaka,
        "vikrama_samvatsara": SAMVATSARA_NAMES[(vikram + 9) % 60],
        "shaka_samvatsara": SAMVATSARA_NAMES[(shaka + 11) % 60],
        "new_year": new_year.isoformat(),
    }


def sankalpa_seasons(
    sunrise: datetime, sunrise_state: dict, purnimanta_month: str | None
) -> dict:
    sign = sunrise_state["sun_rashi_id"]
    vedic_ritu = [
        "Vasanta", "Vasanta",
        "Grishma", "Grishma",
        "Varsha", "Varsha",
        "Sharad", "Sharad",
        "Hemanta", "Hemanta",
        "Shishira", "Shishira",
    ][sign]
    vedic_ayana = (
        "Uttarayana" if sign in (9, 10, 11, 0, 1, 2) else "Dakshinayana"
    )

    lunar = str(purnimanta_month or "").replace("Adhika ", "")
    drik_ritu = {
        "Chaitra": "Vasanta", "Vaishakha": "Vasanta",
        "Jyeshtha": "Grishma", "Ashadha": "Grishma",
        "Shravana": "Varsha", "Bhadrapada": "Varsha",
        "Ashwina": "Sharad", "Kartika": "Sharad",
        "Margashirsha": "Hemanta", "Pausha": "Hemanta",
        "Magha": "Shishira", "Phalguna": "Shishira",
    }.get(lunar, vedic_ritu)

    tropical_sun, _, _ = panchang.tropical_longitudes(sunrise)
    drik_ayana = (
        "Uttarayana"
        if tropical_sun >= 270.0 or tropical_sun < 90.0
        else "Dakshinayana"
    )
    return {
        "drik_ritu": drik_ritu,
        "vedic_ritu": vedic_ritu,
        "drik_ayana": drik_ayana,
        "vedic_ayana": vedic_ayana,
    }


def parse_reference(selected: date, tz: ZoneInfo, value: str | None) -> datetime:
    if value:
        parsed = datetime.strptime(value, "%H:%M").time()
        return datetime.combine(selected, parsed, tzinfo=tz)
    now = datetime.now(tz)
    if selected == now.date():
        return now
    return datetime.combine(selected, time(12, 0), tzinfo=tz)


def sankalpa_context(
    selected: date, lat: float, lon: float, tz: ZoneInfo, hour24: bool, time_value: str | None
):
    reference = parse_reference(selected, tz, time_value)
    sunrise = sunrise_for(selected, lat, lon, tz)
    if not sunrise:
        raise ValueError("Sunrise unavailable for Sankalpa date")
    moment_state = panchang.state_at(reference)
    sunrise_state = panchang.state_at(sunrise)
    months = panchang.lunar_month_info(sunrise, sunrise_state)
    samvat = samvat_context(selected, lat, lon, tz)
    seasons = sankalpa_seasons(
        sunrise, sunrise_state, months.get("purnimanta")
    )
    return {
        "reference": reference.isoformat(),
        "reference_label": panchang.fmt(reference, hour24),
        "sunrise": sunrise.isoformat(),
        "sunrise_label": panchang.fmt(sunrise, hour24),
        "weekday": selected.strftime("%A"),
        "weekday_vedic": WEEKDAY_SANSKRIT[selected.weekday()],
        "tithi": moment_state["tithi"],
        "tithi_number": moment_state["tithi_number"],
        "paksha": moment_state["paksha"],
        "nakshatra": moment_state["nakshatra"],
        "nakshatra_pada": moment_state["nakshatra_pada"],
        "yoga": moment_state["yoga"],
        "karana": moment_state["karana"],
        "moon_rashi": moment_state["moon_rashi"],
        "sun_rashi": moment_state["sun_rashi"],
        "amanta_month": months.get("amanta"),
        "purnimanta_month": months.get("purnimanta"),
        "adhika_month": bool(months.get("adhika")),
        "vikrama_samvat": samvat["vikrama"],
        "shaka_samvat": samvat["shaka"],
        "vikrama_samvatsara": samvat["vikrama_samvatsara"],
        "shaka_samvatsara": samvat["shaka_samvatsara"],
        **seasons,
        "profile": "Sunrise-state for Samvatsara/month/Ritu/Ayana; selected-time state for Tithi/Nakshatra/Yoga/Karana. Drik and Vedic Ritu/Ayana are exposed separately.",
    }


def hindu_day_bounds(reference: datetime, lat: float, lon: float, tz: ZoneInfo):
    today = reference.date()
    sunrise = sunrise_for(today, lat, lon, tz)
    if not sunrise:
        raise ValueError("Sunrise unavailable")
    if reference < sunrise:
        anchor = today - timedelta(days=1)
        sunrise = sunrise_for(anchor, lat, lon, tz)
        sunset = sunset_for(anchor, lat, lon, tz)
        next_sunrise = sunrise_for(today, lat, lon, tz)
    else:
        anchor = today
        sunset = sunset_for(today, lat, lon, tz)
        next_sunrise = sunrise_for(today + timedelta(days=1), lat, lon, tz)
    if not sunrise or not sunset or not next_sunrise:
        raise ValueError("Hindu day boundaries unavailable")
    return anchor, sunrise, sunset, next_sunrise


def fractional_ghati(value: float) -> dict:
    value = max(0.0, value)
    ghati = int(value)
    pala_value = (value - ghati) * 60.0
    pala = int(pala_value)
    vipala = int(round((pala_value - pala) * 60.0))
    if vipala >= 60:
        vipala = 0
        pala += 1
    if pala >= 60:
        pala = 0
        ghati += 1
    return {
        "decimal": round(value, 8),
        "ghati": ghati,
        "pala": pala,
        "vipala": vipala,
        "label": f"{ghati:02d}:{pala:02d}:{vipala:02d}",
    }


def vedic_clock(
    selected: date, lat: float, lon: float, tz: ZoneInfo, hour24: bool, time_value: str | None
):
    reference = parse_reference(selected, tz, time_value)
    anchor, sunrise, sunset, next_sunrise = hindu_day_bounds(reference, lat, lon, tz)
    full_span = next_sunrise - sunrise
    sixty = 60.0 * (reference - sunrise).total_seconds() / full_span.total_seconds()

    if reference <= sunset:
        day_span = sunset - sunrise
        thirty = 30.0 * (reference - sunrise).total_seconds() / day_span.total_seconds()
        half = "day"
    else:
        night_span = next_sunrise - sunset
        thirty = 30.0 + 30.0 * (reference - sunset).total_seconds() / night_span.total_seconds()
        half = "night"

    state = panchang.state_at(reference)
    months = panchang.lunar_month_info(sunrise, panchang.state_at(sunrise))
    return {
        "reference": reference.isoformat(),
        "reference_label": reference.strftime("%H:%M:%S" if hour24 else "%I:%M:%S %p").lstrip("0"),
        "hindu_day": anchor.isoformat(),
        "sunrise": sunrise.isoformat(),
        "sunrise_label": panchang.fmt(sunrise, hour24),
        "sunset": sunset.isoformat(),
        "sunset_label": panchang.fmt(sunset, hour24),
        "next_sunrise": next_sunrise.isoformat(),
        "next_sunrise_label": panchang.fmt(next_sunrise, hour24),
        "ishtakala_60": fractional_ghati(sixty),
        "ritual_30_30": fractional_ghati(thirty),
        "ritual_half": half,
        "lunar_month": months.get("purnimanta"),
        "paksha": state["paksha"],
        "tithi": state["tithi"],
        "weekday_vedic": WEEKDAY_SANSKRIT[reference.weekday()],
    }


def sunrise_context(selected: date, lat: float, lon: float, tz: ZoneInfo, hour24: bool):
    sunrise = sunrise_for(selected, lat, lon, tz)
    sunset = sunset_for(selected, lat, lon, tz)
    next_sunrise = sunrise_for(selected + timedelta(days=1), lat, lon, tz)
    if not sunrise or not sunset or not next_sunrise:
        raise ValueError("Sunrise/sunset unavailable")
    state = panchang.state_at(sunrise)
    return {
        "date": selected.isoformat(),
        "weekday": selected.strftime("%A"),
        "sunrise": sunrise.isoformat(),
        "sunrise_label": panchang.fmt(sunrise, hour24),
        "sunset": sunset.isoformat(),
        "sunset_label": panchang.fmt(sunset, hour24),
        "next_sunrise": next_sunrise.isoformat(),
        "next_sunrise_label": panchang.fmt(next_sunrise, hour24),
        "ahoratra_minutes": round((next_sunrise - sunrise).total_seconds() / 60.0, 3),
        "daylight_minutes": round((sunset - sunrise).total_seconds() / 60.0, 3),
        "sunrise_state": state,
    }


def main():
    payload = json.loads(sys.stdin.read() or "{}")
    mode = str(payload.get("mode") or "sunrise").strip().lower()
    supported = {
        "sunrise","nakshatra","ganda-moola","abhijit-nakshatra","vinchudo",
        "jwalamukhi","creation-days","sankalpa","vedic-clock",
    }
    if mode not in supported:
        raise ValueError("Unsupported Panchang reuse mode")

    lat = float(payload.get("lat", 18.5204))
    lon = float(payload.get("lon", 73.8567))
    if not (-90 <= lat <= 90 and -180 <= lon <= 180):
        raise ValueError("Invalid latitude/longitude")

    timezone_name = payload.get("timezone") or "Asia/Kolkata"
    try:
        tz = ZoneInfo(timezone_name)
    except ZoneInfoNotFoundError:
        timezone_name = "Asia/Kolkata"
        tz = ZoneInfo(timezone_name)

    selected = datetime.strptime(
        payload.get("date") or datetime.now(tz).strftime("%Y-%m-%d"), "%Y-%m-%d"
    ).date()
    hour24 = bool(payload.get("hour24", False))
    time_value = payload.get("time")
    city = (payload.get("city") or "Current location").strip()[:120]

    if mode == "sunrise":
        result = sunrise_context(selected, lat, lon, tz, hour24)
    elif mode == "nakshatra":
        start, end = month_bounds(selected, tz)
        result = {
            "year": selected.year,
            "month": selected.month,
            "month_name": selected.strftime("%B"),
            "intervals": nakshatra_intervals(start, end, hour24),
        }
    elif mode == "ganda-moola":
        result = {"year": selected.year, "intervals": yearly_ganda_moola(selected.year, tz, hour24)}
    elif mode == "abhijit-nakshatra":
        result = {"year": selected.year, "intervals": yearly_abhijit(selected.year, tz, hour24)}
    elif mode == "vinchudo":
        result = {"year": selected.year, "intervals": yearly_vinchudo(selected.year, tz, hour24)}
    elif mode == "jwalamukhi":
        result = {"year": selected.year, "intervals": yearly_jwalamukhi(selected.year, tz, hour24)}
    elif mode == "creation-days":
        result = {"year": selected.year, **creation_days(selected.year, lat, lon, tz, hour24)}
    elif mode == "sankalpa":
        result = sankalpa_context(selected, lat, lon, tz, hour24, time_value)
    else:
        result = vedic_clock(selected, lat, lon, tz, hour24, time_value)

    print(json.dumps({
        "ok": True,
        "mode": mode,
        "engine": {
            "name": "tithika-panchang-reuse",
            "version": ENGINE_VERSION,
            "panchang_version": panchang.ENGINE_VERSION,
            "ayanamsha": "Lahiri / Chitrapaksha",
        },
        "location": {
            "city": city,
            "lat": lat,
            "lon": lon,
            "timezone": timezone_name,
        },
        **result,
    }, ensure_ascii=False))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(json.dumps({
            "ok": False,
            "error": str(exc),
            "code": "PANCHANG_REUSE_FAILED",
        }))
        sys.exit(1)
