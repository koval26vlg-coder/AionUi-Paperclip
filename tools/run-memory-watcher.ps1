$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
$logDir = Join-Path $root "logs"
$logPath = Join-Path $logDir "memory-auto.log"
$watchScript = Join-Path $PSScriptRoot "watch-memory.ps1"

New-Item -ItemType Directory -Force -Path $logDir | Out-Null

# Watcher должен переживать разовые сбои: после аварии перезапускаем его сами,
# а не ждем сутками ручного вмешательства (авария 2026-06-30).
$maxRestarts = 20
$restarts = 0

while ($true) {
    try {
        & $watchScript
        $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        Add-Content -LiteralPath $logPath -Value "[$timestamp] Watcher exited normally." -Encoding UTF8
        break
    } catch {
        $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        Add-Content -LiteralPath $logPath -Value "[$timestamp] FATAL: $($_.Exception.Message)" -Encoding UTF8
        Add-Content -LiteralPath $logPath -Value "[$timestamp] FATAL_DETAILS: $($_ | Out-String)" -Encoding UTF8

        $restarts++
        if ($restarts -ge $maxRestarts) {
            Add-Content -LiteralPath $logPath -Value "[$timestamp] Restart limit reached ($maxRestarts). Giving up." -Encoding UTF8
            exit 1
        }

        Add-Content -LiteralPath $logPath -Value "[$timestamp] Restarting watcher in 30 sec (attempt $restarts of $maxRestarts)." -Encoding UTF8
        Start-Sleep -Seconds 30
    }
}

