#!/usr/bin/env python3
import os
import sys
from datetime import date
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"python"))

import panchang

tz=ZoneInfo("Asia/Kolkata")
d=date(2026,10,8)
lat,lon=18.5204,73.8567

os.environ["TITHIKA_ELEVATION_METERS"]="0"
assert panchang.observer_elevation()==0.0
sea=panchang.rise_set(
    d,lat,lon,tz,
    panchang.astronomy.Body.Sun,
    panchang.astronomy.Direction.Rise,
)
assert sea is not None

os.environ["TITHIKA_ELEVATION_METERS"]="3000"
assert panchang.observer_elevation()==3000.0
high=panchang.rise_set(
    d,lat,lon,tz,
    panchang.astronomy.Body.Sun,
    panchang.astronomy.Direction.Rise,
)
assert high is not None
assert high != sea,(sea,high)

os.environ["TITHIKA_ELEVATION_METERS"]="12000"
assert panchang.observer_elevation()==9000.0
os.environ["TITHIKA_ELEVATION_METERS"]="-900"
assert panchang.observer_elevation()==-500.0

eclipses=(ROOT/"python"/"eclipses.py").read_text()
assert "panchang.observer_elevation()" in eclipses

print("Elevation fixture passed: shared observer height changes rise/set geometry and is clamped safely")
