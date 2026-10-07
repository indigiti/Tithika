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
ok(tithika_page_count() === 292, 'route count must remain 292');
ok(count(tithika_live_slugs()) === 159, 'verified live route registry drifted');
ok(count(array_unique(tithika_live_slugs())) === count(tithika_live_slugs()), 'duplicate live route');
ok(count(tithika_aggregate_slugs()) === 21, 'calculated aggregate registry drifted');
ok(count(tithika_reference_slugs()) === 49, 'structured reference registry drifted');
ok(count(array_intersect(tithika_live_slugs(), tithika_aggregate_slugs())) === 0, 'live/aggregate overlap');
ok(count(array_intersect(tithika_live_slugs(), tithika_reference_slugs())) === 0, 'live/reference overlap');
ok(count(array_intersect(tithika_aggregate_slugs(), tithika_reference_slugs())) === 0, 'aggregate/reference overlap');
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
ok(tithika_indexable_count() === 292, 'all mapped routes must now be production-quality indexable');

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

$api = (string)file_get_contents(dirname(__DIR__) . '/api.php');
ok(str_contains($api, "65536"), 'API request body size limit missing');
ok(str_contains($api, "Search query too long"), 'city search length guard missing');
ok(str_contains($api, "CURLOPT_FOLLOWLOCATION => false"), 'external HTTP redirect following must stay disabled');

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
