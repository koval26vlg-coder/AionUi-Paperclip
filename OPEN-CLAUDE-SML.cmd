@echo off
setlocal
cd /d D:\AionUi-Paperclip

set "CLAUDE_CMD=claude"
where claude >nul 2>nul
if errorlevel 1 set "CLAUDE_CMD=%APPDATA%\npm\claude.cmd"

if not exist "%CLAUDE_CMD%" if "%CLAUDE_CMD%"=="%APPDATA%\npm\claude.cmd" (
  echo CLI Claude не найден в PATH.
  echo Установите Claude Code или добавьте claude.exe/claude.cmd в PATH, затем запустите этот файл снова.
  pause
  exit /b 1
)

"%CLAUDE_CMD%"
