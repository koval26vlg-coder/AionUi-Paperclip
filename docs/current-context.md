# Текущий контекст

Дата создания: 2026-05-10

## Природа проекта

`D:\AionUi-Paperclip` — самостоятельный проект. Его единственная цель — быть инфраструктурой общего контекста и памяти для AI-агентов (сейчас активны Grok Build, Antigravity CLI, Codex и Claude Code; Gemini Vertex сохранен как резервный профиль; будущие агенты могут быть добавлены позже).

Любые упоминания внешних репозиториев и прикладных задач (например, `C:\Users\koval\bat\bitrix24-automation` и его spec-ов вида `bitrix24-automation-hygiene`, `bitnewton-*`) — это работы, которые катятся через эту инфраструктуру, но не являются её частью. Код, тесты и артефакты таких внешних проектов живут в своих репозиториях; здесь остаются только spec-документы, журналы, решения и память о ходе работы.

Следующий агент не должен воспринимать bitrix24-automation или любой другой внешний проект как часть `D:\AionUi-Paperclip`.

Практическая граница:

- **Bitrix/Bit.Newton** — прикладной проект для анализа звонков, сделок, CRM-качества и отчетов. Рабочий код находится в `C:\Users\koval\bat\bitrix24-automation`.
- **Aion/SML** — инфраструктурный проект общей памяти агентов. Рабочая папка `D:\AionUi-Paperclip` содержит SML, документы контекста, agent-log и дашборд `apps/aion-vision`.
- **Aion Vision** показывает состояние общей памяти SML. Он может отображать записи о Bitrix как историю работы агентов, но не должен становиться интерфейсом Bitrix-аналитики.

## Рабочая схема

Актуальная рабочая связка:

- Codex
- Grok Build
- Antigravity CLI
- Claude Code
- Gemini Vertex как fallback profile `gemini-vertex`

По решению 2026-06-24 `MiMo AUTO` выведен из новых иерархических `docs/agent-workflows/`, потому что с 2026-06-25 он становится платным. Решение 2026-07-03 о default `antigravity` superseded решением пользователя от 2026-07-07: новые workflow стартуют с профиля `grok-antigravity` (`L1 Grok Build -> L2 Antigravity CLI -> L3 Codex -> L4 Codex -> L5 Claude Code`), а `Gemini Vertex` остается явным fallback-профилем. Старые workflow с `L1.0 MiMo AUTO`, прежним Antigravity default, временным Gemini default или `grok-gemini` остаются историческими артефактами и не являются текущим шаблоном.

Cursor и Kiro выведены из схемы 2026-06-18; Gemini CLI выведен и удален из активного runtime 2026-06-19 после успешного Antigravity smoke-test; проектный MiMo Code и `MiMo AUTO` также выведены из активной схемы. Историческая память об их работе сохранена в SML и `docs/agent-log/`, а ценные спецификации из `.kiro/specs/` перенесены в `docs/specs/`. Вернуть любой инструмент можно только по отдельному решению пользователя.

AionUi, Paperclip и Hermes больше не используются как основа текущей архитектуры.

Основной MCP-сервер памяти — **Shared_Memory_Layer (SML)** (`tools/sml/`). Старый `aion-file-memory` больше не является активным сервером памяти; он оставлен только как reference/legacy-код.

## Цель

Сделать так, чтобы разные агенты и модели работали в одной общей системе:

- знали запросы и результаты друг друга;
- могли оценивать работу друг друга;
- сохраняли общий контекст;
- фиксировали решения и задачи в документах;
- могли заменять друг друга при окончании подписки или лимитов;
- в будущем использовали общую MCP-память.

## Текущая структура

