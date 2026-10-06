#!/usr/bin/env python3
import os,sys
from datetime import datetime
from zoneinfo import ZoneInfo
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)));sys.path.insert(0,os.path.join(ROOT,"python"))
import jyotish_secondary as x
tz=ZoneInfo("Asia/Kolkata");m=datetime(1990,1,1,12,0,tzinfo=tz);lat,lon=18.5204,73.8567
assert len(x.prashna(m,lat,lon))==4
assert any(r["title"]=="Traditional gemstone" for r in x.gemstone(m,lat,lon))
assert any(r["title"]=="Naming syllable" for r in x.baby(m))
assert any(r["title"]=="1000th lunar-cycle estimate" for r in x.sahasra(m))
assert any(r["title"]=="Ishtakala" for r in x.vedic_time(m,lat,lon,tz))
assert any(r["title"]=="Next matching Pitru-Paksha Tithi" for r in x.shraddha_tithi(m,lat,lon,tz))
print("Secondary Jyotish fixture passed")
