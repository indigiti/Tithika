#!/usr/bin/env python3
import os
import sys
from datetime import datetime
from zoneinfo import ZoneInfo

ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,os.path.join(ROOT,"python"))

import interpretation
import personal_rashifal

ownership={name:[] for name in interpretation.CLASSICAL}
domain={"evidence_index":60,"relevant_planets":["Mercury","Jupiter"]}
periods=[{"level":"Mahadasha","planet":"Mercury","start":"x","end":"y"}]
transits=[
    {"planet":"Moon","house_from_lagna":10,"house_from_moon":4},
    {"planet":"Jupiter","house_from_lagna":10,"house_from_moon":3},
]
score,evidence=personal_rashifal.sample_domain_score(
    "daily","career",domain,ownership,periods,transits
)
assert score==57.2,(score,evidence)
assert evidence["band"]=="active"
assert evidence["base_points"]==25.2
assert evidence["dasha_points"]==16.0
assert evidence["transit_points"]==16.0

tz=ZoneInfo("Asia/Kolkata")
target=datetime(2026,10,6,12,0,tzinfo=tz)
d0,d1=personal_rashifal.period_bounds("daily",target)
assert d0.date().isoformat()=="2026-10-06"
assert (d1-d0).days==1
w0,w1=personal_rashifal.period_bounds("weekly",target)
assert w0.date().isoformat()=="2026-10-05"
assert (w1-w0).days==7
m0,m1=personal_rashifal.period_bounds("monthly",target)
assert m0.date().isoformat()=="2026-10-01"
assert m1.date().isoformat()=="2026-11-01"
y0,y1=personal_rashifal.period_bounds("yearly",target)
assert y0.date().isoformat()=="2026-01-01"
assert y1.date().isoformat()=="2027-01-01"
assert len(personal_rashifal.sample_moments("weekly",w0,w1))==7
assert len(personal_rashifal.sample_moments("monthly",m0,m1))==31
assert len(personal_rashifal.sample_moments("yearly",y0,y1))==12

payload={
    "mode":"daily",
    "date":"1990-01-15",
    "time":"10:30:00",
    "target_date":"2026-10-06",
    "lat":18.5204,
    "lon":73.8567,
    "city":"Pune, Maharashtra, India",
    "timezone":"Asia/Kolkata",
    "node_model":"mean",
}
r=personal_rashifal.build(payload)
assert r["ok"] is True
assert r["engine"]["name"]=="tithika-personal-rashifal"
assert r["mode"]=="daily"
assert r["target_date"]=="2026-10-06"
assert set(r["periods"])=={"daily"}
p=r["periods"]["daily"]
assert p["sample_count"]==1
assert len(p["top_focus"])==3
assert set(p["domains"])=={"identity","resources","learning","career","relationships"}
assert r["integrity"]["periods_complete"] is True
assert r["integrity"]["scores_bounded"] is True
assert r["integrity"]["source_integrity"]["ashtakavarga"] is True
assert r["integrity"]["source_integrity"]["shadbala_planets"] is True
assert r["integrity"]["source_integrity"]["charts"] is True
assert len(r["current_context"]["active_dasha"]) in (2,3)
assert len(r["current_context"]["slow_transits"])==4

for row in p["domains"].values():
    assert 0 <= row["activation_index"] <= 100
    assert row["band"] in {"high","elevated","active","background"}
    assert row["quality"] in {"supportive","mixed","challenging","contextual"}
    assert "not an event probability" in row["interpretation"].lower()

assert "not a probability of events" in r["methodology"]["meaning"].lower()
assert "does not predict guaranteed events" in r["note"].lower()
print("Personalized Rashifal regression fixture passed")
