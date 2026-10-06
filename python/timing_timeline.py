#!/usr/bin/env python3
"""
Tithika Jyotish timing and forecast timeline.

Builds a month-by-month activation timeline from already verified natal evidence,
Vimshottari periods and slow-planet transit houses. The engine intentionally
reports emphasis, timing context and evidence; it does not convert astrology
rules into guaranteed real-world events or probabilities.
"""
from __future__ import annotations

import calendar
import json
import sys
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import horoscope_analysis
import interpretation
import planetary
import vimshottari

ENGINE_VERSION = "0.1.0"
TIMING_PLANETS = ["Jupiter", "Saturn", "Rahu", "Ketu"]
DASHA_WEIGHTS = {"Mahadasha": 18.0, "Antardasha": 12.0, "Pratyantardasha": 6.0}
TRANSIT_WEIGHTS = {"Jupiter": 7.0, "Saturn": 7.0, "Rahu": 5.0, "Ketu": 5.0}
ROLE_SUPPORT = {"yogakaraka", "supportive"}
ROLE_CHALLENGE = {"challenging"}

BAND_ORDER = {"background": 0, "active": 1, "elevated": 2, "high": 3}


def month_start(value: datetime) -> datetime:
    return value.replace(day=1, hour=0, minute=0, second=0, microsecond=0)


def add_months(value: datetime, months: int) -> datetime:
    total = value.year * 12 + (value.month - 1) + months
    year, month0 = divmod(total, 12)
    return value.replace(year=year, month=month0 + 1, day=1)


def parse_start(payload: dict, tz: ZoneInfo) -> datetime:
    raw = str(payload.get("start_month") or payload.get("start_date") or "").strip()
    if not raw:
        return month_start(datetime.now(tz))
    if len(raw) == 7:
        raw = raw + "-01"
    value = datetime.fromisoformat(raw)
    if value.tzinfo is None:
        value = value.replace(tzinfo=tz)
    else:
        value = value.astimezone(tz)
    return month_start(value)


def parse_horizon(payload: dict) -> int:
    months = int(payload.get("months") or 12)
    if months not in (6, 12, 18, 24, 36):
        raise ValueError("months must be one of 6, 12, 18, 24 or 36")
    return months


def active_periods(schedule: dict, moment: datetime) -> list[dict]:
    maha = None
    for row in schedule.get("mahadasha", []):
        start = datetime.fromisoformat(row["full_start"])
        end = datetime.fromisoformat(row["full_end"])
        if start <= moment < end:
            maha = row
            break
    if not maha:
        return []

    antar = None
    for row in maha.get("antardasha", []):
        start = datetime.fromisoformat(row["full_start"])
        end = datetime.fromisoformat(row["full_end"])
        if start <= moment < end:
            antar = row
            break

    rows = [{
        "level": "Mahadasha",
        "planet": maha["lord"],
        "start": maha["full_start"],
        "end": maha["full_end"],
    }]
    if not antar:
        return rows

    rows.append({
        "level": "Antardasha",
        "planet": antar["lord"],
        "start": antar["full_start"],
        "end": antar["full_end"],
    })
    astart = datetime.fromisoformat(antar["full_start"])
    aend = datetime.fromisoformat(antar["full_end"])
    for row in vimshottari.child_periods(antar["lord"], astart, aend):
        start = datetime.fromisoformat(row["full_start"])
        end = datetime.fromisoformat(row["full_end"])
        if start <= moment < end:
            rows.append({
                "level": "Pratyantardasha",
                "planet": row["lord"],
                "start": row["full_start"],
                "end": row["full_end"],
            })
            break
    return rows


def dasha_map(periods: list[dict]) -> dict[str, str]:
    rows: dict[str, str] = {}
    for item in periods:
        if item["planet"] not in rows:
            rows[item["planet"]] = item["level"]
    return rows


def transit_snapshot(
    moment: datetime,
    node_model: str,
    asc_sign: int,
    moon_sign: int,
) -> list[dict]:
    rows = []
    for name in TIMING_PLANETS:
        state = planetary.planet_state(name, moment, node_model)
        rows.append({
            "planet": name,
            "rashi": state["rashi"],
            "rashi_id": state["rashi_id"],
            "retrograde": state["retrograde"],
            "house_from_lagna": horoscope_analysis.house_from(asc_sign, state["rashi_id"]),
            "house_from_moon": horoscope_analysis.house_from(moon_sign, state["rashi_id"]),
        })
    return rows


