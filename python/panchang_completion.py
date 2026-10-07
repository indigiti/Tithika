#!/usr/bin/env python3
"""Completion engine for the remaining Panchang rule/reference surfaces."""
from __future__ import annotations
import json, math, sys
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
import panchang, planetary

ENGINE_VERSION="1.0.0"

MANVADI=[
("Brahma Savarni Manvadi","Magha","Shukla Paksha",7),
("Savarni Manvadi","Phalguna","Shukla Paksha",15),
("Swayambhuva Manvadi","Chaitra","Shukla Paksha",3),
("Swarochisha Manvadi","Chaitra","Shukla Paksha",15),
("Vaivaswata Manvadi","Jyeshtha","Shukla Paksha",15),
("Raivata Manvadi","Ashadha","Shukla Paksha",10),
("Chakshusha Manvadi","Ashadha","Shukla Paksha",15),
("Indra Savarni Manvadi","Bhadrapada","Krishna Paksha",8),
("Daiva Savarni Manvadi","Bhadrapada","Krishna Paksha",15),
("Rudra Savarni Manvadi","Bhadrapada","Shukla Paksha",3),
("Daksha Savarni Manvadi","Ashwina","Shukla Paksha",9),
("Tamasa Manvadi","Kartika","Shukla Paksha",12),
("Uttama Manvadi","Kartika","Shukla Paksha",15),
("Dharma Savarni Manvadi","Pausha","Shukla Paksha",11),
]
YUGADI=[
("Dwapara Yuga Diwas","Phalguna","Krishna Paksha",15),
("Treta Yuga Diwas","Vaishakha","Shukla Paksha",3),
("Kali Yuga Diwas","Ashwina","Krishna Paksha",13),
("Satya Yuga Diwas","Kartika","Shukla Paksha",9),
]
KALPADI=[
("Varaha Kalpadi","Magha","Shukla Paksha",13),
("Brahma Kalpadi","Chaitra","Krishna Paksha",3),
("Kurma Kalpadi First","Chaitra","Shukla Paksha",1),
("Kurma Kalpadi Second","Chaitra","Shukla Paksha",5),
("Parthiva Kalpadi","Vaishakha","Shukla Paksha",3),
("Savitri Kalpadi","Kartika","Shukla Paksha",7),
("Pralaya Kalpadi","Margashirsha","Shukla Paksha",9),
]

def sunrise(d,lat,lon,tz):
    return panchang.rise_set(d,lat,lon,tz,panchang.astronomy.Body.Sun,panchang.astronomy.Direction.Rise)

def sunset(d,lat,lon,tz):
    return panchang.rise_set(d,lat,lon,tz,panchang.astronomy.Body.Sun,panchang.astronomy.Direction.Set)

def norm_month(v): return str(v or "").replace("Adhika ","").strip()

def tithi_num(state):
    return 15 if int(state["tithi_number"])==15 else int(state["tithi_number"])

def day_row(d, sr, state, months, title, rule):
    return {
      "title":title,"date":d.isoformat(),"weekday":d.strftime("%A"),
      "time":panchang.fmt(sr,False),"meta":f'{months.get("purnimanta") or ""} · {state["paksha"]} · {state["tithi"]}',
      "detail":rule,"link_date":d.isoformat()
    }

def select_lunar_rules(year,lat,lon,tz,rules):
    rows=[]; seen=set(); d=date(year,1,1)
    while d.year==year:
        sr=sunrise(d,lat,lon,tz)
        if sr:
            state=panchang.state_at(sr+timedelta(seconds=1))
            months=panchang.lunar_month_info(sr,state)
            month=norm_month(months.get("purnimanta"))
            for title,wmonth,wpaksha,wnum in rules:
                key=(title,d.isoformat())
                if key in seen: continue
                if month==wmonth and state["paksha"]==wpaksha and tithi_num(state)==wnum:
                    rows.append(day_row(d,sr,state,months,title,"Purnimanta month + Paksha + Tithi prevailing at local sunrise"))
                    seen.add(key)
        d+=timedelta(days=1)
    return rows

