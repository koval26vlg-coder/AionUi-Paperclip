param(
    [int]$IntervalSeconds = 15,
    [int]$DebounceSeconds = 5,
    [switch]$Once
)

$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
$logDir = Join-Path $root "logs"
$logPath = Join-Path $logDir "memory-auto.log"
$statePath = Join-Path $logDir "memory-auto.state"
$buildScript = Join-Path $PSScriptRoot "build-context-pack.ps1"

New-Item -ItemType Directory -Force -Path $logDir | Out-Null

function Write-MemoryLog {
    param([string]$Message)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Add-Content -LiteralPath $logPath -Value "[$timestamp] $Message" -Encoding UTF8
}

function Get-MemoryFiles {
    $roots = @(
        (Join-Path $root "AGENTS.md"),
        (Join-Path $root "README.md"),
        (Join-Path $root ".cursor"),
        (Join-Path $root ".kiro"),
        (Join-Path $root "docs"),
        (Join-Path $root "tools")
    )

    foreach ($item in $roots) {
        if (Test-Path -LiteralPath $item -PathType Leaf) {
            Get-Item -LiteralPath $item
        } elseif (Test-Path -LiteralPath $item -PathType Container) {
            Get-ChildItem -LiteralPath $item -Recurse -File -Force |
                Where-Object {
                    $_.FullName -notlike "*\docs\context-packs\*" -and
                    $_.FullName -notlike "*\tools\__pycache__\*" -and
                    $_.FullName -notlike "*\logs\*"
                }
        }
    }
}

function Get-Fingerprint {
    $rows = Get-MemoryFiles |
        Sort-Object FullName |
        ForEach-Object {
            "$($_.FullName)|$($_.Length)|$($_.LastWriteTimeUtc.Ticks)"
        }

    return ($rows -join "`n")
}

function Build-ContextPack {
    & $buildScript | Out-Null
    Set-Content -LiteralPath $statePath -Value (Get-Date -Format "yyyy-MM-dd HH:mm:ss") -Encoding UTF8
    Write-MemoryLog "Context pack rebuilt."
}

Write-MemoryLog "Memory watcher started. Root: $root. Interval: $IntervalSeconds sec."

$previous = $null
if (Test-Path -LiteralPath $statePath -PathType Leaf) {
    $previous = Get-Fingerprint
} else {
    Build-ContextPack
    $previous = Get-Fingerprint
}

while ($true) {
    Start-Sleep -Seconds $IntervalSeconds
    $current = Get-Fingerprint

    if ($current -ne $previous) {
        Write-MemoryLog "Change detected. Waiting debounce: $DebounceSeconds sec."
        Start-Sleep -Seconds $DebounceSeconds
        Build-ContextPack
        $previous = Get-Fingerprint

        if ($Once) {
            break
        }
    } elseif ($Once) {
        Write-MemoryLog "No changes detected in once mode."
        break
    }
}

Write-MemoryLog "Memory watcher stopped."

