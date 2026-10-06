#!/usr/bin/env python3
"""Regression coverage for Tithika's six-phase completion engine."""
from __future__ import annotations

import sys
from datetime import date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))

import completion  # noqa: E402

LAT = 18.5204
LON = 73.8567
TZ = ZoneInfo("Asia/Kolkata")
YEAR = 2026


def dates(rows, name=None):
    return {r["date"] for r in rows if not name or r.get("name") == name}


def test_panchang_completion():
    manvadi = completion.named_tithi_events(YEAR, completion.MANVADI_RULES, LAT, LON, TZ, False)
    assert len(manvadi) >= 13
    by_name = {r["name"]: r["date"] for r in manvadi}
    assert by_name["Swayambhuva Manvadi"] == "2026-03-21"
    assert by_name["Raivata Manvadi"] == "2026-07-24"
    assert by_name["Daksha Savarni Manvadi"] == "2026-10-20"

    yugadi = completion.named_tithi_events(YEAR, completion.YUGADI_RULES, LAT, LON, TZ, False)
    assert {r["date"] for r in yugadi} == {
        "2026-02-17", "2026-04-19", "2026-10-08", "2026-11-18"
    }

    kalpadi = completion.named_tithi_events(YEAR, completion.KALPADI_RULES, LAT, LON, TZ, False)
    assert {"2026-01-30", "2026-03-06", "2026-03-19", "2026-03-23", "2026-04-19", "2026-11-16", "2026-12-18"} <= dates(kalpadi)

    kranti = completion.kranti_samya(YEAR, LAT, LON, TZ, False)
    assert all(r["yoga"] in {"Vyatipata", "Vaidhriti"} for r in kranti)
    assert all(abs(r["sun_declination"] - r["moon_declination"]) < 0.02 for r in kranti)


def test_muhurat_completion():
    d = date(2026, 10, 6)
    gowri = completion.gowri_day(d, LAT, LON, TZ)
    assert len(gowri) == 16
    assert len([r for r in gowri if r["period"] == "day"]) == 8
    assert len([r for r in gowri if r["period"] == "night"]) == 8
    assert any(r["auspicious"] for r in gowri)

    pach = completion.pachchakkhan(d, LAT, LON, TZ)
    assert {r["name"] for r in pach} >= {"Sunrise", "Navkarshi", "Porshi", "Chovihar", "Next Sunrise"}
    sunrise = datetime.fromisoformat(next(r["datetime"] for r in pach if r["name"] == "Sunrise"))
    navkarshi = datetime.fromisoformat(next(r["datetime"] for r in pach if r["name"] == "Navkarshi"))
    assert abs((navkarshi - sunrise).total_seconds() - 48 * 60) < 1

    do_ghati = completion.do_ghati(d, LAT, LON, TZ)
    assert len(do_ghati) == 30
    assert len([r for r in do_ghati if r["period"] == "day"]) == 15
    assert len([r for r in do_ghati if r["period"] == "night"]) == 15

    pakshi = completion.pancha_pakshi(d, LAT, LON, TZ, {"birth_nakshatra": "Rohini"})
    assert pakshi["bird"] in completion.BIRDS
    assert len(pakshi["events"]) == 10
    assert {r["activity"] for r in pakshi["events"]} == set(completion.ACTIVITIES)

    shubha = completion.shubha_dates(YEAR, LAT, LON, TZ)
    assert shubha
    assert all(r["score"] >= 5 for r in shubha)


