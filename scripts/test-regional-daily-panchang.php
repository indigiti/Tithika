<?php
declare(strict_types=1);
require_once dirname(__DIR__).'/includes/site.php';

function regional_daily_ok(bool $value,string $message): void {
    if(!$value) throw new RuntimeException($message);
}

$variants=['hindi','tamil','telugu','kannada','malayalam','gujarati','marathi','bengali','odia','nepali','iskcon','assamese'];
$flat=tithika_flat_routes();
$live=tithika_live_slugs();

foreach($variants as $variant){
    $slug="panchang/{$variant}/daily";
    regional_daily_ok(isset($flat[$slug]),"regional daily route missing: {$slug}");
    regional_daily_ok(($flat[$slug]['template']??'')==='daily',"regional daily route must use daily template: {$slug}");
    regional_daily_ok(in_array($slug,$live,true),"regional daily route not promoted: {$slug}");
    regional_daily_ok(tithika_is_indexable_page($flat[$slug]),"regional daily route not indexable: {$slug}");
    $parent="panchang/{$variant}";
    regional_daily_ok(isset($flat[$parent]),"regional parent missing: {$parent}");
}

$page=(string)file_get_contents(dirname(__DIR__).'/page.php');
regional_daily_ok(str_contains($page,'tkRegionalDailyTitle'),'regional daily title surface missing');
regional_daily_ok(str_contains($page,'tkRegionalDailyTithi'),'regional daily Tithi surface missing');
regional_daily_ok(str_contains($page,'tkRegionalDailyNakshatra'),'regional daily Nakshatra surface missing');
regional_daily_ok(str_contains($page,'tkRegionalDailyRahu'),'regional daily Rahu Kaal surface missing');
regional_daily_ok(str_contains($page,'tkRegionalDailyAbhijit'),'regional daily Abhijit surface missing');

$js=(string)file_get_contents(dirname(__DIR__).'/assets/tithika-site.js');
regional_daily_ok(str_contains($js,'const regionalDailyVariants='),'regional daily variant registry missing');
regional_daily_ok(str_contains($js,'calculateRegionalDaily'),'regional daily calculator missing');
regional_daily_ok(str_contains($js,'api.php?action=regional-calendar&variant='),'regional daily view does not reuse regional adapter');
regional_daily_ok(str_contains($js,'api.php?action=panchang'),'regional daily view does not reuse verified Panchang API');
foreach($variants as $variant){
    regional_daily_ok(str_contains($js,"'panchang/{$variant}/daily':'{$variant}'"),"JS variant mapping missing: {$variant}");
}

regional_daily_ok(count($flat)===304,'route contract must be 304 after regional daily expansion');
regional_daily_ok(count($live)===241,'live route contract must be 241 after regional daily expansion');

echo "Regional daily Panchang surface fixture passed: 12 regional day routes reuse regional + daily Panchang engines\n";
