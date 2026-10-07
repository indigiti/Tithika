<?php
declare(strict_types=1);

require_once __DIR__ . '/content.php';

function tithika_routes(): array {
    static $routes;
    if ($routes === null) $routes = require __DIR__ . '/../config/routes.php';
    return $routes;
}

function tithika_flat_routes(): array {
    static $flat;
    if ($flat !== null) return $flat;
    $flat = [];
    foreach (tithika_routes() as $groupKey => $group) {
        foreach ($group['pages'] as $page) {
            $page['group'] = $groupKey;
            $page['group_title'] = $group['title'];
            $page['group_icon'] = $group['icon'];
            $page['group_description'] = $group['description'];
            $flat[$page['slug']] = $page;
        }
    }
    return $flat;
}

function tithika_find_page(string $slug): ?array {
    $flat = tithika_flat_routes();
    return $flat[$slug] ?? null;
}

function tithika_live_slugs(): array {
    static $live;
    if ($live === null) $live = require __DIR__ . '/../config/live.php';
    return $live;
}

function tithika_is_live_page(string $slug): bool {
    static $lookup;
    if ($lookup === null) $lookup = array_fill_keys(tithika_live_slugs(), true);
    return isset($lookup[$slug]);
}

function tithika_is_indexable_page(array $page): bool {
    if (!empty($page['live'])) return true;
    if (tithika_is_live_page((string)$page['slug'])) return true;
    return tithika_has_editorial_content($page);
}

function tithika_base_path(): string {
    $script = str_replace('\\','/', $_SERVER['SCRIPT_NAME'] ?? '/page.php');
    $dir = rtrim(dirname($script), '/.');
    return $dir === '' ? '/' : $dir . '/';
}

function tithika_url(string $path = ''): string {
    return tithika_base_path() . ltrim($path, '/');
}

function tithika_pretty_url(string $slug): string {
    return tithika_url($slug . '/');
}

function tithika_origin(): string {
    $forwarded = strtolower(trim((string)($_SERVER['HTTP_X_FORWARDED_PROTO'] ?? '')));
    $scheme = ($forwarded === 'https' || (!empty($_SERVER['HTTPS']) && $_SERVER['HTTPS'] !== 'off')) ? 'https' : 'http';
    $host = (string)($_SERVER['HTTP_HOST'] ?? 'localhost');
    $host = preg_replace('/[^A-Za-z0-9.\-:\[\]]/', '', $host) ?: 'localhost';
    return $scheme . '://' . $host;
}

function tithika_absolute_url(string $path = ''): string {
    if (preg_match('~^https?://~i', $path)) return $path;
    return rtrim(tithika_origin(), '/') . '/' . ltrim($path, '/');
}

function tithika_current_canonical(?array $page = null): string {
    if ($page) return tithika_absolute_url(tithika_pretty_url($page['slug']));
    $path = parse_url((string)($_SERVER['REQUEST_URI'] ?? tithika_url()), PHP_URL_PATH) ?: tithika_url();
    return tithika_absolute_url($path);
}

function tithika_asset_url(string $path): string {
    $relative = ltrim($path, '/');
    $file = realpath(__DIR__ . '/../' . $relative);
    $version = ($file && is_file($file)) ? (string)filemtime($file) : '1';
    return tithika_url($relative) . '?v=' . rawurlencode($version);
}

function tithika_template_label(string $template): string {
    return match($template) {
        'daily' => 'Daily timing',
        'calendar' => 'Calendar',
        'muhurat' => 'Muhurat',
        'festival' => 'Festival calendar',
        'calculator' => 'Calculator',
        'astronomy' => 'Astronomy',
        'devotion' => 'Devotional',
        'gallery' => 'Gallery',
        'article' => 'Guide',
        'list' => 'Dates & events',
        default => 'Collection',
    };
}

function tithika_template_copy(string $template, string $title): string {
    return match($template) {
        'daily' => "Location-aware {$title} with local sunrise context, exact timings and clear day navigation.",
        'calendar' => "{$title} in a fast month/year view with regional or lunar-calendar context and date drill-down.",
        'muhurat' => "{$title} with local Panchang evidence, transparent favourable-window rules and date/location controls.",
        'festival' => "{$title} with verified observance rules, local timing evidence and related calendar context.",
        'calculator' => "{$title} as a focused calculation flow with explicit inputs, evidence and structured results.",
        'astronomy' => "{$title} with exact event timing, sidereal calculation context and chronological results.",
        'devotion' => "{$title} in a focused devotional reference with practice context and related observances.",
        'gallery' => "{$title} as a lightweight curated visual index separated from calculation-heavy pages.",
        'article' => "{$title} as a readable Tithika reference with linked concepts and calculation tools.",
        'list' => "{$title} as a structured date/event view with local Panchang context.",
        default => "{$title} organized into a modern, searchable Tithika collection.",
    };
}

