$ErrorActionPreference = "Continue"

$root = Split-Path -Parent $PSScriptRoot

Write-Host "Workspace: $root"

$cursor = Get-Command cursor -ErrorAction SilentlyContinue
if ($cursor) {
    Write-Host "Opening Cursor..."
    Start-Process -FilePath $cursor.Source -ArgumentList @($root)
} else {
    Write-Host "Cursor command not found in PATH."
}

$kiroCandidates = @(
    "$env:LOCALAPPDATA\Programs\Kiro\Kiro.exe",
    "$env:LOCALAPPDATA\kiro\Kiro.exe"
)

$kiro = $kiroCandidates | Where-Object { Test-Path -LiteralPath $_ } | Select-Object -First 1
if ($kiro) {
    Write-Host "Opening Kiro..."
    Start-Process -FilePath $kiro -ArgumentList @("--locale", "ru", $root)
} else {
    Write-Host "Kiro executable not found. Open this folder manually in Kiro."
}

$codex = Get-Command codex -ErrorAction SilentlyContinue
if ($codex) {
    Write-Host "Opening Codex CLI in a new PowerShell window..."
    $command = "Set-Location -LiteralPath '$root'; codex"
    Start-Process -FilePath "powershell.exe" -ArgumentList @("-NoExit", "-Command", $command)
} else {
    Write-Host "Codex command not found in PATH."
}

Write-Host "Done."
