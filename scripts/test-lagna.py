#!/usr/bin/env python3
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENGINE = ROOT / "python" / "lagna.py"

BASE = {
    "lat": 19.0760,
    "lon": 72.8777,
    "city": "Mumbai, India",
    "timezone": "Asia/Kolkata",
    "hour24": False,
}

def run(date_text, instant=None):
    payload = dict(BASE, date=date_text)
    if instant:
        payload["datetime"] = instant
    proc = subprocess.run(
        [sys.executable, str(ENGINE)],
        input=json.dumps(payload),
        text=True,
        capture_output=True,
        cwd=ROOT,
    )
    if proc.returncode != 0:
        raise SystemExit(f"Lagna engine failed: {proc.stdout}\n{proc.stderr}")
    data = json.loads(proc.stdout)
    assert data["ok"] is True, data
    assert data["engine"]["ayanamsha"] == "Lahiri / Chitrapaksha"
    return data

def within(actual, expected, tolerance_minutes=6):
    return abs(
        (datetime.fromisoformat(actual) - datetime.fromisoformat(expected)).total_seconds()
    ) <= tolerance_minutes * 60

nov8 = run("2026-11-08", "2026-11-08T19:00:00+05:30")
assert nov8["instant"]["lagna"] == "Vrishabha", nov8["instant"]
vrishabha = next(row for row in nov8["timeline"] if row["lagna"] == "Vrishabha")
assert within(vrishabha["start"], "2026-11-08T18:27:00+05:30")
assert within(vrishabha["end"], "2026-11-08T20:27:00+05:30")
assert 100 <= vrishabha["duration_minutes"] <= 140

nov9 = run("2026-11-09", "2026-11-09T01:30:00+05:30")
assert nov9["instant"]["lagna"] == "Simha", nov9["instant"]
simha = next(row for row in nov9["timeline"] if row["lagna"] == "Simha")
assert within(simha["start"], "2026-11-09T00:53:00+05:30")
assert within(simha["end"], "2026-11-09T03:01:00+05:30")

# No fake two-hour assumption: at least two signs in a day should have visibly
# different durations.
durations = [round(row["duration_minutes"], 1) for row in nov8["timeline"] if row["duration_minutes"] > 20]
assert len(set(durations)) >= 3, durations

print("Lagna fixture OK: Mumbai 2026 Diwali Vrishabha and Simha intervals")
