<?php
declare(strict_types=1);

function acquireEngineSlot(): mixed {
    // Shared per-server admission control limits PHP-FPM Python fan-out.
    // Use a private writable temp directory, never a public document root.
    $directory = rtrim((string)(getenv('TITHIKA_LOCK_DIR') ?: sys_get_temp_dir()), '/')
        . '/tithika-engine-slots';
    if (!is_dir($directory) && !@mkdir($directory, 0700, true) && !is_dir($directory)) {
        throw new RuntimeException('Calculation capacity unavailable');
    }
    $limit = max(1, min(16, (int)(getenv('TITHIKA_MAX_ENGINE_WORKERS') ?: 4)));
    for ($i = 0; $i < $limit; $i++) {
        $handle = @fopen($directory . '/worker-' . $i . '.lock', 'c');
        if (!is_resource($handle)) continue;
        if (flock($handle, LOCK_EX | LOCK_NB)) return $handle;
        fclose($handle);
    }
    throw new RuntimeException('Calculation capacity exhausted');
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
    $slot = acquireEngineSlot();
    try {
        $proc = proc_open([$python, $script], $desc, $pipes, __DIR__, $env, ['bypass_shell'=>true]);
    } catch (Throwable $e) {
        flock($slot, LOCK_UN); fclose($slot);
        throw $e;
    }
    if (!is_resource($proc)) {
        flock($slot, LOCK_UN); fclose($slot);
        throw new RuntimeException('Unable to start Python calculation engine');
    }
    $deadline = microtime(true) + 25.0;
    $maxOutput = 2097152;
    $maxError = 8192;
    $stdin = json_encode($payload, JSON_UNESCAPED_UNICODE);
    if ($stdin === false || strlen($stdin) > 32768) {
        proc_terminate($proc); proc_close($proc);
        flock($slot, LOCK_UN); fclose($slot);
        throw new RuntimeException('Invalid or oversized engine payload');
    }
    foreach ($pipes as $pipe) stream_set_blocking($pipe, false);
    $writeOffset = 0;
    $stdout = '';
    $stderr = '';
    $exit = -1;
    try {
        while (true) {
            if (microtime(true) >= $deadline) throw new RuntimeException('Calculation timed out');
            $read = [$pipes[1], $pipes[2]];
            $write = isset($pipes[0]) && is_resource($pipes[0]) ? [$pipes[0]] : [];
            $except = null;
            $ready = @stream_select($read, $write, $except, 0, 100000);
            if ($ready === false) throw new RuntimeException('Engine I/O failed');
            foreach ($read as $pipe) {
                $chunk = fread($pipe, 16384);
                if ($chunk === false) continue;
                if ($pipe === $pipes[1]) $stdout .= $chunk;
                else $stderr .= $chunk;
            }
            if (strlen($stdout) > $maxOutput || strlen($stderr) > $maxError) {
                throw new RuntimeException('Calculation output exceeds resource limit');
            }
            if ($write && isset($pipes[0]) && is_resource($pipes[0])) {
                $count = fwrite($pipes[0], substr($stdin, $writeOffset, 8192));
                if ($count === false) throw new RuntimeException('Engine input failed');
                $writeOffset += $count;
                if ($writeOffset >= strlen($stdin)) {
                    fclose($pipes[0]);
                    unset($pipes[0]);
                }
            }
            $status = proc_get_status($proc);
            if (!$status['running']) {
                $exit = (int)$status['exitcode'];
                // Drain remaining buffered output after worker exit.
                $stdout .= stream_get_contents($pipes[1]) ?: '';
                $stderr .= stream_get_contents($pipes[2]) ?: '';
                if (strlen($stdout) > $maxOutput || strlen($stderr) > $maxError) throw new RuntimeException('Calculation output exceeds resource limit');
                break;
            }
        }
    } catch (Throwable $e) {
        proc_terminate($proc);
        // Do not wait indefinitely for a worker that ignores termination.
        foreach ($pipes as $pipe) if (is_resource($pipe)) fclose($pipe);
        proc_close($proc);
        flock($slot, LOCK_UN); fclose($slot);
        throw $e;
    }
    foreach ($pipes as $pipe) if (is_resource($pipe)) fclose($pipe);
    proc_close($proc);
    flock($slot, LOCK_UN); fclose($slot);
    $data = json_decode($stdout ?: '{}', true);
    if (!is_array($data)) {
        throw new RuntimeException('Invalid calculation response' . ($stderr ? ': ' . trim($stderr) : ''));
    }
    if ($exit !== 0 || !($data['ok'] ?? false)) {
        error_log('[Tithika calculation] engine=' . basename($script) . ' exit=' . $exit . ' ' . substr($stderr, 0, 500));
        $data = ['ok'=>false, 'error'=>'Calculation unavailable'];
    }
    return $data;
}
