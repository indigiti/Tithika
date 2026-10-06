#!/usr/bin/env python3
import json, subprocess, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
ENGINE=ROOT/"python"/"shadbala.py"
payload={"lat":18.5204,"lon":73.8567,"city":"Pune, India","timezone":"Asia/Kolkata","date":"2026-10-06","time":"07:40:31"}
p=subprocess.run([sys.executable,str(ENGINE)],input=json.dumps(payload),text=True,capture_output=True,cwd=ROOT)
if p.returncode!=0:
    raise SystemExit(p.stdout+"\n"+p.stderr)
d=json.loads(p.stdout)
assert d["ok"] is True,d
assert d["engine"]["status"]=="complete-six-fold-profile"
assert d["lagna"]["rashi"]=="Tula"
assert len(d["planets"])==7
assert d["solar_context"]["sunrise"] < d["solar_context"]["sunset"] < d["solar_context"]["next_sunrise"]
assert set(d["time_lords"]) >= {"abda","masa","vara","hora"}

by={row["planet"]:row for row in d["planets"]}
assert set(by)=={"Sun","Moon","Mars","Mercury","Jupiter","Venus","Saturn"}

for name,row in by.items():
    c=row["components_virupa"]
    s=c["sthana"]; k=c["kala"]
    assert len(s["saptavargaja_detail"])==7
    assert s["ojayugma"] in (0.0,15.0,30.0)
    assert s["kendradi"] in (15.0,30.0,60.0)
    assert s["drekkana"] in (0.0,15.0)
    assert 0.0 <= s["uchcha"] <= 60.0
    assert 0.0 <= c["dig"] <= 60.0
    assert c["naisargika"] > 0.0
    subtotal=s["subtotal"]+c["dig"]+k["subtotal"]+c["cheshta"]+c["naisargika"]+c["drik"]
    assert abs(subtotal-row["total_virupa"]) < 0.03,(name,subtotal,row["total_virupa"])
    assert abs(row["total_rupa"]*60-row["total_virupa"]) < 0.04
    assert row["required_rupa"] > 0
    assert isinstance(row["meets_required"],bool)

# Classical identity/profile invariants.
assert abs(by["Sun"]["components_virupa"]["cheshta"]-by["Sun"]["components_virupa"]["kala"]["ayana"]) < 0.01
assert abs(by["Moon"]["components_virupa"]["cheshta"]-by["Moon"]["components_virupa"]["kala"]["paksha"]) < 0.01
assert abs(by["Sun"]["components_virupa"]["naisargika"]-60.0)<1e-9
assert abs(by["Saturn"]["components_virupa"]["naisargika"]-8.57)<1e-9
assert by["Sun"]["required_rupa"]==6.5
assert by["Mercury"]["required_rupa"]==7.0
assert len(d["method_notes"])>=6

print("Shadbala fixture OK: complete six-fold arithmetic, Saptavargaja, Kala, Cheshta identities and declared thresholds")
