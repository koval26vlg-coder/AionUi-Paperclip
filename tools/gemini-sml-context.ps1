param(
  [Parameter(Mandatory = $true)]
  [string]$Query,

  [int]$MaxLogEntries = 5,

  [int]$Limit = 5
)

$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

$root = Split-Path -Parent $PSScriptRoot
$python = Join-Path $root ".venv-sml\Scripts\python.exe"

if (-not (Test-Path $python)) {
  throw "SML Python interpreter not found: $python"
}

$env:PYTHONUTF8 = "1"
$env:PYTHONUNBUFFERED = "1"
$env:PYTHONPATH = $root
$env:SML_ROOT = $root
$env:OLLAMA_HOST = "127.0.0.1"

function ConvertTo-JsonLine {
  param([object]$Value)
  return ($Value | ConvertTo-Json -Depth 30 -Compress)
}

$requests = @(
  [ordered]@{
    jsonrpc = "2.0"
    id = 1
    method = "initialize"
    params = [ordered]@{
      protocolVersion = "2024-11-05"
      capabilities = [ordered]@{}
      clientInfo = [ordered]@{
        name = "gemini-sml-context"
        version = "1"
      }
    }
  },
  [ordered]@{
    jsonrpc = "2.0"
    method = "notifications/initialized"
  },
  [ordered]@{
    jsonrpc = "2.0"
    id = 2
    method = "tools/call"
    params = [ordered]@{
      name = "sml.startup_pack"
      arguments = [ordered]@{
        max_log_entries = $MaxLogEntries
      }
    }
  },
  [ordered]@{
    jsonrpc = "2.0"
    id = 3
    method = "tools/call"
    params = [ordered]@{
      name = "sml.semantic_query"
      arguments = [ordered]@{
        query = $Query
        limit = $Limit
        min_score = 0.1
      }
    }
  }
)

$jsonLines = $requests | ForEach-Object { ConvertTo-JsonLine $_ }
$rawOutput = $jsonLines | & $python -X utf8 -m tools.sml.mcp_adapter

if ($LASTEXITCODE -ne 0) {
  throw "SML adapter exited with code $LASTEXITCODE"
}

$responses = @()
foreach ($line in $rawOutput) {
  $trimmed = "$line".Trim()
  if (-not $trimmed.StartsWith("{")) {
    continue
  }
  $responses += ($trimmed | ConvertFrom-Json)
}

function Get-McpText {
  param([object]$Response)

  if ($null -eq $Response) {
    return ""
  }

  if ($Response.result.content -and $Response.result.content.Count -gt 0 -and $Response.result.content[0].text) {
    return [string]$Response.result.content[0].text
  }

  if ($Response.result) {
    return ($Response.result | ConvertTo-Json -Depth 30)
  }

  return ($Response | ConvertTo-Json -Depth 30)
}

$startup = $responses | Where-Object { $_.id -eq 2 } | Select-Object -First 1
$semantic = $responses | Where-Object { $_.id -eq 3 } | Select-Object -First 1

Write-Output "# SML startup_pack"
Write-Output (Get-McpText $startup)
Write-Output ""
Write-Output "# SML semantic_query"
Write-Output "Query: $Query"
Write-Output (Get-McpText $semantic)
