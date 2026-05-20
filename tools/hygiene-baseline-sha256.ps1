$ErrorActionPreference = 'Stop'

$Target = 'C:\Users\koval\bat\bitrix24-automation'
$OutDir = 'C:\Users\koval\bat\_hygiene-baseline'
$OutFile = Join-Path $OutDir 'sha256.txt'

if (-not (Test-Path $OutDir)) {
    New-Item -ItemType Directory -Path $OutDir -Force | Out-Null
}

# 1. Pipeline_Script
$files = New-Object System.Collections.Generic.List[string]
$files.Add('pipelines\bitnewton_sync.py')

# 2. Bat_Contract — все .bat в корне
Get-ChildItem -Path $Target -Filter *.bat -File |
    Sort-Object Name |
    ForEach-Object { $files.Add($_.Name) }

# 3. 17 Python-скриптов Bat_Contract (Requirement 4.3)
$batPy = @(
    'bit_newton_asr.py',
    'bitnewton_sync_to_api.py',
    'crm_contacts.py',
    'crm_deals.py',
    'crm_leads.py',
    'crm_report.py',
    'custom_period_report.py',
    'detailed_calls_analysis.py',
    'detailed_managers_report.py',
    'managers_call_stats.py',
    'managers_call_stats_auto.py',
    'op_deals_analytics.py',
    'op_full_analytics.py',
    'op_lost_deals_analysis.py',
    'ui_audio_downloader.py',
    'web_ui.py',
    'yesterday_leads.py',
    'yesterday_leads_stats.py'
)
foreach ($p in $batPy) { $files.Add($p) }

# 4. Доп. файлы
$extra = @(
    'bitrix24_api.py',
    'bitrix\__init__.py',
    'bitrix\api.py',
    'bitrix\recordings.py',
    'bitrix\dump_one_call_debug.py',
    'asr\__init__.py',
    'asr\bitnewton.py',
    'ui\__init__.py',
    'ui\audio_downloader.py'
)
foreach ($p in $extra) { $files.Add($p) }

$lines = New-Object System.Collections.Generic.List[string]
$missing = New-Object System.Collections.Generic.List[string]
$hashedCount = 0

foreach ($rel in $files) {
    $full = Join-Path $Target $rel
    if (Test-Path -LiteralPath $full -PathType Leaf) {
        $hash = (Get-FileHash -LiteralPath $full -Algorithm SHA256).Hash
        $lines.Add("$hash  $rel")
        $hashedCount++
    } else {
        $missing.Add($rel)
    }
}

# UTF-8 без BOM
$utf8NoBom = New-Object System.Text.UTF8Encoding($false)
[System.IO.File]::WriteAllLines($OutFile, $lines, $utf8NoBom)

Write-Host "Hashed: $hashedCount"
Write-Host "Baseline: $OutFile"
if ($missing.Count -gt 0) {
    Write-Host "Missing files (skipped):"
    $missing | ForEach-Object { Write-Host "  $_" }
}
