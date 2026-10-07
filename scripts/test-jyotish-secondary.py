#!/usr/bin/env python3
import os,sys
from datetime import datetime
from zoneinfo import ZoneInfo
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)));sys.path.insert(0,os.path.join(ROOT,"python"))
import jyotish_secondary as x
tz=ZoneInfo("Asia/Kolkata");lat,lon=18.5204,73.8567
m=datetime(2026,10,6,12,0,tzinfo=tz)
pr=x.prashna(m,lat,lon);assert len(pr)>=12
assert any(r["title"]=="Lagna-lord gemstone reference" for r in x.gemstone(m,lat,lon))
assert any(r["title"]=="Lagna-lord Rudraksha reference" for r in x.rudraksha(m,lat,lon))
assert any(r["title"]=="Naming syllable" for r in x.baby(m))
bird=x.pancha_pakshi(m);assert bird[0]["meta"]=="Cock",bird
nv=x.prashnavali(m,lat,lon);assert all("Favourable" not in str(r) and "Cautious" not in str(r) for r in nv)
ni=x.initials("Rahul");assert ni[0]["meta"]=="Ra" and "Tula" in ni[1]["meta"],ni
assert any(r["title"]=="Ishtakala" for r in x.vedic_time(m,lat,lon,tz))
print("Secondary Jyotish benchmarks passed")
