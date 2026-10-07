from __future__ import annotations

from typing import Any

from .advisor import advise
from .core import SourceRef, classify_intent, compact_text, envelope
from .jyotish import analyze
from .profile import recommend as profile_recommend
from .quality import audit as quality_audit


def _sources_from(result: dict[str, Any]) -> list[SourceRef]:
    return [
        SourceRef(
            engine=s.get("engine", "unknown"),
            version=s.get("version", "unknown"),
            category=s.get("category", "calculated-fact"),
            note=s.get("note", ""),
        )
        for s in (result.get("intelligence") or {}).get("provenance") or []
    ]


def ask(payload: dict[str, Any]) -> dict[str, Any]:
    question = compact_text(payload.get("question") or payload.get("q"), 600)
    if not question:
        raise ValueError("A question is required")

    intent = classify_intent(question)

    if intent == "advisor":
        routed = advise(payload)
        answer = (routed.get("advisor") or {}).get("summary") or "Timing recommendations are ready."
        data = {"conversation": {"question": question, "intent": intent, "answer": answer, "result": routed.get("advisor")}}
        return envelope("ask", data, _sources_from(routed), 0.91, provider=(routed.get("intelligence") or {}).get("provider", "deterministic-synthesis"))

    if intent == "jyotish":
        if not payload.get("date") or not payload.get("time"):
            return envelope(
                "ask",
                {"conversation": {
                    "question": question,
                    "intent": intent,
                    "answer": "For a birth-chart or Jyotish question, provide birth date, exact birth time and location. Tithika will then combine Kundali, Shadbala, D9, Yogas, Vimshottari and current planetary state.",
                    "required": ["date", "time", "lat", "lon", "timezone"],
                }},
                [], 0.98, cache="bypass",
            )
        routed = analyze(payload)
        answer = (routed.get("jyotish") or {}).get("summary") or "Jyotish synthesis is ready."
        return envelope(
            "ask",
            {"conversation": {"question": question, "intent": intent, "answer": answer, "result": routed.get("jyotish")}},
            _sources_from(routed), 0.9, provider=(routed.get("intelligence") or {}).get("provider", "deterministic-synthesis"),
            cache="disabled-personal",
        )

    if intent == "profile":
        routed = profile_recommend(payload)
        return envelope(
            "ask",
            {"conversation": {
                "question": question,
                "intent": intent,
                "answer": "I ranked the verified timing windows using the preferences supplied in this request.",
                "result": routed.get("profile"),
            }},
            _sources_from(routed), 0.9, cache="disabled-personal",
        )

    if intent == "quality":
        routed = quality_audit(payload)
        q = routed.get("quality") or {}
        return envelope(
            "ask",
            {"conversation": {
                "question": question,
                "intent": intent,
                "answer": f"Quality audit status: {q.get('status', 'unknown')}.",
                "result": q,
            }},
            _sources_from(routed), 0.96,
        )

    return envelope(
        "ask",
        {"conversation": {
            "question": question,
            "intent": "general",
            "answer": (
                "Tithika Intelligence can advise on traditional timing, explain Panchang context, "
                "combine Jyotish engines, rank preferences and audit calculation consistency. "
                "Ask a specific timing question or provide birth details for a Jyotish synthesis."
            ),
            "suggestions": [
                "What are the best traditional timing windows today?",
                "Find vehicle purchase Muhurat this week.",
                "Explain my Kundali using Shadbala, D9, Yogas and Dasha.",
                "Check whether today's Panchang and Choghadiya outputs are consistent.",
            ],
        }},
        [], 0.86, cache="bypass",
    )
