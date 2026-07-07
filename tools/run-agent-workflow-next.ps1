[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$WorkflowId,

    [string]$Root,
    [string]$Executor = "Codex",
    [int]$TimeoutSeconds = 390,
    [string]$Task
)

$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
if (-not $Root) {
    $Root = Join-Path $ProjectRoot "docs\agent-workflows"
}

$Python = Join-Path $ProjectRoot ".venv-sml\Scripts\python.exe"
$WorkflowCli = Join-Path $ProjectRoot "tools\agent_workflow.py"
$GrokRunner = Join-Path $ProjectRoot "tools\grok_build_workflow_review.py"
$AntigravityRunner = Join-Path $ProjectRoot "tools\antigravity_workflow_review.py"
$GeminiRunner = Join-Path $ProjectRoot "tools\gemini_vertex_workflow_review.py"

function Invoke-PythonStep {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Label,

        [Parameter(Mandatory = $true)]
        [string[]]$Arguments
    )

    Write-Host ""
    Write-Host ("==> {0}" -f $Label)
    $output = & $Python @Arguments 2>&1
    $exitCode = $LASTEXITCODE
    if ($output) {
        $output | ForEach-Object { Write-Host $_ }
    }
    if ($exitCode -ne 0) {
        throw "$Label failed with exit code $exitCode"
    }
}

function Get-Contract {
    $path = Join-Path (Join-Path $Root $WorkflowId) "contract.json"
    if (-not (Test-Path -LiteralPath $path)) {
        throw "Workflow contract not found: $path"
    }
    return Get-Content -LiteralPath $path -Raw | ConvertFrom-Json
}

function Get-LevelValue {
    param(
        [Parameter(Mandatory = $true)]
        [object]$Contract,

        [Parameter(Mandatory = $true)]
        [string]$Level
    )

    $prop = $Contract.levels.PSObject.Properties[$Level]
    if (-not $prop) {
        throw "Level not found in contract: $Level"
    }
    return $prop.Value
}

function Get-CurrentAssignmentStatus {
    param([Parameter(Mandatory = $true)][object]$Contract)

    $level = Get-LevelValue -Contract $Contract -Level $Contract.current_level
    if ($Contract.current_subrole) {
        foreach ($subrole in @($level.subroles)) {
            if ($subrole.id -eq $Contract.current_subrole) {
                return [string]$subrole.status
            }
        }
        throw "Current subrole not found: $($Contract.current_subrole)"
    }
    return [string]$level.status
}

function Get-RunnerForAgent {
    param([Parameter(Mandatory = $true)][string]$Agent)

    switch ($Agent) {
        "Grok Build" {
            if (-not (Test-Path -LiteralPath $GrokRunner)) { throw "Grok runner not found: $GrokRunner" }
            return $GrokRunner
        }
        "Antigravity CLI" {
            if (-not (Test-Path -LiteralPath $AntigravityRunner)) { throw "Antigravity runner not found: $AntigravityRunner" }
            return $AntigravityRunner
        }
        "Gemini Vertex" {
            if (-not (Test-Path -LiteralPath $GeminiRunner)) { throw "Gemini Vertex runner not found: $GeminiRunner" }
            return $GeminiRunner
        }
        default {
            return $null
        }
    }
}

function Get-HandoffDecision {
    param([Parameter(Mandatory = $true)][string]$Path)

    $text = Get-Content -LiteralPath $Path -Raw
    $match = [regex]::Match(
        $text,
        '(?ims)^##\s*Решение\s*\r?\n\s*(approve|revise|escalate|block)\b'
    )
    if ($match.Success) {
        return $match.Groups[1].Value.ToLowerInvariant()
    }
    $fallback = [regex]::Match($text, '(?i)\b(approve|revise|escalate|block)\b')
    if ($fallback.Success) {
        return $fallback.Groups[1].Value.ToLowerInvariant()
    }
    return "approve"
}

function Get-SafeName {
    param([Parameter(Mandatory = $true)][string]$Value)
    return ($Value -replace '[^A-Za-z0-9_-]+', '-').Trim('-').ToLowerInvariant()
}

if (-not (Test-Path -LiteralPath $Python)) {
    throw "Python runtime not found: $Python"
}
if (-not (Test-Path -LiteralPath $WorkflowCli)) {
    throw "Workflow CLI not found: $WorkflowCli"
}

$contract = Get-Contract
$agent = @($contract.allowed_next_agents)[0]
if (-not $agent) {
    throw "No allowed_next_agents in workflow; nothing to run."
}

