#!/usr/bin/env python3
import os
import sys
from datetime import datetime

ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,os.path.join(ROOT,"python"))

import horoscope_analysis

payload={
    "date":"1990-01-15",
    "time":"10:30:00",
    "lat":18.5204,
    "lon":73.8567,
    "city":"Pune, Maharashtra, India",
    "timezone":"Asia/Kolkata",
    "node_model":"mean",
    "as_of":"2026-10-06T12:00:00+05:30",
}
r=horoscope_analysis.build(payload)
assert r["ok"] is True
assert r["engine"]["name"]=="tithika-horoscope-analysis"
assert r["engine"]["profile"]=="evidence-first-composite"
assert set(r["charts"])=={"D1","D9","D10"}
assert len(r["strengths"])==7
assert r["ashtakavarga"]["sav_total"]==337
assert r["ashtakavarga"]["integrity_valid"] is True
assert r["integrity"]["ashtakavarga"] is True
assert r["integrity"]["shadbala_planets"] is True
assert r["integrity"]["charts"] is True
assert set(r["domains"])=={"identity","resources","learning","career","relationships"}
for row in r["domains"].values():
    assert 0.0 <= row["evidence_index"] <= 100.0
    assert row["method"].startswith("60% normalized Shadbala")
assert len(r["timing"]["major_transits"])==4
assert {x["planet"] for x in r["timing"]["major_transits"]}=={"Jupiter","Saturn","Rahu","Ketu"}
assert r["dasha"]["current"] is not None
assert r["birth_profile"]["nakshatra"]
assert r["sensitivity"]["level"] in {"normal","moderate","high"}
assert len(r["methodology"])>=5
print("Unified horoscope analysis regression fixture passed")
