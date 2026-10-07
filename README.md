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

The homepage now uses the same local production shell as mapped routes:

- no runtime Tailwind/CDN dependency
- shared canonical/OpenGraph/JSON-LD metadata
- keyboard-accessible location chooser
- responsive family/engine overview
- production-quality route counts
- direct paths into Panchang, Muhurat, Jyotish, festivals and editorial content

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

### Vrat rule engine

The Vrat stack now separates exact Tithi occurrence from observance selection and supports:

- `/vrat/ekadashi/`, `/vrat/dwadashi/` and Mahadwadashi classification
- Smarta, Vaishnava and ISKCON-compatible Ekadashi date profiles
- 96-minute Arunodaya purity and Vriddhi handling
- all eight Mahadwadashi classifiers: Unmilini, Vanjuli, Trisparsha, Pakshavarddhini, Jaya, Vijaya, Jayanti and Papanashini
- Mahadwadashi priority over ordinary Vaishnava/ISKCON Ekadashi
- Hari Vasara-aware Ekadashi Parana
- Shravana Yoga / Vishnushrinkhala Dwadashi detection
- special Shravana/Sangava-aware Parana handling
- machine-readable evidence for every override

Purnima and Amavasya remain exact astronomical occurrence surfaces for festival/observance rule layers.

### Shared festival rule engine

All 13 currently verified major festivals now use one declarative rule registry instead of a monolithic selector switch. Shared selectors cover sunrise, Madhyahna, Aparahna, Pradosh, Nishita, moonrise, Sandhi, Ghatasthapana, Bhadra-aware Purnima and auspicious Choghadiya windows.

Current migrated festivals include Ganesh Chaturthi, Raksha Bandhan, Navratri, Vijayadashami, Holi, Karwa Chauth, Janmashtami, Rama Navami, Hanuman Jayanti, Akshaya Tritiya, Vat Savitri, Durga Puja and Diwali.

### Shared Muhurat rule foundation

`python/muhurat_rules.py` provides the common substrate for the next specialized Muhurat stage:

- local sunrise/sunset context
- Rahu Kaal, Yamaganda and Gulika exclusion
- Vishti/Bhadra Karana exclusion
- interval merge/subtraction
- minimum-duration filtering
- configurable weekday/Tithi/Nakshatra/Yoga/Karana allow/block rules
- midpoint Panchang evidence
- auditable accepted/rejected-window reasons
- Abhijit/Vijaya overlap flags

The common engine is exposed through `api.php?action=muhurat-rules`.

### Specialized Muhurat profiles

Stage 5 layers versioned ceremony rules on the shared substrate:

- `/muhurat/vivah/`
- `/muhurat/griha-pravesh/`
- `/muhurat/property/`
- `/muhurat/vehicle/`
- selectable Namakarana, Annaprashana and Mundana Sanskar profiles
- weekday, Tithi and Nakshatra Shuddhi
- Rahu Kaal, Yamaganda, Gulika, Vishti/Bhadra and blocked-Yoga subtraction
- Adhika-month rejection where required
- Guru/Shukra combustion checks for Vivah/Griha profiles
- minimum-window enforcement and evidence attached to each accepted window

### Panchang decision utilities

Stage 6 makes these mapped tools calculation-backed:

- `/panchang/tarabalam/` — personalized 9-Tara cycle; favourable Tara 2/4/6/8/9
- `/panchang/chandrabalam/` — personalized Moon-house strength; favourable houses 1/3/6/7/10/11
- `/panchang/panchak/` — exact Moon-longitude Panchak intervals
- `/panchang/bhadra/` — exact Vishti Karana intervals

### Reusable Muhurat utilities

The shared Muhurat reuse engine now powers:

- `/muhurat/shubha-hora/`
- `/muhurat/panchaka-rahita/`
- `/muhurat/auspicious-yoga/`
- `/muhurat/sarvartha-siddhi/`
- `/muhurat/amrit-siddhi/`
- `/muhurat/guru-pushya/`
- `/muhurat/ravi-pushya/`
- `/muhurat/dwipushkar/`
- `/muhurat/tripushkar/`
- `/muhurat/ravi-yoga/`

