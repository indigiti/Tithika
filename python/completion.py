#!/usr/bin/env python3
"""Tithika completion engine for the six remaining rule families.

The engine deliberately composes Tithika's existing Lahiri Panchang, festival,
Vrat, regional-calendar and planetary substrates.  Every mode exposes its rule
profile in the JSON response so UI and regression fixtures can audit selection.
"""
from __future__ import annotations

import json
import math
import sys
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import festival_rules
import lagna
import lunar_occurrences
import mahadwadashi
import panchang
import planetary
import regional_calendar
import sankranti
import vrat_rules

ENGINE_VERSION = "1.0.0"

MODE_TITLES = {
    "manvadi": "Manvadi Tithi",
    "yugadi-tithi": "Yugadi Tithi",
    "kalpadi": "Kalpadi Tithi",
    "kranti-samya": "Kranti Samya / Mahapata",
    "gowri": "Gowri Panchangam",
    "jain-pachchakkhan": "Jain Pachchakkhan",
    "pancha-pakshi": "Pancha Pakshi",
    "do-ghati": "Do Ghati Muhurat",
    "shubha-dates": "Shubha Dates",
    "iskcon-ekadashi": "ISKCON Ekadashi",
    "kalashtami": "Kalashtami",
    "chandra-darshan": "Chandra Darshan",
    "masik-janmashtami": "Masik Janmashtami",
    "ishti-anvadhan": "Ishti & Anvadhan",
    "shraddha": "Shraddha Dates",
    "purushottam-maas": "Purushottam Maas",
    "chaturmasa": "Chaturmasa",
    "festival-hindu": "Hindu Festival Calendar",
    "festival-tamil": "Tamil Festival Calendar",
    "festival-malayalam": "Malayalam Festival Calendar",
    "festival-month": "Lunar Month Festival Calendar",
    "festival-yearly": "Festival Yearly Calendar",
    "prashna-kundali": "Prashna Kundali",
    "gemstone": "Gemstone Calculator",
    "rudraksha": "Rudraksha Calculator",
    "baby-name": "Baby Name / Initials",
    "name-initials": "Name Initials",
    "rashi-by-name": "Rashi by Name",
    "sahasra-chandrodaya": "1000 Chandrodaya",
    "shraddha-tithi": "Shraddha Tithi",
    "planet-parallel": "Planetary Parallels",
    "ecliptic-crossings": "Ecliptic Crossings",
    "indian-seasons": "Indian Seasons",
}

MANVADI_RULES = [
    ("Brahma Savarni Manvadi", "Magha", 6),
    ("Savarni Manvadi", "Phalguna", 14),
    ("Swayambhuva Manvadi", "Chaitra", 2),
    ("Swarochisha Manvadi", "Chaitra", 14),
    ("Vaivaswata Manvadi", "Jyeshtha", 14),
    ("Raivata Manvadi", "Ashadha", 9),
    ("Chakshusha Manvadi", "Ashadha", 14),
    ("Indra Savarni Manvadi", "Bhadrapada", 22),
    ("Daiva Savarni Manvadi", "Bhadrapada", 29),
    ("Rudra Savarni Manvadi", "Bhadrapada", 2),
    ("Daksha Savarni Manvadi", "Ashwina", 8),
    ("Tamasa Manvadi", "Kartika", 11),
    ("Uttama Manvadi", "Kartika", 14),
    ("Dharma Savarni Manvadi", "Pausha", 10),
]
YUGADI_RULES = [
    ("Dwapara Yuga Diwas", "Phalguna", 29),
    ("Treta Yuga Diwas", "Vaishakha", 2),
    ("Kali Yuga Diwas", "Ashwina", 27),
    ("Satya Yuga Diwas", "Kartika", 8),
]
KALPADI_RULES = [
    ("Varaha Kalpadi", "Magha", 12),
    ("Brahma Kalpadi", "Chaitra", 17),
    ("Kurma Kalpadi First", "Chaitra", 0),
    ("Kurma Kalpadi Second", "Chaitra", 4),
    ("Parthiva Kalpadi", "Vaishakha", 2),
    ("Savitri Kalpadi", "Kartika", 6),
    ("Pralaya Kalpadi", "Margashirsha", 8),
]

