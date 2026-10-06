#!/usr/bin/env python3
import json, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
ENGINE=ROOT/"python"/"ashtakavarga.py"
payload={"lat":18.5204,"lon":73.8567,"city":"Pune, India","timezone":"Asia/Kolkata","date":"2026-10-06","time":"07:40:31"}
p=subprocess.run([sys.executable,str(ENGINE)],input=json.dumps(payload),text=True,capture_output=True,cwd=ROOT)
if p.returncode!=0: raise SystemExit(p.stdout+"\n"+p.stderr)
d=json.loads(p.stdout);assert d["ok"] is True,d
expected={"Sun":48,"Moon":49,"Mars":39,"Mercury":54,"Jupiter":56,"Venus":52,"Saturn":39}
assert d["integrity"]["valid"] is True,d["integrity"]
assert d["sav"]["total"]==337
assert len(d["sav"]["scores"])==12
for p,total in expected.items():
 assert d["bav"][p]["total"]==total,(p,d["bav"][p]["total"])
 assert all(0<=x<=8 for x in d["bav"][p]["scores"])
assert sum(d["lagna_ashtakavarga"]["scores"])==d["lagna_ashtakavarga"]["total"]
assert len(d["rows"])==12
print("Ashtakavarga fixture OK: classical BAV checksums and 337-point SAV")
