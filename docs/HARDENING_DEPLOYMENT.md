# Tithika Hardening / DigiOps deployment gates

## Required production configuration
- PHP 8.2+ with proc_open enabled; Python 3.9+ available to PHP-FPM.
- TITHIKA_PUBLIC_ORIGIN=https://your-approved-production-domain (required for canonical origin safety; no trailing path).
- TITHIKA_ENV=production (use staging for test deployments).
- TITHIKA_MAX_ENGINE_WORKERS=4 (per application/server local worker slots; tune with capacity tests).
- TITHIKA_LOCK_DIR=<private writable directory outside the document root>.
- PYTHON_BIN=<absolute executable path> if python3 is not available in PATH.

## Security notes
- The static service worker caches only same-origin CSS/JS/SVG under assets. API results, HTML pages, profiles and birth details are never cached by it.
- The deployed webroot excludes docs/ and scripts/. The private artifact contains internal documentation and test code.
- PHP calculation admission control is per server filesystem; clustered deployments require a shared external admission service or queue.
- Input size, output size and timeout protections are not a substitute for a global rate limiter/WAF at ingress.
- Location lookup providers can have separate rate/usage policies. Apply network-level rate limits and cache geocoding when deploying.
- Personal Kundali records currently persist in browser localStorage. Deploy production on a dedicated hostname, separate from other applications, and obtain affirmative consent before implementing synchronization.

## Release gates still required
1. Successful GitHub Actions lint & build on exact merged main commit.
2. HTTP 200 smoke tests on staging homepage, representative Panchang/Muhurat/Kundali pages, API and ICS.
3. Validate expected 404/413/422/503 errors without internal path leakage.
4. Verify document root, cache headers, staging X-Robots-Tag and robots disallow; production canonical origin and sitemap.
5. Browser E2E at mobile and desktop widths; keyboard/accessibility and location/date navigation.
6. Load test bounded Python worker population, low tail latency, and healthy recovery under pressure.
7. Independently compare location-aware Panchang and festival dates against external astronomical/observance benchmarks.
8. DigiOps deployment artifact, rollback and post-deploy smoke checks.

No production readiness claim is justified until these gates pass.
