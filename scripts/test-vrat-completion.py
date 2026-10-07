#!/usr/bin/env python3
import os,sys
from datetime import date,datetime
from zoneinfo import ZoneInfo
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)));sys.path.insert(0,os.path.join(ROOT,"python"))
import festival_rules,vrat_completion as x
tz=ZoneInfo("Asia/Kolkata");lat,lon=18.5204,73.8567
isk=x.iskcon_ekadashi(2026,lat,lon,tz);assert len(isk)>=20 and all("iskcon-" in r["detail"] for r in isk)
kal=x.kalashtami(2026,lat,lon,tz);assert len(kal)>=10
jan=x.masik_janmashtami(2026,lat,lon,tz);assert len(jan)>=10
for r in jan:
    d=date.fromisoformat(r["date"]);n=festival_rules.nishita_period(d,lat,lon,tz);assert n
    assert "no civil-midnight shortcut" in r["detail"]
dar=x.chandra_darshan(2026,lat,lon,tz);assert len(dar)>=10
assert all("not a meteorological" in r["detail"] for r in dar)
isht=x.ishti_anvadhan(2026,lat,lon,tz);assert len(isht)>=40
chat=x.chaturmasa(2026,lat,lon,tz);assert len(chat)==1
shr=x.shraddha(2026,lat,lon,tz)
titles={r["title"].split(" · ")[0] for r in shr}
for expected in ("Amavasya Shraddha","Sankranti Shraddha","Pitru Paksha Shraddha","Vaidhriti Shraddha","Vyatipata Shraddha","Manvadi Shraddha","Yugadi Shraddha","Purvedyu Shraddha","Ashtaka Shraddha","Anvashtaka Shraddha"):
    assert expected in titles,(expected,titles)
assert len(x.collections("vrat/top-10"))==10
print("Vrat completion semantic fixture passed")
