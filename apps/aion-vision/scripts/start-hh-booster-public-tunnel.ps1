[CmdletBinding()]
param(
    [string]$HostAddress = "127.0.0.1",
    [int]$Port = 8787,
    [string]$LogPath = "",
    [switch]$PrintOnly
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$appDir = Split-Path -Parent $scriptDir
$repoRoot = Split-Path -Parent (Split-Path -Parent $appDir)

if (-not $LogPath) {
    $LogPath = Join-Path $appDir "data\hh-booster-public-tunnel.log"
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

function Test-LocalServer {
    param([string]$BaseUrl)
    try {
        $response = Invoke-WebRequest -Uri $BaseUrl -UseBasicParsing -TimeoutSec 5
        return ($response.StatusCode -eq 200)
    }
    catch {
        return $false
    }
}

$localBaseUrl = "http://${HostAddress}:$Port"
$npxPath = Resolve-Tool -Names @("npx.cmd", "npx")

Write-Host ""
Write-Host "HH Resume Booster public tunnel"
Write-Host "==============================="
Write-Host "Local URL : $localBaseUrl"
Write-Host "Log       : $LogPath"
Write-Host ""

if (-not $npxPath) {
    throw "npx not found. Install Node.js/npm or use another visible tunnel."
}

if (-not (Test-LocalServer -BaseUrl $localBaseUrl)) {
    Write-Host "NO-GO: local HH server is not reachable at $localBaseUrl"
    Write-Host "Start it first:"
    Write-Host "& `"$scriptDir\start-hh-booster-test.ps1`" -Port $Port -SkipBuild"
    exit 2
}

$commandText = "& `"$npxPath`" --yes localtunnel --port $Port --local-host $HostAddress"
Write-Host "Command:"
Write-Host $commandText
Write-Host ""
Write-Host "After localtunnel prints a public URL, use it in:"
Write-Host "& `"$scriptDir\watch-hh-booster-test.ps1`" -OperatorBaseUrl `"$localBaseUrl`" -PublicBaseUrl `"https://...`""
Write-Host "& `"$scriptDir\prepare-hh-booster-public-launch.ps1`" -PublicBaseUrl `"https://...`""
Write-Host ""

if ($PrintOnly) {
    Write-Host "PrintOnly: tunnel not started."
    exit 0
}

$logDir = Split-Path -Parent $LogPath
if ($logDir -and -not (Test-Path -LiteralPath $logDir)) {
    New-Item -ItemType Directory -Path $logDir | Out-Null
}

"[$(Get-Date -Format o)] HH Resume Booster public tunnel start: $commandText" | Tee-Object -FilePath $LogPath -Append
& $npxPath --yes localtunnel --port $Port --local-host $HostAddress 2>&1 | Tee-Object -FilePath $LogPath -Append
