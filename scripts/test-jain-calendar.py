#!/usr/bin/env python3
import os
import sys
from datetime import datetime
from zoneinfo import ZoneInfo

ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,os.path.join(ROOT,"python"))

import jain_calendar

tz=ZoneInfo("Asia/Kolkata")
lat,lon=22.3072,73.1812

new_year=jain_calendar.jain_new_year(2026,lat,lon,tz,False)
assert new_year.isoformat()=="2026-11-10",new_year

assert jain_calendar.kartikadi_year(
    datetime(2026,10,6).date(),lat,lon,tz,False
)==2082
assert jain_calendar.kartikadi_year(
    datetime(2026,11,9).date(),lat,lon,tz,False
)==2082
assert jain_calendar.kartikadi_year(
    datetime(2026,11,10).date(),lat,lon,tz,False
)==2083

oct_rows=jain_calendar.calculate_month(
    datetime(2026,10,1).date(),lat,lon,tz,False
)
oby={row["date"]:row for row in oct_rows}
oct6=oby["2026-10-06"]
assert oct6["regional_year"]==2082,oct6
assert oct6["vir_samvat"]==2552,oct6
assert oct6["calendar_basis"]=="kartikadi-amanta-jain",oct6

nov_rows=jain_calendar.calculate_month(
    datetime(2026,11,1).date(),lat,lon,tz,False
)
nby={row["date"]:row for row in nov_rows}
nov9=nby["2026-11-09"]
assert nov9["regional_year"]==2082,nov9
assert nov9["vir_samvat"]==2552,nov9
assert nov9["tithi"]=="Amavasya",nov9

nov10=nby["2026-11-10"]
assert nov10["regional_year"]==2083,nov10
assert nov10["vir_samvat"]==2553,nov10
assert "Kartak" in nov10["regional_month"],nov10
assert nov10["paksha"]=="Shukla Paksha",nov10
assert nov10["tithi"]=="Pratipada",nov10

# Aatham/Chaudas flags must mirror sunrise Tithi numbers.
for row in oct_rows+nov_rows:
    if not row.get("available"):
        continue
    flags=row["jain_observance"]
    assert flags["aatham"]==(row["tithi_number"]==8),row
    assert flags["chaudas"]==(row["tithi_number"]==14),row
    assert flags["amavasya"]==(row["tithi"]=="Amavasya"),row

print("Jain Kartikadi calendar fixture passed")
