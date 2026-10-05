<?php
declare(strict_types=1);
header('Content-Type: application/json; charset=utf-8');
header('Cache-Control: no-store, max-age=0');

function out(array $data, int $status = 200): never {
    http_response_code($status);
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
            'User-Agent: ChoghadiyaModern/1.0 (+https://example.com)'
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

$action = $_GET['action'] ?? 'calculate';
try {
    if ($action === 'reverse') {
        $lat = filter_input(INPUT_GET, 'lat', FILTER_VALIDATE_FLOAT);
        $lon = filter_input(INPUT_GET, 'lon', FILTER_VALIDATE_FLOAT);
        if ($lat === false || $lon === false || $lat === null || $lon === null) out(['ok'=>false,'error'=>'Invalid coordinates'], 422);
        $url = 'https://nominatim.openstreetmap.org/reverse?format=jsonv2&zoom=10&addressdetails=1&lat=' . rawurlencode((string)$lat) . '&lon=' . rawurlencode((string)$lon);
        $r = curlJson($url); $a = $r['address'] ?? [];
        $city = $a['city'] ?? $a['town'] ?? $a['village'] ?? $a['municipality'] ?? $a['county'] ?? 'Current location';
        $state = $a['state'] ?? ''; $country = $a['country'] ?? '';
        $label = implode(', ', array_values(array_filter([$city, $state, $country])));
        out(['ok'=>true,'label'=>$label ?: ($r['display_name'] ?? 'Current location')]);
    }
    if ($action === 'search') {
        $q = trim((string)($_GET['q'] ?? ''));
        if (mb_strlen($q) < 2) out(['ok'=>true,'results'=>[]]);
        $url = 'https://nominatim.openstreetmap.org/search?format=jsonv2&limit=6&addressdetails=1&q=' . rawurlencode($q);
        $rows = curlJson($url); $results = [];
        foreach ($rows as $r) {
            $a = $r['address'] ?? [];
            $city = $a['city'] ?? $a['town'] ?? $a['village'] ?? $a['municipality'] ?? $r['name'] ?? '';
            $state = $a['state'] ?? ''; $country = $a['country'] ?? '';
            $results[] = [
                'label' => implode(', ', array_values(array_filter([$city, $state, $country]))) ?: ($r['display_name'] ?? ''),
                'display_name' => $r['display_name'] ?? '',
                'lat' => (float)$r['lat'], 'lon' => (float)$r['lon']
            ];
        }
        out(['ok'=>true,'results'=>$results]);
    }
    if ($action !== 'calculate') out(['ok'=>false,'error'=>'Unknown action'], 404);

    $raw = file_get_contents('php://input') ?: '{}';
    $payload = json_decode($raw, true);
    if (!is_array($payload)) out(['ok'=>false,'error'=>'Invalid JSON'], 400);
    $lat = (float)($payload['lat'] ?? 19.0760); $lon = (float)($payload['lon'] ?? 72.8777);
    if ($lat < -90 || $lat > 90 || $lon < -180 || $lon > 180) out(['ok'=>false,'error'=>'Invalid coordinates'], 422);

    $script = __DIR__ . '/python/choghadiya.py';
    if (!is_file($script)) out(['ok'=>false,'error'=>'Calculation engine not found'], 500);
    $python = getenv('PYTHON_BIN') ?: 'python3';
    $desc = [0=>['pipe','r'],1=>['pipe','w'],2=>['pipe','w']];
    $proc = proc_open([$python, $script], $desc, $pipes, __DIR__, null, ['bypass_shell'=>true]);
    if (!is_resource($proc)) out(['ok'=>false,'error'=>'Unable to start Python calculation engine'], 500);
    fwrite($pipes[0], json_encode($payload, JSON_UNESCAPED_UNICODE)); fclose($pipes[0]);
    $stdout = stream_get_contents($pipes[1]); fclose($pipes[1]);
    $stderr = stream_get_contents($pipes[2]); fclose($pipes[2]);
    $exit = proc_close($proc);
    $data = json_decode($stdout ?: '{}', true);
    if (!is_array($data)) out(['ok'=>false,'error'=>'Invalid calculation response','detail'=>$stderr], 500);
    if ($exit !== 0 || !($data['ok'] ?? false)) out($data + ['detail'=>$stderr], 422);
    out($data);
} catch (Throwable $e) {
    out(['ok'=>false,'error'=>$e->getMessage()], 500);
}
