@echo off
setlocal

set "WORKSPACE=D:\AionUi-Paperclip"
set "VSCODE_EXE=C:\Users\koval\AppData\Local\Programs\Microsoft VS Code\Code.exe"
set "CLAUDE_CMD=%APPDATA%\npm\claude.cmd"
set "MIMO_CMD=%APPDATA%\npm\mimo.cmd"

echo === VS Code ===
if exist "%VSCODE_EXE%" (
  echo Found: %VSCODE_EXE%
  "%VSCODE_EXE%" --version
) else (
  echo Missing: %VSCODE_EXE%
)

echo.
echo === Workspace ===
if exist "%WORKSPACE%\AGENTS.md" echo Found AGENTS.md
if exist "%WORKSPACE%\CLAUDE.md" echo Found CLAUDE.md
if exist "%WORKSPACE%\.mcp.json" echo Found .mcp.json
if exist "%WORKSPACE%\.vscode\tasks.json" echo Found .vscode\tasks.json
if exist "%WORKSPACE%\docs\context-packs\context-pack-latest.md" echo Found context-pack-latest.md
if exist "%WORKSPACE%\docs\relationship-maps\graphify-sml-relationship-map.json" echo Found relationship-map JSON

echo.
echo === Memory auto status ===
"C:\Program Files\PowerShell\7\pwsh.exe" -NoProfile -ExecutionPolicy Bypass -File "%WORKSPACE%\tools\status-memory-auto.ps1"

echo.
echo === Claude MCP, if available ===
if exist "%CLAUDE_CMD%" (
  "%CLAUDE_CMD%" mcp list
) else (
  echo Claude CLI not found at %CLAUDE_CMD%
)

echo.
echo === MiMo MCP, if available ===
if exist "%MIMO_CMD%" (
  "%MIMO_CMD%" mcp list
) else (
  echo MiMo CLI not found at %MIMO_CMD%
)

pause
