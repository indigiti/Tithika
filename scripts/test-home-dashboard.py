#!/usr/bin/env python3
import json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
ENGINE=ROOT/"python"/"home_dashboard.py"
payload={
 "lat":18.5204,"lon":73.8567,"city":"Pune, Maharashtra, India",
 "timezone":"Asia/Kolkata","date":"2026-10-06","hour24":False
}
p=subprocess.run([sys.executable,str(ENGINE)],input=json.dumps(payload),text=True,capture_output=True,cwd=ROOT,timeout=240)
if p.returncode!=0: raise SystemExit(p.stdout+"\n"+p.stderr)
d=json.loads(p.stdout)
assert d["ok"] is True,d
assert d["date"]=="2026-10-06"
assert d["today"]["tithi"]=="Ekadashi",d["today"]
assert d["today"]["nakshatra"]=="Ashlesha",d["today"]
assert d["today"]["moon_rashi"]=="Karka",d["today"]
assert d["today"]["sunrise"] and d["today"]["sunset"]
assert len(d["choghadiya"]["day"])==8
assert d["advisor"]["recommendations"],d["advisor"]
assert isinstance(d["upcoming"]["calendar"],list)
assert isinstance(d["upcoming"]["planets"],list)
assert len(d["provenance"])==3
print("Home dashboard fixture OK: Panchang, Choghadiya, advisor, calendar and planet aggregation")
