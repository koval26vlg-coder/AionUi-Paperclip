$ErrorActionPreference = "Continue"

$root = Split-Path -Parent $PSScriptRoot
$taskName = "Aion File Memory Auto"
$logPath = Join-Path $root "logs\memory-auto.log"
$heartbeatPath = Join-Path $root "logs\memory-auto.heartbeat"
$packPath = Join-Path $root "docs\context-packs\context-pack-latest.md"
$mapPath = Join-Path $root "docs\relationship-maps\graphify-sml-relationship-map.md"
$mapJsonPath = Join-Path $root "docs\relationship-maps\graphify-sml-relationship-map.json"

# Порог тревоги: если heartbeat старше этого числа секунд — watcher, вероятно,
# мёртв. По умолчанию интервал watcher 15 сек, берём запас.
$HeartbeatStaleSeconds = 120

$task = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
if ($task) {
    $info = Get-ScheduledTaskInfo -TaskName $taskName
    [pscustomobject]@{
        TaskName = $task.TaskName
        State = $task.State
        LastRunTime = $info.LastRunTime
        LastTaskResult = $info.LastTaskResult
        NextRunTime = $info.NextRunTime
    }
} else {
    "Scheduled task not found: $taskName"
}

if (Test-Path -LiteralPath $heartbeatPath -PathType Leaf) {
    # Убираем BOM/пробелы; ISO 8601 с суффиксом Z надёжно парсит DateTimeOffset.
    $hbRaw = ((Get-Content -LiteralPath $heartbeatPath -Raw) -replace '^﻿', '').Trim()
    $hbTime = [ref]([DateTimeOffset]::MinValue)
    if ([DateTimeOffset]::TryParse($hbRaw, $hbTime)) {
        $ageSec = [int]([DateTimeOffset]::UtcNow - $hbTime.Value).TotalSeconds
        if ($ageSec -le $HeartbeatStaleSeconds) {
            "Heartbeat: OK (age ${ageSec}s, last $hbRaw)"
        } else {
            "Heartbeat: STALE (age ${ageSec}s > ${HeartbeatStaleSeconds}s) — watcher, вероятно, не работает!"
        }
    } else {
        "Heartbeat: present but unparseable ($hbRaw)"
    }
} else {
    "Heartbeat: MISSING ($heartbeatPath) — watcher не запускался после обновления."
}

if (Test-Path -LiteralPath $packPath -PathType Leaf) {
    "Context pack: $packPath"
    "Context pack updated: $((Get-Item -LiteralPath $packPath).LastWriteTime)"
}

if (Test-Path -LiteralPath $mapPath -PathType Leaf) {
    "Relationship map: $mapPath"
    "Relationship map updated: $((Get-Item -LiteralPath $mapPath).LastWriteTime)"
}

if (Test-Path -LiteralPath $mapJsonPath -PathType Leaf) {
    "Relationship map JSON: $mapJsonPath"
    "Relationship map JSON size: $((Get-Item -LiteralPath $mapJsonPath).Length) bytes"
}

if (Test-Path -LiteralPath $logPath -PathType Leaf) {
    "Last log lines:"
    Get-Content -LiteralPath $logPath -Tail 20
} else {
    "Log not found: $logPath"
}
