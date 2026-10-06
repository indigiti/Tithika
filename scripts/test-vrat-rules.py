#!/usr/bin/env python3
import os
import sys
from datetime import date, datetime
from zoneinfo import ZoneInfo

ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,os.path.join(ROOT,"python"))

import vrat_rules

tz=ZoneInfo("Asia/Kolkata")
dwadashi_start=datetime.fromisoformat("2026-10-07T00:34:00+05:30")
dwadashi_end=datetime.fromisoformat("2026-10-07T23:16:00+05:30")
p=vrat_rules.ordinary_ekadashi_parana(
    date(2026,10,6),dwadashi_start,dwadashi_end,
    19.0760,72.8777,tz,False
)
assert p is not None
start=datetime.fromisoformat(p["start"])
end=datetime.fromisoformat(p["end"])
sunrise=datetime.fromisoformat(p["sunrise"])
hari=datetime.fromisoformat(p["hari_vasara_end"])
assert p["date"]=="2026-10-07"
assert start>=sunrise
assert start>=hari
assert end>start
assert end<=dwadashi_end
assert "hari-vasara" in p["rule"]

base=vrat_rules.base_ekadashi_dates(
    datetime.fromisoformat("2026-10-05T17:49:00+05:30"),
    datetime.fromisoformat("2026-10-06T20:36:00+05:30"),
    19.0760,72.8777,tz
)
assert base["smarta_date"]<=base["vaishnava_date"]
assert base["smarta_basis"]
assert base["vaishnava_basis"]

profile=vrat_rules.shravana_profile(
    dwadashi_start,dwadashi_end,date(2026,10,7),
    19.0760,72.8777,tz
)
assert set(profile)=={
    "shravana_yoga","vishnushrinkhala","overlap_minutes","intervals"
}
assert profile["overlap_minutes"]>=0

print("Shared Vrat rules fixture passed")