def declination_from_ecliptic(lon_deg, lat_deg, eps=23.4392911):
    lo=math.radians(lon_deg); la=math.radians(lat_deg); ob=math.radians(eps)
    return math.degrees(math.asin(
        math.sin(la)*math.cos(ob)+math.cos(la)*math.sin(ob)*math.sin(lo)
    ))

def kranti_state(moment):
    slon,slat,_=planetary.tropical_coordinates("Sun",moment)
    mlon,mlat,_=planetary.tropical_coordinates("Moon",moment)
    ds=declination_from_ecliptic(slon,slat)
    dm=declination_from_ecliptic(mlon,mlat)
    pair=(int(slon//30),int(mlon//30))
    opposite_axis={(0,4),(4,0),(1,9),(9,1),(2,8),(8,2),(3,7),(7,3),(5,11),(11,5),(6,10),(10,6)}
    return pair in opposite_axis, ds, dm, abs(ds)-abs(dm), slon, mlon

def refine_zero(lo,hi):
    a=kranti_state(lo); b=kranti_state(hi)
    fa=a[3]; fb=b[3]
    for _ in range(42):
        mid=lo+(hi-lo)/2
        fm=kranti_state(mid)[3]
        if fa==0: return lo
        if fb==0: return hi
        if fa*fm<=0:
            hi=mid; fb=fm
        else:
            lo=mid; fa=fm
    return lo+(hi-lo)/2

def refine_boundary(lo,hi,target=0.5):
    flo=abs(kranti_state(lo)[3])-target
    for _ in range(42):
        mid=lo+(hi-lo)/2
        fm=abs(kranti_state(mid)[3])-target
        if flo*fm<=0:
            hi=mid
        else:
            lo=mid;flo=fm
    return lo+(hi-lo)/2

def kranti_rows(year,tz):
    # Classical Mahapata window: the broad Kranti-Samya axis must apply and
    # the lunar declination passes from 30' before to 30' beyond the solar
    # declination (|difference in declination magnitude| <= 0.5 degree).
    start=datetime(year,1,1,tzinfo=tz);end=datetime(year+1,1,1,tzinfo=tz)
    step=timedelta(minutes=10);rows=[];cur=start
    prev=kranti_state(cur); prev_active=prev[0] and abs(prev[3])<=0.5
    began=start if prev_active else None; best=None
    while cur<end:
        nxt=min(end,cur+step); now=kranti_state(nxt)
        active=now[0] and abs(now[3])<=0.5
        if active and not prev_active:
            began=refine_boundary(cur,nxt)
            best=(abs(kranti_state(began)[3]),began)
        elif active:
            score=abs(now[3])
            if best is None or score<best[0]: best=(score,nxt)
        elif prev_active and began is not None:
            stop=refine_boundary(cur,nxt)
            mid=(began+stop)/2; _,ds,dm,_,_,_=kranti_state(mid)
            kind="Vyatipata" if ds*dm>=0 else "Vaidhriti"
            rows.append({
              "title":f"{kind} Kranti Samya / Mahapata","date":began.date().isoformat(),
              "time":f"{panchang.fmt(began,False)} – {panchang.fmt(stop,False)}",
              "meta":f"midpoint declinations Sun {ds:+.4f}° · Moon {dm:+.4f}°",
              "detail":f"Mahapata interval: |declination magnitude difference| ≤ 0.5° · {began.isoformat()} → {stop.isoformat()}",
              "link_date":began.date().isoformat()
            })
            began=None;best=None
        cur=nxt;prev=now;prev_active=active
    return rows

def published_snapshot(selected,lat,lon,tz):
    sr=sunrise(selected,lat,lon,tz); ss=sunset(selected,lat,lon,tz)
    if not sr or not ss: raise ValueError("Solar events unavailable")
    st=panchang.state_at(sr+timedelta(seconds=1)); months=panchang.lunar_month_info(sr,st)
    return [{
      "title":"Publication-ready Panchang snapshot","date":selected.isoformat(),"time":panchang.fmt(sr,False),
      "meta":f'{st["tithi"]} · {st["nakshatra"]} · {st["yoga"]}',
      "detail":f'Sunrise {panchang.fmt(sr,False)} · Sunset {panchang.fmt(ss,False)} · {months.get("purnimanta") or ""} · {st["paksha"]}',
      "link_date":selected.isoformat()
    }]

def utilities():
    names=[
      ("Daily Panchang","panchang/daily"),("Month Panchang","panchang/month"),
      ("Nakshatra transitions","panchang/nakshatra"),("Tarabalam","panchang/tarabalam"),
      ("Chandrabalam","panchang/chandrabalam"),("Panchak","panchang/panchak"),
      ("Bhadra","panchang/bhadra"),("Sankalpa","panchang/sankalpa"),
      ("Vedic Clock","panchang/vedic-clock"),("Manvadi","panchang/manvadi-tithi"),
      ("Yugadi","panchang/yugadi-tithi"),("Kalpadi","panchang/kalpadi-tithi"),
      ("Kranti Samya","panchang/kranti-samya")
    ]
    return [{"title":a,"meta":b,"detail":"Verified Tithika Panchang utility"} for a,b in names]

def main():
    p=json.loads(sys.stdin.read() or "{}")
    slug=str(p.get("slug") or "").strip("/")
    lat=float(p.get("lat",18.5204)); lon=float(p.get("lon",73.8567))
    tzname=p.get("timezone") or "Asia/Kolkata"
    try: tz=ZoneInfo(tzname)
    except ZoneInfoNotFoundError: tz=ZoneInfo("Asia/Kolkata"); tzname="Asia/Kolkata"
    selected=datetime.strptime(p.get("date") or datetime.now(tz).strftime("%Y-%m-%d"),"%Y-%m-%d").date()
    year=selected.year
    if slug=="panchang/manvadi-tithi": title="Manvadi Tithi"; rows=select_lunar_rules(year,lat,lon,tz,MANVADI)
    elif slug=="panchang/yugadi-tithi": title="Yugadi Tithi"; rows=select_lunar_rules(year,lat,lon,tz,YUGADI)
    elif slug=="panchang/kalpadi-tithi": title="Kalpadi Tithi"; rows=select_lunar_rules(year,lat,lon,tz,KALPADI)
    elif slug=="panchang/kranti-samya": title="Kranti Samya Dosha"; rows=kranti_rows(year,tz)
    elif slug=="panchang/published": title="Published Panchang"; rows=published_snapshot(selected,lat,lon,tz)
    elif slug=="panchang/utilities": title="Panchang Utilities"; rows=utilities()
    else: raise ValueError("Unsupported Panchang completion slug")
    print(json.dumps({
      "ok":True,"family":"panchang","slug":slug,"title":title,"year":year,
      "summary":f'{len(rows)} structured result(s) · {tzname}',
      "metrics":[{"label":"Results","value":str(len(rows)),"note":str(year)},
                 {"label":"Ayanamsha","value":"Lahiri","note":"shared Panchang core"},
                 {"label":"Profile","value":"Explicit","note":"route-specific rule"}],
      "sections":[{"title":title,"note":"Deterministic Tithika rule profile","items":rows}],
      "engine":{"name":"tithika-panchang-completion","version":ENGINE_VERSION,"ayanamsha":"Lahiri / Chitrapaksha"}
    },ensure_ascii=False))
if __name__=="__main__":
    try: main()
    except Exception as exc:
        print(json.dumps({"ok":False,"error":str(exc),"code":"PANCHANG_COMPLETION_FAILED"})); sys.exit(1)
