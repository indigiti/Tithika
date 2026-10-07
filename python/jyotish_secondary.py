#!/usr/bin/env python3
"""Secondary Jyotish utilities backed by Tithika's chart, Panchang and strength engines."""
from __future__ import annotations
import json, sys
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
import panchang, planetary, lagna, panchang_reuse, shadbala

ENGINE_VERSION="1.1.0"
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
BIRDS=["Vulture","Owl","Crow","Cock","Peacock"]
PANCHA_BIRD_BY_PAKSHA={
 "Shukla Paksha":{
  "Vulture":{"Ashwini","Bharani","Krittika","Rohini","Mrigashira"},
  "Owl":{"Ardra","Punarvasu","Pushya","Ashlesha","Magha"},
  "Crow":{"Purva Phalguni","Uttara Phalguni","Hasta","Chitra","Swati"},
  "Cock":{"Vishakha","Anuradha","Jyeshtha","Mula","Purva Ashadha"},
  "Peacock":{"Uttara Ashadha","Shravana","Dhanishta","Shatabhisha","Purva Bhadrapada","Uttara Bhadrapada","Revati"},
 },
 "Krishna Paksha":{
  "Vulture":{"Revati","Uttara Bhadrapada","Purva Bhadrapada","Shatabhisha","Dhanishta"},
  "Owl":{"Shravana","Uttara Ashadha","Purva Ashadha","Mula","Jyeshtha"},
  "Crow":{"Anuradha","Vishakha","Swati","Chitra","Hasta"},
  "Cock":{"Uttara Phalguni","Purva Phalguni","Magha","Ashlesha","Pushya"},
  "Peacock":{"Punarvasu","Ardra","Mrigashira","Rohini","Krittika","Bharani","Ashwini"},
 },
}

def parse_dt(p,tz):
    d=str(p.get("birth_date") or p.get("date") or datetime.now(tz).strftime("%Y-%m-%d"))
    t=str(p.get("birth_time") or p.get("time") or "12:00:00")
    if len(t)==5:t+=":00"
    return datetime.strptime(d+" "+t,"%Y-%m-%d %H:%M:%S").replace(tzinfo=tz)

def base_state(moment,lat,lon):
    moon=planetary.planet_state("Moon",moment);sun=planetary.planet_state("Sun",moment);asc=lagna.lagna_state(moment,lat,lon);st=panchang.state_at(moment)
    return moon,sun,asc,st

def row(title,value,meta="",detail=""):
    return {"title":title,"meta":value,"detail":(meta+" · " if meta and detail else meta)+detail}

def chart_rows(moment,lat,lon):
    asc=lagna.lagna_state(moment,lat,lon)
    rows=[row("Prashna Lagna",f'{asc["lagna"]} {asc["degree_in_sign"]:.2f}°',"Whole-sign house 1","Question-time ascendant")]
    for p in planetary.positions(moment,False,"mean"):
        house=((p["rashi_id"]-asc["lagna_id"])%12)+1
        rows.append(row(p["name"],f'{p["rashi"]} {p["degree_in_rashi"]:.2f}°',f'House {house} · {p["nakshatra"]} Pada {p["pada"]}',("Retrograde" if p["retrograde"] else "Direct")))
    st=panchang.state_at(moment)
    rows.extend([row("Tithi",st["tithi"],st["paksha"],"Question-time Panchang"),row("Yoga",st["yoga"],st["nakshatra"],"Question-time Panchang")])
    return rows

def strength_evidence(moment,lat,lon,tz,planet):
    data=shadbala.calculate({"date":moment.strftime("%Y-%m-%d"),"time":moment.strftime("%H:%M:%S"),"lat":lat,"lon":lon,"timezone":tz.key})
    return next((p for p in data["planets"] if p["planet"]==planet),None)

def gemstone(moment,lat,lon,tz):
    moon,_,asc,_=base_state(moment,lat,lon);lord=RASHI_LORD.get(asc["lagna"],"");strength=strength_evidence(moment,lat,lon,tz,lord)
    ratio=strength["ratio"] if strength else None
    return [
      row("Lagna lord",lord,asc["lagna"],"Traditional baseline used for this reference"),
      row("Lagna-lord gemstone",GEMS.get(lord,"—"),f'Shadbala {strength["total_rupa"]:.2f} Rupa · ratio {ratio:.2f}' if strength else "Strength unavailable","Candidate reference only; gemstone prescription also depends on functional beneficence, dignity, Dasha and practitioner tradition."),
      row("Moon context",moon["rashi"],moon["nakshatra"],"Not used as a one-factor prescription.")
    ]

