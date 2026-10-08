#!/usr/bin/env python3
from datetime import date
from zoneinfo import ZoneInfo
import os, sys

ROOT=os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0,os.path.join(ROOT,"python"))

import regional_calendar
import nepali_calendar

selected=date(2026,10,8)
lat,lon=18.5204,73.8567
tz=ZoneInfo("Asia/Kolkata")

for variant in regional_calendar.SUPPORTED:
    daily=regional_calendar.calculate_day(variant,selected,lat,lon,tz,False)
    month=regional_calendar.calculate_month(variant,selected,lat,lon,tz,False)
    row=next(x for x in month if x.get("date")==selected.isoformat())
    assert daily["regional_month"]==row["regional_month"],(variant,daily,row)
    assert daily["regional_day"]==row["regional_day"],(variant,daily,row)
    assert daily["tithi"]==row["tithi"],(variant,daily,row)
    assert daily["nakshatra"]==row["nakshatra"],(variant,daily,row)
    assert daily["calendar_basis"]==row["calendar_basis"],(variant,daily,row)
    assert daily["yoga"] and daily["karana"],(variant,daily)
    assert daily["sunrise_label"] and daily["sunset_label"],(variant,daily)
    for key in ("abhijit","rahu_kaal","yamaganda","gulika"):
        value=(daily.get("muhurtas") or {}).get(key)
        assert value and value.get("start") and value.get("end"),(variant,key,value)

np_tz=ZoneInfo("Asia/Kathmandu")
np_lat,np_lon=27.7172,85.3240
daily=nepali_calendar.calculate_day(selected,np_lat,np_lon,np_tz,False)
month=nepali_calendar.calculate_month(selected,np_lat,np_lon,np_tz,False)
row=next(x for x in month if x.get("date")==selected.isoformat())
for key in ("regional_month","regional_day","regional_year","regional_date_native","data_quality","tithi","nakshatra"):
    assert daily.get(key)==row.get(key),(key,daily.get(key),row.get(key))
assert daily["calendar_basis"]=="bikram-sambat-civil"
assert daily["yoga"] and daily["karana"]
assert (daily.get("muhurtas") or {}).get("abhijit")

print(f"Regional daily Panchang fixture passed: {len(regional_calendar.SUPPORTED)+1} variants")