- Рабочая папка: `D:\AionUi-Paperclip`.
- `AGENTS.md` - единые правила для всех агентов.
- `CLAUDE.md` - проектные правила Claude Code.
- `.mcp.json` - проектное подключение SML для Claude Code и других MCP-клиентов, которые читают корневой MCP-конфиг.
- `.vscode/` - настройки и tasks для работы с общей памятью из VS Code.
- `docs/agent-log/` - журнал работы агентов.
- `docs/agent-workflows/` - иерархические workflow задач между Grok Build, Antigravity CLI, Codex, Claude Code, fallback Gemini Vertex и пользователем. Каждый workflow хранит `contract.json`, `brief.md`, `handoff.md`, `events.jsonl`, уровни `L1-L5` и финальный отчет. Старые workflow могут содержать исторические `L1.0/L1.1`, `MiMo AUTO`, прежний Antigravity default, временный Gemini Vertex default или `grok-gemini`, но это не текущий шаблон.
- `docs/decisions.md` - журнал решений.
- `docs/tasks.md` - список задач.
- `docs/memory/` - файловый источник истины для общей памяти.
- `docs/specs/` - спецификации проекта, в т.ч. ядра SML `agents-shared-memory-layer`.
- `docs/START-HERE.md` - первый файл для любого нового агента.
- `docs/agent-memory-bootstrap.md` - каноническое правило автоподхвата памяти из любой папки.
- `docs/context-index.md` - карта всех источников контекста.
- `docs/context-packs/` - собранные контекстные пакеты.
- `docs/relationship-maps.md` - стандарт построения карт связей и индекс текущих графов.
- `docs/relationship-maps/` - Markdown/JSON карты связей для SML, агентов, документов и инструментов.
- `docs/handoffs/` - передачи задач между агентами.
- `docs/agents.md` - реестр агентов.
- `docs/local-environment.md` - локальное окружение.
- `docs/vscode-sml.md` - роль VS Code как общей IDE-оболочки SML.
- `tools/sml/` - основной MCP-сервер Shared_Memory_Layer (CLI: `python -m tools.sml.core stats|ping|selfcheck`). Схема БД v2: FTS5-индекс `records_fts` даёт полнотекстовый фоллбэк семантического поиска, когда Ollama недоступна (`sml.semantic_query` отвечает `mode="text"`).
- `tools/aion_memory_mcp.py` - legacy/reference-сервер файловой памяти, не основной путь.
- `tools/watch-memory.ps1` - фоновый наблюдатель: context-pack, relationship-map, экспорт дашборда, бэкап БД и heartbeat (`logs/memory-auto.heartbeat`).
- `tools/status-memory-auto.ps1` - статус автоматизации, включая проверку свежести heartbeat.
- `tools/normalize-sml-authors.py` - нормализация имён агентов в SML.
- `tools/backup-sml.py` - бэкап БД SML с ротацией и `--verify` (integrity + сверка записей).
- `.github/workflows/ci.yml` - CI: selfcheck + pytest ядра SML на push/PR.
- `apps/aion-vision/` - дашборд SML: живые данные через `/api/sml-dashboard` и поиск по памяти `/api/search` (`scripts/search-sml.py`, семантика + FTS5-фоллбэк). Панели «Здоровье системы» (watcher/поиск/бэкап) и «Аналитика памяти» (тренды по неделям, разбивка по агентам/типам). Dev: `START-AION-VISION.cmd` (vite middleware). Прод: `START-AION-VISION-SERVE.cmd` → `scripts/serve-sml.py` (stdlib HTTP-сервис, отдаёт `dist/` + API без dev-сервера).
- `apps/aion-vision/#hh-booster` - операторский экран HH Resume Booster validation test на 14 дней. Публичная форма `#hh-booster-public` принимает `channel` и `offer` query-параметры, например `#hh-booster-public?channel=Telegram&offer=response`, чтобы честно добирать per-offer coverage по avatar/audit/response.
- `docs/HOW-TO-USE.md` - гайд для новичка: запуск агентов и панели, поиск по памяти, обслуживание, troubleshooting.
- Ollama опциональна: без неё поиск работает в режиме FTS5 (по словам); семантика — только при запущенной Ollama.
- `docs/memory-automation.md` - описание автоматизации памяти.
- `docs/memory-autoprotocol.md` - правило автоматического поиска похожего контекста перед задачей.
- `tools/agent-memory-bootstrap.ps1` - абсолютный bootstrap памяти: статус watcher, relationship-map query и excerpt context-pack из любой текущей папки.
- `tools/agent_workflow.py` - CLI иерархических workflow задач: `new`, `claim`, `submit-work`, `approve-level`, `request-revision`, `escalate`, `approve-risk`, `finalize`, `status`.
- `tools/start-agent-swarm.ps1` и `START-AGENT-SWARM.cmd` - короткий запускатель роя: создает новый `docs/agent-workflows/<workflow-id>/`, выполняет Aion SML bootstrap, печатает status/monitor команды и по умолчанию стартует с `Grok Build L1` (`-Profile grok-antigravity`); `Antigravity CLI` доступен через `-Profile antigravity`, `Gemini Vertex` через `-Profile gemini-vertex`, legacy Grok->Gemini через `-Profile grok-gemini`.
- `tools/watch-agent-workflows.ps1` - видимый монитор workflow; показывает текущий уровень, разрешенного следующего агента, возраст ожидания, handoff, blockers и risk gate.
- `tools/agent_limit_monitor.py` - локальный монитор расхода агентов: Codex tokens из `C:\Users\koval\.codex\state_5.sqlite`, Claude Code usage из `C:\Users\koval\.claude\projects\**\*.jsonl`, Antigravity quota/log status без numeric usage. MiMo больше не собирается в дефолтном мониторинге. Снимки пишутся в `docs/agent-limits/latest.md` и `latest.json`.
- `tools/watch-agent-limits.ps1` - видимый монитор лимитов/токенов; для фонового наблюдения создан heartbeat automation `automation-7` "Лимиты агентов" раз в 6 часов.
- `LOAD-SML-MEMORY.cmd` - ручной запуск того же bootstrap для проверки.

