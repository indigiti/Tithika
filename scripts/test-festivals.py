#!/usr/bin/env python3
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENGINE = ROOT / "python" / "festivals.py"
BASE = {
    "lat": 19.0760,
    "lon": 72.8777,
    "city": "Mumbai, India",
    "timezone": "Asia/Kolkata",
    "date": "2026-01-01",
    "hour24": False,
}

def run(kind):
    proc = subprocess.run(
        [sys.executable, str(ENGINE)],
        input=json.dumps(dict(BASE, kind=kind)),
        text=True,
        capture_output=True,
        cwd=ROOT,
    )
    if proc.returncode != 0:
        raise SystemExit(f"{kind} failed: {proc.stdout}\n{proc.stderr}")
    data = json.loads(proc.stdout)
    assert data["ok"] is True, data
    assert data["event"], (kind, data)
    return data["event"]

def within(actual, expected, tolerance_minutes=10):
    a = datetime.fromisoformat(actual)
    e = datetime.fromisoformat(expected)
    return abs((a - e).total_seconds()) <= tolerance_minutes * 60

ganesh = run("ganesh-chaturthi")
assert ganesh["date"] == "2026-09-14", ganesh
assert within(ganesh["puja"]["start"], "2026-09-14T11:20:00+05:30")
assert within(ganesh["puja"]["end"], "2026-09-14T13:48:00+05:30")

rakhi = run("raksha-bandhan")
assert rakhi["date"] == "2026-08-28", rakhi
assert within(rakhi["thread_ceremony"]["end"], "2026-08-28T09:48:00+05:30")
assert rakhi["bhadra_status"] == "clear-at-sunrise"

navratri = run("navratri")
assert navratri["date"] == "2026-10-11", navratri
assert within(navratri["ghatasthapana"]["start"], "2026-10-11T06:31:00+05:30")
assert within(navratri["ghatasthapana"]["end"], "2026-10-11T10:27:00+05:30")

dussehra = run("dussehra")
assert dussehra["date"] == "2026-10-20", dussehra
assert within(dussehra["aparahna"]["start"], "2026-10-20T13:33:00+05:30")
assert within(dussehra["aparahna"]["end"], "2026-10-20T15:53:00+05:30")
assert within(dussehra["vijay_muhurat"]["start"], "2026-10-20T14:19:00+05:30")
assert within(dussehra["vijay_muhurat"]["end"], "2026-10-20T15:06:00+05:30")

holi = run("holi")
assert holi["date"] == "2026-03-02", holi
assert holi["rangwali_holi_date"] == "2026-03-03"
assert within(holi["pradosh"]["start"], "2026-03-02T18:44:00+05:30")
assert within(holi["pradosh"]["end"], "2026-03-02T21:11:00+05:30")

karwa = run("karwa-chauth")
assert karwa["date"] == "2026-10-29", karwa
assert within(karwa["moonrise"], "2026-10-29T21:00:00+05:30", 12)
assert within(karwa["upavasa"]["start"], "2026-10-29T06:37:00+05:30", 10)

diwali = run("diwali")
assert diwali["date"] == "2026-11-08", diwali
assert within(diwali["pradosh"]["start"], "2026-11-08T18:02:00+05:30", 10)
assert within(diwali["pradosh"]["end"], "2026-11-08T20:34:00+05:30", 10)
assert diwali["vrishabha_lagna_status"] == "verified"
assert within(diwali["vrishabha_lagna"]["start"], "2026-11-08T18:27:00+05:30", 6)
assert within(diwali["vrishabha_lagna"]["end"], "2026-11-08T20:27:00+05:30", 6)
assert within(diwali["lakshmi_puja"]["start"], "2026-11-08T18:27:00+05:30", 6)
assert within(diwali["lakshmi_puja"]["end"], "2026-11-08T20:27:00+05:30", 6)

janmashtami = run("janmashtami")
assert janmashtami["date"] == "2026-09-04", janmashtami
assert within(janmashtami["nishita"]["start"], "2026-09-05T00:14:00+05:30", 7)
assert within(janmashtami["nishita"]["end"], "2026-09-05T01:01:00+05:30", 7)
assert janmashtami["dahi_handi_date"] == "2026-09-05"
assert janmashtami["selection_status"] == "base-nishita-rule"

rama = run("rama-navami")
assert rama["date"] == "2026-03-26", rama
assert within(rama["puja"]["start"], "2026-03-26T11:30:00+05:30", 10)
assert within(rama["puja"]["end"], "2026-03-26T13:57:00+05:30", 10)
assert rama["vaishnava_date"] == "2026-03-27"

hanuman = run("hanuman-jayanti")
assert hanuman["date"] == "2026-04-02", hanuman

akshaya = run("akshaya-tritiya")
assert akshaya["date"] == "2026-04-19", akshaya
assert within(akshaya["puja"]["start"], "2026-04-19T10:49:00+05:30", 10)
assert within(akshaya["puja"]["end"], "2026-04-19T12:38:00+05:30", 10)

vat = run("vat-savitri")
assert vat["date"] == "2026-05-16", vat

durga = run("durga-puja")
assert durga["date"] == "2026-10-19", durga
assert within(durga["sandhi_puja"]["start"], "2026-10-19T10:27:00+05:30", 5)
assert within(durga["sandhi_puja"]["end"], "2026-10-19T11:15:00+05:30", 5)

print("Major festival fixtures OK: Mumbai 2026 batches 1-2")
