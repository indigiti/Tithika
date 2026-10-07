<?php
declare(strict_types=1);

$_SERVER['HTTP_HOST']='tithika.example';
$_SERVER['HTTPS']='on';
$_SERVER['SCRIPT_NAME']='/tithika/intelligence.php';
$_SERVER['REQUEST_URI']='/tithika/intelligence/';

ob_start();
include dirname(__DIR__).'/intelligence.php';
$html=ob_get_clean();

function ai_ok(bool $value,string $message): void {
    if(!$value) throw new RuntimeException($message);
}
ai_ok(str_contains($html,'Tithika Intelligence'),'Intelligence title missing');
ai_ok(str_contains($html,'Six layers.'),'six-layer editorial section missing');
ai_ok(str_contains($html,'/tithika/assets/intelligence.css?v='),'Intelligence CSS is not base-path aware');
ai_ok(str_contains($html,'/tithika/assets/intelligence.js?v='),'Intelligence JS is not base-path aware');
ai_ok(str_contains($html,'window.TITHIKA_BASE = "/tithika/"'),'Intelligence runtime base path incorrect');
ai_ok(str_contains($html,'https://tithika.example/tithika/intelligence/'),'Intelligence canonical incorrect');
ai_ok(!str_contains($html,'cdn.tailwindcss.com'),'runtime Tailwind CDN found');
ai_ok(!preg_match('~<script[^>]+src=["\']https?://~i',$html),'external runtime script found');
echo "Intelligence surface fixture passed\n";
