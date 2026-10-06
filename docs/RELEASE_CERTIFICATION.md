# Tithika Production Certification

This document records the production-readiness contract enforced by CI. It is not a claim that every mapped route is complete; unfinished shells are deliberately excluded from search indexing until their calculation engine or editorial adapter is verified.

## Certified baseline

- Product route contract: **292**
- Verified calculation/live routes: **179**
- Structured editorial routes: **62**
- Additional canonical live redirect: **1** (`muhurat/choghadiya`)
- Total production-quality/indexable detail routes: **242**
- Remaining mapped `noindex,follow` shells: **50**

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

### Six-phase Panchang rule completion

The previously gated Panchang rule family is now promoted through `python/completion.py`:

- `/panchang/manvadi-tithi/` — 14 named Manvadi rules with explicit lunar-month/Tithi selection, Adhika exclusion and Kshaya fallback based on maximum sunrise-day overlap.
- `/panchang/yugadi-tithi/` — the four Yuga commencement Tithis with the same deterministic observance-day selector.
- `/panchang/kalpadi-tithi/` — the seven encoded Kalpadi observances with month/Tithi regression anchors.
- `/panchang/kranti-samya/` — sub-second Sun/Moon declination-equality crossings filtered to Vyatipata/Vaidhriti Yoga, rather than treating the whole Yoga span as Mahapata.

The 2026 Maharashtra Manvadi/Yugadi/Kalpadi anchors and formula invariants are covered by `scripts/test-completion.py`.

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

### Six-phase Muhurat rule completion

The remaining Muhurat family now uses explicit, inspectable profiles:

- `/panchang/gowri/` and `/muhurat/gowri/` — weekday-specific Gowri day/night cycles over eight equal local daylight and eight equal local night segments.
- `/muhurat/jain-pachchakkhan/` — local sunrise/sunset Pachchakkhan reference timings including Navkarshi, Porshi, Purimaddha, Avaddha and Chovihar.
- `/muhurat/pancha-pakshi/` and `/jyotish/pancha-pakshi/` — Nakshatra/Paksha bird selection with a disclosed main-Yama reference profile. Lineage-specific sub-Yama variants are not silently blended into the output.
- `/muhurat/do-ghati/` — thirty local Muhurtas, each two variable local Ghatis; daylight and night are independently divided into fifteen.
- `/muhurat/shubha-dates/` — transparent Panchang quality scoring. The response states that ceremony-specific Muhurat profiles take precedence.

All are regression-gated in `scripts/test-completion.py`.

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

### Six-phase Vrat rule completion

The remaining Vrat shells now have dedicated selectors in `python/completion.py`:

- `/vrat/iskcon-ekadashi/` — exact Ekadashi windows, Arunodaya/Vriddhi handling, Mahadwadashi priority and Parana rules; CI locks the complete 24-date published Pune 2026 ISKCON sequence.
- `/vrat/kalashtami/` — Krishna Ashtami selected for Pradosh/night prevalence with the one-Ghati-after-sunset condition.
- `/vrat/chandra-darshan/` — first post-Amavasya geometric sunset-to-moonset opportunity; the response does not claim an atmospheric crescent-visibility forecast.
- `/vrat/masik-janmashtami/` — Krishna Ashtami overlap with local Nishita.
- `/vrat/ishti-anvadhan/` — Anvadhan on the Purnima/Amavasya Parva day and Ishti on the following civil day.
- `/vrat/shraddha/` — deterministic core Shraddha collection covering Amavasya, Sankranti, Pitru Paksha, Manvadi and Yugadi occasions; it is not labelled as an exhaustive sect-specific 96-day catalogue.
- `/vrat/purushottam-maas/` — contiguous Adhika lunar-month detection from the no-solar-ingress month condition.
- `/vrat/chaturmasa/` — Devshayani/Sayana Ekadashi through Prabodhini/Utthana Ekadashi.

The full batch is regression-gated by `scripts/test-completion.py`.

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
9. Six-phase completion regressions, including the full 2026 Pune ISKCON date-set contract.

## Six requested completion phases closed

The six engine-reuse phases requested for this release are now implemented and promoted:

1. **Panchang rule completion** — 4 routes.
2. **Muhurat rule completion** — 7 routes, including the shared Gowri and Pancha Pakshi surfaces.
3. **Vrat rule completion** — 8 routes.
4. **Festival/calendar aggregation** — 19 routes: Hindu/Tamil/Malayalam collections, twelve lunar-month collections and four verified yearly festival calendars.
5. **Secondary Jyotish calculators** — 8 routes with traditional correspondences clearly labelled as such.
6. **Astronomy reference** — 3 routes for planetary parallels, ecliptic crossings and Nirayana Indian seasons.

That is **49 newly promoted routes**. The remaining **50** mapped `noindex,follow` routes are outside these six completed batches and stay gated because they still need a separate evidence-backed rule family or substantive editorial adapter. They are not promoted merely to reduce the shell count.

Each promoted route has a deterministic engine/profile, a shared API/UI adapter, CI regression coverage and membership in `config/live.php`.
