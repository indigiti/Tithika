<?php
declare(strict_types=1);
require_once dirname(__DIR__).'/includes/site.php';

function dc_ok(bool $ok,string $message): void {
    if(!$ok) throw new RuntimeException($message);
}

$registry=tithika_devotion_registry();
$routes=array_values(array_filter(
    tithika_flat_routes(),
    static fn(array $page): bool => ($page['group']??'')==='devotion'
));

dc_ok(count($routes)===41,'Devotion route contract changed unexpectedly');
dc_ok(count($registry)===41,'Devotion corpus must cover exactly 41 routes');

$routeSlugs=array_column($routes,'slug');
sort($routeSlugs);
$corpusSlugs=array_keys($registry);
sort($corpusSlugs);
dc_ok($routeSlugs===$corpusSlugs,'Devotion route/corpus slug parity mismatch');

foreach($routes as $page){
    $slug=$page['slug'];
    $entry=$registry[$slug]??null;
    dc_ok(is_array($entry),"Missing corpus entry: $slug");
    foreach(['kind','summary','practice','observance','source','links'] as $field){
        dc_ok(array_key_exists($field,$entry),"Missing $field: $slug");
    }
    dc_ok(mb_strlen(trim((string)$entry['summary']))>=60,"Summary too thin: $slug");
    dc_ok(mb_strlen(trim((string)$entry['practice']))>=60,"Practice context too thin: $slug");
    dc_ok(mb_strlen(trim((string)$entry['observance']))>=45,"Observance context too thin: $slug");
    dc_ok(($entry['source']['editorial']??'')==='original-tithika',"Editorial source policy mismatch: $slug");
    dc_ok(($entry['source']['sacred_text']??'')==='not-embedded',"Sacred text boundary mismatch: $slug");
    dc_ok(!array_key_exists('full_text',$entry),"Unsourced full sacred text embedded: $slug");
    foreach((array)$entry['links'] as $linked){
        dc_ok(tithika_find_page((string)$linked)!==null,"Broken related route from $slug: $linked");
    }
    if(($entry['kind']??'')==='collection'){
        dc_ok(count((array)($entry['items']??[]))>=3,"Collection index too small: $slug");
    }

    $content=tithika_editorial_content($page);
    dc_ok(is_array($content),'Editorial adapter missing: '.$slug);
    dc_ok(($content['source']['policy']??'')!=='','Source policy not exposed: '.$slug);
}

function render_devotion(string $slug): string {
    $_GET['slug']=$slug;
    $_SERVER['HTTP_HOST']='tithika.example';
    $_SERVER['HTTPS']='on';
    $_SERVER['SCRIPT_NAME']='/tithika/page.php';
    $_SERVER['REQUEST_URI']='/tithika/'.$slug.'/';
    ob_start();
    include dirname(__DIR__).'/page.php';
    return (string)ob_get_clean();
}

$aarti=render_devotion('devotion/aarti');
dc_ok(str_contains($aarti,'Corpus index'),'Aarti corpus index not rendered');
dc_ok(str_contains($aarti,'Ganesha Aarti'),'Aarti-specific index missing');
dc_ok(str_contains($aarti,'Source &amp; edition policy') || str_contains($aarti,'Source & edition policy'),'Source policy UI missing');

$shiva=render_devotion('devotion/gods/lord-shiva');
dc_ok(str_contains($shiva,'Maha Shivaratri'),'Shiva route-specific observance content missing');

$vivah=render_devotion('devotion/rituals/vivah-sanskar');
dc_ok(str_contains($vivah,'Saptapadi'),'Vivah route-specific corpus content missing');

echo "Devotion corpus fixture passed: 41/41 route coverage, link integrity, source boundaries and route-specific rendering\n";
