#!/usr/bin/env python3
"""
Tithika deep marriage analysis.

This layer intentionally does NOT create a second compatibility score.
It exposes independent evidence from:
- D1 seventh house and seventh lord.
- D9/Navamsha Lagna, seventh house/lord and key Grahas.
- Venus/Jupiter structural comparison.
- Mangal Dosha cancellation evidence and mutual-Manglik matching.
- Overlapping Vimshottari periods where marriage-significator lords are active.

The rule profile is explicit so disputed lineage-specific interpretations are
not silently mixed into the Ashtakoota 36-point result.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import doshas
import kundali
import lagna
import panchang
import planetary
import vimshottari

ENGINE_VERSION = "0.1.0"

SIGN_LORDS = [
    "Mars", "Venus", "Mercury", "Moon", "Sun", "Mercury",
    "Venus", "Mars", "Jupiter", "Saturn", "Saturn", "Jupiter"
]

NATURAL = {
    "Sun": {"Moon":"friend","Mars":"friend","Jupiter":"friend","Mercury":"neutral","Venus":"enemy","Saturn":"enemy"},
    "Moon": {"Sun":"friend","Mercury":"friend","Mars":"neutral","Jupiter":"neutral","Venus":"neutral","Saturn":"neutral"},
    "Mars": {"Sun":"friend","Moon":"friend","Jupiter":"friend","Mercury":"enemy","Venus":"neutral","Saturn":"neutral"},
    "Mercury": {"Sun":"friend","Venus":"friend","Moon":"enemy","Mars":"neutral","Jupiter":"neutral","Saturn":"neutral"},
    "Jupiter": {"Sun":"friend","Moon":"friend","Mars":"friend","Mercury":"enemy","Venus":"enemy","Saturn":"neutral"},
    "Venus": {"Mercury":"friend","Saturn":"friend","Sun":"enemy","Moon":"enemy","Mars":"neutral","Jupiter":"neutral"},
    "Saturn": {"Mercury":"friend","Venus":"friend","Sun":"enemy","Moon":"enemy","Mars":"neutral","Jupiter":"neutral"},
}

KEY_PLANETS = ["Sun","Moon","Mars","Mercury","Jupiter","Venus","Saturn","Rahu","Ketu"]


def parse_birth(profile: dict) -> tuple[datetime, ZoneInfo, str]:
    tzname = str(profile.get("timezone") or "Asia/Kolkata")
    try:
        tz = ZoneInfo(tzname)
    except ZoneInfoNotFoundError:
        tzname = "Asia/Kolkata"
        tz = ZoneInfo(tzname)

    text = str(profile.get("datetime") or "").strip()
    if not text:
        date_text = profile.get("date") or datetime.now(tz).strftime("%Y-%m-%d")
        time_text = profile.get("time") or "12:00:00"
        text = f"{date_text}T{time_text}"

    birth = datetime.fromisoformat(text)
    if birth.tzinfo is None:
        birth = birth.replace(tzinfo=tz)
    else:
        birth = birth.astimezone(tz)
    return birth, tz, tzname


def natural_relation(a: str, b: str) -> str:
    if a == b:
        return "same-lord"
    return NATURAL.get(a, {}).get(b, "neutral")


def whole_sign_house(sign_id: int, lagna_id: int) -> int:
    return ((sign_id - lagna_id) % 12) + 1


def find_placement(placements: list[dict], name: str) -> dict:
    return next(row for row in placements if row["name"] == name)


def sign_relation(a: int, b: int) -> dict:
    forward = ((b - a) % 12) + 1
    reverse = ((a - b) % 12) + 1
    pair = tuple(sorted((forward, reverse)))
    label = {
        (1,1): "same-sign",
        (2,12): "2/12",
        (3,11): "3/11",
        (4,10): "4/10",
        (5,9): "5/9",
        (6,8): "6/8",
        (7,7): "7/7",
    }.get(pair, f"{pair[0]}/{pair[1]}")
    return {"forward":forward, "reverse":reverse, "pair":list(pair), "label":label}


def build_profile(profile: dict, as_of: datetime) -> dict:
    birth, tz, tzname = parse_birth(profile)
    lat = float(profile.get("lat", 19.0760))
    lon = float(profile.get("lon", 72.8777))
    if not (-89.999 <= lat <= 89.999 and -180 <= lon <= 180):
        raise ValueError("Invalid latitude/longitude")

    asc = lagna.lagna_state(birth, lat, lon)
    d1 = []
    d9 = []
    states = {}
    for name in KEY_PLANETS:
        st = planetary.planet_state(name, birth)
        states[name] = st
        d1.append({
            "name": name,
            "rashi_id": st["rashi_id"],
            "rashi": st["rashi"],
            "degree_in_rashi": st["degree_in_rashi"],
            "house": whole_sign_house(st["rashi_id"], asc["lagna_id"]),
            "retrograde": st["retrograde"],
            "combust": st["combust"],
        })
        nav = kundali.navamsha_sign(st["longitude"])
        d9.append({
            "name": name,
            "rashi_id": nav["rashi_id"],
            "rashi": nav["rashi"],
            "degree_in_rashi": nav["degree_in_rashi"],
            "retrograde": st["retrograde"],
        })

    d9_lagna = kundali.navamsha_sign(asc["sidereal_longitude"])
    for row in d9:
        row["house"] = whole_sign_house(row["rashi_id"], d9_lagna["rashi_id"])

    seventh_sign = (asc["lagna_id"] + 6) % 12
    seventh_lord = SIGN_LORDS[seventh_sign]
    seventh_lord_row = find_placement(d1, seventh_lord)
    lagna_lord = SIGN_LORDS[asc["lagna_id"]]

    d9_seventh_sign = (d9_lagna["rashi_id"] + 6) % 12
    d9_seventh_lord = SIGN_LORDS[d9_seventh_sign]
    d9_seventh_lord_row = find_placement(d9, d9_seventh_lord)
    d9_lagna_lord = SIGN_LORDS[d9_lagna["rashi_id"]]

    seventh_occupants = [x for x in d1 if x["house"] == 7]
    d9_seventh_occupants = [x for x in d9 if x["house"] == 7]

    venus = find_placement(d1, "Venus")
    jupiter = find_placement(d1, "Jupiter")
    venus_d9 = find_placement(d9, "Venus")
    jupiter_d9 = find_placement(d9, "Jupiter")

    mangal = doshas.mangal(birth, lat, lon, "mean")
    dasha = vimshottari.calculate(birth, as_of)

    return {
        "name": str(profile.get("name") or "")[:120],
        "birth_datetime": birth.isoformat(),
        "location": {
            "city": str(profile.get("city") or "Current location")[:120],
            "lat": lat, "lon": lon, "timezone": tzname,
        },
        "lagna": {
            "rashi_id": asc["lagna_id"],
            "rashi": asc["lagna"],
            "degree_in_rashi": asc["degree_in_sign"],
            "lord": lagna_lord,
        },
        "d1": {
            "seventh_sign_id": seventh_sign,
            "seventh_sign": panchang.RASHI_NAMES[seventh_sign],
            "seventh_lord": seventh_lord,
            "seventh_lord_house": seventh_lord_row["house"],
            "seventh_lord_rashi": seventh_lord_row["rashi"],
            "seventh_occupants": seventh_occupants,
            "lagna_lord_relation_to_seventh_lord": natural_relation(lagna_lord, seventh_lord),
            "placements": d1,
        },
        "d9": {
            "lagna": {
                "rashi_id": d9_lagna["rashi_id"],
                "rashi": d9_lagna["rashi"],
                "degree_in_rashi": d9_lagna["degree_in_rashi"],
                "lord": d9_lagna_lord,
            },
            "seventh_sign_id": d9_seventh_sign,
            "seventh_sign": panchang.RASHI_NAMES[d9_seventh_sign],
            "seventh_lord": d9_seventh_lord,
            "seventh_lord_house": d9_seventh_lord_row["house"],
            "seventh_lord_rashi": d9_seventh_lord_row["rashi"],
            "seventh_occupants": d9_seventh_occupants,
            "placements": d9,
        },
        "significators": {
            "venus": venus,
            "jupiter": jupiter,
            "venus_d9": venus_d9,
            "jupiter_d9": jupiter_d9,
        },
        "mangal": mangal,
        "_birth": birth,
        "_dasha": dasha,
    }


def compact_profile(row: dict) -> dict:
    return {k:v for k,v in row.items() if not k.startswith("_")}


def dasha_candidate_intervals(profile: dict, start: datetime, end: datetime) -> list[dict]:
    marriage_lords = {
        profile["d1"]["seventh_lord"],
        profile["d9"]["seventh_lord"],
        "Venus",
        "Jupiter",
    }
    rows = []
    for md in profile["_dasha"]["mahadasha"]:
        mstart = datetime.fromisoformat(md["full_start"])
        mend = datetime.fromisoformat(md["full_end"])
        if mend <= start or mstart >= end:
            continue
        for ad in md["antardasha"]:
            astart = datetime.fromisoformat(ad["full_start"])
            aend = datetime.fromisoformat(ad["full_end"])
            if aend <= start or astart >= end:
                continue
            md_hit = md["lord"] in marriage_lords
            ad_hit = ad["lord"] in marriage_lords
            if not (md_hit or ad_hit):
                continue
            rows.append({
                "start": max(astart, start),
                "end": min(aend, end),
                "mahadasha": md["lord"],
                "antardasha": ad["lord"],
                "strength": 2 if md_hit and ad_hit else 1,
                "active_significators": [
                    x for x in (md["lord"], ad["lord"]) if x in marriage_lords
                ],
            })
    return rows


def overlap_windows(a: dict, b: dict, start: datetime, end: datetime) -> list[dict]:
    aa = dasha_candidate_intervals(a, start, end)
    bb = dasha_candidate_intervals(b, start, end)
    out = []
    for x in aa:
        for y in bb:
            s = max(x["start"], y["start"])
            e = min(x["end"], y["end"])
            if e <= s:
                continue
            out.append({
                "start": s.isoformat(),
                "end": e.isoformat(),
                "duration_days": round((e-s).total_seconds()/86400.0, 2),
                "groom": {
                    "mahadasha": x["mahadasha"], "antardasha": x["antardasha"],
                    "strength": x["strength"], "active_significators": x["active_significators"],
                },
                "bride": {
                    "mahadasha": y["mahadasha"], "antardasha": y["antardasha"],
                    "strength": y["strength"], "active_significators": y["active_significators"],
                },
                "combined_strength": x["strength"] + y["strength"],
            })
    out.sort(key=lambda r: (-r["combined_strength"], r["start"]))
    # Remove exact duplicates caused by adjacent source intervals.
    dedup = []
    seen = set()
    for row in out:
        key = (row["start"], row["end"], row["groom"]["mahadasha"], row["groom"]["antardasha"], row["bride"]["mahadasha"], row["bride"]["antardasha"])
        if key not in seen:
            seen.add(key); dedup.append(row)
    return dedup[:24]


def pair_factors(groom: dict, bride: dict) -> dict:
    g7 = groom["d1"]["seventh_lord"]
    b7 = bride["d1"]["seventh_lord"]
    gd97 = groom["d9"]["seventh_lord"]
    bd97 = bride["d9"]["seventh_lord"]

    gv = groom["significators"]["venus"]
    bv = bride["significators"]["venus"]
    gj = groom["significators"]["jupiter"]
    bj = bride["significators"]["jupiter"]

    return {
        "seventh_lords": {
            "groom": g7, "bride": b7,
            "groom_to_bride_relation": natural_relation(g7, b7),
            "bride_to_groom_relation": natural_relation(b7, g7),
            "sign_relation": sign_relation(
                find_placement(groom["d1"]["placements"], g7)["rashi_id"],
                find_placement(bride["d1"]["placements"], b7)["rashi_id"],
            ),
        },
        "d9_seventh_lords": {
            "groom": gd97, "bride": bd97,
            "groom_to_bride_relation": natural_relation(gd97, bd97),
            "bride_to_groom_relation": natural_relation(bd97, gd97),
        },
        "d9_lagna": sign_relation(
            groom["d9"]["lagna"]["rashi_id"], bride["d9"]["lagna"]["rashi_id"]
        ),
        "venus": {
            "sign_relation": sign_relation(gv["rashi_id"], bv["rashi_id"]),
            "groom": {"rashi":gv["rashi"],"house":gv["house"]},
            "bride": {"rashi":bv["rashi"],"house":bv["house"]},
            "d9_sign_relation": sign_relation(
                groom["significators"]["venus_d9"]["rashi_id"],
                bride["significators"]["venus_d9"]["rashi_id"],
            ),
        },
        "jupiter": {
            "sign_relation": sign_relation(gj["rashi_id"], bj["rashi_id"]),
            "groom": {"rashi":gj["rashi"],"house":gj["house"]},
            "bride": {"rashi":bj["rashi"],"house":bj["house"]},
            "d9_sign_relation": sign_relation(
                groom["significators"]["jupiter_d9"]["rashi_id"],
                bride["significators"]["jupiter_d9"]["rashi_id"],
            ),
        },
    }


def mangal_pair(groom: dict, bride: dict) -> dict:
    gb = bool(groom["mangal"]["present"])
    bb = bool(bride["mangal"]["present"])
    mutual = gb and bb
    ge = bool(groom["mangal"].get("effective_present", gb))
    be = bool(bride["mangal"].get("effective_present", bb))

    pair_evidence = []
    if mutual:
        pair_evidence.append({
            "rule":"mutual-manglik",
            "strength":"strong",
            "description":"Both birth charts satisfy the base Mangal Dosha rule; mutual-Manglik cancellation is shown as pair-level evidence."
        })

    return {
        "groom_base": gb, "bride_base": bb,
        "groom_effective_after_profile": ge,
        "bride_effective_after_profile": be,
        "mutual_manglik": mutual,
        "pair_cancellation_evidence": pair_evidence,
        "effective_mismatch": ge != be and not mutual,
        "note":"Mangal cancellation traditions vary. Tithika applies only the stated conservative chart-level rules plus mutual-Manglik pair evidence; other regional exceptions remain un-applied."
    }


def analyze_profiles(groom_input: dict, bride_input: dict, as_of: datetime, horizon_years: int = 12) -> dict:
    groom = build_profile(groom_input, as_of)
    bride = build_profile(bride_input, as_of)
    horizon_years = max(1, min(30, int(horizon_years)))
    end = as_of + timedelta(days=365.25*horizon_years)

    return {
        "groom": compact_profile(groom),
        "bride": compact_profile(bride),
        "pair": pair_factors(groom, bride),
        "mangal": mangal_pair(groom, bride),
        "dasha_overlap": {
            "from": as_of.isoformat(),
            "to": end.isoformat(),
            "horizon_years": horizon_years,
            "rule": "candidate when Mahadasha or Antardasha lord is D1 seventh lord, D9 seventh lord, Venus or Jupiter",
            "windows": overlap_windows(groom, bride, as_of, end),
        },
        "disclaimer":"This is a transparent traditional Jyotish comparison layer, not a deterministic prediction of marriage quality or timing. No additional compatibility score is generated."
    }


def main():
    payload = json.loads(sys.stdin.read() or "{}")
    as_of_text = str(payload.get("as_of") or "").strip()
    if as_of_text:
        as_of = datetime.fromisoformat(as_of_text)
        if as_of.tzinfo is None:
            as_of = as_of.replace(tzinfo=ZoneInfo("Asia/Kolkata"))
    else:
        as_of = datetime.now(ZoneInfo("Asia/Kolkata"))

    result = analyze_profiles(
        payload.get("groom") or {},
        payload.get("bride") or {},
        as_of,
        int(payload.get("horizon_years") or 12),
    )
    print(json.dumps({
        "ok":True,
        "engine":{
            "name":"tithika-marriage-analysis",
            "version":ENGINE_VERSION,
            "ayanamsha":"Lahiri / Chitrapaksha",
            "house_system":"whole-sign",
            "navamsha":"D9",
            "scoring":"none",
        },
        **result,
    }, ensure_ascii=False))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(json.dumps({"ok":False,"error":str(exc),"code":"MARRIAGE_ANALYSIS_FAILED"}))
        sys.exit(1)
