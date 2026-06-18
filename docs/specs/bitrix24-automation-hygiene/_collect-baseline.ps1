$repo = 'C:\Users\koval\bat\bitrix24-automation'
$files = @(
  'pipelines\bitnewton_sync.py',
  'bit_newton_asr.py','bitnewton_sync_to_api.py','crm_contacts.py','crm_deals.py',
  'crm_leads.py','crm_report.py','custom_period_report.py','detailed_calls_analysis.py',
  'detailed_managers_report.py','managers_call_stats.py','managers_call_stats_auto.py',
  'op_deals_analytics.py','op_full_analytics.py','op_lost_deals_analysis.py',
  'ui_audio_downloader.py','web_ui.py','yesterday_leads.py','yesterday_leads_stats.py',
  'bitrix24_api.py',
  'bitrix\__init__.py','bitrix\api.py','bitrix\recordings.py','bitrix\dump_one_call_debug.py',
  'asr\__init__.py','asr\bitnewton.py',
  'ui\__init__.py','ui\audio_downloader.py'
)
$bats = Get-ChildItem -Path $repo -Filter *.bat -File -ErrorAction SilentlyContinue |
  Sort-Object Name | ForEach-Object { $_.Name }
$all = $files + $bats
$total = $all.Count
$hashed = 0
$missing = 0
$lines = foreach ($f in $all) {
  $p = Join-Path $repo $f
  if (Test-Path $p) {
    $h = (Get-FileHash -Algorithm SHA256 $p).Hash
    $hashed++
    "$h  $f"
  } else {
    $missing++
    "MISSING  $f"
  }
}
$out = 'D:\AionUi-Paperclip\.kiro\specs\bitrix24-automation-hygiene\baseline-sha256.txt'
$header = @(
  "# baseline SHA-256 для защищаемых файлов Property 5",
  "# Target_Repo: $repo",
  "# Собрано: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')",
  "# Алгоритм: SHA256 (Get-FileHash)",
  "# Всего записей: $total | Захешировано: $hashed | MISSING: $missing",
  ""
)
($header + $lines) | Set-Content -Path $out -Encoding utf8
Write-Output "TOTAL=$total HASHED=$hashed MISSING=$missing"
Write-Output "OUT=$out"
