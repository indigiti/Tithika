#!/usr/bin/env python3
"""Completion engine for the remaining Vrat and fasting surfaces."""
from __future__ import annotations
import json, sys
from datetime import date, datetime, timedelta, time
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
import panchang, lunar_occurrences, festival_rules, sankranti
import panchang_completion

ENGINE_VERSION="1.1.0"

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
        choices=[]
        for d in {start.date()-timedelta(days=1),start.date(),end.date()}:
            if d.year!=year: continue
            ss=sunset(d,lat,lon,tz); nr=sunrise(d+timedelta(days=1),lat,lon,tz)
            sr=sunrise(d,lat,lon,tz)
            if not ss or not nr or not sr: continue
            if nr<=ss: nr+=timedelta(days=1)
            ov0=max(start,ss); ov1=min(end,nr)
            overlap=max(0.0,(ov1-ov0).total_seconds())
            ghati=(ss-sr)/30
            strong=start<=ss<end and end>=ss+ghati
            if overlap>0: choices.append((strong,overlap,d,ss,ov0,ov1))
        if not choices: continue
        choices.sort(key=lambda x:(x[0],x[1]),reverse=True)
        strong,overlap,selected,ss,ov0,ov1=choices[0]
        basis=("Ashtami prevails from sunset for at least one local day-Ghati"
               if strong else "maximum Krishna Ashtami overlap with the local night")
        rows.append({"title":"Kalashtami","date":selected.isoformat(),
          "time":f'{fmt(start)} → {fmt(end)}',"meta":"Krishna Ashtami · night selector",
          "detail":basis+f" · night overlap {overlap/60:.1f} minutes",
          "link_date":selected.isoformat(),"night_overlap_start":ov0.isoformat(),"night_overlap_end":ov1.isoformat()})
    return rows

def chandra_darshan(year,lat,lon,tz):
    rows=[]
    rule=lunar_occurrences.KINDS["amavasya"][0]
    for event in lunar_occurrences.events_for_rule(year,rule,lat,lon,tz,False):
        conjunction=datetime.fromisoformat(event["end"])
        for offset in range(0,4):
            d=conjunction.date()+timedelta(days=offset)
            if d.year!=year: continue
            ss=sunset(d,lat,lon,tz);ms=moonset(d,lat,lon,tz)
            if not ss or not ms or ss<=conjunction or ms<=ss: continue
            sun_lon,moon_lon,_=panchang.tropical_longitudes(ss)
            elong=(moon_lon-sun_lon)%360.0
            lag=(ms-ss).total_seconds()/60.0
            age=(ss-conjunction).total_seconds()/3600.0
            # Geometric eligibility only: Danjon-scale elongation plus a useful
            # sunset-to-moonset lag. Weather/extinction are intentionally excluded.
            if 7.0<=elong<=30.0 and lag>=20.0:
                rows.append({"title":"Chandra Darshan","date":d.isoformat(),"time":f"{fmt(ss)} – {fmt(ms)}",
                  "meta":"First geometrically eligible post-Amavasya crescent window",
                  "detail":f"Elongation {elong:.2f}° · Moonset lag {lag:.0f} min · lunar age {age:.1f} h. This is an astronomical candidate, not a weather-dependent visibility guarantee.",
                  "link_date":d.isoformat(),"elongation_deg":round(elong,4),"moonset_lag_minutes":round(lag,2),"lunar_age_hours":round(age,2)})
                break
    return rows

def masik_janmashtami(year,lat,lon,tz):
    rows=[]
    for start,end in exact_tithi_intervals(year,22,tz):
        choices=[]
        for d in {start.date()-timedelta(days=1),start.date(),end.date()}:
            if d.year!=year: continue
            period=festival_rules.nishita_period(d,lat,lon,tz)
            if not period: continue
            n0,n1=period;ov0=max(start,n0);ov1=min(end,n1)
            overlap=max(0.0,(ov1-ov0).total_seconds())
            if overlap>0: choices.append((overlap,d,n0,n1,ov0,ov1))
        if not choices: continue
        overlap,d,n0,n1,ov0,ov1=max(choices,key=lambda x:x[0])
        rows.append({"title":"Masik Krishna Janmashtami","date":d.isoformat(),
          "time":f"{fmt(ov0)} – {fmt(ov1)}","meta":"Krishna Ashtami · local Nishita selector",
          "detail":f"Ashtami overlaps local solar Nishita for {overlap/60:.1f} minutes.",
          "link_date":d.isoformat(),"nishita_start":n0.isoformat(),"nishita_end":n1.isoformat()})
    return rows

