Set-StrictMode -Version Latest

function Add-AionPathEntry {
    param(
        [System.Collections.Generic.List[string]] $Entries,

        [Parameter(Mandatory = $false)]
        [string] $PathEntry
    )

    if ([string]::IsNullOrWhiteSpace($PathEntry)) {
        return
    }

    $trimmed = $PathEntry.Trim()
    if ($trimmed -eq '${PATH}') {
        return
    }

    $expanded = [Environment]::ExpandEnvironmentVariables($trimmed).TrimEnd('\')
    if (-not (Test-Path -LiteralPath $expanded -PathType Container)) {
        return
    }

    foreach ($existing in $Entries) {
        if ([string]::Equals($existing, $expanded, [StringComparison]::OrdinalIgnoreCase)) {
            return
        }
    }

    $Entries.Add($expanded) | Out-Null
}

function Get-AionStablePath {
    $entries = [System.Collections.Generic.List[string]]::new()
    $homeDir = [Environment]::GetFolderPath('UserProfile')
    $systemRoot = $env:SystemRoot
    if ([string]::IsNullOrWhiteSpace($systemRoot)) {
        $systemRoot = 'C:\Windows'
    }

    $preferred = @(
        (Join-Path $systemRoot 'system32'),
        $systemRoot,
        (Join-Path $homeDir 'bat'),
        'C:\Program Files\PowerShell\7',
        'C:\Program Files\nodejs',
        (Join-Path $homeDir 'AppData\Roaming\npm'),
        (Join-Path $homeDir 'AppData\Local\agy\bin'),
        'C:\Program Files\Git\cmd'
    )

    foreach ($entry in $preferred) {
        Add-AionPathEntry -Entries $entries -PathEntry $entry
    }

    $sourcePaths = @(
        [Environment]::GetEnvironmentVariable('Path', 'Process'),
        [Environment]::GetEnvironmentVariable('PATH', 'Process'),
        [Environment]::GetEnvironmentVariable('Path', 'User'),
        [Environment]::GetEnvironmentVariable('PATH', 'User'),
        [Environment]::GetEnvironmentVariable('Path', 'Machine'),
        [Environment]::GetEnvironmentVariable('PATH', 'Machine')
    )

    foreach ($source in $sourcePaths) {
        if ([string]::IsNullOrWhiteSpace($source)) {
            continue
        }
        foreach ($entry in ($source -split ';')) {
            Add-AionPathEntry -Entries $entries -PathEntry $entry
        }
    }

    return ($entries -join ';')
}

function Repair-AgentCliPath {
    $stablePath = Get-AionStablePath
    $env:Path = $stablePath
    $env:PATH = $stablePath
    [Environment]::SetEnvironmentVariable('Path', $stablePath, 'Process')
    return $stablePath
}
