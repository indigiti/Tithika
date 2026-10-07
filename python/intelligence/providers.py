from __future__ import annotations

import json
import os
import urllib.request
from typing import Any

from .core import compact_text


class SynthesisProvider:
    name = "deterministic-synthesis"

    def summarize(self, title: str, findings: list[str], context: dict[str, Any] | None = None) -> str:
        clean = [compact_text(x, 220) for x in findings if compact_text(x, 220)]
        if not clean:
            return f"{title}: no additional interpretation is available from the verified inputs."
        return f"{title}: " + " ".join(clean[:4])


class HttpJsonProvider(SynthesisProvider):
    """Optional external synthesis adapter.

    Disabled by default. It receives only compact derived findings, not raw birth
    payloads. The endpoint may be a local model gateway or a compatible hosted
    service that accepts title/findings/context and returns a text field.
    """

    name = "http-json-synthesis"

    def __init__(self, endpoint: str, api_key: str = ""):
        self.endpoint = endpoint
        self.api_key = api_key

    def summarize(self, title: str, findings: list[str], context: dict[str, Any] | None = None) -> str:
        body = json.dumps({
            "title": compact_text(title, 120),
            "findings": [compact_text(x, 220) for x in findings[:8]],
            "context": context or {},
            "instruction": (
                "Summarize only the supplied findings. Do not invent dates, planetary "
                "positions, Tithi, Nakshatra, Muhurat times or medical/legal/financial claims."
            ),
        }).encode("utf-8")
        headers = {"Content-Type": "application/json", "Accept": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        req = urllib.request.Request(self.endpoint, data=body, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=12) as response:
            data = json.loads(response.read().decode("utf-8"))
        text = data.get("text") if isinstance(data, dict) else None
        if not text:
            raise RuntimeError("External synthesis provider returned no text")
        return compact_text(text, 1200)


def provider_router() -> SynthesisProvider:
    enabled = os.getenv("TITHIKA_AI_EXTERNAL", "").strip().lower() in {"1", "true", "yes"}
    endpoint = os.getenv("TITHIKA_AI_ENDPOINT", "").strip()
    if enabled and endpoint:
        return HttpJsonProvider(endpoint, os.getenv("TITHIKA_AI_API_KEY", ""))
    return SynthesisProvider()
