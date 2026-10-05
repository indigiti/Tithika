#!/usr/bin/env python3
import json
import subprocess
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
ENGINE=ROOT/"python"/"seasons.py"
payload={
    "lat":19.0760,
    "lon":72.8777,
    "city":"Mumbai, India",
    "timezone":"Asia/Kolkata",
    "date":"2025-01-01"
}
proc=subprocess.run([sys.executable,str(ENGINE)],input=json.dumps(payload),text=True,capture_output=True,cwd=ROOT)
if proc.returncode!=0:
    raise SystemExit(f"Seasons engine failed: {proc.stdout}\n{proc.stderr}")
data=json.loads(proc.stdout)
assert data["ok"] is True
assert data["year"] == 2025
events=data["events"]
assert events["vernal_equinox"]["datetime"].startswith("2025-03-20T14:31")
assert events["summer_solstice"]["datetime"].startswith("2025-06-21T08:12")
assert events["autumnal_equinox"]["datetime"].startswith("2025-09-22T23:49")
assert events["winter_solstice"]["datetime"].startswith("2025-12-21T20:33")
print("Seasons fixture OK: 2025 Asia/Kolkata")
