#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date, datetime, timedelta
from typing import Any

from intelligence.core import EngineRegistry, FileTTLCache, public_context


def parse_date(value: Any) -> date:
    text=str(value or "").strip()
    return datetime.strptime(text,"%Y-%m-%d").date() if text else date.today()


def iso_date(value: Any) -> date | None:
    if not value:
        return None
    text=str(value)
    try:
        return datetime.fromisoformat(text).date()
    except ValueError:
        try:
            return datetime.strptime(text[:10],"%Y-%m-%d").date()
        except ValueError:
            return None


def event_date(row: dict[str, Any], tradition: str="smarta") -> date | None:
    obs=row.get("observance") if isinstance(row.get("observance"),dict) else {}
    profile=obs.get(tradition) if isinstance(obs.get(tradition),dict) else {}
    return iso_date(profile.get("date") or row.get("date") or row.get("datetime") or row.get("start"))


def normalize_event(kind: str,row: dict[str,Any],tradition: str) -> dict[str,Any] | None:
    d=event_date(row,tradition)
    if not d:
        return None
    if kind=="ekadashi":
        obs=row.get("observance") if isinstance(row.get("observance"),dict) else {}
        profile=obs.get(tradition) if isinstance(obs.get(tradition),dict) else {}
        return {
            "type":"vrat","kind":"ekadashi","date":d.isoformat(),
            "title":"Ekadashi","subtitle":str(profile.get("basis") or row.get("paksha") or "Fasting observance"),
            "datetime":row.get("start"),"route":"vrat/ekadashi",
        }
    if kind in {"pradosh","sankashti"}:
        return {
            "type":"vrat","kind":kind,"date":d.isoformat(),
            "title":str(row.get("name") or ("Pradosh Vrat" if kind=="pradosh" else "Sankashti Chaturthi")),
            "subtitle":str(row.get("paksha") or "Rule-selected observance"),
            "datetime":(row.get("puja") or {}).get("start") if isinstance(row.get("puja"),dict) else row.get("moonrise"),
            "route":"vrat/pradosham" if kind=="pradosh" else "vrat/sankashti-chaturthi",
        }
    if kind=="sankranti":
        return {
            "type":"solar","kind":"sankranti","date":d.isoformat(),
            "title":f"{row.get('rashi','')} Sankranti".strip(),
            "subtitle":"Nirayana solar ingress","datetime":row.get("datetime"),
            "route":"panchang/sankranti",
        }
    if kind in {"transit","retrograde"}:
        planet=str(row.get("planet") or "Planet")
        if kind=="transit":
            title=f"{planet} enters {row.get('to_rashi') or row.get('rashi') or 'new Rashi'}"
            subtitle=f"{row.get('from_rashi','')} → {row.get('to_rashi','')}".strip(" →")
            route="planets/transit"
        else:
            action="turns retrograde" if row.get("event")=="retrograde" else "turns direct"
            title=f"{planet} {action}"
            subtitle=str(row.get("rashi") or "Planetary station")
            route="planets/retrograde"
        return {
            "type":"planet","kind":kind,"date":d.isoformat(),
            "title":title,"subtitle":subtitle,"datetime":row.get("datetime"),"route":route,
        }
    return None


def run_engine(registry: EngineRegistry,name: str,payload: dict[str,Any]) -> tuple[str,dict[str,Any]]:
    return name,registry.run(name,payload)


