#!/usr/bin/env python3
import os,sys
from datetime import datetime
from zoneinfo import ZoneInfo
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)));sys.path.insert(0,os.path.join(ROOT,"python"))
import astronomy_reference as x

tz=ZoneInfo("Asia/Kolkata")
m=datetime(2026,10,6,12,0,tzinfo=tz)
assert len(x.zodiac_rows(m,True))==12
assert len(x.zodiac_rows(m,False))==12

# Indian Ritus use tropical solar boundaries, not Nirayana Sankranti.
seasons=x.season_rows(2026,19.0760,72.8777,tz)
assert len(seasons)==6
by={r["title"]:r for r in seasons}
assert by["Vasanta"]["date"]=="2026-02-18",by
assert by["Grishma"]["date"]=="2026-04-20",by
assert by["Varsha"]["date"]=="2026-06-21",by
assert by["Sharad"]["date"]=="2026-08-23",by
assert by["Hemanta"]["date"]=="2026-10-23",by
assert by["Shishira"]["date"] in ("2026-12-21","2026-12-22"),by
assert all("tropical zodiac" in r["meta"] for r in seasons)

# Exact mutual parallels are root-refined events; each emitted event must have
# declinations equal/opposite to tight numerical tolerance.
parallel=x.parallel_events(2026,tz)
assert parallel,parallel
for r in parallel[:50]:
    parts=r["meta"].replace("°","").split("/")
    a=float(parts[0].strip()); b=float(parts[1].strip())
    if "Contra-parallel" in r["title"]:
        assert abs(a+b)<0.0015,r
    else:
        assert abs(a-b)<0.0015,r

cross=x.crossing_rows(2026,tz)
assert len(cross)>10
print("Astronomy reference semantic fixture passed")
