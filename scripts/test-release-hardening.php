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
ok(tithika_page_count() === 309, 'route count must remain 309');
ok(count(tithika_live_slugs()) === 232, 'verified live route registry drifted');
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
foreach (['', '/prayagraj', '/haridwar', '/ujjain', '/nashik-trimbakeshwar'] as $suffix) {
    $slug = 'festivals/mahakumbh' . $suffix;
    ok(isset($flat[$slug]), "Mahakumbh guide missing from route map: {$slug}");
    $guide = tithika_editorial_content($flat[$slug]);
    ok(($guide['lang'] ?? '') === 'mr', "Mahakumbh guide must declare Marathi: {$slug}");
    ok(!empty($guide['sections']) && !empty($guide['references']), "Mahakumbh guide missing sections or sources: {$slug}");
    foreach ($guide['links'] ?? [] as $link) {
        ok(isset($flat[$link]), "Mahakumbh guide link is not mapped: {$link}");
    }
    ok(tithika_is_indexable_page($flat[$slug]), "Mahakumbh guide not indexable: {$slug}");
    ok(!in_array($slug, tithika_live_slugs(), true), "Editorial guide must not be registered as a computed route: {$slug}");
}
foreach (tk_kumbh_pages() as $key => $page) {
    $slug = 'festivals/mahakumbh/'.$key;
    ok(isset($flat[$slug]) && tithika_is_indexable_page($flat[$slug]), "Simhastha route not indexable: {$slug}");
    ok(!tithika_is_live_page($slug), "Simhastha content must not use the calculation registry: {$slug}");
}
$kumbh = tk_kumbh_data();
ok(count(explode(' ', $kumbh['parvakal']['nashik'])) === 65, 'Nashik Parvakal count mismatch');
ok(count(explode(' ', $kumbh['parvakal']['trimbakeshwar'])) === 41, 'Trimbakeshwar Parvakal count mismatch');
ok((tk_kumbh_next('2027-08-03')[1] ?? null) === 'amrut-2', 'next snan did not advance');
ok(tk_kumbh_next('2027-09-13') === null, 'past snan should not remain active');
ok(count(array_merge(...array_column(tk_kumbh_records('faq'), 'questions'))) === 72, 'FAQ count mismatch');
ok(count(tk_kumbh_records('scriptures')) === 16, 'scripture count mismatch');

$savedGet = $_GET;
$_GET = ['venue'=>'trimbakeshwar'];
ob_start();
tk_kumbh_render('calendar');
$venueHtml = (string)ob_get_clean();
ok(str_contains($venueHtml, 'amrut-3-trimbakeshwar') && !str_contains($venueHtml, 'amrut-3-nashik'), 'venue filter must isolate the third snan');
$_GET = ['event'=>'amrut-3-trimbakeshwar'];
ob_start();
tk_kumbh_render('calendar');
$eventHtml = (string)ob_get_clean();
ok(str_contains($eventHtml, '2027-09-12') && str_contains($eventHtml, 'कुशावर्त तीर्थ'), 'deep link must show the correct event');
ok(!str_contains($eventHtml, '00:00'), 'unknown public access time must not render midnight');
$_GET = ['q'=>'Kushawarta'];
ob_start();
tk_kumbh_render('faq');
$faqHtml = (string)ob_get_clean();
ok(str_contains($faqHtml, 'कुशावर्त म्हणजे काय?') && !str_contains($faqHtml, 'कुंभमेळा म्हणजे काय?'), 'Roman alias FAQ search failed');
$_GET = $savedGet;

ok($editorialCount >= 60, 'editorial coverage unexpectedly small');
ok(tithika_indexable_count() === count(array_filter($flat, 'tithika_is_indexable_page')), 'indexable count mismatch');
ok(tithika_indexable_count() === 309, 'all mapped routes must now be production-quality indexable');

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
ok(!empty($manifest['icons'][0]['src']), 'PWA icon missing');
ok(is_file(dirname(__DIR__).'/assets/icon.svg'), 'PWA icon asset missing');
ok(is_file(dirname(__DIR__).'/service-worker.js'), 'PWA service worker missing');

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

// A previous navigation typo passed text-only audits and corrupted every page.
ok((bool)preg_match('~<a href="/panchang/"[^>]*>[^<]+</a>~', $header), 'navigation anchor closing bracket missing');
$oldHost = $_SERVER['HTTP_HOST'];
$oldServer = $_SERVER['SERVER_NAME'] ?? null;
$_SERVER['HTTP_HOST'] = 'attacker.invalid';
$_SERVER['SERVER_NAME'] = 'tithika.example';
ok(tithika_origin() === 'https://tithika.example', 'canonical origin must not trust Host when SERVER_NAME is available');
$_SERVER['HTTP_HOST'] = 'stage.digiti.in';
ok(tithika_is_staging(), 'staging origin must be blocked from indexing');
$_SERVER['HTTP_HOST'] = $oldHost;
if ($oldServer === null) unset($_SERVER['SERVER_NAME']); else $_SERVER['SERVER_NAME'] = $oldServer;

// Verify failure and recovery remain visible to the user instead of leaving
// the static "Building verified result…" skeleton on calendar pages.
$phpEngine = (string)file_get_contents(dirname(__DIR__).'/includes/engine-runtime.php');
ok(str_contains($phpEngine, '$root = dirname(__DIR__);'), 'worker root regression');
$siteJs = (string)file_get_contents(dirname(__DIR__).'/assets/tithika-site.js');
ok(str_contains($siteJs, "if(navratriFamilyPages.has(pageSlug) && $('#tkPhaseSections'))"), 'Navratri must not depend on unrelated solar API');
ok(str_contains($siteJs, "retry.textContent='Retry'"), 'calendar failure must expose retry button');
echo "SEO/content/accessibility/release hardening fixture passed\n";
