<?php
declare(strict_types=1);

function loc_ok(bool $value, string $message): void {
    if (!$value) throw new RuntimeException($message);
}

$_GET['lang']='hi';
$_COOKIE=[];
$_SERVER['HTTP_HOST']='tithika.example';
$_SERVER['HTTPS']='on';
$_SERVER['SCRIPT_NAME']='/tithika/index.php';
$_SERVER['REQUEST_URI']='/tithika/?lang=hi';

ob_start();
include dirname(__DIR__).'/index.php';
$home=(string)ob_get_clean();

loc_ok(str_contains($home,'<html lang="hi">'),'Hindi html lang missing');
loc_ok(str_contains($home,'आज, स्पष्ट रूप से।'),'Hindi dashboard hero missing');
loc_ok(str_contains($home,'पंचांग'),'Hindi primary navigation missing');
loc_ok(str_contains($home,'एक मंच, स्पष्ट उत्पाद समूह।'),'Hindi product-family section missing');
loc_ok(str_contains($home,'ब्लैक बॉक्स नहीं, प्रमाण पर आधारित।'),'Hindi calculation-stack section missing');
loc_ok(str_contains($home,'संदर्भ और भक्ति'),'Hindi reference section missing');
loc_ok(str_contains($home,'"inLanguage":"hi"'),'schema language is not Hindi');
loc_ok(str_contains($home,'window.TITHIKA_I18N = {"locale":"hi"'),'client locale payload missing');
loc_ok(!str_contains($home,'?>?>'),'stray PHP close token rendered in navigation');

$_SERVER['SCRIPT_NAME']='/tithika/settings.php';
$_SERVER['REQUEST_URI']='/tithika/settings/?lang=hi';
ob_start();
include dirname(__DIR__).'/settings.php';
$settings=(string)ob_get_clean();

loc_ok(str_contains($settings,'तिथिका को अपने अनुसार बनाएँ।'),'Hindi Settings hero missing');
loc_ok(str_contains($settings,'data-setting="language"'),'language preference missing');
loc_ok(str_contains($settings,'data-setting="numerals"'),'numeral preference missing');
loc_ok(str_contains($settings,'data-value="deva"'),'Devanagari numeral option missing');
loc_ok(str_contains($settings,'० १ २ ३'),'Devanagari numeral example missing');

$dict=tithika_dictionary();
loc_ok(isset($dict['en'],$dict['hi']),'English/Hindi dictionaries missing');
loc_ok(array_diff_key($dict['en'],$dict['hi'])===[],'Hindi dictionary is missing English keys');
loc_ok(array_diff_key($dict['hi'],$dict['en'])===[],'English dictionary is missing Hindi keys');

$core=(string)file_get_contents(dirname(__DIR__).'/assets/settings-core.js');
loc_ok(str_contains($core,"language:new Set(['en','hi'])"),'settings locale allow-list missing');
loc_ok(str_contains($core,"numerals:new Set(['latin','deva'])"),'numeral allow-list missing');
loc_ok(str_contains($core,'numberingSystem'), 'Intl numbering system support missing');

$settingsJs=(string)file_get_contents(dirname(__DIR__).'/assets/settings.js');
loc_ok(substr_count($settingsJs,'const $=s=>document.querySelector(s);')===1,'settings single-selector helper malformed');
loc_ok(substr_count($settingsJs,'const $$=s=>[...document.querySelectorAll(s)];')===1,'settings multi-selector helper malformed');

$dashboard=(string)file_get_contents(dirname(__DIR__).'/assets/home-dashboard.js');
loc_ok(str_contains($dashboard,'numberingSystem:'),'dashboard does not apply numeral preference');
loc_ok(str_contains($dashboard,'dynamic.dashboard_lead'),'dashboard summary is not localized');

echo "Localization fixture passed: Hindi shell/home/settings, schema language and Devanagari numerals\n";