$state = [string]$contract.state
$level = [string]$contract.current_level
$subrole = [string]$contract.current_subrole
$assignment = if ($subrole) { $subrole } else { $level }
$wfDir = Join-Path $Root $WorkflowId
$safeAgent = Get-SafeName $agent

Write-Host "Aion Agent Workflow Next"
Write-Host "========================"
Write-Host ("Workflow : {0}" -f $WorkflowId)
Write-Host ("Root     : {0}" -f $Root)
Write-Host ("State    : {0}" -f $state)
Write-Host ("Current  : {0}" -f $assignment)
Write-Host ("Agent    : {0}" -f $agent)

$runner = Get-RunnerForAgent $agent
if (-not $runner) {
    Write-Host ""
    Write-Host ("Agent {0} has no isolated CLI runner here." -f $agent)
    Write-Host "This is expected for Codex/Claude levels: continue in the agent chat, then submit the handoff through agent_workflow.py."
    exit 0
}

if ($state -eq "waiting_for_approval") {
    $reviewTask = if ($Task) {
        $Task
    } else {
        "Проверь submitted handoff текущего уровня $assignment. Учитывай brief.md, contract.json, events.jsonl и последний handoff. Если работа годится для передачи дальше, решение approve. Если нужно вернуть на доработку, решение revise и явно укажи причину."
    }
    $out = Join-Path $wfDir ("tmp-{0}-{1}-approval-review.md" -f (Get-SafeName $assignment), $safeAgent)
    Invoke-PythonStep -Label ("Run review-only {0} approval check" -f $agent) -Arguments @(
        $runner,
        $WorkflowId,
        "--root", $Root,
        "--task", $reviewTask,
        "--out", $out,
        "--timeout", [string]$TimeoutSeconds
    )
    $decision = Get-HandoffDecision $out
    Write-Host ""
    Write-Host ("Decision: {0}" -f $decision)
    if ($decision -eq "approve" -or $decision -eq "escalate") {
        Invoke-PythonStep -Label ("Approve {0} as {1}" -f $assignment, $agent) -Arguments @(
            $WorkflowCli,
            "--root", $Root,
            "approve-level",
            $WorkflowId,
            "--agent", $agent,
            "--executor", $Executor
        )
    } else {
        Invoke-PythonStep -Label ("Request revision for {0} as {1}" -f $assignment, $agent) -Arguments @(
            $WorkflowCli,
            "--root", $Root,
            "request-revision",
            $WorkflowId,
            "--agent", $agent,
            "--executor", $Executor,
            "--reason", ("Reviewer decision: {0}" -f $decision),
            "--disagreement-file", $out
        )
    }
} else {
    $status = Get-CurrentAssignmentStatus $contract
    if ($status -eq "pending" -or $status -eq "") {
        Invoke-PythonStep -Label ("Claim {0} as {1}" -f $assignment, $agent) -Arguments @(
            $WorkflowCli,
            "--root", $Root,
            "claim",
            $WorkflowId,
            "--agent", $agent,
            "--executor", $Executor
        )
    } elseif ($status -ne "in_progress") {
        throw "Current assignment status must be pending or in_progress before work; got '$status'."
    }

    $workTask = if ($Task) {
        $Task
    } else {
        "Выполни текущий уровень $assignment как $agent. Используй brief.md, contract.json, events.jsonl и последний handoff. Верни чистый handoff со стандартными разделами и решением approve/revise/escalate/block."
    }
    $out = Join-Path $wfDir ("tmp-{0}-{1}-handoff.md" -f (Get-SafeName $assignment), $safeAgent)
    Invoke-PythonStep -Label ("Run review-only {0} work" -f $agent) -Arguments @(
        $runner,
        $WorkflowId,
        "--root", $Root,
        "--task", $workTask,
        "--out", $out,
        "--timeout", [string]$TimeoutSeconds
    )
    Invoke-PythonStep -Label ("Submit {0} as {1}" -f $assignment, $agent) -Arguments @(
        $WorkflowCli,
        "--root", $Root,
        "submit-work",
        $WorkflowId,
        "--agent", $agent,
        "--executor", $Executor,
        "--handoff-file", $out
    )
}

Write-Host ""
Invoke-PythonStep -Label "Workflow status" -Arguments @(
    $WorkflowCli,
    "--root", $Root,
    "status",
    $WorkflowId
)
