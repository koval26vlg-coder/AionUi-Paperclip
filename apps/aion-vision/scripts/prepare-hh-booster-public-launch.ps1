[CmdletBinding()]
param(
    [string]$PublicBaseUrl = "",
    [string]$OperatorBaseUrl = "http://127.0.0.1:8787",
    [int]$Port = 8787,
    [switch]$SkipServerCheck,
    [switch]$CheckPublicHttp,
    [switch]$StartExperiment,
    [int]$FreshRehearsalMinutes = 15,
    [switch]$SkipFreshRehearsalCheck,
    [switch]$PrintOnly
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$appDir = Split-Path -Parent $scriptDir
$repoRoot = Split-Path -Parent (Split-Path -Parent $appDir)
$pythonPath = Join-Path $repoRoot ".venv-sml\Scripts\python.exe"
$experimentStateScript = Join-Path $repoRoot "tools\hh_resume_booster_experiment_state.py"
$manifestScript = Join-Path $repoRoot "tools\hh_resume_booster_launch_manifest.py"
$prelaunchScript = Join-Path $repoRoot "tools\hh_resume_booster_prelaunch_check.py"
$dataDir = Join-Path $appDir "data"
$manifestPath = Join-Path $dataDir "hh-booster-launch-manifest.md"
$jsonlPath = Join-Path $dataDir "hh-booster-leads.jsonl"
$experimentPath = Join-Path $dataDir "hh-booster-experiment.json"
$startScript = Join-Path $scriptDir "start-hh-booster-test.ps1"
$publicTunnelScript = Join-Path $scriptDir "start-hh-booster-public-tunnel.ps1"

function Normalize-BaseUrl {
    param([string]$BaseUrl)
    return $BaseUrl.Trim().TrimEnd("/")
}

function Is-PlaceholderUrl {
    param([string]$BaseUrl)
    if (-not $BaseUrl.Trim()) {
        return $true
    }
    $lowered = $BaseUrl.ToLowerInvariant()
    return (
        $lowered -match "public[_-]host" -or
        $lowered -match "your-public" -or
        $lowered -match "example\.(com|net|org|test)" -or
        $lowered -match "\.(example|test|invalid)(/|$)"
    )
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

function Convert-RehearsalTimestampUtc {
    param(
        $Value,
        [datetime]$Fallback
    )

    if ($Value -is [datetime]) {
        return ([datetime]$Value).ToUniversalTime()
    }

    try {
        return ([DateTimeOffset]::Parse([string]$Value)).UtcDateTime
    }
    catch {
        return $Fallback.ToUniversalTime()
    }
}

function Get-FreshRehearsalMetadata {
    param(
        [string]$BaseUrl,
        [int]$MaxAgeMinutes
    )

    if (-not (Test-Path -LiteralPath $dataDir)) {
        return $null
    }

    $nowUtc = (Get-Date).ToUniversalTime()
    $files = Get-ChildItem -LiteralPath $dataDir -Filter "hh-booster-day0-rehearsal-*.json" -ErrorAction SilentlyContinue |
        Sort-Object LastWriteTime -Descending
    foreach ($file in $files) {
        try {
            $record = Get-Content -LiteralPath $file.FullName -Raw | ConvertFrom-Json
        }
        catch {
            continue
        }

        if ((Normalize-BaseUrl $record.publicBaseUrl) -ne $BaseUrl) {
            continue
        }
        if ($record.status -ne "ready_for_launch") {
            continue
        }
        if ($record.blockingFailures -and $record.blockingFailures.Count -gt 0) {
            continue
        }

        $generatedAtUtc = Convert-RehearsalTimestampUtc -Value $record.generatedAt -Fallback $file.LastWriteTime
        $ageMinutes = ($nowUtc - $generatedAtUtc).TotalMinutes
        if ($ageMinutes -le $MaxAgeMinutes) {
            return [pscustomobject]@{
                path = $file.FullName
                ageMinutes = [math]::Round($ageMinutes, 2)
                record = $record
            }
        }
    }

    return $null
}

function Resolve-Tool {
    param([string[]]$Names)
    foreach ($name in $Names) {
        $cmd = Get-Command $name -ErrorAction SilentlyContinue
        if ($cmd) {
            return $cmd.Source
        }
    }
    return $null
}

function Write-TunnelOptions {
    $operator = Normalize-BaseUrl $OperatorBaseUrl
    Write-Host "Visible tunnel options:"
    $cloudflared = Resolve-Tool -Names @("cloudflared.exe", "cloudflared")
    $ngrok = Resolve-Tool -Names @("ngrok.exe", "ngrok")
    $ssh = Resolve-Tool -Names @("ssh.exe", "ssh")
    if ($cloudflared) {
        Write-Host "- cloudflared: cloudflared tunnel --url $operator"
    }
    if ($ngrok) {
        Write-Host "- ngrok: ngrok http $operator"
    }
    if (Test-Path -LiteralPath $publicTunnelScript) {
        Write-Host "- localtunnel via project launcher: & `"$publicTunnelScript`" -Port $Port"
    }
    else {
        Write-Host "- localtunnel via npx: npx localtunnel --port $Port"
    }
    if ($ssh) {
        Write-Host "- localhost.run via ssh: ssh -R 80:127.0.0.1:$Port nokey@localhost.run"
    }
    if (-not $cloudflared -and -not $ngrok) {
        Write-Host "- No installed cloudflared/ngrok found. Use a trusted tunnel/domain manually, or run localtunnel with npx in a visible terminal."
    }
}

if (-not (Test-Path -LiteralPath $pythonPath)) {
    throw "Python runtime not found: $pythonPath"
}
if (-not (Test-Path -LiteralPath $manifestScript)) {
    throw "Manifest script not found: $manifestScript"
}
if (-not (Test-Path -LiteralPath $experimentStateScript)) {
    throw "Experiment state script not found: $experimentStateScript"
}
if (-not (Test-Path -LiteralPath $prelaunchScript)) {
    throw "Prelaunch script not found: $prelaunchScript"
}
if (-not (Test-Path -LiteralPath $startScript)) {
    throw "Start script not found: $startScript"
}
if (-not (Test-Path -LiteralPath $publicTunnelScript)) {
    throw "Public tunnel helper not found: $publicTunnelScript"
}

$operatorBase = Normalize-BaseUrl $OperatorBaseUrl
$publicBase = Normalize-BaseUrl $PublicBaseUrl

Write-Host ""
Write-Host "HH Resume Booster public launch helper"
Write-Host "======================================"
Write-Host "Operator base : $operatorBase"
Write-Host "Public base   : $(if ($publicBase) { $publicBase } else { 'n/a' })"
Write-Host "Manifest      : $manifestPath"
Write-Host "Experiment    : $experimentPath"
Write-Host "Start now     : $(if ($StartExperiment) { 'yes' } else { 'no' })"
$freshRehearsalLabel = if ($FreshRehearsalMinutes -gt 0) { "$FreshRehearsalMinutes min" } else { "disabled" }
Write-Host "Fresh rehearsal: $freshRehearsalLabel"
Write-Host ""

if (-not $publicBase) {
    Write-Host "NO-GO: PublicBaseUrl is required before candidate links are published."
    Write-Host ""
    Write-Host "1. Start local server in a visible terminal:"
    Write-Host "& `"$startScript`" -Port $Port -SkipBuild"
    Write-Host ""
    Write-TunnelOptions
    Write-Host ""
    Write-Host "2. Rerun this helper with the real public URL:"
    Write-Host "& `"$PSCommandPath`" -PublicBaseUrl `"https://REAL_PUBLIC_HOST`""
    exit $(if ($PrintOnly) { 0 } else { 2 })
}

if (Is-PlaceholderUrl -BaseUrl $publicBase) {
    Write-Host "NO-GO: PublicBaseUrl looks like a placeholder/test URL. Use the real public tunnel/domain."
    exit $(if ($PrintOnly) { 0 } else { 2 })
}

$publicBaseIsEphemeral = Is-EphemeralTunnelUrl -BaseUrl $publicBase
if ($publicBaseIsEphemeral) {
    Write-Host "Temporary tunnel detected: public host must be rechecked immediately before publishing."
}

$manifestCommand = @(
    $manifestScript,
    "--public-base-url",
    $publicBase,
    "--operator-base-url",
    $operatorBase,
    "--out",
    $manifestPath
)

$prelaunchCommand = @(
    $prelaunchScript,
    "--operator-base-url",
    $operatorBase,
    "--public-base-url",
    $publicBase
)
if ($SkipServerCheck) {
    $prelaunchCommand += "--skip-server-check"
}
if ($CheckPublicHttp) {
    $prelaunchCommand += "--check-public-http"
}
$freshRehearsalLaunchArgs = ""
if ($SkipFreshRehearsalCheck) {
    $freshRehearsalLaunchArgs = " -SkipFreshRehearsalCheck"
}
elseif ($FreshRehearsalMinutes -gt 0) {
    $freshRehearsalLaunchArgs = " -FreshRehearsalMinutes $FreshRehearsalMinutes"
}
else {
    $freshRehearsalLaunchArgs = " -FreshRehearsalMinutes 0"
}

Write-Host "Launch manifest command:"
Write-Host "& `"$pythonPath`" `"$manifestScript`" --public-base-url `"$publicBase`" --operator-base-url `"$operatorBase`" --out `"$manifestPath`""
Write-Host ""
Write-Host "Experiment state status:"
Write-Host "& `"$pythonPath`" `"$experimentStateScript`" --state `"$experimentPath`" --data `"$jsonlPath`" status"
Write-Host "Experiment start command if Start test was not pressed in UI:"
Write-Host "& `"$pythonPath`" `"$experimentStateScript`" --state `"$experimentPath`" --data `"$jsonlPath`" start"
Write-Host "& `"$pythonPath`" `"$experimentStateScript`" --state `"$experimentPath`" --data `"$jsonlPath`" start --write"
Write-Host "One-command launch if ready to start the 14-day clock now:"
Write-Host "& `"$PSCommandPath`" -PublicBaseUrl `"$publicBase`" -OperatorBaseUrl `"$operatorBase`" -CheckPublicHttp$freshRehearsalLaunchArgs -StartExperiment"
Write-Host ""
Write-Host "Prelaunch GO/NO-GO command:"
$prelaunchText = "& `"$pythonPath`" `"$prelaunchScript`" --operator-base-url `"$operatorBase`" --public-base-url `"$publicBase`""
if ($SkipServerCheck) {
    $prelaunchText += " --skip-server-check"
}
if ($CheckPublicHttp) {
    $prelaunchText += " --check-public-http"
}
Write-Host $prelaunchText
Write-Host ""

if ($PrintOnly) {
    Write-Host "PrintOnly: experiment start, manifest and prelaunch not executed."
    exit 0
}

$statusRaw = & $pythonPath $experimentStateScript --state $experimentPath --data $jsonlPath status --json
if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}
$status = $statusRaw | ConvertFrom-Json
$startedAt = $status.state.startedAt
if (-not $startedAt -and $StartExperiment) {
    Write-Host "Checking launch readiness before starting the 14-day clock."
    $prestartCommand = @($prelaunchCommand + "--json")
    $prestartRaw = & $pythonPath @prestartCommand
    $prestartExitCode = $LASTEXITCODE
    try {
        $prestart = $prestartRaw | ConvertFrom-Json
    }
    catch {
        Write-Host "NO-GO: pre-start readiness check did not return valid JSON. Experiment was not started."
        Write-Host $prestartRaw
        exit $(if ($prestartExitCode) { $prestartExitCode } else { 2 })
    }

    $allowedPrestartFailures = @("experiment_started", "launch_manifest")
    $blockingFailures = @(
        $prestart.checks |
            Where-Object {
                $_.status -eq "fail" -and
                ($allowedPrestartFailures -notcontains $_.name)
            }
    )
    if ($blockingFailures.Count -gt 0) {
        Write-Host "NO-GO: pre-start readiness check found blocking failures. Experiment was not started."
        foreach ($failure in $blockingFailures) {
            Write-Host ("- {0}: {1}" -f $failure.name, $failure.detail)
        }
        exit 2
    }

    if ($publicBaseIsEphemeral -and (-not $SkipFreshRehearsalCheck) -and $FreshRehearsalMinutes -gt 0) {
        $freshRehearsal = Get-FreshRehearsalMetadata -BaseUrl $publicBase -MaxAgeMinutes $FreshRehearsalMinutes
        if (-not $freshRehearsal) {
            Write-Host "NO-GO: temporary public URL has no fresh successful day-0 rehearsal metadata. Experiment was not started."
            Write-Host "Run:"
            Write-Host "& `"$scriptDir\start-hh-booster-day0-rehearsal.ps1`" -PublicBaseUrl `"$publicBase`" -SkipBuild -WriteSmoke"
            Write-Host "Then rerun this launch helper within $FreshRehearsalMinutes minutes, or pass -SkipFreshRehearsalCheck only if you intentionally accept the risk."
            exit 2
        }
        Write-Host ("Fresh rehearsal: {0} ({1} minutes old)" -f $freshRehearsal.path, $freshRehearsal.ageMinutes)
    }

    Write-Host "Starting experiment because -StartExperiment was provided."
    & $pythonPath $experimentStateScript --state $experimentPath --data $jsonlPath start --write
    if ($LASTEXITCODE -ne 0) {
        exit $LASTEXITCODE
    }
    $statusRaw = & $pythonPath $experimentStateScript --state $experimentPath --data $jsonlPath status --json
    if ($LASTEXITCODE -ne 0) {
        exit $LASTEXITCODE
    }
    $status = $statusRaw | ConvertFrom-Json
    $startedAt = $status.state.startedAt
}

if (-not $startedAt) {
    Write-Host "NO-GO: experiment is not started. Launch manifest was not written."
    Write-Host "Press `Старт теста` in the operator UI, run the start command, or rerun this helper with -StartExperiment:"
    Write-Host "& `"$pythonPath`" `"$experimentStateScript`" --state `"$experimentPath`" --data `"$jsonlPath`" start --write"
    Write-Host "& `"$PSCommandPath`" -PublicBaseUrl `"$publicBase`" -OperatorBaseUrl `"$operatorBase`" -CheckPublicHttp$freshRehearsalLaunchArgs -StartExperiment"
    exit 2
}

& $pythonPath @manifestCommand
if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}

& $pythonPath @prelaunchCommand
exit $LASTEXITCODE
