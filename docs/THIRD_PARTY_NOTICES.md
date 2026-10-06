# Third-Party Notices

## Astronomy Engine

Tithika vendors Astronomy Engine for astronomical position and rise/set calculations.

- Project: Astronomy Engine
- Author: Don Cross
- Upstream repository: https://github.com/cosinekitty/astronomy
- Vendored file: `python/vendor/astronomy.py`
- Upstream blob pinned when vendored: `1a48fdf620540df22fcf421d0df0c2c016999e52`
- License: MIT

The complete MIT license notice is retained at the top of the vendored source file.

Tithika's Panchang-specific Lahiri/Chitrapaksha conversion, Hindu calendar state logic, transition search, lunar-month mapping, and Muhurta rules are implemented separately in `python/panchang.py`.


## Nepali Bikram Sambat calendar facts

Tithika vendors the Bikram Sambat civil month-length and Baisakh-1 anchor table from the MIT-licensed Nepali Calendar project, then implements its own Python conversion and Panchang integration.

- Project: Nepali Calendar / `@sushill/bikram-sambat`
- Upstream repository: https://github.com/sushilldhakal/nepali-calendar
- Upstream file: `packages/bikram-sambat/src/bs-calendar-data.json`
- Vendored file: `python/vendor/nepali_bs_calendar.json`
- License: MIT
- Upstream data note: BS 2000–2099 is the official lookup range; outer embedded years are Sankranti-estimated.

The upstream MIT license is retained beside the vendored data in `python/vendor/nepali_bs_calendar.LICENSE`. Tithika's AD↔BS conversion and Lahiri Panchang integration are implemented separately in `python/nepali_calendar.py`.