def rudraksha(moment,lat,lon,tz):
    moon,_,asc,_=base_state(moment,lat,lon);lord=RASHI_LORD.get(asc["lagna"],"");strength=strength_evidence(moment,lat,lon,tz,lord)
    return [
      row("Lagna lord",lord,asc["lagna"],"Traditional baseline"),
      row("Lagna-lord Rudraksha",RUDRA.get(lord,"5 Mukhi"),f'Shadbala {strength["total_rupa"]:.2f} Rupa' if strength else "Strength unavailable","Reference association, not a universal prescription."),
      row("Janma Nakshatra",moon["nakshatra"],f'Pada {moon["pada"]}',"Birth-Moon context")
    ]

def baby(moment):
    moon=planetary.planet_state("Moon",moment);nak=moon["nakshatra"];pada=int(moon["pada"]);syll=NAK_SYLLABLES.get(nak,[])
    return [row("Janma Nakshatra",nak,f"Pada {pada}","Nirayana Moon"),row("Naming syllable",syll[pada-1] if len(syll)>=pada else "—","Traditional Namakarana sound","Use as a starting sound, not a compulsory spelling."),row("All four Pada sounds",", ".join(syll),"","Reference")]

def initials(name=""):
    initial=(name.strip()[:2] if name.strip() else "").title();matches=[]
    for r,vals in RASHI_INITIALS.items():
        if any(initial.lower().startswith(v.lower()) or (initial and v.lower().startswith(initial[0].lower())) for v in vals):matches.append(r)
    return [row("Name initial",initial or "Enter a name","Traditional name-Rashi heuristic","Birth chart remains authoritative"),row("Possible Rashis",", ".join(matches) if matches else "No unique mapping","","Initial-based Rashi is approximate and may map to multiple signs.")]

def sahasra(moment):
    # Count the first full Moon after the birth moment as #1, jump close to
    # the 1000th using the mean synodic month, then refine to the exact phase.
    first=panchang.astronomy.SearchMoonPhase(180.0,panchang.astronomy_time(moment),40.0)
    if first is None:return [row("1000th full Moon","Not resolved","","Astronomy search failed")]
    first_dt=panchang.datetime_from_astronomy(first,moment.tzinfo)
    estimate=first_dt+timedelta(days=29.530588861*999)
    target=panchang.astronomy.SearchMoonPhase(180.0,panchang.astronomy_time(estimate-timedelta(days=10)),20.0)
    if target is None:return [row("1000th full Moon","Not resolved","","Final phase search failed")]
    exact=panchang.datetime_from_astronomy(target,moment.tzinfo)
    return [row("First full Moon after birth",first_dt.isoformat(),"Full-Moon phase #1","Geocentric phase instant"),row("1000th full Moon phase",exact.isoformat(),exact.strftime("%A"),"Mean-cycle jump refined by Astronomy Engine full-Moon search; ritual celebration date should be checked against the local Panchang.")]

def vedic_time(moment,lat,lon,tz):
    d=moment.date();sr=panchang_reuse.sunrise_for(d,lat,lon,tz)
    if sr and moment<sr:d-=timedelta(days=1)
    data=panchang_reuse.vedic_clock(d,lat,lon,tz,True,moment.strftime("%H:%M"))
    return [row("Ishtakala",data["ishtakala_60"]["label"],"60 Ghati sunrise-to-sunrise","Ghati:Pala:Vipala"),row("Day/Night Ghati",data["ritual_30_30"]["label"],data["ritual_half"],"30 daylight + 30 night Ghati profile"),row("Hindu day",data["hindu_day"],data["weekday_vedic"],data["tithi"])]

def shraddha_tithi(moment,lat,lon,tz):
    st=panchang.state_at(moment);target=int(st["tithi_id"]);year=moment.year;found=[]
    for y in (year,year+1):
        d=date(y,8,15)
        while d<=date(y,11,15):
            sr=panchang_reuse.sunrise_for(d,lat,lon,tz)
            if sr:
                s=panchang.state_at(sr+timedelta(seconds=1));mi=panchang.lunar_month_info(sr,s);m=str(mi.get("purnimanta") or "").replace("Adhika ","")
                if s["paksha"]=="Krishna Paksha" and m=="Ashwina" and int(s["tithi_id"])==target:
                    found.append(d);break
            d+=timedelta(days=1)
        if found:break
    return [row("Reference Tithi",st["tithi"],st["paksha"],"Captured from the supplied date/time"),row("Next matching Pitru-Paksha Tithi",found[0].isoformat() if found else "Not resolved","Ashwina Krishna","Sunrise Tithi match in the Purnimanta Pitru-Paksha profile.")]

