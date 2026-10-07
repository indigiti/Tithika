#!/usr/bin/env python3
"""Completion engine for Gowri, Jain Pachchakkhan, Do-Ghati, Pancha-Pakshi and generic Shubha Dates."""
from __future__ import annotations
import json, sys
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
import panchang

ENGINE_VERSION="1.0.0"
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
MUHURTA_NAMES=["Rudra","Uraga","Mitra","Pitara","Vasu","Ambu","Vishwedeva","Vidhi","Brahma","Indra","Indragni","Daitya","Varuna","Aryama","Bhaga",
"Ishwara","Ajaikapada","Ahirbudhnya","Pusha","Ashwini","Yama","Agni","Brahma","Chandra","Aditi","Brihaspati","Vishnu","Surya","Tvashta","Samirana"]
MUHURTA_AUSPICIOUS={
 "Mitra","Vasu","Ambu","Vishwedeva","Vidhi","Brahma","Indra","Varuna","Aryama",
 "Ahirbudhnya","Pusha","Ashwini","Chandra","Aditi","Brihaspati","Vishnu","Surya","Tvashta","Samirana"
}
PAKSHI=["Vulture","Owl","Crow","Cock","Peacock"]
ACT_SCORE={"Ruling":"Best","Eating":"Good","Walking":"Average","Sleeping":"Bad","Dying":"Very Bad"}
ACT_WEIGHT={"Ruling":6,"Eating":16,"Walking":12,"Sleeping":4,"Dying":10}
SHUKLA_GROUP={6:"A",1:"A",0:"B",2:"B",5:"B",3:"C",4:"D"}
KRISHNA_GROUP={6:"A",1:"A",0:"B",5:"B",2:"C",3:"D",4:"E"}

