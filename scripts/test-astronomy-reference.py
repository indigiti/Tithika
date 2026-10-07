#!/usr/bin/env python3
import os,sys
from datetime import datetime,timedelta
from zoneinfo import ZoneInfo
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)));sys.path.insert(0,os.path.join(ROOT,"python"))
import astronomy_reference as x
tz=ZoneInfo("Asia/Kolkata");m=datetime(2026,10,6,12,0,tzinfo=tz)
assert len(x.zodiac_rows(m,True))==12 and len(x.zodiac_rows(m,False))==12
seasons=x.season_rows(2026,19.0760,72.8777,tz);assert len(seasons)==6
expected=[("Vasanta",datetime(2026,2,18,21,20,tzinfo=tz)),("Grishma",datetime(2026,4,20,7,8,tzinfo=tz))]
for name,want in expected:
 row=next(r for r in seasons if r["title"]==name);got=datetime.fromisoformat(row["start"])
 assert abs((got-want).total_seconds())<10*60,(name,got,want)
par=x.parallel_events(2026,10,tz);assert par
for r in par[:5]:
 at=datetime.fromisoformat(r["datetime"]);parts=r["title"].split();a=parts[0];b=parts[-1]
 da,db=x.declination(a,at),x.declination(b,at)
 residual=abs(da-db) if r["parallel_type"]=="parallel" else abs(da+db)
 assert residual<1e-4,(r,residual)
cross=x.crossing_rows(2026,tz);assert len(cross)>10
print("Astronomy reference truth fixture passed")
