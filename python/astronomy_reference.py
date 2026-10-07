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

def refine_declination_root(a,b,body_a,body_b,contra=False):
    def metric(t):
        da=declination(body_a,t);db=declination(body_b,t)
        return da+db if contra else da-db
    fa=metric(a)
    for _ in range(45):
        mid=a+(b-a)/2;fm=metric(mid)
        if abs(fm)<1e-9:return mid
        if fa==0 or fa*fm<=0:b=mid
        else:a=mid;fa=fm
    return a+(b-a)/2

def parallel_rows(year,tz):
    """Search exact mutual parallel and contra-parallel declination instants."""
    rows=[];start=datetime(year,1,1,tzinfo=tz);end=datetime(year+1,1,1,tzinfo=tz)
    step=timedelta(hours=6)
    for i,a_name in enumerate(BODIES):
        for b_name in BODIES[i+1:]:
            cur=start;da0=declination(a_name,cur);db0=declination(b_name,cur)
            prev_parallel=da0-db0;prev_contra=da0+db0
            while cur<end:
                nxt=min(end,cur+step);da1=declination(a_name,nxt);db1=declination(b_name,nxt)
                for contra,f0,f1 in ((False,prev_parallel,da1-db1),(True,prev_contra,da1+db1)):
                    if f0==0 or f0*f1<0:
                        root=cur if f0==0 else refine_declination_root(cur,nxt,a_name,b_name,contra)
                        da=declination(a_name,root);db=declination(b_name,root)
                        sep=abs(da+db if contra else da-db)
                        # Avoid duplicate roots on adjacent brackets.
                        if not any(x["title"]==f"{a_name} {'Contra-parallel' if contra else 'Parallel'} {b_name}" and abs((datetime.fromisoformat(x["instant"])-root).total_seconds())<1800 for x in rows):
                            rows.append({"title":f"{a_name} {'Contra-parallel' if contra else 'Parallel'} {b_name}",
                              "date":root.date().isoformat(),"time":root.strftime("%H:%M:%S"),"instant":root.isoformat(),
                              "meta":f"{da:+.6f}° / {db:+.6f}°","detail":f"Exact declination root; residual {sep:.9f}°.",
                              "link_date":root.date().isoformat()})
                cur=nxt;prev_parallel=da1-db1;prev_contra=da1+db1
    rows.sort(key=lambda r:r["instant"])
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

def tropical_ingress(year,target_lon,tz):
    # SearchSunLongitude is apparent geocentric tropical solar longitude.
    # Seed shortly before the expected annual boundary.
    seeds={330:(year,2,10),30:(year,4,10),90:(year,6,10),150:(year,8,10),210:(year,10,10),270:(year,12,10)}
    y,m,d=seeds[target_lon]
    t=panchang.astronomy.SearchSunLongitude(
        float(target_lon),panchang.astronomy_time(datetime(y,m,d,tzinfo=tz)),35.0
    )
    if t is None: raise ValueError(f"Tropical solar ingress {target_lon}° unavailable")
    return panchang.datetime_from_astronomy(t,tz)

def season_rows(year,lat,lon,tz):
    # Indian six-Ritu reference follows tropical two-sign seasons:
    # Vasanta 330°, Grishma 30°, Varsha 90°, Sharad 150°,
    # Hemanta 210°, Shishira 270°.
    starts=[330,30,90,150,210,270];rows=[]
    for (name,span,english),lon0 in zip(RITUS,starts):
        at=tropical_ingress(year,lon0,tz)
        rows.append({"title":name,"date":at.date().isoformat(),"time":at.strftime("%I:%M %p").lstrip("0"),
          "instant":at.isoformat(),"meta":f"{span} · {english} · tropical {lon0}°",
          "detail":"Tropical solar-longitude boundary calculated with Astronomy Engine; location only changes displayed local time.",
          "link_date":at.date().isoformat()})
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
