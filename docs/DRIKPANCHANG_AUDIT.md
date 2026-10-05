# DrikPanchang → Tithika Product Audit

Scan date: 2026-10-06

Benchmark reviewed:
- https://www.drikpanchang.com/
- https://www.drikpanchang.com/panchang/hindu-panchangs.html
- https://www.drikpanchang.com/panchang/panchang-utilities.html
- https://www.drikpanchang.com/calendars/vedic-calendars.html
- https://www.drikpanchang.com/muhurat/muhurat.html
- https://www.drikpanchang.com/vrats/hindu-vrat-list.html
- https://www.drikpanchang.com/festivals/hindu-festivals-collection.html
- https://www.drikpanchang.com/utilities/astrology-utilities.html
- https://www.drikpanchang.com/astrology/vedic-astrology.html
- https://www.drikpanchang.com/lyrics/devotional-lyrics.html
- https://www.drikpanchang.com/gallery/gallery.html
- https://www.drikpanchang.com/tutorials/drikpanchang-tutorials.html

## What the benchmark does well

1. Very broad product coverage across Panchang, regional calendars, Muhurat, Vrat, festivals, Jyotish, astronomy, devotional content and visual collections.
2. Location-dependent daily calculation is central to the product rather than an afterthought.
3. Strong internal linking between related Hindu calendar concepts.
4. Deep regional coverage rather than one generic Hindu calendar.
5. Date-driven pages are useful for repeat visits and search.

## Upgrade opportunities for Tithika

### Information architecture

The benchmark exposes a very large global navigation on most pages. Tithika replaces that with:
- 10 clear product families.
- One compact primary navigation.
- A full searchable/browsable site map.
- Contextual "related tools" links within each page family.
- Mobile-first navigation instead of desktop mega-menu behavior compressed onto small screens.

### Shared context

Location, date, timezone and time-format behavior should be global application state.

Tithika architecture:
```
User location/date
      ↓
Shared Context Layer
      ↓
Panchang | Calendar | Muhurat | Vrat | Festival | Jyotish | Astronomy
```

Changing the city or date should not force a user to repeat the same input when changing tools.

### Performance

Tithika should avoid a separate large page implementation for every utility.

Current architecture:
- `config/routes.php` = route/product manifest
- `includes/site.php` = shared shell
- `page.php` = page renderer
- `assets/tithika.css` = shared UI bundle
- `assets/tithika-site.js` = shared date/location context
- specialized calculation modules load only on pages that require them

Targets:
- no Tailwind CDN on mapped utility pages
- no duplicated mega-navigation HTML
- no synchronous image-heavy gallery assets on calculation pages
- native lazy-loading for future images
- cache long-lived CSS/JS
- cache calculation responses by location/date/engine version
- precompute year calendars where safe
- use server-side data first; hydrate only live clocks/current-state elements
- avoid loading Jyotish/planetary engines on simple devotional/article pages

### UI/UX

Legacy table-heavy layouts are converted to specific interaction patterns:

| Data type | Tithika pattern |
| --- | --- |
| Daily Panchang | summary cards + progressive details |
| Muhurat | timeline + good/neutral/avoid states |
| Month/year calendar | responsive calendar grid |
| Festival/Vrat | chronological cards + filters |
| Calculator | input → result flow |
| Planet events | timeline |
| Devotional text | distraction-light reader |
| Gallery | lazy-loaded masonry/grid |
| Reference/tutorial | readable article + linked concepts |

### Data integrity

Do not display fabricated Tithi, Nakshatra, Yoga, Karana, planetary or Jyotish results.

A page can be visually complete while its specialized calculation adapter remains disabled. Production status must be explicit in code/QA until the corresponding engine is verified.

## Calculation-engine roadmap

1. Solar foundation — sunrise, sunset, timezone, DST.
2. Panchang astronomy — Sun/Moon longitude and ayanamsha.
3. Tithi / Nakshatra / Yoga / Karana transitions.
4. Lunar month and Paksha.
5. Moonrise / moonset.
6. Auspicious/in-auspicious daily timings.
7. Festival rule engine.
8. Muhurat rule engine.
9. Planet ephemeris, transit, retrograde and combustion.
10. Birth/Jyotish calculators.

## Regional strategy

Do not fork the full application for every regional Panchang.

Use:
```
Astronomical facts
       +
Regional rule profile
       +
Language / labels
       =
Regional Panchang
```

Regional profiles should control month naming, era, festival rules, day-boundary conventions and presentation labels.

## SEO / URL strategy

Each logical product page has a stable route such as:
- `/panchang/daily/`
- `/calendars/tamil/`
- `/muhurat/vivah/`
- `/vrat/ekadashi/`
- `/festivals/hindu/`
- `/jyotish/birthstar/`
- `/planets/transit/`

Year/date/location should primarily be parameters/state, not duplicated application code.

## Copyright / product differentiation

Tithika uses the benchmark to understand feature coverage and information architecture. Do not copy DrikPanchang branding, artwork, written explanations, proprietary calculations, page markup, or visual theme. Tithika should develop its own calculation implementation, editorial content and product identity.