def ishti_anvadhan(year,lat,lon,tz):
    rows=[]
    for kind in ("purnima","amavasya"):
        rule=lunar_occurrences.KINDS[kind][0]
        for e in lunar_occurrences.events_for_rule(year,rule,lat,lon,tz,False):
            a=datetime.fromisoformat(e["start"]);b=datetime.fromisoformat(e["end"])
            # Widely used Ishti/Anvadhan calendars pair Anvadhan with the
            # Purnima/Amavasya occurrence and Ishti with the local civil date
            # on which that Tithi ends.
            d=b.date();basis="local civil date containing the exact Purnima/Amavasya Tithi end"
            if d.year!=year: continue
            prev=d-timedelta(days=1)
            rows.extend([
              {"title":"Anvadhan","date":prev.isoformat(),"time":"Previous civil day","meta":f"Before {kind.title()} Ishti","detail":"Anvadhan on the civil day preceding the selected Ishti.","link_date":prev.isoformat()},
              {"title":"Ishti","date":d.isoformat(),"time":f"{fmt(a)} → {fmt(b)}","meta":kind.title(),"detail":basis,"link_date":d.isoformat()}
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
    rows=[];seen=set()
    def add(row,key):
        if key in seen:return
        seen.add(key);rows.append(row)
    # 12 Amavasya Shraddha dates: select the sunrise carrying Amavasya where present.
    for e in lunar_occurrences.events_for_rule(year,lunar_occurrences.KINDS["amavasya"][0],lat,lon,tz,False):
        a=datetime.fromisoformat(e["start"]);b=datetime.fromisoformat(e["end"])
        cand=[x for x in e.get("sunrise_candidates",[]) if int(x["date"][:4])==year]
        d=date.fromisoformat(cand[0]["date"]) if cand else (a+(b-a)/2).date()
        if d.year==year:add({"title":"Amavasya Shraddha","date":d.isoformat(),"time":f"{fmt(a)} → {fmt(b)}","meta":"Amavasya class","detail":"Amavasya occurrence; sunrise-selected where available.","link_date":d.isoformat()},("amavasya",d))
    # 12 Sankranti Shraddha occasions.
    for e in sankranti.find_year(year,lat,lon,tz,False):
        d=date.fromisoformat(e["date"])
        add({"title":"Sankranti Shraddha","date":e["date"],"time":e["time_label"],"meta":e["name"],"detail":"Nirayana solar ingress Shraddha class.","link_date":e["date"]},("sankranti",d,e["rashi_id"]))
    # Pitru Paksha is the Ashwina Krishna fortnight in the Purnimanta profile.
    d=date(year,1,1)
    while d.year==year:
        sr=sunrise(d,lat,lon,tz)
        if sr:
            st=panchang.state_at(sr+timedelta(seconds=1));mi=panchang.lunar_month_info(sr,st);m=norm_month(mi.get("purnimanta"))
            if st["paksha"]=="Krishna Paksha" and m=="Ashwina":
                add({"title":f'{st["tithi"]} Shraddha',"date":d.isoformat(),"time":fmt(sr),"meta":"Pitru Paksha · Ashwina Krishna","detail":"Tithi prevailing at local sunrise in the Purnimanta Pitru-Paksha fortnight.","link_date":d.isoformat()},("pitru",d))
        d+=timedelta(days=1)
    # Vaidhriti and Vyatipata sunrise-Yoga Shraddha classes.
    d=date(year,1,1)
    while d.year==year:
        sr=sunrise(d,lat,lon,tz)
        if sr:
            st=panchang.state_at(sr+timedelta(seconds=1))
            if st["yoga"] in ("Vaidhriti","Vyatipata"):
                add({"title":f'{st["yoga"]} Shraddha',"date":d.isoformat(),"time":fmt(sr),"meta":"Nitya Yoga Shraddha class","detail":f'{st["yoga"]} Yoga prevailing at local sunrise.',"link_date":d.isoformat()},("yoga",st["yoga"],d))
        d+=timedelta(days=1)
    # Purvedyu / Ashtaka / Anvashtaka: Krishna Saptami, Ashtami and
    # Navami across the five traditional lunar months.
    trio_months={"Bhadrapada","Margashirsha","Pausha","Magha","Phalguna"}
    trio_names={7:"Purvedyu Shraddha",8:"Ashtaka Shraddha",9:"Anvashtaka Shraddha"}
    d=date(year,1,1)
    while d.year==year:
        sr=sunrise(d,lat,lon,tz)
        if sr:
            st=panchang.state_at(sr+timedelta(seconds=1));mi=panchang.lunar_month_info(sr,st)
            m=norm_month(mi.get("purnimanta"));n=int(st["tithi_number"])
            if st["paksha"]=="Krishna Paksha" and m in trio_months and n in trio_names:
                add({"title":trio_names[n],"date":d.isoformat(),"time":fmt(sr),
                     "meta":f"{m} · {st['tithi']}",
                     "detail":"Shannavati Purvedyu/Ashtaka/Anvashtaka class selected by local-sunrise Tithi.",
                     "link_date":d.isoformat()},("trio",m,n,d))

    # Manvadi, Yugadi and Kalpadi classes reuse the dedicated Panchang selectors.
    for label,rules in [("Manvadi Shraddha",panchang_completion.MANVADI),("Yugadi Shraddha",panchang_completion.YUGADI),("Kalpadi Shraddha",panchang_completion.KALPADI)]:
        for x in panchang_completion.select_lunar_rules(year,lat,lon,tz,rules):
            d=date.fromisoformat(x["date"])
            add({**x,"title":label+" · "+x["title"],"detail":"Traditional Shraddha class · "+x["detail"]},(label,x["title"],d))
    rows.sort(key=lambda r:(r["date"],r["title"]))
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
