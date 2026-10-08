<?php
declare(strict_types=1);

function notify_ok(bool $value,string $message): void {
    if(!$value) throw new RuntimeException($message);
}

$_GET['lang']='en';
$_COOKIE=[];
$_SERVER['HTTP_HOST']='tithika.example';
$_SERVER['HTTPS']='on';
$_SERVER['SCRIPT_NAME']='/tithika/notifications.php';
$_SERVER['REQUEST_URI']='/tithika/notifications/';

ob_start();
include dirname(__DIR__).'/notifications.php';
$html=(string)ob_get_clean();

notify_ok(str_contains($html,'id="tkNotificationCenter"'),'Notification Center shell missing');
notify_ok(str_contains($html,'data-notify-category="ekadashi"'),'Ekadashi preference missing');
notify_ok(str_contains($html,'data-notify-category="solar"'),'solar-event preference missing');
notify_ok(str_contains($html,'id="tkNotifyFeed"'),'calendar feed action missing');
notify_ok(str_contains($html,'id="tkNotifyPermission"'),'on-site alert permission control missing');

$core=(string)file_get_contents(dirname(__DIR__).'/assets/settings-core.js');
notify_ok(str_contains($core,'notificationCategories'),'notification categories missing from local settings');
notify_ok(str_contains($core,'onsiteAlerts'),'on-site alert setting missing');
notify_ok(str_contains($core,"'solar'"),'solar notification category missing');

$client=(string)file_get_contents(dirname(__DIR__).'/assets/notifications.js');
notify_ok(str_contains($client,'api.php?action=notification-agenda'),'notification client does not use verified agenda API');
notify_ok(str_contains($client,'calendar.ics'),'notification client does not build ICS feed');
notify_ok(str_contains($client,'tithika.notified.v1'),'notification de-duplication store missing');
notify_ok(str_contains($client,"Notification.permission==='granted'"),'browser permission guard missing');

$calendar=(string)file_get_contents(dirname(__DIR__).'/calendar.php');
notify_ok(str_contains($calendar,'BEGIN:VCALENDAR'),'ICS calendar header missing');
notify_ok(str_contains($calendar,'BEGIN:VEVENT'),'ICS event emission missing');
notify_ok(str_contains($calendar,'python/notification_agenda.py'),'ICS feed does not reuse notification agenda engine');
notify_ok(str_contains($calendar,'DTSTART;VALUE=DATE'),'all-day ICS support missing');
notify_ok(str_contains($calendar,'DTSTART:'),'timed ICS support missing');

$api=(string)file_get_contents(dirname(__DIR__).'/api.php');
notify_ok(str_contains($api,"$action === 'notification-agenda'"),'notification agenda API route missing');

$ht=(string)file_get_contents(dirname(__DIR__).'/.htaccess');
notify_ok(str_contains($ht,'RewriteRule ^notifications/?$ notifications.php'),'Notification Center rewrite missing');
notify_ok(str_contains($ht,'RewriteRule ^calendar\\.ics$ calendar.php'),'calendar feed rewrite missing');

echo "Notification surface fixture passed: preferences, agenda API, on-site alerts and ICS feed\n";
