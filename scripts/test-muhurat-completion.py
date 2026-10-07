#!/usr/bin/env python3
import os,sys
from datetime import date
from zoneinfo import ZoneInfo
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)));sys.path.insert(0,os.path.join(ROOT,"python"))
import muhurat_completion as x
tz=ZoneInfo("Asia/Kolkata");lat,lon=18.5204,73.8567;d=date(2026,10,7)
g=x.gowri(d,lat,lon,tz);assert sum(len(s["items"]) for s in g)==16
assert len(x.pachchakkhan(d,lat,lon,tz)[0]["items"])==10
dg=x.do_ghati(d,lat,lon,tz)[0]["items"]
assert len(dg)==30
assert [r["title"] for r in dg]==x.MUHURTA_NAMES
assert x.MUHURTA_NAMES[:8]==["Rudra","Uraga","Mitra","Pitara","Vasu","Ambu","Vishwedeva","Vidhi"]
pp=x.pakshi_sections(d,lat,lon,tz,"Peacock")
assert sum(len(s["items"]) for s in pp)==10
assert all("Sūkṣma" in s["note"] for s in pp)
# Krishna Wednesday belongs to the dedicated dark-half Group C profile.
assert all("group C" in r["meta"] for s in pp for r in s["items"])
assert len(x.shubha_dates(2026,lat,lon,tz)[0]["items"])>0
print("Muhurat completion semantic fixture passed")
