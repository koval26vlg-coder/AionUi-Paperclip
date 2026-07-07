[CmdletBinding()]
param(
    [string]$BaseUrl = "http://127.0.0.1:8787",
    [string]$PublicBaseUrl = "",
    [string]$DataPath = "",
    [switch]$WriteSmoke,
    [switch]$Json
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$appDir = Split-Path -Parent $scriptDir
$repoRoot = Split-Path -Parent (Split-Path -Parent $appDir)
$distIndex = Join-Path $appDir "dist\index.html"
$pythonPath = Join-Path $repoRoot ".venv-sml\Scripts\python.exe"
$dataAdminScript = Join-Path $repoRoot "tools\hh_resume_booster_data_admin.py"

if (-not $DataPath) {
    $DataPath = Join-Path $appDir "data\hh-booster-leads.jsonl"
}

function Normalize-BaseUrl {
    param([string]$Url)
    return $Url.Trim().TrimEnd("/")
}

function Add-Check {
    param(
        [System.Collections.Generic.List[object]]$Checks,
        [string]$Name,
        [string]$Status,
        [string]$Detail
    )
    $Checks.Add([pscustomobject]@{
        name = $Name
        status = $Status
        detail = $Detail
    }) | Out-Null
}

function Is-LocalUrl {
    param([string]$Url)
    try {
        $uri = [System.Uri](Normalize-BaseUrl $Url)
        return $uri.Host -in @("127.0.0.1", "localhost", "::1")
    }
    catch {
        return $false
    }
}

function Invoke-TextGet {
    param([string]$Url)
    $response = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 10
    return @{
        StatusCode = [int]$response.StatusCode
        Content = [string]$response.Content
    }
}

function Invoke-JsonGet {
    param([string]$Url)
    return Invoke-RestMethod -Uri $Url -Method Get -TimeoutSec 10
}

function Invoke-JsonPost {
    param(
        [string]$Url,
        [object]$Payload
    )
    return Invoke-RestMethod -Uri $Url -Method Post -ContentType "application/json" -Body ($Payload | ConvertTo-Json -Depth 8) -TimeoutSec 10
}

function Test-AppShell {
    param([string]$Content)
    return $Content.Contains('id="root"') -or $Content.Contains("<title>Aion Vision</title>")
}

function Test-TunnelInterstitial {
    param([string]$Content)
    $markers = @(
        "Tunnel Password",
        "localtunnel",
        "friendly reminder",
        "To access this website, please enter the tunnel password"
    )
    foreach ($marker in $markers) {
        if ($Content.IndexOf($marker, [System.StringComparison]::OrdinalIgnoreCase) -ge 0) {
            return $true
        }
    }
    return $false
}

$base = Normalize-BaseUrl $BaseUrl
$publicBase = if ($PublicBaseUrl.Trim()) { Normalize-BaseUrl $PublicBaseUrl } else { "" }
$checks = [System.Collections.Generic.List[object]]::new()

if (Test-Path -Path $distIndex) {
    Add-Check $checks "dist" "pass" "dist/index.html exists"
}
else {
    Add-Check $checks "dist" "fail" "dist/index.html missing; run npm run build or start-hh-booster-test.ps1"
}

try {
    $root = Invoke-TextGet "$base/"
    if ($root.StatusCode -eq 200 -and (Test-AppShell $root.Content)) {
        Add-Check $checks "http_root" "pass" "$base/ returned 200"
    }
    else {
        Add-Check $checks "http_root" "warn" "$base/ returned HTTP $($root.StatusCode), but content did not look like app shell"
    }
}
catch {
    Add-Check $checks "http_root" "fail" "$base/ unavailable: $($_.Exception.Message)"
}

try {
    $leads = Invoke-JsonGet "$base/api/hh-booster/leads?limit=1"
    if ($leads.ok -eq $true -and $null -ne $leads.leads) {
        Add-Check $checks "api_leads" "pass" "GET /api/hh-booster/leads ok"
    }
    else {
        Add-Check $checks "api_leads" "fail" "GET /api/hh-booster/leads returned unexpected payload"
    }
}
catch {
    Add-Check $checks "api_leads" "fail" "GET /api/hh-booster/leads failed: $($_.Exception.Message)"
}

try {
    $experiment = Invoke-JsonGet "$base/api/hh-booster/experiment"
    if ($experiment.ok -eq $true -and $null -ne $experiment.experiment) {
        $started = if ($experiment.experiment.startedAt) { $experiment.experiment.startedAt } else { "not started" }
        Add-Check $checks "api_experiment" "pass" "GET /api/hh-booster/experiment ok, startedAt=$started"
    }
    else {
        Add-Check $checks "api_experiment" "fail" "GET /api/hh-booster/experiment returned unexpected payload"
    }
}
catch {
    Add-Check $checks "api_experiment" "fail" "GET /api/hh-booster/experiment failed: $($_.Exception.Message)"
}

if ($publicBase) {
    if (Is-LocalUrl $publicBase) {
        Add-Check $checks "public_url" "fail" "PublicBaseUrl points to localhost; do not send it to candidates"
    }
    else {
        try {
            $publicRoot = Invoke-TextGet "$publicBase/"
            if (Test-TunnelInterstitial $publicRoot.Content) {
                Add-Check $checks "public_url" "fail" "$publicBase/ returned a tunnel interstitial/password page"
            }
            elseif ($publicRoot.StatusCode -eq 200 -and (Test-AppShell $publicRoot.Content)) {
                Add-Check $checks "public_url" "pass" "$publicBase/ returned 200"
            }
            elseif ($publicRoot.StatusCode -eq 200) {
                Add-Check $checks "public_url" "warn" "$publicBase/ returned 200, but content did not look like app shell"
            }
            else {
                Add-Check $checks "public_url" "warn" "$publicBase/ returned HTTP $($publicRoot.StatusCode)"
            }
        }
        catch {
            Add-Check $checks "public_url" "fail" "$publicBase/ unavailable: $($_.Exception.Message)"
        }
    }

    try {
        $publicLeads = Invoke-JsonGet "$publicBase/api/hh-booster/leads?limit=1"
        if ($publicLeads.ok -eq $true -and $null -ne $publicLeads.leads) {
            Add-Check $checks "public_api_leads" "pass" "GET public /api/hh-booster/leads ok"
        }
        else {
            Add-Check $checks "public_api_leads" "fail" "GET public /api/hh-booster/leads returned unexpected payload"
        }
    }
    catch {
        Add-Check $checks "public_api_leads" "fail" "GET public /api/hh-booster/leads failed: $($_.Exception.Message)"
    }

    try {
        $publicExperiment = Invoke-JsonGet "$publicBase/api/hh-booster/experiment"
        if ($publicExperiment.ok -eq $true -and $null -ne $publicExperiment.experiment) {
            $publicStarted = if ($publicExperiment.experiment.startedAt) { $publicExperiment.experiment.startedAt } else { "not started" }
            Add-Check $checks "public_api_experiment" "pass" "GET public /api/hh-booster/experiment ok, startedAt=$publicStarted"
        }
        else {
            Add-Check $checks "public_api_experiment" "fail" "GET public /api/hh-booster/experiment returned unexpected payload"
        }
    }
    catch {
        Add-Check $checks "public_api_experiment" "fail" "GET public /api/hh-booster/experiment failed: $($_.Exception.Message)"
    }
}
elseif (Is-LocalUrl $base) {
    Add-Check $checks "public_url" "warn" "No PublicBaseUrl provided; local 127.0.0.1 links are not suitable for remote candidates"
}
else {
    Add-Check $checks "public_url" "pass" "BaseUrl is non-local and can be used as a public candidate URL if reachable"
}

if ($WriteSmoke) {
    $smokeId = "qa-preflight-" + [Guid]::NewGuid().ToString("N")
    $payload = [pscustomobject]@{
        id = $smokeId
        createdAt = (Get-Date).ToUniversalTime().ToString("o")
        offer = "audit"
        contact = "$smokeId@example.test"
        role = "qa preflight"
        intent = "not_now"
        channel = "preflight"
        notes = "temporary write-smoke; should be removed automatically"
        consentAccepted = $true
    }
    try {
        $post = Invoke-JsonPost "$base/api/hh-booster/leads" $payload
        if ($post.ok -eq $true) {
            Add-Check $checks "write_smoke_post" "pass" "POST /api/hh-booster/leads accepted temporary qa lead $smokeId"
            if ((Test-Path -Path $pythonPath) -and (Test-Path -Path $dataAdminScript) -and (Test-Path -Path $DataPath)) {
                & $pythonPath $dataAdminScript --data $DataPath --id $smokeId --action delete --write --json | Out-Null
                Add-Check $checks "write_smoke_cleanup" "pass" "temporary qa lead removed from local JSONL with backup"
            }
            else {
                Add-Check $checks "write_smoke_cleanup" "warn" "temporary qa lead posted, but local cleanup tool/data path was unavailable"
            }
        }
        else {
            Add-Check $checks "write_smoke_post" "fail" "POST /api/hh-booster/leads returned unexpected payload"
        }
    }
    catch {
        Add-Check $checks "write_smoke_post" "fail" "POST /api/hh-booster/leads failed: $($_.Exception.Message)"
    }
}
else {
    Add-Check $checks "write_smoke" "skip" "Not run. Add -WriteSmoke to POST a temporary qa lead and clean it up locally."
}

$failed = @($checks | Where-Object { $_.status -eq "fail" })
$warnings = @($checks | Where-Object { $_.status -eq "warn" })
$result = [pscustomobject]@{
    ok = ($failed.Count -eq 0)
    baseUrl = $base
    publicBaseUrl = if ($publicBase) { $publicBase } else { $null }
    operatorUrl = "$base/#hh-booster"
    publicFormUrl = if ($publicBase) { "$publicBase/#hh-booster-public" } else { "$base/#hh-booster-public" }
    dataPath = $DataPath
    failed = $failed.Count
    warnings = $warnings.Count
    checks = @($checks)
}

if ($Json) {
    $result | ConvertTo-Json -Depth 8
}
else {
    Write-Host ""
    Write-Host "HH Resume Booster launch preflight"
    Write-Host "=================================="
    Write-Host ("Base URL      : {0}" -f $result.baseUrl)
    Write-Host ("Operator      : {0}" -f $result.operatorUrl)
    Write-Host ("Public form   : {0}" -f $result.publicFormUrl)
    if ($result.publicBaseUrl) {
        Write-Host ("Public base   : {0}" -f $result.publicBaseUrl)
    }
    Write-Host ("Data path     : {0}" -f $result.dataPath)
    Write-Host ""
    foreach ($check in $checks) {
        Write-Host ("[{0}] {1}: {2}" -f $check.status, $check.name, $check.detail)
    }
    Write-Host ""
    if ($result.ok) {
        Write-Host "Result: ok"
    }
    else {
        Write-Host "Result: failed"
    }
}

if ($failed.Count -gt 0) {
    exit 2
}
exit 0
