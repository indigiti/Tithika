#!/usr/bin/env python3
"""
Tithika BPHS Shodashavarga engine.

Implements the classical sixteen divisional charts:
D1, D2, D3, D4, D7, D9, D10, D12, D16, D20, D24, D27, D30, D40, D45, D60.

Rule profile follows the Parashara construction:
- D2 Parashara Hora: Leo/Cancer only.
- D10: odd signs count from themselves, even signs from the 9th.
- D30: unequal 5/5/8/7/5 divisions, reversed for even signs.
"""
from __future__ import annotations

import json, math, sys
from datetime import datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import lagna
import panchang
import planetary

ENGINE_VERSION="0.1.0"
SHODASHAVARGA=[1,2,3,4,7,9,10,12,16,20,24,27,30,40,45,60]
NAMES={
 1:"Rashi",2:"Hora",3:"Drekkana",4:"Chaturthamsha",7:"Saptamsha",
 9:"Navamsha",10:"Dashamsha",12:"Dvadashamsha",16:"Shodashamsha",
 20:"Vimshamsha",24:"Siddhamsha",27:"Bhamsha",30:"Trimshamsha",
 40:"Khavedamsha",45:"Akshavedamsha",60:"Shashtyamsha"
}
THEMES={
 1:"Overall life and body",2:"Wealth and resources",3:"Siblings and courage",
 4:"Fortune and property",7:"Children and lineage",9:"Dharma and marriage",
 10:"Career and public work",12:"Parents and ancestry",16:"Vehicles and comforts",
 20:"Spiritual practice",24:"Education and learning",27:"Strengths and weaknesses",
 30:"Misfortune and vulnerabilities",40:"Maternal lineage and auspiciousness",
 45:"Paternal lineage and character",60:"Fine karmic pattern / all matters"
}
MOVABLE={0,3,6,9}; FIXED={1,4,7,10}; DUAL={2,5,8,11}

def parse_birth(p,tz):
    s=str(p.get("datetime") or "").strip()
    if not s:
        s=f"{p.get('date') or datetime.now(tz).strftime('%Y-%m-%d')}T{p.get('time') or '12:00:00'}"
    d=datetime.fromisoformat(s)
    return d.replace(tzinfo=tz) if d.tzinfo is None else d.astimezone(tz)

def is_odd_sign(sign_id:int)->bool:
    # Classical 1-based odd signs are 0-based even indexes.
    return sign_id % 2 == 0

def quality(sign_id:int)->int:
    # movable=0, fixed=1, dual=2
    return sign_id % 3

def equal_part(deg:float,n:int)->int:
    return min(n-1,int((deg*n)/30.0))

def trimshamsha(sign_id:int,deg:float):
    odd=is_odd_sign(sign_id)
    if odd:
        bounds=[5,10,18,25,30]
        signs=[0,10,8,2,6]      # Mars,Saturn,Jupiter,Mercury,Venus odd signs
        starts=[0,5,10,18,25]
    else:
        bounds=[5,12,20,25,30]
        signs=[1,5,11,9,7]      # Venus,Mercury,Jupiter,Saturn,Mars even signs
        starts=[0,5,12,20,25]
    idx=next(i for i,b in enumerate(bounds) if deg < b or math.isclose(deg,b) and b==30)
    width=bounds[idx]-starts[idx]
    frac=max(0.0,min(0.999999999,(deg-starts[idx])/width))
    return signs[idx],idx,frac*30.0,min(deg-starts[idx],bounds[idx]-deg)