GOWRI_DAY = {
    6:["Uthi","Amirdha","Rogam","Laabam","Dhanam","Sugam","Soram","Visham"],
    0:["Amirdha","Visham","Rogam","Laabam","Dhanam","Sugam","Soram","Uthi"],
    1:["Rogam","Laabam","Dhanam","Sugam","Soram","Uthi","Visham","Amirdha"],
    2:["Laabam","Dhanam","Sugam","Soram","Visham","Uthi","Amirdha","Rogam"],
    3:["Dhanam","Sugam","Soram","Uthi","Amirdha","Visham","Rogam","Laabam"],
    4:["Sugam","Soram","Uthi","Visham","Amirdha","Rogam","Laabam","Dhanam"],
    5:["Soram","Uthi","Visham","Amirdha","Rogam","Laabam","Dhanam","Sugam"],
}
GOWRI_NIGHT = {
    6:["Dhanam","Sugam","Soram","Visham","Uthi","Amirdha","Rogam","Laabam"],
    0:["Sugam","Soram","Uthi","Amirdha","Visham","Rogam","Laabam","Dhanam"],
    1:["Soram","Uthi","Visham","Amirdha","Rogam","Laabam","Dhanam","Sugam"],
    2:["Uthi","Amirdha","Rogam","Laabam","Dhanam","Sugam","Soram","Visham"],
    3:["Amirdha","Visham","Rogam","Laabam","Dhanam","Sugam","Soram","Uthi"],
    4:["Rogam","Laabam","Dhanam","Sugam","Soram","Uthi","Visham","Amirdha"],
    5:["Laabam","Dhanam","Sugam","Soram","Uthi","Visham","Amirdha","Rogam"],
}
GOWRI_GOOD = {"Amirdha","Dhanam","Uthi","Laabam","Sugam"}

DO_GHATI_NAMES = [
    ("Rudra",False),("Uraga",False),("Mitra",True),("Pitara",False),("Vasu",True),
    ("Ambu",True),("Vishwedeva",True),("Vidhi",True),("Brahma",True),("Indra",True),
    ("Indragni",False),("Daitya",False),("Varuna",True),("Aryama",True),("Bhaga",False),
    ("Ishwara",False),("Ajaikapada",False),("Ahirbudhnya",True),("Pusha",True),("Ashwini",True),
    ("Yama",False),("Agni",False),("Brahma",True),("Chandra",True),("Aditi",True),
    ("Brihaspati",True),("Vishnu",True),("Surya",True),("Tvashta",True),("Samirana",True),
]

BIRDS = ["Vulture","Owl","Crow","Cock","Peacock"]
BRIGHT_BIRD = {
    **{n:"Vulture" for n in panchang.NAKSHATRA_NAMES[0:5]},
    **{n:"Owl" for n in panchang.NAKSHATRA_NAMES[5:11]},
    **{n:"Crow" for n in panchang.NAKSHATRA_NAMES[11:16]},
    **{n:"Cock" for n in panchang.NAKSHATRA_NAMES[16:22]},
    **{n:"Peacock" for n in panchang.NAKSHATRA_NAMES[22:27]},
}
DARK_SWAP = {"Vulture":"Peacock","Owl":"Cock","Crow":"Crow","Cock":"Owl","Peacock":"Vulture"}
ACTIVITIES = ["Ruling","Eating","Walking","Sleeping","Dying"]
ACTIVITY_SCORE = {"Ruling":1.0,"Eating":0.8,"Walking":0.6,"Sleeping":0.4,"Dying":0.2}
# Published mirror-table day groups.  The base row is rotated per bird.
BRIGHT_GROUPS = {
    "A":["Eating","Walking","Ruling","Sleeping","Dying"],
    "B":["Ruling","Sleeping","Dying","Eating","Walking"],
    "C":["Sleeping","Dying","Eating","Walking","Ruling"],
    "D":["Walking","Ruling","Sleeping","Dying","Eating"],
}
DARK_GROUPS = {
    "A":["Walking","Ruling","Eating","Dying","Sleeping"],
    "B":["Eating","Dying","Sleeping","Ruling","Walking"],
    "C":["Ruling","Eating","Walking","Sleeping","Dying"],
    "D":["Sleeping","Walking","Dying","Eating","Ruling"],
    "E":["Dying","Sleeping","Ruling","Walking","Eating"],
}

