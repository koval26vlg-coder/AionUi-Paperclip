param(
    [string] $ShimDir = (Join-Path ([Environment]::GetFolderPath('UserProfile')) 'bat')
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

New-Item -ItemType Directory -Force -Path $ShimDir | Out-Null

function Write-AionShim {
    param(
        [Parameter(Mandatory = $true)]
        [string] $Name,

        [Parameter(Mandatory = $true)]
        [string] $Content
    )

    $path = Join-Path $ShimDir $Name
    $normalized = $Content.Trim() + "`r`n"

    if (Test-Path -LiteralPath $path -PathType Leaf) {
        $existing = Get-Content -LiteralPath $path -Raw -Encoding UTF8
        if ($existing -eq $normalized) {
            Write-Host "unchanged $path"
            return
        }

        if ($existing -notmatch 'Aion agent CLI shim') {
            $stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
            Copy-Item -LiteralPath $path -Destination "$path.aion-backup-$stamp" -Force
        }
    }

    Set-Content -LiteralPath $path -Value $normalized -Encoding ASCII
    Write-Host "wrote $path"
}

Write-AionShim -Name 'node.cmd' -Content @'
@echo off
rem Aion agent CLI shim: stable node launcher.
"C:\Program Files\nodejs\node.exe" %*
'@

Write-AionShim -Name 'npm.cmd' -Content @'
@echo off
rem Aion agent CLI shim: stable npm launcher.
"C:\Program Files\nodejs\node.exe" "C:\Program Files\nodejs\node_modules\npm\bin\npm-cli.js" %*
'@

Write-AionShim -Name 'npx.cmd' -Content @'
@echo off
rem Aion agent CLI shim: stable npx launcher.
"C:\Program Files\nodejs\node.exe" "C:\Program Files\nodejs\node_modules\npm\bin\npx-cli.js" %*
'@

Write-AionShim -Name 'claude.cmd' -Content @'
@echo off
rem Aion agent CLI shim: stable Claude Code launcher.
"C:\Users\koval\AppData\Roaming\npm\node_modules\@anthropic-ai\claude-code\bin\claude.exe" %*
'@

Write-AionShim -Name 'agy.cmd' -Content @'
@echo off
rem Aion agent CLI shim: stable Antigravity launcher.
"C:\Users\koval\AppData\Local\agy\bin\agy.exe" %*
'@

Write-AionShim -Name 'cmd.cmd' -Content @'
@echo off
rem Aion agent CLI shim: stable Windows command processor launcher.
"C:\Windows\System32\cmd.exe" %*
'@

Write-AionShim -Name 'where.cmd' -Content @'
@echo off
rem Aion agent CLI shim: stable where.exe launcher.
"C:\Windows\System32\where.exe" %*
'@

Write-Host "Agent CLI shims installed in $ShimDir"
