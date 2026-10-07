#!/usr/bin/env python3
"""Aggregation engine for remaining calendar and festival collection surfaces."""
from __future__ import annotations
import json, sys
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
import panchang, festival_rules, lunar_occurrences, regional_calendar, sankranti

ENGINE_VERSION="1.0.0"
MONTH_SLUGS={
 "festivals/chaitra":"Chaitra","festivals/vaishakha":"Vaishakha","festivals/jyeshtha":"Jyeshtha",
 "festivals/ashadha":"Ashadha","festivals/shravana":"Shravana","festivals/bhadrapada":"Bhadrapada",
 "festivals/ashwina":"Ashwina","festivals/kartika":"Kartika","festivals/margashirsha":"Margashirsha",
 "festivals/pausha":"Pausha","festivals/magha":"Magha","festivals/phalguna":"Phalguna",
}
COLLECTIONS={
 "festivals/dashavatara":["Matsya","Kurma","Varaha","Narasimha","Vamana","Parashurama","Rama","Krishna","Buddha","Kalki"],
 "festivals/navdurga":["Shailaputri","Brahmacharini","Chandraghanta","Kushmanda","Skandamata","Katyayani","Kalaratri","Mahagauri","Siddhidatri"],
 "festivals/deities":["Ganesha","Shiva","Vishnu","Rama","Krishna","Hanuman","Durga","Lakshmi","Saraswati","Kartikeya"],
 "festivals/regional-deities":["Vitthal","Khandoba","Ayyappa","Jagannath","Venkateswara","Murugan","Guruvayurappan"],
 "festivals/pilgrim-places":["Kashi","Prayagraj","Haridwar","Rameswaram","Dwarka","Puri","Tirupati","Ujjain","Nashik"],
 "festivals/vishnu-avatars":["Sanaka","Varaha","Narada","Nara-Narayana","Kapila","Dattatreya","Yajna","Rishabha","Prithu","Matsya","Kurma","Dhanvantari","Mohini","Narasimha","Vamana","Parashurama","Vyasa","Rama","Balarama","Krishna","Buddha","Kalki"],
 "festivals/puja-vidhi":["Ganesha Puja","Lakshmi Puja","Shiva Puja","Holi Puja"],
 "festivals/gurus-saints":["Adi Shankaracharya","Ramanujacharya","Madhvacharya","Kabir","Guru Nanak","Tukaram","Dnyaneshwar"],
}
PUJA={
 "festivals/puja/ganesha":("Ganesha Puja",["Sankalpa","Avahana","Asana and Padya","Gandha-Pushpa","Naivedya","Aarti"]),
 "festivals/puja/lakshmi":("Lakshmi Puja",["Sankalpa","Kalasha","Lakshmi Avahana","Shodashopachara","Naivedya","Aarti"]),
 "festivals/puja/shivaratri":("Shivaratri Puja",["Sankalpa","Abhisheka","Bilva Archana","Mantra Japa","Naivedya","Aarti"]),
 "festivals/puja/holi":("Holi Puja",["Sankalpa","Holika setup","Puja offerings","Pradakshina","Holika Dahan"]),
}
CALENDAR_THEMES={
 "calendars/diwali":["Dhanteras","Naraka Chaturdashi","Lakshmi Puja / Diwali","Govardhan Puja","Bhai Dooj"],
 "calendars/durga-puja":["Mahalaya","Shashthi","Saptami","Mahashtami","Maha Navami","Vijayadashami"],
 "calendars/onam":["Atham","Chithira","Chodhi","Vishakam","Anizham","Thriketa","Moolam","Pooradam","Uthradam","Thiruvonam"],
 "calendars/mysore-dasara":["Navratri begins","Ayudha Puja","Mahanavami","Vijayadashami"],
 "calendars/saraswati-puja":["Vasant Panchami","Navratri Saraswati Avahana","Saraswati Puja"],
 "calendars/chhath":["Nahay Khay","Kharna","Sandhya Arghya","Usha Arghya"],
 "calendars/navratri":["Chaitra Navratri","Shardiya Navratri"],
 "calendars/shardiya-navratri":["Ghatasthapana","Navdurga days","Durga Ashtami","Maha Navami","Vijayadashami"],
 "calendars/chaitra-navratri":["Ghatasthapana","Navdurga days","Rama Navami"],
 "calendars/dashavatara":["Matsya","Kurma","Varaha","Narasimha","Vamana","Parashurama","Rama","Krishna","Buddha","Kalki"],
 "calendars/dasha-mahavidya":["Kali","Tara","Tripura Sundari","Bhuvaneshwari","Bhairavi","Chhinnamasta","Dhumavati","Bagalamukhi","Matangi","Kamala"],
 "calendars/dwadasha-siddhividya":["Twelve Siddhavidya observance reference"],
 "calendars/gujarati-diwali":["Dhanteras","Kali Chaudas","Diwali","Bestu Varas","Bhai Bij"],
 "calendars/dashain":["Ghatasthapana","Fulpati","Maha Ashtami","Maha Navami","Vijaya Dashami","Kojagrat Purnima"],
 "calendars/tihar":["Kaag Tihar","Kukur Tihar","Gai Tihar / Lakshmi Puja","Govardhan Puja / Mha Puja","Bhai Tika"],
}

