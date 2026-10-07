#!/usr/bin/env python3
import os,sys
from datetime import datetime
from zoneinfo import ZoneInfo
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)));sys.path.insert(0,os.path.join(ROOT,"python"))
import astronomy_reference as x
tz=ZoneInfo("Asia/Kolkata");m=datetime(2026,10,6,12,0,tzinfo=tz)
assert len(x.zodiac_rows(m,True))==12 and len(x.zodiac_rows(m,False))==12
seasons=x.season_rows(2026,18.5204,73.8567,tz);assert len(seasons)==6,seasons
assert [r["title"] for r in seasons]==["Vasanta","Grishma","Varsha","Sharad","Hemanta","Shishira"],seasons
# Boundaries must be tropical Ritu sectors, not Lahiri Sankranti dates.
assert seasons[0]["date"].startswith("2026-02"),seasons
assert seasons[1]["date"].startswith("2026-04"),seasons
assert seasons[2]["date"].startswith("2026-06"),seasons
par=x.parallel_rows(2026,tz);assert len(par)>10
for r in par[:20]:
    vals=[float(v.replace("°","")) for v in r["meta"].split(" / ")]
    if "Contra-parallel" in r["title"]: assert abs(vals[0]+vals[1])<0.002
    else: assert abs(vals[0]-vals[1])<0.002
cross=x.crossing_rows(2026,tz);assert len(cross)>10
print("Astronomy reference benchmarks passed")