def prashnavali(moment,lat,lon):
    # Do not manufacture a divinatory yes/no result. A named textual
    # Prashnavali requires an explicit traditional grid/selection supplied by
    # the user. Until then provide only auditable Prashna chart context.
    st=panchang.state_at(moment);asc=lagna.lagna_state(moment,lat,lon);moon=planetary.planet_state("Moon",moment)
    return [row("Prashna context",f'{asc["lagna"]} Lagna',st["tithi"],"No synthetic favourable/unfavourable verdict is generated."),row("Question-time Moon",moon["rashi"],moon["nakshatra"],"Use a named Prashnavali text/grid for a textual oracle result."),row("Input requirement","Traditional selection required","Grid/cell/verse","Tithika will not infer an oracle answer from an unrelated Nakshatra modulo.")]

def pancha_birth_bird(nakshatra,paksha):
    table=PANCHA_BIRD_BY_PAKSHA.get(paksha) or PANCHA_BIRD_BY_PAKSHA["Shukla Paksha"]
    return next((bird for bird,naks in table.items() if nakshatra in naks),None)

def pancha_pakshi(moment):
    moon=planetary.planet_state("Moon",moment);st=panchang.state_at(moment)
    bird=pancha_birth_bird(moon["nakshatra"],st["paksha"]) or "Unresolved"
    return [
      row("Birth bird",bird,moon["nakshatra"],f'{st["paksha"]} · Nakshatra/Paksha assignment'),
      row("Assignment profile","Explicit 27-Nakshatra bright/dark table","Named traditional profile","Pancha Pakshi lineages publish variant groupings; Tithika keeps this table explicit instead of deriving a hidden longitude shortcut."),
      row("Current Panchang",st["tithi"],moment.strftime("%A"),"Open Pancha Pakshi Muhurat for location-aware Yama/sub-Yama timing.")
    ]

def main():
    p=json.loads(sys.stdin.read() or "{}");slug=str(p.get("slug") or "").strip("/")
    lat=float(p.get("lat",18.5204));lon=float(p.get("lon",73.8567));tzname=p.get("timezone") or "Asia/Kolkata"
    try:tz=ZoneInfo(tzname)
    except ZoneInfoNotFoundError:tz=ZoneInfo("Asia/Kolkata");tzname="Asia/Kolkata"
    moment=parse_dt(p,tz);title=slug.split("/")[-1].replace("-"," ").title()
    if slug=="jyotish/prashna-kundali":title="Prashna Kundali";items=chart_rows(moment,lat,lon)
    elif slug=="jyotish/pancha-pakshi":title="Pancha Pakshi Bird Calculator";items=pancha_pakshi(moment)
    elif slug=="jyotish/gemstone":title="Gemstone Reference Calculator";items=gemstone(moment,lat,lon,tz)
    elif slug=="jyotish/rudraksha":title="Rudraksha Reference Calculator";items=rudraksha(moment,lat,lon,tz)
    elif slug=="jyotish/baby-name":title="Baby Name Calculator";items=baby(moment)
    elif slug=="jyotish/sahasra-chandrodaya":title="1000 Chandrodaya Calculator";items=sahasra(moment)
    elif slug=="jyotish/vedic-time":title="Vedic Time";items=vedic_time(moment,lat,lon,tz)
    elif slug=="jyotish/shraddha-tithi":title="Shraddha Tithi Calculator";items=shraddha_tithi(moment,lat,lon,tz)
    elif slug=="jyotish/name-initials":title="Name Initials";items=initials(str(p.get("name") or ""))
    elif slug=="jyotish/prashnavali":title="Prashnavali / Prashna Context";items=prashnavali(moment,lat,lon)
    elif slug=="jyotish/rashi-by-name":title="Find Rashi by Name";items=initials(str(p.get("name") or ""))
    else:raise ValueError("Unsupported secondary Jyotish slug")
    note="Traditional Jyotish reference. Calculated astronomy/chart factors are separated from interpretive or lineage-specific recommendations."
    print(json.dumps({"ok":True,"family":"jyotish-secondary","slug":slug,"title":title,"year":moment.year,"summary":note,
      "metrics":[{"label":"Moment","value":moment.strftime("%Y-%m-%d %H:%M"),"note":tzname},{"label":"Ayanamsha","value":"Lahiri","note":"shared planetary core"},{"label":"Method","value":"Auditable","note":"no random/synthetic verdict"}],
      "sections":[{"title":title,"note":note,"items":items}],"engine":{"name":"tithika-jyotish-secondary","version":ENGINE_VERSION,"ayanamsha":"Lahiri / Chitrapaksha"}},ensure_ascii=False))
if __name__=="__main__":
    try:main()
    except Exception as exc:
        print(json.dumps({"ok":False,"error":str(exc),"code":"JYOTISH_SECONDARY_FAILED"}));sys.exit(1)
