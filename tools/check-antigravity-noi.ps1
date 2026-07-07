param(
    [string] $HostName = "147.90.11.165",
    [string] $User = "root",
    [int] $Port = 22,
    [int] $ConnectTimeoutSeconds = 8,
    [switch] $Smoke
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Continue"

$sshCommand = Get-Command ssh.exe -ErrorAction SilentlyContinue
$ssh = if ($sshCommand) { $sshCommand.Source } else { $null }
if (-not $ssh) {
    $ssh = "C:\Windows\System32\OpenSSH\ssh.exe"
}
if (-not (Test-Path -LiteralPath $ssh)) {
    throw "ssh.exe not found. Expected at C:\Windows\System32\OpenSSH\ssh.exe"
}

Write-Host "Antigravity NOI check"
Write-Host "Target: $User@$HostName`:$Port"

$client = [System.Net.Sockets.TcpClient]::new()
try {
    $iar = $client.BeginConnect($HostName, $Port, $null, $null)
    if (-not $iar.AsyncWaitHandle.WaitOne($ConnectTimeoutSeconds * 1000)) {
        Write-Host "TCP: timeout"
        exit 2
    }
    $client.EndConnect($iar)
    Write-Host "TCP: connected"

    $stream = $client.GetStream()
    $stream.ReadTimeout = $ConnectTimeoutSeconds * 1000
    $buffer = New-Object byte[] 256
    try {
        $n = $stream.Read($buffer, 0, $buffer.Length)
        if ($n -gt 0) {
            $banner = [Text.Encoding]::ASCII.GetString($buffer, 0, $n).Trim()
            Write-Host "SSH banner: $banner"
        } else {
            Write-Host "SSH banner: empty"
            exit 3
        }
    } catch {
        Write-Host "SSH banner: read failed - $($_.Exception.Message)"
        exit 3
    }
} finally {
    $client.Close()
}

$remoteVersion = 'export PATH="$HOME/.local/bin:$PATH"; echo SSH_OK; hostname; agy --version'
& $ssh -p $Port -o BatchMode=yes -o ConnectTimeout=$ConnectTimeoutSeconds -o ConnectionAttempts=1 "$User@$HostName" $remoteVersion
if ($LASTEXITCODE -ne 0) {
    Write-Host "SSH command failed with exit code $LASTEXITCODE"
    exit $LASTEXITCODE
}

if ($Smoke) {
    $remoteSmoke = 'export PATH="$HOME/.local/bin:$PATH"; agy --print "Ответь ровно одним словом: ok"'
    & $ssh -p $Port -o BatchMode=yes -o ConnectTimeout=$ConnectTimeoutSeconds -o ConnectionAttempts=1 "$User@$HostName" $remoteSmoke
    exit $LASTEXITCODE
}

exit 0
