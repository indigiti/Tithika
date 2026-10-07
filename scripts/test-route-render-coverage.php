<?php
declare(strict_types=1);

$_SERVER['HTTP_HOST'] = 'tithika.example';
$_SERVER['HTTPS'] = 'on';
$_SERVER['SCRIPT_NAME'] = '/index.php';
$_SERVER['REQUEST_URI'] = '/';
require dirname(__DIR__) . '/includes/site.php';

function route_ok(bool $value, string $message): void {
    if (!$value) throw new RuntimeException($message);
}

$forbidden = [
    'Calculation engine adapter pending',
    'Verified calculation data will populate this row.',
    'tk-placeholder-list',
    'Unsupported values remain intentionally blank until their engine module is validated.',
    'The final editorial content can support',
];

$flat = tithika_flat_routes();
$failures = [];
foreach ($flat as $slug => $page) {
    if (!tithika_is_indexable_page($page)) continue;
    $cmd = escapeshellarg(PHP_BINARY) . ' ' .
        escapeshellarg(__DIR__ . '/render-route.php') . ' ' .
        escapeshellarg($slug);
    $output = [];
    $code = 0;
    exec($cmd . ' 2>&1', $output, $code);
    $html = implode("\n", $output);
    if ($code !== 0) {
        $failures[] = "{$slug}: renderer exited {$code}";
        continue;
    }
    foreach ($forbidden as $needle) {
        if (str_contains($html, $needle)) {
            $failures[] = "{$slug}: placeholder renderer contains '{$needle}'";
        }
    }
    if (empty($page['live']) && !str_contains($html, '<h1>')) {
        $failures[] = "{$slug}: missing rendered H1";
    }
}
route_ok($failures === [], "Indexable route render audit failed:\n" . implode("\n", $failures));
echo "Route render coverage fixture passed for " . count($flat) . " mapped routes\n";
