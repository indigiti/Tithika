#!/usr/bin/env python3
"""Astronomy/reference engine for exact parallels, ecliptic crossings, tropical Indian seasons and zodiac references."""
from __future__ import annotations
import json, math, sys
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
import panchang, planetary

ENGINE_VERSION="1.1.0"
BODIES=["Sun","Moon","Mercury","Venus","Mars","Jupiter","Saturn"]
TROPICAL_SIGNS=["Aries","Taurus","Gemini","Cancer","Leo","Virgo","Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]
SIDEREAL_SIGNS=panchang.RASHI_NAMES
RITUS=[
 ("Vasanta","Meena → Mesha","Spring",330.0),
 ("Grishma","Vrishabha → Mithuna","Summer",30.0),
 ("Varsha","Karka → Simha","Monsoon",90.0),
 ("Sharad","Kanya → Tula","Autumn",150.0),
 ("Hemanta","Vrishchika → Dhanu","Pre-winter",210.0),
 ("Shishira","Makara → Kumbha","Winter",270.0),
]

def fmt(dt): return panchang.fmt(dt,True)

def declination(name,moment):
    lon,lat,_=planetary.tropical_coordinates(name,moment)
    eps=math.radians(23.4392911)
    lo=math.radians(lon); la=math.radians(lat)
    dec=math.asin(math.sin(la)*math.cos(eps)+math.cos(la)*math.sin(eps)*math.sin(lo))
    return math.degrees(dec)

def bisect_zero(fn,left,right,iterations=42):
    fl=fn(left); fr=fn(right)
    if abs(fl)<1e-12:return left
    if abs(fr)<1e-12:return right
    if fl*fr>0: return None
    lo,hi=left,right
    for _ in range(iterations):
        mid=lo+(hi-lo)/2; fm=fn(mid)
        if abs(fm)<1e-12:return mid
        if fl*fm<=0:
            hi=mid;fr=fm
        else:
            lo=mid;fl=fm
    return lo+(hi-lo)/2

def parallel_events(year,tz):
    """Exact geocentric declination equality/opposition events for the classical seven."""
    start=datetime(year,1,1,tzinfo=tz); end=datetime(year+1,1,1,tzinfo=tz)
    step=timedelta(hours=4); rows=[]; seen=set()
    for i,a in enumerate(BODIES):
        for b in BODIES[i+1:]:
            for kind in ("parallel","contra-parallel"):
                fn=(lambda t,a=a,b=b: declination(a,t)-declination(b,t)) if kind=="parallel" else (lambda t,a=a,b=b: declination(a,t)+declination(b,t))
                left=start; fl=fn(left); probe=left+step
                while probe<=end:
                    fp=fn(probe)
                    if fl==0 or fp==0 or fl*fp<0:
                        at=bisect_zero(fn,left,probe)
                        if at and start<=at<end:
                            key=(a,b,kind,round(at.timestamp()/60))
                            if key not in seen:
                                da,db=declination(a,at),declination(b,at)
                                rows.append({
                                  "title":f"{a} {'Parallel' if kind=='parallel' else 'Contra-parallel'} {b}",
                                  "date":at.date().isoformat(),"time":fmt(at),
                                  "meta":f"{da:+.5f}° / {db:+.5f}°",
                                  "detail":f"Exact geocentric declination {'equality' if kind=='parallel' else 'opposition'} refined by root search · {at.isoformat()}",
                                  "link_date":at.date().isoformat()
                                }); seen.add(key)
                    left=probe;fl=fp;probe+=step
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
                fn=lambda t,n=name: latitude(n,t)
                at=bisect_zero(fn,cur,nxt)
                if at:
                    direction="Ascending" if latitude(name,at+timedelta(minutes=5))>0 else "Descending"
                    rows.append({"title":f"{name} {direction} ecliptic crossing","date":at.date().isoformat(),"time":fmt(at),
                     "meta":"Geocentric tropical ecliptic latitude = 0°","detail":at.isoformat(),"link_date":at.date().isoformat()})
            cur=nxt;prev=val
    rows.sort(key=lambda r:(r["date"],r["time"],r["title"]))
    return rows

def sun_tropical_longitude(moment):
    return planetary.tropical_coordinates("Sun",moment)[0]

def signed_target_delta(lon,target):
    return ((lon-target+180.0)%360.0)-180.0

def tropical_ingress(year,target,tz):
    # Search wide enough to bracket the target once in the civil year.
    start=datetime(year,1,1,tzinfo=tz);end=datetime(year+1,1,1,tzinfo=tz)
    left=start; step=timedelta(hours=12)
    fl=signed_target_delta(sun_tropical_longitude(left),target)
    probe=left+step
    while probe<=end:
        fp=signed_target_delta(sun_tropical_longitude(probe),target)
        # Ignore the artificial +/-180 wrap and accept the local zero crossing only.
        if abs(fl-fp)<60 and (fl==0 or fp==0 or fl*fp<0):
            fn=lambda t: signed_target_delta(sun_tropical_longitude(t),target)
            at=bisect_zero(fn,left,probe)
            if at and at.year==year:return at
        left=probe;fl=fp;probe+=step
    return None

def season_rows(year,lat,lon,tz):
    rows=[]
    for name,span,english,target in RITUS:
        at=tropical_ingress(year,target,tz)
        if not at:continue
        rows.append({"title":name,"date":at.date().isoformat(),"time":fmt(at),
          "meta":f"{span} · {english} · tropical zodiac",
          "detail":f"Begins when the tropical Sun reaches {target:.0f}°; local display only, location does not change the astronomical instant.",
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
    if slug=="planets/parallel":title="Planets Mutual Parallel";items=parallel_events(year,tz)
    elif slug=="planets/ecliptic-crossings":title="Planets Ecliptic Crossings";items=crossing_rows(year,tz)
    elif slug=="astronomy/indian-seasons":title="Indian Seasons";items=season_rows(year,lat,lon,tz)
    elif slug=="planets/sidereal-zodiac":title="Sidereal Zodiac";items=zodiac_rows(moment,True)
    elif slug=="planets/tropical-zodiac":title="Tropical Zodiac";items=zodiac_rows(moment,False)
    else:raise ValueError("Unsupported astronomy reference slug")
    print(json.dumps({"ok":True,"family":"astronomy-reference","slug":slug,"title":title,"year":year,
      "summary":f"{len(items)} astronomy/reference row(s) · {tzname}",
      "metrics":[{"label":"Rows","value":str(len(items)),"note":str(year)},{"label":"Coordinates","value":"Geocentric","note":"true ecliptic/equatorial conversion"},{"label":"Search","value":"Root-refined","note":"event-time calculation"}],
      "sections":[{"title":title,"note":"Astronomy uses the vendored Astronomy Engine foundation; Indian Ritus use tropical solar boundaries, while sidereal zodiac routes explicitly use Lahiri.","items":items}],
      "engine":{"name":"tithika-astronomy-reference","version":ENGINE_VERSION,"ayanamsha":"Lahiri only where route semantics are sidereal"}},ensure_ascii=False))
if __name__=="__main__":
    try:main()
    except Exception as exc:
        print(json.dumps({"ok":False,"error":str(exc),"code":"ASTRONOMY_REFERENCE_FAILED"}));sys.exit(1)
