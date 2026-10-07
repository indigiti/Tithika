#!/usr/bin/env python3
import os,sys
from datetime import datetime
from zoneinfo import ZoneInfo
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)));sys.path.insert(0,os.path.join(ROOT,"python"))
import jyotish_secondary as x
tz=ZoneInfo("Asia/Kolkata");m=datetime(1990,1,1,12,0,tzinfo=tz);lat,lon=18.5204,73.8567
pr=x.chart_rows(m,lat,lon);assert len(pr)>=12 and pr[0]["title"]=="Prashna Lagna"
gem=x.gemstone(m,lat,lon,tz);assert any("Shadbala" in r["detail"] for r in gem if r["title"]=="Lagna-lord gemstone")
rud=x.rudraksha(m,lat,lon,tz);assert any("Shadbala" in r["detail"] for r in rud if r["title"]=="Lagna-lord Rudraksha")
assert any(r["title"]=="Naming syllable" for r in x.baby(m))
ini=x.initials("Ravi");assert ini[0]["meta"]=="Ra" and ini[1]["title"]=="Possible Rashis"
pv=x.prashnavali(m,lat,lon);joined=" ".join(str(v) for r in pv for v in r.values())
assert "Favourable" not in joined and "Mixed" not in joined and "Cautious" not in joined
bird=x.pancha_pakshi(m);assert bird[0]["meta"] in x.BIRDS
s=x.sahasra(m);assert s[-1]["title"]=="1000th full Moon phase" and "T" in s[-1]["meta"]
assert any(r["title"]=="Ishtakala" for r in x.vedic_time(m,lat,lon,tz))
print("Secondary Jyotish truth fixture passed")
