#!/usr/bin/env python3
import os
import sys
from datetime import datetime
from zoneinfo import ZoneInfo

ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,os.path.join(ROOT,"python"))

import muhurat_rules

# Pure interval subtraction fixture.
a=datetime.fromisoformat("2026-10-06T06:00:00+05:30")
b=datetime.fromisoformat("2026-10-06T18:00:00+05:30")
blocks=[
    (datetime.fromisoformat("2026-10-06T08:00:00+05:30"),
     datetime.fromisoformat("2026-10-06T09:00:00+05:30"),"A"),
    (datetime.fromisoformat("2026-10-06T12:00:00+05:30"),
     datetime.fromisoformat("2026-10-06T13:30:00+05:30"),"B"),
]
clean=muhurat_rules.subtract_intervals(a,b,blocks)
assert clean==[
    (datetime.fromisoformat("2026-10-06T06:00:00+05:30"),
     datetime.fromisoformat("2026-10-06T08:00:00+05:30")),
    (datetime.fromisoformat("2026-10-06T09:00:00+05:30"),
     datetime.fromisoformat("2026-10-06T12:00:00+05:30")),
    (datetime.fromisoformat("2026-10-06T13:30:00+05:30"),
     datetime.fromisoformat("2026-10-06T18:00:00+05:30")),
]

tz=ZoneInfo("Asia/Kolkata")
profile=muhurat_rules.normalized_profile({})
day=muhurat_rules.calculate_day(
    datetime(2026,10,6).date(),19.0760,72.8777,tz,profile,False
)
assert day["windows"],day
assert day["blocked_intervals"],day
assert all(row["start"] < row["end"] for row in day["windows"])
assert all(row["panchang"]["karana"]!="Vishti" for row in day["accepted_windows"])

# No accepted window may overlap any merged common exclusion.
for row in day["accepted_windows"]:
    x0=datetime.fromisoformat(row["start"])
    x1=datetime.fromisoformat(row["end"])
    for block in day["blocked_intervals"]:
        b0=datetime.fromisoformat(block["start"])
        b1=datetime.fromisoformat(block["end"])
        assert muhurat_rules.overlap(x0,x1,b0,b1) is None,(row,block)

# Custom profiles must reject with explicit evidence rather than silently remove data.
blocked=muhurat_rules.normalized_profile({
    "name":"blocked-weekday-test",
    "blocked_weekdays":["Tuesday"],
})
blocked_day=muhurat_rules.calculate_day(
    datetime(2026,10,6).date(),19.0760,72.8777,tz,blocked,False
)
assert blocked_day["windows"]
assert not blocked_day["accepted_windows"]
assert all(
    any("weekday Tuesday is blocked" in reason for reason in row["reasons"])
    for row in blocked_day["windows"]
)

print("Shared Muhurat rule engine fixture passed")
