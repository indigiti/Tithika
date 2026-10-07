#!/usr/bin/env python3
"""Astronomy/reference engine for exact declination parallels, ecliptic crossings, Indian Ritus and zodiac references."""
from __future__ import annotations
import calendar, json, math, sys
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
import panchang, planetary

ENGINE_VERSION="1.1.0"
BODIES=["Sun","Moon","Mercury","Venus","Mars","Jupiter","Saturn"]
TROPICAL_SIGNS=["Aries","Taurus","Gemini","Cancer","Leo","Virgo","Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]
SIDEREAL_SIGNS=panchang.RASHI_NAMES
RITUS=[
 ("Vasanta","Meena → Mesha","Spring",11),
 ("Grishma","Vrishabha → Mithuna","Summer",1),
 ("Varsha","Karka → Simha","Monsoon",3),
 ("Sharad","Kanya → Tula","Autumn",5),
 ("Hemanta","Vrishchika → Dhanu","Pre-winter",7),
 ("Shishira","Makara → Kumbha","Winter",9),
]

def declination(name,moment):
    """True-equator-of-date declination from true ecliptic-of-date lon/lat."""
    lon,lat,_=planetary.tropical_coordinates(name,moment)
    t=panchang.astronomy_time(moment)
    eps=math.radians(panchang.astronomy.e_tilt(t).tobl)
    lo=math.radians(lon);la=math.radians(lat)
    dec=math.asin(math.sin(la)*math.cos(eps)+math.cos(la)*math.sin(eps)*math.sin(lo))
    return math.degrees(dec)

def _bisect_root(func,left,right,iterations=38):
    fl=func(left);fr=func(right)
    if abs(fl)<1e-12:return left
    if abs(fr)<1e-12:return right
    for _ in range(iterations):
        mid=left+(right-left)/2;fm=func(mid)
        if abs(fm)<1e-10:return mid
        if (fl<=0<=fm) or (fl>=0>=fm):
            right=mid;fr=fm
        else:
            left=mid;fl=fm
    return right

def parallel_events(year,month,tz):
    """Exact monthly parallel/contra-parallel declination roots."""
    start=datetime(year,month,1,tzinfo=tz)
    end=datetime(year+1,1,1,tzinfo=tz) if month==12 else datetime(year,month+1,1,tzinfo=tz)
    step=timedelta(hours=3);rows=[];seen=set()
    for i,a in enumerate(BODIES):
        for b in BODIES[i+1:]:
            for mode in ("parallel","contra-parallel"):
                def diff(t):
                    da,db=declination(a,t),declination(b,t)
                    return da-db if mode=="parallel" else da+db
                cur=start;prev=diff(cur)
                while cur<end:
                    nxt=min(end,cur+step);val=diff(nxt)
                    if prev==0 or val==0 or prev*val<0:
                        at=_bisect_root(diff,cur,nxt)
                        if start<=at<end:
                            da,db=declination(a,at),declination(b,at)
                            # Reject the wrong geometry at an equator crossing:
                            # parallel requires same-sign declinations; contra requires opposite.
                            geometry=(da*db>=0) if mode=="parallel" else (da*db<=0)
                            key=(a,b,mode,at.strftime("%Y-%m-%dT%H:%M"))
                            if geometry and key not in seen:
                                seen.add(key)
                                rows.append({
                                  "title":f"{a} {'Parallel' if mode=='parallel' else 'Contra-parallel'} {b}",
                                  "date":at.date().isoformat(),"time":panchang.fmt(at,True),
                                  "meta":f"{da:+.6f}° / {db:+.6f}°",
                                  "detail":f"Exact geocentric true-equator-of-date declination root · residual {abs(diff(at)):.8f}°",
                                  "link_date":at.date().isoformat(),"datetime":at.isoformat(),"parallel_type":mode
                                })
                    cur=nxt;prev=val
    rows.sort(key=lambda r:r["datetime"])
    return rows

def latitude(name,moment):
    return planetary.tropical_coordinates(name,moment)[1]

def crossing_rows(year,tz):
    rows=[]
    for name in ["Moon","Mercury","Venus","Mars","Jupiter","Saturn"]:
        cur=datetime(year,1,1,tzinfo=tz);end=datetime(year+1,1,1,tzinfo=tz);step=timedelta(hours=12);prev=latitude(name,cur)
        while cur<end:
            nxt=min(end,cur+step);val=latitude(name,nxt)
            if prev==0 or val==0 or prev*val<0:
                at=_bisect_root(lambda t:latitude(name,t),cur,nxt)
                direction="Ascending" if latitude(name,at+timedelta(minutes=5))>0 else "Descending"
                rows.append({"title":f"{name} {direction} ecliptic crossing","date":at.date().isoformat(),"time":panchang.fmt(at,True),
                 "meta":"Geocentric true-ecliptic latitude = 0°","detail":at.isoformat(),"link_date":at.date().isoformat(),"datetime":at.isoformat()})
            cur=nxt;prev=val
    rows.sort(key=lambda r:r["datetime"])
    return rows

def tropical_sun_sign(moment):
    lon,_,_=planetary.tropical_coordinates("Sun",moment)
    return int(lon//30.0)%12

def _refine_sun_ingress(left,right,old_sign):
    lo,hi=left,right
    for _ in range(44):
        mid=lo+(hi-lo)/2
        if tropical_sun_sign(mid)==old_sign:lo=mid
        else:hi=mid
    return hi

def tropical_ingresses(year,tz):
    cur=datetime(year-1,12,1,tzinfo=tz);end=datetime(year+1,3,1,tzinfo=tz);step=timedelta(hours=12)
    old=tropical_sun_sign(cur);rows=[]
    while cur<end:
        nxt=min(end,cur+step);new=tropical_sun_sign(nxt)
        if new!=old:
            at=_refine_sun_ingress(cur,nxt,old);sid=tropical_sun_sign(at)
            rows.append({"sign_id":sid,"datetime":at})
            old=sid
        cur=nxt
    return rows

def season_rows(year,lat,lon,tz):
    events=tropical_ingresses(year,tz);rows=[]
    for name,span,english,sid in RITUS:
        start=next((x["datetime"] for x in events if x["sign_id"]==sid and x["datetime"].year==year),None)
        if not start:continue
        next_sid=(sid+2)%12
        end=next((x["datetime"] for x in events if x["sign_id"]==next_sid and x["datetime"]>start),None)
        if not end:continue
        rows.append({"title":name,"date":start.date().isoformat(),"time":f"{panchang.fmt(start,True)} → {panchang.fmt(end,True)}",
          "meta":f"{span} · Tropical Zodiac · {english}",
          "detail":f"Begins {start.isoformat()} · ends {end.isoformat()} · boundary is tropical solar longitude {sid*30}°.",
          "link_date":start.date().isoformat(),"start":start.isoformat(),"end":end.isoformat()})
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
    if slug=="planets/parallel":title="Planets Mutual Parallel";items=parallel_events(year,moment.month,tz)
    elif slug=="planets/ecliptic-crossings":title="Planets Ecliptic Crossings";items=crossing_rows(year,tz)
    elif slug=="astronomy/indian-seasons":title="Indian Seasons";items=season_rows(year,lat,lon,tz)
    elif slug=="planets/sidereal-zodiac":title="Sidereal Zodiac";items=zodiac_rows(moment,True)
    elif slug=="planets/tropical-zodiac":title="Tropical Zodiac";items=zodiac_rows(moment,False)
    else:raise ValueError("Unsupported astronomy reference slug")
    print(json.dumps({"ok":True,"family":"astronomy-reference","slug":slug,"title":title,"year":year,
      "summary":f"{len(items)} astronomy/reference row(s) · {tzname}",
      "metrics":[{"label":"Rows","value":str(len(items)),"note":str(year)},{"label":"Coordinates","value":"Geocentric","note":"true ecliptic/equator of date"},{"label":"Ayanamsha","value":"Lahiri","note":"sidereal-only routes"}],
      "sections":[{"title":title,"note":"Astronomical event searches use the vendored Astronomy Engine foundation; tropical and sidereal frames are kept explicit.","items":items}],
      "engine":{"name":"tithika-astronomy-reference","version":ENGINE_VERSION,"ayanamsha":"Lahiri / Chitrapaksha (sidereal routes only)"}},ensure_ascii=False))
if __name__=="__main__":
    try:main()
    except Exception as exc:
        print(json.dumps({"ok":False,"error":str(exc),"code":"ASTRONOMY_REFERENCE_FAILED"}));sys.exit(1)