def build(payload: dict[str,Any]) -> dict[str,Any]:
    selected=parse_date(payload.get("date"))
    horizon=max(7,min(int(payload.get("horizon_days") or 21),45))
    end=selected+timedelta(days=horizon)
    tradition=str(payload.get("tradition") or "smarta").lower()
    if tradition not in {"smarta","vaishnava","iskcon"}:
        tradition="smarta"

    base={
        "lat":float(payload.get("lat",19.0760)),
        "lon":float(payload.get("lon",72.8777)),
        "city":str(payload.get("city") or "Current location")[:120],
        "timezone":str(payload.get("timezone") or "Asia/Kolkata"),
        "date":selected.isoformat(),
        "hour24":bool(payload.get("hour24",False)),
    }
    if not (-90<=base["lat"]<=90 and -180<=base["lon"]<=180):
        raise ValueError("Invalid latitude/longitude")

    cache=FileTTLCache(namespace="tithika-home-dashboard",ttl_seconds=600)
    key=cache.key("dashboard",{**public_context(base),"tradition":tradition,"horizon":horizon})
    hit=cache.get(key)
    if hit:
        hit["cache"]="hit"
        return hit

    registry=EngineRegistry(timeout_seconds=55)
    jobs=[
        ("panchang",{**base}),
        ("choghadiya",{**base}),
        ("lunar-occurrences",{**base,"kind":"ekadashi"}),
        ("observances-pradosh",{**base,"kind":"pradosh"}),
        ("observances-sankashti",{**base,"kind":"sankashti"}),
        ("sankranti",{**base}),
        ("planetary-transit",{**base,"mode":"transit"}),
        ("planetary-retrograde",{**base,"mode":"retrograde"}),
    ]
    engine_name={
        "observances-pradosh":"observances",
        "observances-sankashti":"observances",
        "planetary-transit":"planetary",
        "planetary-retrograde":"planetary",
    }
    results: dict[str,dict[str,Any]]={}
    with ThreadPoolExecutor(max_workers=6) as pool:
        futures={
            pool.submit(registry.run,engine_name.get(key_name,key_name),job_payload):key_name
            for key_name,job_payload in jobs
        }
        for future in as_completed(futures):
            key_name=futures[future]
            results[key_name]=future.result()

    pan=results["panchang"]
    chog=results["choghadiya"]
    st=pan.get("current_state") or pan.get("sunrise_state") or {}
    sunrise_st=pan.get("sunrise_state") or {}
    month=pan.get("lunar_month") or {}

    rows=[]
    for row in results["lunar-occurrences"].get("events") or []:
        item=normalize_event("ekadashi",row,tradition)
        if item: rows.append(item)
    for key_name,kind in (("observances-pradosh","pradosh"),("observances-sankashti","sankashti")):
        for row in results[key_name].get("events") or []:
            item=normalize_event(kind,row,tradition)
            if item: rows.append(item)
    for row in results["sankranti"].get("events") or []:
        item=normalize_event("sankranti",row,tradition)
        if item: rows.append(item)
    for key_name,kind in (("planetary-transit","transit"),("planetary-retrograde","retrograde")):
        for row in results[key_name].get("events") or []:
            item=normalize_event(kind,row,tradition)
            if item: rows.append(item)

    rows=[
        row for row in rows
        if (d:=iso_date(row.get("date"))) and selected<=d<=end
    ]
    rows.sort(key=lambda row:(row["date"],str(row.get("datetime") or ""),row["title"]))
    dedup=[]
    seen=set()
    for row in rows:
        sig=(row["kind"],row["date"],row["title"])
        if sig in seen: continue
        seen.add(sig);dedup.append(row)

    output={
        "ok":True,
        "cache":"miss",
        "date":selected.isoformat(),
        "horizon_days":horizon,
        "location":pan.get("location") or base,
        "preferences":{"tradition":tradition},
        "today":{
            "weekday":pan.get("weekday"),
            "date_label":pan.get("date_label"),
            "tithi":st.get("tithi"),
            "paksha":st.get("paksha"),
            "nakshatra":st.get("nakshatra"),
            "yoga":st.get("yoga"),
            "karana":st.get("karana"),
            "moon_rashi":pan.get("moon_rashi"),
            "sun_rashi":pan.get("sun_rashi"),
            "amanta_month":month.get("amanta"),
            "purnimanta_month":month.get("purnimanta"),
            "sunrise":pan.get("sunrise_label"),
            "sunset":pan.get("sunset_label"),
            "moonrise":pan.get("moonrise_label"),
            "abhijit":(pan.get("muhurtas") or {}).get("abhijit"),
            "rahu_kaal":(pan.get("muhurtas") or {}).get("rahu_kaal"),
            "sunrise_state":{
                "tithi":sunrise_st.get("tithi"),"nakshatra":sunrise_st.get("nakshatra"),
                "yoga":sunrise_st.get("yoga"),"karana":sunrise_st.get("karana"),
            },
        },
        "choghadiya":{
            "active":chog.get("active"),
            "next_auspicious":chog.get("next_auspicious"),
            "sunrise":chog.get("sunrise_label"),
            "sunset":chog.get("sunset_label"),
        },
        "upcoming":dedup[:10],
        "engine":{
            "name":"tithika-home-dashboard",
            "version":"1.0.0",
            "sources":[
                "tithika-panchang","tithika-choghadiya","tithika-lunar-occurrences",
                "tithika-observances","tithika-sankranti","tithika-planetary"
            ],
        },
    }
    cache.set(key,output)
    return output


def main():
    payload=json.loads(sys.stdin.read() or "{}")
    if not isinstance(payload,dict):
        raise ValueError("Payload must be an object")
    print(json.dumps(build(payload),ensure_ascii=False))


if __name__=="__main__":
    try:
        main()
    except Exception as exc:
        print(json.dumps({"ok":False,"error":str(exc),"code":"HOME_DASHBOARD_FAILED"},ensure_ascii=False))
        sys.exit(1)
