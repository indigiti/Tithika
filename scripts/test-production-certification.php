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
certify(count($live) === 113, 'verified live route count must be 113');
certify(count($indexable) === 176, 'production indexable route count must be 176');
certify(count($noindex) === 116, 'mapped noindex route count must be 116');

foreach (['panchang/nepali','calendars/nepali','calendars/jain','panchang/sunrise','panchang/nakshatra','panchang/ganda-moola','panchang/abhijit-nakshatra','panchang/vinchudo','panchang/jwalamukhi-yoga','panchang/sankalpa','panchang/vedic-clock' ] as $slug) {
    certify(in_array($slug, $live, true), "new regional adapter not promoted: {$slug}");
    certify(tithika_is_indexable_page($flat[$slug]), "new regional adapter is not indexable: {$slug}");
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
    'newly_certified'=>['panchang/nepali','calendars/nepali','calendars/jain','panchang/sunrise','panchang/nakshatra','panchang/ganda-moola','panchang/abhijit-nakshatra','panchang/vinchudo','panchang/jwalamukhi-yoga','panchang/sankalpa','panchang/vedic-clock'],
], JSON_PRETTY_PRINT|JSON_UNESCAPED_SLASHES) . PHP_EOL;
