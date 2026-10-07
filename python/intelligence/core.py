from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from . import VERSION

PYTHON_DIR = Path(__file__).resolve().parents[1]
ROOT = Path(__file__).resolve().parents[2]

ENGINE_SPECS = {
    "choghadiya": "choghadiya.py",
    "panchang": "panchang.py",
    "muhurat-rules": "muhurat_rules.py",
    "specialized-muhurat": "specialized_muhurat.py",
    "kundali": "kundali.py",
    "shadbala": "shadbala.py",
    "vargas": "vargas.py",
    "yogas": "yogas.py",
    "vimshottari": "vimshottari.py",
    "planetary": "planetary.py",
    "horoscope-analysis": "horoscope_analysis.py",
    "interpretation": "interpretation.py",
    "timing-timeline": "timing_timeline.py",
    "personal-rashifal": "personal_rashifal.py",
}


class IntelligenceError(RuntimeError):
    pass


@dataclass(frozen=True)
class SourceRef:
    engine: str
    version: str
    category: str = "calculated-fact"
    note: str = ""

    def as_dict(self) -> dict[str, Any]:
        return {
            "engine": self.engine,
            "version": self.version,
            "category": self.category,
            "note": self.note,
        }


class EngineRegistry:
    def __init__(self, timeout_seconds: int = 40):
        self.timeout_seconds = timeout_seconds

    def run(self, name: str, payload: dict[str, Any]) -> dict[str, Any]:
        relative = ENGINE_SPECS.get(name)
        if not relative:
            raise IntelligenceError(f"Unknown engine: {name}")
        script = PYTHON_DIR / relative
        if not script.is_file():
            raise IntelligenceError(f"Engine unavailable: {name}")
        proc = subprocess.run(
            [sys.executable, str(script)],
            input=json.dumps(payload, ensure_ascii=False),
            text=True,
            capture_output=True,
            cwd=ROOT,
            timeout=self.timeout_seconds,
        )
        try:
            data = json.loads(proc.stdout or "{}")
        except json.JSONDecodeError as exc:
            raise IntelligenceError(
                f"{name} returned invalid JSON: {(proc.stderr or '').strip()[:240]}"
            ) from exc
        if proc.returncode != 0 or not isinstance(data, dict) or not data.get("ok"):
            message = ""
            if isinstance(data, dict):
                message = str(data.get("error") or data.get("detail") or "")
            if not message:
                message = (proc.stderr or "engine failed").strip()
            raise IntelligenceError(f"{name}: {message[:320]}")
        return data

    @staticmethod
    def source(name: str, data: dict[str, Any], category: str = "calculated-fact") -> SourceRef:
        meta = data.get("engine") if isinstance(data.get("engine"), dict) else {}
        return SourceRef(
            engine=str(meta.get("name") or name),
            version=str(meta.get("version") or "unknown"),
            category=category,
            note=str(meta.get("status") or ""),
        )


class FileTTLCache:
    """Short-lived cache for non-personal intelligence results.

    Personal birth/profile requests are intentionally excluded by callers unless
    an explicit opt-in is added later.
    """

    def __init__(self, namespace: str = "tithika-intelligence", ttl_seconds: int = 300):
        base = os.getenv("TITHIKA_AI_CACHE_DIR")
        self.root = Path(base) if base else Path(tempfile.gettempdir()) / namespace
        self.ttl_seconds = max(30, min(int(ttl_seconds), 3600))
        try:
            self.root.mkdir(mode=0o700, parents=True, exist_ok=True)
        except OSError:
            pass

    @staticmethod
    def key(mode: str, payload: dict[str, Any]) -> str:
        material = json.dumps(
            {"version": VERSION, "mode": mode, "payload": payload},
            sort_keys=True,
            ensure_ascii=False,
            separators=(",", ":"),
        )
        return hashlib.sha256(material.encode("utf-8")).hexdigest()

    def get(self, key: str) -> dict[str, Any] | None:
        path = self.root / f"{key}.json"
        try:
            stat = path.stat()
            if time.time() - stat.st_mtime > self.ttl_seconds:
                path.unlink(missing_ok=True)
                return None
            data = json.loads(path.read_text("utf-8"))
            return data if isinstance(data, dict) else None
        except (OSError, json.JSONDecodeError):
            return None

    def set(self, key: str, value: dict[str, Any]) -> None:
        path = self.root / f"{key}.json"
        temp = path.with_suffix(".tmp")
        try:
            temp.write_text(json.dumps(value, ensure_ascii=False), "utf-8")
            os.chmod(temp, 0o600)
            temp.replace(path)
        except OSError:
            try:
                temp.unlink(missing_ok=True)
            except OSError:
                pass


def confidence(score: float, reasons: list[str] | None = None) -> dict[str, Any]:
    score = round(max(0.0, min(1.0, float(score))), 3)
    label = "high" if score >= 0.86 else "medium" if score >= 0.68 else "low"
    return {"score": score, "label": label, "reasons": reasons or []}


def envelope(
    mode: str,
    data: dict[str, Any],
    sources: list[SourceRef],
    score: float,
    *,
    provider: str = "deterministic-synthesis",
    cache: str = "bypass",
    boundaries: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "ok": True,
        "intelligence": {
            "name": "tithika-intelligence",
            "version": VERSION,
            "mode": mode,
            "provider": provider,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "cache": cache,
            "confidence": confidence(score),
            "provenance": [s.as_dict() for s in sources],
            "boundaries": boundaries or [
                "Astronomical and calendrical values come from deterministic Tithika engines.",
                "Interpretive or recommendation text is advisory and exposes its source layer.",
                "AI synthesis must not invent Tithi, Nakshatra, planetary position or Muhurat timestamps.",
            ],
        },
        **data,
    }


def public_context(payload: dict[str, Any]) -> dict[str, Any]:
    allowed = ("lat", "lon", "city", "timezone", "date", "hour24", "purpose", "range")
    return {k: payload[k] for k in allowed if k in payload}


def compact_text(value: Any, limit: int = 180) -> str:
    text = " ".join(str(value or "").split())
    return text[:limit]


def classify_intent(question: str) -> str:
    q = question.casefold()
    if any(word in q for word in ("best time", "muhurat", "auspicious", "choghadiya", "rahu", "today", "this week")):
        return "advisor"
    if any(word in q for word in ("kundali", "birth chart", "dasha", "shadbala", "varga", "yoga", "transit", "horoscope")):
        return "jyotish"
    if any(word in q for word in ("profile", "preference", "recommend for me", "my calendar")):
        return "profile"
    if any(word in q for word in ("wrong", "check", "quality", "anomaly", "inconsistent", "verify")):
        return "quality"
    return "general"
