#!/usr/bin/env python3
"""Completion engine for the remaining Vrat and fasting surfaces."""
from __future__ import annotations
import json, sys
from datetime import date, datetime, timedelta, time
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
import panchang, lunar_occurrences
import panchang_completion

ENGINE_VERSION="1.0.0"

FIXED_RULES={
 "vrat/vinayaka-chaturthi":("Vinayaka Chaturthi",None,"Shukla Paksha",4),
 "vrat/ashoka-ashtami":("Ashoka Ashtami","Chaitra","Shukla Paksha",8),
 "vrat/asha-dashami":("Asha Dashami","Ashadha","Shukla Paksha",10),
 "vrat/durva-ashtami":("Durva Ashtami","Bhadrapada","Shukla Paksha",8),
 "vrat/jivit-putrika":("Jivit Putrika Vrat","Ashwina","Krishna Paksha",8),
 "vrat/shitala-saptami":("Shitala Saptami","Chaitra","Krishna Paksha",7),
}
TOP10=[
 ("Ekadashi","vrat/ekadashi"),("Pradosham","vrat/pradosham"),
 ("Sankashti Chaturthi","vrat/sankashti-chaturthi"),("Purnima","vrat/purnima"),
 ("Amavasya","vrat/amavasya"),("Masik Shivaratri","vrat/masik-shivaratri"),
 ("Satyanarayana","vrat/satyanarayana"),("Skanda Sashti","vrat/skanda-sashti"),
 ("Durgashtami","vrat/durgashtami"),("Kalashtami","vrat/kalashtami"),
]
WEEKDAY_FASTS=[
 ("Sunday","Surya","Sun / vitality tradition"),("Monday","Chandra · Shiva","Moon / Shiva tradition"),
 ("Tuesday","Mangala · Hanuman · Durga","Mars / Hanuman / Devi tradition"),("Wednesday","Budha · Ganesha","Mercury / Ganesha tradition"),
 ("Thursday","Guru · Vishnu","Jupiter / Vishnu tradition"),("Friday","Shukra · Lakshmi","Venus / Lakshmi tradition"),
 ("Saturday","Shani · Hanuman","Saturn / Shani-Hanuman tradition"),
]
DASHAVATARA=["Matsya","Kurma","Varaha","Narasimha","Vamana","Parashurama","Rama","Krishna","Buddha","Kalki"]

def rise(d,lat,lon,tz,body,dirn):
    return panchang.rise_set(d,lat,lon,tz,body,dirn)

def sunrise(d,lat,lon,tz): return rise(d,lat,lon,tz,panchang.astronomy.Body.Sun,panchang.astronomy.Direction.Rise)
def sunset(d,lat,lon,tz): return rise(d,lat,lon,tz,panchang.astronomy.Body.Sun,panchang.astronomy.Direction.Set)
def moonset(d,lat,lon,tz): return rise(d,lat,lon,tz,panchang.astronomy.Body.Moon,panchang.astronomy.Direction.Set)
def norm_month(v): return str(v or "").replace("Adhika ","").strip()
def fmt(dt): return panchang.fmt(dt,False)

def scan_rule(year,lat,lon,tz,title,month,paksha,num):
    rows=[];d=date(year,1,1)
    while d.year==year:
        sr=sunrise(d,lat,lon,tz)
        if sr:
            st=panchang.state_at(sr+timedelta(seconds=1)); months=panchang.lunar_month_info(sr,st)
            if (month is None or norm_month(months.get("purnimanta"))==month) and st["paksha"]==paksha and int(st["tithi_number"])==num:
                rows.append({"title":title,"date":d.isoformat(),"time":fmt(sr),
                  "meta":f'{months.get("purnimanta") or ""} · {st["paksha"]} · {st["tithi"]}',
                  "detail":"Month/Paksha/Tithi prevailing at local sunrise","link_date":d.isoformat()})
        d+=timedelta(days=1)
    return rows

def exact_tithi_intervals(year,target_id,tz):
    start=datetime(year-1,12,28,tzinfo=tz); end=datetime(year+1,1,4,tzinfo=tz); rows=[];cur=start
    while cur<end:
        st=panchang.state_at(cur); current=st["tithi_id"]
        tr=panchang.find_transition(cur,end,"tithi_id",current,step_minutes=180); stop=tr or end
        if current==target_id: rows.append((cur,stop))
        if tr is None: break
        cur=tr+timedelta(seconds=1)
    return rows

