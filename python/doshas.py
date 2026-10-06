#!/usr/bin/env python3
from __future__ import annotations
import json, sys
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
import lagna, planetary

MANGAL_HOUSES={1,2,4,7,8,12}
KALA_TYPES=["Anant","Kulik","Vasuki","Shankhapal","Padma","Maha Padma","Takshak","Karkotak","Shankhachoodh","Ghatak","Vishdhara","Sheshnag"]
CLASSICAL=["Sun","Moon","Mars","Mercury","Jupiter","Venus","Saturn"]

def parse_birth(p,tz):
    s=str(p.get("datetime") or "").strip()
    if not s:s=f"{p.get('date') or datetime.now(tz).strftime('%Y-%m-%d')}T{p.get('time') or '12:00:00'}"
    dt=datetime.fromisoformat(s)
    return dt.replace(tzinfo=tz) if dt.tzinfo is None else dt.astimezone(tz)

def house_of(sign,ref):
    return ((sign-ref)%12)+1

def mangal(birth,lat,lon,node_model):
    asc=lagna.lagna_state(birth,lat,lon)
    states={n:planetary.planet_state(n,birth,node_model) for n in ["Moon","Venus","Mars","Sun","Saturn","Rahu","Ketu"]}
    refs={"Lagna":asc["lagna_id"],"Moon":states["Moon"]["rashi_id"],"Venus":states["Venus"]["rashi_id"]}
    checks=[]
    for ref,sign in refs.items():
        h=house_of(states["Mars"]["rashi_id"],sign)
        checks.append({"reference":ref,"mars_house":h,"afflicted":h in MANGAL_HOUSES})
    afflicted=[x for x in checks if x["afflicted"]]
    return {"present":bool(afflicted),"checks":checks,"afflicted_references":[x["reference"] for x in afflicted],"rule_houses":sorted(MANGAL_HOUSES),"cancellation_status":"not-applied","note":"Base Mangal Dosha is evaluated from Lagna, Moon and Venus. Cancellation combinations are deliberately reported separately and are not guessed in this stage."}

def in_arc(x,start,end):
    span=(end-start)%360.0
    pos=(x-start)%360.0
    return 0.0 <= pos <= span+1e-9

def kalasarpa(birth,lat,lon,node_model):
    states={n:planetary.planet_state(n,birth,node_model) for n in CLASSICAL+["Rahu","Ketu"]}
    rahu=states["Rahu"]["longitude"]; ketu=states["Ketu"]["longitude"]
    arc_rk=[n for n in CLASSICAL if in_arc(states[n]["longitude"],rahu,ketu)]
    arc_kr=[n for n in CLASSICAL if in_arc(states[n]["longitude"],ketu,rahu)]
    full_rk=len(arc_rk)==len(CLASSICAL); full_kr=len(arc_kr)==len(CLASSICAL)
    asc=lagna.lagna_state(birth,lat,lon)
    rh=house_of(states["Rahu"]["rashi_id"],asc["lagna_id"])
    present=full_rk or full_kr
    return {"present":present,"type":(KALA_TYPES[rh-1]+" Kalasarpa Yoga") if present else None,"rahu_house":rh,"direction":"Rahu-to-Ketu" if full_rk else "Ketu-to-Rahu" if full_kr else None,"planets_between":arc_rk if full_rk else arc_kr if full_kr else [],"partial_considered":False,"node_model":node_model}

def saturn_sign(moment):
    return planetary.planet_state("Saturn",moment)["rashi_id"]

def refine_transition(left,right,old):
    lo,hi=left,right
    for _ in range(42):
        mid=lo+(hi-lo)/2
        if saturn_sign(mid)==old: lo=mid
        else: hi=mid
    return hi

def sade_sati(birth,tz,years=100,as_of=None):
    moon=planetary.planet_state("Moon",birth)
    moon_sign=moon["rashi_id"]
    target={(moon_sign-1)%12:"rising",moon_sign:"peak",(moon_sign+1)%12:"setting"}
    start=birth-timedelta(days=365.25*5)
    end=birth+timedelta(days=365.25*years)
    step=timedelta(days=3)
    cursor=start; sign=saturn_sign(cursor); seg_start=cursor; rows=[]; probe=cursor+step
    while probe<=end:
        s=saturn_sign(probe)
        if s!=sign:
            b=refine_transition(probe-step,probe,sign)
            if sign in target:
                rows.append({"phase":target[sign],"rashi_id":sign,"rashi":planetary.classify_longitude(sign*30+0.1)["rashi"],"start":max(seg_start,birth).isoformat(),"end":b.isoformat()})
            seg_start=b; sign=saturn_sign(b+timedelta(seconds=2))
        probe+=step
    if sign in target and seg_start<end:
        rows.append({"phase":target[sign],"rashi_id":sign,"rashi":planetary.classify_longitude(sign*30+0.1)["rashi"],"start":max(seg_start,birth).isoformat(),"end":end.isoformat()})
    rows=[r for r in rows if datetime.fromisoformat(r["end"])>birth]
    current=None
    if as_of:
        for r in rows:
            if datetime.fromisoformat(r["start"])<=as_of<datetime.fromisoformat(r["end"]):
                current=r;break
    return {"moon_rashi":moon["rashi"],"moon_rashi_id":moon_sign,"target_rashis":[(moon_sign-1)%12,moon_sign,(moon_sign+1)%12],"periods":rows,"current":current,"timeline_years":years}

def main():
    p=json.loads(sys.stdin.read() or "{}")
    mode=str(p.get("mode") or "mangal").lower()
    if mode not in ("mangal","kalasarpa","sade-sati"):raise ValueError("Unsupported dosha mode")
    lat=float(p.get("lat",19.076));lon=float(p.get("lon",72.8777))
    tzname=p.get("timezone") or "Asia/Kolkata"
    try:tz=ZoneInfo(tzname)
    except ZoneInfoNotFoundError:tzname="Asia/Kolkata";tz=ZoneInfo(tzname)
    birth=parse_birth(p,tz)
    node_model=str(p.get("node_model") or "mean").lower()
    if node_model not in ("mean","true"):raise ValueError("node_model must be mean or true")
    if mode=="mangal":result=mangal(birth,lat,lon,node_model)
    elif mode=="kalasarpa":result=kalasarpa(birth,lat,lon,node_model)
    else:
        a=str(p.get("as_of") or "").strip()
        as_of=datetime.fromisoformat(a) if a else datetime.now(tz)
        if as_of.tzinfo is None:as_of=as_of.replace(tzinfo=tz)
        result=sade_sati(birth,tz,int(p.get("timeline_years") or 100),as_of)
    print(json.dumps({"ok":True,"mode":mode,"birth_datetime":birth.isoformat(),"engine":{"name":"tithika-doshas","version":"0.1.0","ayanamsha":"Lahiri / Chitrapaksha","node_model":node_model},"result":result},ensure_ascii=False))
if __name__=="__main__":
    try:main()
    except Exception as e:
        print(json.dumps({"ok":False,"error":str(e),"code":"DOSHA_CALCULATION_FAILED"}));sys.exit(1)
