#!/usr/bin/env python3
"""
Tithika unified Jyotish horoscope analysis.

This layer composes already-verified calculation engines into one auditable
birth-chart report. It does not replace the underlying engines and it does not
claim deterministic real-world prediction.

Inputs:
- birth date/time/location
- node model (mean or true)
- optional as_of date/time for the current Dasha/transit context

Outputs:
- D1, D9 and D10 charts
- birth Panchang
- Shadbala summary
- Sarvashtakavarga house support
- structural Yogas
- current Vimshottari timing
- current Jupiter/Saturn/Rahu/Ketu transit houses
- transparent domain evidence indices
"""
from __future__ import annotations

import json
import sys
from datetime import datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import aspects
import ashtakavarga
import lagna
import panchang
import planetary
import shadbala
import vargas
import vimshottari
import yogas

ENGINE_VERSION = "0.1.0"
CLASSICAL = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
TIMING_TRANSITS = ["Jupiter", "Saturn", "Rahu", "Ketu"]
SIGN_LORD = [
    "Mars", "Venus", "Mercury", "Moon", "Sun", "Mercury",
    "Venus", "Mars", "Jupiter", "Saturn", "Saturn", "Jupiter",
]

DOMAIN_PROFILES = {
    "identity": {
        "title": "Identity & temperament",
        "houses": [1],
        "planets": ["Sun", "Moon"],
        "description": "Lagna, luminaries and first-house support.",
    },
    "resources": {
        "title": "Resources & gains",
        "houses": [2, 11],
        "planets": ["Jupiter", "Venus", "Mercury"],
        "description": "Second/eleventh houses with resource significators.",
    },
    "learning": {
        "title": "Learning & dharma",
        "houses": [5, 9],
        "planets": ["Mercury", "Jupiter"],
        "description": "Fifth/ninth houses with knowledge significators.",
    },
    "career": {
        "title": "Career & public work",
        "houses": [10],
        "planets": ["Sun", "Saturn", "Mercury", "Jupiter"],
        "description": "Tenth house, its lord and work significators.",
    },
    "relationships": {
        "title": "Relationships",
        "houses": [7],
        "planets": ["Venus", "Jupiter"],
        "description": "Seventh house, its lord and relationship significators.",
    },
}


def parse_birth(payload: dict, tz: ZoneInfo) -> datetime:
    text = str(payload.get("datetime") or "").strip()
    if not text:
        date_text = payload.get("date") or datetime.now(tz).strftime("%Y-%m-%d")
        time_text = payload.get("time") or "12:00:00"
        text = f"{date_text}T{time_text}"
    value = datetime.fromisoformat(text)
    return value.replace(tzinfo=tz) if value.tzinfo is None else value.astimezone(tz)


def parse_as_of(payload: dict, tz: ZoneInfo) -> datetime:
    text = str(payload.get("as_of") or "").strip()
    if not text:
        return datetime.now(tz)
    value = datetime.fromisoformat(text)
    return value.replace(tzinfo=tz) if value.tzinfo is None else value.astimezone(tz)


def house_from(reference_sign: int, target_sign: int) -> int:
    return ((target_sign - reference_sign) % 12) + 1


def ashtakavarga_snapshot(asc: dict, states: dict[str, dict]) -> dict:
    positions = {name: states[name]["rashi_id"] for name in CLASSICAL}
    positions["Lagna"] = asc["lagna_id"]
    bav = {}
    sav = [0] * 12
    checks = {}

    for target in CLASSICAL:
        scores, contributors = ashtakavarga.make_bav(
            ashtakavarga.TABLES[target], positions
        )
        total = sum(scores)
        expected = ashtakavarga.EXPECTED[target]
        checks[target] = {
            "total": total,
            "expected": expected,
            "valid": total == expected,
        }
        bav[target] = {
            "scores": scores,
            "total": total,
            "contributors": contributors,
        }
        sav = [sav[i] + scores[i] for i in range(12)]

    rows = [
        {
            "rashi_id": sign_id,
            "rashi": panchang.RASHI_NAMES[sign_id],
            "house": house_from(asc["lagna_id"], sign_id),
            "sav": sav[sign_id],
        }
        for sign_id in range(12)
    ]
    rows.sort(key=lambda row: row["house"])
    valid = all(row["valid"] for row in checks.values()) and sum(sav) == 337
    return {
        "rows": rows,
        "sav_total": sum(sav),
        "integrity_valid": valid,
        "bav_totals": {name: bav[name]["total"] for name in CLASSICAL},
    }


