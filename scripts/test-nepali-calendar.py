#!/usr/bin/env python3
import os
import sys
from datetime import date, datetime
from zoneinfo import ZoneInfo

ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,os.path.join(ROOT,"python"))

import nepali_calendar

# Independent civil-date anchors for BS 2083.
a=nepali_calendar.ad_to_bs(date(2026,4,14))
assert (a["year"],a["month"],a["day"])==(2083,1,1),a
assert a["month_name"]=="Baisakh",a
assert a["data_quality"]=="official-lookup",a

oct6=nepali_calendar.ad_to_bs(date(2026,10,6))
assert (oct6["year"],oct6["month"],oct6["day"])==(2083,6,20),oct6
assert oct6["month_name"]=="Ashwin",oct6
assert oct6["month_name_nepali"]=="असोज",oct6

# Round trip inside the verified lookup range.
for y,m,d in [(2083,1,1),(2083,4,1),(2083,6,20),(2083,12,30)]:
    ad=nepali_calendar.bs_to_ad(y,m,d)
    back=nepali_calendar.ad_to_bs(ad)
    assert (back["year"],back["month"],back["day"])==(y,m,d),(y,m,d,ad,back)

tz=ZoneInfo("Asia/Kathmandu")
rows=nepali_calendar.calculate_month(
    datetime(2026,10,1).date(),27.7172,85.3240,tz,False
)
assert len(rows)==31
by={row["date"]:row for row in rows}
r=by["2026-10-06"]
assert r["regional_year"]==2083,r
assert r["regional_month"]=="Ashwin",r
assert r["regional_day"]==20,r
assert r["regional_date_native"]=="२०८३-०६-२०",r
assert r["calendar_basis"]=="bikram-sambat-civil",r
assert r["data_quality"]=="official-lookup",r
assert r["tithi"] and r["nakshatra"]

print("Nepali Bikram Sambat calendar fixture passed")
