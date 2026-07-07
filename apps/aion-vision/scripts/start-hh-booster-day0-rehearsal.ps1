[CmdletBinding()]
param(
    [string]$HostAddress = "127.0.0.1",
    [int]$Port = 8787,
    [string]$PublicBaseUrl = "",
    [switch]$SkipBuild,
    [switch]$WriteSmoke,
    [switch]$RequireStablePublicUrl,
    [int]$TimeoutSeconds = 90,
    [switch]$PrintOnly
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$appDir = Split-Path -Parent $scriptDir
$repoRoot = Split-Path -Parent (Split-Path -Parent $appDir)
$dataDir = Join-Path $appDir "data"
$pythonPath = Join-Path $repoRoot ".venv-sml\Scripts\python.exe"
$startScript = Join-Path $scriptDir "start-hh-booster-test.ps1"
$tunnelScript = Join-Path $scriptDir "start-hh-booster-public-tunnel.ps1"
$preflightScript = Join-Path $scriptDir "preflight-hh-booster-test.ps1"
$watchScript = Join-Path $scriptDir "watch-hh-booster-test.ps1"
$publishKitScript = Join-Path $repoRoot "tools\hh_resume_booster_publish_kit.py"
$prelaunchScript = Join-Path $repoRoot "tools\hh_resume_booster_prelaunch_check.py"
$experimentStateScript = Join-Path $repoRoot "tools\hh_resume_booster_experiment_state.py"
$jsonlPath = Join-Path $dataDir "hh-booster-leads.jsonl"
$experimentPath = Join-Path $dataDir "hh-booster-experiment.json"
$publishKitPath = Join-Path $dataDir "hh-booster-publish-kit.md"
$displayHost = if ($HostAddress -eq "0.0.0.0") { "127.0.0.1" } else { $HostAddress }
$localBaseUrl = "http://${displayHost}:$Port"

function Normalize-BaseUrl {
    param([string]$BaseUrl)
    return $BaseUrl.Trim().TrimEnd("/")
}

function Is-EphemeralTunnelUrl {
    param([string]$BaseUrl)
    if (-not $BaseUrl.Trim()) {
        return $false
    }
    try {
        $uri = [System.Uri]$BaseUrl
    }
    catch {
        return $false
    }
    $hostName = $uri.Host.ToLowerInvariant().TrimEnd(".")
    return (
        $hostName.EndsWith(".loca.lt") -or
        $hostName.EndsWith(".ngrok-free.app") -or
        $hostName.EndsWith(".trycloudflare.com") -or
        $hostName.EndsWith(".localhost.run")
    )
}

function Test-JsonEndpoint {
    param([string]$Url)
    try {
        $response = Invoke-WebRequest -UseBasicParsing -Uri $Url -TimeoutSec 3
        return ($response.StatusCode -eq 200)
    }
    catch {
        return $false
    }
}

function Wait-JsonEndpoint {
    param(
        [string]$Url,
        [int]$TimeoutSeconds,
        [string]$Label
    )
    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    $lastError = ""
    do {
        try {
            $response = Invoke-WebRequest -UseBasicParsing -Uri $Url -TimeoutSec 3
            if ($response.StatusCode -eq 200) {
                return $true
            }
            $lastError = "HTTP $($response.StatusCode)"
        }
        catch {
            $lastError = $_.Exception.Message
        }
        Start-Sleep -Milliseconds 500
    } while ((Get-Date) -lt $deadline)

    throw "Timed out waiting for $Label at $Url. Last error: $lastError"
}

function Wait-TunnelUrl {
    param(
        [string]$LogPath,
        [int]$TimeoutSeconds
    )
    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    do {
        if (Test-Path -LiteralPath $LogPath) {
            $text = Get-Content -LiteralPath $LogPath -Raw
            $match = [regex]::Match($text, "https://[a-z0-9-]+\.(loca\.lt|trycloudflare\.com|ngrok-free\.app)")
            if ($match.Success) {
                return $match.Value
            }
        }
        Start-Sleep -Milliseconds 500
    } while ((Get-Date) -lt $deadline)

    throw "Timed out waiting for public tunnel URL in $LogPath"
}

function Resolve-WindowsPowerShellExe {
    $command = Get-Command "powershell.exe" -ErrorAction SilentlyContinue
    if ($command -and $command.Source) {
        return $command.Source
    }

    $windowsRoot = if ($env:WINDIR) { $env:WINDIR } else { "C:\Windows" }
    $candidates = @(
        (Join-Path $windowsRoot "System32\WindowsPowerShell\v1.0\powershell.exe"),
        (Join-Path $windowsRoot "Sysnative\WindowsPowerShell\v1.0\powershell.exe")
    )
    foreach ($candidate in $candidates) {
        if (Test-Path -LiteralPath $candidate) {
            return $candidate
        }
    }

    throw "Windows PowerShell executable not found. Checked PATH and $($candidates -join ', ')"
}

function Start-VisiblePowerShell {
    param(
        [string]$Command,
        [string]$WorkingDirectory
    )
    $powershellExe = Resolve-WindowsPowerShellExe
    return Start-Process `
        -FilePath $powershellExe `
        -ArgumentList @("-NoExit", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", $Command) `
        -WorkingDirectory $WorkingDirectory `
        -WindowStyle Normal `
        -PassThru
}

function Require-Path {
    param([string]$Path)
    if (-not (Test-Path -LiteralPath $Path)) {
        throw "Required path not found: $Path"
    }
}

foreach ($path in @(
    $pythonPath,
    $startScript,
    $tunnelScript,
    $preflightScript,
    $watchScript,
    $publishKitScript,
    $prelaunchScript,
    $experimentStateScript
)) {
    Require-Path -Path $path
}

if (-not (Test-Path -LiteralPath $dataDir)) {
    New-Item -ItemType Directory -Path $dataDir | Out-Null
}

$visiblePowerShellExe = Resolve-WindowsPowerShellExe
$stamp = Get-Date -Format "yyyyMMdd-HHmmss"
$tunnelLogPath = Join-Path $dataDir "hh-booster-public-tunnel-$stamp.log"
$metadataPath = Join-Path $dataDir "hh-booster-day0-rehearsal-$stamp.json"
$serverStarted = $false
$serverPid = $null
$tunnelPid = $null

function Write-RehearsalMetadata {
    param(
        [string]$Status,
        [string]$Reason = "",
        [object]$Prelaunch = $null,
        [object[]]$BlockingFailures = @(),
        [object]$ExperimentStatus = $null
    )

    if (-not $ExperimentStatus) {
        try {
            $statusRawForMetadata = & $pythonPath $experimentStateScript --state $experimentPath --data $jsonlPath status --json
            if ($LASTEXITCODE -eq 0) {
                $ExperimentStatus = $statusRawForMetadata | ConvertFrom-Json
            }
        }
        catch {
            $ExperimentStatus = $null
        }
    }

    $startedAt = $null
    $totalLeads = $null
    if ($ExperimentStatus) {
        $startedAt = $ExperimentStatus.state.startedAt
        $totalLeads = $ExperimentStatus.summary.total_leads
    }

    $metadata = [ordered]@{
        generatedAt = (Get-Date).ToString("o")
        status = $Status
        reason = $Reason
        localBaseUrl = $localBaseUrl
        publicBaseUrl = $publicBase
        serverStarted = $serverStarted
        serverPid = $serverPid
        tunnelPid = $tunnelPid
        tunnelLogPath = $tunnelLogPath
        publishKitPath = $publishKitPath
        experimentStartedAt = $startedAt
        totalLeads = $totalLeads
        prelaunchStatus = if ($Prelaunch) { $Prelaunch.status } else { $null }
        prelaunchFailures = if ($Prelaunch) { $Prelaunch.failed } else { $null }
        prelaunchWarnings = if ($Prelaunch) { $Prelaunch.warnings } else { $null }
        blockingFailures = @($BlockingFailures | ForEach-Object { $_.name })
        note = "Rehearsal only. It does not start experiment and does not write launch manifest."
    }
    $metadata | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $metadataPath -Encoding UTF8
}

$serverCommand = "& '$startScript' -HostAddress '$HostAddress' -Port $Port"
if ($SkipBuild) {
    $serverCommand += " -SkipBuild"
}

$publicBase = Normalize-BaseUrl $PublicBaseUrl
$tunnelCommand = "& '$tunnelScript' -HostAddress '$HostAddress' -Port $Port -LogPath '$tunnelLogPath'"
$preflightCommand = "& '$preflightScript' -BaseUrl '$localBaseUrl'"
if ($publicBase) {
    $preflightCommand += " -PublicBaseUrl '$publicBase'"
}
if ($WriteSmoke) {
    $preflightCommand += " -WriteSmoke"
}

Write-Host ""
Write-Host "HH Resume Booster day-0 rehearsal"
Write-Host "================================="
Write-Host "Local URL      : $localBaseUrl"
Write-Host "Public URL     : $(if ($publicBase) { $publicBase } else { 'auto localtunnel' })"
Write-Host "Tunnel log     : $tunnelLogPath"
Write-Host "Metadata       : $metadataPath"
Write-Host "Visible shell  : $visiblePowerShellExe"
Write-Host "Start timer    : no"
Write-Host "Write manifest : no"
Write-Host "Write smoke    : $(if ($WriteSmoke) { 'yes' } else { 'no' })"
Write-Host ""
Write-Host "Visible server command:"
Write-Host $serverCommand
Write-Host ""
if (-not $publicBase) {
    Write-Host "Visible tunnel command:"
    Write-Host $tunnelCommand
    Write-Host ""
}
Write-Host "After rehearsal, guarded launch command remains:"
Write-Host "& `"$scriptDir\prepare-hh-booster-public-launch.ps1`" -PublicBaseUrl `"PUBLIC_URL`" -OperatorBaseUrl `"$localBaseUrl`" -CheckPublicHttp -FreshRehearsalMinutes 15 -StartExperiment"
Write-Host ""

if ($PrintOnly) {
    Write-Host "PrintOnly: no server/tunnel/process started."
    exit 0
}

$serverStarted = $false
$serverPid = $null
if (-not (Test-JsonEndpoint -Url "$localBaseUrl/api/hh-booster/experiment")) {
    $serverProcess = Start-VisiblePowerShell -Command $serverCommand -WorkingDirectory $repoRoot
    $serverStarted = $true
    $serverPid = $serverProcess.Id
    Write-Host "Started visible server window PID $serverPid"
}
else {
    Write-Host "Local server already responds at $localBaseUrl"
}

Wait-JsonEndpoint -Url "$localBaseUrl/api/hh-booster/experiment" -TimeoutSeconds $TimeoutSeconds -Label "local HH experiment API" | Out-Null

$tunnelPid = $null
if (-not $publicBase) {
    $tunnelProcess = Start-VisiblePowerShell -Command $tunnelCommand -WorkingDirectory $repoRoot
    $tunnelPid = $tunnelProcess.Id
    Write-Host "Started visible tunnel window PID $tunnelPid"
    $publicBase = Wait-TunnelUrl -LogPath $tunnelLogPath -TimeoutSeconds $TimeoutSeconds
}

$publicBaseIsEphemeral = Is-EphemeralTunnelUrl -BaseUrl $publicBase
if ($RequireStablePublicUrl -and $publicBaseIsEphemeral) {
    throw "PublicBaseUrl is a temporary tunnel: $publicBase. Use a stable domain or rerun without -RequireStablePublicUrl."
}

Wait-JsonEndpoint -Url "$publicBase/api/hh-booster/experiment" -TimeoutSeconds $TimeoutSeconds -Label "public HH experiment API" | Out-Null

$preflightArgs = @{
    BaseUrl = $localBaseUrl
    PublicBaseUrl = $publicBase
}
if ($WriteSmoke) {
    $preflightArgs.WriteSmoke = $true
}
& $preflightScript @preflightArgs
$preflightExitCode = $LASTEXITCODE
if ($preflightExitCode -ne 0) {
    Write-RehearsalMetadata -Status "failed" -Reason "preflight exited with code $preflightExitCode"
    Write-Host "Metadata : $metadataPath"
    exit $preflightExitCode
}

& $pythonPath $publishKitScript --public-base-url $publicBase --operator-base-url $localBaseUrl --out $publishKitPath --write
$publishKitExitCode = $LASTEXITCODE
if ($publishKitExitCode -ne 0) {
    Write-RehearsalMetadata -Status "failed" -Reason "publish kit generation exited with code $publishKitExitCode"
    Write-Host "Metadata : $metadataPath"
    exit $publishKitExitCode
}

$prelaunchRaw = & $pythonPath $prelaunchScript --operator-base-url $localBaseUrl --public-base-url $publicBase --check-public-http --json
$prelaunchExitCode = $LASTEXITCODE
$prelaunch = $prelaunchRaw | ConvertFrom-Json
$allowedFailures = @("experiment_started", "launch_manifest")
$blockingFailures = @(
    $prelaunch.checks |
        Where-Object {
            $_.status -eq "fail" -and
            ($allowedFailures -notcontains $_.name)
        }
)

$statusRaw = & $pythonPath $experimentStateScript --state $experimentPath --data $jsonlPath status --json
$status = $statusRaw | ConvertFrom-Json

$rehearsalStatus = if ($blockingFailures.Count -gt 0) { "blocked" } else { "ready_for_launch" }
$rehearsalReason = if ($blockingFailures.Count -gt 0) { "prelaunch has blocking failures beyond experiment_started/launch_manifest" } else { "only expected prelaunch blockers remain" }
Write-RehearsalMetadata -Status $rehearsalStatus -Reason $rehearsalReason -Prelaunch $prelaunch -BlockingFailures $blockingFailures -ExperimentStatus $status

Write-Host ""
Write-Host "Rehearsal summary"
Write-Host "-----------------"
Write-Host "Operator : $localBaseUrl/#hh-booster"
Write-Host "Public   : $publicBase/#hh-booster-public"
Write-Host "Kit      : $publishKitPath"
Write-Host "Metadata : $metadataPath"
Write-Host "Started  : $(if ($status.state.startedAt) { $status.state.startedAt } else { 'no' })"
Write-Host "Leads    : $($status.summary.total_leads)"
Write-Host "Prelaunch: $($prelaunch.status), failed=$($prelaunch.failed), warnings=$($prelaunch.warnings)"
if ($blockingFailures.Count -gt 0) {
    Write-Host "Blocking failures:"
    foreach ($failure in $blockingFailures) {
        Write-Host ("- {0}: {1}" -f $failure.name, $failure.detail)
    }
    exit 2
}

Write-Host ""
Write-Host "Expected remaining blockers before publishing:"
Write-Host "- Start experiment explicitly."
Write-Host "- Save launch manifest after start."
if ($publicBaseIsEphemeral) {
    Write-Host "- Temporary tunnel warning: rerun public API/prelaunch immediately before publishing links."
}
exit 0
