from __future__ import annotations

from datetime import datetime
from typing import Any

from .core import EngineRegistry, SourceRef, envelope


def _parse(value: Any):
    try:
        return datetime.fromisoformat(str(value))
    except (TypeError, ValueError):
        return None


def audit(payload: dict[str, Any]) -> dict[str, Any]:
    registry = EngineRegistry()
    sources: list[SourceRef] = []
    findings = []
    severity = 0

    chog = registry.run("choghadiya", payload)
    pan = registry.run("panchang", payload)
    sources.extend([registry.source("choghadiya", chog), registry.source("panchang", pan)])

    for name, data in (("choghadiya", chog), ("panchang", pan)):
        loc = data.get("location") or {}
        if payload.get("timezone") and loc.get("timezone") and payload.get("timezone") != loc.get("timezone"):
            findings.append({"level": "warning", "check": "timezone", "engine": name, "message": "Resolved timezone differs from requested timezone."})
            severity += 1

    sunrise = _parse(pan.get("sunrise"))
    sunset = _parse(pan.get("sunset"))
    next_sunrise = _parse(pan.get("next_sunrise"))
    if not (sunrise and sunset and next_sunrise and sunrise < sunset < next_sunrise):
        findings.append({"level": "error", "check": "solar-order", "message": "Sunrise/sunset ordering is invalid or incomplete."})
        severity += 3

    chog_sunrise = _parse(chog.get("sunrise"))
    if sunrise and chog_sunrise and abs((sunrise - chog_sunrise).total_seconds()) > 120:
        findings.append({"level": "warning", "check": "cross-engine-sunrise", "message": "Panchang and Choghadiya sunrise differ by more than two minutes."})
        severity += 2

    st = pan.get("sunrise_state") or {}
    for key in ("tithi", "nakshatra", "yoga", "karana"):
        if not st.get(key):
            findings.append({"level": "error", "check": "panchang-state", "message": f"Missing sunrise {key}."})
            severity += 3

    periods = (chog.get("day") or []) + (chog.get("night") or [])
    if len(periods) != 16:
        findings.append({"level": "error", "check": "choghadiya-count", "message": f"Expected 16 Choghadiya periods; got {len(periods)}."})
        severity += 3

    status = "pass" if severity == 0 else "review" if severity <= 2 else "fail"
    if not findings:
        findings.append({"level": "info", "check": "cross-engine", "message": "Core Panchang and Choghadiya invariants are consistent."})

    return envelope(
        "quality",
        {
            "quality": {
                "status": status,
                "severity_score": severity,
                "checks": findings,
                "policy": "fail-closed on missing deterministic state; warn on cross-engine drift.",
            }
        },
        sources,
        0.97 if status == "pass" else 0.86,
        cache="bypass",
        boundaries=[
            "Quality AI detects structural and cross-engine anomalies; it does not override engine results.",
            "Warnings require inspection when conventions legitimately differ.",
        ],
    )
