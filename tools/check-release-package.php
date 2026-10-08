<?php
declare(strict_types=1);
$root=dirname(__DIR__).'/release';
function must(bool $ok,string $message): void { if(!$ok) throw new RuntimeException($message); }
must(is_file($root.'/RELEASE.json'),'RELEASE.json missing');
$meta=json_decode((string)file_get_contents($root.'/RELEASE.json'),true);
must(is_array($meta),'invalid RELEASE.json');
must(($meta['schema']??'')==='DIGIOPS-RELEASE/1','release schema mismatch');
must(($meta['name']??'')==='Tithika','release name mismatch');
must(($meta['publicPath']??'')==='public_html/tithika/','public path mismatch');
must(($meta['privatePath']??'')==='private_html/tithika/','private path mismatch');
foreach(['.htaccess','index.php','page.php','api.php','intelligence.php','settings.php','notifications.php','calendar.php','assets/tithika-site.js','assets/app.js','assets/choghadiya.css','assets/intelligence.css','assets/intelligence.js','assets/settings-core.js','assets/settings.js','assets/home-dashboard.js','assets/notifications.js','assets/kundali-workspace.js','config/routes.php','config/location-index.php','includes/site.php','includes/i18n.php','includes/location.php','python/panchang.py','python/panchang_completion.py','python/intelligence_gateway.py','python/intelligence/service.py','python/home_dashboard.py','python/notification_agenda.py','scripts/test-localization.php','scripts/test-offline-location.php','scripts/test-offline-location-surface.php','scripts/test-elevation.py'] as $path){
    must(is_file($root.'/public/'.$path),"payload missing: {$path}");
}
must(is_file($root.'/private/build/release.json'),'private release metadata missing');
must(!is_dir($root.'/public/.git'),'git metadata must not ship');
must(!is_dir($root.'/public/.github'),'workflow metadata must not ship');
echo "DigiOps release payload verified\n";
