#!/usr/bin/env python3
import json, subprocess, sys
from datetime import datetime
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
ENGINE=ROOT/"python"/"aspects.py"

def run(mode):
    payload={"mode":mode,"date":"2026-01-01","timezone":"Asia/Kolkata"}
    p=subprocess.run([sys.executable,str(ENGINE)],input=json.dumps(payload),text=True,capture_output=True,cwd=ROOT)
    if p.returncode!=0:
        raise SystemExit(p.stdout+"\n"+p.stderr)
    data=json.loads(p.stdout)
    assert data["ok"] is True, data
    return data

def within(actual, expected, minutes=20):
    a=datetime.fromisoformat(actual)
    e=datetime.fromisoformat(expected)
    return abs((a-e).total_seconds()) <= minutes*60

mutual=run("mutual")
rows=mutual["events"]

def find_pair(a,b,aspect,date):
    return next(
        row for row in rows
        if {row["planet1"],row["planet2"]}=={a,b}
        and row["aspect"]==aspect and row["date"]==date
    )

# Reference planetary-events fixtures for India, 2026.
assert within(find_pair("Mercury","Mars","Square","2026-10-02")["datetime"],"2026-10-02T14:41:00+05:30",25)
assert within(find_pair("Jupiter","Saturn","Trine","2026-09-01")["datetime"],"2026-09-01T03:39:00+05:30",30)
assert within(find_pair("Mars","Saturn","Square","2026-09-01")["datetime"],"2026-09-01T15:25:00+05:30",30)

conj=run("conjunctions")
assert all(row["aspect"]=="Conjunction" for row in conj["events"])

war=run("graha-yuddha")
for row in war["events"]:
    assert row["closest_separation_deg"] <= 1.0
    assert row["rule"]=="same-rashi-within-1-degree-lower-degree-wins"
    assert row["start"] < row["end"]

print("Aspect fixture OK: exact mutual aspects, conjunctions and Graha Yuddha rules")
