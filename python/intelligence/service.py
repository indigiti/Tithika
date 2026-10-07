from __future__ import annotations

from typing import Any

from . import VERSION
from .advisor import advise
from .conversation import ask
from .core import ENGINE_SPECS, SourceRef, envelope
from .jyotish import analyze
from .profile import recommend as profile_recommend
from .quality import audit as quality_audit


LAYERS = [
    {"id": "core", "name": "Intelligence Core", "status": "active"},
    {"id": "advisor", "name": "Panchang / Muhurat Advisor", "status": "active"},
    {"id": "jyotish", "name": "Jyotish Intelligence", "status": "active"},
    {"id": "conversation", "name": "Conversational Tithika", "status": "active"},
    {"id": "profile", "name": "Recommendation / Profile Engine", "status": "active"},
    {"id": "quality", "name": "Quality AI", "status": "active"},
]


def health() -> dict[str, Any]:
    return envelope(
        "health",
        {
            "health": {
                "version": VERSION,
                "architecture": "multi-layer-multi-engine",
                "layers": LAYERS,
                "engines": sorted(ENGINE_SPECS.keys()),
                "external_synthesis": "optional-disabled-by-default",
                "personal_persistent_cache": False,
            }
        },
        [SourceRef("tithika-intelligence-core", VERSION, "orchestration")],
        1.0,
        cache="bypass",
    )


def dispatch(mode: str, payload: dict[str, Any]) -> dict[str, Any]:
    mode = (mode or "health").strip().lower()
    if mode == "health":
        return health()
    if mode == "advisor":
        return advise(payload)
    if mode == "jyotish":
        return analyze(payload)
    if mode == "ask":
        return ask(payload)
    if mode == "profile":
        return profile_recommend(payload)
    if mode == "quality":
        return quality_audit(payload)
    raise ValueError(f"Unsupported intelligence mode: {mode}")