Hora uses exact local day/night twelfths; Panchaka Rahita uses verified Lagna transitions plus the modulo-9 formula; recurring Yogas preserve separate weekday/Nakshatra/Tithi rule tables. Gowri, Jain Pachchakkhan, Pancha Pakshi, Do Ghati and generic Shubha Dates remain deliberately gated.

### Reusable Vrat recurrences

A shared recurrence engine now promotes seven additional Vrat calendars without duplicating Panchang astronomy:

- `/vrat/satyanarayana/` — exact Purnima occurrence calendar
- `/vrat/durgashtami/` — Shukla Ashtami at sunrise
- `/vrat/skanda-sashti/` — Panchami/Sashti civil-day selector
- `/vrat/karthigai/` — Krittika at local sunset
- `/vrat/rohini/` — Rohini after local sunrise
- `/vrat/sawan-somwar/` — Purnimanta + Amanta Shravana Monday profiles
- `/vrat/mangala-gauri/` — Purnimanta + Amanta Shravana Tuesday profiles

The ISKCON Ekadashi route now reuses the integrated Arunodaya/Vriddhi/Mahadwadashi/Hari-Vasara substrate. Kalashtami and Masik Janmashtami have explicit night selectors, while Chandra Darshan is deliberately labeled as a conservative geometric crescent screen rather than a guaranteed naked-eye visibility prediction.

### Regional calendar engine

Stage 7 reuses one Lahiri astronomy core while keeping regional month conventions explicit:

- solar calendars: Tamil, Malayalam, Bengali, Odia and Assamese
- Amanta lunar calendars: Telugu, Kannada, Gujarati and Marathi
- Purnimanta lunar calendar: Hindi
- Gaudiya/ISKCON month naming on the Purnimanta lunar substrate
- regional month/day labels rendered in the shared month grid
- Malayalam Kollavarsham and Bengali Era rollover metadata

Nepali and Jain calendar adapters are now live through dedicated engines. Nepali uses an offline Bikram Sambat civil-date table plus Tithika Panchang; Jain uses an explicit Kartikadi Amanta Vikram/Veer Samvat profile.

### Reusable Panchang utilities

A shared reuse engine now promotes eight additional Panchang surfaces without duplicating astronomical logic:

- Hindu Sunrise
- monthly Nakshatra intervals
- Ganda Moola intervals
- Abhijit Nakshatra
- Vinchudo
- Jwalamukhi Yoga
- structured Sankalpa context
- Vedic Clock with both 60-Ghati Ishtakala and 30+30 day/night models

Manvadi, Yugadi and Kalpadi remain deliberately mapped-but-unreleased pending dedicated observance-day selectors. Kranti Samya remains pending a Mahapat declination-equality engine.

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

### Stage 8 — SEO + internal linking

The shared shell now provides production SEO controls across Tithika:

- absolute canonical URLs
- unique title/description generation
- indexability and calculation certification are separate: verified calculators, calculated aggregations, structured references and editorial routes have distinct registries
- OpenGraph + Twitter metadata
- WebSite/WebPage/Article/CollectionPage JSON-LD
- BreadcrumbList schema on detail pages
- dynamic `/sitemap.xml` containing only production-quality routes
- dynamic `/robots.txt` with sitemap discovery
- topic-aware cross-family internal links that avoid thin mapped shells

### Stage 9 — Devotion / Learn / Gallery content layer

All Devotion, Gallery and Learn routes now have structured editorial content instead of generic placeholder copy:

- original explanatory Learn guides for Panchang, Choghadiya, Muhurat, Nakshatra, Rahu Kaal, FAQ and product guidance
- devotional taxonomy for Aarti, Chalisa, Stotra, Mantra, Yantra, deity and ritual routes
- original lightweight visual indexes for Gallery and Wallpapers
- related tool links connecting editorial content back to verified calculation surfaces
- no copied devotional editions or third-party gallery artwork embedded in the core bundle

### Stage 10 — performance, mobile, accessibility and release hardening

The production shell now includes:

