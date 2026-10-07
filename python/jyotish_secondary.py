#!/usr/bin/env python3
"""Deterministic adapters for Tithika's secondary Jyotish utilities."""
from __future__ import annotations
import json, math, sys
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
import panchang, planetary, lagna, panchang_reuse, kundali, vimshottari

ENGINE_VERSION="1.0.0"
NAK_SYLLABLES={
"Ashwini":["Chu","Che","Cho","La"],"Bharani":["Li","Lu","Le","Lo"],"Krittika":["A","I","U","E"],"Rohini":["O","Va","Vi","Vu"],
"Mrigashira":["Ve","Vo","Ka","Ki"],"Ardra":["Ku","Gha","Na","Cha"],"Punarvasu":["Ke","Ko","Ha","Hi"],"Pushya":["Hu","He","Ho","Da"],
"Ashlesha":["Di","Du","De","Do"],"Magha":["Ma","Mi","Mu","Me"],"Purva Phalguni":["Mo","Ta","Ti","Tu"],"Uttara Phalguni":["Te","To","Pa","Pi"],
"Hasta":["Pu","Sha","Na","Tha"],"Chitra":["Pe","Po","Ra","Ri"],"Swati":["Ru","Re","Ro","Ta"],"Vishakha":["Ti","Tu","Te","To"],
"Anuradha":["Na","Ni","Nu","Ne"],"Jyeshtha":["No","Ya","Yi","Yu"],"Mula":["Ye","Yo","Bha","Bhi"],"Purva Ashadha":["Bhu","Dha","Pha","Dha"],
"Uttara Ashadha":["Bhe","Bho","Ja","Ji"],"Shravana":["Khi","Khu","Khe","Kho"],"Dhanishta":["Ga","Gi","Gu","Ge"],"Shatabhisha":["Go","Sa","Si","Su"],
"Purva Bhadrapada":["Se","So","Da","Di"],"Uttara Bhadrapada":["Du","Tha","Jha","Na"],"Revati":["De","Do","Cha","Chi"]
}
RASHI_LORD={"Mesha":"Mars","Vrishabha":"Venus","Mithuna":"Mercury","Karka":"Moon","Simha":"Sun","Kanya":"Mercury","Tula":"Venus","Vrishchika":"Mars","Dhanu":"Jupiter","Makara":"Saturn","Kumbha":"Saturn","Meena":"Jupiter"}
GEMS={"Sun":"Ruby","Moon":"Pearl","Mars":"Red Coral","Mercury":"Emerald","Jupiter":"Yellow Sapphire","Venus":"Diamond / White Sapphire","Saturn":"Blue Sapphire","Rahu":"Hessonite","Ketu":"Cat\'s Eye"}
RUDRA={"Sun":"1 Mukhi","Moon":"2 Mukhi","Mars":"3 Mukhi","Mercury":"4 Mukhi","Jupiter":"5 Mukhi","Venus":"6 Mukhi","Saturn":"7 Mukhi","Rahu":"8 Mukhi","Ketu":"9 Mukhi"}
RASHI_INITIALS={
"Mesha":["A","L","E"],"Vrishabha":["B","V","U"],"Mithuna":["K","Chh","Gh"],"Karka":["D","H"],"Simha":["M","T"],"Kanya":["P","Th","N"],"Tula":["R","T"],"Vrishchika":["N","Y"],"Dhanu":["Bh","Dh","Ph"],"Makara":["Kh","J"],"Kumbha":["G","S","Sh"],"Meena":["D","Ch","Z"]
}

BRIGHT_BIRD_GROUPS=[
 ("Vulture",{"Ashwini","Bharani","Krittika","Rohini","Mrigashira"}),
 ("Owl",{"Ardra","Punarvasu","Pushya","Ashlesha","Magha"}),
 ("Crow",{"Purva Phalguni","Uttara Phalguni","Hasta","Chitra","Swati"}),
 ("Cock",{"Vishakha","Anuradha","Jyeshtha","Mula","Purva Ashadha"}),
 ("Peacock",{"Uttara Ashadha","Shravana","Dhanishtha","Shatabhisha","Purva Bhadrapada","Uttara Bhadrapada","Revati"}),
]
DARK_BIRD_GROUPS=[
 ("Vulture",{"Revati","Uttara Bhadrapada","Purva Bhadrapada","Shatabhisha","Dhanishtha"}),
 ("Owl",{"Shravana","Uttara Ashadha","Purva Ashadha","Mula","Jyeshtha"}),
 ("Crow",{"Anuradha","Vishakha","Swati","Chitra","Hasta"}),
 ("Cock",{"Uttara Phalguni","Purva Phalguni","Magha","Ashlesha","Pushya"}),
 ("Peacock",{"Punarvasu","Ardra","Mrigashira","Rohini","Krittika","Bharani","Ashwini"}),
]

