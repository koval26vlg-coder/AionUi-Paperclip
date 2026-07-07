# Agent Workflows

`docs/agent-workflows/` stores explicit coordination state for hierarchical agent work.

The workflow is a task/assignment, not a chat. Agents act like departments:

| Level | Department | Default agent | Purpose |
| --- | --- | --- | --- |
| `L1` | Исследовательский отдел | Grok Build | SML bootstrap, problem framing, context scout, prepare L1 handoff. |
| `L2` | Инженерная проверка | Antigravity CLI | Engineering review of L1, constraints, edge cases, revision gate. |
| `L3` | Декомпозиция реализации, тесты и automation | Codex | Implementation decomposition, tests, automation, integration readiness. |
| `L4` | Архитектурный синтез | Codex | Architecture synthesis, contract audit, maintainability and risk gate. |
| `L5` | Финальная инстанция | Claude Code | Independent final technical verification and `final-report.md` for the user. |

As of 2026-06-24, new workflows no longer use `MiMo AUTO` because the user decided to remove it from the active scheme before the paid cutoff. As of 2026-07-07, new workflows default to `grok-antigravity`: `L1 Grok Build -> L2 Antigravity CLI -> L3 Codex -> L4 Codex -> L5 Claude Code`. `antigravity`, `gemini-vertex`, and legacy `grok-gemini` remain explicit profiles. Old workflows may still contain historical `L1.0 MiMo AUTO`, previous Antigravity defaults, temporary Gemini Vertex defaults, or Grok->Gemini experiments; do not use archived contracts as the current template.

## Workflow Layout

Each workflow lives in:

```text
docs/agent-workflows/<workflow-id>/
```

Required files:

- `contract.json` - machine-readable state, current level, allowed next agents, blockers, and risk gate.
- `brief.md` - the original user/task brief. Read this before every level.
- `handoff.md` - the latest handoff packet.
- `events.jsonl` - append-only audit log.
- `final-report.md` - final executive report, created only by `finalize`.

Per-level files:

```text
levels/L1/handoff.md
levels/L2/handoff.md
levels/L3/handoff.md
levels/L4/handoff.md
levels/L5/final-report.md
```

## Anti-Distortion Protocol

Agents must not continue a workflow unless `contract.json.allowed_next_agents` contains their exact name.

Before doing work, the next agent must read:

1. `brief.md`
2. `contract.json`
3. `handoff.md`
4. `events.jsonl`
5. relevant files under `levels/`

Agents must not rewrite earlier conclusions silently. If a later level disagrees with earlier work, it must create `disagreement.md` through `request-revision --disagreement-file`.

No workflow may skip directly from L1 to L5. Escalation moves one level at a time.

New workflows start at `L1` with `Grok Build` under the default `grok-antigravity` profile. `Grok Build`, `Antigravity CLI`, and `Gemini Vertex` are review-only for state mutations, so Codex or Claude Code must act as trusted executor for `claim`, `submit-work`, and `approve-level`.

## Subagents

Subagents are role definitions inside a level. They do not become separate `allowed_next_agents`.

| Level | Agent | Subagents |
| --- | --- | --- |
| `L1` | Grok Build | `grok-memory-bootstrapper`, `grok-problem-framer`, `grok-source-scout`, `grok-handoff-editor` |
| `L2` | Antigravity CLI | `antigravity-engineering-reviewer`, `antigravity-constraint-checker`, `antigravity-edge-case-scout`, `antigravity-revision-gate` |
| `L3` | Codex | `codex-implementation-decomposer`, `codex-test-planner`, `codex-automation-builder`, `codex-integration-checker` |
| `L4` | Codex | `codex-architecture-synthesizer`, `codex-contract-auditor`, `codex-risk-gate`, `codex-maintainability-reviewer` |
| `L5` | Claude Code | `claude-executive-summarizer`, `claude-technical-verifier`, `claude-anti-distortion-auditor`, `claude-final-decision-writer` |

Legacy `grok-gemini` profile:

