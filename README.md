# Tithika

A modern, location-aware Vedic calendar, Panchang and Muhurat platform built with PHP and Python.

## Product architecture

Tithika currently maps **292 logical pages** across 10 product families:

- Panchang
- Calendars
- Muhurat
- Vrat & Upavas
- Festivals
- Jyotish
- Planets & Astronomy
- Devotion
- Gallery
- Learn / reference

All mapped utility pages share one responsive design system, one route manifest and one date/location context layer instead of duplicating page markup.

## Current live experience

### Home — `index.php`

Modern product-style daily dashboard with:

- automatic browser geolocation
- manual city search fallback
- live current Choghadiya
- active-period progress/countdown
- local sunrise and sunset
- Rahu Kaal
- next favourable Choghadiya
- responsive day timeline
- links into the broader Tithika product map

### Daily Panchang — `/panchang/daily/`

The first full Panchang astronomy surface is now engine-backed with:

- local sunrise, sunset, moonrise and moonset
- Lahiri / Chitrapaksha sidereal Sun and Moon longitudes
- Tithi and transition time
- Nakshatra, Pada and transition time
- Yoga and transition time
- Karana and transition time
- Paksha
- Sun and Moon Rashi
- Amanta and Purnimanta lunar month
- Adhika month detection
- Abhijit, Vijaya, Brahma, Godhuli, Pratah/Sayahna Sandhya and Nishita
- Rahu Kala, Yamaganda and Gulika
- date/location-aware recomputation

The same engine is reused by `/panchang/moonrise-moonset/`, `/panchang/rahu-kala/`, `/muhurat/rahu-kala/` and `/muhurat/abhijit/`.

### Month Panchang — `/panchang/month/`

- real sunrise-state Tithi/Nakshatra/Yoga/Karana data for every civil date
- month/year navigation
- Ekadashi/Purnima/Amavasya highlighting
- selected-day drill-down into Daily Panchang
- shared month-result browser cache
- backend reuse of adjacent-day solar events

### Vrat occurrence foundation

Live astronomical occurrence calendars:

- `/vrat/ekadashi/`
- `/vrat/purnima/`
- `/vrat/amavasya/`

Ekadashi candidates also include next-day Parana constraints derived from sunrise, Hari Vasara end and Dwadashi end. Smarta/Vaishnava fasting-date selection remains a separate rule layer.

### Sankranti / solar ingress

The Lahiri sidereal solar-ingress engine powers:

- `/vrat/sankranti/`
- `/calendars/sankranti/`
- `/festivals/sankranti/`
- `/festivals/makar-sankranti/`

It calculates all twelve Nirayana Rashi ingresses with exact local timestamps. Punya Kaal/festival rules remain separate from the astronomical ingress.

### Equinox & solstice

Verified Astronomy Engine events are live for the vernal/autumnal equinoxes and summer/winter solstices, rendered in the selected location's timezone.

### Unified Jyotish analysis — `/jyotish/horoscope-analysis/`

The evidence-first synthesis layer combines existing verified Jyotish engines into one report:

- D1 Rashi, D9 Navamsha and D10 Dashamsha
- complete six-fold Shadbala snapshot
- Sarvashtakavarga house support
- curated structural Yogas
- current Vimshottari Mahadasha/Antardasha/Pratyantardasha context
- current Jupiter, Saturn, Rahu and Ketu houses from Lagna and Moon
- transparent domain evidence indices with disclosed weighting
- divisional-boundary sensitivity warnings
- no deterministic event prediction claims

### Jyotish interpretation report — `/jyotish/interpretation-report/`

The interpretation layer turns calculation evidence into transparent explanatory readings:

- whole-sign functional lordship for all seven classical Grahas
- strict Yogakaraka detection from Kendra + Trikona ownership
- D1 dignity with D9 confirmation and D10 career context
- Shadbala capacity and Sarvashtakavarga house support
- key-house synthesis for H1, H2, H4, H5, H7, H9, H10 and H11
- current Vimshottari lord activation
- Jupiter, Saturn, Rahu and Ketu transit-house activation
- domain narratives for identity, resources, learning, career and relationships
- machine-readable evidence attached to every narrative layer
- explicit safeguards against deterministic event, mortality or high-stakes predictions

### Jyotish timing timeline — `/jyotish/timing-timeline/`

The timing layer turns the interpretation engine into a month/year emphasis timeline:

- 6, 12, 18, 24 or 36-month horizons
- monthly Mahadasha / Antardasha / Pratyantardasha activation
- Jupiter, Saturn, Rahu and Ketu transit-house context
- transparent 0–100 activation indices with disclosed arithmetic
- merged activation windows
- annual domain summaries and peak months
- exact Mahadasha/Antardasha boundary markers
- exact slow-planet Rashi ingress markers
- supportive / mixed / challenging / contextual activation quality
- no event probabilities or guaranteed outcome claims

### Personalized Rashifal — `/jyotish/rashifal/`

The mapped Rashifal family is now backed by the natal interpretation and timing stack:

