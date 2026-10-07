#!/usr/bin/env python3
"""Deterministic adapters for Tithika's secondary Jyotish utilities."""
from __future__ import annotations
import json, math, sys
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
import panchang, planetary, lagna, panchang_reuse

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
GEMS={"Sun":"Ruby","Moon":"Pearl","Mars":"Red Coral","Mercury":"Emerald","Jupiter":"Yellow Sapphire","Venus":"Diamond / White Sapphire","Saturn":"Blue Sapphire"}
RUDRA={"Sun":"1 Mukhi","Moon":"2 Mukhi","Mars":"3 Mukhi","Mercury":"4 Mukhi","Jupiter":"5 Mukhi","Venus":"6 Mukhi","Saturn":"7 Mukhi"}
RASHI_INITIALS={
"Mesha":["A","L","E"],"Vrishabha":["B","V","U"],"Mithuna":["K","Chh","Gh"],"Karka":["D","H"],"Simha":["M","T"],"Kanya":["P","Th","N"],"Tula":["R","T"],"Vrishchika":["N","Y"],"Dhanu":["Bh","Dh","Ph"],"Makara":["Kh","J"],"Kumbha":["G","S","Sh"],"Meena":["D","Ch","Z"]
}

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
    """Question-time D1 chart foundation with all classical Grahas."""
    moon,sun,asc,st=base_state(moment,lat,lon)
    items=[
      row("Prashna Lagna",asc["lagna"],f'{asc["degree_in_sign"]:.2f}°',"Question-time ascendant"),
      row("Tithi",st["tithi"],st["paksha"],"Question-time Panchang"),
      row("Nakshatra",st["nakshatra"],f'Pada {st["nakshatra_pada"]}',"Question-time Moon"),
      row("Yoga",st["yoga"],"","Question-time Nitya Yoga"),
    ]
    for graha in planetary.positions(moment,False,"mean"):
        house=((int(graha["rashi_id"])-int(asc["lagna_id"]))%12)+1
        status=[]
        if graha.get("retrograde"): status.append("retrograde")
        if graha.get("combust"): status.append("combust")
        detail=f'{graha["nakshatra"]} Pada {graha["pada"]}'
        if status: detail+=" · "+", ".join(status)
        items.append(row(
          graha["name"],
          f'{graha["rashi"]} {graha["degree_in_rashi"]:.2f}°',
          f'House {house}',
          detail
        ))
    return items

def gemstone(moment,lat,lon):
    moon,_,asc,_=base_state(moment,lat,lon); lord=RASHI_LORD.get(asc["lagna"],"")
    return [row("Lagna lord",lord,asc["lagna"],"Traditional baseline"),row("Traditional gemstone",GEMS.get(lord,"Consult a qualified practitioner"),"Not a medical or financial recommendation","Gem prescriptions require chart-strength and contraindication review."),row("Moon sign",moon["rashi"],moon["nakshatra"],"Context only")]

def rudraksha(moment,lat,lon):
    moon,_,asc,_=base_state(moment,lat,lon); lord=RASHI_LORD.get(asc["lagna"],"")
    return [row("Lagna lord",lord,asc["lagna"],"Traditional baseline"),row("Traditional Rudraksha",RUDRA.get(lord,"5 Mukhi"),"Reference profile","Sectarian practice and suitability can differ."),row("Janma Nakshatra",moon["nakshatra"],f'Pada {moon["pada"]}',"Birth-Moon context")]

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
    synodic=29.530588861; target=moment+timedelta(days=synodic*1000)
    return [row("1000th lunar-cycle estimate",target.date().isoformat(),f"{synodic:.9f} days × 1000","Astronomical mean-synodic estimate; ritual celebration date should be verified against local Panchang."),row("Elapsed mean days",f"{synodic*1000:.3f}","","Mean cycle, not a phase-by-phase ephemeris count.")]

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
    """Do not fabricate an oracle from unrelated Panchang indices."""
    _,_,asc,st=base_state(moment,lat,lon)
    return [
      row("Status","Quality-gated","","No deterministic Prashnavali answer is generated until a named textual tradition and its lookup rules are implemented."),
      row("Question-time context",asc["lagna"],f'{st["tithi"]} · {st["nakshatra"]}',"Context is retained for audit only; it is not converted into a favourable/unfavourable oracle."),
      row("Implementation requirement","Named source + exact table","","Future activation requires a source-locked question/index mapping and regression fixtures.")
    ]

def pancha_pakshi(moment):
    """Expose birth context without inventing a lineage-specific birth-bird mapping."""
    moon=planetary.planet_state("Moon",moment);st=panchang.state_at(moment)
    return [
      row("Status","Quality-gated","","Pancha Pakshi birth-bird selection depends on a verified tradition/profile table; Nakshatra modulo five is not used."),
      row("Janma Nakshatra",moon["nakshatra"],f'Pada {moon["pada"]}',"Birth-Moon context retained for the future verified profile."),
      row("Current Panchang",st["tithi"],f'{st["paksha"]} · {moment.strftime("%A")}',"No bird/activity prediction is emitted while the rule table is gated.")
    ]

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
