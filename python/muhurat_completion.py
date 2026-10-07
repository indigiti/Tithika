#!/usr/bin/env python3
"""Completion engine for Gowri, Jain Pachchakkhan, Do-Ghati, Pancha-Pakshi and generic Shubha Dates."""
from __future__ import annotations
import json, sys
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
import panchang

ENGINE_VERSION="1.1.0"

GOOD={"Amirdha":"Best","Uthi":"Good","Laabam":"Gain","Dhanam":"Wealth","Sugam":"Good"}
BAD={"Rogam":"Evil","Soram":"Bad","Visham":"Bad"}
DAY_GOWRI={
6:["Uthi","Amirdha","Rogam","Laabam","Dhanam","Sugam","Soram","Visham"],
0:["Amirdha","Visham","Rogam","Laabam","Dhanam","Sugam","Soram","Uthi"],
1:["Rogam","Laabam","Dhanam","Sugam","Soram","Uthi","Visham","Amirdha"],
2:["Laabam","Dhanam","Sugam","Soram","Visham","Uthi","Amirdha","Rogam"],
3:["Dhanam","Sugam","Soram","Uthi","Amirdha","Visham","Rogam","Laabam"],
4:["Sugam","Soram","Uthi","Visham","Amirdha","Rogam","Laabam","Dhanam"],
5:["Soram","Uthi","Visham","Amirdha","Rogam","Laabam","Dhanam","Sugam"],
}
NIGHT_GOWRI={
6:["Dhanam","Sugam","Soram","Visham","Uthi","Amirdha","Rogam","Laabam"],
0:["Sugam","Soram","Uthi","Amirdha","Visham","Rogam","Laabam","Dhanam"],
1:["Soram","Uthi","Visham","Amirdha","Rogam","Laabam","Dhanam","Sugam"],
2:["Uthi","Amirdha","Rogam","Laabam","Dhanam","Sugam","Soram","Visham"],
3:["Amirdha","Visham","Rogam","Laabam","Dhanam","Sugam","Soram","Uthi"],
4:["Rogam","Laabam","Dhanam","Sugam","Soram","Uthi","Visham","Amirdha"],
5:["Laabam","Dhanam","Sugam","Soram","Uthi","Visham","Amirdha","Rogam"],
}

# Classical 30 Muhurta names in order. Each Muhurta is one fifteenth
# of daylight/night respectively (= two local Ghatis).
MUHURTA_NAMES=[
"Rudra","Uraga","Mitra","Pitara","Vasu","Ambu","Vishwedeva","Vidhi","Brahma","Indra",
"Indragni","Daitya","Varuna","Aryama","Bhaga",
"Ishwara","Ajaikapada","Ahirbudhnya","Pusha","Ashwini","Yama","Agni","Brahma","Chandra",
"Aditi","Brihaspati","Vishnu","Surya","Tvashta","Samirana",
]
MUHURTA_AUSPICIOUS={
"Mitra","Vasu","Ambu","Vishwedeva","Vidhi","Brahma","Indra","Varuna","Aryama",
"Ahirbudhnya","Pusha","Ashwini","Chandra","Aditi","Brihaspati","Vishnu","Surya",
"Tvashta","Samirana",
}

PAKSHI=["Vulture","Owl","Crow","Cock","Peacock"]
ACT=["Ruling","Eating","Walking","Sleeping","Dying"]
ACT_WEIGHT={"Ruling":1.0,"Eating":0.8,"Walking":0.6,"Sleeping":0.4,"Dying":0.2}
# Classical sub-Yama shares sum to 144 units: Rule 48, Walk 36,
# Eat 30, Sleep 18, Die 12. Scale these proportions to the local Yama length.
SUB_YAMA_SHARE={"Ruling":48,"Eating":30,"Walking":36,"Sleeping":18,"Dying":12}

# Explicit Pulippani mirror-table profile. This replaces the former synthetic
# weekday/paksha shift algorithm. It is intentionally named because Pancha
# Pakshi lineages differ in sub-period weighting and friendship tables.
BRIGHT_GROUP={6:"A",1:"A",0:"B",2:"B",5:"B",3:"C",4:"D"} # Sun/Tue; Mon/Wed/Sat; Thu; Fri
DARK_GROUP={6:"A",1:"A",0:"B",5:"B",2:"C",3:"D",4:"E"}

