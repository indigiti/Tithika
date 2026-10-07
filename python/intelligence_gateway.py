#!/usr/bin/env python3
from __future__ import annotations

import json
import sys

from intelligence.service import dispatch


def main() -> None:
    payload = json.loads(sys.stdin.read() or "{}")
    if not isinstance(payload, dict):
        raise ValueError("Payload must be a JSON object")
    mode = str(payload.get("mode") or "health")
    result = dispatch(mode, payload)
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(json.dumps({
            "ok": False,
            "error": str(exc),
            "code": "INTELLIGENCE_FAILED",
        }, ensure_ascii=False))
        sys.exit(1)
