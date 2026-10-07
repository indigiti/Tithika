#!/usr/bin/env python3
import os,sys
from datetime import date,datetime
from zoneinfo import ZoneInfo
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)));sys.path.insert(0,os.path.join(ROOT,"python"))
import muhurat_completion as x
tz=ZoneInfo("Asia/Kolkata");lat,lon=18.5204,73.8567;d=date(2026,10,7)
g=x.gowri(d,lat,lon,tz);assert sum(len(s["items"]) for s in g)==16
assert len(x.pachchakkhan(d,lat,lon,tz)[0]["items"])==10
do=x.do_ghati(d,lat,lon,tz)[0]["items"]
assert len(do)==30
assert [r["title"] for r in do[:12]]==["Rudra","Uraga","Mitra","Pitara","Vasu","Ambu","Vishwedeva","Vidhi","Brahma","Indra","Indragni","Daitya"]
assert do[-3]["title"]=="Surya" and do[-1]["title"]=="Samirana"
pp=x.pakshi_sections(d,lat,lon,tz)
assert sum(len(s["items"]) for s in pp)==50
# Unequal Pancha-Pakshi subperiods are essential; equal fifths are invalid.
first=pp[0]["items"][:5]
def mins(r):
    a,b=r["time"].split(" – ")
    ta=datetime.strptime(a,"%I:%M %p");tb=datetime.strptime(b,"%I:%M %p")
    if tb<=ta: tb=tb.replace(day=ta.day+1)
    return (tb-ta).total_seconds()/60
assert len({round(mins(r)) for r in first})>=4,first
assert len(x.shubha_dates(2026,lat,lon,tz)[0]["items"])>0
print("Muhurat semantic completion fixture passed")