BRIGHT={
"A":{
"day":{"Vulture":["Eating","Walking","Ruling","Sleeping","Dying"],"Owl":["Ruling","Dying","Eating","Walking","Sleeping"],"Crow":["Walking","Sleeping","Dying","Ruling","Eating"],"Cock":["Dying","Ruling","Sleeping","Eating","Walking"],"Peacock":["Sleeping","Eating","Walking","Dying","Ruling"]},
"night":{"Vulture":["Dying","Ruling","Sleeping","Eating","Walking"],"Owl":["Sleeping","Eating","Walking","Dying","Ruling"],"Crow":["Eating","Walking","Ruling","Sleeping","Dying"],"Cock":["Walking","Sleeping","Dying","Ruling","Eating"],"Peacock":["Ruling","Dying","Eating","Walking","Sleeping"]}},
"B":{
"day":{"Vulture":["Dying","Ruling","Sleeping","Eating","Walking"],"Owl":["Eating","Walking","Ruling","Sleeping","Dying"],"Crow":["Sleeping","Eating","Walking","Dying","Ruling"],"Cock":["Walking","Sleeping","Dying","Ruling","Eating"],"Peacock":["Ruling","Dying","Eating","Walking","Sleeping"]},
"night":{"Vulture":["Walking","Sleeping","Dying","Ruling","Eating"],"Owl":["Dying","Ruling","Sleeping","Eating","Walking"],"Crow":["Ruling","Dying","Eating","Walking","Sleeping"],"Cock":["Eating","Walking","Ruling","Sleeping","Dying"],"Peacock":["Sleeping","Eating","Walking","Dying","Ruling"]}},
"C":{
"day":{"Vulture":["Sleeping","Eating","Walking","Dying","Ruling"],"Owl":["Walking","Sleeping","Dying","Ruling","Eating"],"Crow":["Eating","Walking","Ruling","Sleeping","Dying"],"Cock":["Ruling","Dying","Eating","Walking","Sleeping"],"Peacock":["Dying","Ruling","Sleeping","Eating","Walking"]},
"night":{"Vulture":["Ruling","Dying","Eating","Walking","Sleeping"],"Owl":["Eating","Walking","Ruling","Sleeping","Dying"],"Crow":["Dying","Ruling","Sleeping","Eating","Walking"],"Cock":["Sleeping","Eating","Walking","Dying","Ruling"],"Peacock":["Walking","Sleeping","Dying","Ruling","Eating"]}},
"D":{
"day":{"Vulture":["Walking","Sleeping","Dying","Ruling","Eating"],"Owl":["Dying","Ruling","Sleeping","Eating","Walking"],"Crow":["Ruling","Dying","Eating","Walking","Sleeping"],"Cock":["Eating","Walking","Ruling","Sleeping","Dying"],"Peacock":["Sleeping","Eating","Walking","Dying","Ruling"]},
"night":{"Vulture":["Eating","Walking","Ruling","Sleeping","Dying"],"Owl":["Walking","Sleeping","Dying","Ruling","Eating"],"Crow":["Sleeping","Eating","Walking","Dying","Ruling"],"Cock":["Dying","Ruling","Sleeping","Eating","Walking"],"Peacock":["Ruling","Dying","Eating","Walking","Sleeping"]}},
}

