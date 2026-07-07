# Отчет агента

Дата: 2026-06-20 09:24 +03:00
Агент: Codex

## Исходный запрос пользователя

Пользователь потребовал обязательно найти и исправить проблему, из-за которой `Claude CLI` не находился, а `mimo`/`npm`/`agy` нестабильно определялись в разных PowerShell-вызовах.

## Краткий план

1. Найти корень нестабильного `PATH`.
2. Проверить реальные установки Claude Code, MiMo, Antigravity, Node.js и npm.
3. Добавить устойчивый слой запуска, который не зависит от сломанного process environment.
4. Обновить мониторинг и документацию.
5. Прогнать smoke-tests.

## Что было сделано

- Найден root cause: process-level `Path` в текущем Codex shell может быть `C:\Program Files\PowerShell\7;C:\Users\koval\bat;${PATH}`. Из-за literal `${PATH}` дочерние native-процессы не видят System32, Node.js и npm.
- Подтверждено, что Claude Code установлен и рабочий через абсолютный путь: `2.1.179 (Claude Code)`.
- Подтверждено, что MiMo установлен и рабочий: `0.1.1`.
- Подтверждено, что Antigravity CLI установлен и рабочий через `C:\Users\koval\AppData\Local\agy\bin\agy.exe`.
- Добавлен `tools/agent-cli-env.ps1` для нормализации `Path/PATH`.
- Добавлен `tools/install-agent-cli-shims.ps1` и установлены shims в `C:\Users\koval\bat`: `node.cmd`, `npm.cmd`, `npx.cmd`, `claude.cmd`, `mimo.cmd`, `agy.cmd`, `cmd.cmd`, `where.cmd`.
- Добавлен `tools/check-agent-runtimes.ps1`.
- Исправлен `tools/agent_limit_monitor.py`: subprocess теперь получает нормализованные `Path` и `PATH`, а MiMo fallback использует `mimo.cmd` вместо `mimo.ps1`.
- Исправлен `tools/antigravity_print.py`: `agy` ищется через стабильный PATH и запускается с нормализованным environment.

## Какие файлы были изменены

- `tools/agent-cli-env.ps1`
- `tools/install-agent-cli-shims.ps1`
- `tools/check-agent-runtimes.ps1`
- `tools/agent_limit_monitor.py`
- `tools/antigravity_print.py`
- `tools/sml/tests/test_agent_limit_monitor.py`
- `docs/current-context.md`
- `docs/tasks.md`
- `C:\Users\koval\bat\node.cmd`
- `C:\Users\koval\bat\npm.cmd`
- `C:\Users\koval\bat\npx.cmd`
- `C:\Users\koval\bat\claude.cmd`
- `C:\Users\koval\bat\mimo.cmd`
- `C:\Users\koval\bat\agy.cmd`
- `C:\Users\koval\bat\cmd.cmd`
- `C:\Users\koval\bat\where.cmd`

## Какие проверки выполнены

- `tools/check-agent-runtimes.ps1` проходит: `cmd`, `where`, `node`, `npm`, `claude`, `mimo`, `agy` найдены и запускаются.
- Искусственно сломанный `Path=C:\Program Files\PowerShell\7;C:\Users\koval\bat;${PATH}` все равно запускает `claude`, `mimo`, `agy`, `npm`, `node` через shims.
- `python -m py_compile tools/agent_limit_monitor.py tools/antigravity_print.py` проходит.
- `pytest tools/sml/tests/test_agent_limit_monitor.py tools/sml/tests/test_antigravity_print.py -q` -> `6 passed`.
- `agent_limit_monitor.py --days 1 --no-write --json` снова измеряет MiMo как `measured_cli`, без прежнего `OSError(193)`.

## Риски и ограничения

- Невозможно исправить process-level `Path` у уже запущенного родительского Codex desktop process из дочерней команды. Поэтому исправление сделано устойчивым wrapper/shim-слоем и нормализацией PATH внутри проектных скриптов.
- Если пользователь удалит `C:\Users\koval\bat` из пользовательского PATH или удалит shims, проблема может вернуться.

## Что должен проверить следующий агент

- Для любых headless workflow использовать `tools/check-agent-runtimes.ps1` при сомнении в окружении.
- Не делать вывод “Claude не установлен” только по неудачному `claude --version` без проверки shims и absolute path.
- При добавлении новых CLI в agent workflow добавлять их в `tools/agent-cli-env.ps1` и при необходимости в `tools/install-agent-cli-shims.ps1`.
