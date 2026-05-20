@echo off
setlocal

if exist "C:\Program Files\nodejs\node.exe" set "PATH=C:\Program Files\nodejs;%PATH%"

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

npm run dev
if errorlevel 1 (
  echo.
  echo [ERROR] Aion Vision не запустился. Проверьте Node.js и npm install в apps\aion-vision.
  pause
  exit /b 1
)
