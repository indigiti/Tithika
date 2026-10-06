<?php
declare(strict_types=1);
require __DIR__ . '/includes/site.php';
header('Content-Type: text/plain; charset=utf-8');
echo "User-agent: *\n";
echo "Allow: /\n";
echo "Disallow: " . tithika_url("config/") . "\n";
echo "Disallow: " . tithika_url("includes/") . "\n";
echo "Disallow: " . tithika_url("python/") . "\n";
echo "Disallow: " . tithika_url("scripts/") . "\n";
echo "Sitemap: " . tithika_absolute_url(tithika_url("sitemap.xml")) . "\n";
