#!/usr/bin/env python3
import json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BASE={
 "lat":18.5204,"lon":73.8567,"city":"Pune, India",
 "timezone":"Asia/Kolkata","date":"2026-10-06","time":"07:40:31",
 "node_model":"mean","as_of":"2026-10-07T12:00:00+05:30"
}
def run(name):
 p=subprocess.run([sys.executable,str(ROOT/"python"/name)],input=json.dumps(BASE),text=True,capture_output=True,cwd=ROOT,timeout=240)
 if p.returncode!=0: raise SystemExit(p.stdout+"\n"+p.stderr)
 d=json.loads(p.stdout);assert d["ok"] is True,d;return d
k=run("kundali.py")
a=run("horoscope_analysis.py")
assert k["lagna"]["rashi"]=="Tula"
assert a["birth_profile"]["lagna"]["rashi"]==k["lagna"]["rashi"]
assert set(a["charts"]) >= {"D1","D9","D10"}
assert len(a["charts"]["D1"]["cells"])==12
assert len(a["charts"]["D9"]["cells"])==12
assert len(a["charts"]["D10"]["cells"])==12
assert len(a["strengths"])==7
assert a["ashtakavarga"]["integrity_valid"] is True
assert a["ashtakavarga"]["sav_total"]==337
assert isinstance(a["yogas"]["items"],list)
assert (a["dasha"]["current"] or {}).get("mahadasha")
print("Kundali Workspace backend contract OK: chart, strengths, Yogas, Dasha and Ashtakavarga agree")
