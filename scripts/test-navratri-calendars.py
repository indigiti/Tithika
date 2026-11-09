#!/usr/bin/env python3
"""2026 India anchors and no-fabrication invariants for all four Navratris."""
import os
import sys
from datetime import date, datetime
from zoneinfo import ZoneInfo

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "python"))
import navratri_calendar as n
import festival_rules as f

TZ = ZoneInfo("Asia/Kolkata")
LAT, LON = 19.076, 72.8777
anchors = {
    "shardiya": "2026-10-11",
    "chaitra": "2026-03-19",
    "magha-gupta": "2026-01-19",
    "ashadha-gupta": "2026-07-15",
}
assert len(n.VARIANTS) == 4
for key, wanted in anchors.items():
    v = n.calculate_variant(key, 2026, LAT, LON, TZ, False)
    assert v is not None, key
    assert v["event"]["date"] == wanted, (key, v["event"]["date"], wanted)
    assert len(v["days"]) == 9, key
    assert [d["tithi"] for d in v["days"]] == list(n.TITHIS[:9])
    assert [d["day"] for d in v["days"]] == list(range(1, 10))
    assert all(datetime.fromisoformat(d["tithi_start"]) < datetime.fromisoformat(d["tithi_end"]) for d in v["days"])
    assert all(d["selection"] in ("sunrise", "vriddhi-two-sunrises",
                "kshaya-no-sunrise-daylight-reference",
                "kshaya-no-sunrise-midpoint-reference") for d in v["days"])
    for a, b in zip(v["days"], v["days"][1:]):
        assert a["tithi_end"] == b["tithi_start"], (key, a, b)
    s = datetime.fromisoformat(v["sandhi"]["start"])
    e = datetime.fromisoformat(v["sandhi"]["end"])
    assert (e-s).total_seconds() == 48*60
    assert datetime.fromisoformat(v["days"][7]["tithi_end"]) == s+(e-s)/2
    g = v["event"]["ghatasthapana"]
    assert datetime.fromisoformat(g["start"]) < datetime.fromisoformat(g["end"])
    doc = n.render(v["slug"], 2026, LAT, LON, TZ)
    assert doc["ok"] and doc["navratri"]["overview"] is False
    assert len(doc["sections"]) == 3
    assert len(doc["sections"][1]["items"]) == 9
    assert doc["year"] == 2026
hub = n.render("calendars/navratri", 2026, LAT, LON, TZ)
ghata = n.render("festivals/ghatasthapana", 2026, LAT, LON, TZ)
assert hub["navratri"]["overview"] and len(hub["sections"][0]["items"]) == 4
assert ghata["navratri"]["overview"] and len(ghata["sections"][0]["items"]) == 4
for row in hub["sections"][0]["items"]:
    assert row["link_slug"].startswith("calendars/")
    assert row["date"] in anchors.values()
print("Four Navratri semantic fixtures passed for Mumbai 2026")