function tithika_route_tokens(array $page): array {
    $text = strtolower(
        str_replace(['-','/','&'], ' ', (string)$page['slug'] . ' ' . (string)$page['title'] . ' ' . (string)($page['group_title'] ?? ''))
    );
    $tokens = preg_split('/[^a-z0-9]+/', $text, -1, PREG_SPLIT_NO_EMPTY) ?: [];
    $stop = array_fill_keys(['tithika','hindu','vedic','calendar','calculator','dates','date','daily','collection','understanding','lord','shri'], true);
    return array_values(array_unique(array_filter($tokens, fn($x) => strlen($x) > 2 && !isset($stop[$x]))));
}

function tithika_related(array $page, int $limit = 6): array {
    $tokens = tithika_route_tokens($page);
    $bridges = [
        'ekadashi'=>['vrat','dwadashi','parana'],
        'muhurat'=>['choghadiya','rahu','abhijit','tarabalam','chandrabalam'],
        'nakshatra'=>['birthstar','tarabalam','jyotish'],
        'diwali'=>['lakshmi','kartika','festival'],
        'ganesha'=>['chaturthi','vinayaka'],
        'shiva'=>['shivaratri','pradosham'],
        'kundali'=>['jyotish','dasha','varga','shadbala'],
        'marriage'=>['vivah','matching','compatibility'],
        'panchang'=>['tithi','nakshatra','yoga','karana'],
    ];

    $scores = [];
    foreach (tithika_flat_routes() as $candidate) {
        if ($candidate['slug'] === $page['slug']) continue;
        if (!tithika_is_indexable_page($candidate)) continue;

        $candidateTokens = tithika_route_tokens($candidate);
        $shared = array_intersect($tokens, $candidateTokens);
        $score = count($shared) * 4;
        if (($candidate['group'] ?? '') === ($page['group'] ?? '')) $score += 3;

        foreach ($bridges as $key=>$relatedTokens) {
            if (!in_array($key, $tokens, true)) continue;
            foreach ($relatedTokens as $term) {
                if (in_array($term, $candidateTokens, true)) $score += 5;
            }
        }

        if ($score > 0) $scores[] = ['score'=>$score,'page'=>$candidate];
    }

    usort($scores, fn($a,$b) => $b['score'] <=> $a['score'] ?: strcmp($a['page']['title'], $b['page']['title']));
    $items = array_map(fn($row) => $row['page'], array_slice($scores, 0, $limit));

    if (count($items) < $limit) {
        foreach (tithika_flat_routes() as $candidate) {
            if (count($items) >= $limit) break;
            if ($candidate['slug'] === $page['slug'] || !tithika_is_indexable_page($candidate)) continue;
            if (in_array($candidate['slug'], array_column($items, 'slug'), true)) continue;
            if (($candidate['group'] ?? '') === ($page['group'] ?? '')) $items[] = $candidate;
        }
    }
    return array_slice($items, 0, $limit);
}

function tithika_page_count(): int {
    return count(tithika_flat_routes());
}

function tithika_indexable_count(): int {
    return count(array_filter(tithika_flat_routes(), 'tithika_is_indexable_page'));
}

function tithika_seo_description(?array $page): string {
    if (!$page) return 'Tithika is a modern location-aware Panchang, Muhurat, festival, Jyotish and Vedic calendar platform.';
    $editorial = tithika_editorial_content($page);
    if ($editorial && !empty($editorial['intro'])) {
        return mb_substr(trim((string)$editorial['intro']), 0, 158);
    }
    return mb_substr(tithika_template_copy($page['template'], $page['title']), 0, 158);
}

function tithika_schema(?array $page, string $title, string $description, string $canonical): array {
    $website = [
        '@type'=>'WebSite',
        '@id'=>tithika_absolute_url(tithika_url()) . '#website',
        'url'=>tithika_absolute_url(tithika_url()),
        'name'=>'Tithika',
        'description'=>'Location-aware Panchang, Muhurat, Jyotish and Vedic calendar utilities.',
        'inLanguage'=>'en',
    ];

    $type = 'WebPage';
    if ($page && in_array($page['template'], ['article','devotion'], true)) $type = 'Article';
    if ($page && in_array($page['template'], ['gallery','collection'], true)) $type = 'CollectionPage';

    $webpage = [
        '@type'=>$type,
        '@id'=>$canonical . '#page',
        'url'=>$canonical,
        'name'=>$title,
        'description'=>$description,
        'isPartOf'=>['@id'=>$website['@id']],
        'inLanguage'=>'en',
    ];

    $graph = [$website, $webpage];
    if ($page) {
        $graph[] = [
            '@type'=>'BreadcrumbList',
            '@id'=>$canonical . '#breadcrumbs',
            'itemListElement'=>[
                ['@type'=>'ListItem','position'=>1,'name'=>'Home','item'=>tithika_absolute_url(tithika_url())],
                ['@type'=>'ListItem','position'=>2,'name'=>$page['group_title'],'item'=>tithika_absolute_url(tithika_pretty_url($page['group']))],
                ['@type'=>'ListItem','position'=>3,'name'=>$page['title'],'item'=>$canonical],
            ],
        ];
    }
    return ['@context'=>'https://schema.org','@graph'=>$graph];
}

