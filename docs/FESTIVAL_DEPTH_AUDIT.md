# Festival-depth audit: Navratri and adjacent calendar families

Date: 2026-11-09
Source code: `config/routes.php`, `config/live.php`, `config/completion.php`,
`python/festival_rules.py`, `python/festival_calendar_completion.py`,
`python/navratri_calendar.py`, `page.php`, `assets/tithika-site.js`.

## What was missing

1. Two of the four annual Navratris (Magha and Ashadha Gupta) had no dedicated
   routes, despite their observances being separate dates and month profiles.
2. Shardiya and Chaitra calendar routes showed generic topic-list references,
   not local astronomical day-by-day dates.
3. `festivals/navratri` calculated only the autumn observance and offered no
   direct variant links; a user could mistake it for an exhaustive Navratri hub.
4. Tithi-start/Tithi-end, Sandhi and Ghatasthapana evidence were not visible
   together in the calendar experience.
5. Generic festival-calendar theme rows sometimes have no dates: they are
   editorial reference entries, not calculation-backed annual calendars.
6. CI counted route coverage and output presence but did not test four
   Navratri variants against independently published date anchors.

## Implemented in feature/navratri-four-variants

- Annual overview: `/calendars/navratri/`.
- Detail routes: `/calendars/shardiya-navratri/`,
  `/calendars/chaitra-navratri/`,
  `/calendars/magha-gupta-navratri/`,
  `/calendars/ashadha-gupta-navratri/`.
- Muhurat comparison: `/festivals/ghatasthapana/`.
- Old `/festivals/navratri/` links to the family hub and each variant.
- Exact Shukla Tithi boundaries from the existing Astronomy Engine, local
  sunrise placement, kshaya/vriddhi flags, named Navdurga reference content.
- Morning Ghatasthapana with optional Abhijit and interval-wide cautions.
- Calculated Sandhi interval and separate Rama Navami / Vijayadashami rule
  cross-links, not fixed offsets from a Gregorian date.
- Responsive overview + chronological nine-Tithi cards, location/year context,
  accessible links, time labels and explicit evidence limitations.

## External benchmark anchors

India date anchors (2026; times depend on city):
- Magha Gupta: 2026-01-19
- Chaitra: 2026-03-19
- Ashadha Gupta: 2026-07-15
- Shardiya: 2026-10-11

Research sources (for independent validation, not for reproduced text or images):
- https://www.drikpanchang.com/navratri/magha-gupta-navratri-dates.html
- https://www.drikpanchang.com/navratri/chaitra-vasant-navratri-dates.html
- https://www.drikpanchang.com/navratri/ashadha-gupta-navratri-dates.html
- https://www.drikpanchang.com/navratri/ashwin-shardiya-navratri-dates.html
- https://www.drikpanchang.com/navratri/shardiya-navratri-ghatasthapana.html
- https://sarvapanchang.com/navratri

The correctness threshold is not simply reproducing a benchmark's day count.
A kshaya Tithi might be omitted or two Tithis might correspond to one civil
date. Tithika does not fabricate independent dates to fill nine visual rows.

## Additional gaps requiring separate certification

| Family | Existing implementation | Next verification |
|---|---|---|
| Diwali sub-festival calendar | Dated Diwali selector plus theme references | Dhanteras, Naraka Chaturdashi, Govardhan, Bhai Dooj selectors |
| Durga Puja day sequence | Mahashtami/Sandhi selector plus theme references | Shashthi, Saptami, Navami, visarjan tradition profiles |
| Onam / Malayalam | Regional solar calculations plus topic references | Atham-to-Thiruvonam Nakshatra selectors |
| Chhath | Theme reference rows only for subevents | Sunset/sunrise Arghya selectors and region validation |
| Mysore Dasara / Dashain | Theme rows with partial date links | Distinct local observance and day rules |
| Saraswati Puja | Theme references | Seasonal and regional Puja selectors |
| Gujarati Diwali / Tihar | Generic subevent collection | Local month/era and sunset selectors |
| Puja Vidhi collection | Structured reference steps | Source review, translation and editorial depth |

Avoid declaring those calendars fully computed until each named observance
has a dedicated selector, multiple geographic/year benchmarks, and a UI that
distinguishes calculated dates from descriptive reference material.

## Release boundary

The PR should be merged only after the new semantic fixtures and existing
Panchang/Muhurat/Jyotish/SEO release workflow pass. Production deployment is
separate and requires DigiOps artifact and staging smoke verification.
