#!/usr/bin/env python3
import os,sys
from datetime import datetime
from zoneinfo import ZoneInfo
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)));sys.path.insert(0,os.path.join(ROOT,"python"))
import jyotish_secondary as x
tz=ZoneInfo("Asia/Kolkata");m=datetime(1990,1,1,12,0,tzinfo=tz);lat,lon=18.5204,73.8567
pr=x.prashna(m,lat,lon);assert len(pr)>=11
g=x.gemstone(m,lat,lon)
assert any(r["title"].startswith("Life stone") for r in g),g
assert any("not an automatic prescription" in r.get("detail","") for r in g),g
assert any(r["title"]=="Naming syllable" for r in x.baby(m))
ini=x.initials("Aarav");assert any("Mesha" in r["meta"] for r in ini if r["title"]=="Possible Rashis"),ini
assert x.birth_bird("Ashwini","Shukla Paksha")=="Vulture"
assert x.birth_bird("Ashwini","Krishna Paksha")=="Peacock"
assert x.birth_bird("Uttara Phalguni","Shukla Paksha")=="Crow"
assert x.birth_bird("Uttara Phalguni","Krishna Paksha")=="Crow"
pv=x.prashnavali(m,lat,lon)
assert not any(r.get("meta") in ("Favourable","Mixed","Cautious") for r in pv)
assert any(r["title"]=="Method note" for r in pv)
s=x.sahasra(datetime(2000,1,1,12,0,tzinfo=tz))
target=next(r for r in s if r["title"]=="1000th full Moon")
assert target["meta"].startswith("2080-10-28"),target
assert any(r["title"]=="First full Moon after birth" for r in s)
assert any(r["title"]=="Ishtakala" for r in x.vedic_time(m,lat,lon,tz))
print("Secondary Jyotish semantic fixture passed")
