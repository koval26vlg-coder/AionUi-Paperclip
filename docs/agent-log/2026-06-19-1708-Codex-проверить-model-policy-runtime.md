# 2026-06-19 17:08 - Codex - проверить model policy runtime

## Исходный запрос пользователя

Пользователь попросил проверить закрепленную model policy для субагентов workflow.

## Что проверено

- Создан временный workflow через `tools/agent_workflow.py`.
- `status` показывает текущих субагентов `L1.0` с моделью `MiMo AUTO / AUTO / Xiaomi API AUTO`.
- Полная матрица `schema.example.json` проверена скриптом: 23 субагента, нет missing/extra/mismatch.
- `tools/sml/tests/test_agent_workflow.py` прошел: 7 passed.
- MiMo runtime проверен через `mimo models`: доступен `mimo/mimo-auto` и модели `xiaomi/mimo-v2-*`.
- `mimo providers list`: есть Xiaomi API credential.
- `ask-gemini.cmd` найден вместо `gemini.cmd`; helper поддерживает `--model`, default `gemini-3.5-flash`, но локальные `.env`/env с `GEMINI_API_KEY` или `GOOGLE_API_KEY` не найдены.
- `codex.cmd` найден, `codex exec` поддерживает `--model` и `-c model=...`; текущий default в `C:\Users\koval\.codex\config.toml` отличается от policy и равен `gpt-5.4-mini`.
- `claude.cmd` найден, поддерживает `--model` и `--effort`; текущий default в `C:\Users\koval\.claude\settings.json` равен `haiku`, effort `xhigh`.

## Вывод

Документальная и contract-часть model policy работает. Runtime-слой пока не исполняет субагентов автоматически по их моделям: нужен отдельный runner/wrapper, который читает `contract.json`, выбирает `subagent.model`, нормализует alias в CLI runtime id и запускает нужный инструмент с `--model`/`-m`/`--effort`.

## Риски

- Gemini официальный `gemini.cmd` отсутствует, доступен только `ask-gemini.cmd`.
- Gemini helper не сможет выполнить live check без `GEMINI_API_KEY` или `GOOGLE_API_KEY`.
- Codex/Claude CLI принимают model flags, но фактическая доступность aliases вроде `codex-5.3`, `gpt-5.5`, `Claude Opus 4.8 alias` не проверялась live, чтобы не тратить лимиты без отдельного подтверждения.
- MiMo model policy лучше исполнять через runtime id `mimo/mimo-auto`, а не человекочитаемую метку `MiMo AUTO`.

## Следующий шаг

Реализовать `agent_model_runner`/`model_runtime_map`, который переводит policy labels в реальные CLI flags и делает сначала dry-run validation, затем optional live ping по явному подтверждению пользователя.
