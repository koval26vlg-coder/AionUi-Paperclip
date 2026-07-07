[CmdletBinding()]
param(
    [string]$DataPath = "",
    [string]$ExperimentPath = "",
    [string]$ManifestPath = "",
    [string]$OperatorBaseUrl = "http://127.0.0.1:8787",
    [string]$PublicBaseUrl = "",
    [int]$FreshRehearsalMinutes = 15,
    [int]$IntervalSeconds = 60,
    [switch]$Watch
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$appDir = Split-Path -Parent $scriptDir
$repoRoot = Split-Path -Parent (Split-Path -Parent $appDir)
$dataDir = Join-Path $appDir "data"
$pythonPath = Join-Path $repoRoot ".venv-sml\Scripts\python.exe"
$metricsScript = Join-Path $repoRoot "tools\hh_resume_booster_metrics.py"

if (-not $DataPath) {
    $DataPath = Join-Path $appDir "data\hh-booster-leads.jsonl"
}

if (-not $ExperimentPath) {
    $ExperimentPath = Join-Path $appDir "data\hh-booster-experiment.json"
}

if (-not $ManifestPath) {
    $ManifestPath = Join-Path $appDir "data\hh-booster-launch-manifest.md"
}

function Read-JsonFile {
    param([string]$Path)
    if (-not (Test-Path -Path $Path)) {
        return $null
    }
    try {
        return Get-Content -Raw -Path $Path | ConvertFrom-Json
    }
    catch {
        return $null
    }
}

function Format-Bool {
    param([bool]$Value)
    if ($Value) { return "yes" }
    return "no"
}

function Value-Or {
    param(
        $Value,
        $Fallback
    )
    if ($null -eq $Value) {
        return $Fallback
    }
    return $Value
}

function Get-NonEmptyLineCount {
    param([string]$Path)
    if (-not (Test-Path -Path $Path)) {
        return 0
    }
    return @(
        Get-Content -Path $Path | Where-Object { $_.Trim() }
    ).Count
}

function Normalize-BaseUrl {
    param([string]$BaseUrl)
    return $BaseUrl.Trim().TrimEnd("/")
}

function Is-LocalUrl {
    param([string]$BaseUrl)
    if (-not $BaseUrl.Trim()) {
        return $true
    }
    $lowered = $BaseUrl.ToLowerInvariant()
    return ($lowered -match "127\.0\.0\.1" -or $lowered -match "localhost" -or $lowered -match "\[::1\]")
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

function Test-JsonEndpoint {
    param(
        [string]$Url,
        [string]$Label
    )
    if (-not $Url.Trim()) {
        return [pscustomobject]@{
            ready = $false
            detail = "$Label missing"
        }
    }
    try {
        $response = Invoke-WebRequest -UseBasicParsing -Uri $Url -TimeoutSec 5
        if ($response.StatusCode -eq 200) {
            try {
                $null = $response.Content | ConvertFrom-Json
                return [pscustomobject]@{
                    ready = $true
                    detail = "HTTP 200 JSON"
                }
            }
            catch {
                return [pscustomobject]@{
                    ready = $false
                    detail = "HTTP 200 but invalid JSON"
                }
            }
        }
        return [pscustomobject]@{
            ready = $false
            detail = "HTTP $($response.StatusCode)"
        }
    }
    catch {
        return [pscustomobject]@{
            ready = $false
            detail = $_.Exception.Message
        }
    }
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

    if (-not $BaseUrl.Trim() -or -not (Test-Path -Path $dataDir)) {
        return $null
    }

    $normalizedBase = Normalize-BaseUrl $BaseUrl
    $nowUtc = (Get-Date).ToUniversalTime()
    $files = Get-ChildItem -Path $dataDir -Filter "hh-booster-day0-rehearsal-*.json" -ErrorAction SilentlyContinue |
        Sort-Object LastWriteTime -Descending

    foreach ($file in $files) {
        $record = Read-JsonFile -Path $file.FullName
        if ($null -eq $record) {
            continue
        }
        if ((Normalize-BaseUrl ([string]$record.publicBaseUrl)) -ne $normalizedBase) {
            continue
        }

        $blockingCount = 0
        if ($record.blockingFailures) {
            $blockingCount = @($record.blockingFailures).Count
        }

        $generatedAtUtc = Convert-RehearsalTimestampUtc -Value $record.generatedAt -Fallback $file.LastWriteTime
        $ageMinutes = ($nowUtc - $generatedAtUtc).TotalMinutes
        $expiresInMinutes = $MaxAgeMinutes - $ageMinutes
        $staleAtLocal = $generatedAtUtc.AddMinutes($MaxAgeMinutes).ToLocalTime()
        $ready = (
            $record.status -eq "ready_for_launch" -and
            $blockingCount -eq 0 -and
            $ageMinutes -le $MaxAgeMinutes
        )

        return [pscustomobject]@{
            path = $file.FullName
            status = $record.status
            reason = $record.reason
            ageMinutes = [math]::Round($ageMinutes, 2)
            expiresInMinutes = [math]::Round($expiresInMinutes, 2)
            staleAt = $staleAtLocal.ToString("yyyy-MM-dd HH:mm:ss")
            blockingFailures = $blockingCount
            ready = $ready
        }
    }

    return $null
}

function Render-Status {
    $now = Get-Date
    $experimentExists = Test-Path -Path $ExperimentPath
    $dataExists = Test-Path -Path $DataPath
    $manifestExists = Test-Path -Path $ManifestPath
    $operatorBase = Normalize-BaseUrl $OperatorBaseUrl
    $publicBase = Normalize-BaseUrl $PublicBaseUrl
    $publicShapeReady = $publicBase -and -not (Is-LocalUrl -BaseUrl $publicBase) -and -not (Is-PlaceholderUrl -BaseUrl $publicBase)
    $publicApiCheck = if ($publicShapeReady) {
        Test-JsonEndpoint -Url "$publicBase/api/hh-booster/experiment" -Label "public experiment API"
    }
    else {
        [pscustomobject]@{
            ready = $false
            detail = if ($publicBase) { "local/placeholder public URL" } else { "missing public URL" }
        }
    }
    $publicReady = [bool]($publicShapeReady -and $publicApiCheck.ready)
    $publicIsEphemeral = Is-EphemeralTunnelUrl -BaseUrl $publicBase
    $freshRehearsal = Get-FreshRehearsalMetadata -BaseUrl $publicBase -MaxAgeMinutes $FreshRehearsalMinutes
    $experiment = Read-JsonFile -Path $ExperimentPath

    Write-Host ""
    Write-Host "HH Resume Booster test status"
    Write-Host "============================="
    Write-Host ("Now        : {0}" -f $now.ToString("yyyy-MM-dd HH:mm:ss"))
    Write-Host ("Data       : {0}" -f $DataPath)
    Write-Host ("Experiment : {0}" -f $ExperimentPath)
    Write-Host ("Manifest   : {0}" -f $ManifestPath)
    Write-Host ("Operator   : {0}/#hh-booster" -f $operatorBase)
    Write-Host ("Public     : {0}" -f $(if ($publicBase) { "$publicBase/#hh-booster-public" } else { "n/a" }))
    Write-Host ""

    if ($experimentExists -and $null -ne $experiment) {
        Write-Host ("Started    : {0}" -f (Value-Or $experiment.startedAt "n/a"))
        Write-Host ("Duration   : {0} days" -f (Value-Or $experiment.durationDays "n/a"))
        Write-Host ("Targets    : leads={0}, paid={1}, channels={2}, roles={3}" -f `
            (Value-Or $experiment.targetLeads "n/a"), `
            (Value-Or $experiment.targetPaidIntent "n/a"), `
            (Value-Or $experiment.targetChannels "n/a"), `
            (Value-Or $experiment.targetRoles "n/a"))
    }
    elseif ($experimentExists) {
        Write-Host "Started    : unreadable experiment file"
    }
    else {
        Write-Host "Started    : n/a - click Start test in #hh-booster first"
    }

    $experimentStarted = $false
    if ($experimentExists -and $null -ne $experiment) {
        $experimentStarted = -not [string]::IsNullOrWhiteSpace([string]$experiment.startedAt)
    }

    if ($dataExists) {
        $item = Get-Item -Path $DataPath
        Write-Host ("JSONL      : exists, bytes={0}, lines={1}, last_write={2}" -f `
            $item.Length, `
            (Get-NonEmptyLineCount -Path $DataPath), `
            $item.LastWriteTime.ToString("yyyy-MM-dd HH:mm:ss"))
    }
    else {
        Write-Host "JSONL      : missing - no server leads yet"
    }

    Write-Host ""
    Write-Host "Launch checklist"
    Write-Host "----------------"
    Write-Host ("Public URL : {0}" -f $(if ($publicReady) { "ready" } elseif ($publicBase) { "not ready" } else { "missing" }))
    if ($publicBase) {
        Write-Host ("Public API : {0}" -f $publicApiCheck.detail)
    }
    if ($publicIsEphemeral) {
        if ($freshRehearsal -and $freshRehearsal.ready) {
            Write-Host ("Rehearsal  : fresh, age={0} min, expires_in={1} min, stale_at={2}, {3}" -f `
                $freshRehearsal.ageMinutes, `
                $freshRehearsal.expiresInMinutes, `
                $freshRehearsal.staleAt, `
                $freshRehearsal.path)
        }
        elseif ($freshRehearsal) {
            $expiredBy = [math]::Round([math]::Max(0, -1 * [double]$freshRehearsal.expiresInMinutes), 2)
            Write-Host ("Rehearsal  : stale/not ready, age={0} min, expired_by={1} min, status={2}, blockers={3}, {4}" -f `
                $freshRehearsal.ageMinutes, `
                $expiredBy, `
                $freshRehearsal.status, `
                $freshRehearsal.blockingFailures, `
                $freshRehearsal.path)
        }
        else {
            Write-Host "Rehearsal  : missing for this temporary public URL"
        }
    }
    elseif ($publicReady) {
        Write-Host "Rehearsal  : not required for stable public URL"
    }
    Write-Host ("Manifest   : {0}" -f $(if ($manifestExists) { "exists" } else { "missing" }))
    Write-Host ("Started    : {0}" -f $(if ($experimentStarted) { "yes" } else { "no" }))
    Write-Host ("Prelaunch  : run after server is visible, public URL is real, Start test is pressed, and manifest exists")
    $freshReady = (-not $publicIsEphemeral) -or ($freshRehearsal -and $freshRehearsal.ready)
    $launchReady = $dataExists -and $publicReady -and $freshReady -and (-not $experimentStarted)
    $launchReadyReason = if ($launchReady) {
        "ready for guarded launch command"
    }
    elseif ($experimentStarted) {
        "already started"
    }
    elseif (-not $dataExists) {
        "server leads JSONL missing"
    }
    elseif (-not $publicReady) {
        "public API not ready"
    }
    elseif (-not $freshReady) {
        "fresh rehearsal missing or stale"
    }
    else {
        "not ready"
    }
    Write-Host ("Launch ready: {0} ({1})" -f $(if ($launchReady) { "yes" } else { "no" }), $launchReadyReason)

    if (-not $dataExists) {
        Write-Host ""
        Write-Host "Next action: start production server visibly; do not publish candidate links yet."
        return
    }

    if (-not $experimentStarted) {
        Write-Host ""
        if ($publicIsEphemeral -and (-not ($freshRehearsal -and $freshRehearsal.ready))) {
            Write-Host "Next action: rerun day-0 rehearsal with write-smoke for this temporary public URL before Start test."
            if ($publicBase) {
                Write-Host "& `"$scriptDir\start-hh-booster-day0-rehearsal.ps1`" -PublicBaseUrl `"$publicBase`" -SkipBuild -WriteSmoke"
            }
        }
        else {
            Write-Host "Next action: guarded launch can start the 14-day clock, save manifest, and run prelaunch."
            Write-Host "& `"$scriptDir\prepare-hh-booster-public-launch.ps1`" -PublicBaseUrl `"$publicBase`" -OperatorBaseUrl `"$operatorBase`" -CheckPublicHttp -FreshRehearsalMinutes $FreshRehearsalMinutes -StartExperiment"
        }
        return
    }

    if (-not $publicReady) {
        Write-Host ""
        Write-Host "Next action: create a real public HTTPS tunnel/domain and rerun this monitor with -PublicBaseUrl."
        return
    }

    if (-not $manifestExists) {
        Write-Host ""
        Write-Host "Next action: save launch manifest, then run prelaunch GO/NO-GO before sharing candidate links."
        return
    }

    if (-not (Test-Path -Path $pythonPath)) {
        Write-Host ""
        Write-Host ("ERROR: Python runtime not found: {0}" -f $pythonPath)
        return
    }

    if (-not (Test-Path -Path $metricsScript)) {
        Write-Host ""
        Write-Host ("ERROR: metrics script not found: {0}" -f $metricsScript)
        return
    }

    $args = @($metricsScript, $DataPath, "--json")
    if ($experimentExists) {
        $args += @("--experiment-state", $ExperimentPath)
    }

    try {
        $metricsJson = & $pythonPath @args
        $metrics = $metricsJson | ConvertFrom-Json
    }
    catch {
        Write-Host ""
        Write-Host ("ERROR: metrics failed: {0}" -f $_.Exception.Message)
        return
    }

    Write-Host ""
    Write-Host "Gate"
    Write-Host "----"
    Write-Host ("Leads      : {0}/{1}" -f $metrics.total_leads, $metrics.experiment.target_leads)
    Write-Host ("Paid       : {0}/{1}" -f $metrics.total_paid_intent, $metrics.experiment.target_paid_intent)
    Write-Host ("Channels   : {0}/{1}" -f $metrics.unique_channels, $metrics.experiment.target_channels)
    Write-Host ("Roles      : {0}/{1}" -f $metrics.unique_roles, $metrics.experiment.target_roles)
    Write-Host ("Offer min  : {0}" -f $metrics.experiment.target_min_leads_per_offer)
    Write-Host ("Coverage   : {0}" -f (Format-Bool -Value ([bool]$metrics.offer_coverage_ready)))
    Write-Host ("Day        : {0}/{1}" -f $metrics.experiment.elapsed_days, $metrics.experiment.duration_days)
    Write-Host ("Complete   : {0}" -f (Format-Bool -Value ([bool]$metrics.experiment.days_complete)))
    Write-Host ("Ready      : {0}" -f (Format-Bool -Value ([bool]$metrics.decision_ready)))

    Write-Host ""
    Write-Host "Pace"
    Write-Host "----"
    Write-Host ("Average    : leads/day={0}, paid/day={1}" -f `
        $metrics.daily.average_leads_per_active_day, `
        $metrics.daily.average_paid_per_active_day)
    Write-Host ("Need/day   : leads={0}, paid={1}" -f `
        $metrics.daily.required_leads_per_remaining_day, `
        $metrics.daily.required_paid_per_remaining_day)

    Write-Host ""
    Write-Host "By offer"
    Write-Host "--------"
    foreach ($offer in $metrics.by_offer) {
        Write-Host ("- {0}: leads={1}, paid={2}, rate={3}%" -f `
            $offer.label, `
            $offer.leads, `
            $offer.paid_intent, `
            $offer.paid_intent_rate)
    }
    Write-Host ("Winner     : {0}" -f $metrics.winner.label)

    Write-Host ""
    Write-Host "Offer coverage"
    Write-Host "--------------"
    foreach ($coverage in $metrics.offer_coverage) {
        Write-Host ("- {0}: leads={1}/{2}, ready={3}" -f `
            $coverage.label, `
            $coverage.leads, `
            $coverage.target, `
            (Format-Bool -Value ([bool]$coverage.ready)))
    }

    Write-Host ""
    Write-Host "Recent days"
    Write-Host "-----------"
    $dailyRows = @($metrics.daily.by_day)
    if ($dailyRows.Count -gt 0) {
        $dailyRows | Select-Object -First 5 | ForEach-Object {
            Write-Host ("- {0}: leads={1}, paid={2}, avatar={3}, audit={4}, response={5}" -f `
                $_.date, $_.leads, $_.paid_intent, $_.avatar, $_.audit, $_.response)
        }
    }
    else {
        Write-Host "- n/a"
    }

    Write-Host ""
    if ($metrics.decision_ready) {
        Write-Host "Next action: export/freeze data and compare paid intent by offer."
    }
    elseif (-not $metrics.experiment.days_complete) {
        Write-Host "Next action: continue collection until the 14-day window is complete."
    }
    else {
        Write-Host "Next action: continue collection until all gates are met, or revise the offer/channel after review."
    }
}

do {
    if ($Watch) {
        Clear-Host
    }
    Render-Status
    if ($Watch) {
        Start-Sleep -Seconds ([Math]::Max(5, $IntervalSeconds))
    }
} while ($Watch)
