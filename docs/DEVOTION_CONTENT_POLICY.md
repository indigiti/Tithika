# Devotion Corpus and Source Policy

Tithika's Devotion layer separates **editorial context** from **sacred source text**.

## Current corpus

All 41 mapped Devotion routes have a route-specific corpus entry in `includes/devotion.php`.

Each entry can contain:

- subject summary;
- practice context;
- calendar/observance connection;
- collection or structural index;
- related Tithika calculation/content routes;
- explicit source and edition status.

The explanatory prose and taxonomy metadata in this corpus are original Tithika editorial content.

## Sacred text boundary

The registry deliberately does not embed full Aarti, Chalisa, Stotra, Mantra, Kavacha, scripture or ritual editions by default.

A full sacred text may be added only when the edition is:

1. demonstrably public domain, or
2. supplied under a compatible license, or
3. created/translated specifically for Tithika with documented rights.

The entry should then record source title, edition/editor where applicable, language/script, license or public-domain basis, and whether transliteration/translation is original or sourced.

This avoids silently mixing recensions, inventing missing verses or copying modern copyrighted editions.

## Collections versus works

Collection pages such as Aarti, Chalisa, Stotram, Mantra, Ashtakam and Kavacham expose a named corpus index. A named work such as Sundarkand or Nama Ramayanam exposes structural context and related observances.

Yantra and ritual pages follow the same rule: orientation and timing context can be original editorial material, but geometry, initiation-dependent Mantra or ritual procedure must come from an identified source tradition.

## Calculation boundary

Devotion pages never hard-code festival or Muhurat dates. Links point back to Tithika's verified Panchang, Vrat, Festival and Muhurat engines so location/date calculation stays independent of editorial content.

## Localization

The registry is structured so future Hindi/Marathi/Tamil/etc. editions can translate metadata without duplicating route or calculation logic. Sacred text language and transliteration should remain separate fields from interface translation.
