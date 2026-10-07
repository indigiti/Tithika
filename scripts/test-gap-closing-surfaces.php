<?php
declare(strict_types=1);

function gap_ok(bool $ok,string $message): void {
    if(!$ok) throw new RuntimeException($message);
}

$_SERVER['HTTP_HOST']='tithika.example';
$_SERVER['HTTPS']='on';
$_SERVER['SCRIPT_NAME']='/tithika/index.php';
$_SERVER['REQUEST_URI']='/tithika/';
ob_start();
include dirname(__DIR__).'/index.php';
$home=ob_get_clean();

gap_ok(str_contains($home,'id="tkDailyDashboard"'),'daily dashboard missing from homepage');
gap_ok(str_contains($home,'id="tkUpcomingEvents"'),'upcoming dashboard feed missing');
gap_ok(str_contains($home,'Open Tithika Intelligence'),'Intelligence entry point missing');
gap_ok(str_contains($home,'/tithika/assets/settings-core.js?v='),'Settings Core not loaded from app root');
gap_ok(str_contains($home,'/tithika/assets/home-dashboard.js?v='),'home dashboard client not loaded from app root');
gap_ok(str_contains($home,'/tithika/settings/'),'settings link missing');

$_SERVER['SCRIPT_NAME']='/tithika/settings.php';
$_SERVER['REQUEST_URI']='/tithika/settings/';
ob_start();
include dirname(__DIR__).'/settings.php';
$settings=ob_get_clean();

gap_ok(str_contains($settings,'Make Tithika yours.'),'Settings hero missing');
gap_ok(str_contains($settings,'data-setting="theme"'),'theme setting missing');
gap_ok(str_contains($settings,'data-setting="clock"'),'clock setting missing');
gap_ok(str_contains($settings,'data-setting="lunarMonth"'),'lunar month setting missing');
gap_ok(str_contains($settings,'data-setting="tradition"'),'tradition setting missing');
gap_ok(str_contains($settings,'id="tkSaveCurrentLocation"'),'saved location control missing');
gap_ok(str_contains($settings,'/tithika/assets/settings.js?v='),'settings client not base-path aware');

$core=(string)file_get_contents(dirname(__DIR__).'/assets/settings-core.js');
gap_ok(str_contains($core,'tithika.settings.v1'),'settings schema key missing');
gap_ok(str_contains($core,"clock:'12'"),'12-hour default missing');
gap_ok(str_contains($core,"lunarMonth:'amanta'"),'Amanta default missing');
gap_ok(str_contains($core,"tradition:'smarta'"),'Smarta default missing');

$ht=(string)file_get_contents(dirname(__DIR__).'/.htaccess');
gap_ok(str_contains($ht,'^settings/?$ settings.php'),'settings pretty route missing');

echo "Gap-closing surface fixture passed\n";
