#!/usr/bin/env python3
import os,sys
from zoneinfo import ZoneInfo
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)));sys.path.insert(0,os.path.join(ROOT,"python"))
import festival_calendar_completion as x
tz=ZoneInfo("Asia/Kolkata");lat,lon=18.5204,73.8567
major=x.major_events(2026,lat,lon,tz)
assert len(major)>80,len(major)
titles={r["title"] for r in major}
for expected in ("Diwali / Lakshmi Puja","Purnima","Amavasya","Ekadashi","Pradosham","Sankashti Chaturthi","Masik Shivaratri"):
    assert expected in titles,expected
assert len(x.purnima_rows(2026,lat,lon,tz))>=12
assert len(x.month_rows(2026,lat,lon,tz,"Ashwina"))>=1
assert len(x.regional_year(2026,lat,lon,tz,"tamil"))>=10
assert len(x.COLLECTIONS["festivals/navdurga"])==9
print("Festival/calendar semantic fixture passed")
