# Agent Limits Monitor

Монитор расхода токенов хранит локальные снимки в этой папке. Он показывает только
фактически измеренный локальный расход; ручное отслеживание остатка/reset убрано
2026-07-07, потому что провайдеры не отдают эти значения локально (см. «Правило точности»).

## Источники

| Agent | Что измеряется | Источник |
| --- | --- | --- |
| Codex | `tokens_used` по локальным thread records | `C:\Users\koval\.codex\state_5.sqlite` |
| Gemini Vertex | `usage_metadata` по workflow-вызовам: input/output/thinking/total/cost estimate | `D:\AionUi-Paperclip\docs\agent-limits\gemini-vertex-usage.jsonl` |
| Claude Code | `message.usage` из локальных JSONL | `C:\Users\koval\.claude\projects\**\*.jsonl` |
| Antigravity CLI | наличие conversation DB и quota refresh events | `C:\Users\koval\.gemini\antigravity-cli` |

## Команды

Разовый снимок:

```powershell
D:\AionUi-Paperclip\.venv-sml\Scripts\python.exe D:\AionUi-Paperclip\tools\agent_limit_monitor.py --days 7
```

Видимый монитор:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File D:\AionUi-Paperclip\tools\watch-agent-limits.ps1 -IntervalSec 900
```

Разово через monitor wrapper:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File D:\AionUi-Paperclip\tools\watch-agent-limits.ps1 -Once
```

## Файлы

- `latest.json` - последний machine-readable snapshot.
- `latest.md` - последний человекочитаемый отчет.

## Правило точности

Если provider/CLI не отдает usage, монитор пишет `n/a`. Остаток лимита по косвенным признакам не выводится — ручное отслеживание лимитов не ведется, потому что провайдеры не раскрывают remaining/reset локально.
