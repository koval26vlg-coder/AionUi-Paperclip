# 2026-07-02 17:25 +03 - Codex - Gemini Vertex limits and usage monitor

## Исходный запрос
Пользователь спросил, какие лимиты у Vertex AI с `gemini-2.5-flash` и как быстро команда их использует.

## Краткий план
- Сверить официальные Google Cloud лимиты и цены.
- Проверить локальный проект, регион и включенный Vertex API.
- Выполнить короткий live smoke для `usage_metadata`.
- Добавить локальный учет `Gemini Vertex` в монитор лимитов.

## Что сделано
- Подтвержден проект `project-4a65d058-0aed-49b3-8b8`, регион `us-central1`, включен `aiplatform.googleapis.com`.
- Подтвержден live вызов `gemini-2.5-flash` через Vertex ADC.
- `tools/gemini_vertex_workflow_review.py` теперь пишет usage-only JSONL без текста промпта и без секретов.
- `tools/agent_limit_monitor.py` теперь собирает `Gemini Vertex` как отдельного агента из `docs/agent-limits/gemini-vertex-usage.jsonl`.
- `docs/agent-limits/README.md` и `limits-config.json` обновлены под `Gemini Vertex`.

## Проверки
- `python -m pytest tools/sml/tests/test_agent_limit_monitor.py tools/sml/tests/test_gemini_vertex_workflow_review.py -q` -> 8 passed.
- `python -m py_compile tools/agent_limit_monitor.py tools/gemini_vertex_workflow_review.py` -> OK.
- `agent_limit_monitor.py --days 1 --no-write --json` показал `Gemini Vertex`: 1 request, 5 246 total tokens, 1 286 prompt, 808 candidates, 3 152 thoughts, estimated cost `$0.0102858`.

## Риски и ограничения
- Исторические Vertex вызовы до этого изменения не имели локального `usage_metadata` JSONL, поэтому exact total за прошлые workflow не восстановлен.
- Remaining/reset для Google Cloud throughput не является локальным счетчиком; монитор не должен придумывать остаток. Заполнять `limits-config.json` только по явному источнику.
- Стоимость считается оценочно по Standard PayGo для `gemini-2.5-flash`: input `$0.30/M`, cached input `$0.03/M`, output/reasoning `$2.50/M`.

## Следующий агент
Для проверки расхода запускать:

```powershell
D:\AionUi-Paperclip\.venv-sml\Scripts\python.exe D:\AionUi-Paperclip\tools\agent_limit_monitor.py --days 1 --no-write --json
```

Для точного учета новых L1/L2 workflow использовать `tools/gemini_vertex_workflow_review.py` без `--no-usage-log`.