SHUKLA_DAY={
"A":{"Vulture":["Eating","Walking","Ruling","Sleeping","Dying"],"Owl":["Ruling","Dying","Eating","Walking","Sleeping"],"Crow":["Walking","Sleeping","Dying","Ruling","Eating"],"Cock":["Dying","Ruling","Sleeping","Eating","Walking"],"Peacock":["Sleeping","Eating","Walking","Dying","Ruling"]},
"B":{"Vulture":["Dying","Ruling","Sleeping","Eating","Walking"],"Owl":["Eating","Walking","Ruling","Sleeping","Dying"],"Crow":["Sleeping","Eating","Walking","Dying","Ruling"],"Cock":["Walking","Sleeping","Dying","Ruling","Eating"],"Peacock":["Ruling","Dying","Eating","Walking","Sleeping"]},
"C":{"Vulture":["Sleeping","Eating","Walking","Dying","Ruling"],"Owl":["Walking","Sleeping","Dying","Ruling","Eating"],"Crow":["Eating","Walking","Ruling","Sleeping","Dying"],"Cock":["Ruling","Dying","Eating","Walking","Sleeping"],"Peacock":["Dying","Ruling","Sleeping","Eating","Walking"]},
"D":{"Vulture":["Walking","Sleeping","Dying","Ruling","Eating"],"Owl":["Dying","Ruling","Sleeping","Eating","Walking"],"Crow":["Ruling","Dying","Eating","Walking","Sleeping"],"Cock":["Eating","Walking","Ruling","Sleeping","Dying"],"Peacock":["Sleeping","Eating","Walking","Dying","Ruling"]},
}
SHUKLA_NIGHT={
"A":{"Vulture":["Dying","Ruling","Sleeping","Eating","Walking"],"Owl":["Sleeping","Eating","Walking","Dying","Ruling"],"Crow":["Eating","Walking","Ruling","Sleeping","Dying"],"Cock":["Walking","Sleeping","Dying","Ruling","Eating"],"Peacock":["Ruling","Dying","Eating","Walking","Sleeping"]},
"B":{"Vulture":["Walking","Sleeping","Dying","Ruling","Eating"],"Owl":["Dying","Ruling","Sleeping","Eating","Walking"],"Crow":["Ruling","Dying","Eating","Walking","Sleeping"],"Cock":["Eating","Walking","Ruling","Sleeping","Dying"],"Peacock":["Sleeping","Eating","Walking","Dying","Ruling"]},
"C":{"Vulture":["Ruling","Dying","Eating","Walking","Sleeping"],"Owl":["Eating","Walking","Ruling","Sleeping","Dying"],"Crow":["Dying","Ruling","Sleeping","Eating","Walking"],"Cock":["Sleeping","Eating","Walking","Dying","Ruling"],"Peacock":["Walking","Sleeping","Dying","Ruling","Eating"]},
"D":{"Vulture":["Eating","Walking","Ruling","Sleeping","Dying"],"Owl":["Walking","Sleeping","Dying","Ruling","Eating"],"Crow":["Sleeping","Eating","Walking","Dying","Ruling"],"Cock":["Dying","Ruling","Sleeping","Eating","Walking"],"Peacock":["Ruling","Dying","Eating","Walking","Sleeping"]},
}
# Dark-half main-activity tables. Day groups C/D/E are aligned to the published
# Pancha Pakshi Mirror ordering (Cock, Vulture, Owl, Peacock, Crow).
KRISHNA_DAY={
"A":{"Vulture":["Walking","Ruling","Eating","Dying","Sleeping"],"Owl":["Dying","Sleeping","Ruling","Walking","Eating"],"Crow":["Eating","Dying","Sleeping","Ruling","Walking"],"Cock":["Ruling","Eating","Walking","Sleeping","Dying"],"Peacock":["Sleeping","Walking","Dying","Eating","Ruling"]},
"B":{"Vulture":["Sleeping","Walking","Dying","Eating","Ruling"],"Owl":["Eating","Dying","Walking","Ruling","Sleeping"],"Crow":["Walking","Ruling","Eating","Sleeping","Dying"],"Cock":["Dying","Sleeping","Ruling","Walking","Eating"],"Peacock":["Ruling","Eating","Sleeping","Dying","Walking"]},
"C":{"Vulture":["Dying","Sleeping","Walking","Ruling","Eating"],"Owl":["Ruling","Eating","Dying","Sleeping","Walking"],"Crow":["Sleeping","Walking","Ruling","Eating","Dying"],"Cock":["Eating","Ruling","Sleeping","Dying","Walking"],"Peacock":["Walking","Dying","Eating","Walking","Ruling"]},
"D":{"Vulture":["Ruling","Eating","Sleeping","Walking","Dying"],"Owl":["Sleeping","Walking","Eating","Dying","Ruling"],"Crow":["Dying","Ruling","Walking","Eating","Sleeping"],"Cock":["Walking","Dying","Ruling","Sleeping","Eating"],"Peacock":["Eating","Sleeping","Dying","Ruling","Walking"]},
"E":{"Vulture":["Eating","Dying","Ruling","Sleeping","Walking"],"Owl":["Walking","Ruling","Sleeping","Eating","Dying"],"Crow":["Ruling","Sleeping","Dying","Walking","Eating"],"Cock":["Sleeping","Eating","Walking","Dying","Ruling"],"Peacock":["Dying","Walking","Eating","Ruling","Sleeping"]},
}
KRISHNA_NIGHT={
"A":{"Vulture":["Sleeping","Walking","Dying","Eating","Ruling"],"Owl":["Eating","Dying","Walking","Ruling","Sleeping"],"Crow":["Walking","Ruling","Eating","Sleeping","Dying"],"Cock":["Dying","Sleeping","Ruling","Dying","Eating"],"Peacock":["Ruling","Eating","Sleeping","Walking","Walking"]},
"B":{"Vulture":["Ruling","Eating","Sleeping","Walking","Dying"],"Owl":["Sleeping","Walking","Dying","Eating","Ruling"],"Crow":["Dying","Sleeping","Ruling","Dying","Eating"],"Cock":["Eating","Ruling","Walking","Sleeping","Walking"],"Peacock":["Walking","Dying","Eating","Ruling","Sleeping"]},
"C":{"Vulture":["Eating","Ruling","Sleeping","Dying","Walking"],"Owl":["Walking","Dying","Eating","Ruling","Sleeping"],"Crow":["Dying","Eating","Walking","Sleeping","Ruling"],"Cock":["Ruling","Sleeping","Dying","Walking","Eating"],"Peacock":["Sleeping","Walking","Ruling","Eating","Dying"]},
"D":{"Vulture":["Dying","Walking","Ruling","Eating","Sleeping"],"Owl":["Ruling","Eating","Sleeping","Walking","Dying"],"Crow":["Sleeping","Dying","Eating","Ruling","Walking"],"Cock":["Eating","Ruling","Walking","Dying","Ruling"],"Peacock":["Walking","Sleeping","Dying","Sleeping","Eating"]},
"E":{"Vulture":["Walking","Sleeping","Dying","Ruling","Eating"],"Owl":["Dying","Eating","Ruling","Sleeping","Walking"],"Crow":["Eating","Walking","Sleeping","Dying","Ruling"],"Cock":["Ruling","Dying","Eating","Walking","Sleeping"],"Peacock":["Sleeping","Ruling","Walking","Eating","Dying"]},
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
    rows=[]
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
    for name,t,basis in vals:
        rows.append({"title":name,"date":selected.isoformat(),"time":fmt(t),"meta":basis,"detail":t.isoformat(),"link_date":selected.isoformat()})
    return [{"title":"Jain Pachchakkhan","note":"Solar Prahar/Ghati profile; Sangh-specific practice can add local constraints.","items":rows}]

def do_ghati(selected,lat,lon,tz):
    sr,ss,nr=sun_events(selected,lat,lon,tz)
    rows=[]; day=(ss-sr)/15; night=(nr-ss)/15
    for i in range(15):
        a=sr+day*i;b=sr+day*(i+1);name=MUHURTA_NAMES[i]
        rows.append({"title":name,"date":selected.isoformat(),"time":f"{fmt(a)} – {fmt(b)}","meta":f"Day Muhurta {i+1} · 2 Ghati · {'Auspicious' if name in MUHURTA_AUSPICIOUS else 'Inauspicious'}","detail":"One fifteenth of local daylight","link_date":selected.isoformat()})
    for i in range(15):
        a=ss+night*i;b=ss+night*(i+1);name=MUHURTA_NAMES[15+i]
        rows.append({"title":name,"date":selected.isoformat(),"time":f"{fmt(a)} – {fmt(b)}","meta":f"Night Muhurta {i+16} · 2 Ghati · {'Auspicious' if name in MUHURTA_AUSPICIOUS else 'Inauspicious'}","detail":"One fifteenth of local night","link_date":selected.isoformat()})
    return [{"title":"30 Do-Ghati Muhurtas","note":"15 daylight + 15 night Muhurtas; canonical 30-name sequence and two-local-Ghati division.","items":rows}]

def pakshi_group(weekday,paksha):
    return (SHUKLA_GROUP if paksha=="Shukla Paksha" else KRISHNA_GROUP)[weekday]

def pakshi_matrix(weekday,paksha,label):
    group=pakshi_group(weekday,paksha)
    tables=(SHUKLA_DAY,SHUKLA_NIGHT) if paksha=="Shukla Paksha" else (KRISHNA_DAY,KRISHNA_NIGHT)
    return tables[0 if label=="Day" else 1][group],group

def pakshi_sections(selected,lat,lon,tz,focus_bird="Peacock"):
    sr,ss,nr=sun_events(selected,lat,lon,tz)
    st=panchang.state_at(sr+timedelta(seconds=1));paksha=st["paksha"]
    if focus_bird not in PAKSHI: focus_bird="Peacock"
    sections=[]
    for label,start,end in [("Day",sr,ss),("Night",ss,nr)]:
        matrix,group=pakshi_matrix(selected.weekday(),paksha,label)
        yama=(end-start)/5;items=[]
        for m in range(5):
            a=start+yama*m;b=start+yama*(m+1)
            activity=matrix[focus_bird][m]
            items.append({"title":f"{focus_bird} · {activity}","date":a.date().isoformat(),
              "time":f"{fmt(a)} – {fmt(b)}","meta":f"{label} Yama {m+1} · {ACT_SCORE[activity]} · group {group}",
              "detail":f'{paksha} · sourced Pancha Pakshi mirror-table major activity',"link_date":a.date().isoformat()})
        sections.append({"title":f"{label} Pancha Pakshi · {focus_bird}",
          "note":"Five exact solar Yamas using the sourced mirror-table major activities. Sūkṣma sub-periods are intentionally not inferred from an unsourced micro-order.",
          "items":items})
    return sections

def shubha_dates(year,lat,lon,tz):
    good_weekdays={0,2,3,4}
    bad_tithi={4,8,9,14,15}
    good_naks={"Rohini","Mrigashira","Punarvasu","Pushya","Uttara Phalguni","Hasta","Chitra","Anuradha","Uttara Ashadha","Shravana","Dhanishta","Uttara Bhadrapada","Revati"}
    rows=[]; d=date(year,1,1)
    while d.year==year:
        sr=rise(d,lat,lon,tz,panchang.astronomy.Body.Sun,panchang.astronomy.Direction.Rise)
        if sr:
            st=panchang.state_at(sr+timedelta(seconds=1))
            if d.weekday() in good_weekdays and st["tithi_number"] not in bad_tithi and st["nakshatra"] in good_naks:
                rows.append({"title":"Generic Shubha Date","date":d.isoformat(),"time":fmt(sr),"meta":f'{d.strftime("%A")} · {st["tithi"]} · {st["nakshatra"]}',"detail":"Conservative generic filter only; ceremony-specific Muhurat profiles remain preferred.","link_date":d.isoformat()})
        d+=timedelta(days=1)
    return [{"title":f"Generic Shubha Dates {year}","note":"Conservative weekday + Tithi + Nakshatra acceptance profile; not a substitute for a ceremony-specific Muhurat.","items":rows}]

def main():
    p=json.loads(sys.stdin.read() or "{}"); slug=str(p.get("slug") or "").strip("/")
    lat=float(p.get("lat",18.5204));lon=float(p.get("lon",73.8567));tzname=p.get("timezone") or "Asia/Kolkata"
    try: tz=ZoneInfo(tzname)
    except ZoneInfoNotFoundError: tz=ZoneInfo("Asia/Kolkata");tzname="Asia/Kolkata"
    selected=datetime.strptime(p.get("date") or datetime.now(tz).strftime("%Y-%m-%d"),"%Y-%m-%d").date()
    if slug in ("muhurat/gowri","panchang/gowri"): title="Gowri Panchangam";sections=gowri(selected,lat,lon,tz)
    elif slug=="muhurat/jain-pachchakkhan": title="Jain Pachchakkhan";sections=pachchakkhan(selected,lat,lon,tz)
    elif slug=="muhurat/do-ghati": title="Do Ghati Muhurat";sections=do_ghati(selected,lat,lon,tz)
    elif slug=="muhurat/pancha-pakshi": title="Pancha Pakshi Activities";sections=pakshi_sections(selected,lat,lon,tz,str(p.get("bird") or "Peacock").title())
    elif slug=="muhurat/shubha-dates": title="Shubha Dates";sections=shubha_dates(selected.year,lat,lon,tz)
    else: raise ValueError("Unsupported Muhurat completion slug")
    count=sum(len(s.get("items",[])) for s in sections)
    print(json.dumps({"ok":True,"family":"muhurat","slug":slug,"title":title,"year":selected.year,
      "summary":f"{count} calculated rows · {tzname}",
      "metrics":[{"label":"Rows","value":str(count),"note":str(selected.year)},{"label":"Solar basis","value":"Local","note":"sunrise/sunset aware"},{"label":"Profile","value":"Versioned","note":"tradition-specific"}],
      "sections":sections,"engine":{"name":"tithika-muhurat-completion","version":ENGINE_VERSION,"ayanamsha":"Lahiri / Chitrapaksha"}},ensure_ascii=False))
if __name__=="__main__":
    try: main()
    except Exception as exc:
        print(json.dumps({"ok":False,"error":str(exc),"code":"MUHURAT_COMPLETION_FAILED"}));sys.exit(1)