DARK={
"A":{
"day":{"Vulture":["Walking","Ruling","Eating","Dying","Sleeping"],"Owl":["Dying","Sleeping","Ruling","Walking","Eating"],"Crow":["Eating","Dying","Sleeping","Ruling","Walking"],"Cock":["Ruling","Eating","Walking","Sleeping","Dying"],"Peacock":["Sleeping","Walking","Dying","Eating","Ruling"]},
"night":{"Vulture":["Sleeping","Walking","Dying","Eating","Ruling"],"Owl":["Eating","Dying","Walking","Ruling","Sleeping"],"Crow":["Walking","Ruling","Eating","Sleeping","Dying"],"Cock":["Dying","Sleeping","Ruling","Dying","Eating"],"Peacock":["Ruling","Eating","Sleeping","Walking","Walking"]}},
"B":{
"day":{"Vulture":["Sleeping","Walking","Dying","Eating","Ruling"],"Owl":["Eating","Dying","Walking","Ruling","Sleeping"],"Crow":["Walking","Ruling","Eating","Sleeping","Dying"],"Cock":["Dying","Sleeping","Ruling","Walking","Eating"],"Peacock":["Ruling","Eating","Sleeping","Dying","Walking"]},
"night":{"Vulture":["Ruling","Eating","Sleeping","Walking","Dying"],"Owl":["Sleeping","Walking","Dying","Eating","Ruling"],"Crow":["Dying","Sleeping","Ruling","Dying","Eating"],"Cock":["Eating","Ruling","Walking","Sleeping","Walking"],"Peacock":["Walking","Dying","Eating","Ruling","Sleeping"]}},
"C":{
"day":{"Vulture":["Dying","Sleeping","Walking","Ruling","Eating"],"Owl":["Ruling","Eating","Dying","Sleeping","Walking"],"Crow":["Sleeping","Walking","Ruling","Eating","Dying"],"Cock":["Eating","Ruling","Sleeping","Dying","Walking"],"Peacock":["Walking","Dying","Eating","Walking","Ruling"]},
"night":{"Vulture":["Eating","Ruling","Sleeping","Dying","Walking"],"Owl":["Walking","Dying","Eating","Ruling","Sleeping"],"Crow":["Dying","Eating","Walking","Sleeping","Ruling"],"Cock":["Ruling","Sleeping","Dying","Walking","Eating"],"Peacock":["Sleeping","Walking","Ruling","Eating","Dying"]}},
"D":{
"day":{"Vulture":["Ruling","Eating","Sleeping","Walking","Dying"],"Owl":["Sleeping","Walking","Eating","Dying","Ruling"],"Crow":["Dying","Ruling","Walking","Eating","Sleeping"],"Cock":["Walking","Dying","Ruling","Sleeping","Eating"],"Peacock":["Eating","Sleeping","Dying","Ruling","Walking"]},
"night":{"Vulture":["Dying","Walking","Ruling","Eating","Sleeping"],"Owl":["Ruling","Eating","Sleeping","Walking","Dying"],"Crow":["Sleeping","Dying","Eating","Ruling","Walking"],"Cock":["Eating","Ruling","Walking","Dying","Ruling"],"Peacock":["Walking","Sleeping","Dying","Sleeping","Eating"]}},
"E":{
"day":{"Vulture":["Eating","Dying","Ruling","Sleeping","Walking"],"Owl":["Walking","Ruling","Sleeping","Eating","Dying"],"Crow":["Ruling","Sleeping","Dying","Walking","Eating"],"Cock":["Sleeping","Eating","Walking","Dying","Ruling"],"Peacock":["Dying","Walking","Eating","Ruling","Sleeping"]},
"night":{"Vulture":["Walking","Sleeping","Dying","Ruling","Eating"],"Owl":["Dying","Eating","Ruling","Sleeping","Walking"],"Crow":["Eating","Walking","Sleeping","Dying","Ruling"],"Cock":["Ruling","Dying","Eating","Walking","Sleeping"],"Peacock":["Sleeping","Ruling","Walking","Eating","Dying"]}},
}

def rise(d,lat,lon,tz,body,dirn):
    return panchang.rise_set(d,lat,lon,tz,body,dirn)

def sun_events(d,lat,lon,tz):
    sr=rise(d,lat,lon,tz,panchang.astronomy.Body.Sun,panchang.astronomy.Direction.Rise)
    ss=rise(d,lat,lon,tz,panchang.astronomy.Body.Sun,panchang.astronomy.Direction.Set)
    nr=rise(d+timedelta(days=1),lat,lon,tz,panchang.astronomy.Body.Sun,panchang.astronomy.Direction.Rise)
    if not sr or not ss or not nr: raise ValueError("Solar events unavailable")
    return sr,ss,nr

def fmt(dt): return panchang.fmt(dt,False)

def slot_rows(start,end,names,prefix):
    span=(end-start)/len(names); rows=[]
    for i,name in enumerate(names):
        a=start+span*i;b=start+span*(i+1)
        quality=GOOD.get(name,BAD.get(name,""))
        rows.append({"title":name,"date":a.date().isoformat(),"time":f"{fmt(a)} – {fmt(b)}","meta":f"{prefix} · {quality}","detail":"Equal solar division at the selected location","link_date":a.date().isoformat()})
    return rows