def rise(d,lat,lon,tz):
    return panchang.rise_set(d,lat,lon,tz,panchang.astronomy.Body.Sun,panchang.astronomy.Direction.Rise)

def major_events(year,lat,lon,tz):
    rows=[]
    for kind in festival_rules.SUPPORTED_KINDS:
        e=festival_rules.calculate_event(kind,year,lat,lon,tz,False)
        if not e: continue
        d=e["date"]
        rows.append({"title":e["title"],"date":d,"time":e.get("weekday",""),
          "meta":f'{e.get("month","")} · {e.get("paksha","")}',
          "detail":f'Selector: {e.get("rule",{}).get("selector","verified festival rule")}',"link_date":d})
    rows.sort(key=lambda x:x["date"])
    return rows

def recurring_events(year,lat,lon,tz):
    rows=[]
    for kind in ("purnima","amavasya","ekadashi"):
        for rule in lunar_occurrences.KINDS[kind]:
            for e in lunar_occurrences.events_for_rule(year,rule,lat,lon,tz,False):
                if kind=="ekadashi":
                    obs=(e.get("observance") or {}).get("smarta") or {}
                    d=obs.get("date")
                    title=rule["name"]
                else:
                    a=datetime.fromisoformat(e["start"]);b=datetime.fromisoformat(e["end"])
                    d=(a+(b-a)/2).date().isoformat();title=rule["name"]
                if not d or int(d[:4])!=year: continue
                rows.append({"title":title,"date":d,"time":"","meta":e.get("purnimanta_month") or "",
                  "detail":"Shared lunar-occurrence engine","link_date":d})
    for e in sankranti.find_year(year,lat,lon,tz,False):
        rows.append({"title":e["title"],"date":e["date"],"time":e["time_label"],"meta":"Sankranti",
          "detail":"Shared Nirayana solar-ingress engine","link_date":e["date"]})
    # De-duplicate same-title/date combinations from overlapping collections.
    out=[];seen=set()
    for r in sorted(rows,key=lambda x:(x["date"],x["title"])):
        key=(r["date"],r["title"])
        if key in seen: continue
        seen.add(key);out.append(r)
    return out

def yearly_events(year,lat,lon,tz):
    rows=major_events(year,lat,lon,tz)+recurring_events(year,lat,lon,tz)
    out=[];seen=set()
    for r in sorted(rows,key=lambda x:(x["date"],x["title"])):
        key=(r["date"],r["title"])
        if key in seen: continue
        seen.add(key);out.append(r)
    return out