## Автоматизация

Фоновый наблюдатель памяти установлен в Windows Task Scheduler.

Имя задачи:

```text
Aion File Memory Auto
```

Назначение: автоматически пересобирать `docs/context-packs/context-pack-latest.md` при изменениях в общей базе.

## Выведенные инструменты

Cursor, Kiro, Gemini CLI, проектный MiMo Code и `MiMo AUTO` выведены из схемы. Их активные конфиги (`.cursor/`, `.kiro/`, `.mimocode/`, `.gemini/`) и запускатели (`OPEN-KIRO-RU.cmd`, `OPEN-MIMO-SML.cmd`, `CHECK-MIMO-SML.cmd`, `OPEN-GEMINI-SML.cmd`, `CHECK-GEMINI-SML.cmd`) удалены, чтобы не создавать путаницу в активной схеме Grok Build + Antigravity CLI + Codex + Claude Code.

Решение 2026-06-24: прежнее исключение `MiMo AUTO L1.0` отменено. Новые workflow не запускают MiMo, не чинят MiMo runtime и не вызывают `mimo stats` в дефолтном мониторинге лимитов.

Сохранено:

- историческая память об их работе — записи в SML и `docs/agent-log/`;
- ценные спецификации из бывшего `.kiro/specs/` перенесены в `docs/specs/` (в т.ч. спецификация ядра SML `agents-shared-memory-layer`, на которую ссылается `tools/sml/__init__.py`).

Вернуть любой из этих инструментов можно только по отдельному решению пользователя.

## Gemini CLI

Gemini CLI удален из активного runtime 2026-06-19. Удалены глобальные npm-пакеты `@google/gemini-cli` и `codex-gemini-helper`, shims `gemini`/`ask-gemini`, проектная `.gemini/`, `GEMINI.md`, Gemini launchers, `docs/gemini-sml.md`, `docs/cursor-gemini-model.md` и старый каталог `D:\Gemini`. Root-файлы `C:\Users\koval\.gemini` удалены точечно; `C:\Users\koval\.gemini\antigravity-cli` сохранен, потому что используется Antigravity.

## Antigravity

Antigravity найден как установленный локальный инструмент и был принят как замена Gemini CLI в уровнях `L1` и `L2`. После временного отката на Gemini Vertex из-за регионального blocker, свежий smoke 2026-07-03 подтвердил локальный доступ: `antigravity_print.py` вернул `OK`, а `antigravity_workflow_review.py` дал валидный L1 handoff с `approve` на временном workflow. По решению пользователя от 2026-07-07 Antigravity является дефолтным `L2` после Grok Build и явным `L1/L2` профилем `antigravity`, а Gemini Vertex остается fallback.

Проверено 2026-06-19:

