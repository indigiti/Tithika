#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
import hashlib
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from typing import Any

import lunar_occurrences
import observances
import sankranti
import planetary
import festival_rules
import panchang

ENGINE_VERSION="1.0.0"
DEFAULT_CATEGORIES=[
    "ekadashi","purnima","amavasya","sankashti","pradosh","shivaratri",
    "sankranti","festivals","transit","retrograde"
]
ALLOWED_CATEGORIES=set(DEFAULT_CATEGORIES+["solar"])


def parse_date(value: Any) -> date:
    text=str(value or "").strip()
    return datetime.strptime(text,"%Y-%m-%d").date() if text else date.today()


def safe_tz(value: Any) -> tuple[str,ZoneInfo]:
    name=str(value or "Asia/Kolkata").strip()
    try:
        return name,ZoneInfo(name)
    except ZoneInfoNotFoundError:
        return "Asia/Kolkata",ZoneInfo("Asia/Kolkata")


def years_between(start: date,end: date) -> list[int]:
    return list(range(start.year,end.year+1))


def iso_dt(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value,datetime):
        return value.isoformat()
    text=str(value).strip()
    return text or None


def event_id(kind: str, when: str, title: str) -> str:
    raw=f"{kind}|{when}|{title}".encode("utf-8")
    return hashlib.sha1(raw).hexdigest()[:20]


def add_event(rows: list[dict[str,Any]], kind: str, title: str, event_date: date,
              route: str, subtitle: str="", start: str | None=None, end: str | None=None,
              all_day: bool=True, meta: dict[str,Any] | None=None) -> None:
    when=start or event_date.isoformat()
    rows.append({
        "id":event_id(kind,when,title),
        "kind":kind,
        "date":event_date.isoformat(),
        "title":title,
        "subtitle":subtitle,
        "route":route,
        "start":start,
        "end":end,
        "all_day":bool(all_day),
        "meta":meta or {},
    })


def ekadashi_rows(year: int,lat: float,lon: float,tz: ZoneInfo,hour24: bool,
                   tradition: str,rows: list[dict[str,Any]]) -> None:
    for rule in lunar_occurrences.KINDS["ekadashi"]:
        for event in lunar_occurrences.events_for_rule(year,rule,lat,lon,tz,hour24):
            profiles=event.get("observance") or {}
            profile=profiles.get(tradition) or profiles.get("smarta") or {}
            d=profile.get("date")
            if not d or int(str(d)[:4])!=year:
                continue
            day=datetime.strptime(str(d),"%Y-%m-%d").date()
            parana=profile.get("parana") or {}
            add_event(
                rows,"ekadashi",f"{event.get('purnimanta_month') or event.get('amanta_month') or ''} Ekadashi".strip(),
                day,"vrat/ekadashi",str(profile.get("basis") or event.get("paksha") or "Ekadashi observance"),
                all_day=True,meta={"tradition":tradition,"paksha":event.get("paksha"),"basis":profile.get("basis")}
            )
            pd=parana.get("date")
            if pd and int(str(pd)[:4])==year:
                pday=datetime.strptime(str(pd),"%Y-%m-%d").date()
                add_event(
                    rows,"parana","Ekadashi Parana",pday,"vrat/ekadashi",
                    "Break-fast window after Ekadashi",
                    start=iso_dt(parana.get("start")),end=iso_dt(parana.get("end")),all_day=False,
                    meta={"tradition":tradition,"start_label":parana.get("start_label"),"end_label":parana.get("end_label")}
                )


def lunar_rows(kind: str,year: int,lat: float,lon: float,tz: ZoneInfo,hour24: bool,
               rows: list[dict[str,Any]]) -> None:
    route="vrat/purnima" if kind=="purnima" else "vrat/amavasya"
    title="Purnima" if kind=="purnima" else "Amavasya"
    for rule in lunar_occurrences.KINDS[kind]:
        for event in lunar_occurrences.events_for_rule(year,rule,lat,lon,tz,hour24):
            candidates=event.get("sunrise_candidates") or []
            picked=next((c for c in candidates if int(str(c.get("date","0"))[:4] or 0)==year),None)
            raw_date=(picked or {}).get("date") or str(event.get("start",""))[:10]
            if not raw_date or int(str(raw_date)[:4])!=year:
                continue
            d=datetime.strptime(str(raw_date),"%Y-%m-%d").date()
            add_event(
                rows,kind,title,d,route,
                f"{event.get('amanta_month') or ''} · {event.get('paksha') or ''}".strip(" ·"),
                start=iso_dt(event.get("start")),end=iso_dt(event.get("end")),all_day=True,
                meta={"amanta_month":event.get("amanta_month"),"purnimanta_month":event.get("purnimanta_month")}
            )


