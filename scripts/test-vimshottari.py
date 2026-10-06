#!/usr/bin/env python3
import json, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
ENGINE=ROOT/"python"/"vimshottari.py"
payload={"lat":18.5204,"lon":73.8567,"city":"Pune, India","timezone":"Asia/Kolkata","date":"2026-10-06","time":"07:40:31","as_of":"2026-10-06T07:40:31+05:30"}
p=subprocess.run([sys.executable,str(ENGINE)],input=json.dumps(payload),text=True,capture_output=True,cwd=ROOT)
if p.returncode!=0: raise SystemExit(p.stdout+"\n"+p.stderr)
d=json.loads(p.stdout);assert d["ok"] is True,d
r=d["result"]
assert r["nakshatra"]=="Ashlesha"
assert r["starting_lord"]=="Mercury"
assert r["nakshatra_pada"]==2
assert abs(r["birth_balance_years"]-10.7143)<0.03,r["birth_balance_years"]
assert r["mahadasha"][0]["lord"]=="Mercury"
assert r["mahadasha"][0]["start"].startswith("2026-10-06")
assert len(r["mahadasha"][0]["antardasha"])>=5
assert abs(d["engine"]["year_days"]-365.25)<1e-9
print("Vimshottari fixture OK: Ashlesha Mercury balance and proportional subperiods")