- приложение: `C:\Users\koval\AppData\Local\Programs\Antigravity\Antigravity.exe`;
- приложение запущено видимо для ручной авторизации пользователя;
- CLI: `C:\Users\koval\AppData\Local\agy\bin\agy.exe`;
- версия CLI: `1.0.10`;
- выполнено `agy install`, путь `C:\Users\koval\AppData\Local\agy\bin` настроен в пользовательском PATH;
- `agy --help` показывает headless-режимы `--print`, `--model`, `--prompt-interactive`, подкоманды `models`, `plugin`, `update`.
- live smoke-test `agy --print "Return exactly OK."` прошел на уровне авторизации/model call: в логе есть keyring auth и `streamGenerateContent`, в conversation DB найден ответ `OK`.
- добавлен wrapper `tools/antigravity_print.py`: он запускает raw `agy --print`, печатает stdout если он есть, а при пустом stdout восстанавливает свежий ответ из `C:\Users\koval\.gemini\antigravity-cli\conversations\*.db`.

Ограничение: raw `agy --print` все еще может завершаться с кодом 0 без stdout. Для headless workflow использовать `D:\AionUi-Paperclip\.venv-sml\Scripts\python.exe D:\AionUi-Paperclip\tools\antigravity_print.py "<prompt>"`.

Оперативный статус 2026-06-29 16:57 +03 был: живой Antigravity model call временно блокировался `FAILED_PRECONDITION (code 400): User location is not supported for the API use`. Проверялись process-level `HTTP_PROXY/HTTPS_PROXY` через локальный Happ/Xray Frankfurt `127.0.0.1:10809`, `CLOUD_CODE_URL=https://cloudcode-pa.googleapis.com`, `useG1Credits=true`, downgrade до `Gemini 3.5 Flash (Medium)`. Этот blocker считать историческим после успешного локального smoke 2026-07-03; если он повторится, переключать конкретный workflow на fallback `gemini-vertex`.

NOI workaround 2026-06-29 17:15 +03: на SSH host `root@147.90.11.165` установлен Antigravity CLI `agy 1.0.13` в `/root/.local/bin/agy`; сервер Ubuntu 22.04 x86_64, внешний маршрут `United States` по `ifconfig.co`. Установка завершена, но live-вызов еще не подтвержден: fresh headless `agy --print` завис без auth, интерактивный `agy` печатает OAuth URL и ждет вход около 30 секунд. Пользователь должен завершить OAuth в видимом запускателе `work/start-antigravity-noi-auth.ps1`, затем обязателен smoke через SSH. До этого NOI не считать готовым Antigravity runtime.

Статус NOI 2026-06-30 11:38 +03: повторный OAuth не завершен. Прямой SSH к `147.90.11.165:22` теперь устанавливает TCP, но не получает SSH banner (`Connection timed out during banner exchange`); ICMP жив. Попытка использовать сохраненный Xray/VLESS REALITY на `147.90.11.165:443` как локальный proxy также не дала egress: TCP/TLS на 443 открывается, но VLESS proxy-запросы зависают. До reboot/console-восстановления VPS не планировать OAuth/smoke на NOI.

Повтор 2026-06-30 14:10 +03: локальный `agy` обновлен до `1.0.14`, но direct smoke и smoke через живой Frankfurt proxy `127.0.0.1:10809` снова дошли до `FAILED_PRECONDITION (code 400): User location is not supported for the API use`. SSH к NOI остается заблокирован на banner exchange: TCP connected, SSH banner не читается; порты `22`, `2222`, `443`, `2022`, `2200` не дали SSH. Xray/REALITY helper к NOI принял `ifconfig.co:443`, но ушел в timeout. Добавлены постоянные helper-скрипты `tools/check-antigravity-noi.ps1` и `tools/start-antigravity-noi-auth.ps1`; после reboot/console recovery VPS выполнить `check-antigravity-noi.ps1`, затем OAuth helper и `check-antigravity-noi.ps1 -Smoke`.

После пользовательского reboot 2026-06-30 16:30 +03 `tools/check-antigravity-noi.ps1` снова показал `TCP: connected` и `SSH banner: read failed`. Обычный reboot не восстановил SSH. Следующий шаг - console/rescue recovery в панели VPS: проверить, загружена ли ОС, работает ли `sshd`, что слушает порт 22, и нет ли firewall/iptables правила, которое принимает TCP и не отдает SSH banner.

