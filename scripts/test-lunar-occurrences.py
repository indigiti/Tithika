#!/usr/bin/env python3
import json
import subprocess
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
ENGINE=ROOT/"python"/"lunar_occurrences.py"
BASE={
    "lat":19.0760,
    "lon":72.8777,
    "city":"Mumbai, India",
    "timezone":"Asia/Kolkata",
    "date":"2026-10-06",
    "hour24":False
}

def run(kind):
    payload=dict(BASE,kind=kind)
    proc=subprocess.run([sys.executable,str(ENGINE)],input=json.dumps(payload),text=True,capture_output=True,cwd=ROOT)
    if proc.returncode!=0:
        raise SystemExit(f"{kind} engine failed: {proc.stdout}\n{proc.stderr}")
    data=json.loads(proc.stdout)
    assert data["ok"] is True
    assert data["kind"] == kind
    assert data["events"]
    return data

ek=run("ekadashi")
assert ek["observance_status"]=="candidate-only"
assert any(
    c["date"]=="2026-10-06"
    for event in ek["events"]
    for c in event.get("sunrise_candidates",[])
), "Expected Oct 6, 2026 Ekadashi sunrise candidate"

pu=run("purnima")
assert all(event["tithi_id"]==14 for event in pu["events"])

am=run("amavasya")
assert all(event["tithi_id"]==29 for event in am["events"])

print("Lunar occurrence fixtures OK: Mumbai 2026")