def parse_dt(p,tz):
    d=str(p.get("birth_date") or p.get("date") or datetime.now(tz).strftime("%Y-%m-%d"))
    t=str(p.get("birth_time") or p.get("time") or "12:00:00")
    if len(t)==5:t+=":00"
    return datetime.strptime(d+" "+t,"%Y-%m-%d %H:%M:%S").replace(tzinfo=tz)

def base_state(moment,lat,lon):
    moon=planetary.planet_state("Moon",moment); sun=planetary.planet_state("Sun",moment); asc=lagna.lagna_state(moment,lat,lon); st=panchang.state_at(moment)
    return moon,sun,asc,st

def row(title,value,meta="",detail=""):
    return {"title":title,"meta":value,"detail":(meta+" · " if meta and detail else meta)+detail}

def prashna(moment,lat,lon):
    moon,sun,asc,st=base_state(moment,lat,lon)
    planets=planetary.positions(moment,False,"mean")
    placements=[]
    for p in planets:
        placements.append({**p,"house":((p["rashi_id"]-asc["lagna_id"])%12)+1})
    houses=[]
    for h in range(1,13):
        occupants=[p["name"] for p in placements if p["house"]==h]
        sign_id=(asc["lagna_id"]+h-1)%12
        houses.append(row(f"House {h}",panchang.RASHI_NAMES[sign_id],", ".join(occupants) or "No classical Graha","Whole-sign Prashna house"))
    return [row("Prashna Lagna",asc["lagna"],f'{asc["degree_in_sign"]:.2f}°',"Question-time ascendant"),
      row("Moon",moon["rashi"],moon["nakshatra"],"Question-time Moon"),
      row("Tithi",st["tithi"],st["paksha"],"Question-time Panchang"),
      row("Yoga",st["yoga"],"","Question-time Nitya Yoga")]+houses

def traditional_lords(moment,lat,lon):
    moon,_,asc,_=base_state(moment,lat,lon)
    lagna_lord=RASHI_LORD.get(asc["lagna"],"")
    moon_lord=RASHI_LORD.get(moon["rashi"],"")
    dasha=vimshottari.calculate(moment,moment)
    current=((dasha.get("current") or {}).get("mahadasha") or {}).get("lord")
    return moon,asc,lagna_lord,moon_lord,current

def gemstone(moment,lat,lon):
    moon,asc,lagna_lord,moon_lord,dasha_lord=traditional_lords(moment,lat,lon)
    candidates=[]
    for basis,lord in [("Lagna lord",lagna_lord),("Moon-sign lord",moon_lord),("Birth Mahadasha lord",dasha_lord)]:
        if lord and lord in GEMS:
            candidates.append(row(basis+" gemstone",GEMS[lord],lord,"Traditional correspondence; not a universal prescription."))
    return [row("Lagna lord",lagna_lord,asc["lagna"],"Chart baseline"),
            row("Moon sign",moon["rashi"],moon["nakshatra"],"Janma Chandra context")]+candidates+[
            row("Prescription status","Reference candidates only","Chart strength/exaltation, functional lordship and contraindications not collapsed into one automatic recommendation.","Use a qualified practitioner before treating a gemstone as remedial advice." )]

def rudraksha(moment,lat,lon):
    moon,asc,lagna_lord,moon_lord,dasha_lord=traditional_lords(moment,lat,lon)
    vals=[]
    for basis,lord in [("Lagna lord",lagna_lord),("Moon-sign lord",moon_lord),("Birth Mahadasha lord",dasha_lord)]:
        if lord and lord in RUDRA:
            vals.append(row(basis+" Rudraksha",RUDRA[lord],lord,"Traditional correspondence; sectarian practice can differ."))
    return [row("Janma Nakshatra",moon["nakshatra"],f'Pada {moon["pada"]}',"Birth-Moon context")]+vals