Проверка HAPP 2026-06-30 17:15 +03: после переключения пользователем профиля оба локальных proxy `127.0.0.1:10808` и `127.0.0.1:10809` показывали egress `United States / Los Angeles / 24SHELLS` (`192.241.126.174`). Повторный локальный OAuth Antigravity через `HTTP_PROXY/HTTPS_PROXY=http://127.0.0.1:10809` восстановил вход как `koval26vlg@gmail.com`, но тогда model-call smoke завершался `FAILED_PRECONDITION`. Этот статус устарел после локального успешного smoke 2026-07-03; Antigravity теперь дефолтный L2 runtime, но требует fallback `gemini-vertex` при повторном runtime-blocker.

Решение 2026-07-02: не пытаться маскировать регион в Antigravity как основной путь, временно был введен default profile `gemini-vertex` через Google Vertex AI, ADC и модель `gemini-2.5-flash`. Это решение superseded решением пользователя 2026-07-03 про `antigravity`, а затем решением 2026-07-07: дефолтный `Рой` использует `grok-antigravity`, `gemini-vertex` остается запасным путем.

Дополнительная проверка 2026-06-19 на workflow авиабилетов VOG -> MNL показала, что Antigravity CLI в обычном `--print` режиме может самостоятельно менять файлы workflow и продвигать state. Повтор 2026-06-20 на drift-dashboard подтвердил риск: даже при просьбе не писать файлы Antigravity прочитал `AGENTS.md`, записал L1.1/L2 handoff и сам вызвал `agent_workflow.py`.

Исправление 2026-06-20:

- `Antigravity CLI` теперь считается review-only участником для workflow state mutations;
- `Gemini Vertex` также считается review-only участником для workflow state mutations;
- `Grok Build` также считается review-only участником для workflow state mutations;
- добавлен `tools/gemini_vertex_workflow_review.py`: runner собирает packet из `brief.md`, `contract.json`, последнего `handoff.md` и `events.jsonl`, отправляет его в Vertex Gemini и валидирует обязательные handoff headings;
- добавлен `tools/antigravity_workflow_review.py`: runner собирает packet из `brief.md`, `contract.json`, последнего `handoff.md` и `events.jsonl`, запускает Antigravity из isolated cwd вне workspace, проверяет, что workflow tree не изменился, и валидирует обязательные handoff headings;
- `tools/grok_build_workflow_review.py` запускает `grok-build` через isolated prompt-file packet, валидирует обязательные handoff headings и передает `SML_MCP_TOOL_NAME_MODE=grok-safe`, чтобы Grok видел SML как `sml_*`;
- `tools/agent_workflow.py` блокирует mutating commands от `--agent "Gemini Vertex"`, `--agent "Antigravity CLI"` и `--agent "Grok Build"` без доверенного `--executor Codex` или `--executor "Claude Code"`;
- для L1/L2 нужно получать текст через isolated runner, затем Codex выполняет `claim/submit-work/approve-level --agent "Grok Build" --executor Codex` на L1 и `--agent "Antigravity CLI" --executor Codex` на L2; для fallback `--profile gemini-vertex` используется аналогичный command с `--agent "Gemini Vertex"`.

## Grok Build

Grok Build 0.2.87 подключен 2026-07-06 как подтвержденный runtime. По решению пользователя 2026-07-07 он является дефолтным L1 профиля `grok-antigravity`: `L1 Grok Build -> L2 Antigravity CLI -> L3 Codex -> L4 Codex -> L5 Claude Code`. Старый `grok-gemini` оставлен как явный legacy-профиль.

Проверено:

