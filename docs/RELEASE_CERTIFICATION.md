# Tithika Production Certification

This document records the production-readiness contract enforced by CI. Indexability, route wiring and calculation semantics are separate concerns: a page can be production-quality as a structured reference without being an independent astronomical calculator. The final completion routes are therefore classified explicitly in `config/quality.php`.

## Certified baseline

- Product route contract: **292**
- Live-route registry entries: **229**
- Structured editorial routes: **62**
- Additional canonical live redirect: **1** (`muhurat/choghadiya`)
- Total production-quality/indexable detail routes: **292**
- Remaining mapped `noindex,follow` shells: **0**

The indexable set is generated from `config/live.php`, structured editorial coverage and explicit canonical live adapters. The XML sitemap uses the same quality state. For the former 99 shell routes, CI additionally enforces **34 calculated**, **18 aggregated**, **15 hybrid**, and **32 reference** classifications.

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

`panchang/manvadi-tithi`, `panchang/yugadi-tithi`, `panchang/kalpadi-tithi` and `panchang/kranti-samya` are promoted through `python/panchang_completion.py`. Tithi observances use explicit Purnimanta month/Paksha/Tithi sunrise selectors. Kranti Samya uses true ecliptic longitude/latitude transformed to true-equator-of-date declination, axis-pair classification, a ±30 arcminute Mahapata boundary and refined transition times.

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

`muhurat/gowri`, `muhurat/jain-pachchakkhan`, `muhurat/pancha-pakshi`, `muhurat/do-ghati` and `muhurat/shubha-dates` are promoted through `python/muhurat_completion.py`. Do-Ghati uses the canonical 30-name sequence. Pancha Pakshi exposes a named Pulippani mirror-table profile with local solar Yamas and weighted sub-Yamas. Generic Shubha Dates is explicitly labeled as a Tithika filter.

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

`vrat/iskcon-ekadashi` reuses Tithika's integrated Arunodaya/Vriddhi/Mahadwadashi/Hari-Vasara substrate. Kalashtami uses measured local-night overlap; Masik Janmashtami uses local solar Nishita; Ishti/Anvadhan is Tithi-end paired; Shraddha aggregates implemented Shraddha classes; Purushottam Maas and Chaturmasa use explicit lunar-month profiles. Chandra Darshan reports geometric crescent eligibility and does not claim weather-dependent visibility.

## Data provenance

Nepali Bikram Sambat civil month data is vendored from the MIT-licensed `sushilldhakal/nepali-calendar` project. Full attribution is in `docs/THIRD_PARTY_NOTICES.md`, and the upstream MIT license is retained beside the data file.

No runtime third-party calendar package or database is required.

## Release gates

A release is certifiable only when all of the following pass on the exact merged `main` commit:

1. PHP and JavaScript syntax.
2. 292-route manifest validation.
3. SEO/content/accessibility/performance release audit.
4. Production certification counts, provenance and completion quality taxonomy.
5. Panchang, Vrat, festival and Muhurat regression fixtures.
6. Regional calendar regressions including Nepali and Jain adapters.
7. Planetary/Jyotish/Kundali/Varga/Yoga/Shadbala/matching/timing/Rashifal regressions.
8. Eclipse, season and Sankranti regression fixtures.

## Final six-phase completion

The former 99-route shell queue is complete. All mapped product routes now have a calculation engine, aggregation adapter, or structured reference adapter and are included in the production-quality indexable contract.

1. **Panchang rule-completion** — Manvadi, Yugadi and Kalpadi sunrise selectors; Kranti Samya/Mahapata declination geometry; Published Panchang and Utilities adapters.
2. **Muhurat rule-completion** — versioned Gowri day/night cycles, Jain Pachchakkhan solar-Prahar timings, 30 Do-Ghati Muhurtas, Pancha Pakshi activity cycles and conservative generic Shubha Dates.
3. **Vrat rule-completion** — shared integrated ISKCON/Vaishnava Ekadashi substrate, night-sensitive Kalashtami and Masik Janmashtami, post-Amavasya Chandra Darshan, Ishti/Anvadhan, Shraddha aggregation, Adhika/Purushottam Maas, Chaturmasa and remaining Vrat/reference surfaces.
4. **Festival/calendar aggregation** — Hindu, Tamil and Malayalam yearly aggregation, lunar-month festival collections, themed yearly calendars and structured festival/puja collections.
5. **Secondary Jyotish calculators** — Prashna, Pancha Pakshi, gemstone/Rudraksha traditional references, Namakarana initials, Sahasra Chandrodaya, Vedic Time, Shraddha Tithi and deterministic Prashnavali context.
6. **Astronomy reference** — declination parallels/contra-parallels, geocentric ecliptic crossings, six Indian Ritus, and sidereal/tropical zodiac reference tables.

The final completion contract is listed in `config/completion.php`; its semantic class is enforced by `config/quality.php`. CI requires all 99 former shell routes to be present in `config/live.php`, classified exactly once, backed by their family adapters and truth fixtures where calculation semantics apply. The route contract remains **292**, with **292 indexable routes and zero mapped noindex shells**.
