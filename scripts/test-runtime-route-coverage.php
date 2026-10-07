<?php
declare(strict_types=1);

require dirname(__DIR__) . '/includes/site.php';

$root = dirname(__DIR__);
$php = PHP_BINARY;
$bad = [
    'Calculation engine adapter pending',
    'Verified calculation data will populate this row.',
    'Month-first navigation',
    'mapped into Tithika as a focused reading page',
    'Fast, lazy-loaded visual browsing',
    'Primary timing / result',
    'Unsupported values remain intentionally blank until their engine module is validated.',
];
$fail = [];

foreach (tithika_flat_routes() as $slug => $page) {
    if (!tithika_is_indexable_page($page)) continue;
    if (!empty($page['live']) && $page['live'] === 'choghadiya.php') continue;

    $code = '$_GET["slug"]=' . var_export($slug, true) . ';'
        . '$_SERVER["HTTP_HOST"]="tithika.example";'
        . '$_SERVER["HTTPS"]="on";'
        . '$_SERVER["SCRIPT_NAME"]="/index.php";'
        . '$_SERVER["REQUEST_URI"]=' . var_export('/' . $slug . '/', true) . ';'
        . 'include ' . var_export($root . '/page.php', true) . ';';
    $proc = proc_open([$php, '-d', 'display_errors=1', '-r', $code], [1=>['pipe','w'],2=>['pipe','w']], $pipes, $root);
    if (!is_resource($proc)) throw new RuntimeException("unable to render {$slug}");
    $html = stream_get_contents($pipes[1]); fclose($pipes[1]);
    $err = stream_get_contents($pipes[2]); fclose($pipes[2]);
    $exit = proc_close($proc);
    if ($exit !== 0) {
        $fail[] = "{$slug}: render exit {$exit}: " . trim($err);
        continue;
    }
    foreach ($bad as $needle) {
        if (str_contains($html, $needle)) {
            $fail[] = "{$slug}: reached demo/fallback UI: {$needle}";
            break;
        }
    }
}

if ($fail) {
    fwrite(STDERR, implode("\n", $fail) . "\n");
    exit(1);
}
echo "Runtime route coverage fixture passed: no indexable route reaches demo/fallback UI\n";
