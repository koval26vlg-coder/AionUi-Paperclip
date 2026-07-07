# Отчет агента

## Дата и время

2026-06-19 17:20:00 +03:00

## Агент

Codex

## Исходный запрос пользователя

Восстановить официальный `gemini` CLI.

## Контекст перед началом

В workflow Gemini CLI используется на уровнях `L1.1` и `L2`. До проверки команда `gemini` в PATH не находилась, был доступен только helper `ask-gemini`, без `GEMINI_API_KEY`/`GOOGLE_API_KEY`.

## План

1. Проверить память Aion и active-run gate.
2. Подтвердить официальный npm-пакет Gemini CLI.
3. Установить официальный CLI.
4. Проверить бинарь, версию, MCP `sml` и live headless prompt.
5. Зафиксировать состояние в документах.

## Что сделано

- Через Context7 и npm подтвержден официальный пакет `@google/gemini-cli`.
- Выполнена установка `npm install -g @google/gemini-cli`.
- Команда `gemini` восстановлена в `C:\Users\koval\AppData\Roaming\npm`.
- Проверена версия `gemini --version`: `0.47.0`.
- Проверен npm global пакет: `@google/gemini-cli@0.47.0`.
- Проверен MCP: `gemini mcp list` показывает `sml` как `Connected`.
- Выполнен минимальный live-тест `gemini --skip-trust --prompt "Return exactly OK." --output-format json`.

## Измененные файлы

- `docs/current-context.md`
- `docs/gemini-sml.md`
- `docs/local-environment.md`
- `docs/tasks.md`
- `docs/agent-log/2026-06-19-1720-Codex-восстановить-официальный-Gemini-CLI.md`

## Проверки

- `node --version` -> `v22.22.2`
- `npm --version` -> `11.13.0`
- `npm view @google/gemini-cli ...` -> `0.47.0`
- `gemini --version` -> `0.47.0`
- `npm list -g @google/gemini-cli --depth=0` -> установлен `@google/gemini-cli@0.47.0`
- `gemini mcp list` -> `sml ... Connected`

## Решения

Официальный CLI восстановлен через `@google/gemini-cli`. Helper `ask-gemini` оставлен как отдельный инструмент и не удалялся.

## Риски и ограничения

Live model call сейчас не проходит из-за авторизации: Google login падает с `IneligibleTierError` / `UNSUPPORTED_LOCATION` для `Gemini Code Assist for individuals`. Для реальных L1.1/L2-прогонов нужно настроить `GEMINI_API_KEY`, `GOOGLE_API_KEY`/Vertex AI или другой доступный способ авторизации.

Активный trading gate остается `RUNNING`; работы по Gemini CLI не запускали trading postprocess, collectors или инженерные шаги по `trading_mvp`.

## Что должен проверить следующий агент

После настройки ключа или Vertex AI выполнить короткий live smoke-test Gemini CLI и затем проверить один workflow-проход уровня `L1.1`/`L2` без тихой подмены model aliases из `docs/agent-workflows/model-policy.md`.