def observance_rows(kind: str,year: int,lat: float,lon: float,tz: ZoneInfo,hour24: bool,
                    rows: list[dict[str,Any]]) -> None:
    route={"sankashti":"vrat/sankashti-chaturthi","pradosh":"vrat/pradosham","shivaratri":"vrat/masik-shivaratri"}[kind]
    for event in observances.calculate(kind,year,lat,lon,tz,hour24):
        d=datetime.strptime(event["date"],"%Y-%m-%d").date()
        start=end=None
        subtitle=str(event.get("observance") or event.get("paksha") or "")
        if kind=="sankashti":
            start=iso_dt(event.get("moonrise"))
            title=str(event.get("name") or "Sankashti Chaturthi")
        elif kind=="pradosh":
            p=event.get("puja") or event.get("pradosh_kaal") or {}
            start=iso_dt(p.get("start"));end=iso_dt(p.get("end"))
            title=str(event.get("name") or "Pradosh Vrat")
        else:
            p=event.get("nishita") or event.get("puja") or {}
            start=iso_dt(p.get("start"));end=iso_dt(p.get("end"))
            title=str(event.get("name") or "Masik Shivaratri")
        add_event(rows,kind,title,d,route,subtitle,start=start,end=end,all_day=start is None,
                  meta={"paksha":event.get("paksha"),"amanta_month":event.get("amanta_month")})


def sankranti_rows(year: int,lat: float,lon: float,tz: ZoneInfo,hour24: bool,
                    rows: list[dict[str,Any]]) -> None:
    for event in sankranti.find_year(year,lat,lon,tz,hour24):
        moment=datetime.fromisoformat(event["datetime"])
        add_event(rows,"sankranti",f"{event.get('rashi','')} Sankranti".strip(),moment.date(),
                  "vrat/sankranti","Nirayana solar ingress",start=moment.isoformat(),all_day=False,
                  meta={"rashi":event.get("rashi"),"punya_kaal":event.get("punya_kaal")})


def festival_rows(year: int,lat: float,lon: float,tz: ZoneInfo,hour24: bool,
                  rows: list[dict[str,Any]]) -> None:
    for kind in festival_rules.SUPPORTED_KINDS:
        event=festival_rules.calculate_event(kind,year,lat,lon,tz,hour24)
        if not event:
            continue
        d=datetime.strptime(event["date"],"%Y-%m-%d").date()
        add_event(rows,"festival",str(event.get("title") or kind.replace("-"," ").title()),d,
                  f"festivals/{kind}",str((event.get("rule") or {}).get("profile") or "Verified festival selector"),
                  all_day=True,meta={"festival_kind":kind,"selector":(event.get("rule") or {}).get("selector")})


def planet_rows(kind: str,year: int,tz: ZoneInfo,rows: list[dict[str,Any]]) -> None:
    source=planetary.transit_events(year,tz) if kind=="transit" else planetary.retrograde_events(year,tz)
    for event in source:
        moment=datetime.fromisoformat(event["datetime"])
        planet=str(event.get("planet") or "Planet")
        if kind=="transit":
            title=f"{planet} enters {event.get('to_rashi') or 'new Rashi'}"
            subtitle=f"{event.get('from_rashi','')} → {event.get('to_rashi','')}".strip(" →")
            route="planets/transit"
        else:
            title=f"{planet} turns {'retrograde' if event.get('event')=='retrograde' else 'direct'}"
            subtitle=str(event.get("rashi") or "Planetary station")
            route="planets/retrograde"
        add_event(rows,kind,title,moment.date(),route,subtitle,start=moment.isoformat(),all_day=False,
                  meta={"planet":planet})


def solar_rows(start: date,end: date,lat: float,lon: float,tz: ZoneInfo,hour24: bool,
               rows: list[dict[str,Any]]) -> None:
    d=start
    while d<=end:
        sunrise=panchang.rise_set(d,lat,lon,tz,panchang.astronomy.Body.Sun,panchang.astronomy.Direction.Rise)
        sunset=panchang.rise_set(d,lat,lon,tz,panchang.astronomy.Body.Sun,panchang.astronomy.Direction.Set)
        observer=panchang.astronomy.Observer(lat,lon,0.0)
        moonrise_event=panchang.astronomy.SearchRiseSet(
            panchang.astronomy.Body.Moon,observer,panchang.astronomy.Direction.Rise,
            panchang.astronomy_time(datetime(d.year,d.month,d.day,0,0,tzinfo=tz)),1.2
        )
        moonrise=panchang.datetime_from_astronomy(moonrise_event,tz) if moonrise_event else None
        for kind,title,moment,route in (
            ("sunrise","Sunrise",sunrise,"panchang/daily"),
            ("sunset","Sunset",sunset,"panchang/daily"),
            ("moonrise","Moonrise",moonrise,"panchang/moonrise"),
        ):
            if moment and moment.date()==d:
                add_event(rows,kind,title,d,route,"Local astronomical event",start=moment.isoformat(),all_day=False)
        d+=timedelta(days=1)


