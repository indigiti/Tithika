#!/usr/bin/env python3
import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime

ROOT=Path(__file__).resolve().parents[1]
ENGINE=ROOT/"python"/"panchang_month.py"
payload={
    "lat":19.0760,
    "lon":72.8777,
    "city":"Mumbai, India",
    "timezone":"Asia/Kolkata",
    "date":"2026-10-06",
    "hour24":False
}
proc=subprocess.run([sys.executable,str(ENGINE)],input=json.dumps(payload),text=True,capture_output=True,cwd=ROOT)
if proc.returncode!=0:
    raise SystemExit(f"Month engine failed: {proc.stdout}\n{proc.stderr}")
data=json.loads(proc.stdout)
assert data["ok"] is True
assert data["year"] == 2026
assert data["month"] == 10
assert data["days_in_month"] == 31
assert data["first_weekday"] == 3  # Thursday, with Monday=0
assert len(data["days"]) == 31
assert data["engine"]["source"] == "shared Daily Panchang astronomy core"
day6=next(row for row in data["days"] if row["day"]==6)
assert day6["available"] is True
assert day6["tithi"] == "Ekadashi"
assert day6["paksha"] == "Krishna Paksha"
assert day6["nakshatra"] == "Ashlesha"
assert day6["yoga"] == "Siddha"
assert day6["karana"] == "Bava"
assert day6["moon_rashi"] == "Karka"

def within(actual, expected, tolerance_minutes=4):
    return abs((datetime.fromisoformat(actual)-datetime.fromisoformat(expected)).total_seconds()) <= tolerance_minutes*60

assert within(day6["tithi_end"], "2026-10-07T00:35:00+05:30")
assert within(day6["nakshatra_end"], "2026-10-06T22:18:00+05:30")
print("Month Panchang fixture OK: Mumbai October 2026")
