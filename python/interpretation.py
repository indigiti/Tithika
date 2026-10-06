#!/usr/bin/env python3
"""
Tithika Jyotish interpretation knowledge layer.

This module converts the already-audited unified horoscope evidence into
structured, traceable interpretations. It does not recalculate astronomy and it
does not make deterministic event, health, wealth, longevity or relationship
claims.

Interpretation profile
----------------------
- Functional lordship from whole-sign Lagna.
- Strict Yogakaraka: one lord owns a non-Lagna Kendra (4/7/10) and a Trikona (5/9).
- D1 dignity plus D9/D10 reinforcement using the same exaltation/ownership rules
  already used by Tithika's Yoga engine.
- Shadbala ratio as capacity evidence.
- Sarvashtakavarga as house-context evidence.
- Active Vimshottari lords as timing activation.
- Jupiter/Saturn/Rahu/Ketu transit houses as contextual activation only.
- Every narrative item carries machine-readable evidence.
"""
from __future__ import annotations

import json
import sys

import horoscope_analysis
import yogas

ENGINE_VERSION = "0.1.0"
CLASSICAL = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
SIGN_LORD = horoscope_analysis.SIGN_LORD

KENDRA = {1, 4, 7, 10}
NON_LAGNA_KENDRA = {4, 7, 10}
TRIKONA = {1, 5, 9}
STRICT_TRIKONA = {5, 9}
DUSTHANA = {6, 8, 12}
UPACHAYA = {3, 6, 10, 11}
MARAKA_LINKED = {2, 7}

HOUSE_THEMES = {
    1: "self, body and orientation",
    2: "resources, family and speech",
    3: "initiative, skills and siblings",
    4: "home, foundations and inner security",
    5: "learning, creativity and discernment",
    6: "service, competition and problem-solving",
    7: "partnerships and agreements",
    8: "change, vulnerability and shared matters",
    9: "dharma, mentors and higher learning",
    10: "career, responsibility and public work",
    11: "gains, networks and long-range goals",
    12: "release, retreat and expenditure",
}

DOMAIN_HOUSES = {
    "identity": {1},
    "resources": {2, 11},
    "learning": {5, 9},
    "career": {10},
    "relationships": {7},
}

DOMAIN_YOGA_CATEGORIES = {
    "identity": {"pancha-mahapurusha", "dignity", "lunar", "nabhasa-ashraya"},
    "resources": {"lordship", "gains-affliction", "exchange"},
    "learning": {"lordship", "dignity"},
    "career": {"lordship", "reputation", "pancha-mahapurusha", "exchange"},
    "relationships": {"lordship", "exchange"},
}


def owned_houses(asc_sign: int) -> dict[str, list[int]]:
    rows = {name: [] for name in CLASSICAL}
    for house in range(1, 13):
        sign = (asc_sign + house - 1) % 12
        lord = SIGN_LORD[sign]
        rows[lord].append(house)
    return rows


def functional_role(houses: list[int]) -> dict:
    hs = set(houses)
    yogakaraka = bool(hs & NON_LAGNA_KENDRA) and bool(hs & STRICT_TRIKONA)

    supportive = 0.0
    challenging = 0.0
    if 1 in hs:
        supportive += 1.5
    supportive += 2.0 * len(hs & STRICT_TRIKONA)
    supportive += 0.5 * len(hs & NON_LAGNA_KENDRA)
    challenging += 1.25 * len(hs & DUSTHANA)
    challenging += 0.25 * len(hs & {3, 11})

    if yogakaraka:
        category = "yogakaraka"
        label = "Yogakaraka / high structural support"
    elif supportive >= 2.0 and challenging == 0:
        category = "supportive"
        label = "Functionally supportive"
    elif challenging >= 1.25 and supportive < 1.5:
        category = "challenging"
        label = "Functionally challenging"
    elif supportive > 0 and challenging > 0:
        category = "mixed"
        label = "Mixed functional portfolio"
    else:
        category = "structural"
        label = "Context-dependent / structural"

    flags = []
    if hs & STRICT_TRIKONA:
        flags.append("trikona-lord")
    if hs & NON_LAGNA_KENDRA:
        flags.append("kendra-lord")
    if hs & DUSTHANA:
        flags.append("dusthana-lord")
    if hs & UPACHAYA:
        flags.append("upachaya-lord")
    if hs & MARAKA_LINKED:
        flags.append("2nd/7th-lordship")
    if yogakaraka:
        flags.append("strict-yogakaraka")

    return {
        "category": category,
        "label": label,
        "support_score": round(supportive, 2),
        "challenge_score": round(challenging, 2),
        "flags": flags,
        "note": (
            "2nd/7th lordship is exposed only as a classical structural marker. "
            "Tithika does not use it for mortality or longevity prediction."
        ) if hs & MARAKA_LINKED else None,
    }


