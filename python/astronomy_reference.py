#!/usr/bin/env python3
"""Astronomy/reference completion engine for parallels, ecliptic crossings, seasons and zodiac references."""
from __future__ import annotations
import json, math, sys
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
import panchang, planetary, sankranti

ENGINE_VERSION="1.0.0"
BODIES=["Sun","Moon","Mercury","Venus","Mars","Jupiter","Saturn"]
TROPICAL_SIGNS=["Aries","Taurus","Gemini","Cancer","Leo","Virgo","Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]
SIDEREAL_SIGNS=panchang.RASHI_NAMES
RITUS=[
 ("Vasanta","Meena → Mesha","Spring"),("Grishma","Vrishabha → Mithuna","Summer"),
 ("Varsha","Karka → Simha","Monsoon"),("Sharad","Kanya → Tula","Autumn"),
 ("Hemanta","Vrishchika → Dhanu","Pre-winter"),("Shishira","Makara → Kumbha","Winter")
]

def declination(name,moment):
    lon,lat,_=planetary.tropical_coordinates(name,moment)
    eps=math.radians(23.4392911);lo=math.radians(lon);la=math.radians(lat)
    dec=math.asin(math.sin(la)*math.cos(eps)+math.cos(la)*math.sin(eps)*math.sin(lo))
    return math.degrees(dec)

def parallel_metric(a,b,moment,contra=False):
    da,db=declination(a,moment),declination(b,moment)
    return (da+db if contra else da-db),da,db

def refine_parallel(a,b,left,right,contra=False):
    fl=parallel_metric(a,b,left,contra)[0]
    lo,hi=left,right
    for _ in range(42):
        mid=lo+(hi-lo)/2
        fm=parallel_metric(a,b,mid,contra)[0]
        if fl==0 or fl*fm<=0:
            hi=mid
        else:
            lo=mid;fl=fm
    return hi

def parallel_rows(year,tz):
    rows=[];start=datetime(year,1,1,tzinfo=tz);end=datetime(year+1,1,1,tzinfo=tz);step=timedelta(hours=6)
    for i,a in enumerate(BODIES):
        for b in BODIES[i+1:]:
            for contra in (False,True):
                cur=start-step;prev=parallel_metric(a,b,cur,contra)[0]
                last_event=None
                while cur<end:
                    nxt=min(cur+step,end);val=parallel_metric(a,b,nxt,contra)[0]
                    if prev==0 or prev*val<0:
                        at=refine_parallel(a,b,cur,nxt,contra)
                        if start<=at<end and (last_event is None or at-last_event>timedelta(hours=1)):
                            _,da,db=parallel_metric(a,b,at,contra)
                            rows.append({"title":f"{a} {'Contra-parallel' if contra else 'Parallel'} {b}",
                              "date":at.date().isoformat(),"time":at.strftime("%H:%M:%S"),
                              "meta":f"{da:+.5f}° / {db:+.5f}°",
                              "detail":f"Exact geocentric declination {'sum' if contra else 'difference'} refined to zero; residual {abs(da+db if contra else da-db):.8f}°.",
                              "link_date":at.date().isoformat()})
                            last_event=at
                    cur=nxt;prev=val
    rows.sort(key=lambda r:(r["date"],r["time"],r["title"]))
    return rows

def latitude(name,moment): return planetary.tropical_coordinates(name,moment)[1]

def crossing_rows(year,tz):
    rows=[]
    for name in ["Moon","Mercury","Venus","Mars","Jupiter","Saturn"]:
        cur=datetime(year,1,1,tzinfo=tz);end=datetime(year+1,1,1,tzinfo=tz);step=timedelta(hours=12);prev=latitude(name,cur)
        while cur<end:
            nxt=min(end,cur+step);val=latitude(name,nxt)
            if prev==0 or prev*val<0:
                lo,hi=cur,nxt
                for _ in range(28):
                    mid=lo+(hi-lo)/2;m=latitude(name,mid)
                    if (latitude(name,lo)<=0 and m<=0) or (latitude(name,lo)>=0 and m>=0):lo=mid
                    else:hi=mid
                at=hi;direction="Ascending" if latitude(name,at+timedelta(minutes=5))>0 else "Descending"
                rows.append({"title":f"{name} {direction} ecliptic crossing","date":at.date().isoformat(),"time":at.strftime("%H:%M"),
                 "meta":"Geocentric tropical ecliptic latitude = 0°","detail":at.isoformat(),"link_date":at.date().isoformat()})
            cur=nxt;prev=val
    rows.sort(key=lambda r:(r.get("date",""),r.get("time","")))
    return rows

def tropical_ritu_sector(moment):
    lon=planetary.tropical_coordinates("Sun",moment)[0]
    return int(((lon+30.0)%360.0)//60.0)

def refine_ritu(left,right,old_sector):
    lo,hi=left,right
    for _ in range(44):
        mid=lo+(hi-lo)/2
        if tropical_ritu_sector(mid)==old_sector: lo=mid
        else: hi=mid
    return hi

def season_rows(year,lat,lon,tz):
    start=datetime(year,1,1,tzinfo=tz);end=datetime(year+1,1,1,tzinfo=tz);step=timedelta(hours=12)
    names=[
      ("Vasanta","Meena → Mesha","Spring"),("Grishma","Vrishabha → Mithuna","Summer"),
      ("Varsha","Karka → Simha","Monsoon"),("Sharad","Kanya → Tula","Autumn"),
      ("Hemanta","Vrishchika → Dhanu","Pre-winter"),("Shishira","Makara → Kumbha","Winter")]
    rows=[];cur=start-step;old=tropical_ritu_sector(cur)
    while cur<end:
        nxt=min(cur+step,end);new=tropical_ritu_sector(nxt)
        if new!=old:
            at=refine_ritu(cur,nxt,old)
            if start<=at<end:
                name,span,english=names[new]
                rows.append({"title":name,"date":at.date().isoformat(),"time":at.strftime("%H:%M:%S"),
                  "meta":f"{span} · {english}",
                  "detail":"Indian six-Ritu boundary from tropical solar longitude; each Ritu spans two tropical zodiac signs.",
                  "link_date":at.date().isoformat()})
            old=new
        cur=nxt
    return rows

def zodiac_rows(moment,sidereal):
    t=panchang.astronomy_time(moment);aya=panchang.lahiri_ayanamsha_deg(t,True);rows=[]
    names=SIDEREAL_SIGNS if sidereal else TROPICAL_SIGNS
    for i,n in enumerate(names):
        a=i*30.0;b=(i+1)*30.0
        detail=(f"Tropical longitude {a:.0f}°–{b:.0f}°" if not sidereal else f"Lahiri sidereal longitude {a:.0f}°–{b:.0f}°; tropical equivalent shifted by current ayanamsha {aya:.4f}°")
        rows.append({"title":n,"meta":f"{a:.0f}°–{b:.0f}°","detail":detail})
    return rows

def main():
    p=json.loads(sys.stdin.read() or "{}");slug=str(p.get("slug") or "").strip("/")
    lat=float(p.get("lat",18.5204));lon=float(p.get("lon",73.8567));tzname=p.get("timezone") or "Asia/Kolkata"
    try:tz=ZoneInfo(tzname)
    except ZoneInfoNotFoundError:tz=ZoneInfo("Asia/Kolkata");tzname="Asia/Kolkata"
    d=str(p.get("date") or datetime.now(tz).strftime("%Y-%m-%d"));tv=str(p.get("time") or "12:00:00")
    if len(tv)==5:tv+=":00"
    moment=datetime.strptime(d+" "+tv,"%Y-%m-%d %H:%M:%S").replace(tzinfo=tz);year=moment.year
    if slug=="planets/parallel":title="Planets Mutual Parallel";items=parallel_rows(year,tz)
    elif slug=="planets/ecliptic-crossings":title="Planets Ecliptic Crossings";items=crossing_rows(year,tz)
    elif slug=="astronomy/indian-seasons":title="Indian Seasons";items=season_rows(year,lat,lon,tz)
    elif slug=="planets/sidereal-zodiac":title="Sidereal Zodiac";items=zodiac_rows(moment,True)
    elif slug=="planets/tropical-zodiac":title="Tropical Zodiac";items=zodiac_rows(moment,False)
    else:raise ValueError("Unsupported astronomy reference slug")
    print(json.dumps({"ok":True,"family":"astronomy-reference","slug":slug,"title":title,"year":year,
      "summary":f"{len(items)} astronomy/reference row(s) · {tzname}",
      "metrics":[{"label":"Rows","value":str(len(items)),"note":str(year)},{"label":"Coordinates","value":"Geocentric","note":"true ecliptic of date"},{"label":"Ayanamsha","value":"Lahiri","note":"sidereal routes"}],
      "sections":[{"title":title,"note":"Reference geometry uses the same vendored Astronomy Engine foundation as Tithika planetary calculations.","items":items}],
      "engine":{"name":"tithika-astronomy-reference","version":ENGINE_VERSION,"ayanamsha":"Lahiri / Chitrapaksha"}},ensure_ascii=False))
if __name__=="__main__":
    try:main()
    except Exception as exc:
        print(json.dumps({"ok":False,"error":str(exc),"code":"ASTRONOMY_REFERENCE_FAILED"}));sys.exit(1)