def gowri(selected,lat,lon,tz):
    sr,ss,nr=sun_events(selected,lat,lon,tz)
    return [
      {"title":"Day Gowri","note":"8 equal sunrise-to-sunset windows","items":slot_rows(sr,ss,DAY_GOWRI[selected.weekday()],"Day")},
      {"title":"Night Gowri","note":"8 equal sunset-to-next-sunrise windows","items":slot_rows(ss,nr,NIGHT_GOWRI[selected.weekday()],"Night")}
    ]

def pachchakkhan(selected,lat,lon,tz):
    sr,ss,nr=sun_events(selected,lat,lon,tz); day=ss-sr; night=nr-ss
    vals=[
      ("Navkarshi",sr+day/15,"2 day-Ghati after sunrise"),
      ("Porshi",sr+day/4,"end of first day Prahar"),
      ("Sadha Porshi",sr+day*3/8,"one and half Prahar"),
      ("Purimaddha",sr+day/2,"solar midday / two Prahar"),
      ("Avaddha",sr+day*3/4,"start of fourth day Prahar"),
      ("Chovihar",ss-day/15,"2 day-Ghati before sunset"),
      ("Evening Pratikraman",ss,"sunset"),
      ("Santhara Porshi",ss+night/4,"end of first night Prahar"),
      ("Nishita",ss+night/2,"middle of night"),
      ("Morning Pratikraman",ss+night*3/4,"start of fourth night Prahar"),
    ]
    rows=[{"title":name,"date":selected.isoformat(),"time":fmt(t),"meta":basis,"detail":t.isoformat(),"link_date":selected.isoformat()} for name,t,basis in vals]
    return [{"title":"Jain Pachchakkhan","note":"Solar Prahar/Ghati profile; Sangh-specific practice can add local constraints.","items":rows}]

def do_ghati(selected,lat,lon,tz):
    sr,ss,nr=sun_events(selected,lat,lon,tz)
    rows=[]; day=(ss-sr)/15; night=(nr-ss)/15
    for i in range(15):
        a=sr+day*i;b=sr+day*(i+1);name=MUHURTA_NAMES[i]
        rows.append({"title":name,"date":selected.isoformat(),"time":f"{fmt(a)} – {fmt(b)}","meta":f"Day Muhurta {i+1} · {'Auspicious' if name in MUHURTA_AUSPICIOUS else 'Inauspicious'}","detail":"One fifteenth of local daylight = two day-Ghatis","link_date":selected.isoformat()})
    for i in range(15):
        a=ss+night*i;b=ss+night*(i+1);name=MUHURTA_NAMES[15+i]
        rows.append({"title":name,"date":selected.isoformat(),"time":f"{fmt(a)} – {fmt(b)}","meta":f"Night Muhurta {i+16} · {'Auspicious' if name in MUHURTA_AUSPICIOUS else 'Inauspicious'}","detail":"One fifteenth of local night = two night-Ghatis","link_date":selected.isoformat()})
    return [{"title":"30 Do-Ghati Muhurtas","note":"Classical 30-name sequence; 15 daylight + 15 night Muhurtas, each equal to two local Ghatis.","items":rows}]

def _pakshi_table(selected,paksha):
    if paksha=="Shukla Paksha":
        return BRIGHT[BRIGHT_GROUP[selected.weekday()]]
    return DARK[DARK_GROUP[selected.weekday()]]

def _tier(score):
    if score>=0.60:return "Peak"
    if score>=0.40:return "Good"
    if score>=0.20:return "Neutral"
    if score>=0.10:return "Weak"
    return "Very weak"

def pakshi_sections(selected,lat,lon,tz,bird="Peacock"):
    if bird not in PAKSHI: bird="Peacock"
    sr,ss,nr=sun_events(selected,lat,lon,tz)
    st=panchang.state_at(sr+timedelta(seconds=1));paksha=st["paksha"]
    table=_pakshi_table(selected,paksha)
    sections=[]
    for label,start,end,key in [("Day",sr,ss,"day"),("Night",ss,nr,"night")]:
        major=(end-start)/5;items=[]
        main_seq=table[key][bird]
        for m,main in enumerate(main_seq):
            y0=start+major*m;y1=start+major*(m+1)
            ai=ACT.index(main)
            subacts=[ACT[(ai+s)%5] for s in range(5)]
            cursor=y0
            for s,subact in enumerate(subacts):
                duration=major*SUB_YAMA_SHARE[subact]/144.0
                a=cursor;b=(y1 if s==4 else cursor+duration);cursor=b
                score=ACT_WEIGHT[main]*ACT_WEIGHT[subact]
                items.append({"title":f"{bird} · {main} / {subact}","date":a.date().isoformat(),"time":f"{fmt(a)} – {fmt(b)}","meta":f"{label} Yama {m+1} · {_tier(score)} · {score:.2f}","detail":f"{paksha} · Pulippani mirror-table profile · weighted sub-Yama {SUB_YAMA_SHARE[subact]}/144","link_date":a.date().isoformat(),"start":a.isoformat(),"end":b.isoformat()})
        sections.append({"title":f"{label} Pancha Pakshi · {bird}","note":"Five local solar Yamas with unequal sub-Yamas scaled by the classical activity shares: Ruling 48, Walking 36, Eating 30, Sleeping 18, Dying 12 (total 144).","items":items})
    return sections

