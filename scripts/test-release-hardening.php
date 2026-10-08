<?php
declare(strict_types=1);

$_SERVER['HTTP_HOST'] = 'tithika.example';
$_SERVER['HTTPS'] = 'on';
$_SERVER['SCRIPT_NAME'] = '/index.php';
$_SERVER['REQUEST_URI'] = '/';

require dirname(__DIR__) . '/includes/site.php';

function ok(bool $value, string $message): void {
    if (!$value) throw new RuntimeException($message);
}

$flat = tithika_flat_routes();
ok(tithika_page_count() === 304, 'route count must remain 304');
ok(count(tithika_live_slugs()) === 241, 'verified live route registry drifted');
ok(count(array_unique(tithika_live_slugs())) === count(tithika_live_slugs()), 'duplicate live route');
foreach (tithika_live_slugs() as $slug) {
    ok(isset($flat[$slug]), "live slug missing from route map: {$slug}");
}

$editorialGroups = ['devotion','gallery','learn'];
$editorialCount = 0;
foreach ($flat as $page) {
    if (in_array($page['group'], $editorialGroups, true)) {
        $editorialCount++;
        ok(tithika_has_editorial_content($page), 'editorial content missing: ' . $page['slug']);
    }
}
ok($editorialCount >= 60, 'editorial coverage unexpectedly small');
ok(tithika_indexable_count() === count(array_filter($flat, 'tithika_is_indexable_page')), 'indexable count mismatch');
ok(tithika_indexable_count() === 304, 'all mapped routes must now be production-quality indexable');

foreach ($flat as $page) {
    if (!tithika_is_indexable_page($page)) continue;
    $description = tithika_seo_description($page);
    ok(mb_strlen($description) >= 45, 'SEO description too short: ' . $page['slug']);
    ok(mb_strlen($description) <= 160, 'SEO description too long: ' . $page['slug']);

    $canonical = tithika_absolute_url(tithika_pretty_url($page['slug']));
    ok(str_starts_with($canonical, 'https://tithika.example/'), 'canonical must be absolute HTTPS');
    ok(str_ends_with($canonical, $page['slug'] . '/'), 'canonical slug mismatch: ' . $page['slug']);

    $schema = tithika_schema($page, $page['title'] . ' — Tithika', $description, $canonical);
    ok(($schema['@context'] ?? '') === 'https://schema.org', 'schema context missing');
    ok(count($schema['@graph'] ?? []) >= 3, 'page schema graph incomplete: ' . $page['slug']);

    foreach (tithika_related($page, 6) as $related) {
        ok($related['slug'] !== $page['slug'], 'self related link: ' . $page['slug']);
        ok(tithika_is_indexable_page($related), 'related link points to thin shell: ' . $related['slug']);
    }
}

$home = file_get_contents(dirname(__DIR__) . '/index.php');
ok($home !== false, 'index.php unreadable');
ok(!str_contains($home, 'cdn.tailwindcss.com'), 'runtime Tailwind CDN reintroduced');
ok(!preg_match('~<script[^>]+src=["\']https?://~i', $home), 'external runtime script found on homepage');

$choghadiya = (string)file_get_contents(dirname(__DIR__) . '/choghadiya.php');
ok($choghadiya !== '', 'choghadiya.php unreadable');
ok(!str_contains($choghadiya, 'cdn.tailwindcss.com'), 'runtime Tailwind CDN reintroduced on Choghadiya');
ok(str_contains($choghadiya, "tithika_asset_url('assets/choghadiya.css')"), 'Choghadiya production CSS is not base-path aware');
ok(str_contains($choghadiya, "tithika_asset_url('assets/app.js')"), 'Choghadiya app asset is not base-path aware');

$choghadiyaCss = dirname(__DIR__) . '/assets/choghadiya.css';
ok(is_file($choghadiyaCss), 'compiled Choghadiya CSS missing');
ok(filesize($choghadiyaCss) > 1000, 'compiled Choghadiya CSS unexpectedly small');

