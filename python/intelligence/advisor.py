from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Any

from .core import EngineRegistry, FileTTLCache, envelope, public_context
from .providers import provider_router

QUALITY_SCORE = {
    "best": 96,
    "good": 88,
    "gain": 84,
    "neutral": 62,
    "avoid": 20,
}

PURPOSE_PROFILE = {
    "marriage": "vivah",
    "vivah": "vivah",
    "home": "griha-pravesh",
    "griha-pravesh": "griha-pravesh",
    "property": "property",
    "vehicle": "vehicle",
    "namakarana": "namakarana",
    "annaprashana": "annaprashana",
    "mundana": "mundana",
}


def _parse_date(payload: dict[str, Any]) -> date:
    raw = str(payload.get("date") or "").strip()
    return datetime.strptime(raw, "%Y-%m-%d").date() if raw else date.today()


def _overlap(a0: str, a1: str, b0: str, b1: str) -> bool:
    try:
        return datetime.fromisoformat(a0) < datetime.fromisoformat(b1) and datetime.fromisoformat(b0) < datetime.fromisoformat(a1)
    except (TypeError, ValueError):
        return False


def _daily_candidates(chog: dict[str, Any], pan: dict[str, Any], day_label: str) -> list[dict[str, Any]]:
    blocked = []
    for key, label in (("rahu_kaal", "Rahu Kaal"), ("yamaganda", "Yamaganda"), ("gulika", "Gulika")):
        row = (pan.get("muhurtas") or {}).get(key) or {}
        if row.get("start") and row.get("end"):
            blocked.append((row["start"], row["end"], label))

    out = []
    for side in ("day", "night"):
        for row in chog.get(side) or []:
            quality = str(row.get("quality") or "neutral").lower()
            if quality == "avoid":
                continue
            cautions = [
                label for b0, b1, label in blocked
                if row.get("start") and row.get("end") and _overlap(row["start"], row["end"], b0, b1)
            ]
            score = QUALITY_SCORE.get(quality, 60) - 10 * len(cautions)
            out.append({
                "date": day_label,
                "kind": "choghadiya",
                "name": row.get("name"),
                "label": row.get("label"),
                "side": side,
                "start": row.get("start"),
                "end": row.get("end"),
                "start_label": row.get("start_label"),
                "end_label": row.get("end_label"),
                "score": max(0, score),
                "cautions": cautions,
                "reason": f"{row.get('name')} is classified as {row.get('label')} in the verified Choghadiya schedule.",
            })

    for key, title, score in (("abhijit", "Abhijit Muhurat", 94), ("vijaya", "Vijaya Muhurat", 91)):
        row = (pan.get("muhurtas") or {}).get(key) or {}
        if row.get("start") and row.get("end"):
            out.append({
                "date": day_label,
                "kind": "panchang-muhurat",
                "name": title,
                "label": "Traditional Muhurat",
                "side": "day",
                "start": row.get("start"),
                "end": row.get("end"),
                "start_label": row.get("start_label"),
                "end_label": row.get("end_label"),
                "score": score,
                "cautions": [],
                "reason": f"{title} comes from the deterministic Panchang Muhurta layer.",
            })
    return out


def _specialized_candidates(registry: EngineRegistry, payload: dict[str, Any], start: date, days: int, purpose: str):
    profile = PURPOSE_PROFILE.get(purpose)
    if not profile:
        return [], []
    p = dict(payload)
    p["profile"] = profile
    data = registry.run("specialized-muhurat", p)
    end = start + timedelta(days=days)
    rows = []
    for day in data.get("auspicious_days") or []:
        try:
            d = datetime.strptime(day.get("date", ""), "%Y-%m-%d").date()
        except (TypeError, ValueError):
            continue
        if not (start <= d < end):
            continue
        for window in day.get("windows") or []:
            rows.append({
                "date": d.isoformat(),
                "kind": "specialized-muhurat",
                "name": data.get("title") or profile,
                "label": "Profile-selected",
                "side": "day",
                "start": window.get("start"),
                "end": window.get("end"),
                "start_label": window.get("start_label"),
                "end_label": window.get("end_label"),
                "score": 99 if window.get("positive_overlaps") else 95,
                "cautions": [],
                "reason": (
                    "Accepted by the versioned specialized Muhurat profile after "
                    "weekday, Tithi, Nakshatra and blocked-period filters."
                ),
                "evidence": window.get("evidence") or {},
                "positive_overlaps": window.get("positive_overlaps") or [],
            })
    return rows, [registry.source("specialized-muhurat", data, "traditional-rule")]


def advise(payload: dict[str, Any]) -> dict[str, Any]:
    registry = EngineRegistry()
    cache = FileTTLCache(ttl_seconds=300)
    start = _parse_date(payload)
    range_name = str(payload.get("range") or "today").lower()
    days = 7 if range_name in {"week", "this-week", "7d"} else 1
    purpose = str(payload.get("purpose") or "general").lower()
    cache_payload = public_context({**payload, "date": start.isoformat(), "range": "week" if days == 7 else "today"})
    key = cache.key("advisor", cache_payload)
    cached = cache.get(key)
    if cached:
        cached["intelligence"]["cache"] = "hit"
        return cached

    sources = []
    candidates = []
    specialized, specialized_sources = _specialized_candidates(registry, payload, start, days, purpose)
    candidates.extend(specialized)
    sources.extend(specialized_sources)

    daily_notes = []
    for offset in range(days):
        d = start + timedelta(days=offset)
        p = dict(payload)
        p["date"] = d.isoformat()
        chog = registry.run("choghadiya", p)
        pan = registry.run("panchang", p)
        sources.extend([
            registry.source("choghadiya", chog),
            registry.source("panchang", pan),
        ])
        candidates.extend(_daily_candidates(chog, pan, d.isoformat()))
        st = pan.get("sunrise_state") or {}
        daily_notes.append({
            "date": d.isoformat(),
            "tithi": st.get("tithi"),
            "nakshatra": st.get("nakshatra"),
            "yoga": st.get("yoga"),
            "moon_rashi": pan.get("moon_rashi"),
        })

    candidates.sort(key=lambda row: (-int(row.get("score") or 0), str(row.get("start") or "")))
    top = candidates[:8]
    provider = provider_router()
    findings = [
        f"{row.get('date')} {row.get('name')} {row.get('start_label')}–{row.get('end_label')} scored {row.get('score')}."
        for row in top[:4]
    ]
    summary = provider.summarize(
        "Traditional timing advisor",
        findings,
        {"purpose": purpose, "range": "week" if days == 7 else "today"},
    )
    result = envelope(
        "advisor",
        {
            "advisor": {
                "purpose": purpose,
                "range": "week" if days == 7 else "today",
                "summary": summary,
                "recommendations": top,
                "daily_context": daily_notes,
                "method": (
                    "Ranks verified Choghadiya and Panchang Muhurta windows; supported "
                    "purposes also use the specialized Muhurat profile as the highest-priority layer."
                ),
            }
        },
        sources,
        0.94 if top else 0.72,
        provider=provider.name,
        cache="miss",
        boundaries=[
            "Recommendations rank traditional timing windows; they are not guarantees of outcomes.",
            "Specialized purposes use declared Muhurat profiles when available.",
            "Astronomical timestamps are copied from deterministic engines, never generated by the synthesis layer.",
        ],
    )
    cache.set(key, result)
    return result