def current_and_upcoming_dasha(result: dict, as_of: datetime) -> dict:
    current = result.get("current")
    upcoming = []
    for row in result.get("mahadasha", []):
        end = datetime.fromisoformat(row["full_end"])
        if end > as_of:
            upcoming.append({
                "lord": row["lord"],
                "start": row["start"],
                "end": row["end"],
            })
        if len(upcoming) >= 3:
            break
    return {
        "starting_lord": result.get("starting_lord"),
        "birth_nakshatra": result.get("nakshatra"),
        "birth_nakshatra_pada": result.get("nakshatra_pada"),
        "birth_balance_years": result.get("birth_balance_years"),
        "current": current,
        "upcoming_mahadasha": upcoming,
    }


def evidence_index(
    profile: dict,
    asc_sign: int,
    shadbala_rows: dict[str, dict],
    sav_by_house: dict[int, int],
) -> dict:
    lords = []
    for house in profile["houses"]:
        sign = (asc_sign + house - 1) % 12
        lords.append(SIGN_LORD[sign])

    relevant = list(dict.fromkeys(profile["planets"] + lords))
    ratios = [
        float(shadbala_rows[name]["ratio"])
        for name in relevant
        if name in shadbala_rows
    ]
    capacity = (
        sum(min(1.5, max(0.0, ratio)) for ratio in ratios)
        / (len(ratios) * 1.5)
        * 100.0
        if ratios else 0.0
    )

    sav_values = [sav_by_house.get(house, 0) for house in profile["houses"]]
    sav_context = (
        sum(min(40.0, max(0.0, float(value))) for value in sav_values)
        / (len(sav_values) * 40.0)
        * 100.0
        if sav_values else 0.0
    )
    index = round(capacity * 0.60 + sav_context * 0.40, 1)

    if index >= 70:
        band = "stronger supporting evidence"
    elif index >= 45:
        band = "mixed / moderate evidence"
    else:
        band = "context-sensitive evidence"

    return {
        "title": profile["title"],
        "description": profile["description"],
        "houses": profile["houses"],
        "house_lords": lords,
        "relevant_planets": relevant,
        "planetary_capacity_pct": round(capacity, 1),
        "sav_context_pct": round(sav_context, 1),
        "evidence_index": index,
        "band": band,
        "strength_ratios": {
            name: shadbala_rows[name]["ratio"]
            for name in relevant
            if name in shadbala_rows
        },
        "sav_by_house": {str(house): sav_by_house.get(house, 0) for house in profile["houses"]},
        "method": "60% normalized Shadbala ratio + 40% normalized SAV house support",
    }


