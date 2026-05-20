param(
    [string]$Target = 'C:\Users\koval\bat\bitrix24-automation',
    [string]$OutDir = 'C:\Users\koval\bat\_hygiene-baseline'
)

$ErrorActionPreference = 'Stop'
Set-Location $Target

# 1. Сбор Scope_Python_Files
$rootPy = Get-ChildItem -Path $Target -Filter *.py -File -ErrorAction SilentlyContinue

$subdirPy = @()
foreach ($sub in @('bitrix','asr','ui','pipelines')) {
    $p = Join-Path $Target $sub
    if (Test-Path $p) {
        $subdirPy += Get-ChildItem -Path $p -Filter *.py -File -Recurse -ErrorAction SilentlyContinue
    }
}

$all = @($rootPy) + @($subdirPy)

# 2. Фильтр исключений
$excludePatterns = @(
    '\\__pycache__\\',
    '\\venv\\',
    '\\\.venv\\',
    '\\system--diarize\\',
    '\\reports\\',
    '\\docs\\'
)

$excludeExactRel = @(
    'pipelines\bitnewton_sync.py',
    'logging_setup.py'
)

$targetFull = (Resolve-Path $Target).Path.TrimEnd('\')

$scope = @()
foreach ($f in $all) {
    $full = $f.FullName
    $skip = $false
    foreach ($pat in $excludePatterns) {
        if ($full -match $pat) { $skip = $true; break }
    }
    if ($skip) { continue }

    # относительный путь
    $rel = $full.Substring($targetFull.Length + 1)

    if ($excludeExactRel -contains $rel) { continue }

    $scope += [pscustomobject]@{
        FullPath = $full
        RelPath  = $rel
    }
}

# Дедуп по RelPath
$scope = $scope | Sort-Object RelPath -Unique

# 3. Подсчёт print( по каждому файлу
$rows = @()
$totalPrints = 0
foreach ($item in $scope) {
    $count = (Select-String -Path $item.FullPath -Pattern '^\s*print\(' -ErrorAction SilentlyContinue | Measure-Object).Count
    $totalPrints += $count
    $rows += [pscustomobject]@{
        RelPath    = $item.RelPath
        PrintCount = $count
    }
}

# 4. Запись CSV (разделитель ;)
if (-not (Test-Path $OutDir)) {
    New-Item -ItemType Directory -Force -Path $OutDir | Out-Null
}

$csvPath = Join-Path $OutDir 'prints_baseline.csv'
$scopeTxt = Join-Path $OutDir 'scope_files.txt'

$csvLines = @('relative_path;print_count')
foreach ($r in $rows) {
    $csvLines += ('{0};{1}' -f $r.RelPath, $r.PrintCount)
}
Set-Content -Path $csvPath -Value $csvLines -Encoding UTF8

# 5. Запись списка файлов
$scopeLines = $rows | ForEach-Object { $_.RelPath }
Set-Content -Path $scopeTxt -Value $scopeLines -Encoding UTF8

# 6. Сводка
$pipelineExcluded = -not ($rows.RelPath -contains 'pipelines\bitnewton_sync.py')

Write-Host "=== BASELINE SUMMARY ==="
Write-Host ("Scope_Python_Files: {0}" -f $rows.Count)
Write-Host ("Total print( occurrences: {0}" -f $totalPrints)
Write-Host ("pipelines\bitnewton_sync.py excluded: {0}" -f $pipelineExcluded)
Write-Host ""
Write-Host "=== TOP 5 files by print( count ==="
$rows | Sort-Object PrintCount -Descending | Select-Object -First 5 | Format-Table -AutoSize
Write-Host ""
Write-Host "CSV: $csvPath"
Write-Host "List: $scopeTxt"
