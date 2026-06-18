@echo off
setlocal
chcp 65001 >nul 2>&1

if exist "C:\Program Files\nodejs\node.exe" set "PATH=C:\Program Files\nodejs;%PATH%"
set "NPM_CMD=npm.cmd"
if exist "C:\Program Files\nodejs\npm.cmd" set "NPM_CMD=C:\Program Files\nodejs\npm.cmd"

cd /d "%~dp0apps\aion-vision"
if errorlevel 1 (
  echo [ERROR] Не удалось перейти в папку apps\aion-vision.
  pause
  exit /b 1
)

set "PYTHON=%~dp0.venv-sml\Scripts\python.exe"
if not exist "%PYTHON%" set "PYTHON=python"

"%PYTHON%" scripts\export-sml-dashboard.py --out public\aion-data.json
if errorlevel 1 (
  echo.
  echo [WARN] Не удалось обновить snapshot SML. Веб-интерфейс попробует live API.
)

call "%NPM_CMD%" run dev
if errorlevel 1 (
  echo.
  echo [ERROR] Aion Vision не запустился. Проверьте Node.js и npm install в apps\aion-vision.
  pause
  exit /b 1
)