$choghadiyaJs = (string)file_get_contents(dirname(__DIR__) . '/assets/app.js');
ok(str_contains($choghadiyaJs, "window.TITHIKA_BASE"), 'Choghadiya JS missing application base path');
ok(!preg_match("~fetch\\([\"\']api\\.php~", $choghadiyaJs), 'relative Choghadiya API request reintroduced');

$originalScriptName = $_SERVER['SCRIPT_NAME'];
$_SERVER['SCRIPT_NAME'] = '/tithika/choghadiya.php';
ob_start();
include dirname(__DIR__) . '/choghadiya.php';
$choghadiyaHtml = ob_get_clean();
$_SERVER['SCRIPT_NAME'] = $originalScriptName;
ok(str_contains($choghadiyaHtml, '/tithika/assets/choghadiya.css?v='), 'Choghadiya CSS does not render from application root');
ok(str_contains($choghadiyaHtml, '/tithika/assets/app.js?v='), 'Choghadiya JS does not render from application root');
ok(str_contains($choghadiyaHtml, 'window.TITHIKA_BASE = "/tithika/"'), 'Choghadiya runtime base path is incorrect');

$site = file_get_contents(dirname(__DIR__) . '/includes/site.php');
ok($site !== false && str_contains($site, 'tk-skip-link'), 'skip link missing');
ok(str_contains($site, 'aria-expanded="false"'), 'location expanded state missing');
ok(str_contains($site, 'application/ld+json'), 'JSON-LD output missing');
ok(str_contains($site, 'rel="canonical"'), 'canonical output missing');
ok(str_contains($site, 'meta name="robots"'), 'robots meta output missing');

$js = file_get_contents(dirname(__DIR__) . '/assets/tithika-site.js');
ok($js !== false && str_contains($js, "e.key==='Escape'"), 'Escape close behavior missing');
ok(str_contains($js, "setAttribute('aria-expanded'"), 'aria-expanded synchronization missing');

$cssPath = dirname(__DIR__) . '/assets/tithika.css';
$jsPath = dirname(__DIR__) . '/assets/tithika-site.js';
ok(filesize($cssPath) < 350000, 'CSS exceeds 350 KB release budget');
ok(filesize($jsPath) < 250000, 'JavaScript exceeds 250 KB release budget');

$manifest = json_decode((string)file_get_contents(dirname(__DIR__) . '/manifest.webmanifest'), true);
ok(is_array($manifest), 'manifest invalid JSON');
ok(($manifest['display'] ?? '') === 'standalone', 'manifest display mode incorrect');
ok(($manifest['short_name'] ?? '') === 'Tithika', 'manifest short name incorrect');

$htaccess = (string)file_get_contents(dirname(__DIR__) . '/.htaccess');
ok(str_contains($htaccess, 'sitemap\.xml'), 'sitemap rewrite missing');
ok(str_contains($htaccess, 'robots\.txt'), 'robots rewrite missing');
ok(str_contains($htaccess, 'X-Content-Type-Options'), 'security headers missing');

ob_start();
$page = $flat['learn/panchang'];
tithika_render_header($page['title'], $page);
$header = ob_get_clean();
ok(str_contains($header, '<meta name="robots" content="index,follow,max-image-preview:large">'), 'quality page not indexable');
ok(str_contains($header, '<link rel="canonical"'), 'canonical not rendered');
ok(str_contains($header, 'BreadcrumbList'), 'breadcrumb schema not rendered');

ob_start();
$shell = $flat['muhurat/gowri'];
tithika_render_header($shell['title'], $shell);
$thinHeader = ob_get_clean();
ok(str_contains($thinHeader, '<meta name="robots" content="index,follow,max-image-preview:large">'), 'completed route must be indexable');

echo "SEO/content/accessibility/release hardening fixture passed\n";
