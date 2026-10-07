#!/usr/bin/env python3
import json
import subprocess
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
ENGINE=ROOT/"python"/"intelligence_gateway.py"

BASE={
    "lat":18.5204,"lon":73.8567,"city":"Pune, Maharashtra, India",
    "timezone":"Asia/Kolkata","date":"2026-10-06","time":"07:40:31",
    "target_date":"2026-10-07","hour24":False,"node_model":"mean"
}

def run(mode, extra=None):
    payload={**BASE,"mode":mode,**(extra or {})}
    p=subprocess.run([sys.executable,str(ENGINE)],input=json.dumps(payload),text=True,capture_output=True,cwd=ROOT,timeout=180)
    if p.returncode!=0:
        raise SystemExit(p.stdout+"\n"+p.stderr)
    data=json.loads(p.stdout)
    assert data["ok"] is True, data
    assert data["intelligence"]["name"]=="tithika-intelligence"
    assert isinstance(data["intelligence"]["provenance"],list)
    return data

health=run("health")
assert health["health"]["architecture"]=="multi-layer-multi-engine"
assert len(health["health"]["layers"])==6
assert len(health["health"]["engines"])>=10
assert health["health"]["personal_persistent_cache"] is False

advisor=run("advisor",{"range":"today","purpose":"general"})
assert advisor["advisor"]["recommendations"], advisor
assert advisor["intelligence"]["confidence"]["score"]>=0.7
assert any(s["category"]=="calculated-fact" for s in advisor["intelligence"]["provenance"])

ask=run("ask",{"question":"What are the best traditional timing windows today?","range":"today"})
assert ask["conversation"]["intent"]=="advisor"
assert ask["conversation"]["answer"]

profile=run("profile",{"preferences":{"purpose":"general","range":"today","prefer_daytime":True}})
assert profile["profile"]["recommendations"], profile
assert profile["profile"]["storage"]=="request-only"
assert profile["intelligence"]["cache"]=="disabled-personal"

quality=run("quality")
assert quality["quality"]["status"] in {"pass","review","fail"}
assert quality["quality"]["checks"]

jyotish=run("jyotish")
assert jyotish["jyotish"]["birth_signature"]["lagna"]["rashi"]=="Tula"
assert jyotish["jyotish"]["birth_signature"]["moon_rashi"]=="Karka"
assert jyotish["jyotish"]["strengths"]
assert jyotish["jyotish"]["privacy"]["persistent_cache"] is False
assert len(jyotish["intelligence"]["provenance"])>=6

print("Tithika Intelligence fixture OK: six layers, provenance, privacy, advisor, Jyotish fusion and quality audit")
