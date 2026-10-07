#!/usr/bin/env python3
"""Repository semantic-hardening guard.

This is intentionally narrow: it prevents known shortcut implementations from
silently returning after they have been replaced by explicit rule/geometry code.
"""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

checks={
 "python/panchang_completion.py":[
   "diff<=0.25",
   "def declination(lon_deg",
 ],
 "python/muhurat_completion.py":[
   'MUHURTA_NAMES=["Rudra","Ahi"',
   "major/5",
   "sub=major/5",
 ],
 "python/vrat_completion.py":[
   "time(23,59,59)",
   "midpoint fallback when no civil midnight",
 ],
 "python/jyotish_secondary.py":[
   "nakshatra_id"]%3",
   "29.530588861; target=moment+timedelta(days=synodic*1000)",
   "idx=(panchang.NAKSHATRA_NAMES.index",
 ],
 "python/astronomy_reference.py":[
   "diff<=1.0",
   "events=sankranti.find_year(year,lat,lon,tz,False)",
 ],
}
for rel,forbidden in checks.items():
    text=(ROOT/rel).read_text(encoding="utf-8")
    for needle in forbidden:
        assert needle not in text,(rel,needle)

# Completion tests must now be semantic fixtures, not count-only smoke tests.
for rel in [
 "scripts/test-panchang-completion.py",
 "scripts/test-muhurat-completion.py",
 "scripts/test-vrat-completion.py",
 "scripts/test-festival-calendar-completion.py",
 "scripts/test-jyotish-secondary.py",
 "scripts/test-astronomy-reference.py",
]:
    text=(ROOT/rel).read_text(encoding="utf-8")
    assert "semantic fixture passed" in text,rel

print("Repository semantic-hardening guard passed")
