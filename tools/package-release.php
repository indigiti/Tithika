<?php
declare(strict_types=1);

$root=dirname(__DIR__);
$out=$root.'/release';
$public=$out.'/public';
$private=$out.'/private';

$remove=function(string $path) use (&$remove): void {
    if(!file_exists($path) && !is_link($path)) return;
    if(is_file($path) || is_link($path)){ unlink($path); return; }
    foreach(array_diff(scandir($path)?:[],['.','..']) as $name) $remove($path.'/'.$name);
    rmdir($path);
};
$copy=function(string $src,string $dst) use (&$copy): void {
    if(is_dir($src)){
        if(!is_dir($dst) && !mkdir($dst,0755,true) && !is_dir($dst)) throw new RuntimeException("mkdir failed: $dst");
        foreach(array_diff(scandir($src)?:[],['.','..']) as $name) $copy($src.'/'.$name,$dst.'/'.$name);
        return;
    }
    if(!is_dir(dirname($dst))) mkdir(dirname($dst),0755,true);
    if(!copy($src,$dst)) throw new RuntimeException("copy failed: $src");
};

$remove($out);
mkdir($public,0755,true);
mkdir($private.'/build',0755,true);

$publicFiles=['.htaccess','index.php','page.php','api.php','choghadiya.php','intelligence.php','settings.php','robots.php','sitemap.php','site-map.php','manifest.webmanifest'];
$publicDirs=['assets','config','includes','python','scripts','docs'];
foreach($publicFiles as $name){ if(!is_file($root.'/'.$name)) throw new RuntimeException("required file missing: $name"); $copy($root.'/'.$name,$public.'/'.$name); }
foreach($publicDirs as $name){ if(!is_dir($root.'/'.$name)) throw new RuntimeException("required directory missing: $name"); $copy($root.'/'.$name,$public.'/'.$name); }

$sha=(string)(getenv('GITHUB_SHA')?:'local');
$build=[
    'schema'=>'DIGIOPS-RELEASE/1',
    'name'=>'Tithika',
    'version'=>'1.0.0',
    'builtAt'=>date(DATE_ATOM),
    'sourceSha'=>$sha,
    'branch'=>(string)(getenv('GITHUB_REF_NAME')?:'local'),
    'ciRunNumber'=>(string)(getenv('GITHUB_RUN_NUMBER')?:''),
    'ciRunId'=>(string)(getenv('GITHUB_RUN_ID')?:''),
    'ciRunAttempt'=>(string)(getenv('GITHUB_RUN_ATTEMPT')?:''),
    'public'=>'public',
    'private'=>'private',
    'publicPath'=>'public_html/tithika/',
    'privatePath'=>'private_html/tithika/',
    'persistentPaths'=>[],
];
$json=json_encode($build,JSON_PRETTY_PRINT|JSON_UNESCAPED_SLASHES).PHP_EOL;
file_put_contents($out.'/RELEASE.json',$json);
file_put_contents($private.'/build/release.json',$json);
echo "Tithika DigiOps release built for {$sha}\n";