NAME_SYLLABLES = {
    "Ashwini":["Chu","Che","Cho","La"],"Bharani":["Li","Lu","Le","Lo"],
    "Krittika":["A","I","U","E"],"Rohini":["O","Va","Vi","Vu"],
    "Mrigashira":["Ve","Vo","Ka","Ki"],"Ardra":["Ku","Gha","Na","Cha"],
    "Punarvasu":["Ke","Ko","Ha","Hi"],"Pushya":["Hu","He","Ho","Da"],
    "Ashlesha":["Di","Du","De","Do"],"Magha":["Ma","Mi","Mu","Me"],
    "Purva Phalguni":["Mo","Ta","Ti","Tu"],"Uttara Phalguni":["Te","To","Pa","Pi"],
    "Hasta":["Pu","Sha","Na","Tha"],"Chitra":["Pe","Po","Ra","Ri"],
    "Swati":["Ru","Re","Ro","Ta"],"Vishakha":["Ti","Tu","Te","To"],
    "Anuradha":["Na","Ni","Nu","Ne"],"Jyeshtha":["No","Ya","Yi","Yu"],
    "Mula":["Ye","Yo","Bha","Bhi"],"Purva Ashadha":["Bhu","Dha","Pha","Dha"],
    "Uttara Ashadha":["Bhe","Bho","Ja","Ji"],"Shravana":["Ju","Je","Jo","Khi"],
    "Dhanishta":["Ga","Gi","Gu","Ge"],"Shatabhisha":["Go","Sa","Si","Su"],
    "Purva Bhadrapada":["Se","So","Da","Di"],"Uttara Bhadrapada":["Du","Tha","Jha","Na"],
    "Revati":["De","Do","Cha","Chi"],
}
RASHI_INITIALS = {
    "Mesha":["A","L","E"],"Vrishabha":["B","V","U"],"Mithuna":["K","Chh","Gh"],
    "Karka":["D","H"],"Simha":["M","T"],"Kanya":["P","Th","N"],
    "Tula":["R","T"],"Vrishchika":["N","Y"],"Dhanu":["Bh","Dh","Ph"],
    "Makara":["Kh","J"],"Kumbha":["G","S","Sh"],"Meena":["D","Ch","Z","Th"],
}
GEMSTONE_TRADITION = {
    "Mesha":("Red Coral","Mars"),"Vrishabha":("Diamond / White Sapphire","Venus"),
    "Mithuna":("Emerald","Mercury"),"Karka":("Pearl","Moon"),"Simha":("Ruby","Sun"),
    "Kanya":("Emerald","Mercury"),"Tula":("Diamond / White Sapphire","Venus"),
    "Vrishchika":("Red Coral","Mars"),"Dhanu":("Yellow Sapphire","Jupiter"),
    "Makara":("Blue Sapphire","Saturn"),"Kumbha":("Blue Sapphire","Saturn"),
    "Meena":("Yellow Sapphire","Jupiter"),
}
RUDRAKSHA_TRADITION = {
    "Mesha":"3 Mukhi","Vrishabha":"6 Mukhi","Mithuna":"4 Mukhi","Karka":"2 Mukhi",
    "Simha":"1 or 12 Mukhi","Kanya":"4 Mukhi","Tula":"6 Mukhi","Vrishchika":"3 Mukhi",
    "Dhanu":"5 Mukhi","Makara":"7 Mukhi","Kumbha":"7 Mukhi","Meena":"5 Mukhi",
}

