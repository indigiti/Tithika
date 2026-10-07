#!/usr/bin/env python3
import os,sys
from datetime import datetime
from zoneinfo import ZoneInfo
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)));sys.path.insert(0,os.path.join(ROOT,"python"))
import panchang,planetary,jyotish_secondary as x
tz=ZoneInfo("Asia/Kolkata");m=datetime(1990,1,1,12,0,tzinfo=tz);lat,lon=18.5204,73.8567
pr=x.prashna(m,lat,lon);assert len(pr)==16 and any(r["title"]=="House 12" for r in pr)
gem=x.gemstone(m,lat,lon);assert any("Prescription status"==r["title"] for r in gem)
assert any("Rudraksha" in r["title"] for r in x.rudraksha(m,lat,lon))
assert any(r["title"]=="Naming syllable" for r in x.baby(m))
s=x.sahasra(m);full=datetime.fromisoformat(next(r["meta"] for r in s if r["title"]=="1000th full Moon"))
sun,moon,_=panchang.tropical_longitudes(full);elong=(moon-sun)%360
assert abs(elong-180)<0.01,elong
assert any(r["title"]=="Ishtakala" for r in x.vedic_time(m,lat,lon,tz))
assert any(r["title"]=="Next matching Pitru-Paksha Tithi" for r in x.shraddha_tithi(m,lat,lon,tz))
pv=x.prashnavali(m,lat,lon);assert any(r["title"]=="Result policy" and "No synthetic" in r["meta"] for r in pv)
print("Secondary Jyotish semantic fixture passed")
