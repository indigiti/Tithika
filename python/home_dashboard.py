#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import festival_calendar_completion
from intelligence.advisor import advise
from intelligence.core import EngineRegistry, FileTTLCache


def _selected(payload):
    tzname=str(payload.get("timezone") or "Asia/Kolkata")
    try:
        tz=ZoneInfo(tzname)
    except ZoneInfoNotFoundError:
        tzname="Asia/Kolkata";tz=ZoneInfo(tzname)
    raw=str(payload.get("date") or "").strip()
    selected=datetime.strptime(raw,"%Y-%m-%d").date() if raw else datetime.now(tz).date()
    return selected,tz,tzname


def _upcoming_calendar(selected,lat,lon,tz,days=35,limit=8):
    rows=[]
    years={selected.year,(selected+timedelta(days=days)).year}
    for year in sorted(years):
        rows.extend(festival_calendar_completion.yearly_events(year,lat,lon,tz))
    end=selected+timedelta(days=days)
    out=[]
    seen=set()
    for row in sorted(rows,key=lambda x:(x.get("date",""),x.get("title",""))):
        try:d=date.fromisoformat(str(row.get("date")))
        except (TypeError,ValueError):continue
        if not (selected<=d<=end):continue
        key=(d.isoformat(),row.get("title"))
        if key in seen:continue
        seen.add(key)
        out.append({
            "date":d.isoformat(),
            "title":row.get("title"),
            "meta":row.get("meta") or "",
            "time":row.get("time") or "",
            "detail":row.get("detail") or "",
            "days_away":(d-selected).days,
        })
        if len(out)>=limit:break
    return out


def _upcoming_planets(selected,timezone_name,registry,days=60,limit=6):
    data=registry.run("planetary",{"date":selected.isoformat(),"timezone":timezone_name,"mode":"transit"})
    end=selected+timedelta(days=days)
    rows=[]
    for event in data.get("events") or []:
        try:d=date.fromisoformat(str(event.get("date")))
        except (TypeError,ValueError):continue
        if selected<=d<=end:
            rows.append({
                "date":d.isoformat(),
                "planet":event.get("planet"),
                "title":f"{event.get('planet')} → {event.get('to_rashi')}",
                "from_rashi":event.get("from_rashi"),
                "to_rashi":event.get("to_rashi"),
                "direction":event.get("direction"),
                "days_away":(d-selected).days,
            })
        if len(rows)>=limit:break
    return rows,data


def build(payload):
    selected,tz,timezone_name=_selected(payload)
    lat=float(payload.get("lat",18.5204));lon=float(payload.get("lon",73.8567))
    if not (-90<=lat<=90 and -180<=lon<=180):raise ValueError("Invalid latitude/longitude")
    city=str(payload.get("city") or "Current location").strip()[:120]
    base={"lat":lat,"lon":lon,"city":city,"timezone":timezone_name,"date":selected.isoformat(),"hour24":bool(payload.get("hour24",False))}
    cache=FileTTLCache(namespace="tithika-home-dashboard",ttl_seconds=900)
    key=cache.key("dashboard",base)
    cached=cache.get(key)
    if cached:
        cached["cache"]="hit"
        return cached

    registry=EngineRegistry(timeout_seconds=55)
    panchang=registry.run("panchang",base)
    choghadiya=registry.run("choghadiya",base)
    advice=advise({**base,"range":"week","purpose":"general"})
    calendar=_upcoming_calendar(selected,lat,lon,tz)
    planets,planet_data=_upcoming_planets(selected,timezone_name,registry)

    st=panchang.get("sunrise_state") or {}
    lunar=panchang.get("lunar_month") or {}
    top=(advice.get("advisor") or {}).get("recommendations") or []
    data={
        "ok":True,
        "cache":"miss",
        "date":selected.isoformat(),
        "location":{"city":city,"lat":lat,"lon":lon,"timezone":timezone_name},
        "today":{
            "weekday":selected.strftime("%A"),
            "tithi":st.get("tithi"),
            "paksha":st.get("paksha"),
            "nakshatra":st.get("nakshatra"),
            "yoga":st.get("yoga"),
            "karana":st.get("karana"),
            "moon_rashi":panchang.get("moon_rashi"),
            "sun_rashi":panchang.get("sun_rashi"),
            "lunar_month":lunar.get("purnimanta") or lunar.get("amanta"),
            "sunrise":panchang.get("sunrise_label"),
            "sunset":panchang.get("sunset_label"),
            "moonrise":panchang.get("moonrise_label"),
            "moonset":panchang.get("moonset_label"),
            "rahu_kaal":(panchang.get("muhurtas") or {}).get("rahu_kaal"),
        },
        "choghadiya":{
            "active":choghadiya.get("active"),
            "day":choghadiya.get("day") or [],
            "night":choghadiya.get("night") or [],
            "next_auspicious":choghadiya.get("next_auspicious"),
        },
        "advisor":{
            "summary":(advice.get("advisor") or {}).get("summary"),
            "recommendations":top[:4],
            "confidence":(advice.get("intelligence") or {}).get("confidence"),
        },
        "upcoming":{"calendar":calendar,"planets":planets},
        "provenance":[
            registry.source("panchang",panchang).as_dict(),
            registry.source("choghadiya",choghadiya).as_dict(),
            registry.source("planetary",planet_data).as_dict(),
        ],
        "note":"Dashboard aggregates verified engines; it does not create new calendar or astronomy rules.",
    }
    cache.set(key,data)
    return data


if __name__=="__main__":
    try:
        payload=json.loads(sys.stdin.read() or "{}")
        print(json.dumps(build(payload),ensure_ascii=False))
    except Exception as exc:
        print(json.dumps({"ok":False,"error":str(exc),"code":"HOME_DASHBOARD_FAILED"},ensure_ascii=False))
        sys.exit(1)
