param(
    [int]$IntervalSec = 900,
    [int]$Days = 7,
    [switch]$Once
)

$ErrorActionPreference = "Stop"

$Root = "D:\AionUi-Paperclip"
$Python = Join-Path $Root ".venv-sml\Scripts\python.exe"
$Script = Join-Path $Root "tools\agent_limit_monitor.py"
$Latest = Join-Path $Root "docs\agent-limits\latest.md"

if (-not (Test-Path -LiteralPath $Python)) {
    throw "Python runtime not found: $Python"
}
if (-not (Test-Path -LiteralPath $Script)) {
    throw "Limit monitor script not found: $Script"
}

function Invoke-AgentLimitSnapshot {
    $stamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss zzz"
    Write-Host ""
    Write-Host "[$stamp] Agent limits snapshot (window: $Days days)"
    Write-Host ("-" * 78)
    & $Python $Script --days $Days
    if (Test-Path -LiteralPath $Latest) {
        Write-Host ("-" * 78)
        Write-Host "latest: $Latest"
    }
}

do {
    Invoke-AgentLimitSnapshot
    if ($Once) {
        break
    }
    Write-Host ""
    Write-Host "Next check in $IntervalSec sec. Press Ctrl+C to stop."
    Start-Sleep -Seconds $IntervalSec
} while ($true)
