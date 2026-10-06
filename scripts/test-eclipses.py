#!/usr/bin/env python3
import json, subprocess, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
ENGINE=ROOT/"python"/"eclipses.py"
payload={
    "mode":"all","date":"2026-01-01",
    "lat":19.0760,"lon":72.8777,"city":"Mumbai, India","timezone":"Asia/Kolkata"
}
p=subprocess.run([sys.executable,str(ENGINE)],input=json.dumps(payload),text=True,capture_output=True,cwd=ROOT)
if p.returncode!=0:
    raise SystemExit(p.stdout+"\n"+p.stderr)
data=json.loads(p.stdout)
assert data["ok"] is True, data
events=data["events"]
summary=[(row["type"],row["kind"],row["peak"]["date"]) for row in events]
assert ("solar","Annular","2026-02-17") in summary, summary
assert ("lunar","Total","2026-03-03") in summary, summary
assert ("solar","Total","2026-08-12") in summary, summary
assert ("lunar","Partial","2026-08-28") in summary, summary
assert len([x for x in summary if x[0]=="solar"])==2
assert len([x for x in summary if x[0]=="lunar"])==2
for row in data["lunar"]:
    assert "locally_visible" in row
    assert row["phases"]["peak"] is not None
for row in data["solar_local"]:
    assert row["partial_begin"]["datetime"] < row["partial_end"]["datetime"]
print("Eclipse fixture OK: 2026 global eclipse set and local visibility layer")
