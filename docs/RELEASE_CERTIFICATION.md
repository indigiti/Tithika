# Tithika Production Certification

This document records the production-readiness contract enforced by CI. It is not a claim that every mapped route is complete; unfinished shells are deliberately excluded from search indexing until their calculation engine or editorial adapter is verified.

## Certified baseline

- Product route contract: **292**
- Verified calculation/live routes: **159**
- Calculated aggregation routes: **21**
- Structured reference routes: **49**
- Structured editorial routes: **62**
- Additional canonical live redirect: **1** (`muhurat/choghadiya`)
- Total production-quality/indexable detail routes: **292**
- Remaining mapped `noindex,follow` shells: **0**

The indexable set is generated from four distinct quality states: verified calculation/live routes (`config/live.php`), calculated aggregations (`config/aggregate.php`), structured references (`config/reference.php`) and structured editorial coverage. **Indexable does not mean verified calculator.** The XML sitemap uses the same quality state.

## Newly certified regional adapters

### Nepali Patro / Nepali Calendar

Routes:
- `/panchang/nepali/`
- `/calendars/nepali/`

Engine:
- `python/nepali_calendar.py`

Contract:
- Offline Gregorian ↔ Bikram Sambat civil conversion.
- Bundled month-length/Baisakh-1 table.
- BS 2000–2099 explicitly marked as the upstream official lookup range.
- Outer embedded years remain available but are marked Sankranti-estimated.
- Daily Tithi/Nakshatra/Paksha remains Tithika's own Lahiri Panchang calculation at local sunrise.
- Benchmark anchors include 2083 Baisakh 1 = 2026-04-14 and 2083 Ashwin/Asoj 20 = 2026-10-06.

### Jain Calendar

Route:
- `/calendars/jain/`

Engine:
- `python/jain_calendar.py`

Contract:
- Explicit **Kartikadi Amanta** Jain/Gujarati-style profile.
- Vikram Samvat turns on Kartika Shukla Pratipada after Diwali.
- Vir Nirvana Samvat is displayed alongside Vikram Samvat.
- Aatham, Chaudas and Amavasya flags derive from the sunrise Tithi.
- The response states that Jain sect/region/Sangh calendars can add observance-specific rules.
- 2026 regression locks Vikram 2082 / Vir 2552 through the Amavasya sunrise on 2026-11-09 and Vikram 2083 / Vir 2553 from Kartika Shukla Pratipada at sunrise on 2026-11-10.

## Newly certified Panchang reuse routes

The following routes reuse the same verified Lahiri Panchang primitives rather than introducing parallel astronomy implementations:

- `/panchang/sunrise/` — local sunrise, sunset, next sunrise and sunrise-state context.
- `/panchang/nakshatra/` — exact monthly Nakshatra transition intervals.
- `/panchang/ganda-moola/` — exact intervals for Ashwini, Ashlesha, Magha, Jyeshtha, Mula and Revati.
- `/panchang/abhijit-nakshatra/` — Moon passage through the explicit Abhijit sidereal span.
- `/panchang/vinchudo/` — exact Moon passage through Vrishchika.
- `/panchang/jwalamukhi-yoga/` — exact overlap of the five encoded Tithi/Nakshatra combinations.
- `/panchang/sankalpa/` — structured Vikrama/Shaka Samvat, dual Drik/Vedic Ritu-Ayana and selected-time Panchang context.
- `/panchang/vedic-clock/` — 60-Ghati Ishtakala and independent 30+30 day/night Ghati clock.

All eight are covered by `scripts/test-panchang-reuse.py`.

### Completed Panchang rule routes

`panchang/manvadi-tithi`, `panchang/yugadi-tithi` and `panchang/kalpadi-tithi` are verified through `python/panchang_completion.py` with explicit Purnimanta month/Paksha/Tithi sunrise selectors and dated regression anchors. `panchang/kranti-samya` remains indexable as a **geometry reference**, not a certified exact Mahapata calculator: it uses true geocentric Sun/Moon declinations including lunar ecliptic latitude and exposes the 0.25° proximity screen explicitly.

## Newly certified Muhurat reuse routes

The following routes reuse the verified Lahiri Panchang, local sunrise/sunset and Lagna geometry while keeping each Muhurat rule family explicit:

- `/muhurat/shubha-hora/` — 12 daylight + 12 night planetary Horas with exact local solar boundaries.
- `/muhurat/panchaka-rahita/` — modulo-9 Tithi + Vara + Nakshatra + Udaya Lagna classification with exact Lagna transitions.
- `/muhurat/auspicious-yoga/` — aggregate yearly view across the seven certified Yoga families below.
- `/muhurat/sarvartha-siddhi/` — weekday-specific Nakshatra combinations.
- `/muhurat/amrit-siddhi/` — seven weekday/Nakshatra pairings.
- `/muhurat/guru-pushya/` — Thursday + Pushya.
- `/muhurat/ravi-pushya/` — Sunday + Pushya.
- `/muhurat/dwipushkar/` — Sunday/Tuesday/Saturday + Bhadra Tithis + Dwi-Pada Nakshatras.
- `/muhurat/tripushkar/` — Sunday/Tuesday/Saturday + Bhadra Tithis + Tri-Pada Nakshatras.
- `/muhurat/ravi-yoga/` — explicit Sun-to-Moon Nakshatra distance rule.