def purnima_rows(year,lat,lon,tz):
    rows=[]
    for e in lunar_occurrences.events_for_rule(year,lunar_occurrences.KINDS["purnima"][0],lat,lon,tz,False):
        a=datetime.fromisoformat(e["start"]);b=datetime.fromisoformat(e["end"]);d=(a+(b-a)/2).date()
        if d.year==year: rows.append({"title":"Purnima","date":d.isoformat(),"time":f'{panchang.fmt(a,False)} → {panchang.fmt(b,False)}',"meta":e.get("purnimanta_month") or "","detail":"Exact Purnima Tithi window","link_date":d.isoformat()})
    return rows

def month_rows(year,lat,lon,tz,month):
    rows=[]
    for r in yearly_events(year,lat,lon,tz):
        d=date.fromisoformat(r["date"]);sr=rise(d,lat,lon,tz)
        if not sr: continue
        st=panchang.state_at(sr+timedelta(seconds=1));mi=panchang.lunar_month_info(sr,st)
        if str(mi.get("purnimanta") or "").replace("Adhika ","")==month: rows.append(r)
    return rows

def regional_year(year,lat,lon,tz,variant):
    # Reuse one ingress index for the whole year instead of recalculating it
    # separately for all 12 Gregorian display months.
    events=regional_calendar.ingress_index(year,lat,lon,tz,False)
    events=sorted(events,key=lambda x:x["datetime"])
    names=regional_calendar.SOLAR_MONTHS[variant]
    rows=[]
    for i,e in enumerate(events):
        start=datetime.fromisoformat(e["datetime"])
        if start.year not in (year-1,year): continue
        nxt=datetime.fromisoformat(events[i+1]["datetime"]) if i+1<len(events) else None
        if not nxt or nxt.year<year or start.year>year: continue
        a=max(start.date(),date(year,1,1)); b=min((nxt-timedelta(seconds=1)).date(),date(year,12,31))
        if a>b: continue
        sid=int(e["rashi_id"])
        rows.append({"title":names[sid],"date":a.isoformat(),"time":f"{a.isoformat()} → {b.isoformat()}",
          "meta":"nirayana-solar","detail":f'Exact Lahiri solar-month span · {variant.title()} profile',"link_date":a.isoformat()})
    # Keep one row per regional solar month in chronological order.
    seen=set(); out=[]
    for r in rows:
        if r["title"] in seen: continue
        seen.add(r["title"]); out.append(r)
    return out

def theme_rows(slug,year,major):
    vals=CALENDAR_THEMES[slug]; bytitle={r["title"].lower():r for r in major};rows=[]
    for name in vals:
        hit=next((r for k,r in bytitle.items() if any(w in k for w in name.lower().split(" / "))),None)
        rows.append(hit or {"title":name,"meta":str(year),"detail":"Festival-calendar reference; exact date appears when backed by a verified Tithika selector."})
    return rows

def ref_items(vals,note="Structured festival reference"):
    return [{"title":x,"meta":"Tithika reference","detail":note} for x in vals]

