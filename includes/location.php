<?php
declare(strict_types=1);

function tithikaLocationIndex(): array {
    static $rows;
    if ($rows !== null) return $rows;
    $path = dirname(__DIR__) . '/config/location-index.php';
    $rows = is_file($path) ? require $path : [];
    return is_array($rows) ? $rows : [];
}

function tithikaHaversineKm(float $lat1, float $lon1, float $lat2, float $lon2): float {
    $r = 6371.0088;
    $p1 = deg2rad($lat1); $p2 = deg2rad($lat2);
    $dp = deg2rad($lat2 - $lat1);
    $dl = deg2rad($lon2 - $lon1);
    $a = sin($dp/2)**2 + cos($p1) * cos($p2) * sin($dl/2)**2;
    return 2 * $r * asin(min(1.0, sqrt($a)));
}

function tithikaLocationLabel(array $row): string {
    return implode(', ', array_values(array_filter([
        (string)($row['city'] ?? ''),
        (string)($row['state'] ?? ''),
        (string)($row['country'] ?? ''),
    ])));
}

function tithikaLocalSearch(string $query, int $limit = 6): array {
    $needle = mb_strtolower(trim($query));
    if ($needle === '') return [];
    $scored = [];
    foreach (tithikaLocationIndex() as $row) {
        $label = tithikaLocationLabel($row);
        $hay = mb_strtolower($label);
        $city = mb_strtolower((string)($row['city'] ?? ''));
        $score = null;
        if ($city === $needle) $score = 0;
        elseif (str_starts_with($city, $needle)) $score = 1;
        elseif (str_contains($city, $needle)) $score = 2;
        elseif (str_contains($hay, $needle)) $score = 3;
        if ($score === null) continue;
        $scored[] = [$score, strlen($label), $row];
    }
    usort($scored, static fn($a,$b) => [$a[0],$a[1]] <=> [$b[0],$b[1]]);
    $out = [];
    foreach (array_slice($scored, 0, max(1,$limit)) as $item) {
        $row = $item[2];
        $out[] = [
            'label' => tithikaLocationLabel($row),
            'display_name' => tithikaLocationLabel($row),
            'lat' => (float)$row['lat'],
            'lon' => (float)$row['lon'],
            'timezone' => (string)$row['timezone'],
            'elevation' => isset($row['elevation']) ? (float)$row['elevation'] : null,
            'source' => 'offline-index',
        ];
    }
    return $out;
}

function tithikaNearestLocal(float $lat, float $lon): ?array {
    $best = null; $bestKm = INF;
    foreach (tithikaLocationIndex() as $row) {
        $km = tithikaHaversineKm($lat,$lon,(float)$row['lat'],(float)$row['lon']);
        if ($km < $bestKm) { $bestKm = $km; $best = $row; }
    }
    if (!$best) return null;
    $best['distance_km'] = $bestKm;
    return $best;
}

function tithikaRegionalTimezone(float $lat, float $lon): ?string {
    // Specific neighboring-country regions precede the broad India fallback.
    if ($lat >= 26.0 && $lat <= 31.0 && $lon >= 80.0 && $lon <= 89.0) return 'Asia/Kathmandu';
    if ($lat >= 5.5 && $lat <= 10.2 && $lon >= 79.0 && $lon <= 82.2) return 'Asia/Colombo';
    if ($lat >= 20.5 && $lat <= 26.8 && $lon >= 88.0 && $lon <= 92.8) return 'Asia/Dhaka';
    if ($lat >= 23.0 && $lat <= 37.2 && $lon >= 60.0 && $lon <= 78.5) return 'Asia/Karachi';
    if ($lat >= 6.0 && $lat <= 37.5 && $lon >= 68.0 && $lon <= 98.0) return 'Asia/Kolkata';
    return null;
}
