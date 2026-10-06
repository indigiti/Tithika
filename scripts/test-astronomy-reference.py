#!/usr/bin/env python3
import os,sys
from datetime import datetime
from zoneinfo import ZoneInfo
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)));sys.path.insert(0,os.path.join(ROOT,"python"))
import astronomy_reference as x
tz=ZoneInfo("Asia/Kolkata");m=datetime(2026,10,6,12,0,tzinfo=tz)
assert len(x.zodiac_rows(m,True))==12 and len(x.zodiac_rows(m,False))==12
assert len(x.season_rows(2026,18.5204,73.8567,tz))==6
assert len(x.parallel_rows(m))>=1
cross=x.crossing_rows(2026,tz);assert len(cross)>10
print("Astronomy reference fixture passed")
