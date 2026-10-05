# Tithika

A modern, location-aware Vedic calendar and Muhurat web experience built with PHP, Python and Tailwind.

## Current experience

### Home — `index.php`
The root page is now a modern product-style Panchang dashboard inspired by clean app interfaces rather than legacy information-dense calendar pages.

It includes:

- automatic browser geolocation
- manual city search fallback
- live current Choghadiya
- active-period progress and countdown
- local sunrise and sunset
- Rahu Kaal
- next favourable Choghadiya
- responsive day timeline
- utility/Bento navigation for Panchang, Muhurat, festivals and planetary modules
- mobile bottom navigation and mobile location sheet

### Choghadiya — `choghadiya.php`

The complete working Choghadiya utility remains available as a dedicated page with:

- day and night Choghadiya
- automatic location detection
- manual place search
- current-period highlighting
- live countdown
- Rahu Kaal
- local sunrise/sunset
- 12/24-hour mode
- date navigation
- responsive mobile Day/Night segmented view

## Architecture

```text
index.php                modern Tithika home
choghadiya.php           full Choghadiya tool
api.php                  PHP API/geocoding bridge
assets/home.js           homepage interactions
assets/app.js            Choghadiya interactions
python/choghadiya.py     solar + Choghadiya calculation engine
```

## Requirements

- PHP 8+
- PHP cURL extension
- Python 3.9+ with `zoneinfo`
- HTTPS in production for browser geolocation
- Internet access for Tailwind CDN and OpenStreetMap Nominatim lookups

No database or Python pip package is currently required.

## Calculation model

The Python engine calculates sunrise and sunset using a 90.833° solar zenith, divides sunrise→sunset into eight equal local day periods and sunset→next sunrise into eight equal local night periods, then applies weekday-specific Choghadiya sequences and Rahu Kaal segments.

## Design direction

Tithika is intentionally being structured as a collection of focused utilities instead of reproducing a single long legacy Panchang page. The next logical modules are Daily Panchang, Muhurat, Festival/Vrat calendars and planetary events.