- `/jyotish/rashifal/` four-horizon personal overview
- `/jyotish/rashifal/daily/` daily birth-chart forecast context
- `/jyotish/rashifal/weekly/` seven-day aggregated context
- `/jyotish/rashifal/monthly/` five-sample monthly context
- `/jyotish/rashifal/yearly/` twelve-month annual context
- separate birth date/time and forecast target date
- Vimshottari Mahadasha/Antardasha/Pratyantardasha activation
- Moon/Sun/Mercury/Venus/Mars short-horizon transit context
- Jupiter/Saturn/Rahu/Ketu medium/long-horizon transit context
- domain-level identity, resources, learning, career and relationship emphasis
- disclosed natal/Dasha/transit score components
- no event probabilities or guaranteed outcome claims

### Choghadiya — `choghadiya.php`

Verified calculation surface with:

- day and night Choghadiya
- current-period highlighting
- live countdown
- Rahu Kaal
- local sunrise/sunset
- 12/24-hour mode
- date navigation
- mobile Day/Night segmented view

## Shared page system

```text
index.php                     modern Tithika home
site-map.php                  browsable map of all routes
page.php                      shared mapped-page renderer

config/routes.php             292-page product/route manifest
includes/site.php             shared shell + route helpers
assets/tithika.css            shared production UI system
assets/tithika-site.js        shared location/date context

api.php                       PHP API / geocoding bridge
python/choghadiya.py          solar + Choghadiya engine
python/panchang.py            Daily Panchang astronomy/rule engine
python/panchang_month.py      Month Panchang engine
python/lunar_occurrences.py   lunar Vrat occurrence/Parana substrate
python/sankranti.py           Nirayana solar-ingress engine
python/seasons.py             equinox/solstice engine
python/horoscope_analysis.py  unified Jyotish synthesis layer
python/interpretation.py      rule-based Jyotish interpretation layer
python/timing_timeline.py      month/year Jyotish timing timeline
python/personal_rashifal.py    personalized daily/weekly/monthly/yearly Rashifal
python/vendor/astronomy.py    vendored Astronomy Engine (MIT)

docs/DRIKPANCHANG_AUDIT.md    benchmark/product audit
docs/TITHIKA_PAGE_MAP.md      implementation map
scripts/validate-routes.php   CI route validator
```

Pretty URLs are handled through Apache rewrite rules, for example:

```text
/panchang/daily/
/calendars/tamil/
/muhurat/vivah/
/vrat/ekadashi/
/festivals/diwali/
/jyotish/birthstar/
/planets/transit/
/devotion/aarti/
```

## Page status

Tithika deliberately separates page creation from calculation-engine readiness:

- **Live** — backed by a verified calculation/content engine.
- **Mapped** — production URL and UI shell exist; specialized engine/content adapter is still pending.
- **Verified** — calculation rules have fixtures and cross-source tests.
- **Released** — engine, UI, SEO, mobile and accessibility audit passed.

Unsupported Tithi, Nakshatra, Yoga, Karana, planetary and Jyotish values are **not fabricated** simply to fill the UI.

## Requirements

- PHP 8.2+
- PHP cURL extension
- PHP mbstring extension
- Python 3.9+ with `zoneinfo`
- Apache `mod_rewrite`
- HTTPS in production for browser geolocation
- internet access for OpenStreetMap Nominatim geocoding

The current Panchang engine vendors its astronomy core, so no Python pip install is required. No database is currently required.

## Current calculation model

The Choghadiya engine uses local sunrise/sunset and weekday-specific day/night sequences. The Daily Panchang engine uses the vendored MIT-licensed Astronomy Engine for apparent geocentric Sun/Moon positions, converts them to Lahiri/Chitrapaksha sidereal longitude, evaluates Panchang state at local sunrise, and refines Tithi/Nakshatra/Yoga/Karana boundaries by binary search.

## Next calculation-engine layers

1. Sun/Moon longitude + Lahiri ayanamsha. ✓
2. Tithi, Nakshatra, Yoga and Karana transitions. ✓
3. Paksha and base Amanta/Purnimanta lunar month. ✓
4. Moonrise/moonset. ✓
5. Core daily auspicious/in-auspicious timings. ✓
6. Base lunar Vrat occurrence engine. ✓
7. Nirayana Sankranti ingress engine. ✓
8. Equinox/solstice astronomy pages. ✓
9. Smarta/Vaishnava Ekadashi observance selection + complete Parana rules.
10. Festival rule engine.
11. Extended Muhurat rule engine.
12. Planet ephemeris/transit/retrograde/combustion. ✓
13. Birth/Jyotish calculators. ✓
14. Shodashavarga + structural Yogas + complete Shadbala. ✓
15. Unified evidence-first horoscope analysis. ✓
16. Auditable Jyotish interpretation knowledge layer. ✓
17. Jyotish timing and forecast timeline engine. ✓
18. Personalized daily/weekly/monthly/yearly Rashifal engine. ✓

See `docs/DRIKPANCHANG_AUDIT.md` and `docs/TITHIKA_PAGE_MAP.md` for the full implementation plan.