| Level | Agent | Subagents |
| --- | --- | --- |
| `L1` | Grok Build | `grok-memory-bootstrapper`, `grok-problem-framer`, `grok-source-scout`, `grok-handoff-editor` |
| `L2` | Gemini Vertex | `gemini-engineering-reviewer`, `gemini-constraint-checker`, `gemini-edge-case-scout`, `gemini-revision-gate` |

## Model Policy

Each subagent stores its requested model in `contract.json` under `subagent.model`.

The full matrix is maintained in:

```text
docs/agent-workflows/model-policy.md
```

Provider model names are treated as user-approved target aliases. If a CLI/provider does not expose the exact alias at runtime, the agent must record that mismatch in the handoff and ask for an approved fallback instead of silently substituting another model.

For default Grok L1, use `tools/grok_build_workflow_review.py`. It sends an isolated workflow packet to `grok --model grok-build --prompt-file ... --disable-web-search --no-subagents` and writes only a handoff draft; Codex then mutates workflow state with `--executor Codex`.

For default Antigravity L2, use `tools/antigravity_workflow_review.py`. It sends an isolated workflow packet to `agy` and writes only a handoff draft; Codex then mutates workflow state with `--executor Codex`. Use `tools/antigravity_print.py` instead of raw `agy --print` when a headless result is needed. The wrapper prints native stdout when available and falls back to the latest Antigravity conversation DB when `agy` returns an empty stdout.

For the fallback Gemini Vertex profile, use `tools/gemini_vertex_workflow_review.py`. It sends an isolated workflow packet to Vertex Gemini and writes only a handoff draft; Codex then mutates workflow state with `--executor Codex`.

For the legacy Grok->Gemini profile, use the same Grok runner for L1 and Gemini Vertex runner for L2.

Important runtime rule: `Gemini Vertex`, `Antigravity CLI`, and `Grok Build` are review-only for workflow state mutations.

To run exactly one current workflow step and avoid the "created but nothing is happening" state, use:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File D:\AionUi-Paperclip\tools\run-agent-workflow-next.ps1 -Root D:\AionUi-Paperclip\docs\agent-workflows -WorkflowId <workflow-id>
```

The runner reads `contract.json`, uses the currently allowed agent, runs the matching isolated review runner for `Grok Build`, `Antigravity CLI`, or `Gemini Vertex`, then lets Codex submit or approve through `agent_workflow.py --executor Codex`. It performs one step only. For example: on `planned/L1` it claims and submits L1; on `waiting_for_approval` it asks the next agent to review the submitted handoff and then approves or requests revision.

For Antigravity:

```powershell
D:\AionUi-Paperclip\.venv-sml\Scripts\python.exe D:\AionUi-Paperclip\tools\antigravity_workflow_review.py <workflow-id> --task "<L1/L2 review task>" --out <handoff-draft.md>
```

Then Codex writes state on behalf of the review-only agent:

```powershell
D:\AionUi-Paperclip\.venv-sml\Scripts\python.exe D:\AionUi-Paperclip\tools\agent_workflow.py claim <workflow-id> --agent "Antigravity CLI" --executor Codex
D:\AionUi-Paperclip\.venv-sml\Scripts\python.exe D:\AionUi-Paperclip\tools\agent_workflow.py submit-work <workflow-id> --agent "Antigravity CLI" --executor Codex --handoff-file <handoff-draft.md>
```

Do not run Antigravity with `cwd=D:\AionUi-Paperclip` and do not ask it to call `agent_workflow.py` directly.

For fallback Gemini Vertex:

```powershell
D:\AionUi-Paperclip\.venv-sml\Scripts\python.exe D:\AionUi-Paperclip\tools\gemini_vertex_workflow_review.py <workflow-id> --task "<L1/L2 review task>" --out <handoff-draft.md>
```

Then Codex writes state on behalf of the review-only agent:

```powershell
D:\AionUi-Paperclip\.venv-sml\Scripts\python.exe D:\AionUi-Paperclip\tools\agent_workflow.py claim <workflow-id> --agent "Gemini Vertex" --executor Codex
D:\AionUi-Paperclip\.venv-sml\Scripts\python.exe D:\AionUi-Paperclip\tools\agent_workflow.py submit-work <workflow-id> --agent "Gemini Vertex" --executor Codex --handoff-file <handoff-draft.md>
```

For experimental Grok Build:

```powershell
D:\AionUi-Paperclip\.venv-sml\Scripts\python.exe D:\AionUi-Paperclip\tools\grok_build_workflow_review.py <workflow-id> --task "<L1 review task>" --out <handoff-draft.md>
```

Then Codex writes state on behalf of the review-only agent:

```powershell
D:\AionUi-Paperclip\.venv-sml\Scripts\python.exe D:\AionUi-Paperclip\tools\agent_workflow.py claim <workflow-id> --agent "Grok Build" --executor Codex
D:\AionUi-Paperclip\.venv-sml\Scripts\python.exe D:\AionUi-Paperclip\tools\agent_workflow.py submit-work <workflow-id> --agent "Grok Build" --executor Codex --handoff-file <handoff-draft.md>
```

Direct Gemini Vertex, Antigravity, and Grok Build mutations are blocked by `agent_workflow.py`. This prevents L1/L2 from self-advancing the workflow after a model call.

## Required Handoff Format

Every submitted level handoff must contain these headings:

```markdown
## Что было сделано

