# tools/sml/start-sml.ps1
# Wrapper запуска SML_Core (Shared_Memory_Layer).
# Запускается MCP-клиентами Codex, Cursor и Kiro через транспорт newline-stdio.
#
# КРИТИЧНО: в stdout процесса должны идти ТОЛЬКО JSON-RPC сообщения от
# Python-сервера. Любая диагностика — только в stderr (Req 1.5).
#
# Ссылки на требования:
#   [Req 1.5]  newline-stdio транспорт MCP.
#   [Req 9.1]  UTF-8 в stdio без экранирования и транслитерации.
#   [Req 10.4] Исходящие запросы ограничены loopback-интерфейсом (127.0.0.1).
#   [Req 14.4] Локальный процесс на Windows + PowerShell 7, без облачных зависимостей.

[CmdletBinding()]
param(
    [switch]$SelfCheck
)

# ---------- Настраиваемые параметры ----------
$SmlRoot      = 'D:\AionUi-Paperclip'
$VenvPython   = Join-Path $SmlRoot '.venv-sml\Scripts\python.exe'
$Module       = 'tools.sml.mcp_adapter'
$OllamaHost   = '127.0.0.1'

# ---------- Окружение процесса ----------
# PYTHONUTF8=1    — весь Python-процесс работает в UTF-8 (Req 9.1).
# PYTHONUNBUFFERED=1 — stdin/stdout не буферизуются (Req 1.5).
# OLLAMA_HOST     — loopback-интерфейс (Req 10.4).
# PYTHONPATH      — чтобы `-m tools.sml.mcp_adapter` импортировался из корня.
$env:PYTHONUTF8       = '1'
$env:PYTHONUNBUFFERED = '1'
$env:OLLAMA_HOST      = $OllamaHost
$env:PYTHONPATH       = $SmlRoot

# ---------- Проверки перед запуском ----------
if (-not (Test-Path -LiteralPath $VenvPython)) {
    [Console]::Error.WriteLine("[sml] ERROR: интерпретатор venv не найден по пути $VenvPython. Выполните задачу 1.1 tasks.md.")
    exit 2
}

# ---------- Убедиться, что Ollama запущена ----------
$ensureScript = Join-Path $SmlRoot 'tools\sml\ensure-ollama.ps1'
if (Test-Path -LiteralPath $ensureScript) {
    # ensure-ollama пишет в stderr, stdout он не трогает.
    & $ensureScript
    if ($LASTEXITCODE -ne 0) {
        [Console]::Error.WriteLine("[sml] WARNING: ensure-ollama вернул код $LASTEXITCODE; продолжаем, но семантический поиск будет недоступен.")
    }
}

# ---------- Запуск ----------
Set-Location -LiteralPath $SmlRoot

if ($SelfCheck) {
    # --selfcheck проверяет, что TemporalStore открывается и Ollama доступна.
    # Маркер `sml-selfcheck-ok` печатается в stdout — это нормально, потому
    # что --selfcheck запускают вручную из консоли, не через MCP-клиент.
    & $VenvPython -X utf8 -m tools.sml.mcp_adapter --selfcheck
    exit $LASTEXITCODE
}

# Штатный запуск MCP-сервера. В stdout пойдут только JSON-RPC ответы.
& $VenvPython -X utf8 -m $Module @args
exit $LASTEXITCODE
