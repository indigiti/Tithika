#!/usr/bin/env python3
"""
Tithika personalized Rashifal engine.

This layer converts the verified natal interpretation + Vimshottari + transit
stack into period-specific personal forecast context for daily, weekly, monthly
and yearly views.

The engine reports relative astrological emphasis. Scores are disclosed,
auditable synthesis indices, never event probabilities or guaranteed outcomes.
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import horoscope_analysis
import interpretation
import planetary
import timing_timeline
import vimshottari

ENGINE_VERSION = "0.1.0"
MODES = {"overview", "daily", "weekly", "monthly", "yearly"}

TRANSIT_PLANETS = [
    "Moon", "Sun", "Mercury", "Venus", "Mars",
    "Jupiter", "Saturn", "Rahu", "Ketu",
]

MODE_PROFILE = {
    "daily": {
        "base_factor": 0.42,
        "dasha": {"Mahadasha": 16.0, "Antardasha": 12.0, "Pratyantardasha": 7.0},
        "transit": {
            "Moon": 10.0, "Sun": 5.0, "Mercury": 4.0, "Venus": 4.0, "Mars": 4.0,
            "Jupiter": 6.0, "Saturn": 6.0, "Rahu": 4.0, "Ketu": 4.0,
        },
    },
    "weekly": {
        "base_factor": 0.45,
        "dasha": {"Mahadasha": 17.0, "Antardasha": 12.0, "Pratyantardasha": 7.0},
        "transit": {
            "Moon": 7.0, "Sun": 4.0, "Mercury": 3.0, "Venus": 3.0, "Mars": 3.0,
            "Jupiter": 6.0, "Saturn": 6.0, "Rahu": 4.0, "Ketu": 4.0,
        },
    },
    "monthly": {
        "base_factor": 0.50,
        "dasha": {"Mahadasha": 18.0, "Antardasha": 12.0, "Pratyantardasha": 6.0},
        "transit": {
            "Moon": 0.0, "Sun": 3.0, "Mercury": 2.0, "Venus": 2.0, "Mars": 3.0,
            "Jupiter": 7.0, "Saturn": 7.0, "Rahu": 5.0, "Ketu": 5.0,
        },
    },
    "yearly": {
        "base_factor": 0.55,
        "dasha": {"Mahadasha": 18.0, "Antardasha": 12.0, "Pratyantardasha": 6.0},
        "transit": {
            "Moon": 0.0, "Sun": 0.0, "Mercury": 0.0, "Venus": 0.0, "Mars": 2.0,
            "Jupiter": 8.0, "Saturn": 8.0, "Rahu": 5.0, "Ketu": 5.0,
        },
    },
}

BAND_ORDER = {"background": 0, "active": 1, "elevated": 2, "high": 3}


def get_timezone(payload: dict) -> tuple[str, ZoneInfo]:
    name = str(payload.get("timezone") or "Asia/Kolkata")
    try:
        return name, ZoneInfo(name)
    except ZoneInfoNotFoundError:
        return "Asia/Kolkata", ZoneInfo("Asia/Kolkata")


def parse_target(payload: dict, tz: ZoneInfo) -> datetime:
    raw = str(
        payload.get("target_date")
        or payload.get("forecast_date")
        or payload.get("as_of")
        or ""
    ).strip()
    if not raw:
        return datetime.now(tz).replace(hour=12, minute=0, second=0, microsecond=0)
    value = datetime.fromisoformat(raw)
    if value.tzinfo is None:
        value = value.replace(tzinfo=tz)
    else:
        value = value.astimezone(tz)
    return value.replace(hour=12, minute=0, second=0, microsecond=0)


def period_bounds(mode: str, target: datetime) -> tuple[datetime, datetime]:
    if mode == "daily":
        start = target.replace(hour=0, minute=0, second=0, microsecond=0)
        return start, start + timedelta(days=1)

    if mode == "weekly":
        start = (target - timedelta(days=target.weekday())).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        return start, start + timedelta(days=7)

    if mode == "monthly":
        start = target.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        return start, timing_timeline.add_months(start, 1)

    if mode == "yearly":
        start = target.replace(
            month=1, day=1, hour=0, minute=0, second=0, microsecond=0
        )
        return start, start.replace(year=start.year + 1)

    raise ValueError("Unsupported forecast mode")


def period_label(mode: str, start: datetime, end: datetime) -> str:
    if mode == "daily":
        return start.strftime("%A, %d %B %Y")
    if mode == "weekly":
        return f"{start.strftime('%d %b')} – {(end - timedelta(days=1)).strftime('%d %b %Y')}"
    if mode == "monthly":
        return start.strftime("%B %Y")
    if mode == "yearly":
        return str(start.year)
    return ""


def sample_moments(mode: str, start: datetime, end: datetime) -> list[datetime]:
    if mode == "daily":
        return [start + timedelta(hours=12)]

    if mode == "weekly":
        return [start + timedelta(days=i, hours=12) for i in range(7)]

    if mode == "monthly":
        # Daily noon sampling avoids aliasing fast Mercury/Venus/Mars changes
        # and removes the former five-point weekly approximation.
        span = (end - start).days
        return [start + timedelta(days=i, hours=12) for i in range(span)]

    if mode == "yearly":
        rows = []
        for month in range(1, 13):
            rows.append(start.replace(month=month, day=15, hour=12))
        return rows

    raise ValueError("Unsupported forecast mode")


def transit_context(
    moment: datetime,
    node_model: str,
    asc_sign: int,
    moon_sign: int,
) -> list[dict]:
    rows = []
    for name in TRANSIT_PLANETS:
        state = planetary.planet_state(name, moment, node_model)
        rows.append({
            "planet": name,
            "rashi": state["rashi"],
            "rashi_id": state["rashi_id"],
            "retrograde": state["retrograde"],
            "house_from_lagna": horoscope_analysis.house_from(
                asc_sign, state["rashi_id"]
            ),
            "house_from_moon": horoscope_analysis.house_from(
                moon_sign, state["rashi_id"]
            ),
        })
    return rows


def relevant_planets(
    key: str,
    domain: dict,
    ownership: dict[str, list[int]],
) -> set[str]:
    houses = interpretation.DOMAIN_HOUSES[key]
    lords = {
        planet
        for planet, owned in ownership.items()
        if set(owned) & houses
    }
    return set(domain.get("relevant_planets", [])) | lords


def score_band(value: float) -> str:
    if value >= 75:
        return "high"
    if value >= 60:
        return "elevated"
    if value >= 45:
        return "active"
    return "background"


def sample_domain_score(
    mode: str,
    key: str,
    domain: dict,
    ownership: dict[str, list[int]],
    periods: list[dict],
    transits: list[dict],
) -> tuple[float, dict]:
    profile = MODE_PROFILE[mode]
    relevant = relevant_planets(key, domain, ownership)
    houses = interpretation.DOMAIN_HOUSES[key]

    base_points = float(domain.get("evidence_index", 0.0)) * profile["base_factor"]
    dasha_hits = [
        item for item in periods
        if item.get("planet") in relevant
    ]
    dasha_points = sum(
        float(profile["dasha"].get(item["level"], 0.0))
        for item in dasha_hits
    )

    transit_hits = [
        row for row in transits
        if (
            row["house_from_lagna"] in houses
            or row["house_from_moon"] in houses
        )
        and float(profile["transit"].get(row["planet"], 0.0)) > 0
    ]
    transit_points = sum(
        float(profile["transit"].get(row["planet"], 0.0))
        for row in transit_hits
    )

    total = round(min(100.0, base_points + dasha_points + transit_points), 1)
    return total, {
        "band": score_band(total),
        "base_points": round(base_points, 1),
        "dasha_points": round(dasha_points, 1),
        "transit_points": round(transit_points, 1),
        "dasha_hits": [
            {"level": item["level"], "planet": item["planet"]}
            for item in dasha_hits
        ],
        "transit_hits": transit_hits,
    }


def sample_row(
    mode: str,
    moment: datetime,
    base: dict,
    schedule: dict,
    node_model: str,
) -> dict:
    asc_sign = int(base["birth_profile"]["lagna"]["rashi_id"])
    moon_row = next(
        row for row in base["planet_interpretations"]
        if row["planet"] == "Moon"
    )
    moon_sign = int(moon_row["natal"]["rashi_id"])
    ownership = base["functional_lordship"]["planet_house_ownership"]
    roles = {
        row["planet"]: row["functional_role"]["category"]
        for row in base["planet_interpretations"]
    }

    periods = timing_timeline.active_periods(schedule, moment)
    transits = transit_context(moment, node_model, asc_sign, moon_sign)
    domains = {}

    for key, domain in base["domain_interpretations"].items():
        score, evidence = sample_domain_score(
            mode, key, domain, ownership, periods, transits
        )
        quality = timing_timeline.activation_quality(
            key, domain, ownership, periods, roles
        )
        domains[key] = {
            "key": key,
            "title": domain["title"],
            "activation_index": score,
            "band": evidence["band"],
            "quality": quality,
            **evidence,
        }

    ranked = sorted(
        domains.values(),
        key=lambda row: (row["activation_index"], BAND_ORDER[row["band"]]),
        reverse=True,
    )
    return {
        "datetime": moment.isoformat(),
        "date": moment.date().isoformat(),
        "weekday": moment.strftime("%A"),
        "dasha": periods,
        "transits": transits,
        "domains": domains,
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
    }


def aggregate_quality(values: list[str]) -> str:
    found = set(values)
    if "supportive" in found and "challenging" in found:
        return "mixed"
    if "mixed" in found:
        return "mixed"
    if found == {"supportive"}:
        return "supportive"
    if found == {"challenging"}:
        return "challenging"
    counts = Counter(values)
    return counts.most_common(1)[0][0] if counts else "contextual"


def domain_narrative(row: dict, mode: str) -> str:
    title = row["title"]
    score = float(row["activation_index"])
    band = row["band"]
    quality = row["quality"]
    return (
        f"{title} has {band} {mode} emphasis at {score:.0f}/100 with "
        f"{quality} timing context. The score summarizes natal evidence, active "
        "Vimshottari lords and horizon-appropriate transits; it is not an event "
        "probability or guarantee."
    )


def aggregate_period(
    mode: str,
    start: datetime,
    end: datetime,
    samples: list[dict],
) -> dict:
    domains = {}
    for key in interpretation.DOMAIN_HOUSES:
        vals = [float(row["domains"][key]["activation_index"]) for row in samples]
        qualities = [row["domains"][key]["quality"] for row in samples]
        peak_sample = max(samples, key=lambda row: row["domains"][key]["activation_index"])
        base = samples[0]["domains"][key]
        avg = round(sum(vals) / len(vals), 1)
        row = {
            "key": key,
            "title": base["title"],
            "activation_index": avg,
            "band": score_band(avg),
            "quality": aggregate_quality(qualities),
            "minimum_index": round(min(vals), 1),
            "peak_index": round(max(vals), 1),
            "peak_date": peak_sample["date"],
            "average_base_points": round(
                sum(float(x["domains"][key]["base_points"]) for x in samples) / len(samples), 1
            ),
            "average_dasha_points": round(
                sum(float(x["domains"][key]["dasha_points"]) for x in samples) / len(samples), 1
            ),
            "average_transit_points": round(
                sum(float(x["domains"][key]["transit_points"]) for x in samples) / len(samples), 1
            ),
        }
        row["interpretation"] = domain_narrative(row, mode)
        domains[key] = row

    ranked = sorted(
        domains.values(),
        key=lambda row: (row["activation_index"], BAND_ORDER[row["band"]]),
        reverse=True,
    )
    return {
        "mode": mode,
        "start": start.isoformat(),
        "end_exclusive": end.isoformat(),
        "label": period_label(mode, start, end),
        "sample_count": len(samples),
        "domains": domains,
        "top_focus": ranked[:3],
        "samples": samples,
    }


def period_markers(
    schedule: dict,
    start: datetime,
    end: datetime,
    node_model: str,
) -> list[dict]:
    rows = timing_timeline.dasha_markers(schedule, start, end)
    rows.extend(timing_timeline.transit_markers(start, end, node_model))
    rows.sort(key=lambda row: row["datetime"])
    return rows


def build_period(
    mode: str,
    target: datetime,
    base: dict,
    schedule: dict,
    node_model: str,
    include_markers: bool = True,
) -> dict:
    start, end = period_bounds(mode, target)
    samples = [
        sample_row(mode, moment, base, schedule, node_model)
        for moment in sample_moments(mode, start, end)
    ]
    result = aggregate_period(mode, start, end, samples)
    result["markers"] = (
        period_markers(schedule, start, end, node_model)
        if include_markers else []
    )
    return result


def build(payload: dict) -> dict:
    mode = str(payload.get("mode") or "overview").lower()
    if mode not in MODES:
        raise ValueError("mode must be overview, daily, weekly, monthly or yearly")

    timezone_name, tz = get_timezone(payload)
    target = parse_target(payload, tz)
    node_model = str(payload.get("node_model") or "mean").lower()
    if node_model not in ("mean", "true"):
        raise ValueError("node_model must be mean or true")

    base_payload = {
        **payload,
        "timezone": timezone_name,
        "node_model": node_model,
        "as_of": target.isoformat(),
    }
    base = interpretation.build(base_payload)
    birth = datetime.fromisoformat(base["birth_datetime"])
    if target.date() < birth.date():
        raise ValueError("Forecast target cannot precede the birth date")

    schedule = vimshottari.calculate(birth, target)

    if mode == "overview":
        periods = {
            item: build_period(
                item, target, base, schedule, node_model, include_markers=False
            )
            for item in ("daily", "weekly", "monthly", "yearly")
        }
        primary = periods["daily"]
    else:
        periods = {mode: build_period(mode, target, base, schedule, node_model)}
        primary = periods[mode]

    current_sample = sample_row("daily", target, base, schedule, node_model)
    active_dasha = current_sample["dasha"]
    slow_transits = [
        row for row in current_sample["transits"]
        if row["planet"] in timing_timeline.TIMING_PLANETS
    ]

    return {
        "ok": True,
        "mode": mode,
        "target_date": target.date().isoformat(),
        "birth_datetime": base["birth_datetime"],
        "location": base["location"],
        "engine": {
            "name": "tithika-personal-rashifal",
            "version": ENGINE_VERSION,
            "profile": "birth-chart-dasha-transit-period-forecast",
            "source_engine": base["engine"],
        },
        "birth_profile": base["birth_profile"],
        "current_context": {
            "active_dasha": active_dasha,
            "slow_transits": slow_transits,
        },
        "periods": periods,
        "primary": {
            "mode": primary["mode"],
            "label": primary["label"],
            "top_focus": primary["top_focus"],
        },
        "methodology": {
            "daily": MODE_PROFILE["daily"],
            "weekly": MODE_PROFILE["weekly"],
            "monthly": MODE_PROFILE["monthly"],
            "yearly": MODE_PROFILE["yearly"],
            "sampling": {
                "daily": "one local-noon sample",
                "weekly": "seven local-noon daily samples",
                "monthly": "one local-noon sample for every civil day in the month",
                "yearly": "one midpoint sample for each month",
            },
            "meaning": (
                "Every 0–100 value is a disclosed emphasis index combining natal "
                "structural evidence, Vimshottari activation and horizon-appropriate "
                "transit houses. It is not a probability of events."
            ),
        },
        "integrity": {
            "source_integrity": base["integrity"],
            "periods_complete": all(
                set(period["domains"]) == set(interpretation.DOMAIN_HOUSES)
                and len(period["top_focus"]) == 3
                for period in periods.values()
            ),
            "scores_bounded": all(
                0 <= float(domain["activation_index"]) <= 100
                for period in periods.values()
                for domain in period["domains"].values()
            ),
        },
        "note": (
            "Personalized Rashifal is an interpretive astrology view of relative "
            "period emphasis. It does not predict guaranteed events and should "
            "not be used as the sole basis for medical, legal, financial or other "
            "high-stakes decisions."
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
            "code": "PERSONAL_RASHIFAL_FAILED",
        }))
        sys.exit(1)