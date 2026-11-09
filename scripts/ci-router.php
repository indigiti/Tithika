<?php
declare(strict_types=1);
// Development/CI-only Apache rewrite emulator. Never ship in public webroot.
$path = parse_url((string)($_SERVER['REQUEST_URI'] ?? '/'), PHP_URL_PATH) ?: '/';
$path = rawurldecode($path);
if (str_contains($path, '..')) {
    http_response_code(400);
    exit;
}
$root = dirname(__DIR__);
$static = realpath($root . $path);
if ($static && is_file($static) && str_starts_with($static, $root . DIRECTORY_SEPARATOR)) {
    if (str_contains($static, '/docs/') || str_contains($static, '/scripts/') || str_contains($static, '/config/') || str_contains($static, '/includes/') || str_contains($static, '/python/')) {
        http_response_code(403);
        exit;
    }
    return false;
}
if ($path === '/' || $path === '/index.php') { require $root . '/index.php'; return true; }
$direct = [
    '/api.php' => '/api.php',
    '/sitemap.xml' => '/sitemap.php',
    '/robots.txt' => '/robots.php',
    '/intelligence/' => '/intelligence.php',
    '/calendar.ics' => '/calendar.php',
    '/notifications/' => '/notifications.php',
    '/settings/' => '/settings.php',
    '/muhurat/choghadiya/' => '/choghadiya.php',
];
if (isset($direct[$path])) { require $root . $direct[$path]; return true; }
$_GET['slug'] = trim($path, '/');
require $root . '/page.php';
return true;
