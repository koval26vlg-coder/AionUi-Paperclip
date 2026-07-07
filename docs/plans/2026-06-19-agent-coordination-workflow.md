# Hierarchical Agent Departments Implementation Plan

> **For Claude:** Use `${SUPERPOWERS_SKILLS_ROOT}/skills/collaboration/executing-plans/SKILL.md` to implement this plan task-by-task.

**Goal:** Build a local hierarchical workflow where MiMo AUTO, Antigravity CLI, Codex, Claude Code, and the user act like departments with explicit handoffs, approvals, escalation, and final reporting.

**Architecture:** Keep SML as durable memory and add file-backed workflows under `docs/agent-workflows/`. A task moves through levels L1-L5; each level writes a structured handoff, the next level reads the original brief plus prior handoff/events, and the final report preserves the task history without "broken telephone" distortion.

**Tech Stack:** Python stdlib, PowerShell, Markdown/JSON files, existing SML MCP, existing `AGENTS.md`/`CLAUDE.md`, Antigravity `agy`, VS Code tasks.

---

## Operating Model

The workflow is a task/assignment, not a multi-model chat.

Levels:

- `L1.0`: нижний AUTO-исполнитель. MiMo AUTO performs the first rough pass: leads, initial hypotheses, obvious risks, and context that Gemini must verify.
- `L1.1`: исследовательский lead. Antigravity CLI reviews MiMo AUTO, expands facts, removes noise, collects alternatives, and submits the checked L1 handoff.
- `L2`: инженерная проверка. Antigravity CLI checks L1 for engineering feasibility, constraints, edge cases, and revision gates.
- `L3`: декомпозиция реализации, тесты и automation. Codex performs implementation decomposition, test planning, automation planning/building, and integration readiness.
- `L4`: архитектурный синтез. Codex synthesizes L1-L3 into a coherent architecture, audits contracts/events, checks maintainability, and runs risk gate review.
- `L5`: финальная инстанция для пользователя. Claude Code performs independent final technical verification and writes `final-report.md` for the user.

MiMo AUTO is scoped only to `L1.0`. This is not a rollback to the old MiMo project configuration: `.mimocode/` and the deleted MiMo launchers are not restored, and SML remains the source of truth.

Subagents are written into `contract.json` as role metadata for each level. They are not separate workflow turns unless modeled as explicit subroles (`L1.0`, `L1.1`).

Every level must preserve:

- what was done;
- evidence or source basis;
- what went well;
- what requires revision;
- risks;
- what must not be lost or distorted;
- decision: `approve`, `revise`, `escalate`, or `block`.

No level may skip directly to L5. If a later level disagrees with an earlier level, it writes `disagreement.md` instead of silently rewriting the conclusion.

## Workflow Files

Each workflow lives in:

```text
docs/agent-workflows/<workflow-id>/
```

Required files:

- `contract.json` - machine-readable state, current level, allowed next agents, risk flags, and unresolved blockers.
- `brief.md` - original user/task brief. Agents must read this instead of relying on memory.
- `handoff.md` - current handoff packet.
- `events.jsonl` - append-only audit log.
- `final-report.md` - final report for the user, created only at L5/finalize.

Generated per-level files are stored in:

```text
docs/agent-workflows/<workflow-id>/levels/L1/L1.0/handoff.md
docs/agent-workflows/<workflow-id>/levels/L1/L1.1/handoff.md
docs/agent-workflows/<workflow-id>/levels/L2/handoff.md
...
```

## CLI Commands

Implement `tools/agent_workflow.py`:

- `new` creates a workflow and sets `current_level="L1"`, `current_subrole="L1.0"`, `allowed_next_agents=["MiMo AUTO"]`.
- `claim` lets only the allowed agent take the current level/subrole.
- `submit-work` validates and stores a standard handoff for the current level/subrole.
- `approve-level` accepts the submitted level/subrole and moves to the next subrole or next level, except L5 which must use `finalize`.
- `request-revision` returns work to the current level agent and can store `disagreement.md`.
- `escalate` moves only one level higher; direct L1-to-L5 escalation is rejected.
- `finalize` creates `final-report.md` and marks the workflow `done`.
- `status` shows current level, state, allowed next agents, blockers, and last event.

## Risk Gate

Risk flags:

- `trading`
- `writes_external_system`
- `long_running`
- `uses_secrets`
- `destructive`

If any flag is true, `risk_gate.required=true`. `finalize` is blocked until `approve-risk` records a risk review. Long-running workflows must use a visible terminal or visible monitor; hidden background runs are prohibited unless the user explicitly approves them.

## Verification

Required tests:

- L1 cannot jump directly to L5.
- An unlisted agent cannot `claim`.
- `approve-level` requires a submitted handoff.
- `finalize` is blocked by unresolved revision/block.
- A full smoke path can move: MiMo AUTO L1.0 -> Gemini L1.1 -> Gemini L2 -> Codex L3 -> Codex L4 -> Claude L5 final report.
- A risk workflow cannot finalize until risk review is approved.

Recommended implementation order:

1. Documentation and schema.
2. CLI and tests.
3. Visible monitor and VS Code task.
4. Smoke workflow verification.
