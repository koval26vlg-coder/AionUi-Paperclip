$ErrorActionPreference = "Continue"

$root = Split-Path -Parent $PSScriptRoot

Write-Host "Workspace: $root"

# Активная связка на 2026-06-18: Codex + Claude Code + Gemini CLI.
# Cursor, Kiro и MiMo Code выведены из схемы.

# VS Code как общая IDE-оболочка SML.
$vscode = "$env:LOCALAPPDATA\Programs\Microsoft VS Code\Code.exe"
if (Test-Path -LiteralPath $vscode) {
    Write-Host "Opening VS Code..."
    Start-Process -FilePath $vscode -ArgumentList @($root)
} else {
    Write-Host "VS Code not found. Open this folder manually."
}

# Claude Code в новом окне PowerShell из рабочей папки.
$claude = Get-Command claude -ErrorAction SilentlyContinue
if (-not $claude -and (Test-Path "$env:APPDATA\npm\claude.cmd")) {
    $claude = [pscustomobject]@{ Source = "$env:APPDATA\npm\claude.cmd" }
}
if ($claude) {
    Write-Host "Opening Claude Code in a new PowerShell window..."
    $command = "Set-Location -LiteralPath '$root'; & '$($claude.Source)'"
    Start-Process -FilePath "powershell.exe" -ArgumentList @("-NoExit", "-Command", $command)
} else {
    Write-Host "Claude command not found. Use OPEN-CLAUDE-SML.cmd."
}

# Codex CLI в новом окне PowerShell из рабочей папки.
$codex = Get-Command codex -ErrorAction SilentlyContinue
if ($codex) {
    Write-Host "Opening Codex CLI in a new PowerShell window..."
    $command = "Set-Location -LiteralPath '$root'; codex"
    Start-Process -FilePath "powershell.exe" -ArgumentList @("-NoExit", "-Command", $command)
} else {
    Write-Host "Codex command not found in PATH."
}

Write-Host "Done."
