param(
    [int]$LatestLogs = 5
)

$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
$packDir = Join-Path $root "docs\context-packs"
New-Item -ItemType Directory -Force -Path $packDir | Out-Null

$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
$fileStamp = Get-Date -Format "yyyy-MM-dd-HHmmss"
$latestPath = Join-Path $packDir "context-pack-latest.md"
$archivePath = Join-Path $packDir "context-pack-$fileStamp.md"

$coreFiles = @(
    "AGENTS.md",
    "docs\START-HERE.md",
    "docs\context-index.md",
    "docs\current-context.md",
    "docs\tasks.md",
    "docs\decisions.md",
    "docs\relationship-maps.md",
    "docs\agents.md",
    "docs\local-environment.md",
    "docs\memory\architecture.md",
    "docs\memory\layers\facts.md",
    "docs\memory\layers\preferences.md",
    "docs\memory\layers\timeline.md",
    "docs\memory\layers\constraints.md"
)

$builder = New-Object System.Text.StringBuilder
[void]$builder.AppendLine("# Контекстный пакет")
[void]$builder.AppendLine()
[void]$builder.AppendLine("Дата сборки: $timestamp")
[void]$builder.AppendLine()
[void]$builder.AppendLine("Этот файл предназначен для быстрого входа любого агента в общий контекст.")
[void]$builder.AppendLine()

foreach ($relative in $coreFiles) {
    $path = Join-Path $root $relative
    if (Test-Path -LiteralPath $path -PathType Leaf) {
        [void]$builder.AppendLine("---")
        [void]$builder.AppendLine()
        [void]$builder.AppendLine("## Файл: $relative")
        [void]$builder.AppendLine()
        [void]$builder.AppendLine((Get-Content -LiteralPath $path -Raw -Encoding UTF8))
        [void]$builder.AppendLine()
    }
}

$logDir = Join-Path $root "docs\agent-log"
if (Test-Path -LiteralPath $logDir -PathType Container) {
    $logs = Get-ChildItem -LiteralPath $logDir -Filter "*.md" -File |
        Where-Object { $_.Name -ne "README.md" } |
        Sort-Object LastWriteTime -Descending |
        Select-Object -First $LatestLogs

    if ($logs.Count -gt 0) {
        [void]$builder.AppendLine("---")
        [void]$builder.AppendLine()
        [void]$builder.AppendLine("## Последние записи журнала агентов")
        [void]$builder.AppendLine()

        foreach ($log in $logs) {
            $relativeLog = Resolve-Path -LiteralPath $log.FullName -Relative
            [void]$builder.AppendLine("### $relativeLog")
            [void]$builder.AppendLine()
            [void]$builder.AppendLine((Get-Content -LiteralPath $log.FullName -Raw -Encoding UTF8))
            [void]$builder.AppendLine()
        }
    }
}

$content = $builder.ToString()
Set-Content -LiteralPath $latestPath -Value $content -Encoding UTF8
Set-Content -LiteralPath $archivePath -Value $content -Encoding UTF8

Write-Output $latestPath
