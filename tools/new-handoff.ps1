param(
    [Parameter(Mandatory = $true)]
    [string]$From,

    [Parameter(Mandatory = $true)]
    [string]$To,

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
$targetDir = Join-Path $root "docs\handoffs"
New-Item -ItemType Directory -Force -Path $targetDir | Out-Null

$target = Join-Path $targetDir "$timestamp-$From-to-$To-$safeTask.md"
$template = Join-Path $root "docs\templates\handoff.md"

Copy-Item -LiteralPath $template -Destination $target -NoClobber
Write-Output $target

