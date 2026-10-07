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

def declination(lon_deg,lat_deg=0.0,eps=23.4392911):
    lo=math.radians(lon_deg);la=math.radians(lat_deg);ob=math.radians(eps)
    return math.degrees(math.asin(math.sin(la)*math.cos(ob)+math.cos(la)*math.sin(ob)*math.sin(lo)))

def kranti_active(moment):
    sun_lon,sun_lat,_=planetary.tropical_coordinates("Sun",moment)
    moon_lon,moon_lat,_=planetary.tropical_coordinates("Moon",moment)
    ds,dm=declination(sun_lon,sun_lat),declination(moon_lon,moon_lat)
    pair=(int(sun_lon//30),int(moon_lon//30))
    opposite_axis={(0,4),(4,0),(1,9),(9,1),(2,8),(8,2),(3,7),(7,3),(5,11),(11,5),(6,10),(10,6)}
    diff=abs(abs(ds)-abs(dm))
    # 0.25° is retained only as a proximity screen. Exact Mahapata duration
    # requires the traditional boundary construction and is therefore not
    # certified as a standalone calculator.
    return pair in opposite_axis and diff<=0.25, ds, dm, diff

def kranti_rows(year,tz):
    start=datetime(year,1,1,tzinfo=tz); end=datetime(year+1,1,1,tzinfo=tz)
    step=timedelta(minutes=20); rows=[]; cur=start; active=False; began=None; best=None
    while cur<=end:
        yes,ds,dm,diff=kranti_active(cur)
        if yes and not active:
            began=cur; best=(diff,cur,ds,dm); active=True
        elif yes and active and diff<(best[0] if best else 99):
            best=(diff,cur,ds,dm)
        elif active and not yes:
            stop=cur
            rows.append({
              "title":"Kranti Samya / Mahapata","date":began.date().isoformat(),
              "time":f'{panchang.fmt(began,False)} – {panchang.fmt(stop,False)}',
              "meta":f'min |declination| difference {best[0]:.4f}°',
              "detail":"Tropical Sun/Moon occupy a Kranti-Samya axis pair and true geocentric declinations (including lunar ecliptic latitude) converge within a 0.25° screening band. This is a geometry reference, not a claim of exact traditional Mahapata boundaries.",
              "link_date":began.date().isoformat()
            })
            active=False; began=None; best=None
        cur+=step
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
