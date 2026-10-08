# Location, Timezone and Elevation Context

Tithika treats location as calculation context, not as an account profile.

## Resolution order

1. A saved browser-local location is used when present.
2. Device geolocation can provide latitude, longitude and altitude when the browser exposes it.
3. City search checks the bundled offline location index first.
4. Offline search results include an IANA timezone and do not require Nominatim or TimeAPI.
5. If no offline city matches, Nominatim can provide coordinates and TimeAPI can resolve timezone.
6. Manual latitude, longitude, IANA timezone and elevation are always available in Settings.

External services are therefore enrichment/fallback providers rather than a hard dependency for indexed cities or manual coordinates.

## Offline index

`config/location-index.php` contains a compact curated set of major Indian cities plus common international hubs. It also includes common historical aliases such as Bangalore/Bengaluru and Bombay/Mumbai.

The index is intentionally compact. It is not presented as a complete global gazetteer and does not fabricate a timezone when no indexed city is sufficiently close.

## Elevation

The saved context supports elevation from -500 m to 9000 m.

The PHP calculation gateway passes elevation to every Python calculation subprocess through `TITHIKA_ELEVATION_METERS`. The shared Panchang observer reads that value and applies it to rise/set geometry. Engines that build their own observer, such as local eclipse visibility, explicitly reuse the same helper.

Choghadiya now uses the shared Tithika rise/set observer rather than its former independent fixed-zenith approximation, so its sunrise/sunset boundaries share the same location and elevation contract as Daily Panchang.

## Privacy

Saved location context remains in browser local storage. Manual coordinates and elevation are not persisted server-side by this feature.

## Boundaries

The offline index does not attempt polygon-level global timezone inference. When a coordinate is not close enough to an indexed city, Tithika either uses the online timezone provider or the timezone explicitly selected by the user. This is preferable to silently assigning a neighboring country's timezone near borders.
