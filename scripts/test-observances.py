#!/usr/bin/env python3
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENGINE = ROOT / "python" / "observances.py"
BASE = {
    "lat": 19.0760,
    "lon": 72.8777,
    "city": "Mumbai, India",
    "timezone": "Asia/Kolkata",
    "date": "2026-10-06",
    "hour24": False,
}

def run(kind):
    payload = dict(BASE, kind=kind)
    proc = subprocess.run(
        [sys.executable, str(ENGINE)],
        input=json.dumps(payload),
        text=True,
        capture_output=True,
        cwd=ROOT,
    )
    if proc.returncode != 0:
        raise SystemExit(f"{kind} engine failed: {proc.stdout}\n{proc.stderr}")
    data = json.loads(proc.stdout)
    assert data["ok"] is True, data
    assert data["kind"] == kind
    assert data["engine"]["status"] == "rule-selected"
    assert data["events"], data
    return data

def within(actual, expected, tolerance_minutes=7):
    a = datetime.fromisoformat(actual)
    e = datetime.fromisoformat(expected)
    return abs((a - e).total_seconds()) <= tolerance_minutes * 60

# Pradosh: Mumbai benchmark publishes Jan 1, 2026 from 18:12 to 20:48.
pr = run("pradosh")
assert 23 <= len(pr["events"]) <= 25
jan1 = next(row for row in pr["events"] if row["date"] == "2026-01-01")
assert jan1["name"] == "Guru Pradosh Vrat"
assert within(jan1["puja"]["start"], "2026-01-01T18:12:00+05:30")
assert within(jan1["puja"]["end"], "2026-01-01T20:48:00+05:30", 8)

# Sankashti: Mumbai daily Panchang publishes Dec 26 with moonrise 20:52.
sa = run("sankashti")
assert 11 <= len(sa["events"]) <= 13
dec26 = next(row for row in sa["events"] if row["date"] == "2026-12-26")
assert within(dec26["moonrise"], "2026-12-26T20:52:00+05:30", 8)
assert dec26["paksha"] == "Krishna Paksha"

# Masik Shivaratri: Mumbai benchmark publishes Feb 15 as Maha Shivaratri,
# with Nishita 00:28-01:17 on Feb 16.
sh = run("shivaratri")
assert 11 <= len(sh["events"]) <= 13
feb15 = next(row for row in sh["events"] if row["date"] == "2026-02-15")
assert feb15["maha_shivaratri"] is True
assert feb15["name"] == "Maha Shivaratri"
assert within(feb15["nishita"]["start"], "2026-02-16T00:28:00+05:30", 7)
assert within(feb15["nishita"]["end"], "2026-02-16T01:17:00+05:30", 7)

oct8 = next(row for row in sh["events"] if row["date"] == "2026-10-08")
assert within(oct8["nishita"]["start"], "2026-10-09T00:02:00+05:30", 7)
assert within(oct8["nishita"]["end"], "2026-10-09T00:50:00+05:30", 7)

print("Observance fixtures OK: Pradosh, Sankashti and Masik Shivaratri for Mumbai 2026")
