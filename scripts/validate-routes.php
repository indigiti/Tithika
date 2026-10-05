<?php
declare(strict_types=1);
$routes = require __DIR__ . '/../config/routes.php';
$seen = [];
$count = 0;
$errors = [];
$allowedTemplates = ['daily','calendar','muhurat','festival','calculator','astronomy','devotion','gallery','article','list','collection'];

foreach ($routes as $groupKey => $group) {
    if (!isset($group['title'],$group['icon'],$group['description'],$group['pages']) || !is_array($group['pages'])) {
        $errors[] = "Invalid group: {$groupKey}";
        continue;
    }
    foreach ($group['pages'] as $page) {
        $count++;
        foreach (['slug','title','template'] as $required) {
            if (empty($page[$required])) $errors[] = "{$groupKey}: missing {$required}";
        }
        $slug = $page['slug'] ?? '';
        if ($slug !== trim($slug,'/') || str_contains($slug,'//') || !preg_match('#^[a-z0-9-]+(?:/[a-z0-9-]+)*$#',$slug)) {
            $errors[] = "Invalid slug: {$slug}";
        }
        if (isset($seen[$slug])) $errors[] = "Duplicate slug: {$slug}";
        $seen[$slug] = true;
        if (!in_array($page['template'] ?? '', $allowedTemplates, true)) $errors[] = "Invalid template for {$slug}";
    }
}
if ($count < 200) $errors[] = "Expected at least 200 mapped pages, found {$count}";

if ($errors) {
    fwrite(STDERR, implode(PHP_EOL,$errors) . PHP_EOL);
    exit(1);
}
echo "Route map valid: {$count} pages across " . count($routes) . " families." . PHP_EOL;
