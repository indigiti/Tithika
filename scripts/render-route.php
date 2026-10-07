<?php
declare(strict_types=1);

$slug = trim((string)($argv[1] ?? ''), '/');
if ($slug === '') {
    fwrite(STDERR, "slug required\n");
    exit(2);
}
$_GET['slug'] = $slug;
$_SERVER['HTTP_HOST'] = 'tithika.example';
$_SERVER['HTTPS'] = 'on';
$_SERVER['SCRIPT_NAME'] = '/page.php';
$_SERVER['REQUEST_URI'] = '/' . $slug . '/';
require dirname(__DIR__) . '/page.php';