def main():
    p=json.loads(sys.stdin.read() or "{}");slug=str(p.get("slug") or "").strip("/")
    lat=float(p.get("lat",18.5204));lon=float(p.get("lon",73.8567));tzname=p.get("timezone") or "Asia/Kolkata"
    try: tz=ZoneInfo(tzname)
    except ZoneInfoNotFoundError: tz=ZoneInfo("Asia/Kolkata");tzname="Asia/Kolkata"
    selected=datetime.strptime(p.get("date") or datetime.now(tz).strftime("%Y-%m-%d"),"%Y-%m-%d").date();year=selected.year
    major=major_events(year,lat,lon,tz); yearly=yearly_events(year,lat,lon,tz);sections=[];title=slug.split("/")[-1].replace("-"," ").title()
    if slug in ("calendars/hindu","calendars/indian","festivals/hindu"):
        title="Hindu Festival Calendar" if slug!="calendars/indian" else "Indian Festival Calendar"
        sections=[{"title":f"Calculated Hindu calendar {year}","note":"Major festival selectors plus recurring Ekadashi, Purnima, Amavasya and Sankranti engines.","items":yearly}]
    elif slug in ("festivals/tamil","calendars/tamil"):
        title="Tamil Festival Calendar";sections=[{"title":"Tamil solar calendar","note":"Nirayana solar month aggregation.","items":regional_year(year,lat,lon,tz,"tamil")},{"title":"Calculated observances","note":"Shared festival and recurring lunar/solar rules","items":yearly}]
    elif slug in ("festivals/malayalam","calendars/malayalam"):
        title="Malayalam Festival Calendar";sections=[{"title":"Malayalam solar calendar","note":"Nirayana solar month aggregation.","items":regional_year(year,lat,lon,tz,"malayalam")},{"title":"Calculated observances","note":"Shared festival and recurring lunar/solar rules","items":yearly}]
    elif slug in MONTH_SLUGS:
        title=MONTH_SLUGS[slug]+" Festivals";sections=[{"title":f"{MONTH_SLUGS[slug]} {year}","note":"Major verified events filtered by Purnimanta month at local sunrise.","items":month_rows(year,lat,lon,tz,MONTH_SLUGS[slug])}]
    elif slug=="calendars/purnima":
        title="Purnima Calendar";sections=[{"title":str(year),"note":"Exact full-moon Tithi occurrences.","items":purnima_rows(year,lat,lon,tz)}]
    elif slug in CALENDAR_THEMES:
        title=slug.split("/")[-1].replace("-"," ").title()+" Calendar";sections=[{"title":str(year),"note":"Festival-family aggregation; verified selectors are reused where available.","items":theme_rows(slug,year,major)}]
    elif slug in ("festivals/top-10","festivals/top-20","festivals/top-25"):
        n=int(slug.split("-")[-1]);title=f"Top {n} Hindu Festivals"
        extra=["Makar Sankranti","Maha Shivaratri","Rama Navami","Hanuman Jayanti","Akshaya Tritiya","Guru Purnima","Raksha Bandhan","Krishna Janmashtami","Ganesh Chaturthi","Navratri","Dussehra","Karwa Chauth","Dhanteras","Diwali","Govardhan Puja","Bhai Dooj","Holi","Durga Puja","Chhath","Onam","Gudi Padwa","Ugadi","Vasant Panchami","Vat Savitri","Teej"]
        sections=[{"title":title,"note":"Discovery collection; calculated festival pages retain their own exact selectors.","items":ref_items(extra[:n])}]
    elif slug in COLLECTIONS:
        title=slug.split("/")[-1].replace("-"," ").title();sections=[{"title":title,"note":"Structured festival knowledge collection.","items":ref_items(COLLECTIONS[slug])}]
    elif slug in PUJA:
        title,steps=PUJA[slug];sections=[{"title":title,"note":"Concise ritual sequence; household/Sampradaya practice may vary.","items":[{"title":f"{i+1}. {x}","meta":"Puja step","detail":"Follow family, temple or priest guidance for mantra and offering details."} for i,x in enumerate(steps)]}]
    else: raise ValueError("Unsupported festival/calendar completion slug")
    count=sum(len(s.get("items",[])) for s in sections)
    print(json.dumps({"ok":True,"family":"festival-calendar","slug":slug,"title":title,"year":year,
      "summary":f"{count} aggregated row(s) · {tzname}",
      "metrics":[{"label":"Rows","value":str(count),"note":str(year)},{"label":"Festival rules","value":str(len(festival_rules.SUPPORTED_KINDS)),"note":"verified selectors"},{"label":"Aggregation","value":"Shared","note":"no duplicate astronomy"}],
      "sections":sections,"engine":{"name":"tithika-festival-calendar-completion","version":ENGINE_VERSION,"ayanamsha":"Lahiri / Chitrapaksha"}},ensure_ascii=False))
if __name__=="__main__":
    try: main()
    except Exception as exc:
        print(json.dumps({"ok":False,"error":str(exc),"code":"FESTIVAL_CALENDAR_COMPLETION_FAILED"}));sys.exit(1)