def chart_placement(chart: dict, planet: str) -> dict:
    return next((row for row in chart.get("placements", []) if row.get("name") == planet), {})


def dignity_label(planet: str, sign_id: int | None) -> str:
    if sign_id is None:
        return "unknown"
    return yogas.dignity(planet, int(sign_id))


def divisional_confirmation(planet: str, d1: dict, d9: dict, d10: dict) -> dict:
    p1 = chart_placement(d1, planet)
    p9 = chart_placement(d9, planet)
    p10 = chart_placement(d10, planet)
    d1d = dignity_label(planet, p1.get("rashi_id"))
    d9d = dignity_label(planet, p9.get("rashi_id"))
    d10d = dignity_label(planet, p10.get("rashi_id"))

    strong = {"own", "exalted"}
    weak = {"debilitated"}
    if d1d in strong and d9d in strong:
        relation = "reinforced"
        message = "D1 strength is reinforced in D9."
    elif d1d in weak and d9d in strong:
        relation = "navamsha-recovery"
        message = "D1 debility is moderated by stronger D9 dignity evidence."
    elif d1d in strong and d9d in weak:
        relation = "mixed"
        message = "Strong D1 dignity is not repeated in D9."
    elif d1d in weak and d9d in weak:
        relation = "repeated-weakness"
        message = "The dignity challenge repeats across D1 and D9."
    else:
        relation = "neutral"
        message = "D1 and D9 do not create a strong dignity reinforcement signal."

    career_relation = (
        "strong-career-confirmation"
        if d10d in strong
        else "career-dignity-challenge"
        if d10d in weak
        else "career-neutral"
    )

    return {
        "d1": {"rashi": p1.get("rashi"), "house": p1.get("house"), "dignity": d1d},
        "d9": {"rashi": p9.get("rashi"), "house": p9.get("house"), "dignity": d9d},
        "d10": {"rashi": p10.get("rashi"), "house": p10.get("house"), "dignity": d10d},
        "d1_d9_relation": relation,
        "d1_d9_message": message,
        "d10_relation": career_relation,
    }


def planet_narrative(
    planet: str,
    houses: list[int],
    role: dict,
    natal: dict,
    strength: dict,
    confirmation: dict,
    dasha_level: str | None,
) -> str:
    owned = ", ".join(f"H{h}" for h in houses)
    placement = f"H{natal.get('house', '—')} {natal.get('rashi', '—')}"
    dignity = confirmation["d1"]["dignity"]
    ratio = strength.get("ratio")
    capacity = (
        f"Shadbala is {float(ratio):.2f}× the declared requirement"
        if ratio is not None else "Shadbala evidence is unavailable"
    )
    active = (
        f" It is currently activated as the {dasha_level} lord."
        if dasha_level else ""
    )
    return (
        f"{planet} rules {owned} and is classified as {role['label'].lower()}. "
        f"In D1 it occupies {placement} with {dignity} dignity. {capacity}. "
        f"{confirmation['d1_d9_message']}{active}"
    )


