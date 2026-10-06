#!/usr/bin/env python3
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENGINE = ROOT / "python" / "planetary.py"
BASE = {
    "timezone": "Asia/Kolkata",
    "date": "2026-10-06",
    "datetime": "2026-10-06T07:40:31+05:30",
}

def run(mode, extra=None):
    payload = dict(BASE, mode=mode)
    if extra:
        payload.update(extra)
    proc = subprocess.run(
        [sys.executable, str(ENGINE)],
        input=json.dumps(payload),
        text=True,
        capture_output=True,
        cwd=ROOT,
    )
    if proc.returncode != 0:
        raise SystemExit(f"{mode} failed: {proc.stdout}\n{proc.stderr}")
    data = json.loads(proc.stdout)
    assert data["ok"] is True, data
    return data

def close(actual, expected, tolerance=0.12):
    return abs(actual - expected) <= tolerance

pos = run("positions")
by = {row["name"]: row for row in pos["planets"]}

# Pune, Oct 6 2026 07:40:31 IST benchmark (Lahiri, mean Rahu/Ketu).
assert close(by["Sun"]["longitude"], 168.6126, 0.08), by["Sun"]
assert close(by["Moon"]["longitude"], 111.5966, 0.10), by["Moon"]
assert close(by["Mars"]["longitude"], 100.3920, 0.10), by["Mars"]
assert close(by["Mercury"]["longitude"], 192.8933, 0.12), by["Mercury"]
assert close(by["Jupiter"]["longitude"], 116.2471, 0.12), by["Jupiter"]
assert close(by["Venus"]["longitude"], 194.1013, 0.12), by["Venus"]
assert close(by["Saturn"]["longitude"], 346.9408, 0.12), by["Saturn"]
assert close(by["Rahu"]["longitude"], 303.2056, 0.18), by["Rahu"]
assert close(by["Ketu"]["longitude"], 123.2056, 0.18), by["Ketu"]
assert by["Venus"]["retrograde"] is True
assert by["Saturn"]["retrograde"] is True
assert by["Mercury"]["retrograde"] is False

retro = run("retrograde", {"date":"2026-01-01","datetime":"2026-01-01T12:00:00+05:30"})
events = retro["events"]

def event(planet, kind, date_prefix):
    return next(
        row for row in events
        if row["planet"] == planet and row["event"] == kind and row["date"].startswith(date_prefix)
    )

def within(actual, expected, minutes=20):
    a = datetime.fromisoformat(actual)
    e = datetime.fromisoformat(expected)
    return abs((a-e).total_seconds()) <= minutes*60

assert within(event("Mercury","retrograde","2026-02-26")["datetime"], "2026-02-26T12:17:00+05:30")
assert within(event("Mercury","direct","2026-03-21")["datetime"], "2026-03-21T01:02:00+05:30")
assert within(event("Mercury","retrograde","2026-06-29")["datetime"], "2026-06-29T23:05:00+05:30")
assert within(event("Mercury","direct","2026-07-24")["datetime"], "2026-07-24T04:27:00+05:30")
assert within(event("Mercury","retrograde","2026-10-24")["datetime"], "2026-10-24T12:41:00+05:30")
assert within(event("Mercury","direct","2026-11-13")["datetime"], "2026-11-13T21:22:00+05:30")
assert within(event("Jupiter","direct","2026-03-11")["datetime"], "2026-03-11T08:58:00+05:30", 30)
assert within(event("Jupiter","retrograde","2026-12-13")["datetime"], "2026-12-13T06:25:00+05:30", 30)

transit = run("transit", {"date":"2026-01-01","datetime":"2026-01-01T12:00:00+05:30"})
assert transit["events"]
assert all(row["from_rashi"] != row["to_rashi"] for row in transit["events"])

comb = run("combustion", {"date":"2026-01-01","datetime":"2026-01-01T12:00:00+05:30"})
assert comb["events"]
assert all(row["profile"] == "classical-angular-separation" for row in comb["events"])

print("Planetary fixture OK: sidereal positions, stations, transits and combustion")
