<?php
declare(strict_types=1);
$_SERVER['HTTP_HOST']='tithika.example';
$_SERVER['HTTPS']='on';
$_SERVER['SCRIPT_NAME']='/tithika/page.php';
$_SERVER['REQUEST_URI']='/tithika/jyotish/janma-kundali/';
$_GET['slug']='jyotish/janma-kundali';
ob_start();include dirname(__DIR__).'/page.php';$html=ob_get_clean();
function kw_ok(bool $v,string $m):void{if(!$v)throw new RuntimeException($m);}
kw_ok(str_contains($html,'id="tkKundaliWorkspace"'),'Kundali workspace root missing');
kw_ok(str_contains($html,'id="tkKundaliLayout"'),'chart layout control missing');
foreach(['south','north','east','west'] as $layout)kw_ok(str_contains($html,'value="'.$layout.'"'),"layout missing: $layout");
kw_ok(str_contains($html,'id="tkKundaliSaved"'),'saved Kundali selector missing');
kw_ok(str_contains($html,'id="tkKundaliSave"'),'save control missing');
kw_ok(str_contains($html,'stored only in this browser'),'local privacy copy missing');
foreach(['charts','graha','yogas','dasha','shadbala','ashtakavarga'] as $tab)kw_ok(str_contains($html,'data-kundali-tab="'.$tab.'"'),"workspace tab missing: $tab");
kw_ok(str_contains($html,'/tithika/assets/kundali-workspace.js?v='),'workspace script not base-path aware');
$js=(string)file_get_contents(dirname(__DIR__).'/assets/kundali-workspace.js');
kw_ok(str_contains($js,'tithika.kundalis.v1'),'local saved-chart schema missing');
kw_ok(str_contains($js,"api.php?action=horoscope-analysis"),'unified analysis endpoint missing');
kw_ok(str_contains($js,"window.TithikaContext?.set"),'saved chart context restore missing');
echo "Kundali Workspace surface fixture passed
";
