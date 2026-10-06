# Tithika Production Certification

This document records the production-readiness contract enforced by CI. It is not a claim that every mapped route is complete; unfinished shells are deliberately excluded from search indexing until their calculation engine or editorial adapter is verified.

## Certified baseline

- Product route contract: **292**
- Verified calculation/live routes: **113**
- Structured editorial routes: **62**
- Additional canonical live redirect: **1** (`muhurat/choghadiya`)
- Total production-quality/indexable detail routes: **176**
- Remaining mapped `noindex,follow` shells: **116**

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

### Deliberately gated Panchang routes

`panchang/manvadi-tithi`, `panchang/yugadi-tithi` and `panchang/kalpadi-tithi` remain `noindex,follow`. CI showed that simple sunrise, Tithi-start or Tithi-midpoint selection is insufficient for all listed observance dates, especially when a Tithi spans two civil dates or an Adhika month creates duplicate lunar-month candidates. These routes require dedicated observance-day selectors before promotion.

`panchang/kranti-samya` also remains gated because Mahapat requires a dedicated declination-equality calculation rather than treating the full Vyatipata/Vaidhriti Yoga span as equivalent.

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

## Remaining shell-completion queue

The remaining **116** mapped routes stay `noindex,follow`. They should be promoted in engine-reuse batches rather than route-by-route:

1. **Panchang rule-completion batch** — dedicated Manvadi/Yugadi/Kalpadi observance-day selectors plus Kranti Samya/Mahapat declination-equality calculation.
2. **Muhurat reuse batch** — Shubha Hora, Gowri, Panchaka Rahita, auspicious Yoga and recurring Yoga-date calendars.
3. **Vrat recurrence batch** — Vinayaka Chaturthi, Sawan Somwar, Skanda Sashti, Karthigai, Rohini, Chandra Darshan and related recurring rules.
4. **Festival/calendar aggregation batch** — Hindu/Tamil/Malayalam month collections and festival-specific yearly calendars built from verified event rules.
5. **Secondary Jyotish calculators** — Prashna, gemstone, Rudraksha, baby-name/name-initial and related evidence-based utilities.
6. **Astronomy reference batch** — parallels, ecliptic crossings and Indian seasons.

Each promotion must add or reuse a deterministic engine, a route-specific UI adapter, a regression fixture and then enter `config/live.php`.