def varga_position(longitude:float,n:int)->dict:
    if n not in SHODASHAVARGA:
        raise ValueError(f"Unsupported Varga D{n}")
    lon=longitude%360.0
    sign=int(lon//30.0)%12
    deg=lon-sign*30.0

    if n==1:
        target=sign; part=0; mapped_deg=deg; margin=min(deg,30-deg)
    elif n==2:
        part=equal_part(deg,2)
        target=(4 if part==0 else 3) if is_odd_sign(sign) else (3 if part==0 else 4)
        mapped_deg=(deg%(15.0))*2.0
        margin=min(deg%15.0,15.0-(deg%15.0))
    elif n==3:
        part=equal_part(deg,3);target=(sign+4*part)%12
        mapped_deg=(deg%(10.0))*3.0;margin=min(deg%10.0,10.0-(deg%10.0))
    elif n==4:
        part=equal_part(deg,4);target=(sign+3*part)%12
        width=7.5;mapped_deg=(deg%width)*4.0;margin=min(deg%width,width-(deg%width))
    elif n==7:
        part=equal_part(deg,7);target=((sign if is_odd_sign(sign) else sign+6)+part)%12
        width=30/7;mapped_deg=(deg%width)*7;margin=min(deg%width,width-(deg%width))
    elif n==9:
        part=equal_part(deg,9);target=int(lon/(30/9))%12
        width=30/9;mapped_deg=(deg%width)*9;margin=min(deg%width,width-(deg%width))
    elif n==10:
        part=equal_part(deg,10);target=((sign if is_odd_sign(sign) else sign+8)+part)%12
        width=3;mapped_deg=(deg%width)*10;margin=min(deg%width,width-(deg%width))
    elif n==12:
        part=equal_part(deg,12);target=(sign+part)%12
        width=2.5;mapped_deg=(deg%width)*12;margin=min(deg%width,width-(deg%width))
    elif n==16:
        part=equal_part(deg,16);target=([0,4,8][quality(sign)]+part)%12
        width=30/16;mapped_deg=(deg%width)*16;margin=min(deg%width,width-(deg%width))
    elif n==20:
        part=equal_part(deg,20);target=([0,8,4][quality(sign)]+part)%12
        width=1.5;mapped_deg=(deg%width)*20;margin=min(deg%width,width-(deg%width))
    elif n==24:
        part=equal_part(deg,24);target=((4 if is_odd_sign(sign) else 3)+part)%12
        width=1.25;mapped_deg=(deg%width)*24;margin=min(deg%width,width-(deg%width))
    elif n==27:
        part=equal_part(deg,27);target=int(lon/(30/27))%12
        width=30/27;mapped_deg=(deg%width)*27;margin=min(deg%width,width-(deg%width))
    elif n==30:
        target,part,mapped_deg,margin=trimshamsha(sign,deg)
    elif n==40:
        part=equal_part(deg,40);target=((0 if is_odd_sign(sign) else 6)+part)%12
        width=.75;mapped_deg=(deg%width)*40;margin=min(deg%width,width-(deg%width))
    elif n==45:
        part=equal_part(deg,45);target=([0,4,8][quality(sign)]+part)%12
        width=30/45;mapped_deg=(deg%width)*45;margin=min(deg%width,width-(deg%width))
    else: # D60
        part=equal_part(deg,60);target=(sign+part)%12
        width=.5;mapped_deg=(deg%width)*60;margin=min(deg%width,width-(deg%width))

    return {
        "division":n,"name":NAMES[n],"part":part+1,
        "rashi_id":target,"rashi":panchang.RASHI_NAMES[target],
        "degree_in_rashi":round(mapped_deg,8),
        "source_rashi_id":sign,"source_rashi":panchang.RASHI_NAMES[sign],
        "source_degree":round(deg,8),
        "boundary_margin_deg":round(max(0.0,margin),8),
    }

def chart_for(n:int,asc_lon:float,states:list[dict])->dict:
    asc=varga_position(asc_lon,n)
    placements=[]
    for st in states:
        v=varga_position(st["longitude"],n)
        placements.append({
            **v,
            "varga_name":v["name"],
            "name":st["name"],
            "house":((v["rashi_id"]-asc["rashi_id"])%12)+1,
            "retrograde":st.get("retrograde",False),
            "vargottama":v["rashi_id"]==st["rashi_id"],
        })
    cells=[]
    for sign_id,rashi in enumerate(panchang.RASHI_NAMES):
        cells.append({
            "rashi_id":sign_id,"rashi":rashi,
            "house":((sign_id-asc["rashi_id"])%12)+1,
            "planets":[x for x in placements if x["rashi_id"]==sign_id],
        })
    return {
        "division":n,"key":f"D{n}","name":NAMES[n],"theme":THEMES[n],
        "lagna":{**asc,"house":1},
        "placements":placements,"cells":cells,
        "minimum_boundary_margin_deg":round(min([asc["boundary_margin_deg"]]+[x["boundary_margin_deg"] for x in placements]),8),
    }

def build(payload:dict)->dict:
    lat=float(payload.get("lat",19.076));lon=float(payload.get("lon",72.8777))
    tzname=payload.get("timezone") or "Asia/Kolkata"
    try:tz=ZoneInfo(tzname)
    except ZoneInfoNotFoundError:tzname="Asia/Kolkata";tz=ZoneInfo(tzname)
    birth=parse_birth(payload,tz)
    asc=lagna.lagna_state(birth,lat,lon)
    node_model=str(payload.get("node_model") or "mean").lower()
    states=planetary.positions(birth,False,node_model)
    requested=payload.get("division")
    divisions=[int(requested)] if requested else SHODASHAVARGA
    charts={f"D{n}":chart_for(n,asc["sidereal_longitude"],states) for n in divisions}
    return {
        "ok":True,"birth_datetime":birth.isoformat(),
        "location":{"city":str(payload.get("city") or "Current location")[:120],"lat":lat,"lon":lon,"timezone":tzname},
        "engine":{
            "name":"tithika-shodashavarga","version":ENGINE_VERSION,
            "ayanamsha":"Lahiri / Chitrapaksha",
            "profile":"BPHS Shodashavarga / Parashara D2 and D10",
        },
        "available":[{"division":n,"key":f"D{n}","name":NAMES[n],"theme":THEMES[n]} for n in SHODASHAVARGA],
        "charts":charts,
        "note":"Higher Vargas are highly birth-time and longitude sensitive. Boundary margin is exposed so near-cusp placements can be treated cautiously."
    }

def main():
    p=json.loads(sys.stdin.read() or "{}")
    print(json.dumps(build(p),ensure_ascii=False))

if __name__=="__main__":
    try:main()
    except Exception as e:
        print(json.dumps({"ok":False,"error":str(e),"code":"VARGA_CALCULATION_FAILED"}));sys.exit(1)