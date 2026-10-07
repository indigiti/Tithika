#!/usr/bin/env python3
import os,sys
from zoneinfo import ZoneInfo
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)));sys.path.insert(0,os.path.join(ROOT,"python"))
import vrat_completion as x
tz=ZoneInfo("Asia/Kolkata");lat,lon=18.5204,73.8567
isk=x.iskcon_ekadashi(2026,lat,lon,tz);assert len(isk)>=20 and all("iskcon-" in r["detail"] for r in isk)
kal=x.kalashtami(2026,lat,lon,tz);assert any(r["date"]=="2026-01-10" for r in kal),kal[:2]
jan=x.masik_janmashtami(2026,lat,lon,tz);assert any(r["date"]=="2026-01-10" for r in jan),jan[:2]
assert all("Nishita" in r["meta"] for r in jan)
dar=x.chandra_darshan(2026,lat,lon,tz)
dar_dates={r["date"] for r in dar}
assert {"2026-01-20","2026-02-18","2026-03-20","2026-04-18"}<=dar_dates,sorted(dar_dates)
assert "2026-01-19" not in dar_dates,dar[:2]
assert all("elongation" in r["detail"] and "altitude" in r["detail"] for r in dar)
isht=x.ishti_anvadhan(2026,lat,lon,tz)
assert any(r["title"]=="Anvadhan" and r["date"]=="2026-01-03" for r in isht),isht[:4]
assert any(r["title"]=="Ishti" and r["date"]=="2026-01-04" for r in isht),isht[:4]
chat=x.chaturmasa(2026,lat,lon,tz);assert len(chat)==1
shr=x.shraddha(2026,lat,lon,tz)
titles={r["title"].split(" · ")[0] for r in shr}
assert {"Amavasya Shraddha","Sankranti Shraddha","Pitru Paksha Shraddha","Vaidhriti Yoga Shraddha","Vyatipata Yoga Shraddha","Manvadi Shraddha","Yugadi Shraddha","Kalpadi Shraddha"}<=titles,titles
print("Vrat semantic completion fixture passed")
