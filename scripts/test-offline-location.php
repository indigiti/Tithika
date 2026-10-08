<?php
declare(strict_types=1);
require dirname(__DIR__).'/includes/location.php';

function loc_ok(bool $ok,string $message): void {
    if(!$ok) throw new RuntimeException($message);
}

$rows=tithikaLocationIndex();
loc_ok(count($rows)>=50,'offline location index is unexpectedly small');

$pune=tithikaLocalSearch('Pune',6);
loc_ok(count($pune)>=1,'Pune missing from offline index');
loc_ok(($pune[0]['timezone']??'')==='Asia/Kolkata','Pune timezone mismatch');
loc_ok(($pune[0]['source']??'')==='offline-index','Pune should resolve offline');

$bangalore=tithikaLocalSearch('Bangalore',6);
loc_ok(count($bangalore)>=1 && ($bangalore[0]['label']??'')!=='','Bangalore alias missing');
loc_ok(str_contains((string)$bangalore[0]['label'],'Bengaluru'),'Bangalore alias should resolve Bengaluru');

$kathmandu=tithikaLocalSearch('Kathmandu',6);
loc_ok(count($kathmandu)>=1,'Kathmandu missing from offline index');
loc_ok(($kathmandu[0]['timezone']??'')==='Asia/Kathmandu','Kathmandu timezone mismatch');

$nearest=tithikaNearestLocal(18.5204,73.8567);
loc_ok(is_array($nearest),'nearest location missing');
loc_ok(($nearest['city']??'')==='Pune','Pune coordinates should resolve to Pune');
loc_ok((float)($nearest['distance_km']??999)<1.0,'Pune nearest distance should be sub-kilometre');

$api=(string)file_get_contents(dirname(__DIR__).'/api.php');
loc_ok(str_contains($api,'TITHIKA_ELEVATION_METERS'),'subprocess elevation propagation missing');
loc_ok(str_contains($api,'count($results) === 0'),'offline search should not wait on external enrichment');
loc_ok(str_contains($api,"'source'=>'offline-index'"),'offline timezone source missing');

echo "Offline location fixture passed: bundled search, aliases, nearest-city timezone and subprocess elevation\n";
