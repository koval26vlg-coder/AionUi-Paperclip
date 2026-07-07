@echo off
setlocal

set "WORKSPACE=D:\AionUi-Paperclip"
set "VSCODE_EXE=C:\Users\koval\AppData\Local\Programs\Microsoft VS Code\Code.exe"

if not exist "%VSCODE_EXE%" (
  echo VS Code не найден по пути:
  echo %VSCODE_EXE%
  echo Установите VS Code или обновите OPEN-VSCODE-SML.cmd правильным путем.
  pause
  exit /b 1
)

"%VSCODE_EXE%" "%WORKSPACE%"
