$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
$logDir = Join-Path $root "logs"
$logPath = Join-Path $logDir "memory-auto.log"
$watchScript = Join-Path $PSScriptRoot "watch-memory.ps1"

New-Item -ItemType Directory -Force -Path $logDir | Out-Null

try {
    & $watchScript
} catch {
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Add-Content -LiteralPath $logPath -Value "[$timestamp] FATAL: $($_.Exception.Message)" -Encoding UTF8
    Add-Content -LiteralPath $logPath -Value "[$timestamp] FATAL_DETAILS: $($_ | Out-String)" -Encoding UTF8
    exit 1
}

