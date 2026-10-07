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
    moon,sun,asc,st=base_state(moment,lat,lon)
    placements=planetary.positions(moment,False,"mean")
    rows=[
      row("Prashna Lagna",asc["lagna"],f'{asc["degree_in_sign"]:.2f}°',"Question-time ascendant"),
      row("Moon",moon["rashi"],moon["nakshatra"],"Question-time Moon"),
      row("Tithi",st["tithi"],st["paksha"],"Question-time Panchang"),
      row("Yoga",st["yoga"],"","Question-time Nitya Yoga"),
    ]
    for p in placements:
        house=((int(p["rashi_id"])-int(asc["lagna_id"]))%12)+1
        rows.append(row(p["name"],f'{p["rashi"]} · House {house}',f'{p["degree_in_rashi"]:.2f}°',"Question-time whole-sign placement"))
    return rows

def trinal_lord_context(moment,lat,lon):
    moon,_,asc,_=base_state(moment,lat,lon)
    lagna_id=int(asc["lagna_id"])
    roles=[
      ("Life stone · Lagna lord",lagna_id),
      ("Supporting stone · 5th lord",(lagna_id+4)%12),
      ("Fortune stone · 9th lord",(lagna_id+8)%12),
    ]
    out=[]
    seen=set()
    for role,sign_id in roles:
        sign=panchang.RASHI_NAMES[sign_id];lord=RASHI_LORD[sign]
        if lord in seen: continue
        seen.add(lord)
        state=planetary.planet_state(lord,moment)
        house=((int(state["rashi_id"])-lagna_id)%12)+1
        out.append((role,sign,lord,state,house))
    moon_lord=RASHI_LORD[moon["rashi"]]
    if moon_lord not in seen:
        state=planetary.planet_state(moon_lord,moment)
        house=((int(state["rashi_id"])-lagna_id)%12)+1
        out.append(("Moon-sign support",moon["rashi"],moon_lord,state,house))
    return moon,asc,out

def gemstone(moment,lat,lon):
    moon,asc,candidates=trinal_lord_context(moment,lat,lon)
    rows=[
      row("Lagna",asc["lagna"],f'{asc["degree_in_sign"]:.2f}°',"Whole-sign chart anchor"),
      row("Moon sign",moon["rashi"],moon["nakshatra"],"Mind/emotional context"),
    ]
    for role,sign,lord,state,house in candidates:
        gem=GEMS.get(lord,"—")
        rows.append(row(
          role,gem,f"{lord} rules {sign}",
          f'Natal placement: {state["rashi"]} · House {house} · {state["degree_in_rashi"]:.2f}°. '
          "This is a lordship-based candidate, not an automatic prescription; dignity, strength, affliction and contraindications require full-chart review."
        ))
    return rows

def rudraksha(moment,lat,lon):
    moon,asc,candidates=trinal_lord_context(moment,lat,lon)
    rows=[
      row("Lagna",asc["lagna"],f'{asc["degree_in_sign"]:.2f}°',"Primary birth-chart anchor"),
      row("Janma Nakshatra",moon["nakshatra"],f'Pada {moon["pada"]}',f'Moon sign {moon["rashi"]}'),
    ]
    for role,sign,lord,state,house in candidates:
        rows.append(row(
          role,RUDRA.get(lord,"5 Mukhi"),f"{lord} · {sign}",
          f'Natal {lord}: {state["rashi"]} · House {house}. Traditional lordship mapping; sectarian practice and suitability can differ.'
        ))
    if not any(r["meta"]=="5 Mukhi" for r in rows):
        rows.append(row("General devotional option","5 Mukhi","Traditional broad-use reference","Not a substitute for Sampradaya or practitioner guidance."))
    return rows

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
    """Find the 1000th astronomical full Moon after the birth instant."""
    first_event=panchang.astronomy.SearchMoonPhase(
        180.0,panchang.astronomy_time(moment),40.0
    )
    if first_event is None: raise ValueError("First post-birth full Moon not found")
    first=panchang.datetime_from_astronomy(first_event,moment.tzinfo)
    # The mean synodic month is used only to jump near lunation #1000.
    # The reported milestone itself is refined by Astronomy Engine.
    approx=first+timedelta(days=29.530588861*999)
    target_event=panchang.astronomy.SearchMoonPhase(
        180.0,panchang.astronomy_time(approx-timedelta(days=3)),7.0
    )
    if target_event is None: raise ValueError("1000th full Moon not found")
    target=panchang.datetime_from_astronomy(target_event,moment.tzinfo)
    age=target-moment
    return [
      row("First full Moon after birth",first.isoformat(),first.strftime("%A"),"Counted as full Moon #1."),
      row("1000th full Moon",target.isoformat(),target.strftime("%A"),"Exact geocentric Sun-Moon opposition refined by Astronomy Engine."),
      row("Age at milestone",f"{age.days} days",f"{age.days/365.2425:.2f} tropical years","Ritual scheduling can still follow family or priestly convention.")
    ]

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
    # A deterministic question-chart context. Do not fabricate a prophetic
    # favourable/mixed/cautious answer from an arbitrary modulo operation.
    _,_,asc,st=base_state(moment,lat,lon)
    return [
      row("Question Lagna",asc["lagna"],f'{asc["degree_in_sign"]:.2f}°',"Use as the chart anchor for a traditional Prashna reading."),
      row("Moon Nakshatra",st["nakshatra"],st["tithi"],"Question-time lunar context."),
      row("Panchang Yoga",st["yoga"],st["paksha"],"Context only; no automatic yes/no prediction is generated."),
      row("Method note","Chart context only","","A complete Prashnavali answer requires a named traditional text/system; Tithika does not invent one.")
    ]

PANCHA_PAKSHI_GROUPS=[
    (0,4,"Vulture"),   # Ashwini .. Mrigashira
    (5,10,"Owl"),      # Ardra .. Purva Phalguni
    (11,15,"Crow"),    # Uttara Phalguni .. Vishakha
    (16,21,"Cock"),    # Anuradha .. Shravana
    (22,26,"Peacock"), # Dhanishtha .. Revati
]
PANCHA_PAKSHI_DARK_REVERSE={"Vulture":"Peacock","Owl":"Cock","Crow":"Crow","Cock":"Owl","Peacock":"Vulture"}

def birth_bird(nakshatra,paksha):
    idx=panchang.NAKSHATRA_NAMES.index(nakshatra)
    bird=next(b for lo,hi,b in PANCHA_PAKSHI_GROUPS if lo<=idx<=hi)
    return PANCHA_PAKSHI_DARK_REVERSE[bird] if paksha=="Krishna Paksha" else bird

def pancha_pakshi(moment):
    moon=planetary.planet_state("Moon",moment);state=panchang.state_at(moment)
    bird=birth_bird(moon["nakshatra"],state["paksha"])
    return [
      row("Birth bird",bird,moon["nakshatra"],f'{state["paksha"]} · Nakshatra/Paksha assignment profile'),
      row("Birth Nakshatra",moon["nakshatra"],f'Pada {moon["pada"]}',"Lahiri sidereal Moon"),
      row("Birth Paksha",state["paksha"],state["tithi"],"Paksha is part of the bird assignment profile."),
      row("Current Panchang",state["tithi"],moment.strftime("%A"),"Open the Pancha Pakshi Muhurat page for the full activity timeline.")
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
    elif slug=="jyotish/name-initials": title="Name Initials";items=initials(str(p.get("name") or ""))
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