def relevant_planets(domain: dict, ownership: dict[str, list[int]], key: str) -> set[str]:
    houses = interpretation.DOMAIN_HOUSES[key]
    lords = {
        planet for planet, owned in ownership.items()
        if set(owned) & houses
    }
    return set(domain.get("relevant_planets", [])) | lords


def activation_quality(
    key: str,
    domain: dict,
    ownership: dict[str, list[int]],
    periods: list[dict],
    roles: dict[str, str],
) -> str:
    relevant = relevant_planets(domain, ownership, key)
    active_roles = {
        roles.get(item["planet"], "structural")
        for item in periods
        if item["planet"] in relevant
    }
    has_support = bool(active_roles & ROLE_SUPPORT)
    has_challenge = bool(active_roles & ROLE_CHALLENGE)
    if has_support and has_challenge:
        return "mixed"
    if has_support:
        return "supportive"
    if has_challenge:
        return "challenging"
    if "mixed" in active_roles:
        return "mixed"
    return "contextual"


def activation_index(
    key: str,
    domain: dict,
    ownership: dict[str, list[int]],
    periods: list[dict],
    transits: list[dict],
) -> tuple[float, dict]:
    relevant = relevant_planets(domain, ownership, key)
    houses = interpretation.DOMAIN_HOUSES[key]

    base = float(domain.get("evidence_index", 0.0)) * 0.55
    dasha_points = sum(
        DASHA_WEIGHTS[item["level"]]
        for item in periods
        if item["planet"] in relevant
    )
    transit_hits = [
        row for row in transits
        if row["house_from_lagna"] in houses or row["house_from_moon"] in houses
    ]
    transit_points = sum(TRANSIT_WEIGHTS[row["planet"]] for row in transit_hits)
    total = round(min(100.0, base + dasha_points + transit_points), 1)

    if total >= 75:
        band = "high"
    elif total >= 60:
        band = "elevated"
    elif total >= 45:
        band = "active"
    else:
        band = "background"

    dasha_hits = [
        {"level": item["level"], "planet": item["planet"]}
        for item in periods if item["planet"] in relevant
    ]
    return total, {
        "band": band,
        "base_evidence_points": round(base, 1),
        "dasha_points": round(dasha_points, 1),
        "transit_points": round(transit_points, 1),
        "dasha_hits": dasha_hits,
        "transit_hits": transit_hits,
    }


def month_narrative(title: str, score: float, band: str, details: dict) -> str:
    reasons = []
    reasons.extend(
        f"{x['level']} {x['planet']}" for x in details["dasha_hits"]
    )
    reasons.extend(
        f"{x['planet']} transit H{x['house_from_lagna']} from Lagna"
        for x in details["transit_hits"]
    )
    why = "; ".join(reasons[:4]) if reasons else "structural natal evidence"
    return (
        f"{title} has {band} emphasis at {score:.0f}/100 for this month. "
        f"Primary evidence: {why}. This activation index measures astrological "
        "emphasis, not the probability of an event."
    )


def monthly_rows(
    start: datetime,
    months: int,
    base: dict,
    schedule: dict,
    node_model: str,
) -> list[dict]:
    asc_sign = int(base["birth_profile"]["lagna"]["rashi_id"])
    moon = next(
        row for row in base["planet_interpretations"]
        if row["planet"] == "Moon"
    )
    moon_sign = int(moon["natal"]["rashi_id"])
    ownership = base["functional_lordship"]["planet_house_ownership"]
    domains = base["domain_interpretations"]
    roles = {
        row["planet"]: row["functional_role"]["category"]
        for row in base["planet_interpretations"]
    }

    rows = []
    for offset in range(months):
        a = add_months(start, offset)
        b = add_months(start, offset + 1)
        sample = a + (b - a) / 2
        periods = active_periods(schedule, sample)
        transits = transit_snapshot(sample, node_model, asc_sign, moon_sign)

        domain_rows = {}
        for key, domain in domains.items():
            score, details = activation_index(
                key, domain, ownership, periods, transits
            )
            quality = activation_quality(
                key, domain, ownership, periods, roles
            )
            domain_rows[key] = {
                "key": key,
                "title": domain["title"],
                "evidence_index": domain["evidence_index"],
                "activation_index": score,
                "band": details["band"],
                "quality": quality,
                "base_evidence_points": details["base_evidence_points"],
                "dasha_points": details["dasha_points"],
                "transit_points": details["transit_points"],
                "dasha_hits": details["dasha_hits"],
                "transit_hits": details["transit_hits"],
                "interpretation": month_narrative(
                    domain["title"], score, details["band"], details
                ),
            }

        ranked = sorted(
            domain_rows.values(),
            key=lambda row: (row["activation_index"], BAND_ORDER[row["band"]]),
            reverse=True,
        )
        rows.append({
            "month": a.strftime("%Y-%m"),
            "label": a.strftime("%B %Y"),
            "sample_datetime": sample.isoformat(),
            "dasha": periods,
            "transits": transits,
            "domains": domain_rows,
            "top_focus": [
                {
                    "key": row["key"],
                    "title": row["title"],
                    "activation_index": row["activation_index"],
                    "band": row["band"],
                    "quality": row["quality"],
                }
                for row in ranked[:3]
            ],
        })
    return rows