def baby(moment):
    moon=planetary.planet_state("Moon",moment); nak=moon["nakshatra"];pada=int(moon["pada"]);syll=NAK_SYLLABLES.get(nak,[])
    return [row("Janma Nakshatra",nak,f"Pada {pada}","Nirayana Moon"),row("Naming syllable",syll[pada-1] if len(syll)>=pada else "—","Traditional Namakarana sound","Use as a starting sound, not a compulsory spelling."),row("All four Pada sounds",", ".join(syll),"","Reference")]

def initials(name=""):
    initial=(name.strip()[:2] if name.strip() else "").title()
    matches=[]
    for r,vals in RASHI_INITIALS.items():
        if any(initial.lower().startswith(v.lower()) or (initial and v.lower().startswith(initial[0].lower())) for v in vals): matches.append(r)
    return [row("Name initial",initial or "Enter a name","Traditional name-Rashi heuristic","Birth chart remains authoritative"),row("Possible Rashis",", ".join(matches) if matches else "No unique mapping","","Initial-based Rashi is approximate by tradition.")]

def sahasra(moment):
    # First full Moon strictly after birth is Chandrodaya #1.
    cursor=panchang.astronomy_time(moment)
    event=panchang.astronomy.SearchMoonPhase(180.0,cursor,35.0)
    if event is None: raise ValueError("First full Moon unavailable")
    first=panchang.datetime_from_astronomy(event,moment.tzinfo)
    last=first
    for _ in range(999):
        event=panchang.astronomy.SearchMoonPhase(180.0,panchang.astronomy_time(last+timedelta(days=20)),20.0)
        if event is None: raise ValueError("Full Moon sequence interrupted")
        last=panchang.datetime_from_astronomy(event,moment.tzinfo)
    age_days=(last-moment).total_seconds()/86400.0
    return [row("First full Moon after birth",first.isoformat(),"Chandrodaya #1","Exact 180° Sun-Moon phase"),
            row("1000th full Moon",last.isoformat(),f"Age {age_days/365.2422:.2f} tropical years","Exact iterative full-Moon search, not mean-synodic multiplication."),
            row("Elapsed days",f"{age_days:.3f}","","Birth instant to 1000th full Moon.")]

def vedic_time(moment,lat,lon,tz):
    d=moment.date();sr=panchang_reuse.sunrise_for(d,lat,lon,tz)
    if sr and moment<sr:d-=timedelta(days=1)
    data=panchang_reuse.vedic_clock(d,lat,lon,tz,True,moment.strftime("%H:%M"))
    return [row("Ishtakala",data["ishtakala_60"]["label"],"60 Ghati sunrise-to-sunrise","Ghati:Pala:Vipala"),row("Day/Night Ghati",data["ritual_30_30"]["label"],data["ritual_half"],"30 daylight + 30 night Ghati profile"),row("Hindu day",data["hindu_day"],data["weekday_vedic"],data["tithi"])]

def shraddha_tithi(moment,lat,lon,tz):
    st=panchang.state_at(moment);target=int(st["tithi_id"]);year=moment.year
    found=[]
    for y in (year,year+1):
        d=date(y,8,15)
        while d<=date(y,11,15):
            sr=panchang_reuse.sunrise_for(d,lat,lon,tz)
            if sr:
                s=panchang.state_at(sr+timedelta(seconds=1));mi=panchang.lunar_month_info(sr,s);m=str(mi.get("purnimanta") or "").replace("Adhika ","")
                if s["paksha"]=="Krishna Paksha" and m in ("Bhadrapada","Ashwina") and int(s["tithi_id"])==target:
                    found.append(d);break
            d+=timedelta(days=1)
        if found:break
    return [row("Reference Tithi",st["tithi"],st["paksha"],"Captured from the supplied date/time"),row("Next matching Pitru-Paksha Tithi",found[0].isoformat() if found else "Not resolved","","Sunrise Tithi match in the Pitru-Paksha season profile.")]

