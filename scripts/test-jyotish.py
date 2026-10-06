#!/usr/bin/env python3
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENGINE = ROOT / "python" / "jyotish.py"
BASE = {
    "lat": 18.5204,
    "lon": 73.8567,
    "city": "Pune, India",
    "timezone": "Asia/Kolkata",
    "date": "2026-10-06",
    "time": "07:40:31",
}

def run(mode):
    proc = subprocess.run(
        [sys.executable, str(ENGINE)],
        input=json.dumps(dict(BASE, mode=mode)),
        text=True,
        capture_output=True,
        cwd=ROOT,
    )
    if proc.returncode != 0:
        raise SystemExit(f"{mode} failed: {proc.stdout}\n{proc.stderr}")
    data = json.loads(proc.stdout)
    assert data["ok"] is True, data
    return data

birthstar = run("birthstar")
assert birthstar["primary"]["value"] == "Ashlesha"
assert birthstar["primary"]["pada"] == 2
assert birthstar["primary"]["rashi"] == "Karka"

janma = run("janma-lagna")
assert janma["primary"]["value"] == "Tula"
assert 4.8 <= janma["primary"]["degree_in_rashi"] <= 6.1

moon = run("moonsign")
assert moon["primary"]["value"] == "Karka"

sun = run("sunsign")
assert sun["primary"]["value"] == "Kanya"

print("Jyotish fixture OK: Pune Birthstar, Janma Rashi, Surya Rashi and Lagna")
