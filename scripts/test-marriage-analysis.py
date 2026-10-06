#!/usr/bin/env python3
import json, subprocess, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
ENGINE=ROOT/"python"/"marriage_analysis.py"

PROFILE={
    "name":"Fixture",
    "date":"2026-10-06","time":"07:40:31",
    "lat":18.5204,"lon":73.8567,
    "city":"Pune, India","timezone":"Asia/Kolkata"
}
payload={
    "groom":PROFILE,"bride":PROFILE,
    "as_of":"2026-10-06T12:00:00+05:30",
    "horizon_years":12
}
p=subprocess.run([sys.executable,str(ENGINE)],input=json.dumps(payload),text=True,capture_output=True,cwd=ROOT)
if p.returncode!=0:
    raise SystemExit(p.stdout+"\n"+p.stderr)
d=json.loads(p.stdout)
assert d["ok"] is True,d
assert d["engine"]["scoring"]=="none"

g=d["groom"]; b=d["bride"]
assert g["lagna"]["rashi"]=="Tula"
assert g["d1"]["seventh_sign"]=="Mesha"
assert g["d1"]["seventh_lord"]=="Mars"
assert g["d1"]["seventh_lord_house"]==10
assert g["d9"]["lagna"]["rashi"]=="Vrischika",g["d9"]["lagna"]
assert g["d9"]["seventh_sign"]=="Vrishabha"
assert g["d9"]["seventh_lord"]=="Venus"
assert g["d9"]["seventh_lord_house"]==4

assert g["mangal"]["present"] is True
assert g["mangal"]["effective_present"] is False
assert any(x["rule"]=="jupiter-conjunct-mars" for x in g["mangal"]["cancellation_evidence"])

pair=d["pair"]
assert pair["d9_lagna"]["label"]=="same-sign"
assert pair["venus"]["sign_relation"]["label"]=="same-sign"
assert pair["jupiter"]["sign_relation"]["label"]=="same-sign"
assert d["mangal"]["mutual_manglik"] is True
assert d["mangal"]["effective_mismatch"] is False
assert any(x["rule"]=="mutual-manglik" for x in d["mangal"]["pair_cancellation_evidence"])

windows=d["dasha_overlap"]["windows"]
assert windows
for row in windows:
    assert row["start"] < row["end"]
    assert 2 <= row["combined_strength"] <= 4
    assert row["duration_days"] > 0

assert d["dasha_overlap"]["horizon_years"]==12
assert "No additional compatibility score" not in d.get("disclaimer","")
assert "No additional compatibility score".lower() in d["disclaimer"].lower()

print("Marriage analysis fixture OK: D1/D9, Mangal cancellation, 7th lords and Dasha overlaps")