def kalashtami(year,lat,lon,tz):
    rows=[]
    for start,end in exact_tithi_intervals(year,22,tz): # Krishna Ashtami
        candidates={start.date(),end.date()}
        selected=None; evidence=""
        for d in sorted(candidates):
            if d.year!=year: continue
            ss=sunset(d,lat,lon,tz); sr=sunrise(d,lat,lon,tz)
            if not ss or not sr: continue
            ghati=(ss-sr)/30
            if start <= ss < end and end >= ss+ghati:
                selected=d; evidence="Ashtami prevails at least one local Ghati after sunset";break
        if selected is None:
            d=start.date()
            ss=sunset(d,lat,lon,tz)
            selected=d if ss and start<=ss<end else (end.date()-timedelta(days=1))
            evidence="Fallback to civil evening with maximum Ashtami night overlap"
        if selected.year==year:
            rows.append({"title":"Kalashtami","date":selected.isoformat(),
             "time":f'{fmt(start)} → {fmt(end)}',"meta":"Krishna Ashtami · night selector",
             "detail":evidence,"link_date":selected.isoformat()})
    return rows

def chandra_darshan(year,lat,lon,tz):
    rows=[]
    rule=lunar_occurrences.KINDS["amavasya"][0]
    for event in lunar_occurrences.events_for_rule(year,rule,lat,lon,tz,False):
        newmoon_end=datetime.fromisoformat(event["end"])
        for offset in range(0,3):
            d=newmoon_end.date()+timedelta(days=offset)
            if d.year!=year: continue
            ss=sunset(d,lat,lon,tz); ms=moonset(d,lat,lon,tz)
            if ss and ms and ms>ss and ms-ss<=timedelta(hours=4) and newmoon_end<ms:
                start=max(ss,newmoon_end)
                rows.append({"title":"Chandra Darshan","date":d.isoformat(),"time":f"{fmt(start)} – {fmt(ms)}",
                  "meta":"First post-Amavasya sunset visibility window",
                  "detail":"Moonset occurs after local sunset; window begins after both sunset and Amavasya end.","link_date":d.isoformat()})
                break
    return rows

def masik_janmashtami(year,lat,lon,tz):
    rows=[]
    for start,end in exact_tithi_intervals(year,22,tz):
        best=None
        for d in {start.date(),end.date(),start.date()+timedelta(days=1)}:
            if d.year!=year: continue
            nishita=datetime.combine(d,time(23,59,59),tzinfo=tz)+timedelta(seconds=1)
            if start<=nishita<end: best=(d,nishita,"Krishna Ashtami prevailing at local Nishita/midnight");break
        if best is None:
            midpoint=start+(end-start)/2; best=(midpoint.date(),midpoint,"Krishna Ashtami midpoint fallback when no civil midnight lies inside Tithi")
        d,anchor,basis=best
        if d.year==year:
            rows.append({"title":"Masik Krishna Janmashtami","date":d.isoformat(),"time":fmt(anchor),
             "meta":"Krishna Ashtami · Nishita selector","detail":basis,"link_date":d.isoformat()})
    return rows

def ishti_anvadhan(year,lat,lon,tz):
    rows=[]
    for kind in ("purnima","amavasya"):
        rule=lunar_occurrences.KINDS[kind][0]
        for e in lunar_occurrences.events_for_rule(year,rule,lat,lon,tz,False):
            a=datetime.fromisoformat(e["start"]); b=datetime.fromisoformat(e["end"]); mid=a+(b-a)/2; d=mid.date()
            if d.year!=year: continue
            prev=d-timedelta(days=1)
            rows.extend([
              {"title":"Anvadhan","date":prev.isoformat(),"time":"Previous civil day","meta":f"Before {kind.title()} Ishti","detail":"Anvadhan paired with the following Ishti occurrence.","link_date":prev.isoformat()},
              {"title":"Ishti","date":d.isoformat(),"time":f"{fmt(a)} → {fmt(b)}","meta":kind.title(),"detail":"Exact Purnima/Amavasya Tithi occurrence.","link_date":d.isoformat()}
            ])
    rows.sort(key=lambda r:(r["date"],r["title"]))
    return rows

def iskcon_ekadashi(year,lat,lon,tz):
    rows=[]
    for rule in lunar_occurrences.KINDS["ekadashi"]:
        for e in lunar_occurrences.events_for_rule(year,rule,lat,lon,tz,False):
            ob=e.get("observance") or {}; isk=ob.get("iskcon") or {}
            d=isk.get("date")
            if not d or int(d[:4])!=year: continue
            par=isk.get("parana") or {}
            rows.append({"title":"ISKCON Ekadashi","date":d,"time":isk.get("weekday",""),
              "meta":f'{e.get("purnimanta_month") or ""} · {e["paksha"]}',
              "detail":f'{isk.get("basis","integrated-vaishnava")} · Parana {par.get("start_label") or par.get("earliest_label") or "—"} – {par.get("end_label") or par.get("deadline_label") or "—"}',
              "link_date":d})
    rows.sort(key=lambda r:r["date"])
    return rows

