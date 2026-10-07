#!/usr/bin/env python3
import os,sys
from zoneinfo import ZoneInfo
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)));sys.path.insert(0,os.path.join(ROOT,"python"))
import vrat_completion as x
tz=ZoneInfo("Asia/Kolkata");lat,lon=18.5204,73.8567
isk=x.iskcon_ekadashi(2026,lat,lon,tz);assert len(isk)>=20 and all("iskcon-" in r["detail"] for r in isk)
kal=x.kalashtami(2026,lat,lon,tz);assert any(r["date"]=="2026-01-10" for r in kal),kal[:3]
jan=x.masik_janmashtami(2026,lat,lon,tz);assert any(r["date"]=="2026-01-10" for r in jan),jan[:3]
dar=x.chandra_darshan(2026,lat,lon,tz);assert any(r["date"]=="2026-01-20" for r in dar),dar[:3]
isht=x.ishti_anvadhan(2026,lat,lon,tz)
pairs={(r["title"],r["date"]) for r in isht}
assert ("Anvadhan","2026-01-03") in pairs and ("Ishti","2026-01-04") in pairs,pairs
assert ("Anvadhan","2026-01-18") in pairs and ("Ishti","2026-01-19") in pairs,pairs
chat=x.chaturmasa(2026,lat,lon,tz);assert len(chat)==1
shr=x.shraddha(2026,lat,lon,tz)
assert any(r["title"].startswith("Sankranti Shraddha") for r in shr)
assert any(r["title"].startswith("Kalpadi Shraddha") for r in shr)
print("Vrat completion benchmarks passed")
