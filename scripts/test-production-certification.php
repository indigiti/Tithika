<?php
declare(strict_types=1);

$_SERVER['HTTP_HOST'] = 'tithika.example';
$_SERVER['HTTPS'] = 'on';
$_SERVER['SCRIPT_NAME'] = '/index.php';
$_SERVER['REQUEST_URI'] = '/';

require dirname(__DIR__) . '/includes/site.php';

function certify(bool $condition, string $message): void {
    if (!$condition) throw new RuntimeException($message);
}

$flat = tithika_flat_routes();
$live = tithika_live_slugs();
$indexable = array_values(array_filter($flat, 'tithika_is_indexable_page'));
$noindex = array_values(array_filter($flat, fn($p) => !tithika_is_indexable_page($p)));

certify(count($flat) === 292, 'route contract must remain 292');
certify(count($live) === 229, 'verified live route count must be 229');
certify(count($indexable) === 292, 'production indexable route count must be 292');
certify(count($noindex) === 0, 'mapped noindex route count must be zero');

$completion = require dirname(__DIR__) . '/config/completion.php';
certify(count($completion) === 99, 'final completion route set must remain 99');
certify(count(array_unique($completion)) === 99, 'final completion route set must be unique');
foreach ($completion as $slug) {
    certify(isset($flat[$slug]), "completion route missing from manifest: {$slug}");
    certify(in_array($slug, $live, true), "completion route not promoted: {$slug}");
    certify(tithika_is_indexable_page($flat[$slug]), "completion route is not indexable: {$slug}");
}

$quality = require dirname(__DIR__) . '/config/quality.php';
certify(count($quality) === 99, 'completion quality taxonomy must classify all 99 routes');
certify(count(array_diff($completion, array_keys($quality))) === 0, 'completion route missing quality classification');
certify(count(array_diff(array_keys($quality), $completion)) === 0, 'quality taxonomy contains non-completion route');
$qualityCounts = array_count_values($quality);
foreach (['calculated'=>34,'aggregated'=>18,'hybrid'=>15,'reference'=>32] as $kind=>$count) {
    certify(($qualityCounts[$kind] ?? 0) === $count, "completion quality count drifted for {$kind}");
}


foreach (['panchang/nepali','calendars/nepali','calendars/jain','panchang/sunrise','panchang/nakshatra','panchang/ganda-moola','panchang/abhijit-nakshatra','panchang/vinchudo','panchang/jwalamukhi-yoga','panchang/sankalpa','panchang/vedic-clock','muhurat/shubha-hora','muhurat/panchaka-rahita','muhurat/auspicious-yoga','muhurat/guru-pushya','muhurat/sarvartha-siddhi','muhurat/amrit-siddhi','muhurat/dwipushkar','muhurat/tripushkar','muhurat/ravi-pushya','muhurat/ravi-yoga','vrat/satyanarayana','vrat/durgashtami','vrat/skanda-sashti','vrat/karthigai','vrat/rohini','vrat/sawan-somwar','vrat/mangala-gauri' ] as $slug) {
    certify(in_array($slug, $live, true), "certified route not promoted: {$slug}");
    certify(tithika_is_indexable_page($flat[$slug]), "certified route is not indexable: {$slug}");
}

foreach ([
    'python/nepali_calendar.py',
    'python/jain_calendar.py',
    'python/vendor/nepali_bs_calendar.json',
    'python/vendor/nepali_bs_calendar.LICENSE',
    'scripts/test-nepali-calendar.py',
    'scripts/test-jain-calendar.py',
    'python/panchang_reuse.py',
    'scripts/test-panchang-reuse.py',
    'python/muhurat_reuse.py',
    'scripts/test-muhurat-reuse.py',
    'python/vrat_recurrence.py',
    'scripts/test-vrat-recurrence.py',
    'config/completion.php',
    'config/quality.php',
    'python/panchang_completion.py',
    'python/muhurat_completion.py',
    'python/vrat_completion.py',
    'python/festival_calendar_completion.py',
    'python/jyotish_secondary.py',
    'python/astronomy_reference.py',
    'scripts/test-panchang-completion.py',
    'scripts/test-muhurat-completion.py',
    'scripts/test-vrat-completion.py',
    'scripts/test-festival-calendar-completion.py',
    'scripts/test-jyotish-secondary.py',
    'scripts/test-astronomy-reference.py',
] as $path) {
    certify(is_file(dirname(__DIR__) . '/' . $path), "certification file missing: {$path}");
}

$notice = (string)file_get_contents(dirname(__DIR__) . '/docs/THIRD_PARTY_NOTICES.md');
certify(str_contains($notice, 'Nepali Bikram Sambat calendar facts'), 'Nepali data provenance notice missing');
certify(str_contains($notice, 'License: MIT'), 'Nepali data license notice missing');

$queue = [];
foreach ($noindex as $page) {
    $queue[$page['group']] = ($queue[$page['group']] ?? 0) + 1;
}
ksort($queue);

echo json_encode([
    'ok'=>true,
    'route_contract'=>count($flat),
    'verified_live'=>count($live),
    'indexable'=>count($indexable),
    'mapped_noindex'=>count($noindex),
    'noindex_by_family'=>$queue,
    'newly_certified'=>$completion,
    'completion_quality'=>$qualityCounts,
], JSON_PRETTY_PRINT|JSON_UNESCAPED_SLASHES) . PHP_EOL;
