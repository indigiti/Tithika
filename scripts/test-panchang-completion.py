#!/usr/bin/env python3
import os,sys
from datetime import date,datetime
from zoneinfo import ZoneInfo
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)));sys.path.insert(0,os.path.join(ROOT,"python"))
import panchang_completion as x
tz=ZoneInfo("Asia/Kolkata");lat,lon=18.5204,73.8567
assert len(x.MANVADI)==14 and len(x.YUGADI)==4 and len(x.KALPADI)==7
man=x.select_lunar_rules(2026,lat,lon,tz,x.MANVADI)
assert any(r["title"]=="Brahma Savarni Manvadi" and r["date"]=="2026-01-25" for r in man),man
assert len(x.select_lunar_rules(2026,lat,lon,tz,x.YUGADI))>=3
assert len(x.select_lunar_rules(2026,lat,lon,tz,x.KALPADI))>=5
kr=x.kranti_rows(2026,tz)
assert len(kr)>=20, len(kr)
assert any(r["date"]=="2026-01-13" for r in kr),kr[:3]
assert all("0.5" in r["detail"] for r in kr)
for r in kr:
    start,end=r["detail"].split(" · ")[-1].split(" → ")
    assert datetime.fromisoformat(end)>datetime.fromisoformat(start)
snap=x.published_snapshot(date(2026,10,6),lat,lon,tz)
assert snap and "Publication-ready" in snap[0]["title"]
print("Panchang semantic completion fixture passed")
