#!/usr/bin/env python3
import os,sys
from datetime import date
from zoneinfo import ZoneInfo
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)));sys.path.insert(0,os.path.join(ROOT,"python"))
import muhurat_completion as x

tz=ZoneInfo("Asia/Kolkata");lat,lon=18.5204,73.8567;d=date(2026,10,6)

g=x.gowri(d,lat,lon,tz)
assert sum(len(s["items"]) for s in g)==16

p=x.pachchakkhan(d,lat,lon,tz)[0]["items"]
assert len(p)==10
assert p[0]["title"]=="Navkarshi"
assert p[1]["title"]=="Porshi"

do=x.do_ghati(d,lat,lon,tz)[0]["items"]
assert len(do)==30
expected=["Rudra","Uraga","Mitra","Pitara","Vasu","Ambu","Vishwedeva","Vidhi","Brahma","Indra","Indragni","Daitya","Varuna","Aryama","Bhaga","Ishwara","Ajaikapada","Ahirbudhnya","Pusha","Ashwini","Yama","Agni","Brahma","Chandra","Aditi","Brihaspati","Vishnu","Surya","Tvashta","Samirana"]
assert [r["title"] for r in do]==expected

# Pancha Pakshi remains intentionally gated: only the verified 5+5 solar
# Yama framework may be emitted until a source-locked bird/activity table exists.
pakshi=x.pakshi_sections(d,lat,lon,tz)
assert sum(len(s["items"]) for s in pakshi)==10
assert all("Yama" in r["title"] for s in pakshi for r in s["items"])
assert all("quality-gated" in r["detail"] for s in pakshi for r in s["items"])

assert len(x.shubha_dates(2026,lat,lon,tz)[0]["items"])>0
print("Muhurat completion semantic fixture passed")