def shubha_dates(year,lat,lon,tz):
    good_weekdays={0,2,3,4}
    bad_tithi={4,8,9,14,15}
    good_naks={"Rohini","Mrigashira","Punarvasu","Pushya","Uttara Phalguni","Hasta","Chitra","Anuradha","Uttara Ashadha","Shravana","Dhanishta","Uttara Bhadrapada","Revati"}
    rows=[];d=date(year,1,1)
    while d.year==year:
        sr=rise(d,lat,lon,tz,panchang.astronomy.Body.Sun,panchang.astronomy.Direction.Rise)
        if sr:
            st=panchang.state_at(sr+timedelta(seconds=1))
            if d.weekday() in good_weekdays and st["tithi_number"] not in bad_tithi and st["nakshatra"] in good_naks:
                rows.append({"title":"Generic Shubha Date","date":d.isoformat(),"time":fmt(sr),"meta":f'{d.strftime("%A")} · {st["tithi"]} · {st["nakshatra"]}',"detail":"Tithika conservative generic filter; use ceremony-specific Muhurat engines for ritual decisions.","link_date":d.isoformat()})
        d+=timedelta(days=1)
    return [{"title":f"Generic Shubha Dates {year}","note":"Explicit generic filter only; it is intentionally not presented as a universal traditional Muhurat selector.","items":rows}]

def main():
    p=json.loads(sys.stdin.read() or "{}");slug=str(p.get("slug") or "").strip("/")
    lat=float(p.get("lat",18.5204));lon=float(p.get("lon",73.8567));tzname=p.get("timezone") or "Asia/Kolkata"
    try:tz=ZoneInfo(tzname)
    except ZoneInfoNotFoundError:tz=ZoneInfo("Asia/Kolkata");tzname="Asia/Kolkata"
    selected=datetime.strptime(p.get("date") or datetime.now(tz).strftime("%Y-%m-%d"),"%Y-%m-%d").date()
    if slug in ("muhurat/gowri","panchang/gowri"):title="Gowri Panchangam";sections=gowri(selected,lat,lon,tz)
    elif slug=="muhurat/jain-pachchakkhan":title="Jain Pachchakkhan";sections=pachchakkhan(selected,lat,lon,tz)
    elif slug=="muhurat/do-ghati":title="Do Ghati Muhurat";sections=do_ghati(selected,lat,lon,tz)
    elif slug=="muhurat/pancha-pakshi":title="Pancha Pakshi Activities";sections=pakshi_sections(selected,lat,lon,tz,str(p.get("bird") or "Peacock").title())
    elif slug=="muhurat/shubha-dates":title="Generic Shubha Dates";sections=shubha_dates(selected.year,lat,lon,tz)
    else:raise ValueError("Unsupported Muhurat completion slug")
    count=sum(len(s.get("items",[])) for s in sections)
    print(json.dumps({"ok":True,"family":"muhurat","slug":slug,"title":title,"year":selected.year,
      "summary":f"{count} calculated rows · {tzname}",
      "metrics":[{"label":"Rows","value":str(count),"note":str(selected.year)},{"label":"Solar basis","value":"Local","note":"sunrise/sunset aware"},{"label":"Profile","value":"Explicit","note":"no hidden lineage mixing"}],
      "sections":sections,"engine":{"name":"tithika-muhurat-completion","version":ENGINE_VERSION,"ayanamsha":"Lahiri / Chitrapaksha"}},ensure_ascii=False))
if __name__=="__main__":
    try:main()
    except Exception as exc:
        print(json.dumps({"ok":False,"error":str(exc),"code":"MUHURAT_COMPLETION_FAILED"}));sys.exit(1)
