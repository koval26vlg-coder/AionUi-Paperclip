$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
$watchScript = Join-Path $PSScriptRoot "run-memory-watcher.ps1"
$taskName = "Aion File Memory Auto"
$pwshCandidates = @(
    "C:\Program Files\PowerShell\7\pwsh.exe",
    (Join-Path $env:ProgramFiles "PowerShell\7\pwsh.exe")
)
$powershell = $pwshCandidates | Where-Object { Test-Path -LiteralPath $_ -PathType Leaf } | Select-Object -First 1
if (-not $powershell) {
    $powershell = Join-Path $env:SystemRoot "System32\WindowsPowerShell\v1.0\powershell.exe"
}

if (-not (Test-Path -LiteralPath $watchScript -PathType Leaf)) {
    throw "Watcher script not found: $watchScript"
}

$argument = "-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$watchScript`""
$action = New-ScheduledTaskAction -Execute $powershell -Argument $argument -WorkingDirectory $root
# Триггер при входе пользователя — watcher поднимается автоматически после
# логина и держит heartbeat зелёным всю сессию.
$trigger = New-ScheduledTaskTrigger -AtLogOn -User $env:USERNAME
# Устойчивость к сбоям: много попыток перезапуска с коротким интервалом,
# чтобы heartbeat восстанавливался без ручного вмешательства. Лимита времени
# выполнения нет (бесконечный watcher).
$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -ExecutionTimeLimit ([TimeSpan]::Zero) `
    -RestartCount 100 `
    -RestartInterval (New-TimeSpan -Minutes 1) `
    -MultipleInstances IgnoreNew

Register-ScheduledTask `
    -TaskName $taskName `
    -Action $action `
    -Trigger $trigger `
    -Settings $settings `
    -Description "Automatically rebuilds D:\AionUi-Paperclip context pack and relationship-map memory layer when shared context files change." `
    -Force | Out-Null

Start-ScheduledTask -TaskName $taskName

Write-Output "Installed and started scheduled task: $taskName"