def dasha_markers(schedule: dict, start: datetime, end: datetime) -> list[dict]:
    rows = []
    for maha in schedule.get("mahadasha", []):
        mstart = datetime.fromisoformat(maha["full_start"])
        if start <= mstart < end:
            rows.append({
                "type": "dasha",
                "level": "Mahadasha",
                "planet": maha["lord"],
                "datetime": mstart.isoformat(),
                "label": f"{maha['lord']} Mahadasha begins",
            })
        for antar in maha.get("antardasha", []):
            astart = datetime.fromisoformat(antar["full_start"])
            if start <= astart < end:
                rows.append({
                    "type": "dasha",
                    "level": "Antardasha",
                    "planet": antar["lord"],
                    "parent": maha["lord"],
                    "datetime": astart.isoformat(),
                    "label": f"{maha['lord']} / {antar['lord']} Antardasha begins",
                })
    return rows


def refine_transit_change(
    name: str,
    left: datetime,
    right: datetime,
    old_sign: int,
    node_model: str,
) -> datetime:
    lo, hi = left, right
    for _ in range(42):
        mid = lo + (hi - lo) / 2
        sign = planetary.classify_longitude(
            planetary.sidereal_coordinates(name, mid, node_model)[0]
        )["rashi_id"]
        if sign == old_sign:
            lo = mid
        else:
            hi = mid
    return hi


def transit_markers(
    start: datetime,
    end: datetime,
    node_model: str,
) -> list[dict]:
    rows = []
    for name in TIMING_PLANETS:
        step = timedelta(days=3 if name in ("Rahu", "Ketu") else 5)
        left = start - step
        old_state = planetary.planet_state(name, left, node_model)
        old_sign = old_state["rashi_id"]
        probe = left + step
        while probe <= end + step:
            lon = planetary.sidereal_coordinates(name, probe, node_model)[0]
            sign = planetary.classify_longitude(lon)["rashi_id"]
            if sign != old_sign:
                event = refine_transit_change(
                    name, probe - step, probe, old_sign, node_model
                )
                if start <= event < end:
                    before = planetary.planet_state(
                        name, event - timedelta(seconds=10), node_model
                    )
                    after = planetary.planet_state(
                        name, event + timedelta(seconds=10), node_model
                    )
                    rows.append({
                        "type": "transit",
                        "planet": name,
                        "datetime": event.isoformat(),
                        "from_rashi": before["rashi"],
                        "to_rashi": after["rashi"],
                        "retrograde": after["retrograde"],
                        "label": (
                            f"{name} enters {after['rashi']}"
                            + (" retrograde" if after["retrograde"] else "")
                        ),
                    })
                old_sign = sign
            else:
                old_sign = sign
            probe += step
    return rows


def merged_windows(rows: list[dict]) -> list[dict]:
    if not rows:
        return []
    windows = []
    current = None
    for row in rows:
        top = row["top_focus"][0]
        signature = (top["key"], top["band"], top["quality"])
        if current and current["_signature"] == signature:
            current["end_month"] = row["month"]
            current["months"] += 1
            current["_scores"].append(float(top["activation_index"]))
            continue
        if current:
            current["average_activation_index"] = round(
                sum(current.pop("_scores")) / current["months"], 1
            )
            current.pop("_signature", None)
            windows.append(current)
        current = {
            "_signature": signature,
            "_scores": [float(top["activation_index"])],
            "start_month": row["month"],
            "end_month": row["month"],
            "months": 1,
            "focus_key": top["key"],
            "focus_title": top["title"],
            "band": top["band"],
            "quality": top["quality"],
        }
    if current:
        current["average_activation_index"] = round(
            sum(current.pop("_scores")) / current["months"], 1
        )
        current.pop("_signature", None)
        windows.append(current)
    return windows


