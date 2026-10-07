from __future__ import annotations

from typing import Any

from .advisor import advise
from .core import SourceRef, envelope


def recommend(payload: dict[str, Any]) -> dict[str, Any]:
    preferences = payload.get("preferences") if isinstance(payload.get("preferences"), dict) else {}
    purpose = str(preferences.get("purpose") or payload.get("purpose") or "general").lower()
    tradition = str(preferences.get("tradition") or "default")
    language = str(preferences.get("language") or "en")
    range_name = str(preferences.get("range") or payload.get("range") or "week")

    advisor_payload = {
        k: payload[k] for k in ("lat", "lon", "city", "timezone", "date", "hour24") if k in payload
    }
    advisor_payload.update({"purpose": purpose, "range": range_name})
    timing = advise(advisor_payload)

    recommendations = []
    for row in (timing.get("advisor") or {}).get("recommendations") or []:
        score = int(row.get("score") or 0)
        if preferences.get("prefer_daytime") and row.get("side") == "day":
            score += 3
        if preferences.get("avoid_night") and row.get("side") == "night":
            score -= 12
        recommendations.append({**row, "personal_score": max(0, min(100, score))})
    recommendations.sort(key=lambda x: (-x["personal_score"], str(x.get("start") or "")))

    src = [
        SourceRef(
            engine=s.get("engine", "unknown"),
            version=s.get("version", "unknown"),
            category=s.get("category", "calculated-fact"),
            note=s.get("note", ""),
        )
        for s in (timing.get("intelligence") or {}).get("provenance") or []
    ]

    return envelope(
        "profile",
        {
            "profile": {
                "preferences": {
                    "purpose": purpose,
                    "tradition": tradition,
                    "language": language,
                    "prefer_daytime": bool(preferences.get("prefer_daytime")),
                    "avoid_night": bool(preferences.get("avoid_night")),
                },
                "recommendations": recommendations[:8],
                "explanation": (
                    "Personal ranking applies explicit user preferences after the verified "
                    "Panchang/Muhurat advisor; it does not change astronomical calculations."
                ),
                "storage": "request-only",
            }
        },
        src,
        0.91,
        cache="disabled-personal",
        boundaries=[
            "Profile preferences affect ranking only, never the underlying calculation.",
            "No profile is persisted by the Python intelligence service.",
        ],
    )