def house_reading(
    house: int,
    asc_sign: int,
    ownership: dict[str, list[int]],
    natal_by_name: dict[str, dict],
    strength_by_name: dict[str, dict],
    sav_by_house: dict[int, int],
    confirmations: dict[str, dict],
) -> dict:
    sign = (asc_sign + house - 1) % 12
    lord = SIGN_LORD[sign]
    natal = natal_by_name.get(lord, {})
    strength = strength_by_name.get(lord, {})
    role = functional_role(ownership[lord])
    sav = sav_by_house.get(house)
    confirmation = confirmations[lord]

    evidence = [
        f"H{house} lord: {lord}",
        f"{lord} placed in H{natal.get('house', '—')} {natal.get('rashi', '—')}",
        f"D1 dignity: {confirmation['d1']['dignity']}",
        f"Shadbala ratio: {float(strength.get('ratio', 0)):.2f}×",
        f"SAV support: {sav}",
    ]
    if house == 10:
        evidence.append(
            f"D10 dignity: {confirmation['d10']['dignity']} in H{confirmation['d10']['house']}"
        )
    if house == 7:
        evidence.append(
            f"D9 dignity: {confirmation['d9']['dignity']} in H{confirmation['d9']['house']}"
        )

    return {
        "house": house,
        "theme": HOUSE_THEMES[house],
        "lord": lord,
        "lord_functional_role": role["category"],
        "lord_placement_house": natal.get("house"),
        "lord_rashi": natal.get("rashi"),
        "d1_dignity": confirmation["d1"]["dignity"],
        "d9_dignity": confirmation["d9"]["dignity"],
        "d10_dignity": confirmation["d10"]["dignity"],
        "shadbala_ratio": strength.get("ratio"),
        "sav": sav,
        "evidence": evidence,
        "interpretation": (
            f"The {HOUSE_THEMES[house]} house is ruled by {lord}. "
            f"Its lord is placed in H{natal.get('house', '—')} and has "
            f"{confirmation['d1']['dignity']} D1 dignity. "
            f"Capacity is {float(strength.get('ratio', 0)):.2f}× the declared "
            f"Shadbala requirement, while this house carries {sav} SAV bindus. "
            f"This is contextual evidence, not an event forecast."
        ),
    }


def active_dasha_levels(analysis: dict) -> dict[str, str]:
    rows = {}
    for item in analysis.get("timing", {}).get("active_dasha_lords", []):
        planet = item.get("planet")
        level = item.get("level")
        if planet and level and planet not in rows:
            rows[planet] = level
    return rows


def domain_activation(
    key: str,
    domain: dict,
    ownership: dict[str, list[int]],
    active_dasha: dict[str, str],
    transits: list[dict],
    yogas_rows: list[dict],
) -> dict:
    houses = DOMAIN_HOUSES[key]
    domain_lords = {
        planet
        for planet, owned in ownership.items()
        if set(owned) & houses
    }
    relevant = set(domain.get("relevant_planets", [])) | domain_lords

    dasha_hits = [
        {"planet": planet, "level": level}
        for planet, level in active_dasha.items()
        if planet in relevant
    ]
    transit_hits = [
        row for row in transits
        if row.get("house_from_lagna") in houses or row.get("house_from_moon") in houses
    ]
    yoga_hits = [
        row for row in yogas_rows
        if row.get("category") in DOMAIN_YOGA_CATEGORIES[key]
    ]

    activation_count = len(dasha_hits) + len(transit_hits)
    if activation_count >= 3:
        activation = "high"
    elif activation_count >= 1:
        activation = "active"
    else:
        activation = "background"

    reasons = []
    reasons.extend(
        f"{x['level']} lord {x['planet']} is relevant to this domain"
        for x in dasha_hits
    )
    reasons.extend(
        f"{x['planet']} transit activates H{x['house_from_lagna']} from Lagna / H{x['house_from_moon']} from Moon"
        for x in transit_hits
    )
    if yoga_hits:
        reasons.append(f"{len(yoga_hits)} structural Yoga(s) map to this domain")

    return {
        "activation": activation,
        "dasha_hits": dasha_hits,
        "transit_hits": transit_hits,
        "yoga_hits": [
            {"name": row.get("name"), "category": row.get("category")}
            for row in yoga_hits[:8]
        ],
        "reasons": reasons,
    }


def domain_narrative(key: str, domain: dict, activation: dict) -> str:
    title = domain.get("title", key.title())
    band = domain.get("band", "context-dependent evidence")
    index = float(domain.get("evidence_index", 0))
    active = activation["activation"]
    if activation["reasons"]:
        timing = " Current activation evidence: " + "; ".join(activation["reasons"][:3]) + "."
    else:
        timing = " No major Dasha/transit activation is flagged by this profile at the selected as-of time."
    return (
        f"{title} currently shows {band} (evidence index {index:.0f}/100). "
        f"The timing state is {active}.{timing} "
        "The index is a disclosed evidence summary, not a probability of outcomes."
    )


