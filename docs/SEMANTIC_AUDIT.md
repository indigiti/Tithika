# Tithika Semantic Audit

This document records the repository-wide semantic hardening pass that follows the
292-route shell-completion milestone. A green route/syntax test is not treated as
proof of calendrical or astrological correctness; rule engines are expected to expose
their method and carry semantic regression fixtures.

## Quality classes

- **Exact geometry/ephemeris** — astronomical roots, longitudes, declinations,
  rise/set events, eclipses, ingress and phase searches computed from the vendored
  Astronomy Engine.
- **Deterministic traditional profile** — a named/versioned calendrical or Jyotish
  rule built from exact Panchang primitives. Different traditions may legitimately
  use a different profile.
- **Structured reference** — discovery, educational, deity, Puja or themed index
  content. It must not present an invented astronomical date.
- **Approximation** — allowed only when explicitly labelled in the API/UI and tests.

## Hardening findings and remediation

### Panchang
- Manvadi/Yugadi/Kalpadi retain explicit month/Paksha/Tithi-at-sunrise selectors.
- Kranti Samya/Mahapata now uses full Sun/Moon ecliptic coordinates, including lunar
  latitude, converts them to equatorial declination and refines actual
  |solar declination| = |lunar declination| roots inside the accepted axis pairs.
- CI validates the rule predicates and the numerical root residual.

### Muhurat
- Gowri and Jain Pachchakkhan remain solar-boundary profiles.
- Do-Ghati now carries the canonical 30-name sequence.
- Pancha Pakshi now emits only the sourced five daytime + five nighttime major Yamas
  for a chosen Pakshi. Unsourced Suksma/micro ordering is deliberately not inferred.
- Generic Shubha Dates remains explicitly labelled as a conservative Tithika filter,
  not a universal ceremony-specific Muhurat.

### Vrat / Shraddha
- ISKCON Ekadashi continues to reuse Arunodaya, Vriddhi, Mahadwadashi and
  Hari-Vasara-aware Parana logic.
- Masik Janmashtami now selects actual local Nishita overlap instead of civil midnight.
- Chandra Darshan is explicitly a geometric young-Moon candidate and no longer claims
  naked-eye visibility.
- Shraddha aggregation includes Amavasya, Sankranti, Pitru Paksha, Vaidhriti,
  Vyatipata, Manvadi, Yugadi and the five-month Purvedyu/Ashtaka/Anvashtaka classes.

### Festival/calendar aggregation
- Yearly Hindu/Tamil/Malayalam calendar views now aggregate the shared major festival
  selectors plus Purnima, Amavasya, Ekadashi, Pradosham, Sankashti, Masik Shivaratri
  and Sankranti engines.
- Themed deity/Puja/discovery collections remain structured references when no
  dedicated date selector exists.

### Secondary Jyotish
- Prashna exposes a whole-sign 12-house question-time chart context.
- Gemstone/Rudraksha output is now a set of traditional chart-context correspondences
  rather than a single automatic remedial prescription.
- Sahasra Chandrodaya searches the actual first through 1000th full Moon.
- Pancha Pakshi birth-bird mapping uses both Janma Nakshatra and Paksha.
- Prashnavali no longer manufactures a favourable/mixed/cautious score from a numeric
  remainder; no omen verdict is emitted without a separately sourced textual system.

### Astronomy
- Mutual parallels/contra-parallels are annual exact declination-root searches rather
  than a one-instant one-degree proximity scan.
- Indian six-Ritu boundaries use tropical solar-longitude ingress.
- Ecliptic crossing logic remains exact zero-latitude refinement.

## Repository-wide scan

The first-party PHP/JS/Python code was reviewed for placeholder/fallback language,
hard-coded verification claims, approximate methods, duplicated calculation paths and
count-only completion tests. Resilience fallbacks that are explicitly surfaced (for
example polar sunrise edge cases or Nepali-calendar source-quality labels) are retained.
Known semantic shortcuts are guarded by `scripts/test-semantic-hardening.py`.

The strong core engines — Panchang, planetary ephemeris, Lagna/Kundali, Vargas,
Shadbala, matching, eclipse, Sankranti and regional calendars — continue to use their
existing dedicated regression suites.
