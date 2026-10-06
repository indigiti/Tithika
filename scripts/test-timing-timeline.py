#!/usr/bin/env python3
import os
import sys

ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,os.path.join(ROOT,"python"))

import timing_timeline

# Transparent scoring fixture:
# 60 structural evidence -> 33 base points (55%)
# Mercury Mahadasha -> 18 points
# Jupiter transit through H10 -> 7 points
# total = 58, "active".
domain={"evidence_index":60,"relevant_planets":["Mercury","Jupiter"]}
ownership={name:[] for name in timing_timeline.interpretation.CLASSICAL}
periods=[{"level":"Mahadasha","planet":"Mercury","start":"x","end":"y"}]
transits=[{
    "planet":"Jupiter","rashi":"Mesha","rashi_id":0,"retrograde":False,
    "house_from_lagna":10,"house_from_moon":4,
}]
score,details=timing_timeline.activation_index(
    "career",domain,ownership,periods,transits
)
assert score==58.0,(score,details)
assert details["band"]=="active"
assert details["base_evidence_points"]==33.0
assert details["dasha_points"]==18.0
assert details["transit_points"]==7.0

payload={
    "date":"1990-01-15",
    "time":"10:30:00",
    "lat":18.5204,
    "lon":73.8567,
    "city":"Pune, Maharashtra, India",
    "timezone":"Asia/Kolkata",
    "node_model":"mean",
    "start_month":"2026-10",
    "months":6,
}
r=timing_timeline.build(payload)
assert r["ok"] is True
assert r["engine"]["name"]=="tithika-jyotish-timing-timeline"
assert r["months"]==6
assert r["start_month"]=="2026-10"
assert len(r["monthly_timeline"])==6
assert r["integrity"]["months_complete"] is True
assert r["integrity"]["domains_complete"] is True
assert r["integrity"]["monotonic_months"] is True
assert r["integrity"]["source_integrity"]["ashtakavarga"] is True
assert r["integrity"]["source_integrity"]["shadbala_planets"] is True
assert r["integrity"]["source_integrity"]["charts"] is True

expected_domains={"identity","resources","learning","career","relationships"}
months=[x["month"] for x in r["monthly_timeline"]]
assert months==["2026-10","2026-11","2026-12","2027-01","2027-02","2027-03"],months

for row in r["monthly_timeline"]:
    assert set(row["domains"])==expected_domains
    assert len(row["top_focus"])==3
    assert len(row["dasha"]) in (2,3)
    assert len(row["transits"])==4
    for domain_row in row["domains"].values():
        assert 0 <= domain_row["activation_index"] <= 100
        assert domain_row["band"] in {"high","elevated","active","background"}
        assert domain_row["quality"] in {"supportive","mixed","challenging","contextual"}
        assert "not the probability" in domain_row["interpretation"].lower()

assert sum(x["months"] for x in r["activation_windows"])==6
assert sum(x["months_covered"] for x in r["yearly_summary"])==6
assert all(x["type"] in {"dasha","transit"} for x in r["markers"])
assert "not an event probability" in r["methodology"]["meaning"].lower()
assert "does not predict guaranteed events" in r["note"].lower()

print("Jyotish timing timeline regression fixture passed")