- `@xai-official/grok@0.2.87` установлен через npm, `grok version` вернул `grok 0.2.87`;
- auth через `grok.com` завершен, `grok models` показывает `grok-composer-2.5-fast` и `grok-build`;
- проектный MCP `sml` добавлен в `D:\AionUi-Paperclip\.grok\config.toml`;
- SML MCP для Grok работает в режиме `SML_MCP_TOOL_NAME_MODE=grok-safe`, поэтому инструменты доступны как `sml_ping`, `sml_startup_pack`, `sml_semantic_query` и т.д.;
- `grok --model grok-build -p ...` вернул `OK`;
- `sml_ping` через Grok вернул `ok=true`, `version sml-0.1.0`, `degraded=false`;
- smoke workflow `2026-07-06-225247-147230-smoke-grok-gemini` создан через `-Profile grok-gemini`, Grok L1 runner сформировал валидный русский handoff, а `submit-work --agent "Grok Build" --executor Codex` перевел workflow в `waiting_for_approval` с `allowed_next_agents=["Gemini Vertex"]`. Для новых workflow default теперь `grok-antigravity`, поэтому после L1 Grok ожидается `allowed_next_agents=["Antigravity CLI"]`.

Ограничение: `grok mcp doctor` может возвращать общий exit code 1 из-за внешних GitHub/Mobbin MCP из совместимых глобальных конфигов. Это не блокирует SML: строка `sml` показывает handshake OK и 10 tools discovered.

`agy --sandbox --print` в локальной проверке завершался без полезного stdout/ответа, поэтому sandbox-флаг не считается достаточным контролем. Контроль теперь строится на изоляции cwd, отсутствии workspace paths в prompt, post-run snapshot check и запрете self-mutation в `agent_workflow.py`.

## Agent CLI runtime PATH

2026-06-20 найден корень нестабильного запуска агентских CLI из Codex shell: process-level `Path` иногда приходил как `C:\Program Files\PowerShell\7;C:\Users\koval\bat;${PATH}`. Из-за literal `${PATH}` дочерние native-процессы (`cmd`, `node`, `npm`) не видели системные каталоги, хотя PowerShell мог показывать расширенный `$env:Path`.

Исправление:

- добавлен `tools/agent-cli-env.ps1` с `Repair-AgentCliPath`, который собирает стабильный `Path/PATH` из System32, Windows, `C:\Users\koval\bat`, Node.js, npm, Antigravity и Git;
- добавлен `tools/install-agent-cli-shims.ps1`;
- добавлен `tools/check-agent-runtimes.ps1`;
- установлены user-level shims в `C:\Users\koval\bat`: `node.cmd`, `npm.cmd`, `npx.cmd`, `claude.cmd`, `agy.cmd`, `cmd.cmd`, `where.cmd`; `mimo.cmd` удален 2026-06-24 вместе с выводом MiMo из схемы;
- `tools/agent_limit_monitor.py` и `tools/antigravity_print.py` теперь нормализуют `Path` и `PATH` для subprocess. MiMo не используется в новых workflow и дефолтном лимит-мониторе.

Проверено 2026-06-20:

- `tools/check-agent-runtimes.ps1` видит `node`, `npm`, `claude`, `agy` и больше не проверяет `mimo`;
- `claude --version` -> `2.1.179 (Claude Code)`;
- глобальный npm-пакет `@mimo-ai/cli` удален 2026-06-24; `mimo` больше не резолвится в текущем PATH;
- `npm --version` -> `10.9.7`;
- `node --version` -> `v22.22.2`;
- `agy --help` доступен;
- в искусственно сломанном `Path=C:\Program Files\PowerShell\7;C:\Users\koval\bat;${PATH}` агентские команды все равно запускаются через shims.

## Spec Kit и Task Master

2026-06-20 добавлен осторожный tooling-слой для работы с кодом:

- GitHub Spec Kit установлен как `C:\Users\koval\.local\bin\specify.exe`, закреплен на `github/spec-kit@v0.9.5`; floating `main` был проверен и отвергнут, потому что `specify --help` падал с `ModuleNotFoundError: specify_cli.bundler.lib`.
- Созданы skills `spec-kit` в `C:\Users\koval\.codex\skills`, `C:\Users\koval\.claude\skills` и shared `agent-skills`.
- Task Master установлен как CLI `task-master` версии `0.43.1`; global MCP не подключен, чтобы не грузить тяжелый набор инструментов во все сессии.
- Созданы skills `task-master-pilot`; MCP для Task Master включать только по отдельному решению пользователя, начиная с reduced mode `TASK_MASTER_TOOLS=core`.
- Cloud Code Router не установлен, потому что это proxy/router для моделей, а не skill/MCP, и он добавляет риск ключей/логов/совместимости без явной необходимости.

