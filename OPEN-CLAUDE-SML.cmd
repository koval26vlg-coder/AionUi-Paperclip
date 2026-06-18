@echo off
setlocal
cd /d D:\AionUi-Paperclip

set "CLAUDE_CMD=claude"
where claude >nul 2>nul
if errorlevel 1 set "CLAUDE_CMD=%APPDATA%\npm\claude.cmd"

if not exist "%CLAUDE_CMD%" if "%CLAUDE_CMD%"=="%APPDATA%\npm\claude.cmd" (
  echo Claude CLI not found in PATH.
  echo Install Claude Code or add claude.exe/claude.cmd to PATH, then run this file again.
  pause
  exit /b 1
)

"%CLAUDE_CMD%"
