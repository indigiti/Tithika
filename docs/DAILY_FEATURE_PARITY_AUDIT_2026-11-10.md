# Tithika daily-feature parity audit — 2026-11-10

Baseline: main a56f535c90052884be2f821e4927311446f167ab.
This audit uses user-supplied screenshots solely as a functional benchmark, not a source of proprietary content or code.

## Verified reasons the screenshots were not implemented

1. Release checks mainly counted valid routes, SEO state and isolated engine fixtures instead of requiring complete page-level features.
2. The daily page presented sunrise-state cards and lists while Panchang's already-calculated start/end timestamps were not shown as a proportional timeline.
3. The home dashboard aggregator covered Ekadashi, Pradosh, Sankashti, Sankranti, planetary ingress and retrograde stations, but not the full daily festival and angular-aspect catalog.
4. Independent Vedic clock, Lagna, Kundali, Chandrabalam, Tarabalam, Sankalpa and Panchaka Rahita routes had not been assembled into the daily experience.
5. Some traditional classifications require additional rule registries, provenance and independent reference validation; a route existing is not evidence those rules are implemented.
6. The earlier PR #36 repaired Python worker paths and stuck Navratri loading. It was not a daily-feature completeness milestone.

## Implemented in this branch

- Dedicated comprehensive section on the canonical daily Panchang route.
- Exact time-weighted Tithi/Nakshatra/Yoga/Karana tracks over the local sunrise-to-next-sunrise Hindu day.
- Consolidated sunrise-state details with solar and lunar times.
- Calculated auspicious and caution intervals.
- Independently loaded upcoming observance and planetary events, with coverage limitations disclosed.
- Live 60-Ghati and 30+30-Ghati readout; a selected historical or future date is marked non-live.
- On-demand sidereal D1 Lagna and Graha preview using the existing Kundali engine.
- Direct discoverability of Sankalpa, Chandrabalam, Tarabalam, Panchaka Rahita, Udaya Lagna, Rashifal and festival tools.
- Route-conditional assets and a feature-completeness regression fixture.

## Still genuinely missing or incomplete

| Capability | Status | Required work |
| --- | --- | --- |
| Complete Diwali/Bhai Dooj/Gujarati New Year and regional festival daily feed | Not covered by current aggregator | New festival selector integration and regional tests |
| Angular planetary conjunction/aspect events, Nakshatra/Pada entries | Not in current dashboard feed | More event types and exact timestamp benchmarks |
| Aadal/Vidal, Dur Muhurta, Varjyam, Baana and other caution windows | Not consolidated | Dedicated traditional rule adapters and tests |
| Anandadi/Tamil yoga, Disha Shool, Homahuti, Agnivasa, Shivavasa, Nivas | Not completed as a certified daily view | Tradition-aware rule pack |
| Chandrabalam and Tarabalam all-sign/day matrix | Personalized utilities exist | Batch daily matrix with per-period transitions |
| Panchaka Rahita plus Udaya Lagna combined table | Both routes exist separately | Combined timeline table with evidence |
| Various Vikram/Gujarati/Kartikadi calendars | Some alternative contexts exist | Separate year rollover and regional conventions |
| Generic daily twelve-sign Rashifal copy | Personalized engine exists | Distinct reviewed editorial product, not astronomical facts |
| Festival images/illustrations | Not delivered | Original/licensed assets with metadata |
| Reference parity against screenshots | Unverified | Fixed-date Mumbai checks plus other cities and years |

## Release acceptance

Do not mark this milestone fully complete until each feature is calculated or clearly identified as editorial/unavailable. Verify exact Mumbai 2026-11-10 values independently, near-midnight transitions, day/night proportions, multi-city timezones and tradition variants. Run automated CI, browser smoke, responsive/accessible tests and staging API checks. Merge only after green checks on the feature head; deploy via the existing DigiOps release artifact on main. Avoid DB or framework migrations.
