<?php
declare(strict_types=1);
$_SERVER['HTTP_HOST']='tithika.example';
$_SERVER['HTTPS']='on';
$_SERVER['SCRIPT_NAME']='/tithika/index.php';
$_SERVER['REQUEST_URI']='/tithika/';
ob_start();include dirname(__DIR__).'/index.php';$html=ob_get_clean();
function home_ok(bool $v,string $m):void{if(!$v)throw new RuntimeException($m);}
home_ok(str_contains($html,'id="tkHomeDashboard"'),'dashboard root missing');
home_ok(str_contains($html,'id="tkHomeTithi"'),'daily Panchang card missing');
home_ok(str_contains($html,'id="tkHomeRecommendations"'),'advisor panel missing');
home_ok(str_contains($html,'id="tkHomeCalendar"'),'upcoming calendar panel missing');
home_ok(str_contains($html,'id="tkHomePlanets"'),'planet transit panel missing');
home_ok(str_contains($html,'/tithika/assets/home.js?v='),'home controller is not base-path aware');
home_ok(!str_contains($html,'cdn.tailwindcss.com'),'runtime Tailwind CDN found on homepage');
echo "Home dashboard surface fixture passed\n";
