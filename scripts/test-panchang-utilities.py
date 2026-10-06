#!/usr/bin/env python3
import os
import sys
from datetime import datetime
from zoneinfo import ZoneInfo

ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,os.path.join(ROOT,"python"))

import panchang
import panchang_utilities

# Pure arithmetic contracts.
assert panchang_utilities.tara_position(0,1)["position"]==2
assert panchang_utilities.tara_position(0,1)["good"] is True
assert panchang_utilities.tara_position(0,2)["position"]==3
assert panchang_utilities.tara_position(0,2)["good"] is False
assert panchang_utilities.chandra_house(0,0)=={
    "house":1,"good":True,"ashtama_chandra":False
}
assert panchang_utilities.chandra_house(0,7)=={
    "house":8,"good":False,"ashtama_chandra":True
}

tz=ZoneInfo("Asia/Kolkata")
d=datetime(2026,10,6).date()
sunrise,next_sunrise=panchang_utilities.hindu_day(
    d,18.5204,73.8567,tz
)

tara=panchang_utilities.tarabalam(
    sunrise,next_sunrise,"Ashwini",False
)
assert tara
for row in tara:
    assert row["start"]<row["end"]
    assert row["position"] in range(1,10)
    assert row["good"]==(row["position"] in {2,4,6,8,9})
    assert len(row["good_birth_nakshatras"]) in (15,16)

chandra=panchang_utilities.chandrabalam(
    sunrise,next_sunrise,"Mesha",False
)
assert chandra
for row in chandra:
    assert row["start"]<row["end"]
    assert row["house"] in range(1,13)
    assert len(row["good_birth_rashis"])==6

# On 2026-10-06 the Moon begins the Pune Hindu day in Karka.
first=chandra[0]
assert first["current_moon_rashi"]=="Karka",first
assert first["good_birth_rashis"]==[
    "Vrishabha","Karka","Kanya","Tula","Makara","Kumbha"
],first

for row in panchang_utilities.panchak(sunrise,next_sunrise,False):
    mid=datetime.fromisoformat(row["start"]) + (
        datetime.fromisoformat(row["end"])-datetime.fromisoformat(row["start"])
    )/2
    assert panchang.state_at(mid)["moon_longitude"]>=300.0

for row in panchang_utilities.bhadra(sunrise,next_sunrise,False):
    mid=datetime.fromisoformat(row["start"]) + (
        datetime.fromisoformat(row["end"])-datetime.fromisoformat(row["start"])
    )/2
    assert panchang.state_at(mid)["karana"]=="Vishti"

print("Panchang decision utilities fixture passed")
