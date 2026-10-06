#!/usr/bin/env python3
import json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];ENGINE=ROOT/"python"/"shadbala.py"
p={"lat":18.5204,"lon":73.8567,"city":"Pune, India","timezone":"Asia/Kolkata","date":"2026-10-06","time":"07:40:31"}
r=subprocess.run([sys.executable,str(ENGINE)],input=json.dumps(p),text=True,capture_output=True,cwd=ROOT)
if r.returncode!=0:raise SystemExit(r.stdout+"\n"+r.stderr)
d=json.loads(r.stdout);assert d["ok"] is True,d
assert d["engine"]["status"]=="foundation-not-totaled"
assert len(d["planets"])==7
assert d["lagna"]["rashi"]=="Tula"
for row in d["planets"]:
 c=row["components"]
 assert 0<=c["uchcha"]<=60
 assert 0<=c["dig"]<=60
 assert c["kendra"] in (15.0,30.0,60.0)
 assert c["drekkana"] in (0.0,15.0)
 assert c["naisargika"]>0
assert "final Shadbala total" in d["withheld"]
print("Shadbala foundation fixture OK: audited components only, total withheld")
