# Tithika Production Certification

This document records the production-readiness contract enforced by CI. It is not a claim that every mapped route is complete; unfinished shells are deliberately excluded from search indexing until their calculation engine or editorial adapter is verified.

## Certified baseline

- Product route contract: **292**
- Verified calculation/live routes: **218**
- Structured editorial routes: **62**
- Additional canonical live redirect: **1** (`muhurat/choghadiya`)
- Total production-quality/indexable detail routes: **281**
- Semantic quality-gated `noindex,follow` routes: **11**

The indexable set is generated from `config/live.php`, structured editorial coverage and explicit canonical live adapters. The XML sitemap uses the same quality state.

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

`panchang/manvadi-tithi`, `panchang/yugadi-tithi` and `panchang/kalpadi-tithi` are promoted through `python/panchang_completion.py` with explicit Purnimanta month/Paksha/Tithi sunrise selectors. `panchang/kranti-samya` now uses true-ecliptic Sun/Moon latitude in its declination geometry, but remains quality-gated until an exact Mahapata boundary formula is source-locked and benchmarked.

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

`muhurat/gowri`, `muhurat/jain-pachchakkhan`, `muhurat/do-ghati` and `muhurat/shubha-dates` are promoted through `python/muhurat_completion.py`. Do-Ghati uses the corrected 30-name classical sequence. `muhurat/pancha-pakshi` is quality-gated: only the verified five day/five night Yama framework is emitted until a source-locked bird/activity and unequal-duration profile is implemented.

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

`vrat/iskcon-ekadashi` reuses Tithika's integrated Arunodaya/Vriddhi/Mahadwadashi/Hari-Vasara substrate. Kalashtami, Masik Janmashtami, Purushottam Maas and Chaturmasa remain promoted; Masik Janmashtami now uses local solar Nishita rather than civil midnight. Chandra Darshan, Ishti/Anvadhan and Shraddha remain quality-gated pending full visibility/observance-class benchmarks.

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

## Full-repository semantic hardening

The six-phase implementation pass exposed an important distinction between **executable** and **semantically certified** routes. CI now enforces that distinction instead of treating any route that returns structured JSON as verified.

### Corrected during the hardening audit

- Do-Ghati Muhurat now uses the canonical 30 Muhurta names.
- Masik Krishna Janmashtami selects by local solar Nishita (sunset-to-next-sunrise midpoint), with a deterministic maximum-night-overlap fallback.
- Planetary mutual parallels/contra-parallels are now exact declination root searches instead of a within-one-degree snapshot.
- Indian Ritus now use tropical solar-longitude boundaries rather than Nirayana Sankranti.
- Prashna Kundali now exposes a full question-time D1 foundation with Lagna plus all nine classical Grahas.
- Fabricated Pancha-Pakshi modulo bird assignment and Prashnavali favourable/mixed/cautious scoring were removed.
- Monthly personalized Rashifal now samples every civil day instead of five roughly weekly samples.
- API body/search limits, canonical-origin hardening and a baseline Content Security Policy were added.

### Semantic quality gates

The following **11** mapped routes are intentionally `noindex,follow` and excluded from `config/live.php` until their exact tradition/rule semantics are implemented and benchmarked:

- `panchang/kranti-samya`
- `muhurat/pancha-pakshi`
- `vrat/chandra-darshan`
- `vrat/ishti-anvadhan`
- `vrat/shraddha`
- `jyotish/pancha-pakshi`
- `jyotish/gemstone`
- `jyotish/rudraksha`
- `jyotish/sahasra-chandrodaya`
- `jyotish/prashnavali`
- `jyotish/rashi-by-name`

Reasons are machine-readable in `config/gated.php`. CI fails if any gated route appears in the live registry or becomes indexable without an explicit fixture change.

### Current strict contract

- **292** mapped product routes
- **218** verified/live calculation routes
- **281** production-quality/indexable detail routes
- **11** semantic quality-gated routes

This stricter contract supersedes the earlier temporary 292/292 promotion claim.
