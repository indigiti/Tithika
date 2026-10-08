<?php
declare(strict_types=1);
require_once __DIR__ . '/includes/site.php';

function calendarFail(string $message, int $status=400): never {
    http_response_code($status);
    header('Content-Type: text/plain; charset=utf-8');
    header('Cache-Control: no-store, max-age=0');
    echo $message;
    exit;
}

function calendarPython(array $payload): array {
    $script=__DIR__.'/python/notification_agenda.py';
    if(!is_file($script)) throw new RuntimeException('Notification agenda engine not found');
    $python=getenv('PYTHON_BIN') ?: 'python3';
    $desc=[0=>['pipe','r'],1=>['pipe','w'],2=>['pipe','w']];
    $proc=proc_open([$python,$script],$desc,$pipes,__DIR__,null,['bypass_shell'=>true]);
    if(!is_resource($proc)) throw new RuntimeException('Unable to start notification agenda engine');
    fwrite($pipes[0],json_encode($payload,JSON_UNESCAPED_UNICODE)); fclose($pipes[0]);
    $stdout=stream_get_contents($pipes[1]); fclose($pipes[1]);
    $stderr=stream_get_contents($pipes[2]); fclose($pipes[2]);
    $exit=proc_close($proc);
    $data=json_decode($stdout ?: '{}',true);
    if(!is_array($data) || $exit!==0 || !($data['ok']??false)){
        throw new RuntimeException((string)($data['error']??trim($stderr)?:'Calendar generation failed'));
    }
    return $data;
}

function icsEscape(string $value): string {
    return str_replace(["\\",";",",","","
"],["\\\\","\;","\,","","\n"],$value);
}

function icsUtc(string $iso): string {
    $dt=new DateTimeImmutable($iso);
    return $dt->setTimezone(new DateTimeZone('UTC'))->format('Ymd\THis\Z');
}

function icsFold(string $line): string {
    if(strlen($line)<=73) return $line;
    $out=''; $remaining=$line; $first=true;
    while(strlen($remaining)>73){
        $cut=73;
        while($cut>0 && (ord($remaining[$cut]) & 0xC0)===0x80) $cut--;
        $part=substr($remaining,0,$cut);
        $out.=($first?'':"\r\n ").$part;
        $remaining=substr($remaining,$cut);
        $first=false;
    }
    return $out.($first?'':"\r\n ").$remaining;
}

$lat=filter_input(INPUT_GET,'lat',FILTER_VALIDATE_FLOAT);
$lon=filter_input(INPUT_GET,'lon',FILTER_VALIDATE_FLOAT);
if($lat===false || $lat===null) $lat=19.0760;
if($lon===false || $lon===null) $lon=72.8777;
if($lat < -90 || $lat > 90 || $lon < -180 || $lon > 180) calendarFail('Invalid coordinates',422);

$horizon=max(1,min((int)($_GET['days']??90),366));
$timezone=trim((string)($_GET['timezone']??'Asia/Kolkata'));
if(!in_array($timezone,timezone_identifiers_list(),true)) $timezone='Asia/Kolkata';
$defaultDate=(new DateTimeImmutable('now',new DateTimeZone($timezone)))->format('Y-m-d');
$date=trim((string)($_GET['date']??$defaultDate));
if(!preg_match('/^\d{4}-\d{2}-\d{2}$/',$date)) calendarFail('Invalid date',422);
$city=mb_substr(trim((string)($_GET['city']??'Current location')),0,120);
$tradition=strtolower(trim((string)($_GET['tradition']??'smarta')));
if(!in_array($tradition,['smarta','vaishnava','iskcon'],true)) $tradition='smarta';

$allowed=['ekadashi','purnima','amavasya','sankashti','pradosh','shivaratri','sankranti','festivals','transit','retrograde','solar'];
$raw=trim((string)($_GET['categories']??''));
$categories=$raw==='' ? array_slice($allowed,0,10) : array_values(array_unique(array_filter(
    array_map(static fn(string $v): string => strtolower(trim($v)),explode(',',$raw)),
    static fn(string $v): bool => in_array($v,$allowed,true)
)));
if(!$categories) calendarFail('No supported calendar categories selected',422);

try {
    $agenda=calendarPython([
        'lat'=>$lat,'lon'=>$lon,'city'=>$city,'timezone'=>$timezone,'date'=>$date,
        'horizon_days'=>$horizon,'tradition'=>$tradition,'hour24'=>true,'categories'=>$categories,
    ]);
} catch(Throwable $e) {
    calendarFail($e->getMessage(),500);
}

$stamp=gmdate('Ymd\THis\Z');
$lines=[
    'BEGIN:VCALENDAR',
    'VERSION:2.0',
    'PRODID:-//Tithika//Verified Vedic Calendar//EN',
    'CALSCALE:GREGORIAN',
    'METHOD:PUBLISH',
    'X-WR-CALNAME:Tithika · '.icsEscape($city),
    'X-WR-TIMEZONE:'.icsEscape($timezone),
    'X-TITHIKA-TRADITION:'.strtoupper($tradition),
];

foreach(($agenda['events']??[]) as $event){
    $title=(string)($event['title']??'Tithika event');
    $subtitle=(string)($event['subtitle']??'');
    $route=trim((string)($event['route']??''),'/');
    $url=$route!=='' ? tithika_absolute_url(tithika_pretty_url($route)) : tithika_absolute_url(tithika_url());
    $lines[]='BEGIN:VEVENT';
    $lines[]='UID:'.icsEscape((string)($event['id']??sha1($title.($event['date']??'')))).'@tithika';
    $lines[]='DTSTAMP:'.$stamp;
    if(!empty($event['all_day'])){
        $d=new DateTimeImmutable((string)$event['date']);
        $lines[]='DTSTART;VALUE=DATE:'.$d->format('Ymd');
        $lines[]='DTEND;VALUE=DATE:'.$d->modify('+1 day')->format('Ymd');
    } elseif(!empty($event['start'])){
        $lines[]='DTSTART:'.icsUtc((string)$event['start']);
        if(!empty($event['end'])) $lines[]='DTEND:'.icsUtc((string)$event['end']);
    } else {
        $d=new DateTimeImmutable((string)$event['date']);
        $lines[]='DTSTART;VALUE=DATE:'.$d->format('Ymd');
        $lines[]='DTEND;VALUE=DATE:'.$d->modify('+1 day')->format('Ymd');
    }
    $lines[]='SUMMARY:'.icsEscape($title);
    if($subtitle!=='') $lines[]='DESCRIPTION:'.icsEscape($subtitle.' · Verified by Tithika');
    $lines[]='CATEGORIES:'.strtoupper(icsEscape((string)($event['kind']??'event')));
    $lines[]='URL:'.icsEscape($url);
    $lines[]='END:VEVENT';
}
$lines[]='END:VCALENDAR';

header('Content-Type: text/calendar; charset=utf-8');
header('Content-Disposition: inline; filename="tithika-calendar.ics"');
header('Cache-Control: private, max-age=300');
echo implode("\r\n",array_map('icsFold',$lines))."\r\n";
