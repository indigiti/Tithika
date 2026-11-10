<?php
declare(strict_types=1);
// Prevent the route-count and generic-shell tests from hiding omitted daily features.
// This fixture is deliberately feature-specific rather than just checking a page exists.
function depth_check(bool $condition,string $message): void {
    if (!$condition) throw new RuntimeException($message);
}
$root=dirname(__DIR__);
$_SERVER['HTTP_HOST']='tithika.example';
$_SERVER['SERVER_NAME']='tithika.example';
$_SERVER['HTTPS']='on';
$_SERVER['SCRIPT_NAME']='/tithika/page.php';
$_SERVER['REQUEST_URI']='/tithika/panchang/daily/';
$_GET['slug']='panchang/daily';
ob_start();
include $root.'/page.php';
$html=ob_get_clean();

foreach ([
    'tkDailyDepth','tkDepthTracks','tkDepthRuler','tkDepthSummary',
    'tkDepthObservances','tkDepthPlanets','tkDepthMoonSign',
    'tkDepthClock','tkDepthChart','tkDepthTiming','tkDepthAdvancedTitle',
] as $id) depth_check(str_contains($html,'id="'.$id.'"'),'Daily feature missing: '.$id);
depth_check(str_contains($html,'/tithika/assets/daily-depth.css?v='),'Daily CSS missing or wrong nested URL');
depth_check(str_contains($html,'/tithika/assets/daily-depth.js?v='),'Daily JS missing or wrong nested URL');
depth_check(str_contains($html,'panchang/chandrabalam/'),'Chandrabalam deep link missing');
depth_check(str_contains($html,'panchang/tarabalam/'),'Tarabalam deep link missing');
depth_check(str_contains($html,'panchang/vedic-clock/'),'Vedic clock deep link missing');
depth_check(str_contains($html,'muhurat/panchaka-rahita/'),'Panchaka Rahita deep link missing');

$js=(string)file_get_contents($root.'/assets/daily-depth.js');
depth_check(str_contains($js,"api('panchang'"),'Daily source must use Panchang API');
depth_check(str_contains($js,"api('home-dashboard'"),'Daily feed must use aggregator');
depth_check(str_contains($js,"api('kundali'"),'Chart must use a calculated Kundali');
depth_check(str_contains($js,"Promise.allSettled"),'Independent module failure isolation missing');
depth_check(str_contains($js,"asDate") || str_contains($js,"const dt="),'Timestamp parser missing');
depth_check(!str_contains($js,'November 10, 2026'),'Hardcoded calendar result prohibited');
depth_check(!str_contains($js,'06:43 AM'),'Hardcoded sunrise prohibited');

$_GET['slug']='panchang/month';
$_SERVER['REQUEST_URI']='/tithika/panchang/month/';
ob_start();
include $root.'/page.php';
$month=ob_get_clean();
depth_check(!str_contains($month,'id="tkDailyDepth"'),'Daily-depth markup leaked into month route');
depth_check(!str_contains($month,'/tithika/assets/daily-depth.css?v='),'Daily-depth CSS leaked to month route');
echo "Daily Panchang depth surface contract passed\n";
