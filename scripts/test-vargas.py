#!/usr/bin/env python3
import json, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"python"))
import vargas, kundali

def r(lon,n): return vargas.varga_position(lon,n)["rashi"]

assert r(10,2)=="Simha"
assert r(20,2)=="Karka"
assert r(40,2)=="Karka"
assert r(50,2)=="Simha"
assert r(15,3)=="Simha"
assert r(8,4)=="Karka"
assert r(31,10)=="Makara"          # Taurus even sign -> 9th therefrom
assert r(4.9,30)=="Mesha"
assert r(7,30)=="Kumbha"
assert r(29,30)=="Tula"
assert r(34,30)=="Vrishabha"
assert r(38,30)=="Kanya"
assert r(59,30)=="Vrishchika"
assert r(0.1,60)=="Mesha"
assert r(0.6,60)=="Vrishabha"
assert r(30.1,60)=="Vrishabha"

# D9 must remain bit-for-bit compatible with the established Kundali Navamsha.
for lon in [0.1,17.2,29.9,44.0,111.5966,168.61,194.1,303.2,359.9]:
    a=vargas.varga_position(lon,9)
    b=kundali.navamsha_sign(lon)
    assert a["rashi_id"]==b["rashi_id"],(lon,a,b)

payload={"lat":18.5204,"lon":73.8567,"city":"Pune, India","timezone":"Asia/Kolkata","date":"2026-10-06","time":"07:40:31"}
p=subprocess.run([sys.executable,str(ROOT/"python"/"vargas.py")],input=json.dumps(payload),text=True,capture_output=True,cwd=ROOT)
if p.returncode!=0: raise SystemExit(p.stdout+"\n"+p.stderr)
d=json.loads(p.stdout); assert d["ok"] is True,d
assert len(d["charts"])==16
assert d["charts"]["D9"]["lagna"]["rashi"]=="Vrishchika"
assert d["charts"]["D1"]["lagna"]["rashi"]=="Tula"
assert d["charts"]["D60"]["minimum_boundary_margin_deg"]>=0
for key,ch in d["charts"].items():
    assert len(ch["placements"])==9,key
    assert len(ch["cells"])==12,key
print("Varga fixture OK: BPHS D2-D60 mappings and established D9 parity")
