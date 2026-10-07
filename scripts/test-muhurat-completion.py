#!/usr/bin/env python3
import os,sys
from datetime import date
from zoneinfo import ZoneInfo
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)));sys.path.insert(0,os.path.join(ROOT,"python"))
import muhurat_completion as x
tz=ZoneInfo("Asia/Kolkata");lat,lon=18.5204,73.8567;d=date(2026,10,6)
g=x.gowri(d,lat,lon,tz);assert sum(len(s["items"]) for s in g)==16
assert [r["title"] for r in g[0]["items"]][:4]==["Rogam","Laabam","Dhanam","Sugam"]
assert len(x.pachchakkhan(d,lat,lon,tz)[0]["items"])==10
dg=x.do_ghati(d,lat,lon,tz)[0]["items"];assert len(dg)==30
assert [r["title"] for r in dg[:10]]==["Rudra","Uraga","Mitra","Pitara","Vasu","Ambu","Vishwedeva","Vidhi","Brahma","Indra"]
assert [r["title"] for r in dg[-5:]]==["Brihaspati","Vishnu","Surya","Tvashta","Samirana"]
pp=x.pakshi_sections(d,lat,lon,tz)
assert sum(len(s["items"]) for s in pp)==50
# 2026-10-06 is Tuesday / Krishna Paksha: Group A, Yama 1.
day=pp[0]["items"][:5]
assert [(r["title"].split(" · ")[0],r["title"].split(" · ")[1]) for r in day]==[
 ("Vulture","Walking"),("Owl","Dying"),("Crow","Eating"),("Cock","Ruling"),("Peacock","Sleeping")
],day
# Every bird shares one Yama boundary; no fabricated five-way subperiod split.
assert len({r["time"] for r in day})==1
assert len(x.shubha_dates(2026,lat,lon,tz)[0]["items"])>0
print("Muhurat completion benchmarks passed")
