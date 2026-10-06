#!/usr/bin/env python3
import json, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
ENGINE=ROOT/"python"/"doshas.py"
BASE={"lat":18.5204,"lon":73.8567,"city":"Pune, India","timezone":"Asia/Kolkata","date":"2026-10-06","time":"07:40:31","as_of":"2026-10-06T07:40:31+05:30"}
def run(mode):
 p=subprocess.run([sys.executable,str(ENGINE)],input=json.dumps(dict(BASE,mode=mode)),text=True,capture_output=True,cwd=ROOT)
 if p.returncode!=0: raise SystemExit(p.stdout+"\n"+p.stderr)
 d=json.loads(p.stdout);assert d["ok"] is True,d;return d["result"]
m=run("mangal")
checks={x["reference"]:x for x in m["checks"]}
assert m["present"] is True
assert checks["Lagna"]["mars_house"]==10 and checks["Lagna"]["afflicted"] is False
assert checks["Moon"]["mars_house"]==1 and checks["Moon"]["afflicted"] is True
assert checks["Venus"]["mars_house"]==10 and checks["Venus"]["afflicted"] is False
k=run("kalasarpa")
assert k["present"] is False
assert k["partial_considered"] is False
s=run("sade-sati")
assert s["moon_rashi"]=="Karka"
assert s["current"] is None
assert s["periods"]
for row in s["periods"]:
 assert row["phase"] in ("rising","peak","setting")
 assert row["start"] < row["end"]
print("Dosha fixture OK: Mangal, Kalasarpa and Sade Sati structure")
