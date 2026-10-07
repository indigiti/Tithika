#!/usr/bin/env python3
import os,sys
from datetime import date,datetime,timedelta
from zoneinfo import ZoneInfo
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)));sys.path.insert(0,os.path.join(ROOT,"python"))
import panchang_completion as x
tz=ZoneInfo("Asia/Kolkata");lat,lon=18.5204,73.8567
assert len(x.MANVADI)==14 and len(x.YUGADI)==4 and len(x.KALPADI)==7
man=x.select_lunar_rules(2026,lat,lon,tz,x.MANVADI)
assert any(r["title"]=="Brahma Savarni Manvadi" and r["date"]=="2026-01-25" for r in man),man[:3]
yug=x.select_lunar_rules(2026,lat,lon,tz,x.YUGADI);kal=x.select_lunar_rules(2026,lat,lon,tz,x.KALPADI)
assert len(yug)>=3 and len(kal)>=5
rows=x.kranti_rows(2026,tz);assert rows
first=rows[0];assert first["title"]=="Vyatipata Yoga",first
a=datetime.fromisoformat(first["start"]);b=datetime.fromisoformat(first["end"])
ea=datetime(2026,1,13,0,15,tzinfo=tz);eb=datetime(2026,1,13,6,28,tzinfo=tz)
assert abs((a-ea).total_seconds())<20*60,(a,ea)
assert abs((b-eb).total_seconds())<20*60,(b,eb)
assert first["profile"]=="true-declination-30-arcmin"
snap=x.published_snapshot(date(2026,10,6),lat,lon,tz);assert snap and "Publication-ready" in snap[0]["title"]
print("Panchang completion truth fixture passed")
