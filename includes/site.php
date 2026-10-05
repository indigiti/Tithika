<?php
declare(strict_types=1);

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
        'daily' => "A location-aware daily view for {$title}, designed around the few values you need first and deeper details on demand.",
        'calendar' => "{$title} in a fast month/year view with location context, filters and date drill-down.",
        'muhurat' => "{$title} presented as clear favourable, neutral and avoid windows with date/location controls.",
        'festival' => "{$title} with upcoming observances, date cards and concise timing details.",
        'calculator' => "{$title} as a focused input → result flow instead of a long reference page.",
        'astronomy' => "{$title} with timeline-first event presentation and calculation metadata.",
        'devotion' => "{$title} in a distraction-light reading experience with language and text-size controls.",
        'gallery' => "{$title} in a responsive visual grid with lazy-loading and category filters.",
        'article' => "{$title} rewritten as a readable reference guide with linked concepts and utilities.",
        'list' => "{$title} as a searchable, filterable date/event list.",
        default => "{$title} organized into a modern, searchable Tithika collection.",
    };
}

function tithika_related(array $page, int $limit = 6): array {
    $routes = tithika_routes();
    $group = $routes[$page['group']] ?? null;
    if (!$group) return [];
    $items = array_values(array_filter($group['pages'], fn($p) => $p['slug'] !== $page['slug']));
    return array_slice($items, 0, $limit);
}

function tithika_page_count(): int {
    return count(tithika_flat_routes());
}

function tithika_render_header(string $title, ?array $page = null): void {
    $routes = tithika_routes();
    $base = tithika_base_path();
    $description = $page ? tithika_template_copy($page['template'], $page['title']) : 'Modern location-aware Vedic calendar and Panchang utilities.';
    ?>
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
  <meta name="theme-color" content="#f8fafc">
  <title><?= htmlspecialchars($title) ?> — Tithika</title>
  <meta name="description" content="<?= htmlspecialchars($description) ?>">
  <link rel="stylesheet" href="<?= htmlspecialchars($base) ?>assets/tithika.css?v=1">
</head>
<body>
<div class="tk-shell">
  <header class="tk-header">
    <a class="tk-brand" href="<?= htmlspecialchars($base) ?>">
      <span class="tk-logo">ति</span>
      <span><strong>Tithika</strong><small>Vedic time, reimagined</small></span>
    </a>
    <nav class="tk-nav" aria-label="Primary">
      <?php foreach (array_slice($routes, 0, 6, true) as $key => $group): ?>
        <a href="<?= htmlspecialchars(tithika_pretty_url($key)) ?>"<?= ($page && $page['group'] === $key) ? ' class="is-active"' : '' ?>><?= htmlspecialchars($group['title']) ?></a>
      <?php endforeach; ?>
      <a href="<?= htmlspecialchars(tithika_url('site-map.php')) ?>">All tools</a>
    </nav>
    <button class="tk-place-button" id="tkPlaceButton" type="button"><span>⌖</span><b id="tkPlaceText">Location</b></button>
  </header>
  <div class="tk-place-panel" id="tkPlacePanel" hidden>
    <div class="tk-place-search">
      <input id="tkCitySearch" autocomplete="off" placeholder="Search city or place">
      <button id="tkDetectLocation" type="button" title="Use current location">⌖</button>
    </div>
    <div id="tkSearchResults" class="tk-search-results"></div>
    <p>Your location is used only to calculate local solar timings.</p>
  </div>
  <main>
<?php
}

function tithika_render_footer(): void {
    $base = tithika_base_path();
    ?>
  </main>
  <footer class="tk-footer">
    <div><strong>Tithika</strong><span>Traditional calendar conventions in a modern utility experience.</span></div>
    <div><a href="<?= htmlspecialchars($base) ?>">Home</a><a href="<?= htmlspecialchars(tithika_url('site-map.php')) ?>">Site map</a><a href="<?= htmlspecialchars(tithika_pretty_url('learn/faq')) ?>">FAQ</a></div>
  </footer>
</div>
<div class="tk-toast" id="tkToast" hidden></div>
<script>
window.TITHIKA_BASE = <?= json_encode($base, JSON_UNESCAPED_SLASHES) ?>;
</script>
<script src="<?= htmlspecialchars($base) ?>assets/tithika-site.js?v=1" defer></script>
</body>
</html>
<?php
}
