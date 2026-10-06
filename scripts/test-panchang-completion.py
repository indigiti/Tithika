#!/usr/bin/env python3
import os,sys
from zoneinfo import ZoneInfo
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)));sys.path.insert(0,os.path.join(ROOT,"python"))
import panchang_completion as x
tz=ZoneInfo("Asia/Kolkata");lat,lon=18.5204,73.8567
assert len(x.MANVADI)==14 and len(x.YUGADI)==4 and len(x.KALPADI)==7
assert len(x.select_lunar_rules(2026,lat,lon,tz,x.YUGADI))>=3
assert len(x.select_lunar_rules(2026,lat,lon,tz,x.KALPADI))>=5
snap=x.published_snapshot(__import__("datetime").date(2026,10,6),lat,lon,tz)
assert snap and "Publication-ready" in snap[0]["title"]
assert len(x.utilities())>=10
print("Panchang completion fixture passed")