2026-06-20 уточнение по MCP/auth:

- Task Master MCP проверен и отсутствует в активных Codex/Claude/Cursor MCP-конфигах; оставлен только CLI `task-master`.
- Snyk CLI установлен глобально как `snyk` версии `1.1305.1`.
- Snyk MCP в Codex, Claude Code и Cursor переведен с `npx snyk@latest` на локальный `C:\Users\koval\AppData\Roaming\npm\snyk.cmd mcp -t stdio`.
- Добавлены helper scripts `agent-skills/scripts/setup-github-snyk-auth.ps1` и `agent-skills/scripts/verify-github-snyk-mcp.ps1`.
- GitHub MCP ожидает user-level `GITHUB_PERSONAL_ACCESS_TOKEN`; Claude official GitHub plugin также использует `${GITHUB_PERSONAL_ACCESS_TOKEN}` в Authorization header.
- Секреты не хранятся в docs/манифестах/MCP JSON. После ввода GitHub/Snyk auth нужно перезапустить Codex/Claude Code/Cursor и запустить verify script.
- После пользовательского ввода GitHub PAT и Snyk OAuth проверено: GitHub API token работает для `koval26vlg-coder`, Claude GitHub MCP `Connected`, Claude Snyk MCP `Connected`, Task Master MCP references отсутствуют.
- Финальная корректировка: Claude `snyk-security` переведен в top-level user-scope `mcpServers`; project-scope дубликат из папки установки skills удален. Проверено из `C:\Users\koval` и из папки установки skills: GitHub, Context7, Playwright, SML и Snyk `Connected`.
- Security hygiene: example GitHub-token-like strings в локальных `claude-api` skill docs нейтрализованы; повторный secret-pattern scan по skills, Aion docs и активным MCP-конфигам показал отсутствие GitHub/Snyk token-like patterns. Активные MCP-конфиги также чистые от `serena`, `task-master*` и старого Snyk npx command.


## Claude Code

Claude Code — активный агент рядом с Grok Build, Antigravity CLI и Codex; Gemini Vertex остается fallback profile `gemini-vertex`.

Подготовлено:

- `CLAUDE.md` - правила Claude Code для русского языка, SML, relationship-map и журналирования;
- `.mcp.json` - проектный MCP-конфиг с сервером `sml`;
- `C:\Users\koval\.claude\CLAUDE.md` - глобальные правила Claude Code для автоподхвата SML из любой папки;
- user-scope MCP `sml` в Claude Code добавлен командой `claude mcp add --scope user ...`;
- `OPEN-CLAUDE-SML.cmd` - запуск Claude из рабочей папки;
- `CHECK-CLAUDE-SML.cmd` - базовая проверка auth/MCP после установки CLI.

Проверено:

- Claude Code установлен: `2.1.179`, авторизован, работает из `D:\AionUi-Paperclip`;
- `claude mcp list` показывает `sml` как `Connected`;
- 2026-06-19 дефолтная модель Claude Code исправлена с недоступного проектного `fable` на проверенный `sonnet`; `claude -p "Return exactly OK."` возвращает `OK`;
- 2026-06-18 `claude mcp list` из внешней папки `C:\Users\koval\Documents\Bitrix24` тоже показывает `sml` как `Connected`;
- 2026-06-18 Claude Code выполнил содержательную работу (аудит проекта + правки P0/P1/P2/P3) и записал отчёт в `docs/agent-log/` — живой рабочий цикл подтверждён.

Важно: Claude Code теперь имеет и проектное, и пользовательское подключение SML. Поэтому локальный Claude Code может подтягивать память из любой папки, если читает глобальные правила и выполняет bootstrap. Claude web, Claude Desktop projects/chats и OpenClaude/Cowork-сессии сами по себе не получают локальный SML-контекст автоматически.

Минимальное правило для Claude Code:

1. прочитать `C:\Users\koval\.claude\CLAUDE.md` или проектный `CLAUDE.md`;
2. выполнить `D:\AionUi-Paperclip\tools\agent-memory-bootstrap.ps1`;
3. использовать подключенный MCP-сервер `sml`, если он доступен;
4. фиксировать итог в `docs/agent-log/`.

