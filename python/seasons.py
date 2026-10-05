#!/usr/bin/env python3
"""Tithika equinox and solstice engine."""
from __future__ import annotations
import json
import sys
from datetime import datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
import panchang

def main():
    payload=json.loads(sys.stdin.read() or "{}")
    date_text=payload.get("date") or datetime.now().strftime("%Y-%m-%d")
    selected=datetime.strptime(date_text,"%Y-%m-%d").date()
    timezone_name=payload.get("timezone") or "Asia/Kolkata"
    try:
        tz=ZoneInfo(timezone_name)
    except ZoneInfoNotFoundError:
        timezone_name="Asia/Kolkata";tz=ZoneInfo(timezone_name)

    seasons=panchang.astronomy.Seasons(selected.year)
    raw={
        "vernal_equinox":seasons.mar_equinox,
        "summer_solstice":seasons.jun_solstice,
        "autumnal_equinox":seasons.sep_equinox,
        "winter_solstice":seasons.dec_solstice,
    }
    labels={
        "vernal_equinox":"March Equinox",
        "summer_solstice":"June Solstice",
        "autumnal_equinox":"September Equinox",
        "winter_solstice":"December Solstice",
    }
    events={}
    for key,value in raw.items():
        local=panchang.datetime_from_astronomy(value,tz)
        events[key]={
            "name":labels[key],
            "datetime":local.isoformat(),
            "date_label":local.strftime("%B %d, %Y").replace(" 0"," "),
            "time_label":local.strftime("%I:%M %p").lstrip("0"),
            "weekday":local.strftime("%A"),
        }

    print(json.dumps({
        "ok":True,
        "year":selected.year,
        "timezone":timezone_name,
        "events":events,
        "engine":{
            "name":"tithika-seasons",
            "source":"Astronomy Engine",
            "scope":"global astronomical instant rendered in selected local timezone"
        }
    },ensure_ascii=False))

if __name__=="__main__":
    try:
        main()
    except Exception as exc:
        print(json.dumps({"ok":False,"error":str(exc),"code":"SEASONS_CALCULATION_FAILED"}))
        sys.exit(1)
