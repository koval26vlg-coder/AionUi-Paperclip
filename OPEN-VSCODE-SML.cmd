@echo off
setlocal

set "WORKSPACE=D:\AionUi-Paperclip"
set "VSCODE_EXE=C:\Users\koval\AppData\Local\Programs\Microsoft VS Code\Code.exe"

if not exist "%VSCODE_EXE%" (
  echo VS Code not found:
  echo %VSCODE_EXE%
  echo Install VS Code or update OPEN-VSCODE-SML.cmd with the correct path.
  pause
  exit /b 1
)

"%VSCODE_EXE%" "%WORKSPACE%"
