@echo off
setlocal
chcp 65001 >nul 2>&1
rem Прод-режим Aion Vision: собрать статику и поднять постоянный HTTP-сервис
rem (живые данные + поиск по памяти работают без dev-сервера vite).

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

echo [1/2] Сборка статики (npm run build)...
call "%NPM_CMD%" run build
if errorlevel 1 (
  echo [ERROR] Сборка не удалась. Проверьте Node.js и npm install в apps\aion-vision.
  pause
  exit /b 1
)

echo [2/2] Запуск HTTP-сервиса на http://127.0.0.1:8787 ...
"%PYTHON%" -X utf8 scripts\serve-sml.py --host 127.0.0.1 --port 8787
