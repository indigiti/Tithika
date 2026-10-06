#!/usr/bin/env python3
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENGINE = ROOT / "python" / "dwadashi.py"
payload = {
    "lat": 19.0760,
    "lon": 72.8777,
    "city": "Mumbai, India",
    "timezone": "Asia/Kolkata",
    "date": "2026-10-06",
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
    raise SystemExit(f"Dwadashi engine failed: {proc.stdout}\n{proc.stderr}")

data = json.loads(proc.stdout)
assert data["ok"] is True, data
assert data["year"] == 2026
assert data["engine"]["status"] == "rule-selected"
assert 22 <= len(data["events"]) <= 26, len(data["events"])

by_date = {row["date"]: row for row in data["events"]}

oct7 = by_date["2026-10-07"]
assert oct7["name"] == "Krishna Kalki Dwadashi"
assert oct7["paksha"] == "Krishna Paksha"
assert oct7["purnimanta_month"] == "Ashwina"
assert oct7["parana"]["date"] == "2026-10-08"

def within(actual, expected, tolerance_minutes=4):
    return abs(
        (datetime.fromisoformat(actual) - datetime.fromisoformat(expected)).total_seconds()
    ) <= tolerance_minutes * 60

assert within(oct7["tithi_start"], "2026-10-07T00:34:00+05:30")
assert within(oct7["tithi_end"], "2026-10-07T23:16:00+05:30")
assert datetime.fromisoformat(oct7["parana"]["end"]) > datetime.fromisoformat(oct7["parana"]["start"])

may27 = by_date["2026-05-27"]
assert may27["name"].endswith("Ramalakshmana Dwadashi")
assert may27["adhika"] is True

aug24 = by_date["2026-08-24"]
assert aug24["name"] == "Damodara Dwadashi"

nov21 = by_date["2026-11-21"]
assert nov21["name"] == "Yogeshwara Dwadashi"
assert "Garuda Dwadashi" in nov21["aliases"]

for row in data["events"]:
    assert row["selected_overlap_minutes"] > 0
    assert row["tithi_start"] < row["tithi_end"]
    assert row["parana"] is None or row["parana"]["start"] < row["parana"]["end"]

print("Dwadashi fixture OK: Mumbai 2026 observances and ordinary Parana")
