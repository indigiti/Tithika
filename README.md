# Tithika

A modern, location-aware Vedic calendar, Panchang and Muhurat platform built with PHP and Python.

## Product architecture

Tithika currently maps **277 logical pages** across 10 product families:

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

config/routes.php             277-page product/route manifest
includes/site.php             shared shell + route helpers
assets/tithika.css            shared production UI system
assets/tithika-site.js        shared location/date context

api.php                       PHP API / geocoding bridge
python/choghadiya.py          current solar + Choghadiya engine

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

The existing Python solar engine calculates sunrise and sunset using a 90.833° solar zenith, divides sunrise→sunset into eight equal local day periods and sunset→next sunrise into eight equal local night periods, then applies weekday-specific Choghadiya sequences and Rahu Kaal segments.

## Next calculation-engine layers

1. Sun/Moon longitude + Lahiri ayanamsha. ✓
2. Tithi, Nakshatra, Yoga and Karana transitions. ✓
3. Paksha and base Amanta/Purnimanta lunar month. ✓
4. Moonrise/moonset. ✓
5. Core daily auspicious/in-auspicious timings. ✓
6. Festival/Vrat rule engine.
7. Muhurat rule engine.
8. Planet ephemeris/transit/retrograde/combustion.
9. Birth/Jyotish calculators.

See `docs/DRIKPANCHANG_AUDIT.md` and `docs/TITHIKA_PAGE_MAP.md` for the full implementation plan.