def yearly_summary(rows: list[dict]) -> list[dict]:
    grouped: dict[int, list[dict]] = {}
    for row in rows:
        grouped.setdefault(int(row["month"][:4]), []).append(row)

    out = []
    for year, months in sorted(grouped.items()):
        aggregates = {}
        for key in interpretation.DOMAIN_HOUSES:
            vals = [
                float(row["domains"][key]["activation_index"])
                for row in months
            ]
            aggregates[key] = {
                "key": key,
                "title": months[0]["domains"][key]["title"],
                "average_activation_index": round(sum(vals) / len(vals), 1),
                "peak_activation_index": round(max(vals), 1),
                "peak_month": max(
                    months,
                    key=lambda row: row["domains"][key]["activation_index"]
                )["month"],
                "active_months": sum(
                    1 for row in months
                    if row["domains"][key]["band"] in ("active", "elevated", "high")
                ),
            }
        ranked = sorted(
            aggregates.values(),
            key=lambda row: row["average_activation_index"],
            reverse=True,
        )
        out.append({
            "year": year,
            "months_covered": len(months),
            "domains": aggregates,
            "top_focus": ranked[:3],
        })
    return out


def build(payload: dict) -> dict:
    timezone_name = str(payload.get("timezone") or "Asia/Kolkata")
    try:
        tz = ZoneInfo(timezone_name)
    except ZoneInfoNotFoundError:
        timezone_name = "Asia/Kolkata"
        tz = ZoneInfo(timezone_name)

    start = parse_start(payload, tz)
    months = parse_horizon(payload)
    end = add_months(start, months)
    node_model = str(payload.get("node_model") or "mean").lower()
    if node_model not in ("mean", "true"):
        raise ValueError("node_model must be mean or true")

    base_payload = {
        **payload,
        "timezone": timezone_name,
        "node_model": node_model,
        "as_of": (start + timedelta(hours=12)).isoformat(),
    }
    base = interpretation.build(base_payload)
    birth = datetime.fromisoformat(base["birth_datetime"])
    if start < month_start(birth):
        raise ValueError("Timeline start month cannot precede the birth month")

    schedule = vimshottari.calculate(birth, start)
    rows = monthly_rows(start, months, base, schedule, node_model)
    markers = dasha_markers(schedule, start, end)
    markers.extend(transit_markers(start, end, node_model))
    markers.sort(key=lambda row: row["datetime"])

    return {
        "ok": True,
        "birth_datetime": base["birth_datetime"],
        "location": base["location"],
        "start_month": start.strftime("%Y-%m"),
        "end_month_exclusive": end.strftime("%Y-%m"),
        "months": months,
        "engine": {
            "name": "tithika-jyotish-timing-timeline",
            "version": ENGINE_VERSION,
            "profile": "monthly-dasha-transit-activation",
            "source_engine": base["engine"],
        },
        "birth_profile": base["birth_profile"],
        "monthly_timeline": rows,
        "activation_windows": merged_windows(rows),
        "yearly_summary": yearly_summary(rows),
        "markers": markers,
        "methodology": {
            "base_component": "55% of the domain's structural evidence index",
            "dasha_component": {
                "Mahadasha": 18,
                "Antardasha": 12,
                "Pratyantardasha": 6,
            },
            "transit_component": {
                "Jupiter": 7,
                "Saturn": 7,
                "Rahu": 5,
                "Ketu": 5,
            },
            "bands": {
                "high": "75-100",
                "elevated": "60-74.9",
                "active": "45-59.9",
                "background": "below 45",
            },
            "sampling": (
                "Each civil month is evaluated at its midpoint. Exact Mahadasha/"
                "Antardasha boundaries and Jupiter/Saturn/Rahu/Ketu sign ingresses "
                "are separately emitted as markers."
            ),
            "meaning": (
                "Activation index is a transparent astrological emphasis score. "
                "It is not an event probability, success rate or certainty measure."
            ),
        },
        "integrity": {
            "months_complete": len(rows) == months,
            "domains_complete": all(
                set(row["domains"]) == set(interpretation.DOMAIN_HOUSES)
                for row in rows
            ),
            "monotonic_months": all(
                rows[i]["month"] < rows[i + 1]["month"]
                for i in range(len(rows) - 1)
            ),
            "source_integrity": base["integrity"],
        },
        "note": (
            "This timeline identifies periods of astrological emphasis from "
            "Vimshottari and slow-transit context. It does not predict guaranteed "
            "events and should not be used as the sole basis for medical, legal, "
            "financial or other high-stakes decisions."
        ),
    }


def main() -> None:
    payload = json.loads(sys.stdin.read() or "{}")
    print(json.dumps(build(payload), ensure_ascii=False))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(json.dumps({
            "ok": False,
            "error": str(exc),
            "code": "JYOTISH_TIMELINE_FAILED",
        }))
        sys.exit(1)
