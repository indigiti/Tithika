<?php
declare(strict_types=1);

$_SERVER['SERVER_NAME']='tithika.example';
$_SERVER['HTTPS']='on';
$_SERVER['SCRIPT_NAME']='/index.php';
require dirname(__DIR__) . '/includes/site.php';

function sq(bool $condition,string $message): void {
    if (!$condition) throw new RuntimeException($message);
}

$flat=tithika_flat_routes();
$live=tithika_live_slugs();
$gated=tithika_gated_routes();

sq(count($gated)===11,'semantic gate count drifted');
sq(count(array_intersect(array_keys($gated),$live))===0,'gated route present in live registry');

foreach($gated as $slug=>$reason){
    sq(isset($flat[$slug]),"gated route missing from map: {$slug}");
    sq(trim((string)$reason)!=='',"gated route reason missing: {$slug}");
    sq(!tithika_is_live_page($slug),"gated route reports live: {$slug}");
    sq(!tithika_is_indexable_page($flat[$slug]),"gated route reports indexable: {$slug}");
}

$mustRemainGated=[
 'panchang/kranti-samya',
 'muhurat/pancha-pakshi',
 'vrat/chandra-darshan','vrat/ishti-anvadhan','vrat/shraddha',
 'jyotish/pancha-pakshi','jyotish/gemstone','jyotish/rudraksha',
 'jyotish/sahasra-chandrodaya','jyotish/prashnavali','jyotish/rashi-by-name',
];
sort($mustRemainGated);
$actual=array_keys($gated);sort($actual);
sq($actual===$mustRemainGated,'semantic gate membership changed without fixture review');

echo "Semantic quality gate fixture passed\n";
