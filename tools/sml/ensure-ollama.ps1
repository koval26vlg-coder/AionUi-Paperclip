# tools/sml/ensure-ollama.ps1
# Проверяет, что локальная служба Ollama отвечает на 127.0.0.1:11434.
# Если нет — запускает `ollama serve` в фоне. Ждёт её готовности НЕ БОЛЬШЕ
# $FastCheckSeconds секунд, чтобы не блокировать MCP-handshake клиента.
#
# Поведение:
# - Ollama уже отвечает → exit 0 (обычный путь).
# - Ollama не отвечает → запускаем `ollama serve`, ждём до 3 сек, дальше
#   возвращаем exit 0 и даём SML стартовать. Ollama докачается сама.
#   Пока она недоступна, `sml.semantic_query` будет возвращать io_error,
#   а все остальные инструменты работать в штатном режиме.
# - Ollama не установлена (путь не найден) → exit 0 с предупреждением.
#   Это единственный случай, когда семантика не поднимется без вмешательства
#   пользователя, но SML всё равно останется живым.
#
# КРИТИЧНО: вся диагностика в STDERR, чтобы не ломать MCP-stdio
# клиента (Req 1.5).

[CmdletBinding()]
param(
    [string]$OllamaExe = 'C:\Users\koval\AppData\Local\Programs\Ollama\ollama.exe',
    [int]$FastCheckSeconds = 3
)

function Write-Info {
    param([string]$Message)
    [Console]::Error.WriteLine("[ensure-ollama] $Message")
}

$endpoint = 'http://127.0.0.1:11434/api/version'

function Test-OllamaReady {
    param([string]$Url)
    try {
        $resp = Invoke-WebRequest -Uri $Url -TimeoutSec 1 -UseBasicParsing -ErrorAction Stop
        return $resp.StatusCode -eq 200
    } catch {
        return $false
    }
}

# Быстрая проверка: если Ollama уже поднята — ничего не делаем.
if (Test-OllamaReady -Url $endpoint) {
    Write-Info "already running"
    exit 0
}

# Ollama не установлена — это ручной step, но SML должен остаться живым.
if (-not (Test-Path -LiteralPath $OllamaExe)) {
    Write-Info "WARNING: Ollama не найдена по пути $OllamaExe. sml.semantic_query вернёт io_error."
    Write-Info "Установите Ollama через native installer (см. задачу 1.2 tasks.md)."
    exit 0
}

# Запускаем в фоне и ждём чуть-чуть — если успела, хорошо;
# если нет — выходим 0 и даём SML стартовать без блокировки.
Write-Info "starting ollama serve in background (soft-wait $FastCheckSeconds s)..."
$env:OLLAMA_HOST = '127.0.0.1'
try {
    Start-Process -FilePath $OllamaExe -ArgumentList 'serve' -WindowStyle Hidden | Out-Null
} catch {
    Write-Info "WARNING: не удалось запустить ollama serve: $_"
    exit 0
}

$deadline = (Get-Date).AddSeconds($FastCheckSeconds)
while ((Get-Date) -lt $deadline) {
    Start-Sleep -Milliseconds 250
    if (Test-OllamaReady -Url $endpoint) {
        Write-Info "ready"
        exit 0
    }
}

# Не успела за soft-окно — не блокируем MCP-handshake.
# SML стартует, semantic_query будет возвращать io_error, пока Ollama не готова.
Write-Info "Ollama ещё не готова (soft timeout ${FastCheckSeconds}s); SML стартует, семантика включится автоматически позже."
exit 0
