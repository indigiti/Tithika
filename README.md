# Choghadiya Modern — PHP + Python + Tailwind

A responsive location-aware Choghadiya dashboard with a PHP API layer, Python solar/Choghadiya calculation engine, and Tailwind UI.

## UI/UX v2

- Dashboard-first current Choghadiya card
- Live period progress and countdown
- Automatic browser geolocation with manual city search fallback
- Compact sticky date/location control dock
- Sunrise, sunset, daylight/night duration cards
- Rahu Kaal and next auspicious window summary
- Responsive day/night timeline cards
- Mobile Day / Night segmented view
- 12/24-hour switch
- Previous/next-day navigation
- Stronger auspicious / neutral / avoid colour semantics
- Responsive desktop, tablet and mobile layout

## Requirements

- PHP 8+
- PHP cURL extension (used for Nominatim city search / reverse geocoding)
- Python 3.9+ with `zoneinfo`
- HTTPS in production for browser geolocation
- Internet access for Tailwind CDN and OpenStreetMap Nominatim lookups

No Python pip packages or database are required.

## Deploy

Upload this folder under your web root, for example:

`public_html/choghadiya/`

Make sure PHP can execute `python3`. If the binary uses a different path, set the `PYTHON_BIN` environment variable.

Open the public HTTPS URL. The browser will request location permission on first load. If permission is blocked or denied, use the city search field.

## Calculation model

The Python engine calculates local sunrise/sunset using a 90.833° solar zenith, divides sunrise→sunset into 8 equal day periods, and sunset→next sunrise into 8 equal night periods. Weekday-specific Choghadiya sequences and Rahu Kaal daylight segments are then applied.
