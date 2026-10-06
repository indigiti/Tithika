#!/usr/bin/env python3
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENGINE = ROOT / "python" / "festivals.py"
BASE = {
    "lat": 19.0760,
    "lon": 72.8777,
    "city": "Mumbai, India",
    "timezone": "Asia/Kolkata",
    "date": "2026-01-01",
    "hour24": False,
}

def run(kind):
    proc = subprocess.run(
        [sys.executable, str(ENGINE)],
        input=json.dumps(dict(BASE, kind=kind)),
        text=True,
        capture_output=True,
        cwd=ROOT,
    )
    if proc.returncode != 0:
        raise SystemExit(f"{kind} failed: {proc.stdout}\n{proc.stderr}")
    data = json.loads(proc.stdout)
    assert data["ok"] is True, data
    assert data["event"], (kind, data)
    return data["event"]

def within(actual, expected, tolerance_minutes=10):
    a = datetime.fromisoformat(actual)
    e = datetime.fromisoformat(expected)
    return abs((a - e).total_seconds()) <= tolerance_minutes * 60

ganesh = run("ganesh-chaturthi")
assert ganesh["date"] == "2026-09-14", ganesh
assert within(ganesh["puja"]["start"], "2026-09-14T11:20:00+05:30")
assert within(ganesh["puja"]["end"], "2026-09-14T13:48:00+05:30")

rakhi = run("raksha-bandhan")
assert rakhi["date"] == "2026-08-28", rakhi
assert within(rakhi["thread_ceremony"]["end"], "2026-08-28T09:48:00+05:30")
assert rakhi["bhadra_status"] == "clear-at-sunrise"

navratri = run("navratri")
assert navratri["date"] == "2026-10-11", navratri
assert within(navratri["ghatasthapana"]["start"], "2026-10-11T06:31:00+05:30")
assert within(navratri["ghatasthapana"]["end"], "2026-10-11T10:27:00+05:30")

dussehra = run("dussehra")
assert dussehra["date"] == "2026-10-20", dussehra
assert within(dussehra["aparahna"]["start"], "2026-10-20T13:33:00+05:30")
assert within(dussehra["aparahna"]["end"], "2026-10-20T15:53:00+05:30")
assert within(dussehra["vijay_muhurat"]["start"], "2026-10-20T14:19:00+05:30")
assert within(dussehra["vijay_muhurat"]["end"], "2026-10-20T15:06:00+05:30")

holi = run("holi")
assert holi["date"] == "2026-03-02", holi
assert holi["rangwali_holi_date"] == "2026-03-03"
assert within(holi["pradosh"]["start"], "2026-03-02T18:44:00+05:30")
assert within(holi["pradosh"]["end"], "2026-03-02T21:11:00+05:30")

karwa = run("karwa-chauth")
assert karwa["date"] == "2026-10-29", karwa
assert within(karwa["moonrise"], "2026-10-29T21:00:00+05:30", 12)
assert within(karwa["upavasa"]["start"], "2026-10-29T06:37:00+05:30", 10)

diwali = run("diwali")
assert diwali["date"] == "2026-11-08", diwali
assert within(diwali["pradosh"]["start"], "2026-11-08T18:02:00+05:30", 10)
assert within(diwali["pradosh"]["end"], "2026-11-08T20:34:00+05:30", 10)
assert diwali["vrishabha_lagna_status"] == "lagna-engine-pending"

print("Major festival fixtures OK: Mumbai 2026 batch 1")
