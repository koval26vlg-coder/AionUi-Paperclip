[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$Title,

    [string]$Brief,
    [string]$BriefFile,
    [string]$WorkflowRoot,
    [string]$CreatedBy = "Codex",
    [string]$Principal = "User",
    [ValidateSet("gemini-vertex", "antigravity", "grok-antigravity", "grok-gemini")]
    [string]$Profile = "grok-antigravity",

    [switch]$RiskTrading,
    [switch]$RiskWritesExternalSystem,
    [switch]$RiskLongRunning,
    [switch]$RiskUsesSecrets,
    [switch]$RiskDestructive,

    [switch]$OpenMonitor,
    [switch]$Watch,
    [int]$IntervalSeconds = 30,
    [switch]$RunNext,
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
if (-not $WorkflowRoot) {
    $WorkflowRoot = Join-Path $ProjectRoot "docs\agent-workflows"
}

$Python = Join-Path $ProjectRoot ".venv-sml\Scripts\python.exe"
$WorkflowCli = Join-Path $ProjectRoot "tools\agent_workflow.py"
$Bootstrap = Join-Path $ProjectRoot "tools\agent-memory-bootstrap.ps1"
$Monitor = Join-Path $ProjectRoot "tools\watch-agent-workflows.ps1"
$RunNextScript = Join-Path $ProjectRoot "tools\run-agent-workflow-next.ps1"

function Quote-CommandArg {
    param([AllowNull()][string]$Value)
    if ($null -eq $Value) {
        return '""'
    }
    if ($Value -match '[\s"]') {
        return '"' + ($Value -replace '"', '\"') + '"'
    }
    return $Value
}

function Format-CommandLine {
    param([string[]]$Parts)
    return (($Parts | ForEach-Object { Quote-CommandArg $_ }) -join " ")
}

function Resolve-VisiblePowerShell {
    $candidates = @()
    if ($env:WINDIR) {
        $candidates += Join-Path $env:WINDIR "System32\WindowsPowerShell\v1.0\powershell.exe"
        $candidates += Join-Path $env:WINDIR "Sysnative\WindowsPowerShell\v1.0\powershell.exe"
    }
    $command = Get-Command powershell.exe -ErrorAction SilentlyContinue
    if ($command) {
        $candidates += $command.Source
    }
    foreach ($candidate in $candidates) {
        if ($candidate -and (Test-Path -LiteralPath $candidate)) {
            return $candidate
        }
    }
    return "powershell.exe"
}

function Resolve-ModernPowerShell {
    $command = Get-Command pwsh.exe -ErrorAction SilentlyContinue
    if ($command) {
        return $command.Source
    }
    if ($PSVersionTable.PSVersion.Major -ge 6) {
        return (Join-Path $PSHOME "pwsh.exe")
    }
    return $null
}

if (-not (Test-Path -LiteralPath $Python)) {
    throw "Python runtime not found: $Python"
}
if (-not (Test-Path -LiteralPath $WorkflowCli)) {
    throw "Workflow CLI not found: $WorkflowCli"
}

if ($BriefFile) {
    if (-not (Test-Path -LiteralPath $BriefFile)) {
        throw "Brief file not found: $BriefFile"
    }
    $Brief = Get-Content -LiteralPath $BriefFile -Raw
}
if (-not $Brief) {
    $Brief = $Title
}

$riskFlags = @()
if ($RiskTrading) { $riskFlags += "--risk-trading" }
if ($RiskWritesExternalSystem) { $riskFlags += "--risk-writes_external_system" }
if ($RiskLongRunning) { $riskFlags += "--risk-long_running" }
if ($RiskUsesSecrets) { $riskFlags += "--risk-uses_secrets" }
if ($RiskDestructive) { $riskFlags += "--risk-destructive" }

$createArgs = @(
    $WorkflowCli,
    "--root", $WorkflowRoot,
    "new",
    "--title", $Title,
    "--brief", $Brief,
    "--created-by", $CreatedBy,
    "--principal", $Principal,
    "--profile", $Profile
) + $riskFlags

$createCommandForDisplay = @($Python) + $createArgs

Write-Host "Aion Agent Swarm"
Write-Host "================"
Write-Host ("Project       : {0}" -f $ProjectRoot)
Write-Host ("Workflow root : {0}" -f $WorkflowRoot)
Write-Host ("Title         : {0}" -f $Title)
Write-Host ("Created by    : {0}" -f $CreatedBy)
Write-Host ("Profile       : {0}" -f $Profile)
Write-Host ("Risk flags    : {0}" -f ($(if ($riskFlags.Count) { $riskFlags -join ", " } else { "none" })))
Write-Host ""

if (Test-Path -LiteralPath $Bootstrap) {
    Write-Host "Memory bootstrap:"
    $modernShell = Resolve-ModernPowerShell
    # Capture output before truncating it. Piping directly to Select-Object -First
    # can close stdout early and make nested Python helpers report a broken pipe.
    $bootstrapOutput = if ($modernShell -and (Test-Path -LiteralPath $modernShell)) {
        & $modernShell -NoProfile -ExecutionPolicy Bypass -File $Bootstrap -Agent $CreatedBy -Query $Title 2>&1
    } else {
        & $Bootstrap -Agent $CreatedBy -Query $Title 2>&1
    }
    $bootstrapOutput | Select-Object -First 18 | ForEach-Object { Write-Host $_ }
    Write-Host ""
}

Write-Host "Create command:"
Write-Host (Format-CommandLine $createCommandForDisplay)
Write-Host ""

if ($DryRun) {
    Write-Host "DryRun: workflow was not created."
    Write-Host ""
    Write-Host "Chat trigger examples:"
    Write-Host "  Рой: $Title"
    Write-Host "  РОЙ, $Title"
    Write-Host "  /swarm $Title"
    Write-Host "  See docs/agent-workflows/SWARM-COMMAND.md for the full trigger protocol."
    exit 0
}

$output = & $Python @createArgs 2>&1
if ($LASTEXITCODE -ne 0) {
    throw "agent_workflow.py new failed with exit code $LASTEXITCODE`n$output"
}

$workflowId = ($output | Where-Object { $_ -and $_.ToString().Trim() } | Select-Object -Last 1).ToString().Trim()
if (-not $workflowId) {
    throw "Workflow id was not returned by agent_workflow.py new."
}

Write-Host ("Workflow id   : {0}" -f $workflowId)
Write-Host ""

$statusArgs = @($WorkflowCli, "--root", $WorkflowRoot, "status", $workflowId)
& $Python @statusArgs
Write-Host ""

$statusCommand = Format-CommandLine (@($Python) + $statusArgs)
$monitorArgs = @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", $Monitor, "-Root", $WorkflowRoot)
if ($Watch) {
    $monitorArgs += "-Watch"
    $monitorArgs += "-IntervalSeconds"
    $monitorArgs += [string]$IntervalSeconds
}
$monitorCommand = Format-CommandLine (@((Resolve-VisiblePowerShell)) + $monitorArgs)
$runNextArgs = @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", $RunNextScript, "-Root", $WorkflowRoot, "-WorkflowId", $workflowId)
$runNextCommand = Format-CommandLine (@((Resolve-VisiblePowerShell)) + $runNextArgs)

Write-Host "Next commands:"
Write-Host ("  Status : {0}" -f $statusCommand)
Write-Host ("  Monitor: {0}" -f $monitorCommand)
Write-Host ("  Run L1 : {0}" -f $runNextCommand)
Write-Host ""
if ($Profile -eq "grok-antigravity" -or $Profile -eq "grok-gemini") {
    Write-Host "Next agent: Grok Build L1. Codex remains the coordinator and must keep the workflow audit trail current."
} elseif ($Profile -eq "antigravity") {
    Write-Host "Next agent: Antigravity CLI L1. Codex remains the coordinator and must keep the workflow audit trail current."
} elseif ($Profile -eq "gemini-vertex") {
    Write-Host "Next agent: Gemini Vertex L1. Codex remains the coordinator and must keep the workflow audit trail current."
}

if ($OpenMonitor) {
    $visibleShell = Resolve-VisiblePowerShell
    Start-Process -FilePath $visibleShell -ArgumentList $monitorArgs -WorkingDirectory $ProjectRoot
    Write-Host ("Opened visible monitor with {0}" -f $visibleShell)
}

if ($RunNext) {
    Write-Host ""
    Write-Host "RunNext requested: starting the first workflow step in this console."
    & (Resolve-VisiblePowerShell) @runNextArgs
}
