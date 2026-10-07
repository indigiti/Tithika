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
PAKSHI=["Vulture","Owl","Crow","Cock","Peacock"]
ACT=["Ruling","Eating","Walking","Sleeping","Dying"]
ACT_SCORE={"Ruling":"Best","Eating":"Good","Walking":"Average","Sleeping":"Bad","Dying":"Very Bad"}

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
        a=sr+day*i;b=sr+day*(i+1)
        rows.append({"title":MUHURTA_NAMES[i],"date":selected.isoformat(),"time":f"{fmt(a)} – {fmt(b)}","meta":f"Day Muhurta {i+1} · 2 Ghati","detail":"One fifteenth of local daylight","link_date":selected.isoformat()})
    for i in range(15):
        a=ss+night*i;b=ss+night*(i+1)
        rows.append({"title":MUHURTA_NAMES[15+i],"date":selected.isoformat(),"time":f"{fmt(a)} – {fmt(b)}","meta":f"Night Muhurta {i+16} · 2 Ghati","detail":"One fifteenth of local night","link_date":selected.isoformat()})
    return [{"title":"30 Do-Ghati Muhurtas","note":"15 daylight + 15 night Muhurtas; each interval equals two local Ghatis.","items":rows}]

def pakshi_sections(selected,lat,lon,tz):
    sr,ss,nr=sun_events(selected,lat,lon,tz)
    st=panchang.state_at(sr+timedelta(seconds=1))
    paksha_shift=0 if st["paksha"]=="Shukla Paksha" else 2
    weekday_shift=(selected.weekday()+paksha_shift)%5
    sections=[]
    for label,start,end,halfshift in [("Day",sr,ss,0),("Night",ss,nr,2)]:
        major=(end-start)/5; items=[]
        for m in range(5):
            sub=major/5
            for s in range(5):
                a=start+major*m+sub*s;b=a+sub
                bird=PAKSHI[(s+weekday_shift+halfshift)%5]
                activity=ACT[(m+s+weekday_shift+halfshift)%5]
                items.append({"title":f"{bird} · {activity}","date":a.date().isoformat(),"time":f"{fmt(a)} – {fmt(b)}","meta":f"{label} · {ACT_SCORE[activity]}","detail":f'{st["paksha"]} · versioned Tithika Pakshi-cycle profile',"link_date":a.date().isoformat()})
        sections.append({"title":f"{label} Pancha Pakshi","note":"Five major periods × five subperiods; activity/bird cycle is explicit and versioned.","items":items})
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
    elif slug=="muhurat/pancha-pakshi": title="Pancha Pakshi Activities";sections=pakshi_sections(selected,lat,lon,tz)
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