All ten are covered by `scripts/test-muhurat-reuse.py`, including 2026 Pune date-set benchmarks and formula invariants.

### Completed Muhurat rule routes

`muhurat/gowri`, `muhurat/jain-pachchakkhan`, `muhurat/pancha-pakshi` and `muhurat/do-ghati` are verified through `python/muhurat_completion.py`. Do-Ghati uses the canonical 30 Muhurta names and auspicious flags. Pancha Pakshi exposes the defensible five-Yama day/night mirror schedule and explicitly does not fabricate Sukshma sub-periods. `muhurat/shubha-dates` is a named Tithika generic reference profile, not a universal traditional Muhurat claim.

## Newly certified Vrat recurrence routes

The following routes reuse the verified Lahiri Panchang and existing lunar/Vrat substrates with explicit recurrence selectors:

- `/vrat/satyanarayana/` — Purnima occurrence calendar backed by exact Tithi windows.
- `/vrat/durgashtami/` — Shukla Ashtami prevailing at local sunrise.
- `/vrat/skanda-sashti/` — Shukla Sashti with the Panchami→Sashti daytime-transition selector; after-sunset Sashti starts roll to the next civil day.
- `/vrat/karthigai/` — Krittika Nakshatra prevailing at local sunset, matching the evening Deepam observance model.
- `/vrat/rohini/` — Rohini Nakshatra prevailing immediately after local sunrise.
- `/vrat/sawan-somwar/` — Mondays inside Shravana, exposed independently for Purnimanta and Amanta lunar-month conventions.
- `/vrat/mangala-gauri/` — Tuesdays inside Shravana, exposed independently for Purnimanta and Amanta lunar-month conventions.

All seven are covered by `scripts/test-vrat-recurrence.py` with 2026 Pune/Maharashtra recurrence anchors and rule invariants.

### Completed Vrat rule routes

`vrat/iskcon-ekadashi` reuses Tithika's integrated Arunodaya/Vriddhi/Mahadwadashi/Hari-Vasara substrate. Kalashtami uses a night selector; Masik Janmashtami uses local solar Nishita; Chandra Darshan exposes a conservative geometric crescent screen; Ishti/Anvadhan uses local-sunrise Tithi prevalence; Purushottam Maas and Chaturmasa use explicit lunar-month selectors. `vrat/shraddha` is classified as a calculated aggregation because it combines Amavasya, Pitru Paksha, Sankranti, Manvadi, Yugadi and Kalpadi classes rather than claiming an exhaustive traditional Shraddha canon.

## Data provenance

Nepali Bikram Sambat civil month data is vendored from the MIT-licensed `sushilldhakal/nepali-calendar` project. Full attribution is in `docs/THIRD_PARTY_NOTICES.md`, and the upstream MIT license is retained beside the data file.

No runtime third-party calendar package or database is required.

## Release gates

A release is certifiable only when all of the following pass on the exact merged `main` commit:

1. PHP and JavaScript syntax.
2. 292-route manifest validation.
3. SEO/content/accessibility/performance release audit.
4. Production certification counts and provenance.
5. Panchang, Vrat, festival and Muhurat regression fixtures.
6. Regional calendar regressions including Nepali and Jain adapters.
7. Planetary/Jyotish/Kundali/Varga/Yoga/Shadbala/matching/timing/Rashifal regressions.
8. Eclipse, season and Sankranti regression fixtures.

## Final six-phase hardening

The former 99-route shell queue now has an explicit quality tier. Routes are not promoted merely because they render.

- **Verified calculation/live** — deterministic rule/ephemeris engine with route-specific regression evidence.
- **Calculated aggregation** — combines verified substrates into a calendar/collection but is not itself a new independent rule engine.
- **Structured reference** — useful, indexable reference content or a deliberately bounded traditional profile; not counted as a verified calculator.
- **Editorial** — independently structured explanatory content.

The six hardening families are:

1. **Panchang** — Manvadi, Yugadi and Kalpadi have dated recurrence anchors; Kranti Samya is explicitly a true-declination geometry reference rather than an exact Mahapata claim.
2. **Muhurat** — canonical Do-Ghati names, audited Gowri/Jain timings and a five-Yama Pancha Pakshi mirror model; generic Shubha Dates is reference-only.
3. **Vrat** — solar Nishita for Masik Janmashtami, geometric Chandra Darshan screening, sunrise-based Ishti pairing, integrated ISKCON/Mahadwadashi logic and Shraddha aggregation.
4. **Festival/calendar** — yearly/monthly views are classified as calculated aggregations; themed discovery pages remain structured references unless every observance has a dated selector.
5. **Secondary Jyotish** — Name Initials dispatch is corrected; Pancha Pakshi birth-bird selection is Paksha-aware; Prashnavali no longer invents modulo-based omens; gemstone/Rudraksha are honestly labeled references; Sahasra Chandrodaya uses exact full-Moon phase search.
6. **Astronomy** — mutual parallels/contra-parallels are root-refined exact declination events, ecliptic crossings remain exact latitude-zero events, and Indian Ritus use tropical solar longitude boundaries.

The route contract remains **292 indexable routes with zero mapped noindex shells**, but CI separately enforces **159 verified/live calculators**, **21 calculated aggregations** and **49 structured references**. The remaining indexable routes are structured editorial/canonical adapters. These categories are deliberately disjoint.
