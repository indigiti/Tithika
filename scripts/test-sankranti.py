#!/usr/bin/env python3
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENGINE = ROOT / "python" / "sankranti.py"
payload = {
    "lat": 19.0760,
    "lon": 72.8777,
    "city": "Mumbai, India",
    "timezone": "Asia/Kolkata",
    "date": "2026-01-01",
    "hour24": False,
}

proc = subprocess.run(
    [sys.executable, str(ENGINE)],
    input=json.dumps(payload),
    text=True,
    capture_output=True,
    cwd=ROOT,
)
if proc.returncode != 0:
    raise SystemExit(f"Sankranti engine failed: {proc.stdout}\n{proc.stderr}")

data = json.loads(proc.stdout)
assert data["ok"] is True
assert data["year"] == 2026
assert data["engine"]["ayanamsha"] == "Lahiri / Chitrapaksha"
assert data["rule_status"] == "astronomical-ingress"
assert len(data["events"]) == 12

expected = {
    "Makara": "2026-01-14T15:13:00+05:30",
    "Kumbha": "2026-02-13T04:14:00+05:30",
    "Meena": "2026-03-15T01:08:00+05:30",
    "Mesha": "2026-04-14T09:38:00+05:30",
    "Vrishabha": "2026-05-15T06:28:00+05:30",
    "Mithuna": "2026-06-15T12:58:00+05:30",
    "Karka": "2026-07-16T23:44:00+05:30",
    "Simha": "2026-08-17T08:03:00+05:30",
    "Kanya": "2026-09-17T07:58:00+05:30",
    "Tula": "2026-10-17T19:57:00+05:30",
    "Vrishchika": "2026-11-16T19:48:00+05:30",
    "Dhanu": "2026-12-16T10:29:00+05:30",
}

def within(actual, expected_value, tolerance_minutes=8):
    a = datetime.fromisoformat(actual)
    e = datetime.fromisoformat(expected_value)
    return abs((a - e).total_seconds()) <= tolerance_minutes * 60

events = {row["rashi"]: row for row in data["events"]}
assert list(events.keys())[0] == "Makara"
for rashi, expected_value in expected.items():
    assert rashi in events, rashi
    row = events[rashi]
    assert within(row["datetime"], expected_value), (rashi, row["datetime"], expected_value)
    target = (row["rashi_id"] * 30.0) % 360.0
    longitude = row["sun_sidereal_longitude"]
    # At ingress, longitude should be on the target boundary (allow wrap at 0°).
    delta = min(abs(longitude-target), abs((longitude+360)-target), abs(longitude-(target+360)))
    assert delta < 0.001, (rashi, longitude, target)

print("Sankranti fixture OK: 12 Nirayana solar ingresses for 2026")