def timing_context(
    dasha: dict,
    natal_by_name: dict[str, dict],
    strength_by_name: dict[str, dict],
    transit_states: dict[str, dict],
    asc_sign: int,
    moon_sign: int,
) -> dict:
    current = dasha.get("current") or {}
    maha = (current.get("mahadasha") or {}).get("lord")
    antar = (current.get("antardasha") or {}).get("lord")
    pratyantar = (
        ((current.get("antardasha") or {}).get("current_pratyantardasha") or {})
        .get("lord")
    )

    active = []
    for level, name in (
        ("Mahadasha", maha),
        ("Antardasha", antar),
        ("Pratyantardasha", pratyantar),
    ):
        if not name:
            continue
        natal = natal_by_name.get(name, {})
        strength = strength_by_name.get(name, {})
        active.append({
            "level": level,
            "planet": name,
            "natal_house": natal.get("house"),
            "natal_rashi": natal.get("rashi"),
            "strength_ratio": strength.get("ratio"),
        })

    transits = []
    for name in TIMING_TRANSITS:
        state = transit_states[name]
        transits.append({
            "planet": name,
            "rashi": state["rashi"],
            "retrograde": state["retrograde"],
            "house_from_lagna": house_from(asc_sign, state["rashi_id"]),
            "house_from_moon": house_from(moon_sign, state["rashi_id"]),
        })

    return {
        "active_dasha_lords": active,
        "major_transits": transits,
        "interpretation_rule": (
            "Timing context reports active Vimshottari lords with natal strength "
            "and current Jupiter/Saturn/Rahu/Ketu houses. It does not convert "
            "these factors into deterministic event predictions."
        ),
    }


