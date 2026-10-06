#!/usr/bin/env python3
import os
import sys
from datetime import datetime
from zoneinfo import ZoneInfo

ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,os.path.join(ROOT,"python"))

import specialized_muhurat

tz=ZoneInfo("Asia/Kolkata")
assert set(specialized_muhurat.PROFILES)=={
    "vivah","griha-pravesh","property","vehicle",
    "namakarana","annaprashana","mundana",
}
for key,p in specialized_muhurat.PROFILES.items():
    assert p["allowed_weekdays"],key
    assert p["minimum_minutes"]>=5,key
    assert p.get("allowed_nakshatras"),key

# Benchmark-structure month: Maharashtra/Pune, June 2026.
selected=datetime(2026,6,1).date()
griha=specialized_muhurat.calculate_month(
    "griha-pravesh",selected,18.5204,73.8567,tz,False
)
assert griha["profile"]=="griha-pravesh"
assert len(griha["days"])==30
assert all(row["date"].startswith("2026-06-") for row in griha["days"])

# June 24, 2026 is a known Chitra/Dashami Griha-Pravesh benchmark day.
by={row["date"]:row for row in griha["days"]}
j24=by["2026-06-24"]
assert j24["weekday"]=="Wednesday"
assert j24["eligible"] is True,j24
assert j24["windows"],j24
assert any(
    w["evidence"]["nakshatra"]=="Chitra"
    and w["evidence"]["tithi"]=="Dashami"
    for w in j24["windows"]
),j24

# Sunday/Tuesday are prohibited by this profile.
assert by["2026-06-21"]["eligible"] is False
assert "prohibited-weekday" in by["2026-06-21"]["reasons"]
assert by["2026-06-23"]["eligible"] is False
assert "prohibited-weekday" in by["2026-06-23"]["reasons"]

# Vehicle profile must keep Tuesday/Saturday prohibited.
vehicle=specialized_muhurat.calculate_month(
    "vehicle",selected,19.0760,72.8777,tz,False
)
vby={row["date"]:row for row in vehicle["days"]}
assert "prohibited-weekday" in vby["2026-06-23"]["reasons"]
assert "prohibited-weekday" in vby["2026-06-27"]["reasons"]
assert vby["2026-06-17"]["eligible"] is True,vby["2026-06-17"]

for result in (griha,vehicle):
    for day in result["auspicious_days"]:
        for w in day["windows"]:
            assert w["start"] < w["end"]
            assert w["duration_minutes"] >= result["rule_profile"]["minimum_minutes"]
            assert w["evidence"]["karana"] != "Vishti"

print("Specialized Muhurat profile fixture passed")
