@echo off
setlocal
chcp 65001 >nul 2>&1
"%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe" -NoProfile -ExecutionPolicy Bypass -File "D:\AionUi-Paperclip\tools\agent-memory-bootstrap.ps1" -Agent "manual" -Query "%*"
