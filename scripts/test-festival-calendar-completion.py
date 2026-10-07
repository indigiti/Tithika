#!/usr/bin/env python3
import os,sys
from zoneinfo import ZoneInfo
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)));sys.path.insert(0,os.path.join(ROOT,"python"))
import festival_calendar_completion as x
tz=ZoneInfo("Asia/Kolkata");lat,lon=18.5204,73.8567
major=x.major_events(2026,lat,lon,tz);assert len(major)==13
assert any(r["title"].startswith("Diwali") for r in major)
yearly=x.yearly_events(2026,lat,lon,tz)
assert len(yearly)>55,len(yearly)
assert any("Sankranti" in r["title"] for r in yearly)
assert any("Ekadashi" in r["title"] for r in yearly)
assert len(x.purnima_rows(2026,lat,lon,tz))>=12
assert len(x.month_rows(2026,lat,lon,tz,"Ashwina"))>=3
assert len(x.regional_year(2026,lat,lon,tz,"tamil"))>=10
assert len(x.COLLECTIONS["festivals/navdurga"])==9
print("Festival/calendar semantic completion fixture passed")
