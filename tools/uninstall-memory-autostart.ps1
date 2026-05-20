$ErrorActionPreference = "Stop"

$taskName = "Aion File Memory Auto"
$task = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue

if ($task) {
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
    Write-Output "Removed scheduled task: $taskName"
} else {
    Write-Output "Scheduled task not found: $taskName"
}