def build(payload: dict) -> dict:
    lat = float(payload.get("lat", 19.0760))
    lon = float(payload.get("lon", 72.8777))
    if not (-89.999 <= lat <= 89.999 and -180 <= lon <= 180):
        raise ValueError("Invalid latitude/longitude")

    timezone_name = payload.get("timezone") or "Asia/Kolkata"
    try:
        tz = ZoneInfo(timezone_name)
    except ZoneInfoNotFoundError:
        timezone_name = "Asia/Kolkata"
        tz = ZoneInfo(timezone_name)

    birth = parse_birth(payload, tz)
    as_of = parse_as_of(payload, tz)
    node_model = str(payload.get("node_model") or "mean").lower()
    if node_model not in ("mean", "true"):
        raise ValueError("node_model must be mean or true")

    asc = lagna.lagna_state(birth, lat, lon)
    states_list = planetary.positions(birth, False, node_model)
    states = {row["name"]: row for row in states_list}
    charts = {
        "D1": vargas.chart_for(1, asc["sidereal_longitude"], states_list),
        "D9": vargas.chart_for(9, asc["sidereal_longitude"], states_list),
        "D10": vargas.chart_for(10, asc["sidereal_longitude"], states_list),
    }

    birth_state = panchang.state_at(birth)
    lunar_month = panchang.lunar_month_info(birth, birth_state)
    strengths_full = shadbala.calculate({
        **payload,
        "datetime": birth.isoformat(),
        "timezone": timezone_name,
    })
    strength_by_name = {
        row["planet"]: row for row in strengths_full.get("planets", [])
    }
    yoga_full = yogas.build({
        **payload,
        "datetime": birth.isoformat(),
        "timezone": timezone_name,
    })
    ashta = ashtakavarga_snapshot(asc, states)
    dasha_full = vimshottari.calculate(birth, as_of)
    dasha = current_and_upcoming_dasha(dasha_full, as_of)

    natal_rows = []
    natal_by_name = {}
    for row in states_list:
        item = {
            "name": row["name"],
            "rashi": row["rashi"],
            "rashi_id": row["rashi_id"],
            "house": house_from(asc["lagna_id"], row["rashi_id"]),
            "degree_in_rashi": row["degree_in_rashi"],
            "nakshatra": row["nakshatra"],
            "pada": row["pada"],
            "retrograde": row["retrograde"],
            "combust": row["combust"],
        }
        natal_rows.append(item)
        natal_by_name[item["name"]] = item

    transit_states = {
        name: planetary.planet_state(name, as_of, node_model)
        for name in TIMING_TRANSITS
    }
    sav_by_house = {row["house"]: row["sav"] for row in ashta["rows"]}
    domains = {
        key: evidence_index(profile, asc["lagna_id"], strength_by_name, sav_by_house)
        for key, profile in DOMAIN_PROFILES.items()
    }

    varga_margin = min(
        charts["D9"]["minimum_boundary_margin_deg"],
        charts["D10"]["minimum_boundary_margin_deg"],
    )
    sensitivity = (
        "high"
        if varga_margin < 0.10
        else "moderate"
        if varga_margin < 0.25
        else "normal"
    )

    return {
        "ok": True,
        "birth_datetime": birth.isoformat(),
        "as_of": as_of.isoformat(),
        "location": {
            "city": str(payload.get("city") or "Current location")[:120],
            "lat": lat,
            "lon": lon,
            "timezone": timezone_name,
        },
        "engine": {
            "name": "tithika-horoscope-analysis",
            "version": ENGINE_VERSION,
            "profile": "evidence-first-composite",
            "ayanamsha": "Lahiri / Chitrapaksha",
            "house_system": "whole-sign",
            "node_model": node_model,
        },
        "birth_profile": {
            "lagna": {
                "rashi": asc["lagna"],
                "rashi_id": asc["lagna_id"],
                "degree_in_rashi": asc["degree_in_sign"],
            },
            "tithi": birth_state["tithi"],
            "paksha": birth_state["paksha"],
            "nakshatra": birth_state["nakshatra"],
            "nakshatra_pada": birth_state["nakshatra_pada"],
            "yoga": birth_state["yoga"],
            "karana": birth_state["karana"],
            "moon_rashi": birth_state["moon_rashi"],
            "sun_rashi": birth_state["sun_rashi"],
            "amanta_month": lunar_month.get("amanta"),
            "purnimanta_month": lunar_month.get("purnimanta"),
        },
        "natal_planets": natal_rows,
        "charts": charts,
        "strengths": [
            {
                "planet": row["planet"],
                "rashi": row["rashi"],
                "house": row["house"],
                "total_rupa": row["total_rupa"],
                "required_rupa": row["required_rupa"],
                "ratio": row["ratio"],
                "meets_required": row["meets_required"],
            }
            for row in strengths_full.get("planets", [])
        ],
        "ashtakavarga": ashta,
        "yogas": {
            "count": yoga_full.get("count", 0),
            "category_counts": yoga_full.get("category_counts", {}),
            "items": yoga_full.get("yogas", []),
        },
        "dasha": dasha,
        "timing": timing_context(
            dasha,
            natal_by_name,
            strength_by_name,
            transit_states,
            asc["lagna_id"],
            states["Moon"]["rashi_id"],
        ),
        "domains": domains,
        "angular_aspects": aspects.snapshot(birth),
        "graha_yuddha": aspects.graha_yuddha_snapshot(birth),
        "sensitivity": {
            "varga_boundary_margin_deg": round(varga_margin, 8),
            "level": sensitivity,
            "note": (
                "D9/D10 are birth-time sensitive. Review birth-time accuracy when "
                "the nearest divisional boundary margin is small."
            ),
        },
        "integrity": {
            "ashtakavarga": ashta["integrity_valid"],
            "shadbala_planets": len(strengths_full.get("planets", [])) == 7,
            "charts": all(key in charts for key in ("D1", "D9", "D10")),
        },
        "methodology": [
            "All astronomy and natal positions come from the existing Tithika Lahiri engine.",
            "Domain evidence indices are comparative summaries, not probabilities or guarantees.",
            "Shadbala measures capacity; it does not by itself classify a planet as beneficial or harmful.",
            "Sarvashtakavarga house support is used as contextual evidence, not as a standalone prediction.",
            "Yoga output is the curated structural detector and is intentionally not exhaustive.",
            "Current timing combines Vimshottari activation with transit-house context without asserting inevitable events.",
        ],
        "note": (
            "This report is an auditable Jyotish synthesis layer. It summarizes "
            "classical calculation evidence and timing context; it does not make "
            "deterministic claims about health, wealth, relationships or life events."
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
            "code": "HOROSCOPE_ANALYSIS_FAILED",
        }))
        sys.exit(1)
