# Tithika Gap-Closing Roadmap

This roadmap tracks the product gaps identified against the DrikPanchang benchmark without copying its branding, prose, artwork or proprietary implementation.

## Priority order

1. **Daily Home Dashboard** — implemented in this change. Aggregates verified Panchang, Choghadiya, upcoming Vrat/Sankranti and planetary events into one location/date context with a short server-side cache.
2. **Settings / Profile Core** — implemented in this change. Local-first preferences for theme, 12/24-hour time, Amanta/Purnimanta month convention, Smarta/Vaishnava/ISKCON preference and an optional saved default location. No database required.
3. **Kundali Workspace 2.0** — next. Chart-style switching, Ayanamsha registry, saved-chart format, integrated Graha/Yoga/Dasha/Shadbala/Ashtakavarga workspace, then Upagraha and Bhavabala.
4. **Localization Engine** — Hindi first, followed by Marathi, Tamil, Telugu, Gujarati, Bengali, Kannada, Malayalam, Odia, Assamese and Nepali using translation catalogs rather than duplicated pages.
5. **Notifications / Calendar subscriptions** — observance, festival, Sankranti, Muhurat and personal timing reminders generated from existing engines.
6. **Regional daily Panchang views** — reusable presentation adapters over existing regional profiles.
7. **Offline location/timezone/elevation layer** — deterministic geodata fallback and custom coordinates.
8. **Devotional content expansion** — original, public-domain or licensed corpus only.
9. **Media / Gallery system** — first-party asset pipeline and metadata.
10. **PWA / mobile applications** — offline shell and installable experiences after the web product stabilizes.

## Phase 1 architecture

The homepage uses `python/home_dashboard.py` as an aggregation layer. It does not duplicate astronomy logic. The aggregator calls existing engines in parallel and normalizes only the fields needed for the consumer dashboard.

Sources:
- Daily Panchang
- Choghadiya
- Ekadashi
- Pradosh
- Sankashti
- Sankranti
- planetary transits
- planetary retrograde/direct stations

The dashboard is cached by date, location, timezone, time format and tradition for a short TTL.

## Phase 2 architecture

`assets/settings-core.js` owns a versioned browser-local schema. Current fields:
- appearance: system / light / dark
- clock: 12 / 24
- lunar month convention: Amanta / Purnimanta
- observance preference: Smarta / Vaishnava / ISKCON
- language compatibility field (English currently active)
- optional saved default location

Birth data is explicitly outside this settings store.

The shared page client reads these settings dynamically when constructing calculation payloads, so future localization and account sync can be layered on without changing every page.