def adhika_intervals(year,lat,lon,tz):
    rows=[];active=None;last=None;name="";d=date(year,1,1)
    while d.year==year:
        sr=sunrise(d,lat,lon,tz)
        adh=False; m=""
        if sr:
            st=panchang.state_at(sr+timedelta(seconds=1));mi=panchang.lunar_month_info(sr,st)
            adh=bool(mi.get("adhika"));m=str(mi.get("amanta") or "")
        if adh and active is None: active=d;name=m
        if active is not None and not adh:
            rows.append((active,d-timedelta(days=1),name));active=None
        last=d;d+=timedelta(days=1)
    if active: rows.append((active,last,name))
    return rows

def purushottam(year,lat,lon,tz):
    return [{"title":"Purushottam / Adhika Maas","date":a.isoformat(),"time":f"{a.isoformat()} → {b.isoformat()}",
      "meta":name,"detail":"Contiguous local-sunrise days whose lunar month is flagged Adhika.","link_date":a.isoformat()} for a,b,name in adhika_intervals(year,lat,lon,tz)]

def ekadashi_month_day(year,lat,lon,tz,month):
    for rule in lunar_occurrences.KINDS["ekadashi"]:
        if rule["paksha"]!="Shukla Paksha": continue
        for e in lunar_occurrences.events_for_rule(year,rule,lat,lon,tz,False):
            if norm_month(e.get("purnimanta_month"))!=month: continue
            ob=e.get("observance") or {}; row=ob.get("smarta") or {}
            if row.get("date") and int(row["date"][:4])==year: return date.fromisoformat(row["date"])
    return None

def chaturmasa(year,lat,lon,tz):
    a=ekadashi_month_day(year,lat,lon,tz,"Ashadha"); b=ekadashi_month_day(year,lat,lon,tz,"Kartika")
    if not a or not b: return []
    return [{"title":"Chaturmasa","date":a.isoformat(),"time":f"{a.isoformat()} → {b.isoformat()}",
      "meta":"Ashadha Shukla Ekadashi → Kartika Shukla Ekadashi",
      "detail":"Versioned Smarta four-month observance span; sect-specific endpoints can be layered separately.","link_date":a.isoformat()}]

def shraddha(year,lat,lon,tz):
    rows=[]
    # Amavasya
    for e in lunar_occurrences.events_for_rule(year,lunar_occurrences.KINDS["amavasya"][0],lat,lon,tz,False):
        mid=datetime.fromisoformat(e["start"])+(datetime.fromisoformat(e["end"])-datetime.fromisoformat(e["start"]))/2
        if mid.year==year: rows.append({"title":"Amavasya Shraddha","date":mid.date().isoformat(),"time":fmt(mid),"meta":"12-Amavasya class","detail":"Amavasya occurrence","link_date":mid.date().isoformat()})
    # Pitru Paksha: Krishna Paksha in Bhadrapada/Ashwina sunrise profile
    d=date(year,1,1)
    while d.year==year:
        sr=sunrise(d,lat,lon,tz)
        if sr:
            st=panchang.state_at(sr+timedelta(seconds=1));mi=panchang.lunar_month_info(sr,st);m=norm_month(mi.get("purnimanta"))
            if st["paksha"]=="Krishna Paksha" and m in ("Bhadrapada","Ashwina"):
                rows.append({"title":"Pitru Paksha Shraddha","date":d.isoformat(),"time":fmt(sr),"meta":f'{m} · {st["tithi"]}',"detail":"Krishna Paksha sunrise Tithi in the Pitru-Paksha season profile.","link_date":d.isoformat()})
        d+=timedelta(days=1)
    # Manvadi / Yugadi Shraddha classes reuse the dedicated selectors.
    for label,rules in [("Manvadi Shraddha",panchang_completion.MANVADI),("Yugadi Shraddha",panchang_completion.YUGADI)]:
        for x in panchang_completion.select_lunar_rules(year,lat,lon,tz,rules):
            rows.append({**x,"title":label+" · "+x["title"],"detail":"Traditional Shraddha class · "+x["detail"]})
    rows.sort(key=lambda r:r["date"])
    return rows

