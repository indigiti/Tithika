#!/usr/bin/env python3
from __future__ import annotations
import json, sys
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
import planetary

SEQ=["Ketu","Venus","Sun","Moon","Mars","Rahu","Jupiter","Saturn","Mercury"]
YEARS={"Ketu":7,"Venus":20,"Sun":6,"Moon":10,"Mars":7,"Rahu":18,"Jupiter":16,"Saturn":19,"Mercury":17}
YEAR_DAYS=365.25
NAK_SPAN=360.0/27.0

def parse_birth(p,tz):
    s=str(p.get("datetime") or "").strip()
    if not s:
        s=f"{p.get('date') or datetime.now(tz).strftime('%Y-%m-%d')}T{p.get('time') or '12:00:00'}"
    dt=datetime.fromisoformat(s)
    return dt.replace(tzinfo=tz) if dt.tzinfo is None else dt.astimezone(tz)

def order_from(lord):
    i=SEQ.index(lord)
    return SEQ[i:]+SEQ[:i]

def period_payload(lord,start,end,clip_start=None,clip_end=None):
    a=max(start,clip_start) if clip_start else start
    b=min(end,clip_end) if clip_end else end
    return {"lord":lord,"start":a.isoformat(),"end":b.isoformat(),"full_start":start.isoformat(),"full_end":end.isoformat(),"duration_days":round((b-a).total_seconds()/86400,6)}

def child_periods(parent_lord,start,end,clip_start=None,clip_end=None):
    total=(end-start).total_seconds()
    rows=[]; cur=start
    for lord in order_from(parent_lord):
        dur=total*(YEARS[lord]/120.0)
        nxt=cur+timedelta(seconds=dur)
        if (clip_end is None or cur<clip_end) and (clip_start is None or nxt>clip_start):
            rows.append(period_payload(lord,cur,nxt,clip_start,clip_end))
        cur=nxt
    return rows

def calculate(birth,as_of):
    moon=planetary.planet_state("Moon",birth)
    lon=moon["longitude"]
    nak_id=int(lon//NAK_SPAN)%27
    lord=SEQ[nak_id%9]
    offset=lon-nak_id*NAK_SPAN
    elapsed_fraction=offset/NAK_SPAN
    full_days=YEARS[lord]*YEAR_DAYS
    elapsed_days=full_days*elapsed_fraction
    first_full_start=birth-timedelta(days=elapsed_days)
    first_full_end=first_full_start+timedelta(days=full_days)

    md=[]
    cur_start=first_full_start
    current_lord=lord
    # cover birth through at least 120 years.
    while cur_start < birth+timedelta(days=122*YEAR_DAYS):
        cur_end=cur_start+timedelta(days=YEARS[current_lord]*YEAR_DAYS)
        if cur_end>birth:
            row=period_payload(current_lord,cur_start,cur_end,birth,None)
            row["antardasha"]=child_periods(current_lord,cur_start,cur_end,birth,None)
            md.append(row)
        cur_start=cur_end
        current_lord=SEQ[(SEQ.index(current_lord)+1)%9]

    current=None
    for m in md:
        fs=datetime.fromisoformat(m["full_start"]); fe=datetime.fromisoformat(m["full_end"])
        if fs<=as_of<fe:
            ad=None
            for a in m["antardasha"]:
                afs=datetime.fromisoformat(a["full_start"]); afe=datetime.fromisoformat(a["full_end"])
                if afs<=as_of<afe:
                    pd=child_periods(a["lord"],afs,afe,None,None)
                    current_pd=next((x for x in pd if datetime.fromisoformat(x["full_start"])<=as_of<datetime.fromisoformat(x["full_end"])),None)
                    ad={**a,"pratyantardasha":pd,"current_pratyantardasha":current_pd}
                    break
            current={"mahadasha":m,"antardasha":ad}
            break

    return {
        "moon":moon,
        "nakshatra_id":nak_id,
        "nakshatra":moon["nakshatra"],
        "nakshatra_pada":moon["pada"],
        "starting_lord":lord,
        "nakshatra_elapsed_fraction":round(elapsed_fraction,10),
        "birth_balance_years":round(YEARS[lord]*(1-elapsed_fraction),10),
        "year_convention_days":YEAR_DAYS,
        "mahadasha":md,
        "current":current
    }

def main():
    p=json.loads(sys.stdin.read() or "{}")
    tzname=p.get("timezone") or "Asia/Kolkata"
    try: tz=ZoneInfo(tzname)
    except ZoneInfoNotFoundError: tzname="Asia/Kolkata"; tz=ZoneInfo(tzname)
    birth=parse_birth(p,tz)
    a=str(p.get("as_of") or "").strip()
    as_of=datetime.fromisoformat(a) if a else datetime.now(tz)
    if as_of.tzinfo is None: as_of=as_of.replace(tzinfo=tz)
    else: as_of=as_of.astimezone(tz)
    r=calculate(birth,as_of)
    print(json.dumps({"ok":True,"birth_datetime":birth.isoformat(),"as_of":as_of.isoformat(),"engine":{"name":"tithika-vimshottari","version":"0.1.0","ayanamsha":"Lahiri / Chitrapaksha","cycle_years":120,"year_days":YEAR_DAYS},"result":r,"note":"Starting Mahadasha is the lord of the Moon's birth Nakshatra. Birth balance uses the untraversed Nakshatra fraction; sub-periods are proportional to the 120-year sequence."},ensure_ascii=False))
if __name__=="__main__":
    try: main()
    except Exception as e:
        print(json.dumps({"ok":False,"error":str(e),"code":"DASHA_CALCULATION_FAILED"}));sys.exit(1)
