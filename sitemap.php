<?php
declare(strict_types=1);
require __DIR__ . '/includes/site.php';

header('Content-Type: application/xml; charset=utf-8');
$lastmod = gmdate('Y-m-d', max(
    (int)@filemtime(__DIR__ . '/config/routes.php'),
    (int)@filemtime(__DIR__ . '/config/live.php'),
    (int)@filemtime(__DIR__ . '/config/aggregate.php'),
    (int)@filemtime(__DIR__ . '/config/reference.php'),
    (int)@filemtime(__DIR__ . '/includes/content.php')
));

$urls = [
    ['loc'=>tithika_absolute_url(tithika_url()), 'priority'=>'1.0', 'changefreq'=>'daily'],
    ['loc'=>tithika_absolute_url(tithika_url('site-map.php')), 'priority'=>'0.6', 'changefreq'=>'weekly'],
];

foreach (tithika_routes() as $key=>$group) {
    $urls[] = [
        'loc'=>tithika_absolute_url(tithika_pretty_url($key)),
        'priority'=>'0.8',
        'changefreq'=>'weekly',
    ];
}

foreach (tithika_flat_routes() as $page) {
    if (!tithika_is_indexable_page($page)) continue;
    $urls[] = [
        'loc'=>tithika_absolute_url(tithika_pretty_url($page['slug'])),
        'priority'=>tithika_is_live_page($page['slug']) ? '0.8' : '0.7',
        'changefreq'=>in_array($page['template'], ['daily','calendar','festival'], true) ? 'daily' : 'monthly',
    ];
}

echo '<?xml version="1.0" encoding="UTF-8"?>' . "\n";
?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
<?php foreach ($urls as $row): ?>
  <url>
    <loc><?= htmlspecialchars($row['loc'], ENT_XML1|ENT_QUOTES, 'UTF-8') ?></loc>
    <lastmod><?= $lastmod ?></lastmod>
    <changefreq><?= $row['changefreq'] ?></changefreq>
    <priority><?= $row['priority'] ?></priority>
  </url>
<?php endforeach; ?>
</urlset>
