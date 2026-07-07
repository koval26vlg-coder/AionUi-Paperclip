[CmdletBinding()]
param(
    [string]$HostAddress = "127.0.0.1",
    [int]$Port = 8787,
    [string]$PublicBaseUrl = "",
    [switch]$SkipBuild,
    [switch]$PrintOnly
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$appDir = Split-Path -Parent $scriptDir
$repoRoot = Split-Path -Parent (Split-Path -Parent $appDir)
$serveScript = Join-Path $scriptDir "serve-sml.py"
$preflightScript = Join-Path $scriptDir "preflight-hh-booster-test.ps1"
$pythonPath = Join-Path $repoRoot ".venv-sml\Scripts\python.exe"
$metricsScript = Join-Path $repoRoot "tools\hh_resume_booster_metrics.py"
$experimentStateScript = Join-Path $repoRoot "tools\hh_resume_booster_experiment_state.py"
$outreachLogScript = Join-Path $repoRoot "tools\hh_resume_booster_outreach_log.py"
$outreachPlanScript = Join-Path $repoRoot "tools\hh_resume_booster_outreach_plan.py"
$publishKitScript = Join-Path $repoRoot "tools\hh_resume_booster_publish_kit.py"
$launchManifestScript = Join-Path $repoRoot "tools\hh_resume_booster_launch_manifest.py"
$prelaunchCheckScript = Join-Path $repoRoot "tools\hh_resume_booster_prelaunch_check.py"
$publicLaunchScript = Join-Path $scriptDir "prepare-hh-booster-public-launch.ps1"
$publicTunnelScript = Join-Path $scriptDir "start-hh-booster-public-tunnel.ps1"
$dailySnapshotScript = Join-Path $repoRoot "tools\hh_resume_booster_daily_snapshot.py"
$decisionScript = Join-Path $repoRoot "tools\hh_resume_booster_decision_report.py"
$dataAdminScript = Join-Path $repoRoot "tools\hh_resume_booster_data_admin.py"
$dataQualityScript = Join-Path $repoRoot "tools\hh_resume_booster_data_quality.py"
$conciergePacketScript = Join-Path $repoRoot "tools\hh_resume_booster_concierge_packet.py"
$followupQueueScript = Join-Path $repoRoot "tools\hh_resume_booster_followup_queue.py"
$followupStateScript = Join-Path $repoRoot "tools\hh_resume_booster_followup_state.py"
$jsonlPath = Join-Path $appDir "data\hh-booster-leads.jsonl"
$experimentPath = Join-Path $appDir "data\hh-booster-experiment.json"
$followupStatePath = Join-Path $appDir "data\hh-booster-followups.jsonl"
$outreachStatePath = Join-Path $appDir "data\hh-booster-outreach.jsonl"

function Resolve-Tool {
    param(
        [string[]]$Names,
        [string[]]$FallbackPaths = @()
    )

    foreach ($name in $Names) {
        $cmd = Get-Command $name -ErrorAction SilentlyContinue
        if ($cmd) {
            return $cmd.Source
        }
    }

    foreach ($path in $FallbackPaths) {
        if ($path -and (Test-Path -LiteralPath $path)) {
            return $path
        }
    }

    return $null
}

function Normalize-BaseUrl {
    param([string]$BaseUrl)
    return $BaseUrl.Trim().TrimEnd("/")
}

function Join-HhPath {
    param(
        [string]$BaseUrl,
        [string]$HashPath
    )
    return "$(Normalize-BaseUrl $BaseUrl)/$HashPath"
}

function Get-ChannelLink {
    param(
        [string]$BaseUrl,
        [string]$Channel
    )
    $encoded = [System.Uri]::EscapeDataString($Channel)
    return "$(Normalize-BaseUrl $BaseUrl)/#hh-booster-public?channel=$encoded"
}

function Get-OfferLink {
    param(
        [string]$BaseUrl,
        [string]$Offer
    )
    $encoded = [System.Uri]::EscapeDataString($Offer)
    return "$(Normalize-BaseUrl $BaseUrl)/#hh-booster-public?offer=$encoded"
}

function Get-OfferChannelLink {
    param(
        [string]$BaseUrl,
        [string]$Channel,
        [string]$Offer
    )
    $encodedChannel = [System.Uri]::EscapeDataString($Channel)
    $encodedOffer = [System.Uri]::EscapeDataString($Offer)
    return "$(Normalize-BaseUrl $BaseUrl)/#hh-booster-public?channel=$encodedChannel&offer=$encodedOffer"
}

if (-not (Test-Path -LiteralPath $serveScript)) {
    throw "serve-sml.py not found: $serveScript"
}

if (-not (Test-Path -LiteralPath $pythonPath)) {
    throw "Python runtime not found: $pythonPath"
}

if (-not (Test-Path -LiteralPath $metricsScript)) {
    throw "Metrics script not found: $metricsScript"
}

if (-not (Test-Path -LiteralPath $experimentStateScript)) {
    throw "Experiment state script not found: $experimentStateScript"
}

if (-not (Test-Path -LiteralPath $outreachLogScript)) {
    throw "Outreach log script not found: $outreachLogScript"
}

if (-not (Test-Path -LiteralPath $outreachPlanScript)) {
    throw "Outreach plan script not found: $outreachPlanScript"
}

if (-not (Test-Path -LiteralPath $publishKitScript)) {
    throw "Publish kit script not found: $publishKitScript"
}

if (-not (Test-Path -LiteralPath $launchManifestScript)) {
    throw "Launch manifest script not found: $launchManifestScript"
}

if (-not (Test-Path -LiteralPath $prelaunchCheckScript)) {
    throw "Prelaunch check script not found: $prelaunchCheckScript"
}

if (-not (Test-Path -LiteralPath $publicLaunchScript)) {
    throw "Public launch helper not found: $publicLaunchScript"
}

if (-not (Test-Path -LiteralPath $publicTunnelScript)) {
    throw "Public tunnel helper not found: $publicTunnelScript"
}

if (-not (Test-Path -LiteralPath $dailySnapshotScript)) {
    throw "Daily snapshot script not found: $dailySnapshotScript"
}

if (-not (Test-Path -LiteralPath $followupQueueScript)) {
    throw "Follow-up queue script not found: $followupQueueScript"
}

if (-not (Test-Path -LiteralPath $conciergePacketScript)) {
    throw "Concierge packet script not found: $conciergePacketScript"
}

if (-not (Test-Path -LiteralPath $dataQualityScript)) {
    throw "Data quality script not found: $dataQualityScript"
}

if (-not (Test-Path -LiteralPath $followupStateScript)) {
    throw "Follow-up state script not found: $followupStateScript"
}

$displayHost = if ($HostAddress -eq "0.0.0.0") { "127.0.0.1" } else { $HostAddress }
$localBaseUrl = "http://${displayHost}:$Port"
$shareBaseUrl = if ($PublicBaseUrl.Trim()) { Normalize-BaseUrl $PublicBaseUrl } else { $localBaseUrl }
$npmPath = Resolve-Tool -Names @("npm.cmd", "npm") -FallbackPaths @(
    (Join-Path $env:APPDATA "npm\npm.cmd"),
    "C:\Users\koval\bat\npm.cmd"
)

$channels = @("hh.ru", "Telegram", "VK", "Авито Работа", "Рекомендация", "Другое")
$offers = @(
    @{ Id = "avatar"; Label = "Аватарка" },
    @{ Id = "audit"; Label = "Аудит резюме" },
    @{ Id = "response"; Label = "Отклик под вакансию" }
)
$tunnelTools = @(
    @{ Name = "cloudflared"; Command = "cloudflared tunnel --url $localBaseUrl" },
    @{ Name = "ngrok"; Command = "ngrok http $localBaseUrl" },
    @{ Name = "lt"; Command = "npx localtunnel --port $Port" },
    @{ Name = "localtunnel"; Command = "npx localtunnel --port $Port" },
    @{ Name = "ssh"; Command = "ssh -R 80:${displayHost}:$Port nokey@localhost.run" }
)

Write-Host ""
Write-Host "HH Resume Booster 14-day test"
Write-Host "================================"
Write-Host "App directory : $appDir"
Write-Host "Data JSONL    : $jsonlPath"
Write-Host "Experiment    : $experimentPath"
Write-Host "Follow-ups    : $followupStatePath"
Write-Host "Outreach      : $outreachStatePath"
Write-Host "Decision gate : 14 days, 30 leads, 10 paid intent, 2 channels, 5 roles, 5 leads per offer"
Write-Host "Operator      : $(Join-HhPath $shareBaseUrl '#hh-booster')"
Write-Host "Public form   : $(Join-HhPath $shareBaseUrl '#hh-booster-public')"
Write-Host ""
Write-Host "Channel links:"
foreach ($channel in $channels) {
    Write-Host ("- {0}: {1}" -f $channel, (Get-ChannelLink $shareBaseUrl $channel))
}
Write-Host ""
Write-Host "Offer links:"
foreach ($offer in $offers) {
    Write-Host ("- {0}: {1}" -f $offer.Label, (Get-OfferLink $shareBaseUrl $offer.Id))
}
Write-Host ""
Write-Host "Offer + channel examples:"
foreach ($offer in $offers) {
    Write-Host ("- {0} / Telegram: {1}" -f $offer.Label, (Get-OfferChannelLink $shareBaseUrl "Telegram" $offer.Id))
}
Write-Host ""
Write-Host "Launch preflight after server starts:"
Write-Host "& `"$preflightScript`" -BaseUrl `"$localBaseUrl`""
if ($PublicBaseUrl.Trim()) {
    Write-Host "& `"$preflightScript`" -BaseUrl `"$localBaseUrl`" -PublicBaseUrl `"$shareBaseUrl`""
}
Write-Host "Write-smoke preflight after server starts:"
Write-Host "& `"$preflightScript`" -BaseUrl `"$localBaseUrl`" -WriteSmoke"
Write-Host ""
Write-Host "Launch manifest / freeze:"
if ($PublicBaseUrl.Trim()) {
    Write-Host "& `"$pythonPath`" `"$launchManifestScript`" --public-base-url `"$shareBaseUrl`" --out `"$appDir\data\hh-booster-launch-manifest.md`""
}
else {
    Write-Host "& `"$pythonPath`" `"$launchManifestScript`" --out `"$appDir\data\hh-booster-launch-manifest.md`""
}
Write-Host "Prelaunch GO/NO-GO after server starts, experiment is started, and manifest is saved:"
if ($PublicBaseUrl.Trim()) {
    Write-Host "& `"$pythonPath`" `"$prelaunchCheckScript`" --operator-base-url `"$localBaseUrl`" --public-base-url `"$shareBaseUrl`""
}
else {
    Write-Host "& `"$pythonPath`" `"$prelaunchCheckScript`" --operator-base-url `"$localBaseUrl`" --public-base-url `"https://PUBLIC_HOST`""
}
Write-Host "Public launch helper after you have a real tunnel/domain:"
if ($PublicBaseUrl.Trim()) {
    Write-Host "& `"$publicLaunchScript`" -PublicBaseUrl `"$shareBaseUrl`""
    Write-Host "& `"$publicLaunchScript`" -PublicBaseUrl `"$shareBaseUrl`" -CheckPublicHttp -StartExperiment"
}
else {
    Write-Host "& `"$publicLaunchScript`" -PublicBaseUrl `"https://REAL_PUBLIC_HOST`""
    Write-Host "& `"$publicLaunchScript`" -PublicBaseUrl `"https://REAL_PUBLIC_HOST`" -CheckPublicHttp -StartExperiment"
}
Write-Host "Visible localtunnel launcher if you need a temporary public URL:"
Write-Host "& `"$publicTunnelScript`" -Port $Port"
Write-Host ""
Write-Host "Daily metrics:"
Write-Host "& `"$pythonPath`" `"$metricsScript`" `"$jsonlPath`""
Write-Host "Experiment state status:"
Write-Host "& `"$pythonPath`" `"$experimentStateScript`" --state `"$experimentPath`" --data `"$jsonlPath`" status"
Write-Host "Start 14-day experiment from CLI (dry-run first, then --write):"
Write-Host "& `"$pythonPath`" `"$experimentStateScript`" --state `"$experimentPath`" --data `"$jsonlPath`" start"
Write-Host "& `"$pythonPath`" `"$experimentStateScript`" --state `"$experimentPath`" --data `"$jsonlPath`" start --write"
Write-Host "Data quality audit:"
Write-Host "& `"$pythonPath`" `"$dataQualityScript`" `"$jsonlPath`" --experiment-state `"$experimentPath`""
Write-Host "Daily outreach plan:"
if ($PublicBaseUrl.Trim()) {
    Write-Host "& `"$pythonPath`" `"$outreachPlanScript`" `"$jsonlPath`" --experiment-state `"$experimentPath`" --public-base-url `"$shareBaseUrl`""
}
else {
    Write-Host "& `"$pythonPath`" `"$outreachPlanScript`" `"$jsonlPath`" --experiment-state `"$experimentPath`""
}
Write-Host "Publish kit for links/texts:"
if ($PublicBaseUrl.Trim()) {
    Write-Host "& `"$pythonPath`" `"$publishKitScript`" --public-base-url `"$shareBaseUrl`" --operator-base-url `"$localBaseUrl`" --out `"$appDir\data\hh-booster-publish-kit.md`" --write"
}
else {
    Write-Host "& `"$pythonPath`" `"$publishKitScript`" --public-base-url `"https://REAL_PUBLIC_HOST`" --operator-base-url `"$localBaseUrl`" --out `"$appDir\data\hh-booster-publish-kit.md`" --write"
}
Write-Host "Outreach activity dry-run:"
Write-Host "& `"$pythonPath`" `"$outreachLogScript`" --state `"$outreachStatePath`" --leads `"$jsonlPath`" add --channel Telegram --type direct_message --offer response --messages-sent 10 --audience-count 10 --note `"no personal data`""
Write-Host "Outreach activity write:"
Write-Host "& `"$pythonPath`" `"$outreachLogScript`" --state `"$outreachStatePath`" --leads `"$jsonlPath`" add --channel Telegram --type direct_message --offer response --messages-sent 10 --audience-count 10 --note `"no personal data`" --write"
Write-Host "Outreach activity summary:"
Write-Host "& `"$pythonPath`" `"$outreachLogScript`" --state `"$outreachStatePath`" --leads `"$jsonlPath`" summary"
Write-Host ""
Write-Host "Concierge packet:"
Write-Host "& `"$pythonPath`" `"$conciergePacketScript`" `"$jsonlPath`""
Write-Host "Concierge packet with visible contacts:"
Write-Host "& `"$pythonPath`" `"$conciergePacketScript`" `"$jsonlPath`" --intent ready --show-contact --markdown"
Write-Host "Concierge follow-up queue:"
Write-Host "& `"$pythonPath`" `"$followupQueueScript`" `"$jsonlPath`""
Write-Host "Concierge queue with visible contacts:"
Write-Host "& `"$pythonPath`" `"$followupQueueScript`" `"$jsonlPath`" --intent ready --show-contact"
Write-Host "Mark follow-up outcome:"
Write-Host "& `"$pythonPath`" `"$followupStateScript`" --leads `"$jsonlPath`" --state `"$followupStatePath`" mark `"LEAD_ID`" --status confirmed_paid_intent --note `"short note`" --write"
Write-Host "Follow-up outcome summary:"
Write-Host "& `"$pythonPath`" `"$followupStateScript`" --leads `"$jsonlPath`" --state `"$followupStatePath`" summary"
Write-Host "Daily snapshot:"
if ($PublicBaseUrl.Trim()) {
    Write-Host "& `"$pythonPath`" `"$dailySnapshotScript`" `"$jsonlPath`" --experiment-state `"$experimentPath`" --followup-state `"$followupStatePath`" --outreach-state `"$outreachStatePath`" --public-base-url `"$shareBaseUrl`" --default-out --strict-data-quality"
}
else {
    Write-Host "& `"$pythonPath`" `"$dailySnapshotScript`" `"$jsonlPath`" --experiment-state `"$experimentPath`" --followup-state `"$followupStatePath`" --outreach-state `"$outreachStatePath`" --default-out --strict-data-quality"
}
Write-Host ""
Write-Host "Final decision report:"
Write-Host "& `"$pythonPath`" `"$decisionScript`" `"$jsonlPath`" --followup-state `"$followupStatePath`" --out `"$appDir\data\hh-booster-decision-report.md`""
Write-Host "Final report includes strict data-quality gate; warnings/errors return exit code 2."
Write-Host "Draft report before gates:"
Write-Host "& `"$pythonPath`" `"$decisionScript`" `"$jsonlPath`" --followup-state `"$followupStatePath`" --draft --out `"$appDir\data\hh-booster-decision-draft.md`""
Write-Host ""
Write-Host "Visible status:"
if ($PublicBaseUrl.Trim()) {
    Write-Host "& `"$scriptDir\watch-hh-booster-test.ps1`" -OperatorBaseUrl `"$localBaseUrl`" -PublicBaseUrl `"$shareBaseUrl`""
}
else {
    Write-Host "& `"$scriptDir\watch-hh-booster-test.ps1`""
}
Write-Host "Watch mode:"
if ($PublicBaseUrl.Trim()) {
    Write-Host "& `"$scriptDir\watch-hh-booster-test.ps1`" -OperatorBaseUrl `"$localBaseUrl`" -PublicBaseUrl `"$shareBaseUrl`" -Watch -IntervalSeconds 60"
}
else {
    Write-Host "& `"$scriptDir\watch-hh-booster-test.ps1`" -Watch -IntervalSeconds 60"
}
Write-Host ""
Write-Host "Privacy/delete dry-run:"
Write-Host "& `"$pythonPath`" `"$dataAdminScript`" --contact `"CONTACT_OR_TELEGRAM`""
Write-Host "Privacy/delete write:"
Write-Host "& `"$pythonPath`" `"$dataAdminScript`" --contact `"CONTACT_OR_TELEGRAM`" --action delete --write"
Write-Host ""

if (-not $PublicBaseUrl.Trim()) {
    Write-Host "External sharing:"
    Write-Host "- Do not publish 127.0.0.1 links to candidates."
    Write-Host "- Start a public tunnel/domain in a separate visible terminal, then rerun this script with -PublicBaseUrl."
    Write-Host "- Example: -PublicBaseUrl `"https://your-public-host.example`""
    Write-Host ""
}

Write-Host "Tunnel helpers detected on this machine:"
$detectedAnyTunnel = $false
foreach ($tool in $tunnelTools) {
    $cmd = Get-Command $tool.Name -ErrorAction SilentlyContinue
    if ($cmd) {
        $detectedAnyTunnel = $true
        Write-Host ("- {0}: {1}" -f $tool.Name, $tool.Command)
    }
}
if (-not $detectedAnyTunnel) {
    Write-Host "- none detected; use a known public domain/tunnel manually if candidates are remote."
}
Write-Host ""

if ($PrintOnly) {
    Write-Host "PrintOnly: server not started."
    exit 0
}

if (-not $SkipBuild) {
    if (-not $npmPath) {
        throw "npm not found. Install npm or ensure C:\Users\koval\bat\npm.cmd is available."
    }
    Write-Host "Building Aion Vision..."
    Push-Location $appDir
    try {
        & $npmPath run build
    }
    finally {
        Pop-Location
    }
}
else {
    Write-Host "SkipBuild: using existing dist/."
}

Write-Host ""
Write-Host "Starting visible production server. Press Ctrl+C to stop."
Write-Host "Local operator : $(Join-HhPath $localBaseUrl '#hh-booster')"
Write-Host "Local public   : $(Join-HhPath $localBaseUrl '#hh-booster-public')"
Write-Host ""

Push-Location $appDir
try {
    & $pythonPath $serveScript --host $HostAddress --port $Port
}
finally {
    Pop-Location
}
