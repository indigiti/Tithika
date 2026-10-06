#!/usr/bin/env python3
import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime

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
assert ek["observance_status"]=="smarta-vaishnava-iskcon-mahadwadashi-integrated"
oct_event=next(
    event for event in ek["events"]
    if event.get("observance",{}).get("smarta",{}).get("date")=="2026-10-06"
)
assert oct_event["observance"]["vaishnava"]["date"]=="2026-10-06"
assert oct_event["observance"]["vaishnava"]["basis"]=="shuddha-at-arunodaya"


# Mahadwadashi is now integrated into Vaishnava/ISKCON date selection.
maha_events=[
    event for event in ek["events"]
    if event.get("observance",{}).get("mahadwadashi",{}).get("active")
]
assert maha_events, "expected integrated Mahadwadashi overrides in 2026"
maha_dates={
    event["observance"]["mahadwadashi"]["date"]: event
    for event in maha_events
}
for expected in ("2026-05-27","2026-07-11","2026-11-21"):
    assert expected in maha_dates,(expected,sorted(maha_dates))
    obs=maha_dates[expected]["observance"]
    assert obs["vaishnava"]["date"]==expected
    assert obs["iskcon"]["date"]==expected
    assert obs["vaishnava"]["basis"]=="mahadwadashi-override"
    assert obs["iskcon"]["basis"]=="iskcon-mahadwadashi-override"
    assert obs["vaishnava"]["parana"] is not None

# Vyanjuli is sunrise-boundary sensitive. In Mumbai the August Pavitropana
# fast is Aug 23 without a Mahadwadashi override; Pune crosses the second
# Dwadashi sunrise and is covered separately by the Pune recurrence fixture.
aug_event=next(
    event for event in ek["events"]
    if event["start"].startswith("2026-08-23")
)
assert aug_event["observance"]["iskcon"]["date"]=="2026-08-23",aug_event["observance"]
assert aug_event["observance"]["mahadwadashi"]["active"] is False,aug_event["observance"]

july_event=next(
    event for event in ek["events"]
    if event["start"].startswith("2026-07-10")
)
assert july_event["observance"]["smarta"]["date"]=="2026-07-10"
assert july_event["observance"]["vaishnava"]["date"]=="2026-07-11"
july_basis=july_event["observance"]["vaishnava"]["basis"]
assert july_basis in ("gauna-after-dashami-arunodaya","mahadwadashi-override"),july_basis
if july_basis=="mahadwadashi-override":
    maha=july_event["observance"]["mahadwadashi"]
    assert maha["active"] is True
    assert maha["date"]=="2026-07-11"
    assert maha["yogas"]

candidate=next(
    c
    for c in oct_event.get("sunrise_candidates",[])
    if c["date"]=="2026-10-06"
)
assert candidate["parana"] is not None
parana=candidate["parana"]
assert parana["date"]=="2026-10-07"
assert datetime.fromisoformat(parana["earliest"]) >= datetime.fromisoformat(parana["next_sunrise"])
assert datetime.fromisoformat(parana["earliest"]) >= datetime.fromisoformat(parana["hari_vasara_end"])
if parana["deadline"]:
    assert datetime.fromisoformat(parana["earliest"]) < datetime.fromisoformat(parana["deadline"])

pu=run("purnima")
assert all(event["tithi_id"]==14 for event in pu["events"])

am=run("amavasya")
assert all(event["tithi_id"]==29 for event in am["events"])

print("Lunar occurrence fixtures OK: Mumbai 2026")