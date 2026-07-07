param(
    [string] $HostName = "147.90.11.165",
    [string] $User = "root",
    [int] $Port = 22
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$sshCommand = Get-Command ssh.exe -ErrorAction SilentlyContinue
$ssh = if ($sshCommand) { $sshCommand.Source } else { $null }
if (-not $ssh) {
    $ssh = "C:\Windows\System32\OpenSSH\ssh.exe"
}
if (-not (Test-Path -LiteralPath $ssh)) {
    throw "ssh.exe not found. Expected at C:\Windows\System32\OpenSSH\ssh.exe"
}

$target = "$User@$HostName"
$remote = 'export PATH="$HOME/.local/bin:$PATH"; agy'

Write-Host "Antigravity OAuth on NOI ($target)"
Write-Host "1. Open the Google URL printed by agy."
Write-Host "2. Finish login in the browser."
Write-Host "3. If the CLI times out, press Enter here to retry and get a fresh URL."
Write-Host "4. After auth succeeds, close/exit agy and run:"
Write-Host "   pwsh -NoProfile -ExecutionPolicy Bypass -File D:\AionUi-Paperclip\tools\check-antigravity-noi.ps1 -Smoke"
Write-Host ""

while ($true) {
    & $ssh -tt -p $Port -o BatchMode=yes -o ConnectTimeout=8 $target $remote
    $code = $LASTEXITCODE
    Write-Host ""
    Write-Host "agy exited with code $code."
    $answer = Read-Host "Press Enter to retry, or type q to close"
    if ($answer -match '^(q|quit|exit)$') {
        break
    }
}
