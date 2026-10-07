#!/usr/bin/env python3
import os,sys
from datetime import datetime
from zoneinfo import ZoneInfo
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)));sys.path.insert(0,os.path.join(ROOT,"python"))
import jyotish_secondary as x

tz=ZoneInfo("Asia/Kolkata");m=datetime(1990,1,1,12,0,tzinfo=tz);lat,lon=18.5204,73.8567

p=x.prashna(m,lat,lon)
assert len(p)==13,p
assert p[0]["title"]=="Prashna Lagna"
grahas={"Sun","Moon","Mars","Mercury","Jupiter","Venus","Saturn","Rahu","Ketu"}
assert grahas.issubset({r["title"] for r in p})

assert any(r["title"]=="Traditional gemstone" for r in x.gemstone(m,lat,lon))
assert any(r["title"]=="Naming syllable" for r in x.baby(m))
assert any(r["title"]=="1000th lunar-cycle estimate" for r in x.sahasra(m))
assert any(r["title"]=="Ishtakala" for r in x.vedic_time(m,lat,lon,tz))
assert any(r["title"]=="Next matching Pitru-Paksha Tithi" for r in x.shraddha_tithi(m,lat,lon,tz))

pak=x.pancha_pakshi(m)
assert pak[0]["meta"]=="Quality-gated"
assert not any(r["title"]=="Birth bird" for r in pak)

pv=x.prashnavali(m,lat,lon)
assert pv[0]["meta"]=="Quality-gated"
assert not any(r["meta"] in ("Favourable","Mixed","Cautious") for r in pv)
print("Secondary Jyotish semantic fixture passed")