def collections(slug):
    if slug=="vrat/top-10": vals=TOP10
    elif slug=="vrat/navagraha-weekdays" or slug=="vrat/deity-weekdays": vals=[(a,b) for a,b,_ in WEEKDAY_FASTS]
    elif slug=="vrat/dashavatara": vals=[(x,"festivals/dashavatara") for x in DASHAVATARA]
    else: vals=[]
    return [{"title":a,"meta":b,"detail":"Structured Tithika observance reference"} for a,b in vals]

def katha(slug):
    title={"vrat/katha":"Vrat Katha Library","vrat/katha/satyanarayana":"Satyanarayana Vrat Katha",
      "vrat/katha/ekadashi":"Ekadashi Vrat Katha","vrat/katha/karwa-chauth":"Karwa Chauth Vrat Katha",
      "vrat/katha/ahoi-ashtami":"Ahoi Ashtami Vrat Katha"}[slug]
    items=[
      {"title":"Purpose","meta":"Devotional reading","detail":"A concise observance guide and traditional story context; Tithika does not fabricate scripture text."},
      {"title":"Timing","meta":"Use the linked calculated Vrat date","detail":"Read or recite according to family, temple or Sampradaya practice."},
      {"title":"Practice note","meta":"Tradition varies","detail":"Local priest, temple or Sampradaya guidance prevails where ritual details differ."}
    ]
    return title,items

def main():
    p=json.loads(sys.stdin.read() or "{}");slug=str(p.get("slug") or "").strip("/")
    lat=float(p.get("lat",18.5204));lon=float(p.get("lon",73.8567));tzname=p.get("timezone") or "Asia/Kolkata"
    try: tz=ZoneInfo(tzname)
    except ZoneInfoNotFoundError: tz=ZoneInfo("Asia/Kolkata");tzname="Asia/Kolkata"
    selected=datetime.strptime(p.get("date") or datetime.now(tz).strftime("%Y-%m-%d"),"%Y-%m-%d").date();year=selected.year
    if slug in FIXED_RULES:
        title,month,paksha,num=FIXED_RULES[slug];items=scan_rule(year,lat,lon,tz,title,month,paksha,num)
    elif slug=="vrat/kalashtami": title="Kalashtami";items=kalashtami(year,lat,lon,tz)
    elif slug=="vrat/chandra-darshan": title="Chandra Darshan";items=chandra_darshan(year,lat,lon,tz)
    elif slug=="vrat/masik-janmashtami": title="Masik Krishna Janmashtami";items=masik_janmashtami(year,lat,lon,tz)
    elif slug=="vrat/ishti-anvadhan": title="Ishti & Anvadhan";items=ishti_anvadhan(year,lat,lon,tz)
    elif slug=="vrat/iskcon-ekadashi": title="ISKCON Ekadashi";items=iskcon_ekadashi(year,lat,lon,tz)
    elif slug=="vrat/purushottam-maas": title="Purushottam Maas";items=purushottam(year,lat,lon,tz)
    elif slug=="vrat/chaturmasa": title="Chaturmasa";items=chaturmasa(year,lat,lon,tz)
    elif slug=="vrat/shraddha": title="Shraddha Dates";items=shraddha(year,lat,lon,tz)
    elif slug in ("vrat/top-10","vrat/navagraha-weekdays","vrat/deity-weekdays","vrat/dashavatara"):
        title=slug.split("/")[-1].replace("-"," ").title();items=collections(slug)
    elif slug.startswith("vrat/katha"):
        title,items=katha(slug)
    else: raise ValueError("Unsupported Vrat completion slug")
    sections=[{"title":title,"note":"Explicit Tithika observance profile; regional/Sampradaya differences remain visible in rule text.","items":items}]
    print(json.dumps({"ok":True,"family":"vrat","slug":slug,"title":title,"year":year,
      "summary":f"{len(items)} structured result(s) · {tzname}",
      "metrics":[{"label":"Results","value":str(len(items)),"note":str(year)},{"label":"Panchang","value":"Lahiri","note":"shared core"},{"label":"Selector","value":"Explicit","note":"no hidden geography guess"}],
      "sections":sections,"engine":{"name":"tithika-vrat-completion","version":ENGINE_VERSION,"ayanamsha":"Lahiri / Chitrapaksha"}},ensure_ascii=False))
if __name__=="__main__":
    try: main()
    except Exception as exc:
        print(json.dumps({"ok":False,"error":str(exc),"code":"VRAT_COMPLETION_FAILED"}));sys.exit(1)
