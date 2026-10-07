#!/usr/bin/env python3
import json
import subprocess
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
ENGINE=ROOT/"python"/"home_dashboard.py"
payload={
    "lat":18.5204,"lon":73.8567,"city":"Pune, Maharashtra, India",
    "timezone":"Asia/Kolkata","date":"2026-10-06","hour24":False,
    "tradition":"smarta","horizon_days":21
}
proc=subprocess.run(
    [sys.executable,str(ENGINE)],
    input=json.dumps(payload),text=True,capture_output=True,cwd=ROOT,timeout=180
)
if proc.returncode!=0:
    raise SystemExit(proc.stdout+"\n"+proc.stderr)
data=json.loads(proc.stdout)
assert data["ok"] is True,data
assert data["engine"]["name"]=="tithika-home-dashboard"
assert data["today"]["tithi"]=="Ekadashi",data["today"]
assert data["today"]["nakshatra"]=="Ashlesha",data["today"]
assert data["today"]["amanta_month"]=="Bhadrapada"
assert data["today"]["purnimanta_month"]=="Ashwina"
assert data["choghadiya"]["next_auspicious"] is not None
assert data["preferences"]["tradition"]=="smarta"
assert data["upcoming"],data
assert any(row["kind"]=="sankranti" and row["date"]=="2026-10-17" for row in data["upcoming"]),data["upcoming"]
assert any(row["kind"] in {"ekadashi","pradosh","sankashti"} for row in data["upcoming"])
assert set(data["engine"]["sources"]) >= {"tithika-panchang","tithika-choghadiya","tithika-observances","tithika-planetary"}
print("Home dashboard fixture OK: Pune 2026-10-06 daily state + upcoming aggregation")
