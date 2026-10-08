<?php
declare(strict_types=1);
header('Content-Type: application/json; charset=utf-8');
require_once __DIR__ . '/includes/location.php';

function out(array $data, int $status = 200, bool $cacheable = false): never {
    http_response_code($status);
    header($cacheable ? 'Cache-Control: private, max-age=300' : 'Cache-Control: no-store, max-age=0');
    echo json_encode($data, JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE);
    exit;
}

function curlJson(string $url): array {
    if (!function_exists('curl_init')) throw new RuntimeException('PHP cURL extension is required for city lookup.');
    $ch = curl_init($url);
    curl_setopt_array($ch, [
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_FOLLOWLOCATION => true,
        CURLOPT_CONNECTTIMEOUT => 5,
        CURLOPT_TIMEOUT => 10,
        CURLOPT_HTTPHEADER => [
            'Accept: application/json',
            'User-Agent: Tithika/0.2 (+https://github.com/indigiti/Tithika)'
        ]
    ]);
    $body = curl_exec($ch);
    $code = (int) curl_getinfo($ch, CURLINFO_RESPONSE_CODE);
    $err = curl_error($ch);
    curl_close($ch);
    if ($body === false || $code < 200 || $code >= 300) throw new RuntimeException($err ?: "Geocoding service returned HTTP $code");
    $json = json_decode($body, true);
    if (!is_array($json)) throw new RuntimeException('Invalid geocoding response');
    return $json;
}

function readPayload(): array {
    $raw = file_get_contents('php://input') ?: '{}';
    $payload = json_decode($raw, true);
    if (!is_array($payload)) out(['ok'=>false,'error'=>'Invalid JSON'], 400);
    $lat = (float)($payload['lat'] ?? 19.0760);
    $lon = (float)($payload['lon'] ?? 72.8777);
    if ($lat < -90 || $lat > 90 || $lon < -180 || $lon > 180) {
        out(['ok'=>false,'error'=>'Invalid coordinates'], 422);
    }
    if (array_key_exists('elevation', $payload)) {
        $elevation = filter_var($payload['elevation'], FILTER_VALIDATE_FLOAT);
        if ($elevation === false || $elevation < -500 || $elevation > 9000) {
            out(['ok'=>false,'error'=>'Invalid elevation'], 422);
        }
        $payload['elevation'] = (float)$elevation;
    }
    return $payload;
}

function runPythonEngine(string $relativeScript, array $payload): array {
    $script = __DIR__ . '/' . ltrim($relativeScript, '/');
    if (!is_file($script)) throw new RuntimeException('Calculation engine not found');
    $python = getenv('PYTHON_BIN') ?: 'python3';
    $desc = [0=>['pipe','r'],1=>['pipe','w'],2=>['pipe','w']];
    $env = getenv();
    if (!is_array($env)) $env = [];
    $elevation = (float)($payload['elevation'] ?? 0.0);
    $elevation = max(-500.0, min(9000.0, $elevation));
    $env['TITHIKA_ELEVATION_METERS'] = (string)$elevation;
    $proc = proc_open([$python, $script], $desc, $pipes, __DIR__, $env, ['bypass_shell'=>true]);
    if (!is_resource($proc)) throw new RuntimeException('Unable to start Python calculation engine');
    fwrite($pipes[0], json_encode($payload, JSON_UNESCAPED_UNICODE));
    fclose($pipes[0]);
    $stdout = stream_get_contents($pipes[1]); fclose($pipes[1]);
    $stderr = stream_get_contents($pipes[2]); fclose($pipes[2]);
    $exit = proc_close($proc);
    $data = json_decode($stdout ?: '{}', true);
    if (!is_array($data)) {
        throw new RuntimeException('Invalid calculation response' . ($stderr ? ': ' . trim($stderr) : ''));
    }
    if ($exit !== 0 || !($data['ok'] ?? false)) {
        $data['detail'] = $stderr ?: ($data['detail'] ?? '');
        $data['_exit'] = $exit;
    }
    return $data;
}

$action = $_GET['action'] ?? 'calculate';

