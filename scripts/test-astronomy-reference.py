#!/usr/bin/env python3
import os,sys
from datetime import datetime
from zoneinfo import ZoneInfo
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)));sys.path.insert(0,os.path.join(ROOT,"python"))
import astronomy_reference as x
tz=ZoneInfo("Asia/Kolkata");m=datetime(2026,10,6,12,0,tzinfo=tz)
assert len(x.zodiac_rows(m,True))==12 and len(x.zodiac_rows(m,False))==12
seasons=x.season_rows(2026,18.5204,73.8567,tz);assert len(seasons)==6
for row,target in zip(seasons,[330,30,90,150,210,270]):
    at=datetime.fromisoformat(row["instant"])
    import panchang
    sun,_,_=panchang.tropical_longitudes(at)
    assert abs(((sun-target+180)%360)-180)<0.01,(row,sun,target)
pars=x.parallel_rows(2026,tz);assert pars
for row in pars[:20]:
    a,b=row["title"].replace("Contra-parallel","Parallel").split(" Parallel ")
    at=datetime.fromisoformat(row["instant"]);da=x.declination(a,at);db=x.declination(b,at)
    metric=abs(da+db) if "Contra-parallel" in row["title"] else abs(da-db)
    assert metric<1e-5,(row,metric)
cross=x.crossing_rows(2026,tz);assert len(cross)>10
print("Astronomy reference semantic fixture passed")
