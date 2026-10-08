<?php
declare(strict_types=1);

function rd_ok(bool $ok,string $message): void {
    if(!$ok) throw new RuntimeException($message);
}

$_SERVER['HTTP_HOST']='tithika.example';
$_SERVER['HTTPS']='on';
$_SERVER['SCRIPT_NAME']='/tithika/page.php';
$_SERVER['REQUEST_URI']='/tithika/panchang/tamil/';
$_GET['slug']='panchang/tamil';

ob_start();
include dirname(__DIR__).'/page.php';
$html=(string)ob_get_clean();

rd_ok(str_contains($html,'id="tkRegionalTabs"'),'regional Day/Month tabs missing');
rd_ok(str_contains($html,'id="tkRegionalDayTab"'),'regional Day tab missing');
rd_ok(str_contains($html,'id="tkRegionalMonthTab"'),'regional Month tab missing');
rd_ok(str_contains($html,'id="tkRegionalDayView"'),'regional daily view container missing');
rd_ok(str_contains($html,'id="tkRegionalDaySummary"'),'regional daily summary missing');
rd_ok(str_contains($html,'id="tkRegionalDayTimings"'),'regional daily timing list missing');
rd_ok(str_contains($html,'id="tkRegionalMonthView" hidden'),'month view should be secondary on Panchang routes');

$js=(string)file_get_contents(dirname(__DIR__).'/assets/tithika-site.js');
foreach([
 'panchang/hindi','panchang/tamil','panchang/telugu','panchang/kannada',
 'panchang/malayalam','panchang/gujarati','panchang/marathi','panchang/bengali',
 'panchang/odia','panchang/assamese','panchang/iskcon','panchang/nepali'
] as $slug){
    rd_ok(str_contains($js,"'".$slug."'"),"regional Panchang client mapping missing: ".$slug);
}
rd_ok(str_contains($js,'calculateRegionalDay'),'regional daily fetch flow missing');
rd_ok(str_contains($js,"view:'day'"),'regional daily API payload missing');
rd_ok(str_contains($js,'renderRegionalDay'),'regional daily renderer missing');
rd_ok(str_contains($js,"setRegionalView('day',true)"),'month-date drilldown does not switch to day view');

echo "Regional daily Panchang surface fixture passed\n";
