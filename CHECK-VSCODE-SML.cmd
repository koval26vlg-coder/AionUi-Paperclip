@echo off
setlocal

set "WORKSPACE=D:\AionUi-Paperclip"
set "VSCODE_EXE=C:\Users\koval\AppData\Local\Programs\Microsoft VS Code\Code.exe"
set "CLAUDE_CMD=%APPDATA%\npm\claude.cmd"

echo === VS Code ===
if exist "%VSCODE_EXE%" (
  echo Найден: %VSCODE_EXE%
  "%VSCODE_EXE%" --version
) else (
  echo Отсутствует: %VSCODE_EXE%
)

echo.
echo === Рабочая область ===
if exist "%WORKSPACE%\AGENTS.md" echo Найден AGENTS.md
if exist "%WORKSPACE%\CLAUDE.md" echo Найден CLAUDE.md
if exist "%WORKSPACE%\.mcp.json" echo Найден .mcp.json
if exist "%WORKSPACE%\.vscode\tasks.json" echo Найден .vscode\tasks.json
if exist "%WORKSPACE%\docs\context-packs\context-pack-latest.md" echo Найден context-pack-latest.md
if exist "%WORKSPACE%\docs\relationship-maps\graphify-sml-relationship-map.json" echo Найден JSON карты связей

echo.
echo === Статус автонаблюдателя памяти ===
"C:\Program Files\PowerShell\7\pwsh.exe" -NoProfile -ExecutionPolicy Bypass -File "%WORKSPACE%\tools\status-memory-auto.ps1"

echo.
echo === Claude MCP, если доступен ===
if exist "%CLAUDE_CMD%" (
  "%CLAUDE_CMD%" mcp list
) else (
  echo CLI Claude не найден по пути %CLAUDE_CMD%
)

pause