def build(payload: dict[str,Any]) -> dict[str,Any]:
    start=parse_date(payload.get("date"))
    horizon=max(1,min(int(payload.get("horizon_days") or 45),366))
    end=start+timedelta(days=horizon)
    lat=float(payload.get("lat",19.0760));lon=float(payload.get("lon",72.8777))
    if not (-90<=lat<=90 and -180<=lon<=180):
        raise ValueError("Invalid latitude/longitude")
    timezone_name,tz=safe_tz(payload.get("timezone"))
    city=str(payload.get("city") or "Current location")[:120]
    tradition=str(payload.get("tradition") or "smarta").lower()
    if tradition not in {"smarta","vaishnava","iskcon"}:
        tradition="smarta"
    hour24=bool(payload.get("hour24",False))
    requested=payload.get("categories")
    if isinstance(requested,list):
        categories=[str(x).lower() for x in requested if str(x).lower() in ALLOWED_CATEGORIES]
    else:
        categories=DEFAULT_CATEGORIES[:]
    categories=list(dict.fromkeys(categories))

    rows: list[dict[str,Any]]=[]
    years=years_between(start,end)
    for year in years:
        if "ekadashi" in categories:
            ekadashi_rows(year,lat,lon,tz,hour24,tradition,rows)
        if "purnima" in categories:
            lunar_rows("purnima",year,lat,lon,tz,hour24,rows)
        if "amavasya" in categories:
            lunar_rows("amavasya",year,lat,lon,tz,hour24,rows)
        for kind in ("sankashti","pradosh","shivaratri"):
            if kind in categories:
                observance_rows(kind,year,lat,lon,tz,hour24,rows)
        if "sankranti" in categories:
            sankranti_rows(year,lat,lon,tz,hour24,rows)
        if "festivals" in categories:
            festival_rows(year,lat,lon,tz,hour24,rows)
        if "transit" in categories:
            planet_rows("transit",year,tz,rows)
        if "retrograde" in categories:
            planet_rows("retrograde",year,tz,rows)

    if "solar" in categories:
        solar_rows(start,end,lat,lon,tz,hour24,rows)

    filtered=[]
    seen=set()
    for row in rows:
        d=datetime.strptime(row["date"],"%Y-%m-%d").date()
        if not (start<=d<=end):
            continue
        sig=(row["kind"],row["date"],row["title"],row.get("start"))
        if sig in seen:
            continue
        seen.add(sig);filtered.append(row)
    filtered.sort(key=lambda r:(r["date"],r.get("start") or "",r["kind"],r["title"]))

    return {
        "ok":True,
        "date":start.isoformat(),
        "through":end.isoformat(),
        "horizon_days":horizon,
        "location":{"city":city,"lat":lat,"lon":lon,"timezone":timezone_name},
        "preferences":{"tradition":tradition,"categories":categories},
        "events":filtered,
        "counts":{
            "total":len(filtered),
            "by_kind":{kind:sum(1 for row in filtered if row["kind"]==kind) for kind in sorted({r["kind"] for r in filtered})}
        },
        "engine":{
            "name":"tithika-notification-agenda","version":ENGINE_VERSION,
            "sources":["tithika-lunar-occurrences","tithika-observances","tithika-sankranti",
                       "tithika-festival-rules","tithika-planetary","tithika-panchang"]
        },
        "delivery":{
            "calendar_feed":"ics",
            "onsite_alerts":"while-tithika-is-open",
            "background_push":"reserved-for-pwa-service-worker-phase"
        }
    }


def main() -> None:
    payload=json.loads(sys.stdin.read() or "{}")
    if not isinstance(payload,dict):
        raise ValueError("Payload must be an object")
    print(json.dumps(build(payload),ensure_ascii=False))


if __name__=="__main__":
    try:
        main()
    except Exception as exc:
        print(json.dumps({"ok":False,"error":str(exc),"code":"NOTIFICATION_AGENDA_FAILED"},ensure_ascii=False))
        sys.exit(1)
