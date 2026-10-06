#!/usr/bin/env python3
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENGINE = ROOT / "python" / "mahadwadashi.py"
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
    raise SystemExit(f"Mahadwadashi engine failed: {proc.stdout}\n{proc.stderr}")

data = json.loads(proc.stdout)
assert data["ok"] is True, data
assert data["year"] == 2026
assert data["engine"]["status"] == "candidate-classification"
assert data["events"], data

by_date = {row["date"]: row for row in data["events"]}

# Maharashtra 2026 benchmark structure:
# May 27 Unmilini, Aug 24 Vanjuli, Nov 21 Trisparsha.
assert "2026-05-27" in by_date, sorted(by_date)
assert "Unmilini Mahadwadashi" in by_date["2026-05-27"]["yogas"], by_date["2026-05-27"]

assert "2026-08-24" in by_date, sorted(by_date)
assert "Vanjuli Mahadwadashi" in by_date["2026-08-24"]["yogas"], by_date["2026-08-24"]

assert "2026-11-21" in by_date, sorted(by_date)
assert "Trisparsha Mahadwadashi" in by_date["2026-11-21"]["yogas"], by_date["2026-11-21"]

# Every emitted event must carry machine-auditable rule evidence.
for row in data["events"]:
    assert row["yogas"]
    assert row["evidence"]
    assert row["dwadashi_start"] < row["dwadashi_end"]

print("Mahadwadashi fixture OK: 2026 Maharashtra structural yogas detected")
