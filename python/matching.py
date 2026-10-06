#!/usr/bin/env python3
"""
Tithika Ashtakoota / Guna Milan compatibility engine.

Two modes:
- horoscope: full birth profiles with Moon-based 36-point Ashtakoota plus
  separate Mangal, D1 summary and current Vimshottari integration.
- nakshatra: lightweight Nakshatra + Pada compatibility using the same tables.

The 36-point score is Moon-based. Mangal Dosha is intentionally kept outside
the score, matching standard Ashtakoota practice.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import doshas
import lagna
import panchang
import planetary
import vimshottari
import marriage_analysis

ENGINE_VERSION = "0.1.0"
NAK_SPAN = 360.0 / 27.0
PADA_SPAN = NAK_SPAN / 4.0

SIGN_LORDS = ["Mars","Venus","Mercury","Moon","Sun","Mercury","Venus","Mars","Jupiter","Saturn","Saturn","Jupiter"]

VARNA = {
    0:("Kshatriya",3), 1:("Vaishya",2), 2:("Shudra",1), 3:("Brahmin",4),
    4:("Kshatriya",3), 5:("Vaishya",2), 6:("Shudra",1), 7:("Brahmin",4),
    8:("Kshatriya",3), 9:("Vaishya",2), 10:("Shudra",1), 11:("Brahmin",4),
}

VASHYA_ORDER=["Chatushpada","Manava","Jalachara","Vanachara","Keeta"]
VASHYA_MATRIX=[
    [2.0,1.0,1.0,0.0,1.0],
    [1.0,2.0,0.5,0.0,1.0],
    [1.0,0.5,2.0,0.0,1.0],
    [0.0,0.0,0.0,2.0,0.0],
    [1.0,1.0,1.0,0.0,2.0],
]

TARA_NAMES=["Janma","Sampat","Vipat","Kshema","Pratyari","Sadhaka","Vadha","Maitra","Ati-Maitra"]
TARA_BAD={3,5,7}

YONI_NAMES=["Horse","Elephant","Goat","Serpent","Dog","Cat","Rat","Cow","Buffalo","Tiger","Deer","Monkey","Mongoose","Lion"]
YONI_BY_NAK=[
    "Horse","Elephant","Goat","Serpent","Serpent","Dog","Cat","Goat","Cat",
    "Rat","Rat","Cow","Buffalo","Tiger","Buffalo","Tiger","Deer","Deer",
    "Dog","Monkey","Mongoose","Monkey","Lion","Horse","Lion","Cow","Elephant"
]
YONI_MATRIX=[
    [4,2,2,3,2,2,2,1,0,1,3,3,2,1],
    [2,4,3,3,2,2,2,2,3,1,2,3,2,0],
    [2,3,4,2,1,2,1,3,3,1,2,0,3,1],
    [3,3,2,4,2,1,1,1,1,2,2,2,0,2],
    [2,2,1,2,4,2,1,2,2,1,0,2,1,1],
    [2,2,2,1,2,4,0,2,2,1,3,3,2,1],
    [2,2,1,1,1,0,4,2,2,2,2,2,1,2],
    [1,2,3,1,2,2,2,4,3,0,3,2,2,1],
    [0,3,3,1,2,2,2,3,4,1,2,2,2,1],
    [1,1,1,2,1,1,2,0,1,4,1,1,2,1],
    [3,2,2,2,0,3,2,3,2,1,4,3,2,1],
    [3,3,0,2,2,3,2,2,2,1,3,4,3,2],
    [2,2,3,0,1,2,1,2,2,2,2,3,4,2],
    [1,0,1,2,1,1,2,1,1,1,1,2,2,4],
]

GANA_BY_NAK=[
    "Deva","Manushya","Rakshasa","Manushya","Deva","Manushya","Deva","Deva","Rakshasa",
    "Rakshasa","Manushya","Manushya","Deva","Rakshasa","Deva","Rakshasa","Deva","Rakshasa",
    "Rakshasa","Manushya","Manushya","Deva","Rakshasa","Rakshasa","Manushya","Manushya","Deva"
]
GANA_POINTS={
    ("Deva","Deva"):6.0,("Deva","Manushya"):6.0,("Deva","Rakshasa"):0.0,
    ("Manushya","Deva"):5.0,("Manushya","Manushya"):6.0,("Manushya","Rakshasa"):0.0,
    ("Rakshasa","Deva"):1.0,("Rakshasa","Manushya"):0.0,("Rakshasa","Rakshasa"):6.0,
}

NADI_BY_NAK=[
    "Adi","Madhya","Antya","Antya","Madhya","Adi","Adi","Madhya","Antya",
    "Antya","Madhya","Adi","Adi","Madhya","Antya","Antya","Madhya","Adi",
    "Adi","Madhya","Antya","Antya","Madhya","Adi","Adi","Madhya","Antya"
]

NATURAL={
    "Sun":{"Moon":"friend","Mars":"friend","Jupiter":"friend","Mercury":"neutral","Venus":"enemy","Saturn":"enemy"},
    "Moon":{"Sun":"friend","Mercury":"friend","Mars":"neutral","Jupiter":"neutral","Venus":"neutral","Saturn":"neutral"},
    "Mars":{"Sun":"friend","Moon":"friend","Jupiter":"friend","Mercury":"enemy","Venus":"neutral","Saturn":"neutral"},
    "Mercury":{"Sun":"friend","Venus":"friend","Moon":"enemy","Mars":"neutral","Jupiter":"neutral","Saturn":"neutral"},
    "Jupiter":{"Sun":"friend","Moon":"friend","Mars":"friend","Mercury":"enemy","Venus":"enemy","Saturn":"neutral"},
    "Venus":{"Mercury":"friend","Saturn":"friend","Sun":"enemy","Moon":"enemy","Mars":"neutral","Jupiter":"neutral"},
    "Saturn":{"Mercury":"friend","Venus":"friend","Sun":"enemy","Moon":"enemy","Mars":"neutral","Jupiter":"neutral"},
}
MAITRI_POINTS={(0,0):5.0,(0,1):4.0,(1,1):3.0,(0,2):1.0,(1,2):0.5,(2,2):0.0}
REL_RANK={"friend":0,"neutral":1,"enemy":2}
BHAKOOT_DOSHA={(2,12),(5,9),(6,8)}

def parse_birth(profile: dict) -> tuple[datetime, ZoneInfo, str]:
    tzname=str(profile.get("timezone") or "Asia/Kolkata")
    try: tz=ZoneInfo(tzname)
    except ZoneInfoNotFoundError:
        tzname="Asia/Kolkata"; tz=ZoneInfo(tzname)
    text=str(profile.get("datetime") or "").strip()
    if not text:
        date_text=profile.get("date") or datetime.now(tz).strftime("%Y-%m-%d")
        time_text=profile.get("time") or "12:00:00"
        text=f"{date_text}T{time_text}"
    dt=datetime.fromisoformat(text)
    dt=dt.replace(tzinfo=tz) if dt.tzinfo is None else dt.astimezone(tz)
    return dt,tz,tzname

def moon_summary_from_longitude(lon: float) -> dict:
    lon%=360.0
    c=planetary.classify_longitude(lon)
    return {
        "longitude":round(lon,8),
        "rashi_id":c["rashi_id"],"rashi":c["rashi"],"degree_in_rashi":c["degree_in_rashi"],
        "nakshatra_id":c["nakshatra_id"],"nakshatra":c["nakshatra"],"pada":c["pada"],
    }

def moon_summary_from_nakshatra(nak_index: int, pada: int) -> dict:
    if not (0<=nak_index<27 and 1<=pada<=4): raise ValueError("Invalid nakshatra/pada")
    lon=(nak_index*NAK_SPAN + (pada-0.5)*PADA_SPAN)%360.0
    return moon_summary_from_longitude(lon)

def vashya_class(m: dict) -> str:
    s=m["rashi_id"];d=m["degree_in_rashi"]
    if s==8:return "Manava" if d<15 else "Chatushpada"
    if s==9:return "Chatushpada" if d<15 else "Jalachara"
    return {0:"Chatushpada",1:"Chatushpada",2:"Manava",3:"Jalachara",4:"Vanachara",5:"Manava",6:"Manava",7:"Keeta",10:"Manava",11:"Jalachara"}[s]

def tara_leg(a:int,b:int)->tuple[str,float]:
    count=((b-a)%27)+1; rem=count%9 or 9
    return TARA_NAMES[rem-1],0.0 if rem in TARA_BAD else 1.5

def relation(a:str,b:str)->str:
    if a==b:return "friend"
    return NATURAL[a][b]

def cancellation(rule:str,description:str)->dict:
    return {"rule":rule,"description":description}

def score(bride:dict,groom:dict)->dict:
    rows=[]

    bv,br=VARNA[bride["rashi_id"]];gv,gr=VARNA[groom["rashi_id"]]
    rows.append({"name":"Varna","earned":1.0 if gr>=br else 0.0,"maximum":1.0,"basis":f"Groom {gv} × Bride {bv}"})

    bc=vashya_class(bride);gc=vashya_class(groom)
    vp=VASHYA_MATRIX[VASHYA_ORDER.index(gc)][VASHYA_ORDER.index(bc)]
    rows.append({"name":"Vashya","earned":vp,"maximum":2.0,"basis":f"Groom {gc} × Bride {bc}"})

    f1,p1=tara_leg(bride["nakshatra_id"],groom["nakshatra_id"])
    f2,p2=tara_leg(groom["nakshatra_id"],bride["nakshatra_id"])
    rows.append({"name":"Tara","earned":p1+p2,"maximum":3.0,"basis":f"Bride→Groom {f1}; Groom→Bride {f2}"})

    ba=YONI_BY_NAK[bride["nakshatra_id"]];ga=YONI_BY_NAK[groom["nakshatra_id"]]
    yp=float(YONI_MATRIX[YONI_NAMES.index(ga)][YONI_NAMES.index(ba)])
    rows.append({"name":"Yoni","earned":yp,"maximum":4.0,"basis":f"Groom {ga} × Bride {ba}"})

    bl=SIGN_LORDS[bride["rashi_id"]];gl=SIGN_LORDS[groom["rashi_id"]]
    r1=relation(gl,bl);r2=relation(bl,gl);ranks=tuple(sorted((REL_RANK[r1],REL_RANK[r2])))
    mp=MAITRI_POINTS[ranks]
    rows.append({"name":"Graha Maitri","earned":mp,"maximum":5.0,"basis":f"{gl}→{bl} {r1}; {bl}→{gl} {r2}"})

    bg=GANA_BY_NAK[bride["nakshatra_id"]];gg=GANA_BY_NAK[groom["nakshatra_id"]]
    gp=GANA_POINTS[(gg,bg)]
    rows.append({"name":"Gana","earned":gp,"maximum":6.0,"basis":f"Groom {gg} × Bride {bg}"})

    bi=bride["rashi_id"];gi=groom["rashi_id"]
    from_groom=(bi-gi)%12+1;from_bride=(gi-bi)%12+1
    pair=tuple(sorted((from_groom,from_bride)));bh_present=pair in BHAKOOT_DOSHA
    bh_cancel=[]
    if bh_present:
        if bl==gl: bh_cancel.append(cancellation("same-sign-lord",f"Both Moon signs are ruled by {bl}"))
        elif relation(bl,gl)=="friend" and relation(gl,bl)=="friend":
            bh_cancel.append(cancellation("mutual-friendly-lords",f"{bl} and {gl} are mutual natural friends"))
    rows.append({"name":"Bhakoot","earned":0.0 if bh_present else 7.0,"maximum":7.0,"basis":f"Moon signs stand {pair[0]}/{pair[1]}","dosha":bh_present,"cancelled":bh_present and bool(bh_cancel),"cancellations":bh_cancel})

    bn=NADI_BY_NAK[bride["nakshatra_id"]];gn=NADI_BY_NAK[groom["nakshatra_id"]]
    n_present=bn==gn;n_cancel=[]
    if n_present:
        same_star=bride["nakshatra_id"]==groom["nakshatra_id"];same_sign=bi==gi;different_pada=bride["pada"]!=groom["pada"]
        if same_star and different_pada:n_cancel.append(cancellation("same-nakshatra-different-pada","Same Nakshatra, different Padas"))
        if same_sign and not same_star:n_cancel.append(cancellation("same-rashi-different-nakshatra","Same Moon sign, different Nakshatras"))
        if same_star and not same_sign:n_cancel.append(cancellation("same-nakshatra-different-rashi","Same Nakshatra, different Moon signs"))
    rows.append({"name":"Nadi","earned":0.0 if n_present else 8.0,"maximum":8.0,"basis":f"Groom {gn} × Bride {bn}","dosha":n_present,"cancelled":n_present and bool(n_cancel),"cancellations":n_cancel})

    total=round(sum(r["earned"] for r in rows),2)
    bh_unfavorable=bh_present and not bool(bh_cancel)
    n_unfavorable=n_present and not bool(n_cancel)
    if n_unfavorable:
        band="inauspicious"
        reason="Nadi Kuta is unfavorable; reference convention gives it overriding priority."
    elif bh_unfavorable:
        if total>=26: band="very-good"
        elif total>=21: band="middling"
        else: band="inauspicious"
        reason="Bhakoot is unfavorable, so the stricter reference band is applied."
    else:
        if total>=31: band="excellent"
        elif total>=21: band="very-good"
        elif total>=17: band="middling"
        else: band="inauspicious"
        reason="Reference Ashtakoota score band with favorable/cancelled Bhakoot and Nadi."
    return {
        "kootas":rows,"total":total,"maximum":36.0,"band":band,"band_reason":reason,
        "bhakoot":{"present":bh_present,"cancelled":bh_present and bool(bh_cancel),"cancellations":bh_cancel},
        "nadi":{"present":n_present,"cancelled":n_present and bool(n_cancel),"cancellations":n_cancel},
    }

def current_dasha_payload(birth:datetime,as_of:datetime)->dict:
    d=vimshottari.calculate(birth,as_of)
    cur=d.get("current") or {}
    ad=cur.get("antardasha") or {}
    pd=ad.get("current_pratyantardasha") or {}
    return {
        "nakshatra":d["nakshatra"],"starting_lord":d["starting_lord"],
        "mahadasha":(cur.get("mahadasha") or {}).get("lord"),
        "antardasha":ad.get("lord"),"pratyantardasha":pd.get("lord")
    }

def profile_summary(profile:dict,as_of:datetime)->dict:
    birth,tz,tzname=parse_birth(profile)
    lat=float(profile.get("lat",19.076));lon=float(profile.get("lon",72.8777))
    city=str(profile.get("city") or "Current location")[:120]
    moon=planetary.planet_state("Moon",birth)
    asc=lagna.lagna_state(birth,lat,lon)
    mangal=doshas.mangal(birth,lat,lon,"mean")
    placements=[]
    for name in ["Sun","Moon","Mars","Mercury","Jupiter","Venus","Saturn","Rahu","Ketu"]:
        st=planetary.planet_state(name,birth)
        placements.append({
            "name":name,"rashi":st["rashi"],"rashi_id":st["rashi_id"],
            "degree_in_rashi":st["degree_in_rashi"],
            "house":((st["rashi_id"]-asc["lagna_id"])%12)+1,
            "retrograde":st["retrograde"]
        })
    return {
        "birth_datetime":birth.isoformat(),"location":{"city":city,"lat":lat,"lon":lon,"timezone":tzname},
        "moon":{k:moon[k] for k in ["longitude","rashi_id","rashi","degree_in_rashi","nakshatra_id","nakshatra","pada"]},
        "lagna":{"rashi":asc["lagna"],"rashi_id":asc["lagna_id"],"degree_in_rashi":asc["degree_in_sign"]},
        "placements":placements,"mangal":mangal,"dasha":current_dasha_payload(birth,as_of)
    }

def nak_profile(p:dict)->dict:
    if "nakshatra_id" in p:n=int(p["nakshatra_id"])
    else:
        name=str(p.get("nakshatra") or "")
        if name not in panchang.NAKSHATRA_NAMES:raise ValueError("Unknown Nakshatra")
        n=panchang.NAKSHATRA_NAMES.index(name)
    return moon_summary_from_nakshatra(n,int(p.get("pada") or 1))

def main():
    payload=json.loads(sys.stdin.read() or "{}")
    mode=str(payload.get("mode") or "horoscope").lower()
    if mode not in ("horoscope","nakshatra"):raise ValueError("Unsupported matching mode")
    if mode=="nakshatra":
        bride=nak_profile(payload.get("bride") or {});groom=nak_profile(payload.get("groom") or {})
        result=score(bride,groom)
        output={"ok":True,"mode":mode,"bride":{"moon":bride},"groom":{"moon":groom},"match":result}
    else:
        as_of_text=str(payload.get("as_of") or "").strip()
        if as_of_text:
            as_of=datetime.fromisoformat(as_of_text)
            if as_of.tzinfo is None:as_of=as_of.replace(tzinfo=ZoneInfo("Asia/Kolkata"))
        else:
            as_of=datetime.now(ZoneInfo("Asia/Kolkata"))
        bride=profile_summary(payload.get("bride") or {},as_of)
        groom=profile_summary(payload.get("groom") or {},as_of)
        result=score(bride["moon"],groom["moon"])
        mangal_compatible=bride["mangal"]["present"]==groom["mangal"]["present"]
        deep = marriage_analysis.analyze_profiles(
            payload.get("groom") or {},
            payload.get("bride") or {},
            as_of,
            int(payload.get("horizon_years") or 12),
        )
        output={
            "ok":True,"mode":mode,"bride":bride,"groom":groom,"match":result,
            "integration":{
                "mangal_compatible":mangal_compatible,
                "mangal_note":"Both charts have the same base Manglik status." if mangal_compatible else "One chart is Manglik and the other is not under the base rule profile.",
                "dasha_as_of":as_of.isoformat(),
                "deep_analysis": deep
            }
        }
    output["engine"]={"name":"tithika-ashtakoota","version":ENGINE_VERSION,"ayanamsha":"Lahiri / Chitrapaksha","maximum_gunas":36,"mangal_in_score":False}
    output["note"]="Ashtakoota is a traditional Moon-based compatibility framework, not a deterministic prediction of relationship success. Mangal, Lagna and Dasha are shown separately from the 36-point total."
    print(json.dumps(output,ensure_ascii=False))

if __name__=="__main__":
    try:main()
    except Exception as exc:
        print(json.dumps({"ok":False,"error":str(exc),"code":"MATCHING_CALCULATION_FAILED"}))
        sys.exit(1)