MONTH_SLUGS = {m.lower():m for m in panchang.LUNAR_MONTH_NAMES}


def rise(d, lat, lon, tz, body=panchang.astronomy.Body.Sun):
    return panchang.rise_set(d, lat, lon, tz, body, panchang.astronomy.Direction.Rise)


def set_(d, lat, lon, tz, body=panchang.astronomy.Body.Sun):
    return panchang.rise_set(d, lat, lon, tz, body, panchang.astronomy.Direction.Set)


def strip_adhika(name):
    return str(name or "").replace("Adhika ", "").strip()


def tithi_windows(year:int, tithi_id:int, tz:ZoneInfo):
    start_angle=(tithi_id*12.0)%360.0
    end_angle=((tithi_id+1)*12.0)%360.0
    cursor=panchang.astronomy_time(datetime(year-1,12,1,0,0,tzinfo=tz))
    out=[]
    for _ in range(18):
        a=panchang.astronomy.SearchMoonPhase(start_angle,cursor,40.0)
        if a is None: break
        b=panchang.astronomy.SearchMoonPhase(end_angle,a,3.0)
        if b is None: break
        s=panchang.datetime_from_astronomy(a,tz); e=panchang.datetime_from_astronomy(b,tz)
        if s.year>year+1: break
        if e.year>=year-1 and s.year<=year+1: out.append((s,e))
        cursor=panchang.astronomy_time(s+timedelta(days=2))
    return out


def month_for_window(start,end):
    mid=start+(end-start)/2
    st=panchang.state_at(mid)
    return panchang.lunar_month_info(mid,st)


def select_tithi_day(start,end,lat,lon,tz):
    d=(start-timedelta(days=1)).date(); last=(end+timedelta(days=1)).date(); candidates=[]
    while d<=last:
        sr=rise(d,lat,lon,tz)
        if sr and start<=sr<end:
            candidates.append((d,sr))
        d+=timedelta(days=1)
    if candidates:
        return candidates[0][0], candidates[0][1], "tithi-prevails-at-sunrise"
    # Kshaya fallback: choose civil day containing the larger local overlap.
    best=None
    d=start.date()-timedelta(days=1)
    while d<=end.date()+timedelta(days=1):
        sr=rise(d,lat,lon,tz); ns=rise(d+timedelta(days=1),lat,lon,tz)
        if sr and ns:
            overlap=max(timedelta(0),min(end,ns)-max(start,sr))
            if best is None or overlap>best[0]: best=(overlap,d,sr)
        d+=timedelta(days=1)
    if best: return best[1],best[2],"kshaya-maximum-panchang-day-overlap"
    return start.date(),None,"civil-date-fallback"


def named_tithi_events(year,rules,lat,lon,tz,hour24):
    cache={}; rows=[]
    for name,month,tithi_id in rules:
        cache.setdefault(tithi_id,tithi_windows(year,tithi_id,tz))
        matches=[]
        for start,end in cache[tithi_id]:
            info=month_for_window(start,end)
            if strip_adhika(info.get("purnimanta"))!=month or info.get("adhika"):
                continue
            d,sr,basis=select_tithi_day(start,end,lat,lon,tz)
            if d.year!=year: continue
            matches.append((d,start,end,sr,basis,info))
        if not matches: continue
        d,start,end,sr,basis,info=sorted(matches,key=lambda x:x[0])[0]
        state=panchang.state_at(sr+timedelta(seconds=1)) if sr else panchang.state_at(start+(end-start)/2)
        rows.append({"name":name,"date":d.isoformat(),"weekday":d.strftime("%A"),"month":month,
                     "tithi":state["tithi"],"paksha":state["paksha"],"start":start.isoformat(),"end":end.isoformat(),
                     "start_label":panchang.transition_label(start,d,hour24),"end_label":panchang.transition_label(end,d,hour24),
                     "basis":basis})
    return sorted(rows,key=lambda r:r["date"])


