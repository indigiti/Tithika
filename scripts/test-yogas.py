#!/usr/bin/env python3
import json, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"python"))
import yogas, panchang

def P(name,sign,asc=0,combust=False):
    return {"name":name,"rashi_id":sign,"rashi":panchang.RASHI_NAMES[sign],"house":((sign-asc)%12)+1,"combust":combust}

# Synthetic chart locks the geometry of several headline yogas.
asc=0
planets={
 "Sun":P("Sun",4,asc),
 "Moon":P("Moon",0,asc),
 "Mars":P("Mars",0,asc),
 "Mercury":P("Mercury",4,asc),
 "Jupiter":P("Jupiter",3,asc),
 "Venus":P("Venus",6,asc),
 "Saturn":P("Saturn",6,asc),
}
rows=yogas.detect_from_chart(asc,planets)
names={x["name"] for x in rows}
assert "Gajakesari Yoga" in names
assert "Budha-Aditya Yoga" in names
assert "Chandra-Mangala Yoga" in names
assert "Ruchaka Yoga" in names or any(x.startswith("Ruchaka Yoga") for x in names)
assert any(x.startswith("Sasa Yoga") for x in names)   # Saturn exalted in Libra, 7th Kendra

# Explicit Parivartana: Mars in Taurus, Venus in Aries.
planets2={
 "Sun":P("Sun",4,asc),"Moon":P("Moon",2,asc),"Mars":P("Mars",1,asc),
 "Mercury":P("Mercury",5,asc),"Jupiter":P("Jupiter",8,asc),
 "Venus":P("Venus",0,asc),"Saturn":P("Saturn",10,asc),
}
rows2=yogas.detect_from_chart(asc,planets2)
assert any(x["name"].startswith("Parivartana Yoga") and set(x["evidence"]["planets"])=={"Mars","Venus"} for x in rows2)

# Real regression chart: engine must remain stable and expose auditable evidence.
payload={"lat":18.5204,"lon":73.8567,"city":"Pune, India","timezone":"Asia/Kolkata","date":"2026-10-06","time":"07:40:31"}
p=subprocess.run([sys.executable,str(ROOT/"python"/"yogas.py")],input=json.dumps(payload),text=True,capture_output=True,cwd=ROOT)
if p.returncode!=0: raise SystemExit(p.stdout+"\n"+p.stderr)
d=json.loads(p.stdout);assert d["ok"] is True,d
assert d["lagna"]["rashi"]=="Tula"
assert isinstance(d["yogas"],list)
for row in d["yogas"]:
    assert row["name"] and row["rule"] and isinstance(row["evidence"],dict)
print("Yoga fixture OK: headline, Mahapurusha, exchange and live-chart structural rules")
