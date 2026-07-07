# Agent Workflow Model Policy

Эта политика закрепляет пользовательский выбор моделей для уровней и субагентов `docs/agent-workflows/`.

Важно: названия моделей ниже сохраняются как пользовательские алиасы/целевые model labels. Перед живым запуском конкретного CLI нужно отдельно проверить доступность модели у провайдера и соответствие реальному имени модели в API/CLI.

Профиль по умолчанию для новых workflow — `grok-antigravity`. Он использует `Grok Build 0.2.87` для `L1`, `Antigravity CLI` для `L2`, затем стандартные `Codex L3/L4` и `Claude Code L5`.

Профиль `antigravity` сохранен как явный режим без Grok. Он использует `Antigravity CLI` для `L1/L2` через `agy`, isolated runner `tools/antigravity_workflow_review.py` и закрепленный alias `Antigravity CLI AUTO`.

Профиль `gemini-vertex` сохранен как резервный режим. Он использует `Gemini Vertex` для `L1/L2` через Google Vertex AI, ADC, `GOOGLE_CLOUD_PROJECT`, `GOOGLE_CLOUD_LOCATION` и текущую рабочую модель `gemini-2.5-flash`.

Профиль `grok-gemini` оставлен как legacy/экспериментальный режим. Он использует `Grok Build 0.2.87` для `L1`, `Gemini Vertex` для `L2`, затем стандартные `Codex L3/L4` и `Claude Code L5`. Live runtime Grok подтвержден 2026-07-06: `grok 0.2.87`, auth через `grok.com`, `grok-build` headless smoke, MCP `sml` в Grok-safe режиме и валидный L1 handoff через `tools/grok_build_workflow_review.py`.

## Матрица Моделей

| Level | Subagent | Model |
| --- | --- | --- |
| `L1` | `grok-memory-bootstrapper` | Grok Build 0.2.87 / High |
| `L1` | `grok-problem-framer` | Grok Build 0.2.87 / Medium |
| `L1` | `grok-source-scout` | Grok Build 0.2.87 / High |
| `L1` | `grok-handoff-editor` | Grok Build 0.2.87 / Medium |
| `L2` | `antigravity-engineering-reviewer` | Antigravity CLI AUTO / High |
| `L2` | `antigravity-constraint-checker` | Antigravity CLI AUTO / High |
| `L2` | `antigravity-edge-case-scout` | Antigravity CLI AUTO / High |
| `L2` | `antigravity-revision-gate` | Antigravity CLI AUTO / High |
| `L3` | `codex-implementation-decomposer` | codex-5.3 / xhigh |
| `L3` | `codex-test-planner` | gpt-5.5 / xhigh |
| `L3` | `codex-automation-builder` | gpt-5.4 mini / xhigh |
| `L3` | `codex-integration-checker` | gpt-5.4 / xhigh |
| `L4` | `codex-architecture-synthesizer` | gpt-5.5 / xhigh |
| `L4` | `codex-contract-auditor` | gpt-5.5 / xhigh |
| `L4` | `codex-risk-gate` | gpt-5.5 / xhigh |
| `L4` | `codex-maintainability-reviewer` | gpt-5.5 / xhigh |
| `L5` | `claude-executive-summarizer` | Claude Opus 4.7 alias / xhigh |
| `L5` | `claude-technical-verifier` | Claude Haiku 4.5 alias / xhigh |
| `L5` | `claude-anti-distortion-auditor` | Claude Sonnet 4.6 alias / xhigh |
| `L5` | `claude-final-decision-writer` | Claude Opus 4.8 alias / xhigh |

## Explicit Antigravity Profile

Use `agent_workflow.py new --profile antigravity` or `start-agent-swarm.ps1 -Profile antigravity` when the user wants to skip Grok and start directly with Antigravity L1.

