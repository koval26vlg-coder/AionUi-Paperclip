$ErrorActionPreference = "Continue"

$root = Split-Path -Parent $PSScriptRoot
$taskName = "Aion File Memory Auto"
$logPath = Join-Path $root "logs\memory-auto.log"
$packPath = Join-Path $root "docs\context-packs\context-pack-latest.md"

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

if (Test-Path -LiteralPath $packPath -PathType Leaf) {
    "Context pack: $packPath"
    "Context pack updated: $((Get-Item -LiteralPath $packPath).LastWriteTime)"
}

if (Test-Path -LiteralPath $logPath -PathType Leaf) {
    "Last log lines:"
    Get-Content -LiteralPath $logPath -Tail 20
} else {
    "Log not found: $logPath"
}