def prashnavali(moment,lat,lon):
    _,_,asc,st=base_state(moment,lat,lon)
    return [row("Prashna Lagna",asc["lagna"],st["tithi"],"Question-time chart context"),
            row("Nakshatra",st["nakshatra"],st["paksha"],"Question-time Moon"),
            row("Result policy","No synthetic omen score","","Tithika does not manufacture a favourable/mixed/cautious answer from an arbitrary numeric remainder. A named textual Prashnavali requires its own sourced corpus and selection method.")]

def pancha_pakshi(moment):
    moon=planetary.planet_state("Moon",moment);st=panchang.state_at(moment)
    groups=BRIGHT_BIRD_GROUPS if st["paksha"]=="Shukla Paksha" else DARK_BIRD_GROUPS
    bird=next((b for b,naks in groups if moon["nakshatra"] in naks),None)
    if bird is None: raise ValueError("Birth bird mapping unavailable")
    return [row("Birth bird",bird,moon["nakshatra"],f'{st["paksha"]} Nakshatra assignment'),
            row("Janma Nakshatra",moon["nakshatra"],f'Pada {moon["pada"]}',"Lahiri sidereal Moon"),
            row("Current Panchang",st["tithi"],moment.strftime("%A"),"Use this fixed birth bird on the Pancha Pakshi Muhurat page.")]

def main():
    p=json.loads(sys.stdin.read() or "{}");slug=str(p.get("slug") or "").strip("/")
    lat=float(p.get("lat",18.5204));lon=float(p.get("lon",73.8567));tzname=p.get("timezone") or "Asia/Kolkata"
    try:tz=ZoneInfo(tzname)
    except ZoneInfoNotFoundError:tz=ZoneInfo("Asia/Kolkata");tzname="Asia/Kolkata"
    moment=parse_dt(p,tz); title=slug.split("/")[-1].replace("-"," ").title()
    if slug=="jyotish/prashna-kundali": title="Prashna Kundali";items=prashna(moment,lat,lon)
    elif slug=="jyotish/pancha-pakshi": title="Pancha Pakshi Bird Calculator";items=pancha_pakshi(moment)
    elif slug=="jyotish/gemstone": title="Gemstone Calculator";items=gemstone(moment,lat,lon)
    elif slug=="jyotish/rudraksha": title="Rudraksha Calculator";items=rudraksha(moment,lat,lon)
    elif slug=="jyotish/baby-name": title="Baby Name Calculator";items=baby(moment)
    elif slug=="jyotish/sahasra-chandrodaya": title="1000 Chandrodaya Calculator";items=sahasra(moment)
    elif slug=="jyotish/vedic-time": title="Vedic Time";items=vedic_time(moment,lat,lon,tz)
    elif slug=="jyotish/shraddha-tithi": title="Shraddha Tithi Calculator";items=shraddha_tithi(moment,lat,lon,tz)
    elif slug=="jyotish/name-initials": title="Name Initials";items=baby(moment)
    elif slug=="jyotish/prashnavali": title="Prashnavali";items=prashnavali(moment,lat,lon)
    elif slug=="jyotish/rashi-by-name": title="Find Rashi by Name";items=initials(str(p.get("name") or p.get("city") or ""))
    else:raise ValueError("Unsupported secondary Jyotish slug")
    note="Traditional Jyotish reference. Interpretive recommendations are not medical, financial or scientific claims."
    print(json.dumps({"ok":True,"family":"jyotish-secondary","slug":slug,"title":title,"year":moment.year,"summary":note,
      "metrics":[{"label":"Moment","value":moment.strftime("%Y-%m-%d %H:%M"),"note":tzname},{"label":"Ayanamsha","value":"Lahiri","note":"shared planetary core"},{"label":"Method","value":"Deterministic","note":"no random result"}],
      "sections":[{"title":title,"note":note,"items":items}],"engine":{"name":"tithika-jyotish-secondary","version":ENGINE_VERSION,"ayanamsha":"Lahiri / Chitrapaksha"}},ensure_ascii=False))
if __name__=="__main__":
    try:main()
    except Exception as exc:
        print(json.dumps({"ok":False,"error":str(exc),"code":"JYOTISH_SECONDARY_FAILED"}));sys.exit(1)
