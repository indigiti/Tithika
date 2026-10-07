#!/usr/bin/env python3
import os,sys
from zoneinfo import ZoneInfo
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)));sys.path.insert(0,os.path.join(ROOT,"python"))
import vrat_completion as x
tz=ZoneInfo("Asia/Kolkata");lat,lon=18.5204,73.8567
isk=x.iskcon_ekadashi(2026,lat,lon,tz);assert len(isk)>=20 and all("iskcon-" in r["detail"] for r in isk)
kal=x.kalashtami(2026,lat,lon,tz);assert any(r["date"]=="2026-01-10" for r in kal),kal[:2]
jan=x.masik_janmashtami(2026,lat,lon,tz);assert any(r["date"]=="2026-01-10" for r in jan),jan[:2]
dar=x.chandra_darshan(2026,lat,lon,tz);assert any(r["date"]=="2026-01-20" for r in dar),dar[:2]
isht=x.ishti_anvadhan(2026,lat,lon,tz)
pairs={(r["title"],r["date"]) for r in isht}
for pair in [("Anvadhan","2026-01-03"),("Ishti","2026-01-04"),("Anvadhan","2026-01-18"),("Ishti","2026-01-19")]:assert pair in pairs,(pair,sorted(pairs)[:8])
chat=x.chaturmasa(2026,lat,lon,tz);assert len(chat)==1
shr=x.shraddha(2026,lat,lon,tz)
assert any(r["title"]=="Dwadashi Shraddha" and r["date"]=="2026-10-07" for r in shr)
assert any(r["title"]=="Sankranti Shraddha" for r in shr)
assert any(r["title"].startswith("Vaidhriti") for r in shr) and any(r["title"].startswith("Vyatipata") for r in shr)
assert any(r["title"].startswith("Kalpadi Shraddha") for r in shr)
for title in ("Purvedyu Shraddha","Ashtaka Shraddha","Anvashtaka Shraddha"):
    assert sum(1 for r in shr if r["title"]==title)>=4,(title,[r for r in shr if r["title"]==title])
print("Vrat completion truth fixture passed")
