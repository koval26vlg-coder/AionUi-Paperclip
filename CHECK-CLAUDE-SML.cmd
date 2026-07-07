@echo off
setlocal
cd /d D:\AionUi-Paperclip

set "CLAUDE_CMD=claude"
where claude >nul 2>nul
if errorlevel 1 set "CLAUDE_CMD=%APPDATA%\npm\claude.cmd"

if not exist "%CLAUDE_CMD%" if "%CLAUDE_CMD%"=="%APPDATA%\npm\claude.cmd" (
  echo CLI Claude не найден в PATH.
  echo Установите Claude Code или сначала добавьте claude.exe/claude.cmd в PATH.
  pause
  exit /b 1
)

echo === Статус авторизации Claude ===
"%CLAUDE_CMD%" auth status
echo.
echo === Список MCP-серверов Claude ===
"%CLAUDE_CMD%" mcp list
echo.
echo Если sml подключен, спросите Claude:
echo "Проверь MCP SML: вызови sml.ping и sml.startup_pack. Ответь по-русски, видишь ли ты общую память."
pause