def declination(body,moment,lat,lon):
    t=panchang.astronomy_time(moment)
    obs=panchang.astronomy.Observer(lat,lon,0.0)
    return float(panchang.astronomy.Equator(body,t,obs,True,True).dec)


def kranti_samya(year,lat,lon,tz,hour24):
    rows=[]; start=datetime(year,1,1,0,0,tzinfo=tz); end=datetime(year+1,1,1,0,0,tzinfo=tz)
    step=timedelta(hours=3); left=start
    def f(dt): return declination(panchang.astronomy.Body.Moon,dt,lat,lon)-declination(panchang.astronomy.Body.Sun,dt,lat,lon)
    fl=f(left)
    while left<end:
        right=min(end,left+step); fr=f(right)
        if fl==0 or fl*fr<0:
            right_value=fr
            lo,hi=left,right
            for _ in range(36):
                mid=lo+(hi-lo)/2
                fm=f(mid)
                if fl*fm<=0: hi=mid; fr=fm
                else: lo=mid; fl=fm
            moment=hi; st=panchang.state_at(moment)
            if st["yoga"] in ("Vyatipata","Vaidhriti"):
                rows.append({"name":"Kranti Samya / Mahapata","date":moment.date().isoformat(),"weekday":moment.strftime("%A"),
                             "datetime":moment.isoformat(),"time_label":panchang.fmt(moment,hour24),"yoga":st["yoga"],
                             "sun_declination":round(declination(panchang.astronomy.Body.Sun,moment,lat,lon),6),
                             "moon_declination":round(declination(panchang.astronomy.Body.Moon,moment,lat,lon),6),
                             "basis":"Sun-Moon declination equality during Vyatipata/Vaidhriti Yoga"})
        left=right; fl=right_value if 'right_value' in locals() else fr
        if 'right_value' in locals(): del right_value
    # de-duplicate crossings refined from adjacent samples
    ded=[]
    for row in rows:
        if not ded or abs((datetime.fromisoformat(row["datetime"])-datetime.fromisoformat(ded[-1]["datetime"])).total_seconds())>3600:
            ded.append(row)
    return ded


def split_period(start,end,n,names=None):
    span=(end-start)/n; rows=[]
    for i in range(n):
        a=start+span*i; b=start+span*(i+1); row={"index":i+1,"start":a.isoformat(),"end":b.isoformat(),
          "start_label":panchang.fmt(a),"end_label":panchang.fmt(b)}
        if names is not None: row["name"]=names[i]
        rows.append(row)
    return rows


def gowri_day(d,lat,lon,tz):
    sr=rise(d,lat,lon,tz); ss=set_(d,lat,lon,tz); ns=rise(d+timedelta(days=1),lat,lon,tz)
    if not sr or not ss or not ns: return []
    rows=[]
    for period,start,end,names in (("day",sr,ss,GOWRI_DAY[d.weekday()]),("night",ss,ns,GOWRI_NIGHT[d.weekday()])):
        for r in split_period(start,end,8,names):
            r.update({"period":period,"auspicious":r["name"] in GOWRI_GOOD,"basis":"8 equal local day/night Gowri periods"}); rows.append(r)
    return rows


def pachchakkhan(d,lat,lon,tz):
    sr=rise(d,lat,lon,tz); ss=set_(d,lat,lon,tz); ns=rise(d+timedelta(days=1),lat,lon,tz)
    if not sr or not ss or not ns: return []
    daylight=ss-sr; night=ns-ss
    points=[
        ("Sunrise",sr),("Navkarshi",sr+timedelta(minutes=48)),("Porshi",sr+daylight/4),
        ("Sadha Porshi",sr+daylight*3/8),("Purimaddha",sr+daylight/2),("Avaddha",sr+daylight*3/4),
        ("Chovihar",ss-timedelta(minutes=48)),("Evening Pratikraman",ss),
        ("Santhara Porshi",ss+night/4),("Nishita",ss+night/2),("Morning Pratikram