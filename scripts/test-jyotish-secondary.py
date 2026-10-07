#!/usr/bin/env python3
import os,sys
from datetime import datetime
from zoneinfo import ZoneInfo
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)));sys.path.insert(0,os.path.join(ROOT,"python"))
import jyotish_secondary as x
tz=ZoneInfo("Asia/Kolkata");m=datetime(1990,1,1,12,0,tzinfo=tz);lat,lon=18.5204,73.8567
pr=x.prashna(m,lat,lon);assert len(pr)>=11
assert any(r["title"]=="Traditional gemstone" for r in x.gemstone(m,lat,lon))
assert any(r["title"]=="Naming syllable" for r in x.baby(m))
ini=x.initials("Aarav");assert any("Mesha" in r["meta"] for r in ini if r["title"]=="Possible Rashis"),ini
pv=x.prashnavali(m,lat,lon)
assert not any(r.get("meta") in ("Favourable","Mixed","Cautious") for r in pv)
assert any(r["title"]=="Method note" for r in pv)
assert any(r["title"]=="1000th lunar-cycle estimate" for r in x.sahasra(m))
assert any(r["title"]=="Ishtakala" for r in x.vedic_time(m,lat,lon,tz))
print("Secondary Jyotish semantic fixture passed")