## На чем основан вывод

## Что получилось хорошо

## Что требует доработки

## Какие есть риски

## Что нельзя потерять/исказить дальше

## Решение
```

Valid decisions are `approve`, `revise`, `escalate`, and `block`.

## CLI

Use:

```powershell
D:\AionUi-Paperclip\.venv-sml\Scripts\python.exe D:\AionUi-Paperclip\tools\agent_workflow.py status <workflow-id>
```

Shortcut for starting a new swarm workflow:

```powershell
.\START-AGENT-SWARM.cmd -Title "Проверить идею продукта" -Brief "Нужно оценить спрос, риски, MVP и план проверки."
```

Default profile:

```powershell
.\tools\start-agent-swarm.ps1 -Title "Проверить идею продукта" -Brief "..."
```

Explicit fallback Gemini Vertex profile:

```powershell
.\tools\start-agent-swarm.ps1 -Title "Проверить идею продукта" -Brief "..." -Profile gemini-vertex
```

Explicit Antigravity-only profile:

```powershell
.\tools\start-agent-swarm.ps1 -Title "Проверить идею продукта" -Brief "..." -Profile antigravity
```

Legacy Grok -> Gemini profile:

```powershell
.\tools\start-agent-swarm.ps1 -Title "Проверить идею продукта" -Brief "..." -Profile grok-gemini
```

Chat trigger:

```text
Рой: <задача>
Рой, <задача>
РОЙ: <задача>
РОЙ, <задача>
рой: <задача>
```

The trigger is case-insensitive for `Рой`; uppercase `РОЙ` is the same command.

Full trigger protocol: `docs/agent-workflows/SWARM-COMMAND.md`.

Commands:

- `new`
- `claim`
- `submit-work`
- `approve-level`
- `request-revision`
- `escalate`
- `approve-risk`
- `finalize`
- `status`

For review-only agents such as `Gemini Vertex`, `Antigravity CLI`, and `Grok Build`, mutating commands require a trusted executor:

```powershell
... agent_workflow.py approve-level <workflow-id> --agent "Antigravity CLI" --executor Codex
```

New workflows start with:

```json
"current_level": "L1",
"workflow_profile": "grok-antigravity",
"allowed_next_agents": ["Grok Build"]
```

## Risk Gate

Risk flags:

- `trading`
- `writes_external_system`
- `long_running`
- `uses_secrets`
- `destructive`

If any risk flag is true, `risk_gate.required=true`. The workflow cannot be finalized until `approve-risk` passes.

Long-running workflows must run in a visible terminal or through a visible monitor. Hidden background runs are prohibited unless the user explicitly approves them and metadata is recorded.

