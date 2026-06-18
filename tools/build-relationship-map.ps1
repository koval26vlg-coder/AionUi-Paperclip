param(
    [string]$Topic = "Graphify SML Codex Gemini карты связей",
    [int]$MaxLogs = 12,
    [int]$MaxSmlRecords = 90,
    [int]$MaxCodeFiles = 160,
    [switch]$Quiet
)

$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
$skillScript = Join-Path $env:USERPROFILE ".codex\skills\relationship-map-builder\scripts\build_relationship_map.py"
$python = Join-Path $root ".venv-sml\Scripts\python.exe"
$outDir = Join-Path $root "docs\relationship-maps"
$markdownOut = Join-Path $outDir "graphify-sml-relationship-map.md"
$jsonOut = Join-Path $outDir "graphify-sml-relationship-map.json"

if (-not (Test-Path -LiteralPath $skillScript -PathType Leaf)) {
    throw "Relationship map builder not found: $skillScript"
}

if (-not (Test-Path -LiteralPath $python -PathType Leaf)) {
    $python = Join-Path $env:SystemRoot "py.exe"
}

New-Item -ItemType Directory -Force -Path $outDir | Out-Null

& $python $skillScript `
    --root $root `
    --topic $Topic `
    --out $markdownOut `
    --json-out $jsonOut `
    --include-all-docs `
    --include-recent-sml `
    --max-logs $MaxLogs `
    --max-sml-records $MaxSmlRecords `
    --max-code-files $MaxCodeFiles | ForEach-Object {
        if (-not $Quiet) {
            Write-Output $_
        }
    }

if (-not (Test-Path -LiteralPath $markdownOut -PathType Leaf)) {
    throw "Relationship map markdown was not created: $markdownOut"
}

if (-not (Test-Path -LiteralPath $jsonOut -PathType Leaf)) {
    throw "Relationship map JSON was not created: $jsonOut"
}

if (-not $Quiet) {
    Write-Output $markdownOut
    Write-Output $jsonOut
}
