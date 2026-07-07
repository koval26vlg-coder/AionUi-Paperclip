param(
    [switch] $NoRepair
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Continue'

$envScript = Join-Path $PSScriptRoot 'agent-cli-env.ps1'

if (-not $NoRepair) {
    . $envScript
    $stablePath = Repair-AgentCliPath
    Write-Host "PATH normalized. Entries: $(($stablePath -split ';').Count)"
} else {
    Write-Host "PATH repair skipped."
}

$checks = @(
    @{ Name = 'cmd'; Command = 'cmd'; Args = @('/c', 'echo OK') },
    @{ Name = 'where'; Command = 'where.exe'; Args = @('node') },
    @{ Name = 'node'; Command = 'node'; Args = @('--version') },
    @{ Name = 'npm'; Command = 'npm'; Args = @('--version') },
    @{ Name = 'claude'; Command = 'claude'; Args = @('--version') },
    @{ Name = 'agy'; Command = 'agy'; Args = @('--help') }
)

$rows = foreach ($check in $checks) {
    $resolved = Get-Command $check.Command -CommandType Application, ExternalScript -ErrorAction SilentlyContinue | Select-Object -First 1
    $output = ''
    $ok = $false
    if ($resolved) {
        try {
            $output = (& $resolved.Source @($check.Args) 2>&1 | Select-Object -First 3) -join ' '
            $ok = $LASTEXITCODE -eq 0 -or $null -eq $LASTEXITCODE
        } catch {
            $output = $_.Exception.Message
            $ok = $false
        }
    } else {
        $output = 'not found'
    }

    [pscustomobject]@{
        Name = $check.Name
        Found = [bool] $resolved
        Path = if ($resolved) { $resolved.Source } else { '' }
        OK = $ok
        Output = $output
    }
}

$rows | Format-Table -AutoSize

if ($rows | Where-Object { -not $_.Found -or -not $_.OK }) {
    exit 1
}

exit 0
