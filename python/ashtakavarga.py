#!/usr/bin/env python3
from __future__ import annotations
import json, sys
from datetime import datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
import lagna, planetary, panchang

PLANETS=["Sun","Moon","Mars","Mercury","Jupiter","Venus","Saturn"]
REFERENCES=PLANETS+["Lagna"]
TABLES={
"Sun":{"Sun":[1,2,4,7,8,9,10,11],"Moon":[3,6,10,11],"Mars":[1,2,4,7,8,9,10,11],"Mercury":[3,5,6,9,10,11,12],"Jupiter":[5,6,9,11],"Venus":[6,7,12],"Saturn":[1,2,4,7,8,9,10,11],"Lagna":[3,4,6,10,11,12]},
"Moon":{"Sun":[3,6,7,8,10,11],"Moon":[1,3,6,7,10,11],"Mars":[2,3,5,6,9,10,11],"Mercury":[1,3,4,5,7,8,10,11],"Jupiter":[1,4,7,8,10,11,12],"Venus":[3,4,5,7,9,10,11],"Saturn":[3,5,6,11],"Lagna":[3,6,10,11]},
"Mars":{"Sun":[3,5,6,10,11],"Moon":[3,6,11],"Mars":[1,2,4,7,8,10,11],"Mercury":[3,5,6,11],"Jupiter":[6,10,11,12],"Venus":[6,8,11,12],"Saturn":[1,4,7,8,9,10,11],"Lagna":[1,3,6,10,11]},
"Mercury":{"Sun":[5,6,9,11,12],"Moon":[2,4,6,8,10,11],"Mars":[1,2,4,7,8,9,10,11],"Mercury":[1,3,5,6,9,10,11,12],"Jupiter":[6,8,11,12],"Venus":[1,2,3,4,5,8,9,11],"Saturn":[1,2,4,7,8,9,10,11],"Lagna":[1,2,4,6,8,10,11]},
"Jupiter":{"Sun":[1,2,3,4,7,8,9,10,11],"Moon":[2,5,7,9,11],"Mars":[1,2,4,7,8,10,11],"Mercury":[1,2,4,5,6,9,10,11],"Jupiter":[1,2,3,4,7,8,10,11],"Venus":[2,5,6,9,10,11],"Saturn":[3,5,6,12],"Lagna":[1,2,4,5,6,7,9,10,11]},
"Venus":{"Sun":[8,11,12],"Moon":[1,2,3,4,5,8,9,11,12],"Mars":[3,4,6,8,9,11,12],"Mercury":[3,5,6,9,11],"Jupiter":[5,8,9,10,11],"Venus":[1,2,3,4,5,8,9,10,11],"Saturn":[3,4,5,8,9,10,11],"Lagna":[1,2,3,4,5,8,9]},
"Saturn":{"Sun":[1,2,4,7,8,10,11],"Moon":[3,6,11],"Mars":[3,5,6,10,11,12],"Mercury":[6,8,9,10,11,12],"Jupiter":[5,6,11,12],"Venus":[6,11,12],"Saturn":[3,5,6,11],"Lagna":[1,3,4,6,10,11]}
}
LAGNA_TABLE={
"Sun":[3,4,6,10,11],"Moon":[3,6,10,11],"Mars":[1,3,6,10,11],"Mercury":[1,2,4,6,8,10,11],"Jupiter":[1,2,4,5,6,7,9,10,11],"Venus":[1,2,3,4,5,8,9],"Saturn":[1,3,4,6,10,11],"Lagna":[3,6,10,11]
}
EXPECTED={"Sun":48,"Moon":49,"Mars":39,"Mercury":54,"Jupiter":56,"Venus":52,"Saturn":39}

def parse_birth(p,tz):
    s=str(p.get("datetime") or "").strip()
    if not s:s=f"{p.get('date') or datetime.now(tz).strftime('%Y-%m-%d')}T{p.get('time') or '12:00:00'}"
    d=datetime.fromisoformat(s)
    return d.replace(tzinfo=tz) if d.tzinfo is None else d.astimezone(tz)

def make_bav(table,positions):
    scores=[0]*12
    contributors={}
    for ref,houses in table.items():
        ref_sign=positions[ref]
        signs=[]
        for h in houses:
            sign=(ref_sign+h-1)%12
            scores[sign]+=1;signs.append(sign)
        contributors[ref]=signs
    return scores,contributors

def main():
    p=json.loads(sys.stdin.read() or "{}")
    lat=float(p.get("lat",19.076));lon=float(p.get("lon",72.8777))
    tzname=p.get("timezone") or "Asia/Kolkata"
    try:tz=ZoneInfo(tzname)
    except ZoneInfoNotFoundError:tzname="Asia/Kolkata";tz=ZoneInfo(tzname)
    birth=parse_birth(p,tz)
    asc=lagna.lagna_state(birth,lat,lon)
    states={n:planetary.planet_state(n,birth) for n in PLANETS}
    positions={n:states[n]["rashi_id"] for n in PLANETS};positions["Lagna"]=asc["lagna_id"]
    bav={};sav=[0]*12;checks={}
    for target in PLANETS:
        scores,contributors=make_bav(TABLES[target],positions)
        total=sum(scores);checks[target]={"total":total,"expected":EXPECTED[target],"valid":total==EXPECTED[target]}
        bav[target]={"scores":scores,"total":total,"contributors":contributors}
        sav=[sav[i]+scores[i] for i in range(12)]
    lagna_scores,lagna_contrib=make_bav(LAGNA_TABLE,positions)
    rows=[{"rashi_id":i,"rashi":panchang.RASHI_NAMES[i],"sav":sav[i],"house":((i-asc["lagna_id"])%12)+1,"bav":{n:bav[n]["scores"][i] for n in PLANETS},"lagna":lagna_scores[i]} for i in range(12)]
    print(json.dumps({"ok":True,"birth_datetime":birth.isoformat(),"engine":{"name":"tithika-ashtakavarga","version":"0.1.0","profile":"classical-Parashari-raw-BAV-SAV","ayanamsha":"Lahiri / Chitrapaksha"},"positions":positions,"bav":bav,"lagna_ashtakavarga":{"scores":lagna_scores,"total":sum(lagna_scores),"contributors":lagna_contrib},"sav":{"scores":sav,"total":sum(sav)},"rows":rows,"integrity":{"bav":checks,"sav_total":sum(sav),"sav_expected":337,"valid":all(x["valid"] for x in checks.values()) and sum(sav)==337},"note":"Raw Bhinnashtakavarga and Sarvashtakavarga are calculated from the seven classical planets plus Lagna contributor tables. Rahu and Ketu are excluded."},ensure_ascii=False))
if __name__=="__main__":
    try:main()
    except Exception as e:
        print(json.dumps({"ok":False,"error":str(e),"code":"ASHTAKAVARGA_CALCULATION_FAILED"}));sys.exit(1)
