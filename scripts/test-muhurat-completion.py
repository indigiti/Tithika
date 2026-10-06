#!/usr/bin/env python3
import os,sys
from datetime import date
from zoneinfo import ZoneInfo
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)));sys.path.insert(0,os.path.join(ROOT,"python"))
import muhurat_completion as x
tz=ZoneInfo("Asia/Kolkata");lat,lon=18.5204,73.8567;d=date(2026,10,6)
g=x.gowri(d,lat,lon,tz);assert sum(len(s["items"]) for s in g)==16
assert len(x.pachchakkhan(d,lat,lon,tz)[0]["items"])==10
assert len(x.do_ghati(d,lat,lon,tz)[0]["items"])==30
assert sum(len(s["items"]) for s in x.pakshi_sections(d,lat,lon,tz))==50
assert len(x.shubha_dates(2026,lat,lon,tz)[0]["items"])>0
print("Muhurat completion fixture passed")
