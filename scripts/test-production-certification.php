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
certify(count($live) === 179, 'verified live route count must be 179');
certify(count($indexable) === 242, 'production indexable route count must be 242');
certify(count($noindex) === 50, 'mapped noindex route count must be 50');

$completionRoutes = [
    'panchang/manvadi-tithi',
    'panchang/yugadi-tithi',
    'panchang/kalpadi-tithi',
    'panchang/kranti-samya',
    'panchang/gowri',
    'muhurat/gowri',
    'muhurat/jain-pachchakkhan',
    'muhurat/pancha-pakshi',
    'jyotish/pancha-pakshi',
    'muhurat/do-ghati',
    'muhurat/shubha-dates',
    'vrat/iskcon-ekadashi',
    'vrat/kalashtami',
    'vrat/chandra-darshan',
    'vrat/masik-janmashtami',
    'vrat/ishti-anvadhan',
    'vrat/shraddha',
    'vrat/purushottam-maas',
    'vrat/chaturmasa',
    'festivals/hindu',
    'festivals/tamil',
    'festivals/malayalam',
    'festivals/chaitra',
    'festivals/vaishakha',
    'festivals/jyeshtha',
    'festivals/ashadha',
    'festivals/shravana',
    'festivals/bhadrapada',
    'festivals/ashwina',
    'festivals/kartika',
    'festivals/margashirsha',
    'festivals/pausha',
    'festivals/magha',
    'festivals/phalguna',
    'calendars/diwali',
    'calendars/durga-puja',
    'calendars/navratri',
    'calendars/shardiya-navratri',
    'jyotish/prashna-kundali',
    'jyotish/gemstone',
    'jyotish/rudraksha',
    'jyotish/baby-name',
    'jyotish/name-initials',
    'jyotish/rashi-by-name',
    'jyotish/sahasra-chandrodaya',
    'jyotish/shraddha-tithi',
    'planets/parallel',
    'planets/ecliptic-crossings',
    'astronomy/indian-seasons',
];

foreach (['panchang/nepali','calendars/nepali','calendars/jain','panchang/sunrise','panchang/nakshatra','panchang/ganda-moola','panchang/abhijit-nakshatra','panchang/vinchudo','panchang/jwalamukhi-yoga','panchang/sankalpa','panchang/vedic-clock','muhurat/shubha-hora','muhurat/panchaka-rahita','muhurat/auspicious-yoga','muhurat/guru-pushya','muhurat/sarvartha-siddhi','muhurat/amrit-siddhi','muhurat/dwipushkar','muhurat/tripushkar','muhurat/ravi-pushya','muhurat/ravi-yoga','vrat/satyanarayana','vrat/durgashtami','vrat/skanda-sashti','vrat/karthigai','vrat/rohini','vrat/sawan-somwar','vrat/mangala-gauri' ] as $slug) {
    certify(in_array($slug, $live, true), "certified route not promoted: {$slug}");
    certify(tithika_is_indexable_page($flat[$slug]), "certified route is not indexable: {$slug}");
}

foreach ($completionRoutes as $slug) {
    certify(in_array($slug, $live, true), "six-phase route not promoted: {$slug}");
    certify(tithika_is_indexable_page($flat[$slug]), "six-phase route is not indexable: {$slug}");
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
    'python/completion.py',
    'scripts/test-completion.py',
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
    'newly_certified'=>$completionRoutes,
], JSON_PRETTY_PRINT|JSON_UNESCAPED_SLASHES) . PHP_EOL;
