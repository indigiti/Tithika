#!/usr/bin/env python3
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENGINE = ROOT / "python" / "panchang.py"

payload = {
    "lat": 19.0760,
    "lon": 72.8777,
    "city": "Mumbai, India",
    "timezone": "Asia/Kolkata",
    "date": "2026-10-06",
    "hour24": False
}

proc = subprocess.run(
    [sys.executable, str(ENGINE)],
    input=json.dumps(payload),
    text=True,
    capture_output=True,
    cwd=ROOT
)
if proc.returncode != 0:
    raise SystemExit(f"Engine failed: {proc.stdout}\n{proc.stderr}")

data = json.loads(proc.stdout)
assert data["ok"] is True
assert data["sunrise_state"]["tithi"] == "Ekadashi"
assert data["sunrise_state"]["paksha"] == "Krishna Paksha"
assert data["sunrise_state"]["nakshatra"] == "Ashlesha"
assert data["sunrise_state"]["yoga"] == "Siddha"
assert data["sunrise_state"]["karana"] == "Bava"
assert data["moon_rashi"] == "Karka"
assert data["sun_rashi"] == "Kanya"
assert data["lunar_month"]["amanta"] == "Bhadrapada"
assert data["lunar_month"]["purnimanta"] == "Ashwina"
assert data["moonrise_label"]
assert data["moonset_label"]

def minutes(iso):
    dt = datetime.fromisoformat(iso)
    return dt.hour * 60 + dt.minute + dt.second / 60

def near(actual_iso, expected_minutes, tolerance=3.0):
    actual = minutes(actual_iso)
    # Tithi transition is after midnight, represented naturally as next-day local time.
    return abs(actual - expected_minutes) <= tolerance

assert near(data["nakshatra"][0]["end"], 22*60 + 17, 3), data["nakshatra"][0]
assert near(data["yoga"][0]["end"], 7*60 + 20, 3), data["yoga"][0]
assert near(data["karana"][0]["end"], 13*60 + 19, 3), data["karana"][0]
assert near(data["tithi"][0]["end"], 35, 3), data["tithi"][0]

print("Panchang fixture OK: Mumbai 2026-10-06")