function tithika_render_header(string $title, ?array $page = null): void {
    $routes = tithika_routes();
    $base = tithika_base_path();
    $description = tithika_seo_description($page);
    $canonical = tithika_current_canonical($page);
    $indexable = !$page || tithika_is_indexable_page($page);
    $schema = tithika_schema($page, $title . ' — Tithika', $description, $canonical);
    ?>
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
  <meta name="theme-color" content="#f8fafc">
  <meta name="color-scheme" content="light dark">
  <title><?= htmlspecialchars($title) ?> — Tithika</title>
  <meta name="description" content="<?= htmlspecialchars($description) ?>">
  <meta name="robots" content="<?= $indexable ? 'index,follow,max-image-preview:large' : 'noindex,follow' ?>">
  <link rel="canonical" href="<?= htmlspecialchars($canonical) ?>">
  <meta property="og:type" content="<?= ($page && in_array($page['template'], ['article','devotion'], true)) ? 'article' : 'website' ?>">
  <meta property="og:site_name" content="Tithika">
  <meta property="og:title" content="<?= htmlspecialchars($title) ?> — Tithika">
  <meta property="og:description" content="<?= htmlspecialchars($description) ?>">
  <meta property="og:url" content="<?= htmlspecialchars($canonical) ?>">
  <meta name="twitter:card" content="summary">
  <meta name="twitter:title" content="<?= htmlspecialchars($title) ?> — Tithika">
  <meta name="twitter:description" content="<?= htmlspecialchars($description) ?>">
  <link rel="manifest" href="<?= htmlspecialchars(tithika_url('manifest.webmanifest')) ?>">
  <script src="<?= htmlspecialchars(tithika_asset_url('assets/settings-core.js')) ?>"></script>
  <link rel="stylesheet" href="<?= htmlspecialchars(tithika_asset_url('assets/tithika.css')) ?>">
  <script type="application/ld+json"><?= json_encode($schema, JSON_UNESCAPED_SLASHES|JSON_UNESCAPED_UNICODE|JSON_HEX_TAG|JSON_HEX_AMP) ?></script>
</head>
<body>
<a class="tk-skip-link" href="#main-content">Skip to content</a>
<div class="tk-shell">
  <header class="tk-header">
    <a class="tk-brand" href="<?= htmlspecialchars($base) ?>" aria-label="Tithika home">
      <span class="tk-logo" aria-hidden="true">ति</span>
      <span><strong>Tithika</strong><small>Vedic time, reimagined</small></span>
    </a>
    <nav class="tk-nav" aria-label="Primary">
      <?php foreach (array_slice($routes, 0, 6, true) as $key => $group): ?>
        <a href="<?= htmlspecialchars(tithika_pretty_url($key)) ?>"<?= ($page && $page['group'] === $key) ? ' class="is-active" aria-current="page"' : '' ?>><?= htmlspecialchars($group['title']) ?></a>
      <?php endforeach; ?>
      <a href="<?= htmlspecialchars(tithika_url('site-map.php')) ?>">All tools</a>
      <a href="<?= htmlspecialchars(tithika_url('settings/')) ?>">Settings</a>
    </nav>
    <a class="tk-mobile-tools" href="<?= htmlspecialchars(tithika_url('site-map.php')) ?>">All tools</a>
    <button class="tk-place-button" id="tkPlaceButton" type="button" aria-expanded="false" aria-controls="tkPlacePanel"><span aria-hidden="true">⌖</span><b id="tkPlaceText">Location</b></button>
  </header>
  <div class="tk-place-panel" id="tkPlacePanel" hidden aria-label="Location chooser">
    <div class="tk-place-search">
      <input id="tkCitySearch" autocomplete="off" inputmode="search" aria-label="Search city or place" placeholder="Search city or place">
      <button id="tkDetectLocation" type="button" title="Use current location" aria-label="Use current location">⌖</button>
    </div>
    <div id="tkSearchResults" class="tk-search-results" aria-live="polite"></div>
    <p>Your location is used only to calculate local solar timings.</p>
  </div>
  <main id="main-content">
<?php
}

function tithika_render_footer(): void {
    $base = tithika_base_path();
    ?>
  </main>
  <footer class="tk-footer">
    <div><strong>Tithika</strong><span>Traditional calendar conventions in a modern, evidence-first utility experience.</span></div>
    <div>
      <a href="<?= htmlspecialchars($base) ?>">Home</a>
      <a href="<?= htmlspecialchars(tithika_url('site-map.php')) ?>">Site map</a>
      <a href="<?= htmlspecialchars(tithika_url('sitemap.xml')) ?>">XML sitemap</a>
      <a href="<?= htmlspecialchars(tithika_pretty_url('learn/faq')) ?>">FAQ</a>
    </div>
  </footer>
</div>
<div class="tk-toast" id="tkToast" role="status" aria-live="polite" hidden></div>
<script>
window.TITHIKA_BASE = <?= json_encode($base, JSON_UNESCAPED_SLASHES) ?>;
</script>
<script src="<?= htmlspecialchars(tithika_asset_url('assets/tithika-site.js')) ?>" defer></script>
<script src="<?= htmlspecialchars(tithika_asset_url('assets/settings.js')) ?>" defer></script>
</body>
</html>
<?php
}
