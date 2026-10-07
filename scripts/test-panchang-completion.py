#!/usr/bin/env python3
import os,sys
from datetime import date
from zoneinfo import ZoneInfo
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)));sys.path.insert(0,os.path.join(ROOT,"python"))
import panchang_completion as x
tz=ZoneInfo("Asia/Kolkata");lat,lon=18.5204,73.8567
assert len(x.MANVADI)==14 and len(x.YUGADI)==4 and len(x.KALPADI)==7
man=x.select_lunar_rules(2026,lat,lon,tz,x.MANVADI)
yug=x.select_lunar_rules(2026,lat,lon,tz,x.YUGADI)
kal=x.select_lunar_rules(2026,lat,lon,tz,x.KALPADI)
by_man={r["title"]:r["date"] for r in man}
by_yug={r["title"]:r["date"] for r in yug}
by_kal={r["title"]:r["date"] for r in kal}
assert by_man["Brahma Savarni Manvadi"]=="2026-01-25",by_man
assert by_man["Daksha Savarni Manvadi"]=="2026-10-20",by_man
assert by_yug=={
 "Dwapara Yuga Diwas":"2026-02-17","Treta Yuga Diwas":"2026-04-19",
 "Kali Yuga Diwas":"2026-10-08","Satya Yuga Diwas":"2026-11-18"
},by_yug
assert by_kal["Varaha Kalpadi"]=="2026-01-30",by_kal
assert by_kal["Kurma Kalpadi First"]=="2026-03-19",by_kal
assert by_kal["Savitri Kalpadi"]=="2026-11-16",by_kal
snap=x.published_snapshot(date(2026,10,6),lat,lon,tz)
assert snap and "Publication-ready" in snap[0]["title"]
# Kranti geometry must use real lunar latitude, so the helper should accept it.
assert abs(x.declination(90,5)-x.declination(90,0))>1.0
print("Panchang completion benchmarks passed")
