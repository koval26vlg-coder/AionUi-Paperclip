@echo off
setlocal
cd /d D:\AionUi-Paperclip

set "CLAUDE_CMD=claude"
where claude >nul 2>nul
if errorlevel 1 set "CLAUDE_CMD=%APPDATA%\npm\claude.cmd"

if not exist "%CLAUDE_CMD%" if "%CLAUDE_CMD%"=="%APPDATA%\npm\claude.cmd" (
  echo Claude CLI not found in PATH.
  echo Install Claude Code or add claude.exe/claude.cmd to PATH first.
  pause
  exit /b 1
)

echo === Claude auth status ===
"%CLAUDE_CMD%" auth status
echo.
echo === Claude MCP list ===
"%CLAUDE_CMD%" mcp list
echo.
echo If sml is connected, ask Claude:
echo "Проверь MCP SML: вызови sml.ping и sml.startup_pack. Ответь по-русски, видишь ли ты общую память."
pause
