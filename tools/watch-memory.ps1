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
$heartbeatPath = Join-Path $logDir "memory-auto.heartbeat"
$buildScript = Join-Path $PSScriptRoot "build-context-pack.ps1"
$relationshipMapScript = Join-Path $PSScriptRoot "build-relationship-map.ps1"

New-Item -ItemType Directory -Force -Path $logDir | Out-Null

function Write-MemoryLog {
    param([string]$Message)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Add-Content -LiteralPath $logPath -Value "[$timestamp] $Message" -Encoding UTF8
}

function Write-Heartbeat {
    # Метка живости watcher: обновляется каждый цикл, даже без изменений.
    # status-memory-auto.ps1 проверяет её свежесть и поднимает тревогу,
    # если watcher молча умер (Task Scheduler уронил процесс и т.п.).
    # Файл параллельно читают status-скрипты, поэтому запись идет с retry
    # и не имеет права ронять watcher: пропущенный heartbeat лучше мертвой памяти
    # (авария 2026-06-30: одна блокировка файла убила watcher на несколько суток).
    $ts = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ss") + "Z"
    for ($attempt = 1; $attempt -le 5; $attempt++) {
        try {
            Set-Content -LiteralPath $heartbeatPath -Value $ts -Encoding UTF8 -ErrorAction Stop
            return
        } catch {
            Start-Sleep -Milliseconds (200 * $attempt)
        }
    }
    Write-MemoryLog "Heartbeat write failed after 5 retries: $heartbeatPath"
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
                    $_.FullName -notlike "*\docs\relationship-maps\*" -and
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

function Build-RelationshipMap {
    if (-not (Test-Path -LiteralPath $relationshipMapScript -PathType Leaf)) {
        Write-MemoryLog "Relationship map skipped: script not found: $relationshipMapScript"
        return
    }

    try {
        & $relationshipMapScript -Quiet | Out-Null
        Write-MemoryLog "Relationship map rebuilt."
    } catch {
        Write-MemoryLog "Relationship map rebuild failed: $($_.Exception.Message)"
    }
}

function Build-DashboardData {
    $python = Join-Path $root ".venv-sml\Scripts\python.exe"
    $exportScript = Join-Path $root "apps\aion-vision\scripts\export-sml-dashboard.py"

    if (-not (Test-Path -LiteralPath $python -PathType Leaf)) {
        Write-MemoryLog "Dashboard export skipped: python not found: $python"
        return
    }
    if (-not (Test-Path -LiteralPath $exportScript -PathType Leaf)) {
        Write-MemoryLog "Dashboard export skipped: script not found: $exportScript"
        return
    }

    try {
        & $python -X utf8 $exportScript | Out-Null
        Write-MemoryLog "Dashboard data exported."
    } catch {
        Write-MemoryLog "Dashboard export failed: $($_.Exception.Message)"
    }
}

function Backup-SmlDatabase {
    $python = Join-Path $root ".venv-sml\Scripts\python.exe"
    $backupScript = Join-Path $PSScriptRoot "backup-sml.py"

    if (-not (Test-Path -LiteralPath $python -PathType Leaf)) {
        return
    }
    if (-not (Test-Path -LiteralPath $backupScript -PathType Leaf)) {
        return
    }

    try {
        & $python -X utf8 $backupScript --if-stale --verify | Out-Null
        Write-MemoryLog "SML backup checked."
    } catch {
        Write-MemoryLog "SML backup failed: $($_.Exception.Message)"
    }
}

function Build-MemoryLayers {
    Build-ContextPack
    Build-RelationshipMap
    Build-DashboardData
    Backup-SmlDatabase
}

# Одновременно должен работать только один watcher: два экземпляра
# дерутся за heartbeat-файл и роняют друг друга.
$script:watcherMutex = New-Object System.Threading.Mutex($false, "Global\AionMemoryWatcher")
if (-not $script:watcherMutex.WaitOne(0)) {
    Write-MemoryLog "Watcher already running. Duplicate instance exits."
    exit 0
}

Write-MemoryLog "Memory watcher started. Root: $root. Interval: $IntervalSeconds sec."
Write-Heartbeat

$previous = $null
if (Test-Path -LiteralPath $statePath -PathType Leaf) {
    $previous = Get-Fingerprint
} else {
    Build-MemoryLayers
    $previous = Get-Fingerprint
}

while ($true) {
    Start-Sleep -Seconds $IntervalSeconds
    Write-Heartbeat
    $current = Get-Fingerprint

    if ($current -ne $previous) {
        Write-MemoryLog "Change detected. Waiting debounce: $DebounceSeconds sec."
        Start-Sleep -Seconds $DebounceSeconds
        Build-MemoryLayers
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
