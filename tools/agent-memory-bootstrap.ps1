param(
    [string]$Agent = "agent",
    [string]$Query = "",
    [int]$ContextChars = 9000,
    [switch]$NoStatus
)

$ErrorActionPreference = "Stop"

$root = "D:\AionUi-Paperclip"
$python = Join-Path $root ".venv-sml\Scripts\python.exe"
$contextPack = Join-Path $root "docs\context-packs\context-pack-latest.md"
$bootstrapDoc = Join-Path $root "docs\agent-memory-bootstrap.md"
$relationshipQuery = Join-Path $root "tools\query-relationship-map.py"
$relationshipMap = Join-Path $root "docs\relationship-maps\graphify-sml-relationship-map.json"
$statusScript = Join-Path $root "tools\status-memory-auto.ps1"

if (-not (Test-Path -LiteralPath $root -PathType Container)) {
    throw "SML memory root not found: $root"
}

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Output "# SML Memory Bootstrap"
Write-Output ""
Write-Output "Agent: $Agent"
Write-Output "Memory root: $root"
if ($Query.Trim()) {
    Write-Output "Query: $Query"
}
Write-Output ""
Write-Output "Read first:"
Write-Output "- $bootstrapDoc"
Write-Output "- $root\AGENTS.md"
Write-Output "- $contextPack"
Write-Output "- $root\docs\current-context.md"
Write-Output "- $root\docs\tasks.md"
Write-Output "- $root\docs\decisions.md"
Write-Output ""

if (-not $NoStatus -and (Test-Path -LiteralPath $statusScript -PathType Leaf)) {
    Write-Output "## Memory Automation Status"
    try {
        & $statusScript | Select-Object -First 24
    } catch {
        Write-Output "Status check failed: $($_.Exception.Message)"
    }
    Write-Output ""
}

if ($Query.Trim() -and (Test-Path -LiteralPath $relationshipQuery -PathType Leaf) -and (Test-Path -LiteralPath $relationshipMap -PathType Leaf)) {
    Write-Output "## Relationship Map Query"
    try {
        if (Test-Path -LiteralPath $python -PathType Leaf) {
            & $python -X utf8 $relationshipQuery $Query --graph $relationshipMap
        } else {
            & py -3 $relationshipQuery $Query --graph $relationshipMap
        }
    } catch {
        Write-Output "Relationship-map query failed: $($_.Exception.Message)"
    }
    Write-Output ""
}

if (Test-Path -LiteralPath $contextPack -PathType Leaf) {
    Write-Output "## Context Pack Excerpt"
    $content = Get-Content -LiteralPath $contextPack -Raw -Encoding UTF8
    if ($content.Length -gt $ContextChars) {
        Write-Output $content.Substring(0, $ContextChars)
        Write-Output ""
        Write-Output "... context pack truncated. Open full file when needed: $contextPack"
    } else {
        Write-Output $content
    }
} else {
    Write-Output "Context pack not found: $contextPack"
}