try {
    if ($action === 'reverse') {
        $lat = filter_input(INPUT_GET, 'lat', FILTER_VALIDATE_FLOAT);
        $lon = filter_input(INPUT_GET, 'lon', FILTER_VALIDATE_FLOAT);
        if ($lat === false || $lon === false || $lat === null || $lon === null) out(['ok'=>false,'error'=>'Invalid coordinates'], 422);
        $nearest = tithikaNearestLocal((float)$lat,(float)$lon);
        if ($nearest && (float)$nearest['distance_km'] <= 80.0) {
            out([
                'ok'=>true,
                'label'=>tithikaLocationLabel($nearest),
                'timezone'=>(string)$nearest['timezone'],
                'elevation'=>$nearest['elevation'] ?? null,
                'source'=>'offline-index',
                'distance_km'=>round((float)$nearest['distance_km'],1),
            ], 200, true);
        }
        try {
            $url = 'https://nominatim.openstreetmap.org/reverse?format=jsonv2&zoom=10&addressdetails=1&lat=' . rawurlencode((string)$lat) . '&lon=' . rawurlencode((string)$lon);
            $r = curlJson($url); $a = $r['address'] ?? [];
            $city = $a['city'] ?? $a['town'] ?? $a['village'] ?? $a['municipality'] ?? $a['county'] ?? 'Current location';
            $state = $a['state'] ?? ''; $country = $a['country'] ?? '';
            $label = implode(', ', array_values(array_filter([$city, $state, $country])));
            out(['ok'=>true,'label'=>$label ?: ($r['display_name'] ?? 'Current location'),'source'=>'nominatim']);
        } catch (Throwable $e) {
            out(['ok'=>true,'label'=>'Current location','source'=>'coordinate-only']);
        }
    }

    if ($action === 'timezone') {
        $lat = filter_input(INPUT_GET, 'lat', FILTER_VALIDATE_FLOAT);
        $lon = filter_input(INPUT_GET, 'lon', FILTER_VALIDATE_FLOAT);
        if ($lat === false || $lon === false || $lat === null || $lon === null) {
            out(['ok'=>false,'error'=>'Invalid coordinates'], 422);
        }
        $nearest = tithikaNearestLocal((float)$lat,(float)$lon);
        if ($nearest && (float)$nearest['distance_km'] <= 250.0) {
            out(['ok'=>true,'timezone'=>(string)$nearest['timezone'],'source'=>'offline-index'], 200, true);
        }
        $regional = tithikaRegionalTimezone((float)$lat,(float)$lon);
        if ($regional !== null) {
            out(['ok'=>true,'timezone'=>$regional,'source'=>'offline-region'], 200, true);
        }
        try {
            $url = 'https://timeapi.io/api/timezone/coordinate?latitude=' . rawurlencode((string)$lat) . '&longitude=' . rawurlencode((string)$lon);
            $r = curlJson($url);
            $timezone = trim((string)($r['timeZone'] ?? $r['timezone'] ?? ''));
            if ($timezone === '' || !in_array($timezone, timezone_identifiers_list(), true)) {
                throw new RuntimeException('Timezone could not be resolved');
            }
            out(['ok'=>true,'timezone'=>$timezone,'source'=>'timeapi'], 200, true);
        } catch (Throwable $e) {
            out(['ok'=>false,'error'=>'Timezone could not be resolved offline or online'], 502);
        }
    }

    if ($action === 'search') {
        $q = trim((string)($_GET['q'] ?? ''));
        if (mb_strlen($q) < 2) out(['ok'=>true,'results'=>[]]);
        $results = tithikaLocalSearch($q, 6);
        if (count($results) < 6) {
            try {
                $url = 'https://nominatim.openstreetmap.org/search?format=jsonv2&limit=6&addressdetails=1&q=' . rawurlencode($q);
                $rows = curlJson($url);
                foreach ($rows as $r) {
                    $a = $r['address'] ?? [];
                    $city = $a['city'] ?? $a['town'] ?? $a['village'] ?? $a['municipality'] ?? $r['name'] ?? '';
                    $state = $a['state'] ?? ''; $country = $a['country'] ?? '';
                    $label = implode(', ', array_values(array_filter([$city, $state, $country]))) ?: ($r['display_name'] ?? '');
                    $duplicate = false;
                    foreach ($results as $existing) {
                        if (abs((float)$existing['lat']-(float)$r['lat']) < 0.02 && abs((float)$existing['lon']-(float)$r['lon']) < 0.02) {
                            $duplicate = true; break;
                        }
                    }
                    if ($duplicate) continue;
                    $results[] = [
                        'label'=>$label,
                        'display_name'=>$r['display_name'] ?? '',
                        'lat'=>(float)$r['lat'],
                        'lon'=>(float)$r['lon'],
                        'timezone'=>null,
                        'elevation'=>null,
                        'source'=>'nominatim',
                    ];
                    if (count($results) >= 6) break;
                }
            } catch (Throwable $e) {
                // Offline results remain usable when the external provider is unavailable.
            }
        }
        out(['ok'=>true,'results'=>array_slice($results,0,6),'offline'=>count(tithikaLocalSearch($q,6))>0], 200, true);
    }

    if ($action === 'calculate') {
        $payload = readPayload();
        $data = runPythonEngine('python/choghadiya.py', $payload);
        if (!($data['ok'] ?? false)) out($data, 422);
        out($data);
    }

    if ($action === 'panchang') {
        $payload = readPayload();
        $data = runPythonEngine('python/panchang.py', $payload);
        if (!($data['ok'] ?? false)) {
            $status = (($data['code'] ?? '') === 'PANCHANG_DEPENDENCY_MISSING') ? 503 : 422;
            out($data, $status);
        }
        out($data, 200, true);
    }

    if ($action === 'panchang-month') {
        $payload = readPayload();
        $data = runPythonEngine('python/panchang_month.py', $payload);
        if (!($data['ok'] ?? false)) out($data, 422);
        out($data, 200, true);
    }

    if ($action === 'lunar-occurrences') {
        $payload = readPayload();
        $kind = strtolower(trim((string)($_GET['kind'] ?? 'ekadashi')));
        if (!in_array($kind, ['ekadashi','purnima','amavasya'], true)) {
            out(['ok'=>false,'error'=>'Unsupported occurrence kind'], 422);
        }
        $payload['kind'] = $kind;
        $data = runPythonEngine('python/lunar_occurrences.py', $payload);
        if (!($data['ok'] ?? false)) out($data, 422);
        out($data, 200, true);
    }

    if ($action === 'sankranti') {
        $payload = readPayload();
        $data = runPythonEngine('python/sankranti.py', $payload);
        if (!($data['ok'] ?? false)) out($data, 422);
        out($data, 200, true);
    }

    if ($action === 'observances') {
        $payload = readPayload();
        $kind = strtolower(trim((string)($_GET['kind'] ?? 'pradosh')));
        if (!in_array($kind, ['pradosh','sankashti','shivaratri'], true)) {
            out(['ok'=>false,'error'=>'Unsupported observance kind'], 422);
        }
        $payload['kind'] = $kind;
        $data = runPythonEngine('python/observances.py', $payload);
        if (!($data['ok'] ?? false)) out($data, 422);
        out($data, 200, true);
    }

    if ($action === 'vrat-recurrence') {
        $payload = readPayload();
        $mode = strtolower(trim((string)($_GET['mode'] ?? 'durgashtami')));
        if (!in_array($mode, ['satyanarayana','durgashtami','skanda-sashti','karthigai','rohini','sawan-somwar','mangala-gauri'], true)) {
            out(['ok'=>false,'error'=>'Unsupported Vrat recurrence mode'], 422);
        }
        $payload['mode'] = $mode;
        $data = runPythonEngine('python/vrat_recurrence.py', $payload);
        if (!($data['ok'] ?? false)) out($data, 422);
        out($data, 200, true);
    }

    if ($action === 'mahadwadashi') {
        $payload = readPayload();
        $data = runPythonEngine('python/mahadwadashi.py', $payload);
        if (!($data['ok'] ?? false)) out($data, 422);
        out($data, 200, true);
    }

    if ($action === 'dwadashi') {
        $payload = readPayload();
        $data = runPythonEngine('python/dwadashi.py', $payload);
        if (!($data['ok'] ?? false)) out($data, 422);
        out($data, 200, true);
    }

    if ($action === 'festival') {
        $payload = readPayload();
        $kind = strtolower(trim((string)($_GET['kind'] ?? 'ganesh-chaturthi')));
        if (!in_array($kind, ['ganesh-chaturthi','raksha-bandhan','navratri','dussehra','holi','karwa-chauth','janmashtami','rama-navami','hanuman-jayanti','akshaya-tritiya','vat-savitri','durga-puja','diwali'], true)) {
            out(['ok'=>false,'error'=>'Unsupported festival kind'], 422);
        }
        $payload['kind'] = $kind;
        $data = runPythonEngine('python/festivals.py', $payload);
        if (!($data['ok'] ?? false)) out($data, 422);
        out($data, 200, true);
    }

    if ($action === 'muhurat-rules') {
        $payload = readPayload();
        $data = runPythonEngine('python/muhurat_rules.py', $payload);
        if (!($data['ok'] ?? false)) out($data, 422);
        out($data, 200, true);
    }

    if ($action === 'specialized-muhurat') {
        $payload = readPayload();
        $profile = strtolower(trim((string)($_GET['profile'] ?? 'vivah')));
        if (!in_array($profile, ['vivah','griha-pravesh','property','vehicle','namakarana','annaprashana','mundana'], true)) {
            out(['ok'=>false,'error'=>'Unsupported Muhurat profile'], 422);
        }
        $payload['profile'] = $profile;
        $data = runPythonEngine('python/specialized_muhurat.py', $payload);
        if (!($data['ok'] ?? false)) out($data, 422);
        out($data, 200, true);
    }

    if ($action === 'muhurat-reuse') {
        $payload = readPayload();
        $mode = strtolower(trim((string)($_GET['mode'] ?? 'hora')));
        if (!in_array($mode, ['hora','panchaka-rahita','auspicious-yoga','sarvartha-siddhi','amrit-siddhi','guru-pushya','ravi-pushya','dwipushkar','tripushkar','ravi-yoga'], true)) {
            out(['ok'=>false,'error'=>'Unsupported Muhurat reuse mode'], 422);
        }
        $payload['mode'] = $mode;
        $data = runPythonEngine('python/muhurat_reuse.py', $payload);
        if (!($data['ok'] ?? false)) out($data, 422);
        out($data, 200, true);
    }

    if ($action === 'panchang-utility') {
        $payload = readPayload();
        $mode = strtolower(trim((string)($_GET['mode'] ?? 'tarabalam')));
        if (!in_array($mode, ['tarabalam','chandrabalam','panchak','bhadra','all'], true)) {
            out(['ok'=>false,'error'=>'Unsupported Panchang utility mode'], 422);
        }
        $payload['mode'] = $mode;
        $data = runPythonEngine('python/panchang_utilities.py', $payload);
        if (!($data['ok'] ?? false)) out($data, 422);
        out($data, 200, true);
    }

    if ($action === 'panchang-reuse') {
        $payload = readPayload();
        $mode = strtolower(trim((string)($_GET['mode'] ?? 'sunrise')));
        if (!in_array($mode, ['sunrise','nakshatra','ganda-moola','abhijit-nakshatra','vinchudo','jwalamukhi','sankalpa','vedic-clock'], true)) {
            out(['ok'=>false,'error'=>'Unsupported Panchang reuse mode'], 422);
        }
        $payload['mode'] = $mode;
        $data = runPythonEngine('python/panchang_reuse.py', $payload);
        if (!($data['ok'] ?? false)) out($data, 422);
        out($data, 200, true);
    }

    if ($action === 'regional-calendar') {
        $payload = readPayload();
        $variant = strtolower(trim((string)($_GET['variant'] ?? 'hindi')));
        if (!in_array($variant, ['hindi','tamil','telugu','kannada','malayalam','gujarati','marathi','bengali','odia','assamese','iskcon','nepali','jain'], true)) {
            out(['ok'=>false,'error'=>'Unsupported regional calendar variant'], 422);
        }
        $payload['variant'] = $variant;
        $script = match($variant) {
            'nepali' => 'python/nepali_calendar.py',
            'jain' => 'python/jain_calendar.py',
            default => 'python/regional_calendar.py',
        };
        $data = runPythonEngine($script, $payload);
        if (!($data['ok'] ?? false)) out($data, 422);
        out($data, 200, true);
    }

    if ($action === 'phase-completion') {
        $payload = readPayload();
        $slug = trim((string)($payload['slug'] ?? ''), '/');
        $completion = require __DIR__ . '/config/completion.php';
        if (!in_array($slug, $completion, true)) {
            out(['ok'=>false,'error'=>'Unsupported completion route'], 422);
        }
        $payload['slug'] = $slug;
        $script = match (true) {
            $slug === 'panchang/gowri' => 'python/muhurat_completion.py',
            str_starts_with($slug, 'panchang/') => 'python/panchang_completion.py',
            str_starts_with($slug, 'muhurat/') => 'python/muhurat_completion.py',
            str_starts_with($slug, 'vrat/') => 'python/vrat_completion.py',
            str_starts_with($slug, 'calendars/'),
            str_starts_with($slug, 'festivals/') => 'python/festival_calendar_completion.py',
            str_starts_with($slug, 'jyotish/') => 'python/jyotish_secondary.py',
            str_starts_with($slug, 'planets/'),
            str_starts_with($slug, 'astronomy/') => 'python/astronomy_reference.py',
            default => null,
        };
        if ($script === null) out(['ok'=>false,'error'=>'Completion engine unavailable'], 422);
        $data = runPythonEngine($script, $payload);
        if (!($data['ok'] ?? false)) out($data, 422);
        out($data, 200, true);
    }

    if ($action === 'lagna') {
        $payload = readPayload();
        $data = runPythonEngine('python/lagna.py', $payload);
        if (!($data['ok'] ?? false)) out($data, 422);
        out($data, 200, true);
    }

    if ($action === 'planetary') {
        $payload = readPayload();
        $mode = strtolower(trim((string)($_GET['mode'] ?? 'positions')));
        if (!in_array($mode, ['positions','transit','retrograde','combustion'], true)) {
            out(['ok'=>false,'error'=>'Unsupported planetary mode'], 422);
        }
        $payload['mode'] = $mode;
        $data = runPythonEngine('python/planetary.py', $payload);
        if (!($data['ok'] ?? false)) out($data, 422);
        out($data, 200, true);
    }

    if ($action === 'jyotish') {
        $payload = readPayload();
        $mode = strtolower(trim((string)($_GET['mode'] ?? 'birthstar')));
        if (!in_array($mode, ['birthstar','janma-lagna','moonsign','sunsign'], true)) {
            out(['ok'=>false,'error'=>'Unsupported Jyotish mode'], 422);
        }
        $payload['mode'] = $mode;
        $data = runPythonEngine('python/jyotish.py', $payload);
        if (!($data['ok'] ?? false)) out($data, 422);
        out($data, 200, true);
    }

    if ($action === 'aspects') {
        $payload = readPayload();
        $mode = strtolower(trim((string)($_GET['mode'] ?? 'mutual')));
        if (!in_array($mode, ['mutual','lunar','conjunctions','graha-yuddha'], true)) {
            out(['ok'=>false,'error'=>'Unsupported aspects mode'], 422);
        }
        $payload['mode'] = $mode;
        $data = runPythonEngine('python/aspects.py', $payload);
        if (!($data['ok'] ?? false)) out($data, 422);
        out($data, 200, true);
    }

    if ($action === 'eclipses') {
        $payload = readPayload();
        $mode = strtolower(trim((string)($_GET['mode'] ?? 'all')));
        if (!in_array($mode, ['all','solar','lunar'], true)) {
            out(['ok'=>false,'error'=>'Unsupported eclipse mode'], 422);
        }
        $payload['mode'] = $mode;
        $data = runPythonEngine('python/eclipses.py', $payload);
        if (!($data['ok'] ?? false)) out($data, 422);
        out($data, 200, true);
    }

    if ($action === 'kundali') {
        $payload = readPayload();
        $data = runPythonEngine('python/kundali.py', $payload);
        if (!($data['ok'] ?? false)) out($data, 422);
        out($data, 200, true);
    }

    if ($action === 'horoscope-analysis') {
        $payload = readPayload();
        $data = runPythonEngine('python/horoscope_analysis.py', $payload);
        if (!($data['ok'] ?? false)) out($data, 422);
        out($data, 200, true);
    }

    if ($action === 'jyotish-interpretation') {
        $payload = readPayload();
        $data = runPythonEngine('python/interpretation.py', $payload);
        if (!($data['ok'] ?? false)) out($data, 422);
        out($data, 200, true);
    }

    if ($action === 'jyotish-timeline') {
        $payload = readPayload();
        $data = runPythonEngine('python/timing_timeline.py', $payload);
        if (!($data['ok'] ?? false)) out($data, 422);
        out($data, 200, true);
    }

    if ($action === 'personal-rashifal') {
        $payload = readPayload();
        $mode = strtolower(trim((string)($_GET['mode'] ?? 'overview')));
        if (!in_array($mode, ['overview','daily','weekly','monthly','yearly'], true)) {
            out(['ok'=>false,'error'=>'Unsupported Rashifal mode'], 422);
        }
        $payload['mode'] = $mode;
        $data = runPythonEngine('python/personal_rashifal.py', $payload);
        if (!($data['ok'] ?? false)) out($data, 422);
        out($data, 200, true);
    }

    if ($action === 'vimshottari') {
        $payload = readPayload();
        $data = runPythonEngine('python/vimshottari.py', $payload);
        if (!($data['ok'] ?? false)) out($data, 422);
        out($data, 200, true);
    }

    if ($action === 'dosha') {
        $payload = readPayload();
        $mode = strtolower(trim((string)($_GET['mode'] ?? 'mangal')));
        if (!in_array($mode, ['mangal','kalasarpa','sade-sati'], true)) {
            out(['ok'=>false,'error'=>'Unsupported dosha mode'], 422);
        }
        $payload['mode'] = $mode;
        $data = runPythonEngine('python/doshas.py', $payload);
        if (!($data['ok'] ?? false)) out($data, 422);
        out($data, 200, true);
    }

    if ($action === 'ashtakavarga') {
        $payload = readPayload();
        $data = runPythonEngine('python/ashtakavarga.py', $payload);
        if (!($data['ok'] ?? false)) out($data, 422);
        out($data, 200, true);
    }

    if ($action === 'shadbala') {
        $payload = readPayload();
        $data = runPythonEngine('python/shadbala.py', $payload);
        if (!($data['ok'] ?? false)) out($data, 422);
        out($data, 200, true);
    }

    if ($action === 'vargas') {
        $payload = readPayload();
        $data = runPythonEngine('python/vargas.py', $payload);
        if (!($data['ok'] ?? false)) out($data, 422);
        out($data, 200, true);
    }

    if ($action === 'yogas') {
        $payload = readPayload();
        $data = runPythonEngine('python/yogas.py', $payload);
        if (!($data['ok'] ?? false)) out($data, 422);
        out($data, 200, true);
    }

    if ($action === 'matching') {
        $payload = readPayload();
        $mode = strtolower(trim((string)($_GET['mode'] ?? 'horoscope')));
        if (!in_array($mode, ['horoscope','nakshatra'], true)) {
            out(['ok'=>false,'error'=>'Unsupported matching mode'], 422);
        }
        $payload['mode'] = $mode;
        $data = runPythonEngine('python/matching.py', $payload);
        if (!($data['ok'] ?? false)) out($data, 422);
        out($data, 200, true);
    }

    if ($action === 'marriage-analysis') {
        $payload = readPayload();
        $data = runPythonEngine('python/marriage_analysis.py', $payload);
        if (!($data['ok'] ?? false)) out($data, 422);
        out($data, 200, true);
    }

    if ($action === 'seasons') {
        $payload = readPayload();
        $data = runPythonEngine('python/seasons.py', $payload);
        if (!($data['ok'] ?? false)) out($data, 422);
        out($data, 200, true);
    }

    if ($action === 'home-dashboard') {
        $payload = readPayload();
        $data = runPythonEngine('python/home_dashboard.py', $payload);
        if (!($data['ok'] ?? false)) out($data, 422);
        out($data, 200, true);
    }

    if ($action === 'notification-agenda') {
        $payload = readPayload();
        $data = runPythonEngine('python/notification_agenda.py', $payload);
        if (!($data['ok'] ?? false)) out($data, 422);
        out($data, 200, true);
    }

    $intelligenceModes = [
        'ai-health' => 'health',
        'ai-advisor' => 'advisor',
        'ai-jyotish' => 'jyotish',
        'ai-ask' => 'ask',
        'ai-profile' => 'profile',
        'ai-quality' => 'quality',
    ];
    if (isset($intelligenceModes[$action])) {
        $payload = readPayload();
        $payload['mode'] = $intelligenceModes[$action];
        $data = runPythonEngine('python/intelligence_gateway.py', $payload);
        if (!($data['ok'] ?? false)) out($data, 422);
        out($data, 200, $action === 'ai-health');
    }

    out(['ok'=>false,'error'=>'Unknown action'], 404);
} catch (Throwable $e) {
    out(['ok'=>false,'error'=>$e->getMessage()], 500);
}