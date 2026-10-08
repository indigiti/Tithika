<?php
declare(strict_types=1);

function ol_ok(bool $ok,string $message): void {
    if(!$ok) throw new RuntimeException($message);
}

$_SERVER['HTTP_HOST']='tithika.example';
$_SERVER['HTTPS']='on';
$_SERVER['SCRIPT_NAME']='/tithika/settings.php';
$_SERVER['REQUEST_URI']='/tithika/settings/';
ob_start();
include dirname(__DIR__).'/settings.php';
$html=(string)ob_get_clean();

foreach(['tkManualCity','tkManualLat','tkManualLon','tkManualTimezone','tkManualElevation','tkSaveManualLocation'] as $id){
    ol_ok(str_contains($html,'id="'.$id.'"'),"manual location control missing: $id");
}
ol_ok(str_contains($html,'Asia/Kolkata'),'manual timezone example missing');
ol_ok(str_contains($html,'Elevation (m)') || str_contains($html,'ऊँचाई'),'elevation label missing');

$core=(string)file_get_contents(dirname(__DIR__).'/assets/settings-core.js');
ol_ok(str_contains($core,'elevation:Number.isFinite'),'saved location elevation sanitization missing');

$settings=(string)file_get_contents(dirname(__DIR__).'/assets/settings.js');
ol_ok(str_contains($settings,'timezoneValid'),'manual IANA timezone validation missing');
ol_ok(str_contains($settings,'tkSaveManualLocation'),'manual save handler missing');

$site=(string)file_get_contents(dirname(__DIR__).'/assets/tithika-site.js');
ol_ok(str_contains($site,'elevation:state.elevation'),'calculation payload elevation missing');
ol_ok(str_contains($site,'p.coords.altitude'),'device altitude support missing');
ol_ok(str_contains($site,"x.source==='offline-index'"),'offline search source indicator missing');

$tabPos=strpos($site,"$('#tkRegionalDayTab')?.addEventListener");
$shiftPos=strpos($site,"document.querySelectorAll('[data-shift-date]')");
ol_ok($tabPos!==false && $shiftPos!==false && $tabPos<$shiftPos,'regional Day/Month listeners regressed inside date-shift handler');

echo "Offline location surface fixture passed: manual controls, elevation context and regional listener wiring\n";