def test_vrat_completion():
    iskcon = completion.iskcon_ekadashi(YEAR, LAT, LON, TZ, False)
    assert len(iskcon) >= 20
    assert {"2026-07-25", "2026-08-24"} <= dates(iskcon)
    assert all(r.get("parana") for r in iskcon)

    chandra = completion.chandra_darshan(YEAR, LAT, LON, TZ, False)
    assert "2026-10-12" in dates(chandra)

    ishti = completion.ishti_anvadhan(YEAR, LAT, LON, TZ, False)
    assert "2026-10-10" in dates(ishti, "Anvadhan")
    assert "2026-10-11" in dates(ishti, "Ishti")

    kalashtami = completion.kalashtami(YEAR, LAT, LON, TZ, False)
    janmashtami = completion.masik_janmashtami(YEAR, LAT, LON, TZ, False)
    assert len(kalashtami) >= 11
    assert len(janmashtami) >= 11

    adhika = completion.adhika_months(YEAR, LAT, LON, TZ)
    assert adhika
    assert all(r["start_date"] <= r["end_date"] for r in adhika)

    chaturmasa = completion.chaturmasa(YEAR, LAT, LON, TZ, False)
    assert len(chaturmasa) == 1
    assert chaturmasa[0]["start_date"] < chaturmasa[0]["end_date"]

    shraddha = completion.shraddha_events(YEAR, LAT, LON, TZ, False)
    categories = {r["category"] for r in shraddha}
    assert {"amavasya", "sankranti", "pitru-paksha", "manvadi", "yugadi"} <= categories


def test_festival_aggregation():
    all_events = completion.festival_aggregate(YEAR, LAT, LON, TZ, False, "festival-hindu", {})
    assert len(all_events) == len(completion.festival_rules.SUPPORTED_KINDS)
    assert all_events == sorted(all_events, key=lambda r: r["date"])

    tamil = completion.festival_aggregate(YEAR, LAT, LON, TZ, False, "festival-tamil", {})
    malayalam = completion.festival_aggregate(YEAR, LAT, LON, TZ, False, "festival-malayalam", {})
    assert all(r.get("regional_month") for r in tamil)
    assert all(r.get("regional_month") for r in malayalam)

    kartika = completion.festival_aggregate(YEAR, LAT, LON, TZ, False, "festival-month", {"calendar_month": "Kartika"})
    assert kartika
    assert all(r.get("purnimanta_month") == "Kartika" for r in kartika)

    diwali = completion.festival_aggregate(YEAR, LAT, LON, TZ, False, "festival-yearly", {"festival_kind": "diwali"})
    assert len(diwali) == 3
    assert {r["date"][:4] for r in diwali} == {"2025", "2026", "2027"}


def test_secondary_jyotish():
    base = {"date": "2026-10-06", "time": "12:00:00"}
    prashna = completion.jyotish_secondary("prashna-kundali", base, LAT, LON, TZ)
    assert len(prashna["placements"]) == len(completion.planetary.CLASSICAL_ORDER)
    assert prashna["lagna"]["rashi"] in completion.panchang.RASHI_NAMES

    gemstone = completion.jyotish_secondary("gemstone", base, LAT, LON, TZ)
    rudraksha = completion.jyotish_secondary("rudraksha", base, LAT, LON, TZ)
    assert gemstone["traditional_correspondence"]
    assert rudraksha["traditional_correspondence"]

    naming = completion.jyotish_secondary("baby-name", base, LAT, LON, TZ)
    assert naming["recommended_syllable"]

    shraddha = completion.jyotish_secondary("shraddha-tithi", base, LAT, LON, TZ)
    assert shraddha["tithi"]

    thousand = completion.jyotish_secondary(
        "sahasra-chandrodaya", {"date": "1950-01-01", "birth_date": "1950-01-01"}, LAT, LON, TZ
    )
    assert thousand["thousandth_full_moon"]


def test_astronomy_completion():
    parallels = completion.planet_parallel(date(2026, 10, 6), LAT, LON, TZ)
    assert isinstance(parallels, list)
    assert all(r["orb_deg"] <= 0.75 for r in parallels)

    crossings = completion.ecliptic_crossings(YEAR, TZ)
    assert crossings
    assert crossings == sorted(crossings, key=lambda r: r["datetime"])

    seasons = completion.indian_seasons(YEAR, TZ)
    assert len(seasons) == 6
    assert [r["name"] for r in seasons] == [
        "Vasanta Ritu", "Grishma Ritu", "Varsha Ritu",
        "Sharad Ritu", "Hemanta Ritu", "Shishira Ritu"
    ]
    assert seasons == sorted(seasons, key=lambda r: r["datetime"])


if __name__ == "__main__":
    test_panchang_completion()
    test_muhurat_completion()
    test_vrat_completion()
    test_festival_aggregation()
    test_secondary_jyotish()
    test_astronomy_completion()
    print("six-phase completion regression: OK")
