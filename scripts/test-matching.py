#!/usr/bin/env python3
import json, subprocess, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
ENGINE=ROOT/"python"/"matching.py"

def run(payload):
    p=subprocess.run([sys.executable,str(ENGINE)],input=json.dumps(payload),text=True,capture_output=True,cwd=ROOT)
    if p.returncode!=0:
        raise SystemExit(p.stdout+"\n"+p.stderr)
    d=json.loads(p.stdout)
    assert d["ok"] is True,d
    return d

same=run({
    "mode":"nakshatra",
    "groom":{"nakshatra":"Hasta","pada":2},
    "bride":{"nakshatra":"Hasta","pada":2},
})
assert same["match"]["total"]==28.0,same["match"]
by={x["name"]:x for x in same["match"]["kootas"]}
assert by["Varna"]["earned"]==1.0
assert by["Vashya"]["earned"]==2.0
assert by["Tara"]["earned"]==3.0
assert by["Yoni"]["earned"]==4.0
assert by["Graha Maitri"]["earned"]==5.0
assert by["Gana"]["earned"]==6.0
assert by["Bhakoot"]["earned"]==7.0
assert by["Nadi"]["earned"]==0.0
assert same["match"]["nadi"]["present"] is True
assert same["match"]["nadi"]["cancelled"] is False
assert same["match"]["band"]=="inauspicious"

cancelled=run({
    "mode":"nakshatra",
    "groom":{"nakshatra":"Hasta","pada":1},
    "bride":{"nakshatra":"Hasta","pada":4},
})
assert cancelled["match"]["total"]==28.0
assert cancelled["match"]["nadi"]["present"] is True
assert cancelled["match"]["nadi"]["cancelled"] is True
assert any(x["rule"]=="same-nakshatra-different-pada" for x in cancelled["match"]["nadi"]["cancellations"])

bh=run({
    "mode":"nakshatra",
    "groom":{"nakshatra":"Ashwini","pada":2},
    "bride":{"nakshatra":"Rohini","pada":2},
})
bhrow=next(x for x in bh["match"]["kootas"] if x["name"]=="Bhakoot")
assert bhrow["earned"]==0.0,bhrow
assert bh["match"]["bhakoot"]["present"] is True

profile={
    "date":"2026-10-06","time":"07:40:31",
    "lat":18.5204,"lon":73.8567,"city":"Pune, India","timezone":"Asia/Kolkata"
}
full=run({
    "mode":"horoscope","groom":profile,"bride":profile,
    "as_of":"2026-10-06T12:00:00+05:30"
})
assert full["match"]["total"]==28.0
assert full["engine"]["maximum_gunas"]==36
assert full["engine"]["mangal_in_score"] is False
assert full["integration"]["mangal_compatible"] is True
assert full["groom"]["moon"]["nakshatra"]=="Ashlesha"
assert full["bride"]["lagna"]["rashi"]=="Tula"
assert full["groom"]["dasha"]["mahadasha"]=="Mercury"
assert len(full["groom"]["placements"])==9

print("Matching fixture OK: Ashtakoota 36-point tables, Nadi/Bhakoot flags and Kundali/Dasha integration")
