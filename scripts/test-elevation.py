#!/usr/bin/env python3
import os
import sys
from datetime import date
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"python"))

import panchang
import choghadiya

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

os.environ["TITHIKA_ELEVATION_METERS"]="0"
chog_sea=choghadiya.solar_event(d,lat,lon,tz,True)
os.environ["TITHIKA_ELEVATION_METERS"]="3000"
chog_high=choghadiya.solar_event(d,lat,lon,tz,True)
assert chog_sea is not None and chog_high is not None
assert chog_high != chog_sea,(chog_sea,chog_high)

os.environ["TITHIKA_ELEVATION_METERS"]="12000"
assert panchang.observer_elevation()==9000.0
os.environ["TITHIKA_ELEVATION_METERS"]="-900"
assert panchang.observer_elevation()==-500.0

eclipses=(ROOT/"python"/"eclipses.py").read_text()
assert "panchang.observer_elevation()" in eclipses

print("Elevation fixture passed: shared observer height changes Panchang and Choghadiya rise/set geometry and is clamped safely")