Если Claude говорит, что видит только локальные Cowork-сессии и не имеет доступа к проектам/чатам Claude, значит используется не наш локальный Claude Code-контур SML, а отдельная оболочка.

## VS Code

VS Code добавлен в общий контекст как рабочая IDE-оболочка, а не как отдельный агент. Он нужен, чтобы открывать `D:\AionUi-Paperclip`, держать рядом правила агентов, context-pack, SML-скрипты, журнал и терминалы Codex/Claude/Antigravity.

Подготовлено:

- `.vscode/settings.json` - настройки рабочей папки, UTF-8 и исключения тяжелых каталогов;
- `.vscode/tasks.json` - задачи для проверки памяти, пересборки context-pack, пересборки relationship-map, поиска по карте и проверки Claude MCP;
- `OPEN-VSCODE-SML.cmd` - запуск VS Code в рабочей папке;
- `CHECK-VSCODE-SML.cmd` - проверка VS Code, общей памяти и Claude MCP;
- `docs/vscode-sml.md` - инструкция по роли VS Code.

Проверено: `Code.exe` найден по пути `C:\Users\koval\AppData\Local\Programs\Microsoft VS Code\Code.exe`, версия VS Code `1.124.2`, но команда `code` не найдена в PATH текущей PowerShell-сессии. Поэтому запускатели используют прямой путь к `Code.exe`.

## Поведение агентов по умолчанию

Агенты больше не должны ждать отдельной команды "посмотри в память".

Для сложных задач по умолчанию используется иерархическая схема отделов:

1. `L1` Grok Build - SML bootstrap, первичная постановка задачи, разведка контекста и итоговый L1-handoff.
2. `L2` Antigravity CLI - инженерная проверка L1, ограничения, edge cases и gate ревизии.
3. `L3` Codex - декомпозиция реализации, тесты и automation.
4. `L4` Codex - архитектурный синтез, contract audit, risk gate и сопровождение.
5. `L5` Claude Code - независимая финальная техническая проверка и `final-report.md` для пользователя.

Агент может продолжать workflow только если `contract.json.allowed_next_agents` содержит его точное имя. Каждый уровень пишет стандартный handoff, а несогласие фиксируется через `disagreement.md`, чтобы не создавать "испорченный телефон".

Модельная политика субагентов закреплена в `docs/agent-workflows/model-policy.md` и попадает в `contract.json` новых workflow. Модель нельзя тихо подменять: если провайдер/CLI не поддерживает указанный alias, следующий агент фиксирует mismatch в handoff и запрашивает approved fallback.

Перед любой содержательной задачей агент сам:

1. определяет тему запроса;
2. запускает абсолютный bootstrap:

```powershell
& "D:\AionUi-Paperclip\tools\agent-memory-bootstrap.ps1" -Agent "<имя агента>" -Query "<тема>"
```

3. вызывает `sml.startup_pack`;
4. ищет похожее через `sml.semantic_query`;
5. если SML недоступен, ищет по `docs/context-packs/context-pack-latest.md` и `docs/`;
6. учитывает найденное перед ответом или действием.

## Карты связей

Для построения и обновления карт связей добавлен постоянный Codex skill:

```text
C:\Users\koval\.codex\skills\relationship-map-builder
```

Текущая карта по Graphify/SML/Codex/Gemini находится в:

```text
docs/relationship-maps/graphify-sml-relationship-map.md
docs/relationship-maps/graphify-sml-relationship-map.json
```

Карты связей являются автоматическим производным слоем над SML и документами. Watcher памяти пересобирает их вместе с context-pack, а агенты используют `tools/query-relationship-map.py "<тема>"` как быстрый навигатор перед широким поиском по файлам. Этот слой помогает видеть центральные узлы и мосты, но не заменяет SML как основную память.


## Историческая хроника вынесена

Датированные хроники workflow (Drift Workflow Control, sports betting, HH Resume Booster)
и записи об установке инструментов/скиллов перенесены в
docs/history/current-context-chronicle-2026-06-07.md, чтобы не раздувать живой контекст.
Актуальная архитектура описана в разделах выше и в docs/decisions.md.
