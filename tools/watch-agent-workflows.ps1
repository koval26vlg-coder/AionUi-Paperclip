param(
  [string]$Root = "D:\AionUi-Paperclip\docs\agent-workflows",
  [int]$IntervalSeconds = 15
)

$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

while ($true) {
  Clear-Host
  Write-Host "Agent workflow monitor: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
  Write-Host "Root: $Root"
  Write-Host ""

  if (-not (Test-Path $Root)) {
    Write-Host "No workflow root found."
  } else {
    $workflowDirs = Get-ChildItem -Path $Root -Directory | Sort-Object LastWriteTime -Descending
    if (-not $workflowDirs) {
      Write-Host "No workflows yet."
    }

    foreach ($dir in $workflowDirs) {
      $contractPath = Join-Path $dir.FullName "contract.json"
      if (-not (Test-Path $contractPath)) {
        continue
      }

      try {
        $contract = Get-Content -Raw $contractPath | ConvertFrom-Json
        $updated = [datetime]$contract.updated_at
        $age = New-TimeSpan -Start $updated -End (Get-Date)
        $ageText = "{0:00}:{1:00}:{2:00}" -f [int]$age.TotalHours, $age.Minutes, $age.Seconds

        Write-Host "[$($contract.state)] $($contract.workflow_id)"
        Write-Host "  title:   $($contract.title)"
        Write-Host "  level:   $($contract.current_level)"
        if ($contract.current_subrole) {
          Write-Host "  subrole: $($contract.current_subrole)"
        }
        Write-Host "  next:    $($contract.allowed_next_agents -join ', ')"
        Write-Host "  event:   $($contract.last_event)"
        Write-Host "  updated: $($contract.updated_at) (age $ageText)"
        if ($contract.last_handoff) {
          Write-Host "  handoff: $($contract.last_handoff)"
        }
        if ($contract.risk_gate.required -and $contract.risk_gate.status -ne "passed") {
          Write-Host "  risk:    required/$($contract.risk_gate.status)"
        }
        if ($contract.blockers.Count -gt 0) {
          Write-Host "  blockers:"
          foreach ($blocker in $contract.blockers) {
            Write-Host "    - $($blocker.level): $($blocker.reason)"
          }
        }
        Write-Host ""
      } catch {
        Write-Host "[$($dir.Name)] failed to read contract: $($_.Exception.Message)"
        Write-Host ""
      }
    }
  }

  Start-Sleep -Seconds $IntervalSeconds
}
