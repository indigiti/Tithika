#!/usr/bin/env python3
import json, subprocess, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
ENGINE=ROOT/"python"/"kundali.py"

def run(node_model):
    payload={
        "lat":18.5204,"lon":73.8567,"city":"Pune, India",
        "timezone":"Asia/Kolkata","date":"2026-10-06","time":"07:40:31",
        "node_model":node_model
    }
    p=subprocess.run([sys.executable,str(ENGINE)],input=json.dumps(payload),text=True,capture_output=True,cwd=ROOT)
    if p.returncode!=0:
        raise SystemExit(p.stdout+"\n"+p.stderr)
    data=json.loads(p.stdout)
    assert data["ok"] is True, data
    return data

mean=run("mean")
assert mean["lagna"]["rashi"]=="Tula"
assert mean["panchang"]["nakshatra"]=="Ashlesha"
assert mean["panchang"]["moon_rashi"]=="Karka"
assert len(mean["d1"]["cells"])==12
assert len(mean["d9"]["cells"])==12
assert sorted(cell["house"] for cell in mean["d1"]["cells"])==list(range(1,13))
moon=next(x for x in mean["d1"]["placements"] if x["name"]=="Moon")
assert moon["rashi"]=="Karka"
assert moon["house"]==10
rahu=next(x for x in mean["d1"]["placements"] if x["name"]=="Rahu")
assert rahu["rashi"]=="Kumbha"
assert mean["engine"]["house_system"]=="whole-sign"

true=run("true")
trahu=next(x for x in true["d1"]["placements"] if x["name"]=="Rahu")
assert abs(trahu["longitude"]-304.87) <= 0.25, trahu
assert true["engine"]["rahu_ketu"]=="true nodes"

print("Kundali fixture OK: D1 whole-sign houses, D9 and mean/true nodes")
