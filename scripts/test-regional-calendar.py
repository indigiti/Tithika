#!/usr/bin/env python3
import os
import sys
from datetime import datetime
from zoneinfo import ZoneInfo

ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,os.path.join(ROOT,"python"))

import regional_calendar

tz=ZoneInfo("Asia/Kolkata")

# Malayalam solar calendar benchmark: Kanni 8, Kollavarsham 1202.
mal=regional_calendar.calculate_month(
    "malayalam",datetime(2026,9,1).date(),13.0827,80.2707,tz,False
)
mby={row["date"]:row for row in mal if row.get("available")}
sep24=mby["2026-09-24"]
assert sep24["regional_month"]=="Kanni",sep24
assert sep24["regional_day"]==8,sep24
assert sep24["era"]["name"]=="Kollavarsham"
assert sep24["era"]["year"]==1202,sep24

# Bengali solar calendar benchmark: Bhadro 13, Bengali Era 1433.
ben=regional_calendar.calculate_month(
    "bengali",datetime(2026,8,1).date(),22.5726,88.3639,tz,False
)
bby={row["date"]:row for row in ben if row.get("available")}
aug30=bby["2026-08-30"]
assert aug30["regional_month"]=="Bhadro",aug30
assert aug30["regional_day"]==13,aug30
assert aug30["era"]["name"]=="Bengali Era"
assert aug30["era"]["year"]==1433,aug30

assert bby["2026-08-17"]["regional_month"]=="Srabon",bby["2026-08-17"]
assert bby["2026-08-17"]["regional_day"]==32,bby["2026-08-17"]
assert bby["2026-08-18"]["regional_month"]=="Bhadro",bby["2026-08-18"]
assert bby["2026-08-18"]["regional_day"]==1,bby["2026-08-18"]

# Assamese follows the same first-sunrise-after-Sankranti month rollover.
assam=regional_calendar.calculate_month(
    "assamese",datetime(2026,8,1).date(),20.7690,72.9613,tz,False
)
aby={row["date"]:row for row in assam if row.get("available")}
assert aby["2026-08-17"]["regional_month"]=="Sawan",aby["2026-08-17"]
assert aby["2026-08-17"]["regional_day"]==32,aby["2026-08-17"]
assert aby["2026-08-18"]["regional_month"]=="Bhad",aby["2026-08-18"]
assert aby["2026-08-18"]["regional_day"]==1,aby["2026-08-18"]

# Solar and lunar convention contracts.
for variant in ("tamil","malayalam","bengali","odia","assamese"):
    rows=regional_calendar.calculate_month(
        variant,datetime(2026,10,1).date(),18.5204,73.8567,tz,False
    )
    assert len(rows)==31
    assert all(
        (not row.get("available")) or row["calendar_basis"]=="nirayana-solar"
        for row in rows
    )

for variant in ("telugu","kannada","gujarati","marathi"):
    rows=regional_calendar.calculate_month(
        variant,datetime(2026,10,1).date(),18.5204,73.8567,tz,False
    )
    assert len(rows)==31
    assert all(
        (not row.get("available")) or row["calendar_basis"]=="amanta-lunar"
        for row in rows
    )

hindi=regional_calendar.calculate_month(
    "hindi",datetime(2026,10,1).date(),18.5204,73.8567,tz,False
)
assert all(
    (not row.get("available")) or row["calendar_basis"]=="purnimanta-lunar"
    for row in hindi
)

iskcon=regional_calendar.calculate_month(
    "iskcon",datetime(2026,11,1).date(),18.5204,73.8567,tz,False
)
assert all(
    (not row.get("available")) or row["calendar_basis"]=="purnimanta-lunar"
    for row in iskcon
)
assert any(
    row.get("available") and row.get("regional_month")=="Damodara"
    for row in iskcon
),[row.get("regional_month") for row in iskcon if row.get("available")]

print("Regional calendar fixture passed")