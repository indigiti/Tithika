#!/usr/bin/env bash
set -euo pipefail
export TITHIKA_ENV=staging
export TITHIKA_MAX_ENGINE_WORKERS=2
php -S 127.0.0.1:18765 scripts/ci-router.php >/tmp/tithika-http-smoke.log 2>&1 &
server_pid=$!
trap 'kill "$server_pid" 2>/dev/null || true' EXIT
for i in {1..40}; do
  if curl --silent --fail http://127.0.0.1:18765/ >/dev/null; then break; fi
  sleep 0.2
done

home="$(curl -fsS http://127.0.0.1:18765/)"
grep -q 'Tithika' <<<"$home"
grep -q 'noindex,follow' <<<"$home"
daily="$(curl -fsS http://127.0.0.1:18765/panchang/daily/)"
grep -q 'Daily Panchang' <<<"$daily"
grep -q 'noindex,follow' <<<"$daily"
curl -fsS http://127.0.0.1:18765/robots.txt | grep -q 'Disallow: /'
curl -fsS http://127.0.0.1:18765/sitemap.xml | grep -q '<urlset'
curl -fsS http://127.0.0.1:18765/service-worker.js | grep -q 'tithika-assets'
curl -fsS http://127.0.0.1:18765/assets/icon.svg | grep -q '<svg'

get_status() {
  curl -sS -o /tmp/tithika-http-response -w '%{http_code}' "$@"
}
status="$(get_status -H 'Content-Type: application/json' --data '{invalid-json' 'http://127.0.0.1:18765/api.php?action=calculate')"
[[ "$status" == 400 ]] || { echo "Expected malformed JSON 400; got $status"; exit 1; }
status="$(get_status -H 'Content-Type: application/json' --data-binary @<(head -c 33000 /dev/zero | tr '\0' x) 'http://127.0.0.1:18765/api.php?action=calculate')"
[[ "$status" == 413 ]] || { echo "Expected oversized JSON 413; got $status"; exit 1; }
status="$(get_status 'http://127.0.0.1:18765/api.php?action=does-not-exist')"
[[ "$status" == 404 ]] || { echo "Expected unknown API 404; got $status"; exit 1; }
echo "HTTP smoke passed: homepage, dynamic route, staging SEO, assets, 400/413/404 gates."
