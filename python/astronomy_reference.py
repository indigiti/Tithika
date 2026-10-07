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

def refine_declination_root(a,b,fa,fb,contra=False):
    for _ in range(42):
        mid=a+(b-a)/2
        dm={x:declination(x,mid) for x in BODIES}
        # caller stores names on function attributes to avoid duplicate closure plumbing
        va=dm[refine_declination_root.pa]; vb=dm[refine_declination_root.pb]
        fm=va+vb if contra else va-vb
        if fa*fm<=0:
            b=mid;fb=fm
        else:
            a=mid;fa=fm
    return a+(b-a)/2

def parallel_rows(moment):
    year=moment.year; tz=moment.tzinfo
    start=datetime(year,1,1,tzinfo=tz);end=datetime(year+1,1,1,tzinfo=tz)
    rows=[];step=timedelta(hours=6)
    for i,a_name in enumerate(BODIES):
        for b_name in BODIES[i+1:]:
            refine_declination_root.pa=a_name;refine_declination_root.pb=b_name
            cur=start
            da=declination(a_name,cur);db=declination(b_name,cur)
            fp=da-db;fc=da+db
            while cur<end:
                nxt=min(end,cur+step);na=declination(a_name,nxt);nb=declination(b_name,nxt)
                np=na-nb;nc=na+nb
                for contra,f0,f1 in ((False,fp,np),(True,fc,nc)):
                    if f0==0 or f0*f1<0:
                        at=refine_declination_root(cur,nxt,f0,f1,contra)
                        aa=declination(a_name,at);bb=declination(b_name,at)
                        if not rows or not any(r["title"]==f"{a_name} {'Contra-parallel' if contra else 'Parallel'} {b_name}" and abs((datetime.fromisoformat(r["detail"])-at).total_seconds())<3600 for r in rows):
                            rows.append({"title":f"{a_name} {'Contra-parallel' if contra else 'Parallel'} {b_name}","date":at.date().isoformat(),
                              "time":at.strftime("%H:%M"),"meta":f"{aa:+.5f}° / {bb:+.5f}°",
                              "detail":at.isoformat(),"link_date":at.date().isoformat()})
                cur=nxt;fp=np;fc=nc
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

def tropical_solar_ingress(year,longitude,tz):
    # Search a window that safely covers the target tropical solar longitude.
    approx={330:(2,1),30:(4,1),90:(6,1),150:(8,1),210:(10,1),270:(12,1)}[longitude]
    start=datetime(year,approx[0],approx[1],tzinfo=tz)-timedelta(days=25)
    found=panchang.astronomy.SearchSunLongitude(float(longitude),panchang.astronomy_time(start),55.0)
    if found is None: return None
    return panchang.datetime_from_astronomy(found,tz)

def season_rows(year,lat,lon,tz):
    starts=[330,30,90,150,210,270]
    rows=[]
    for (name,span,english),lon in zip(RITUS,starts):
        at=tropical_solar_ingress(year,lon,tz)
        if at is None: continue
        rows.append({"title":name,"date":at.date().isoformat(),"time":panchang.fmt(at,True),
          "meta":f"{span} · {english}","detail":f"Tropical solar longitude {lon}° boundary.","link_date":at.date().isoformat()})
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
    if slug=="planets/parallel":title="Planets Mutual Parallel";items=parallel_rows(moment)
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
