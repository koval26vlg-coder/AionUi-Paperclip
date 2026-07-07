# Agent Limits Monitor

Монитор лимитов и токенов хранит локальные снимки в этой папке.

## Источники

| Agent | Что измеряется | Источник | Остаток/reset |
| --- | --- | --- | --- |
| Codex | `tokens_used` по локальным thread records | `C:\Users\koval\.codex\state_5.sqlite` | Только если вручную заполнен `limits-config.json` |
| Gemini Vertex | `usage_metadata` по workflow-вызовам: input/output/thinking/total/cost estimate | `D:\AionUi-Paperclip\docs\agent-limits\gemini-vertex-usage.jsonl` | Throughput/cost quota в Google Cloud; локально только если вручную заполнен `limits-config.json` |
| Claude Code | `message.usage` из локальных JSONL | `C:\Users\koval\.claude\projects\**\*.jsonl` | Только если вручную заполнен `limits-config.json` |
| MiMo | tokens/cost/model usage | `mimo stats` | Только если вручную заполнен `limits-config.json` |
| Antigravity CLI | наличие conversation DB и quota refresh events | `C:\Users\koval\.gemini\antigravity-cli` | Numeric usage локально не найден |

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

- `limits-config.json` - ручные лимиты и reset timestamps. `null` означает "не угадывать".
- `latest.json` - последний machine-readable snapshot.
- `latest.md` - последний человекочитаемый отчет.

## Правило точности

Если provider/CLI не отдает usage, remaining или reset, монитор пишет `n/a`. Нельзя выводить остаток лимита по косвенным признакам без явного лимита в `limits-config.json`.
