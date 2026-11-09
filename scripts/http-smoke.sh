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
for slug in calendars/navratri calendars/shardiya-navratri calendars/chaitra-navratri calendars/magha-gupta-navratri calendars/ashadha-gupta-navratri festivals/ghatasthapana; do
  route_html="$(curl -fsS "http://127.0.0.1:18765/$slug/")"
  grep -q 'tkPhaseSections' <<<"$route_html" || { echo "Navratri calculator missing for $slug"; exit 1; }
  grep -q 'noindex,follow' <<<"$route_html" || { echo "Staging noindex missing for $slug"; exit 1; }
done
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

# Previously only malformed requests were tested: a broken subprocess path
# passed all those gates and took every live calculator offline.
payload='{"lat":19.076,"lon":72.8777,"city":"Mumbai, India","timezone":"Asia/Kolkata","date":"2026-11-09","hour24":false}'
assert_json() {
  local response="$1" family="$2"
  printf '%s' "$response" | python3 -c '
import json,sys
body=json.load(sys.stdin)
assert body.get("ok") is True, body
if len(sys.argv)>1 and sys.argv[1] != "-":
    assert body.get("family") == sys.argv[1], body
' "$family"
}
solar="$(curl --silent --show-error --fail --max-time 30 -H 'Content-Type: application/json' --data "$payload" 'http://127.0.0.1:18765/api.php?action=calculate')"
assert_json "$solar" "-"
navratri="$(curl --silent --show-error --fail --max-time 30 -H 'Content-Type: application/json' --data "${payload%?},\"slug\":\"calendars/navratri\"}" 'http://127.0.0.1:18765/api.php?action=phase-completion')"
assert_json "$navratri" "navratri-calendar"
printf '%s' "$navratri" | python3 -c 'import json,sys; d=json.load(sys.stdin); assert len(d["navratri"]["variants"])==4; assert d["navratri"]["overview"]'
detail="$(curl --silent --show-error --fail --max-time 30 -H 'Content-Type: application/json' --data "${payload%?},\"slug\":\"calendars/shardiya-navratri\"}" 'http://127.0.0.1:18765/api.php?action=phase-completion')"
assert_json "$detail" "navratri-calendar"
printf '%s' "$detail" | python3 -c 'import json,sys; d=json.load(sys.stdin); assert len(d["navratri"]["variants"][0]["days"])==9'
echo "HTTP smoke passed: routes, SEO, PWA, API rejection and real Python-backed calendar responses."
