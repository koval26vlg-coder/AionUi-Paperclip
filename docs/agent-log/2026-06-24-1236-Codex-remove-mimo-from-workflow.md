# 2026-06-24 12:36 +03 - Codex - MiMo removed from new agent workflows

## Request

Пользователь попросил убрать MiMo, потому что с 2026-06-25 он становится платным.

## Result

Новые `docs/agent-workflows` больше не стартуют с `MiMo AUTO L1.0`.

Текущая цепочка:

```text
L1 Antigravity CLI -> L2 Antigravity CLI -> L3 Codex -> L4 Codex -> L5 Claude Code
```

Обновлены:

- `tools/agent_workflow.py`
- `tools/start-agent-swarm.ps1`
- `tools/agent_limit_monitor.py`
- `tools/check-agent-runtimes.ps1`
- `tools/install-agent-cli-shims.ps1`
- `docs/agent-limits/limits-config.json`
- `docs/agent-workflows/schema.example.json`
- `docs/agent-workflows/model-policy.md`
- `docs/agent-workflows/README.md`
- `docs/agent-workflows/README-smoke.md`
- `AGENTS.md`
- `README.md`
- `docs/current-context.md`
- `docs/tasks.md`
- `docs/decisions.md`
- глобальные правила Codex и Claude

Старые workflow с `L1.0 MiMo AUTO` оставлены как исторические артефакты и не переписаны.

Локальный runtime также очищен:

- удален глобальный npm-пакет `@mimo-ai/cli`;
- удален user-level shim `C:\Users\koval\bat\mimo.cmd`;
- `check-agent-runtimes.ps1` больше не проверяет `mimo`;
- `install-agent-cli-shims.ps1` больше не создает `mimo.cmd`.

## Verification

- `python -m py_compile tools/agent_workflow.py tools/agent_limit_monitor.py`
- `python -m json.tool docs/agent-limits/limits-config.json`
- `python -m json.tool docs/agent-workflows/schema.example.json`
- `python -m pytest tools/sml/tests/test_agent_workflow.py tools/sml/tests/test_agent_limit_monitor.py -q` -> `13 passed`
- `tools/start-agent-swarm.ps1 -Title "No MiMo smoke" -Brief "Verify new workflow starts without MiMo." -DryRun`
- temp workflow smoke: `current_level=L1`, `current_subrole=null`, `allowed_next_agents=["Antigravity CLI"]`, generated `contract.json` has no legacy L1.0/L1.1/MiMo/Xiaomi markers when the brief itself does not contain them.
- `agent_limit_monitor.py --days 1 --no-write --json` returns only `Codex`, `Claude Code`, `Antigravity CLI`.
- `npm list -g @mimo-ai/cli --depth=0` -> empty.
- `Get-Command mimo` -> not found.
- `tools/check-agent-runtimes.ps1 -NoRepair` -> passed for `cmd`, `where`, `node`, `npm`, `claude`, `agy`.