- local versioned CSS/JS assets with long-lived immutable caching
- gzip/deflate support and safe delivery headers
- shared web manifest
- skip navigation and visible keyboard focus
- accurate `aria-expanded` state + Escape handling for the location chooser
- mobile access to the full tool map
- reduced-motion handling
- content-visibility on large lower-page sections
- removal of the homepage Tailwind CDN dependency
- CI budgets for CSS/JS size, SEO metadata, editorial coverage, schema, accessibility markers and crawl configuration

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
config/live.php               centralized verified/live route registry
includes/site.php             shared shell + SEO/schema/route helpers
includes/content.php          structured Devotion/Learn/Gallery content
sitemap.php / robots.php      quality-filtered crawl endpoints
manifest.webmanifest          installable app metadata
assets/tithika.css            shared production UI system
assets/tithika-site.js        shared location/date/accessibility context

api.php                       PHP API / geocoding bridge
python/choghadiya.py          solar + Choghadiya engine
python/panchang.py            Daily Panchang astronomy/rule engine
python/panchang_month.py      Month Panchang engine
python/lunar_occurrences.py   lunar Vrat occurrence adapter
python/vrat_rules.py           Smarta/Vaishnava/ISKCON + Mahadwadashi rules
python/dwadashi.py             Dwadashi + Shravana/Vishnushrinkhala rules
python/mahadwadashi.py         eight Mahadwadashi classifier
python/festival_rules.py       declarative major-festival rule registry
python/festivals.py            festival API adapter
python/muhurat_rules.py        shared Muhurat filtering substrate
python/specialized_muhurat.py  Vivah/Griha/Property/Vehicle/Sanskar profiles
python/panchang_utilities.py    Tarabalam/Chandrabalam/Panchak/Bhadra
python/panchang_reuse.py        Sunrise/Nakshatra/Ganda/Sankalpa/Vedic Clock reuse
python/muhurat_reuse.py         Hora/Panchaka Rahita/recurring auspicious Yogas
python/vrat_recurrence.py        recurring Vrat selectors and regional Shravana profiles
python/regional_calendar.py     regional solar/Amanta/Purnimanta calendars
python/sankranti.py           Nirayana solar-ingress engine
python/seasons.py             equinox/solstice engine
python/horoscope_analysis.py  unified Jyotish synthesis layer
python/interpretation.py      rule-based Jyotish interpretation layer
python/timing_timeline.py      month/year Jyotish timing timeline
python/personal_rashifal.py    personalized daily/weekly/monthly/yearly Rashifal
python/vendor/astronomy.py    vendored Astronomy Engine (MIT)

docs/DRIKPANCHANG_AUDIT.md    benchmark/product audit
docs/TITHIKA_PAGE_MAP.md      implementation map
docs/RELEASE_CERTIFICATION.md production certification + semantic route-quality tiers
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
- **Reference/Aggregate** — production-quality indexable content exists, but it is intentionally not counted as a standalone verified calculation engine.
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
9. Smarta/Vaishnava/ISKCON Ekadashi + Dwadashi/Mahadwadashi + Parana rules. ✓
10. Shared festival rule engine + migration of verified major festivals. ✓
11. Shared Muhurat rule engine foundation. ✓
12. Specialized Vivah/Griha/Property/Vehicle/Sanskar Muhurat profiles. ✓
13. Tarabalam, Chandrabalam, Panchak and Bhadra decision utilities. ✓
14. Regional solar/Amanta/Purnimanta calendar engine. ✓
15. Dedicated Nepali Bikram Sambat + Jain Kartikadi calendar adapters. ✓
16. Planet ephemeris/transit/retrograde/combustion. ✓
17. Birth/Jyotish calculators. ✓
18. Shodashavarga + structural Yogas + complete Shadbala. ✓
19. Unified evidence-first horoscope analysis. ✓
20. Auditable Jyotish interpretation knowledge layer. ✓
21. Jyotish timing and forecast timeline engine. ✓
22. Personalized daily/weekly/monthly/yearly Rashifal engine. ✓
23. SEO/schema/internal-linking and quality-filtered sitemap. ✓
24. Devotion/Learn/Gallery structured content layer. ✓
25. Performance/mobile/accessibility/release hardening. ✓
26. Production certification contract + remaining-shell queue. ✓
27. Deterministic Panchang reuse batch (8 routes). ✓
28. Deterministic Muhurat reuse batch (10 routes). ✓
29. Deterministic Vrat recurrence batch (7 routes). ✓

See `docs/DRIKPANCHANG_AUDIT.md` and `docs/TITHIKA_PAGE_MAP.md` for the full implementation plan.