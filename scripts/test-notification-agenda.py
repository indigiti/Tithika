#!/usr/bin/env python3
import json,subprocess,sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
ENGINE=ROOT/"python"/"notification_agenda.py"

def run(payload):
    p=subprocess.run([sys.executable,str(ENGINE)],input=json.dumps(payload),text=True,capture_output=True,cwd=ROOT,timeout=240)
    if p.returncode!=0:
        raise SystemExit(p.stdout+"\n"+p.stderr)
    data=json.loads(p.stdout)
    assert data["ok"] is True,data
    return data

base={
    "lat":18.5204,"lon":73.8567,"city":"Pune, Maharashtra, India",
    "timezone":"Asia/Kolkata","date":"2026-10-06","hour24":False,
    "tradition":"smarta"
}
agenda=run({**base,"horizon_days":30,"categories":["ekadashi","sankranti"]})
assert agenda["engine"]["name"]=="tithika-notification-agenda"
assert agenda["preferences"]["tradition"]=="smarta"
assert agenda["events"],agenda
assert all(row["kind"] in {"ekadashi","parana","sankranti"} for row in agenda["events"])
assert any(row["kind"]=="sankranti" and row["date"]=="2026-10-17" for row in agenda["events"]),agenda["events"]
assert any(row["kind"]=="ekadashi" for row in agenda["events"]),agenda["events"]
assert all(agenda["date"]<=row["date"]<=agenda["through"] for row in agenda["events"])

iskcon=run({**base,"tradition":"iskcon","horizon_days":45,"categories":["ekadashi"]})
ek=[row for row in iskcon["events"] if row["kind"]=="ekadashi"]
assert ek and all(row["meta"].get("tradition")=="iskcon" for row in ek)
assert any(row["kind"]=="parana" for row in iskcon["events"]),iskcon["events"]

solar=run({**base,"horizon_days":1,"categories":["solar"]})
assert any(row["kind"]=="sunrise" for row in solar["events"]),solar["events"]
assert any(row["kind"]=="sunset" for row in solar["events"]),solar["events"]
assert solar["delivery"]["background_push"]=="reserved-for-pwa-service-worker-phase"

print("Notification agenda fixture OK: filtered observances, ISKCON Parana, Sankranti and solar events")
