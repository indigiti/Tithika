#!/usr/bin/env python3
import os,sys
from datetime import datetime
from zoneinfo import ZoneInfo
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)));sys.path.insert(0,os.path.join(ROOT,"python"))
import astronomy_reference as x
tz=ZoneInfo("Asia/Kolkata");m=datetime(2026,10,6,12,0,tzinfo=tz)
assert len(x.zodiac_rows(m,True))==12 and len(x.zodiac_rows(m,False))==12
seasons=x.season_rows(2026,18.5204,73.8567,tz)
assert [r["date"] for r in seasons]==["2026-02-18","2026-04-20","2026-06-21","2026-08-23","2026-10-23","2026-12-22"],seasons
parallel=x.parallel_rows(m);assert len(parallel)>10
for r in parallel[:20]:
    a,b=[float(v.replace("°","")) for v in r["meta"].split(" / ")]
    if "Contra-parallel" in r["title"]: assert abs(a+b)<0.001
    else: assert abs(a-b)<0.001
cross=x.crossing_rows(2026,tz);assert len(cross)>10
print("Astronomy semantic reference fixture passed")
