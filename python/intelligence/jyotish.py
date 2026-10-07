from __future__ import annotations

from typing import Any

from .core import EngineRegistry, SourceRef, envelope
from .providers import provider_router


def _planet_strengths(data: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for row in data.get("planets") or []:
        rows.append({
            "planet": row.get("planet"),
            "rupa": row.get("total_rupa"),
            "required": row.get("required_rupa"),
            "ratio": row.get("ratio"),
            "meets_required": row.get("meets_required"),
        })
    return sorted(rows, key=lambda x: float(x.get("ratio") or 0), reverse=True)


def _current_dasha(data: dict[str, Any]) -> dict[str, Any]:
    current = ((data.get("result") or {}).get("current") or {})
    maha = current.get("mahadasha") or {}
    antar = current.get("antardasha") or {}
    return {
        "mahadasha": maha.get("lord"),
        "antardasha": antar.get("lord"),
        "mahadasha_end": maha.get("full_end") or maha.get("end"),
        "antardasha_end": antar.get("full_end") or antar.get("end"),
    }


def analyze(payload: dict[str, Any]) -> dict[str, Any]:
    if not str(payload.get("date") or "").strip():
        raise ValueError("Birth date is required for Jyotish intelligence")
    if not str(payload.get("time") or "").strip():
        raise ValueError("Birth time is required for Jyotish intelligence")

    registry = EngineRegistry(timeout_seconds=55)
    sources: list[SourceRef] = []

    kundali = registry.run("kundali", payload)
    sources.append(registry.source("kundali", kundali))

    shadbala = registry.run("shadbala", payload)
    sources.append(registry.source("shadbala", shadbala, "calculated-strength"))

    varga_payload = dict(payload)
    varga_payload["division"] = 9
    vargas = registry.run("vargas", varga_payload)
    sources.append(registry.source("vargas", vargas, "calculated-chart"))

    yogas = registry.run("yogas", payload)
    sources.append(registry.source("yogas", yogas, "traditional-rule"))

    dasha_payload = dict(payload)
    if payload.get("target_date") and not dasha_payload.get("as_of"):
        dasha_payload["as_of"] = str(payload["target_date"])
    vimshottari = registry.run("vimshottari", dasha_payload)
    sources.append(registry.source("vimshottari", vimshottari, "traditional-rule"))

    transit_payload = {
        "date": payload.get("target_date") or payload.get("as_of") or payload.get("date"),
        "timezone": payload.get("timezone") or "Asia/Kolkata",
        "node_model": payload.get("node_model") or "mean",
        "mode": "positions",
    }
    planetary = registry.run("planetary", transit_payload)
    sources.append(registry.source("planetary", planetary))

    strengths = _planet_strengths(shadbala)
    lagna = kundali.get("lagna") or {}
    panchang = kundali.get("panchang") or {}
    dasha = _current_dasha(vimshottari)

    yoga_rows = yogas.get("yogas") or yogas.get("results") or []
    if isinstance(yoga_rows, dict):
        yoga_rows = [{"name": key, **(value if isinstance(value, dict) else {"value": value})} for key, value in yoga_rows.items()]
    notable_yogas = []
    for row in yoga_rows[:12] if isinstance(yoga_rows, list) else []:
        if isinstance(row, dict):
            notable_yogas.append({
                "name": row.get("name") or row.get("yoga") or row.get("title"),
                "present": row.get("present", True),
                "detail": row.get("detail") or row.get("reason") or row.get("description"),
            })

    provider = provider_router()
    findings = [
        f"Janma Lagna is {lagna.get('rashi')}.",
        f"Birth Moon is {panchang.get('moon_rashi')} in {panchang.get('nakshatra')}.",
    ]
    if strengths:
        findings.append(
            "Highest Shadbala ratios: " +
            ", ".join(f"{x.get('planet')} {float(x.get('ratio') or 0):.2f}x" for x in strengths[:3])
            + "."
        )
    if dasha.get("mahadasha"):
        findings.append(
            f"Current Vimshottari period: {dasha.get('mahadasha')} Mahadasha"
            + (f" / {dasha.get('antardasha')} Antardasha." if dasha.get("antardasha") else ".")
        )

    summary = provider.summarize(
        "Jyotish multi-engine synthesis",
        findings,
        {"layers": ["kundali", "shadbala", "d9", "yogas", "vimshottari", "transits"]},
    )

    return envelope(
        "jyotish",
        {
            "jyotish": {
                "summary": summary,
                "birth_signature": {
                    "lagna": lagna,
                    "moon_rashi": panchang.get("moon_rashi"),
                    "nakshatra": panchang.get("nakshatra"),
                    "nakshatra_pada": panchang.get("nakshatra_pada"),
                    "sun_rashi": panchang.get("sun_rashi"),
                },
                "strengths": strengths,
                "current_dasha": dasha,
                "notable_yogas": notable_yogas,
                "d9": vargas.get("charts") or vargas.get("chart") or vargas.get("D9"),
                "transits": planetary.get("planets") or [],
                "layers": {
                    "kundali": kundali,
                    "shadbala": shadbala,
                    "vargas": vargas,
                    "yogas": yogas,
                    "vimshottari": vimshottari,
                    "planetary": planetary,
                },
                "privacy": {
                    "persistent_cache": False,
                    "external_provider_receives_raw_birth_data": False,
                },
            }
        },
        sources,
        0.93,
        provider=provider.name,
        cache="disabled-personal",
        boundaries=[
            "This combines declared Jyotish calculation systems; interpretive traditions can differ.",
            "Shadbala measures strength, not benefic or malefic outcome by itself.",
            "Birth-time-sensitive Vargas should be treated cautiously near divisional boundaries.",
            "External synthesis, if enabled, receives compact derived findings rather than raw birth payloads.",
        ],
    )
