#!/usr/bin/env python3
import os,sys
from zoneinfo import ZoneInfo
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)));sys.path.insert(0,os.path.join(ROOT,"python"))
import vrat_completion as x
tz=ZoneInfo("Asia/Kolkata");lat,lon=18.5204,73.8567
isk=x.iskcon_ekadashi(2026,lat,lon,tz);assert len(isk)>=20 and all("iskcon-" in r["detail"] for r in isk)
kal=x.kalashtami(2026,lat,lon,tz);assert len(kal)>=10
jan=x.masik_janmashtami(2026,lat,lon,tz);assert len(jan)>=10
dar=x.chandra_darshan(2026,lat,lon,tz);assert len(dar)>=10
isht=x.ishti_anvadhan(2026,lat,lon,tz);assert len(isht)>=40
chat=x.chaturmasa(2026,lat,lon,tz);assert len(chat)==1
assert len(x.collections("vrat/top-10"))==10
print("Vrat completion fixture passed")