def build(payload: dict) -> dict:
    analysis = horoscope_analysis.build(payload)
    asc_sign = int(analysis["birth_profile"]["lagna"]["rashi_id"])
    ownership = owned_houses(asc_sign)
    natal_by_name = {row["name"]: row for row in analysis.get("natal_planets", [])}
    strength_by_name = {row["planet"]: row for row in analysis.get("strengths", [])}
    sav_by_house = {
        int(row["house"]): int(row["sav"])
        for row in analysis.get("ashtakavarga", {}).get("rows", [])
    }
    active = active_dasha_levels(analysis)

    confirmations = {
        planet: divisional_confirmation(
            planet,
            analysis["charts"]["D1"],
            analysis["charts"]["D9"],
            analysis["charts"]["D10"],
        )
        for planet in CLASSICAL
    }

    planets = []
    for planet in CLASSICAL:
        role = functional_role(ownership[planet])
        natal = natal_by_name.get(planet, {})
        strength = strength_by_name.get(planet, {})
        dasha_level = active.get(planet)
        planets.append({
            "planet": planet,
            "owned_houses": ownership[planet],
            "functional_role": role,
            "natal": natal,
            "strength": strength,
            "divisional_confirmation": confirmations[planet],
            "active_dasha_level": dasha_level,
            "interpretation": planet_narrative(
                planet,
                ownership[planet],
                role,
                natal,
                strength,
                confirmations[planet],
                dasha_level,
            ),
        })

    key_houses = [1, 2, 4, 5, 7, 9, 10, 11]
    houses = [
        house_reading(
            house,
            asc_sign,
            ownership,
            natal_by_name,
            strength_by_name,
            sav_by_house,
            confirmations,
        )
        for house in key_houses
    ]

    domain_rows = {}
    transits = analysis.get("timing", {}).get("major_transits", [])
    yoga_rows = analysis.get("yogas", {}).get("items", [])
    for key, domain in analysis.get("domains", {}).items():
        activation = domain_activation(
            key,
            domain,
            ownership,
            active,
            transits,
            yoga_rows,
        )
        domain_rows[key] = {
            **domain,
            "activation": activation,
            "interpretation": domain_narrative(key, domain, activation),
        }

    ranked = sorted(
        domain_rows.items(),
        key=lambda item: (
            float(item[1].get("evidence_index", 0)),
            1 if item[1]["activation"]["activation"] == "high" else
            0.5 if item[1]["activation"]["activation"] == "active" else 0,
        ),
        reverse=True,
    )

    current_focus = [
        {
            "key": key,
            "title": row.get("title"),
            "evidence_index": row.get("evidence_index"),
            "activation": row["activation"]["activation"],
        }
        for key, row in ranked
        if row["activation"]["activation"] != "background"
    ][:3]

    return {
        "ok": True,
        "birth_datetime": analysis["birth_datetime"],
        "as_of": analysis["as_of"],
        "location": analysis["location"],
        "engine": {
            "name": "tithika-jyotish-interpretation",
            "version": ENGINE_VERSION,
            "profile": "auditable-rule-based-interpretation",
            "source_engine": analysis["engine"],
        },
        "birth_profile": analysis["birth_profile"],
        "functional_lordship": {
            "lagna_rashi": analysis["birth_profile"]["lagna"]["rashi"],
            "planet_house_ownership": ownership,
            "strict_yogakaraka_rule": "owns one of H4/H7/H10 and one of H5/H9",
        },
        "planet_interpretations": planets,
        "house_interpretations": houses,
        "domain_interpretations": domain_rows,
        "current_focus": current_focus,
        "timing": analysis["timing"],
        "yogas": analysis["yogas"],
        "sensitivity": analysis["sensitivity"],
        "integrity": {
            **analysis["integrity"],
            "planet_interpretations": len(planets) == 7,
            "key_house_interpretations": len(houses) == len(key_houses),
            "domain_interpretations": set(domain_rows) == set(DOMAIN_HOUSES),
        },
        "methodology": [
            "The interpretation layer consumes the unified horoscope engine; it does not recalculate planetary astronomy.",
            "Functional roles are inferred from whole-sign house lordship and exposed with owned houses and rule flags.",
            "Strict Yogakaraka status requires ownership of H4/H7/H10 plus H5/H9.",
            "D1 dignity is cross-checked against D9, with D10 used as career-specific divisional context.",
            "Shadbala is treated as capacity evidence and Sarvashtakavarga as house-context evidence.",
            "Vimshottari and major transits mark activation only; they are not converted into guaranteed events.",
            "2nd/7th lordship is never used for mortality or longevity prediction.",
        ],
        "note": (
            "This is a rule-based Jyotish interpretation layer for explanatory "
            "context. It is not a deterministic prediction engine and should not "
            "be used as the sole basis for medical, legal, financial or other "
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
            "code": "JYOTISH_INTERPRETATION_FAILED",
        }))
        sys.exit(1)