| Level | Subagent | Model |
| --- | --- | --- |
| `L1` | `antigravity-source-verifier` | Antigravity CLI AUTO / High |
| `L1` | `antigravity-context-expander` | Antigravity CLI AUTO / Low |
| `L1` | `antigravity-noise-filter` | Antigravity CLI AUTO / Low |
| `L1` | `antigravity-handoff-editor` | Antigravity CLI AUTO / Medium |
| `L2` | `antigravity-engineering-reviewer` | Antigravity CLI AUTO / High |
| `L2` | `antigravity-constraint-checker` | Antigravity CLI AUTO / High |
| `L2` | `antigravity-edge-case-scout` | Antigravity CLI AUTO / High |
| `L2` | `antigravity-revision-gate` | Antigravity CLI AUTO / High |

## Fallback Gemini Vertex Profile

Use `agent_workflow.py new --profile gemini-vertex` or `start-agent-swarm.ps1 -Profile gemini-vertex` when `agy`/Antigravity is unavailable or Vertex AI is explicitly preferred.

| Level | Subagent | Model |
| --- | --- | --- |
| `L1` | `gemini-source-verifier` | gemini-2.5-flash via Vertex AI / High |
| `L1` | `gemini-context-expander` | gemini-2.5-flash via Vertex AI / Low |
| `L1` | `gemini-noise-filter` | gemini-2.5-flash via Vertex AI / Low |
| `L1` | `gemini-handoff-editor` | gemini-2.5-flash via Vertex AI / Medium |
| `L2` | `gemini-engineering-reviewer` | gemini-2.5-flash via Vertex AI / High |
| `L2` | `gemini-constraint-checker` | gemini-2.5-flash via Vertex AI / High |
| `L2` | `gemini-edge-case-scout` | gemini-2.5-flash via Vertex AI / High |
| `L2` | `gemini-revision-gate` | gemini-2.5-flash via Vertex AI / High |

## Legacy Grok -> Gemini Profile

Use `agent_workflow.py new --profile grok-gemini` or `start-agent-swarm.ps1 -Profile grok-gemini` only when the user explicitly wants the older Grok->Gemini chain.

| Level | Subagent | Model |
| --- | --- | --- |
| `L1` | `grok-memory-bootstrapper` | Grok Build 0.2.87 / High |
| `L1` | `grok-problem-framer` | Grok Build 0.2.87 / Medium |
| `L1` | `grok-source-scout` | Grok Build 0.2.87 / High |
| `L1` | `grok-handoff-editor` | Grok Build 0.2.87 / Medium |
| `L2` | `gemini-engineering-reviewer` | gemini-2.5-flash via Vertex AI / High |
| `L2` | `gemini-constraint-checker` | gemini-2.5-flash via Vertex AI / High |
| `L2` | `gemini-edge-case-scout` | gemini-2.5-flash via Vertex AI / High |
| `L2` | `gemini-revision-gate` | gemini-2.5-flash via Vertex AI / High |

## Contract Shape

Each subagent in `contract.json` stores model metadata:

```json
{
  "id": "grok-memory-bootstrapper",
  "name": "Загрузчик общей памяти",
  "role": "Подтянуть SML-контекст, AGENTS.md, context-pack, decisions, tasks и последние agent-log до анализа задачи.",
  "model": {
    "provider": "xAI Grok Build",
    "name": "Grok Build 0.2.87",
    "effort": "High"
  }
}
```

MiMo/Xiaomi aliases are no longer part of the active model policy for new workflows as of 2026-06-24. Old `contract.json` files may still contain historical `L1.0 MiMo AUTO` entries and should be treated as archived evidence, not as the current template.

## Runtime Rule

If a provider does not expose the exact requested model alias at runtime, the agent must not silently substitute a different model. It must record the mismatch in the handoff and either request revision, escalate, or use an explicitly approved fallback.

For `Gemini Vertex`, the required runtime is Google Vertex AI via ADC and `google-genai`; the current model is `gemini-2.5-flash`. For `Antigravity CLI AUTO`, the required runtime is `agy` itself. For `Grok Build 0.2.87`, the required runtime is the local `grok` CLI with completed auth, `grok-build` model access, project `.grok/config.toml` and SML tools exposed as `sml_*` aliases. If an exact `--model` is later requested and unavailable, that is a mismatch and must be recorded in the handoff.

