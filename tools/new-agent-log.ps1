param(
    [Parameter(Mandatory = $true)]
    [ValidateSet("codex", "cursor", "kiro")]
    [string]$Agent,

    [Parameter(Mandatory = $true)]
    [string]$Task
)

$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
$safeTask = ($Task.ToLowerInvariant() -replace '[^a-zа-я0-9]+', '-' -replace '^-|-$', '')
if ([string]::IsNullOrWhiteSpace($safeTask)) {
    $safeTask = "task"
}

$timestamp = Get-Date -Format "yyyy-MM-dd-HHmm"
$target = Join-Path $root "docs\agent-log\$timestamp-$Agent-$safeTask.md"
$template = Join-Path $root "docs\templates\agent-report.md"

Copy-Item -LiteralPath $template -Destination $target -NoClobber
Write-Output $target

