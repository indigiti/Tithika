#!/usr/bin/env python3
import os
import sys

ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,os.path.join(ROOT,"python"))

import interpretation

# Rule fixture: Cancer Lagna gives Mars H5 + H10, the strict Yogakaraka pattern.
ownership=interpretation.owned_houses(3)
assert ownership["Mars"]==[5,10], ownership["Mars"]
role=interpretation.functional_role(ownership["Mars"])
assert role["category"]=="yogakaraka"
assert "strict-yogakaraka" in role["flags"]

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
r=interpretation.build(payload)
assert r["ok"] is True
assert r["engine"]["name"]=="tithika-jyotish-interpretation"
assert r["engine"]["profile"]=="auditable-rule-based-interpretation"
assert len(r["planet_interpretations"])==7
assert len(r["house_interpretations"])==8
assert set(r["domain_interpretations"])=={"identity","resources","learning","career","relationships"}
assert r["integrity"]["ashtakavarga"] is True
assert r["integrity"]["shadbala_planets"] is True
assert r["integrity"]["charts"] is True
assert r["integrity"]["planet_interpretations"] is True
assert r["integrity"]["key_house_interpretations"] is True
assert r["integrity"]["domain_interpretations"] is True

for row in r["planet_interpretations"]:
    assert row["owned_houses"]
    assert row["functional_role"]["category"] in {"yogakaraka","supportive","challenging","mixed","structural"}
    assert row["divisional_confirmation"]["d1"]["dignity"] in {"exalted","own","debilitated","other"}
    assert row["interpretation"]

for row in r["domain_interpretations"].values():
    assert 0 <= row["evidence_index"] <= 100
    assert row["activation"]["activation"] in {"high","active","background"}
    assert "not a probability" in row["interpretation"].lower()

assert "not a deterministic prediction engine" in r["note"].lower()
print("Jyotish interpretation regression fixture passed")
