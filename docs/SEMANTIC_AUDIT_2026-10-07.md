# Tithika Full Repository Semantic Audit — 2026-10-07

Baseline audited: `main@d35323bfbdff391ccd14799aca11c097b6b85000`

Audit branch: `audit/full-repo-semantic-hardening`

## Scope

The audit covered:

- all mapped routes and the shared live/indexable registry;
- all first-party Python calculation, rule, aggregation and reference engines;
- PHP API/route/render dispatch;
- JavaScript syntax and page integration;
- every Python regression fixture;
- release/SEO/accessibility certification;
- the 99-route final completion batch;
- placeholder rendering on every indexable route.

The audit deliberately separates three concepts:

1. **astronomical calculation** — a numerical result derived from ephemeris/solar/lunar geometry;
2. **traditional rule profile** — a named, versioned observance/Muhurat/Jyotish selector;
3. **structured reference adapter** — an indexable knowledge/reference surface that does not claim to be an astronomical calculation.

## Correctness defects fixed

### Panchang / Mahapata

- Replaced longitude-only declination approximation with true ecliptic longitude + latitude conversion.
- Kranti Samya now searches exact declination roots and refines the Mahapata interval rather than using a coarse 20-minute scan plus a fixed proximity hit.
- Added 2026 date/window semantic anchors.

### Muhurat

- Corrected the canonical 30 Do-Ghati Muhurta names and auspicious/inauspicious classification.
- Replaced equal Pancha-Pakshi sub-periods with unequal activity-duration profiles.
- Added semantic assertions that reject equal fifths and lock canonical Do-Ghati names.

### Vrat / observance

- Masik Krishna Janmashtami now uses the local Nishita Muhurta instead of civil midnight.
- Chandra Darshan now requires post-Amavasya crescent geometry at sunset (elongation, apparent altitude and moonset lag), rather than moonset-after-sunset alone.
- Ishti/Anvadhan selection was corrected and date-pair fixtures added.
- Shraddha output was expanded with Sankranti, Vaidhriti, Vyatipata and Kalpadi classes in addition to Amavasya, Pitru Paksha, Manvadi and Yugadi.
- Mahadwadashi documentation now matches the integrated override behavior already used by Ekadashi selection.

### Festival / calendar aggregation

- Yearly Hindu aggregation now combines the declarative major-festival registry with recurring Ekadashi, Purnima, Amavasya and Sankranti engines.
- Fixed Sankranti result-schema mismatches in yearly aggregation.
- Month collections now filter the richer calculated yearly event set.

### Secondary Jyotish

- Fixed `jyotish/name-initials` dispatch; it no longer returns the baby-name calculator.
- Removed fabricated modulo-based Prashnavali scoring.
- Expanded Prashna from a four-field snapshot to question-time whole-sign Graha placements.
- Gemstone and Rudraksha pages now expose lordship-based candidates with natal context and explicit non-prescriptive language.
- Sahasra Chandrodaya now refines the 1000th astronomical full Moon instead of reporting only a mean-synodic estimate.
- Pancha-Pakshi birth-bird assignment now uses Nakshatra + Paksha instead of a simple Nakshatra modulo.

### Astronomy reference

- Mutual parallels/contra-parallels now search and refine exact yearly declination-equality roots.
- Indian Ritus now use tropical solar-longitude boundaries instead of Nirayana Sankranti boundaries.
- Semantic fixtures verify declination equality and the six 2026 tropical season boundaries.

## Repository-wide hardening

- Added an isolated route renderer for CI.
- Added an indexable-route render audit across the full 292-route manifest.
- CI fails if an indexable page renders known placeholder/shell copy.
- The six completion fixtures run early in CI and now contain semantic date/rule invariants rather than count-only assertions.
- Existing core suites were reviewed for benchmark coverage. Strong date/invariant fixtures already exist for Sankranti, Vrat recurrence, Muhurat reuse, specialized Muhurat, planetary geometry, regional calendars, matching, Dwadashi/Mahadwadashi, eclipses, Lagna, and other major engines.

## Explicit model boundaries retained

Some outputs are intentionally labelled as candidate/reference profiles rather than universal prescriptions:

- generic Shubha Dates are a conservative Tithika filter, not a ceremony-specific Muhurat;
- gemstone/Rudraksha results are traditional lordship-based candidates, not automatic prescriptions;
- name-to-Rashi is an approximate traditional naming heuristic; birth-chart Rashi remains authoritative;
- Prashnavali exposes a question-chart context unless a named traditional Prashnavali system is selected;
- Nepali dates outside the bundled official lookup range remain explicitly marked Sankranti-estimated;
- polar/missing-rise fallbacks remain explicit in affected lunar-day calculations.

These are not hidden fallbacks and must remain labelled in API/UI output.

## Certification requirement

A future release is not considered semantically certified merely because engines return non-empty arrays. Exact date/time anchors, geometric invariants, named-rule invariants, or explicit reference-adapter classification are required.

