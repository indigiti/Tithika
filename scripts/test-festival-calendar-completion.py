#!/usr/bin/env python3
import os,sys
from zoneinfo import ZoneInfo
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)));sys.path.insert(0,os.path.join(ROOT,"python"))
import festival_calendar_completion as x
tz=ZoneInfo("Asia/Kolkata");lat,lon=18.5204,73.8567
major=x.major_events(2026,lat,lon,tz);assert len(major)==13
annual=x.yearly_observances(2026,lat,lon,tz)
assert len(annual)>100,len(annual)
pairs={(r["title"],r["date"]) for r in annual}
assert any("Diwali" in a and b.startswith("2026-") for a,b in pairs)
assert ("Ekadashi","2026-10-06") in pairs
assert any(a=="Purnima" for a,b in pairs) and any(a=="Amavasya" for a,b in pairs)
assert any("Pradosh" in a for a,b in pairs) and any("Sankashti" in a for a,b in pairs)
assert len(x.month_rows(2026,lat,lon,tz,"Ashwina"))>5
assert len(x.regional_year(2026,lat,lon,tz,"tamil"))>=10
print("Festival/calendar aggregation truth fixture passed")
