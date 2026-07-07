# Журнал решений

## 2026-06-20 - Spec Kit и Task Master добавлены как осторожный agent-tooling слой

### Контекст

Пользователь попросил перейти от оценки полезности Context7, Playwright MCP, Spec Kit, Task Master и Cloud Code Router к практической установке рекомендованного набора.

### Решение

Spec Kit установлен как `specify` и закреплен на релизе `github/spec-kit@v0.9.5`, потому что floating `main` установился как `0.11.4.dev0`, но падал на `specify --help` из-за отсутствующего `specify_cli.bundler.lib`. Для Codex, Claude Code и shared `agent-skills` созданы skills `spec-kit`.

Task Master установлен как глобальный CLI `task-master` версии `0.43.1`, но не подключен как глобальный MCP. Для него созданы skills `task-master-pilot`, которые требуют включать MCP только по отдельной команде и начинать с reduced mode `TASK_MASTER_TOOLS=core`.

Cloud Code Router не устанавливался: это не skill/MCP, а прокси маршрутизации моделей, который добавляет риск ключей, логов, несовместимости инструментов и не нужен без явного давления по стоимости/лимитам.

### Последствие

Текущая активная связка остается `Codex + Claude Code + Antigravity CLI`. Context7 и Playwright MCP остаются базовыми усилителями качества кода/фронтенда; Spec Kit становится стандартным способом превращать размытую задачу в spec/plan/tasks; Task Master используется только для больших проектов с явным persistent task graph.

### Автор: Codex
### Теги: agent-tooling, spec-kit, task-master, mcp, codex, claude-code

## 2026-05-10 - Базовая архитектура

Решение: использовать Codex, Cursor и Kiro как три основных агента.

Роли:

- Codex - инженерная реализация, анализ, тесты, ревью.
- Cursor - IDE-агент, быстрые правки, навигация, второе мнение.
- Kiro - specs, планирование, требования, архитектурная декомпозиция.

Причина: такая схема проще и чище, чем поддерживать дополнительный хаб в виде Hermes, AionUi или Paperclip.

Последствие: общий контекст должен храниться в проектных файлах и общей MCP-памяти, а не в отдельном чате одного агента.

## 2026-05-10 - Источник истины

Решение: считать источником истины файлы `AGENTS.md` и `docs/`.

Причина: чат конкретного агента может быть недоступен другому агенту, а файлы рабочей области доступны всем.

Последствие: после важной работы агент обязан обновлять журнал и контекст.


## 2026-05-10 - Порядок итераций для bitrix24-automation

Решение: итерации по проекту `C:\Users\koval\bat\bitrix24-automation` катать строго по очереди. Сначала — `bitrix24-automation-hygiene` (git + docs/_archive/ + чистка reports TTL + удаление фасадных `__init__.py` + pyproject + logging_setup). После полного прохождения гигиены — заводить первый spec среднего блока `bitnewton-typing-and-tests` (типизация monolith + тесты KPI). Декомпозиция `pipelines/bitnewton_sync.py` возможна только после того, как тесты KPI существуют и зелёные.

Причина: без git любая ошибка необратима. Без тестов декомпозиция монолита 4290 строк — слепая правка с проявлением ошибок только на живом звонке.

Последствие: средний блок разведён на 5 независимых spec-ов в `docs/tasks.md`. Пункты 1-3 последовательны (типизация → декомпозиция → валидация схем). Пункты 4-5 (idempotency, ASR-клиент) независимы, могут катиться параллельно.

## 2026-05-11 - Природа проекта D:\AionUi-Paperclip

Решение: считать `D:\AionUi-Paperclip` самостоятельным проектом — инфраструктурой общего контекста и памяти для AI-агентов. Любые внешние репозитории (в том числе `C:\Users\koval\bat\bitrix24-automation`) рассматриваются как прикладные задачи, которые катятся через эту инфраструктуру, но не являются её частью.

Причина: ранее в контексте и отчётах упоминания bitrix24-automation создавали впечатление, что проект связан с Bitrix. Это не так — Bitrix-репозиторий лишь первый внешний потребитель инфраструктуры.

Последствие: spec-документы, журналы, решения и память о работе над внешними репозиториями могут храниться здесь, но код и артефакты этих репозиториев остаются в их собственных каталогах. В `docs/current-context.md` добавлен явный раздел «Природа проекта» с этой формулировкой.
## 2026-05-12 - Ввод Shared_Memory_Layer в эксплуатацию

### Контекст
Спека agents-shared-memory-layer реализована. Стек: SQLite WAL + LanceDB + Ollama bge-m3 + newline-stdio MCP. На момент ввода в эксплуатацию тесты были зелёные, бенчмарки sml.read p99=0.058ms, sml.semantic_query p99=289ms укладывались в SLA.

### Решение
SML подключён к Codex (~/.codex/config.toml), Cursor (.cursor/mcp.json) и Kiro (.kiro/settings/mcp.json). Перезапуск MCP-клиентов активирует sml.* инструменты. docs/ остаётся источником истины.

### Автор: kiro
### Теги: sml, mcp, production

## 2026-05-12 - SML является основной памятью

### Контекст
После реализации `tools/sml/` старые документы всё ещё содержали активные инструкции использовать `aion-file-memory`.

### Решение
Считать `sml` единственным основным MCP-сервером памяти для Codex, Cursor и Kiro. `aion-file-memory` оставить только как legacy/reference и как исторический rollback-ориентир.

### Последствие
Новые задачи, новые агенты и автопротокол памяти должны использовать `sml.startup_pack`, `sml.semantic_query`, `sml.write`, `sml.add_log`, `sml.add_decision`, `sml.supersede` и `sml.build_context_pack`.

### Автор: Codex
### Теги: sml, mcp, migration
## 2026-05-13 - SML является основной памятью для Codex, Cursor и Kiro

### Контекст
Проверка 2026-05-13 показала, что сам SML работает, Cursor MCP видит сервер sml как ready, а старое решение в памяти содержало устаревшие сведения про aion-file-memory и старые числа тестов.

### Решение
Считать SML единственным активным слоем общей памяти. Cursor запускает SML напрямую через Python из D:\AionUi-Paperclip\.venv-sml. Kiro и Codex используют тот же MCP-сервер sml. Устаревшие решения про параллельное использование aion-file-memory должны быть superseded.

### Автор: Codex
### Теги: sml, cursor, kiro, codex, decision
## 2026-05-13 - Начало работы над bitnewton-typing-and-tests

### Контекст
Подготовка к выполнению задачи bitnewton-typing-and-tests в проекте bitrix24-automation.

### Решение
Создана спецификация задачи в docs/projects/bitnewton-typing-and-tests.md. Работа будет вестись через shell-команды, так как целевой проект находится вне основного воркспейса. Первым приоритетом является типизация и создание тестов для scoring.py.

### Автор: Gemini CLI
### Теги: bitnewton, automation, typing, tests, decision
## 2026-05-19 - Разделение Aion/SML и Bitrix-проекта

### Контекст
Пользователь заметил, что AionUi-Paperclip и bitrix24-automation смешиваются в контексте и UI.

### Решение
Считать D:\AionUi-Paperclip инфраструктурой общей памяти SML и Aion Vision. Bitrix/Bit.Newton аналитика остается внешним прикладным проектом в C:\Users\koval\bat\bitrix24-automation. В AionUi-Paperclip допустимы только журналы, решения и backlog по внешнему проекту, но не активный код/runtime Bitrix.

### Автор: Codex
### Теги: project-boundary, sml, bitrix, aion-vision

## 2026-05-27 - Активная связка сокращена до Codex + Gemini

### Контекст
Пользователь сообщил, что из всех инструментов фактически остались только Codex и Gemini.

### Решение
Считать текущей активной рабочей схемой пару Codex + Gemini CLI. Codex выполняет инженерную работу, Gemini CLI через SML, `GEMINI.md`, `/sml:task`, `/sml:review` и VS Code IDE-режим используется как независимый ревьюер, аналитик и резервный агент.

Cursor и Kiro больше не планируются как обязательные этапы. Их конфиги и документы остаются как историческая настройка и возможный резерв, но новые задачи не должны зависеть от них без отдельного решения пользователя.

### Автор: Codex
### Теги: codex, gemini, workflow, active-agents
## 2026-06-02 - АПС временно запускать через service account

### Контекст
После успешного preflight и dry-run первый write упал на сетевом read timeout. В скрипт добавлены retry/backoff для Bitrix REST и Google Sheets API, после чего write прошел успешно: fetched_deals=1395, matched_deals=199, updated_rows=72, inserted_rows=127, state last_success_utc=2026-06-02T12:03:36Z.

### Решение
Для automation-5 АПС временно считать основным рабочим режимом локальный `automations/aps/sync_bitrix_to_sheet.py --write` через Google service account. 2026-06-02 боевой прогон успешно обновил 72 строки и добавил 127 строк в таблицу. Google Drive MCP/OAuth оставить резервом для точечных проверок, потому что в этом прогоне он снова вернул 429 RATE_LIMIT_EXCEEDED.

### Автор: Codex
### Теги: okru, automation-5, aps, bitrix, google-sheets, service-account
## 2026-06-03 - automation-5 АПС переведена в один текущий чат

### Контекст
Пользователь уточнил, что ежедневная автоматизация АПС должна запускаться каждый раз в одном и том же чате, учитывать историю прошлых запусков и использовать удачные/неудачные методы из раздела автоматизаций и SML.

### Решение
Существующая automation-5 «АПС» обновлена вместо создания дубля: kind=heartbeat, destination=thread, schedule по рабочим дням 09:30. В prompt закреплен основной маршрут через `C:/Users/koval/Documents/ОК.ру/automations/aps/run_sync_with_env.ps1 -Write`, обязательный SML/preflight старт, критерии отбора сделок ОП, менеджеры, инкрементальное обновление и отчет с предложениями по оптимизации.

### Автор: Codex
### Теги: okru, automation-5, aps, heartbeat, bitrix, google-sheets
## 2026-06-03 - automation-6 «Рейтинговая планерка» переведена в один чат

### Контекст
Пользователь попросил настроить автоматизацию подготовки данных для «Рейтинговой планерки», не создавать новый чат при каждом запуске, использовать историю прошлых запусков и переименовать чат.

### Решение
Существующая automation-6 обновлена вместо создания дубля: kind=heartbeat, status=ACTIVE, target thread 019e8e45-63a0-7ae2-84bc-9fc92fef6ad0, расписание сохранено по понедельникам 16:00. Чат переименован в «Рейтинговая планерка - автоматизация». Prompt закрепляет SML старт, preflight, Excel-источники D:/ОК/Рейтинговая, Bitrix REST + stage-history для общей конверсии, фильтры АРТ/MAX/исключение категорий 26 и 28, сортировку пяти блоков по убыванию, яркую подсветку текущего лидера и бледную подсветку лидера прошлого релевантного запуска. В memory.md добавлена актуальная запись и ограничение игнорировать нерелевантные HFT/алготрейдинг записи.

### Автор: Codex
### Теги: okru, automation-6, reytingovaya-planerka, heartbeat, google-sheets, bitrix
## 2026-06-03 - automation-2 Конверсия за неделю переведена в один чат

### Контекст
Пользователь попросил настроить автоматизацию Bitrix24 -> Google Sheets для недельной конверсии по категориям и менеджерам, запускать в одном чате, учитывать прошлые методы и переименовать чат. Preflight в текущем запуске вернул ok=true.

### Решение
Существующая automation-2 `Конверсия за неделю` обновлена без дубля: kind=heartbeat, status=ACTIVE, target thread `019e8e44-e621-7321-abb0-e655a9af75e3`, чат переименован в `Конверсия за неделю - автоматизация`. Расписание стоит по будням утром, а prompt выполняет рабочую часть только если текущая дата является первым рабочим днем недели по строке рабочих дат Google Sheet. Закреплен успешный быстрый маршрут 2026-06-01: preflight -> SML -> Bitrix REST + stage-history -> компактный Google Sheets batchUpdate -> минимальная проверка.

### Автор: Codex
### Теги: okru, automation-2, konversiya-za-nedelyu, heartbeat, bitrix, google-sheets
## 2026-06-04 - АПС: оптимизировать OAuth retry и diff-only updates

### Контекст
Запуск automation-5 2026-06-04 прошел успешно только после повторного старта: первый write упал на временной ошибке DNS Google OAuth. После write контрольный dry-run увидел 22 потенциальных обновления без новых строк из-за защитного overlap.

### Решение
Следующая оптимизация automation-5: добавить retry/backoff на этапе получения Google OAuth token, отправлять в Google Sheets только реально изменившиеся ячейки после сравнения значений, и отдельно считать изменения столбца `Общий смысл`. Это сократит повторные обновления строк и сделает отчет полезнее.

### Автор: Codex
### Теги: okru, automation-5, aps, optimization, google-sheets, oauth
## 2026-06-04 - АПС: только ОП и исключение указанных менеджеров

### Контекст
Пользователь уточнил, что менеджеры Белозеров Александр, Гребенченко Екатерина, Жойкина Анна, Иванов Денис, Левченкова Екатерина, Рыбаков Илья, Щирова Екатерина не должны попадать в отчет АПС. Также в отчет не должны попадать сделки из воронки ОР / отдел развития; пример сделки 27051.

### Решение
Для automation-5 АПС закрепить жесткие ограничения: использовать только `ОП воронка` (`CATEGORY_ID=1`), всегда исключать `ОР воронка` (`CATEGORY_ID=29`), исключать перечисленных менеджеров, исключать стадию `Оплата получена`, а существующие строки, переставшие соответствовать этим ограничениям, удалять из Google Sheets. Helper обновлен и cleanup 2026-06-04 удалил 99 лишних строк.

### Автор: Codex
### Теги: okru, automation-5, aps, bitrix, google-sheets, filter, cleanup
## 2026-06-04 - АПС: cleanup должен проверять видимую колонку Менеджер

### Контекст
Пользователь показал, что после предыдущего cleanup в АПС остались строки с запрещенными менеджерами. Прямая проверка Google Sheets нашла строки, где видимый менеджер запрещен, но cleanup ориентировался на текущего ответственного из Bitrix и пропускал часть старых строк.

### Решение
Для automation-5 cleanup обязан сначала проверять значение столбца `Менеджер` в самой Google Таблице и удалять строку, если там указан запрещенный менеджер или менеджер вне allowlist. Затем можно проверять текущее состояние сделки в Bitrix. Код helper обновлен, write удалил 21 строку, финальная проверка показала 0 строк с запрещенными менеджерами.

### Автор: Codex
### Теги: okru, automation-5, aps, cleanup, google-sheets, manager-filter
## 2026-06-08 - automation-2 использует weekly_conversion helper

### Контекст
Плановый запуск automation-2 2026-06-08 успешно записал недельную конверсию в Google Sheet и выявил необходимость не повторять длинный one-off расчет вручную.

### Решение
Для automation-2 основным маршрутом считать helper `C:/Users/koval/Documents/ОК.ру/automations/weekly_conversion/run_weekly_conversion.py`: запускать через `.venv/Scripts/python.exe` с `--run-date`, `--anchor-date`, `--write-date`, `--write`. Helper считает Bitrix REST + stage-history, динамически находит строки категорий на листе, пишет через Google service account, сохраняет JSON-артефакт и имеет retry/backoff для Google transport/OAuth ошибок. Prompt automation-2 обновлен под этот маршрут.

### Автор: Codex
### Теги: okru, automation-2, weekly-conversion, helper, bitrix, google-sheets
## 2026-06-09 - АПС: расширить retry для Google transport ошибок

### Контекст
Запуск automation-5 2026-06-09 несколько раз падал на нестабильной сети: DNS getaddrinfo failed, SSL EOF и WinError 10054 при Google/transport write. Dry-run проходил, а write падал до успешной записи.

### Решение
Для automation-5 в helper `sync_bitrix_to_sheet.py` считать retryable также `winerror 10054`, `принудительно разорвал`, `eof occurred`, `unexpected_eof`, `ssl`; в `config.json` увеличить `sheet.max_attempts` до 7. Этот маршрут позволил завершить write: основной write deleted=2, затем cleanup write deleted=1, финальный dry-run deleted=0.

### Автор: Codex
### Теги: okru, automation-5, aps, retry, google-sheets, transport
## 2026-06-11 - automation-3: не наследовать системный proxy в Bitrix REST расчете

### Контекст
На запуске 2026-06-11 расчет `Счет отправлен, %` сначала упал на системный proxy `127.0.0.1:10809`, хотя preflight Bitrix profile был доступен через source-IP маршрут.

### Решение
Для automation-3 Bitrix REST клиент в `calc_invoice_conversion.py` должен использовать `requests.Session.trust_env = False` и source-IP из preflight, а не системные `HTTP_PROXY/HTTPS_PROXY`. Wrapper `run_daily.ps1` должен проверять `$LASTEXITCODE`, чтобы ошибки Python-расчета не маскировались.

### Автор: codex
### Теги: automation-3, bitrix, google-sheets, proxy, source-ip
## 2026-06-14 - Карты связей строятся через relationship-map-builder поверх SML

### Контекст
Пользователь попросил изучить safishamsi/graphify и сделать постоянный skill для построения карт связей в проектах и рабочих средах. Graphify полезен как внешний deep knowledge graph, но в AionUi-Paperclip основной памятью остается SML.

### Решение
Для регулярных карт связей использовать Codex skill C:\Users\koval\.codex\skills\relationship-map-builder. Он строит Markdown/JSON графы из SML, документов и локальных файлов, хранит confidence labels EXTRACTED/INFERRED/AMBIGUOUS и пишет артефакты в docs/relationship-maps/. Upstream Graphify можно использовать дополнительно для глубокого codebase-графа, но не ставить его hooks поверх AGENTS.md/GEMINI.md без проверки SML-правил.

### Автор: Codex
### Теги: graphify, relationship-map, sml, codex-skill
## 2026-06-14 - Relationship-map стал автоматическим навигационным слоем памяти

### Контекст
Пользователь попросил, чтобы карта связей не строилась вручную по желанию, а автоматически работала как дополнительный слой памяти для быстрого поиска контекста, логических цепочек и навигации между агентами, задачами, решениями и инструментами.

### Решение
Существующий watcher памяти tools/watch-memory.ps1 теперь пересобирает не только docs/context-packs/context-pack-latest.md, но и docs/relationship-maps/graphify-sml-relationship-map.md/json через tools/build-relationship-map.ps1. Агенты должны использовать tools/query-relationship-map.py как быстрый навигационный слой перед широким поиском по файлам; SML остается основной памятью.

### Автор: Codex
### Теги: relationship-map, memory-layer, automation, sml
## 2026-06-15 - automation-3: daily writer фильтрует нерабочие даты

### Контекст
На запуске 2026-06-15 `write_daily.py --run-date 2026-06-15` сначала выбрал 2026-06-14/колонку Z, потому что июньская строка содержит календарные даты, включая выходные и праздник 12.06.2026.

### Решение
Для automation-3 `write_daily.py` должен выбирать target только среди рабочих дат: будни минус подтвержденные праздники. На июнь 2026 явно закреплен нерабочий день 2026-06-12, поэтому запуск 2026-06-15 пишет за 2026-06-11 в колонку W.

### Автор: codex
### Теги: automation-3, calendar, google-sheets, holiday, daily-run
## 2026-06-15 - automation-5 АПС: пропуск первого рабочего дня недели

### Контекст
Пользователь остановил запуск 2026-06-15 и уточнил, что по первым дням рабочей недели автоматизацию АПС запускать не нужно.

### Решение
Для automation-5 перед SML/preflight/helper выполнять календарную проверку. Если текущая дата является первым рабочим днем недели (обычно понедельник; если понедельник выходной/праздник — следующий рабочий день после выходных/праздников), основную синхронизацию АПС не запускать: не читать Bitrix/Google Sheets без необходимости и не выполнять write helper. В чате кратко фиксировать пропуск по календарному правилу. Prompt automation-5 обновлен.

### Автор: Codex
### Теги: okru, automation-5, aps, calendar, first-working-day, heartbeat
## 2026-06-15 - automation-6 использует rating_planerka helper

### Контекст
Запуск «Рейтинговой планерки» 2026-06-15 показал, что расчет можно стабильно собрать локально, но запись в Google Sheets заблокирована правами.

### Решение
Для automation-6 основным маршрутом считать helper `automations/rating_planerka/run_rating_planerka.py --run-date YYYY-MM-DD --write` после SML и preflight. Helper читает Excel из `D:/ОК/Рейтинговая`, считает Bitrix24 REST+stage-history за месяц, находит блоки вкладки `неделя`, готовит сортировку и подсветку, сохраняет JSON-артефакт. На 2026-06-15 запись не прошла: service account читает таблицу, но write дает Google 403; OAuth connector не стартует. Нужно дать service account editor-доступ к таблице или восстановить OAuth connector.

### Автор: Codex
### Теги: okru, automation-6, reytingovaya-planerka, helper, google-sheets, bitrix, blocker
## 2026-06-15 - automation-6: write-доступ к Google Sheets после проверки локальных аккаунтов

### Контекст
После запроса взять доступы из других проектов проверены локальные service account/OAuth/Chrome fallback. Текущий service account имеет только чтение; OAuth scope не подходит; Chrome Default держит Cookies живым процессом.

### Решение
Не повторять длительный поиск доступов и не извлекать/записывать токены или cookie. Для записи в целевую таблицу нужен один из рабочих каналов: editor-доступ текущему service account, восстановленный Google Drive connector или явное разрешение пользователя временно закрыть Chrome и выдать service account права через UI Default-профиля.

### Автор: Codex
### Теги: automation-6, рейтинговая-планерка, google-sheets, доступы
## 2026-06-16 - automation-4: Bitrix REST не должен наследовать системный proxy

### Контекст
На запуске 2026-06-16 preflight Bitrix profile был доступен, но helper `run_planerka_conversion.py` упал на `Missing dependencies for SOCKS support`, потому что requests унаследовал системный proxy из окружения.

### Решение
В `automations/planerka_conversion/run_planerka_conversion.py` BitrixClient использует `requests.Session.trust_env = False`, чтобы REST-расчет шел через source-IP маршрут preflight и не наследовал HTTP_PROXY/HTTPS_PROXY.

### Автор: Codex
### Теги: okru, automation-4, bitrix, proxy, source-ip
## 2026-06-16 - automation-4: не считать service-account fallback готовым без включенных Google APIs

### Контекст
При восстановлении записи automation-4 в Google Slides 2026-06-16 был найден мертвый системный WinINet proxy socks=127.0.0.1:1091 и отключен. После этого локальные HTTP-запросы заработали, но Google Drive connector продолжил падать на handshake к wham/apps. Service account валиден, но проект 341665085965 возвращает 403 для Slides API и Service Usage API.

### Решение
Для automation-4 не пытаться писать в Google Slides через service account, пока в проекте 341665085965 вручную не включены Service Usage API и Google Slides API, а презентация не расшарена на codex-991@gen-lang-client-0276620581.iam.gserviceaccount.com с правами Editor. При сетевых сбоях сначала проверять, не включен ли мертвый proxy 127.0.0.1:1091.

### Автор: Codex
### Теги: automation-4, google-slides, service-account, google-drive-connector, proxy
## 2026-06-16 - Claude Code добавлен в активную связку общей памяти

### Контекст
Пользователь сообщил, что к текущей системе добавился Claude. До этого актуальная связка была Codex + Gemini CLI, а Claude Code числился только потенциальным дополнительным агентом.

### Решение
Считать активной рабочей связкой Codex + Gemini CLI + Claude Code. Для Claude подготовлены `CLAUDE.md`, проектный `.mcp.json` с сервером `sml`, `OPEN-CLAUDE-SML.cmd` и `CHECK-CLAUDE-SML.cmd`. Claude Code должен работать через те же источники истины: AGENTS.md, context-pack, SML, relationship-map и agent-log. Claude Code установлен (`2.1.178`), `sml` в `claude mcp list` подключен, но живой prompt/smoke-test отложен до авторизации через `claude auth login`.

### Автор: Codex
### Теги: claude-code, sml, agents, shared-memory
## 2026-06-17 - VS Code добавлен как общая IDE-оболочка SML

### Контекст
Пользователь попросил добавить VS Code в общую память с контекстом. VS Code уже был установлен и ранее упоминался как оболочка для Gemini CLI, но не был описан как отдельный рабочий слой общей памяти.

### Решение
Считать VS Code активной рабочей оболочкой, а не агентом. Он открывает `D:\AionUi-Paperclip`, дает доступ к `AGENTS.md`, `CLAUDE.md`, context-pack, SML-скриптам, relationship-map и терминалам агентов. Добавлены `.vscode/settings.json`, `.vscode/tasks.json`, `OPEN-VSCODE-SML.cmd`, `CHECK-VSCODE-SML.cmd` и `docs/vscode-sml.md`. Найден VS Code `1.124.2`; поскольку `code` не найден в PATH текущей PowerShell-сессии, запускатели используют прямой путь `C:\Users\koval\AppData\Local\Programs\Microsoft VS Code\Code.exe`.

### Автор: Codex
### Теги: vscode, sml, ide, shared-memory
## 2026-06-17 - MiMo Code подключен к SML как экспериментальный агент

### Контекст
Пользователь попросил перейти от предложения интеграции MiMo Code к делу. Перед этим были изучены документация MiMo Code, GitHub-организация XiaomiMiMo и репозиторий XiaomiMiMo/MiMo-Code.

### Решение
Установить MiMo Code `0.1.1` глобально через npm и подключить к проекту `D:\AionUi-Paperclip` как экспериментального агента поверх SML. Создан `.mimocode/mimocode.json` с `default_agent: "plan"`, локальным MCP-сервером `sml`, инструкциями `AGENTS.md` и `docs/mimo-code-integration.md`, осторожными permissions и исключениями watcher. Созданы подагенты `sml-review`, `sml-plan`, `sml-build`, а также `OPEN-MIMO-SML.cmd` и `CHECK-MIMO-SML.cmd`. Собственную MiMo persistent memory считать рабочим кешем, а не заменой SML.

### Проверка
`mimo mcp list` показывает `sml connected`. `mimo providers list` показывает `0 credentials`, поэтому живой prompt/smoke-test ожидает выбора провайдера или MiMo Auto в интерактивном запуске.

### Автор: Codex
### Теги: mimo-code, sml, mcp, experimental-agent
## 2026-06-17 - automation-3: numerator `Счет отправлен` считается внутри когорты созданных сделок

### Контекст
Пользователь показал скрин Bitrix за 2026-06-16: у Юлианны Винокуровой в отчете `Счет отправлен, %` = 100%, а automation-3 записала 200%. Диагностика показала, что helper считал все stage-history переходы в `C1:UC_9NU15J` за день, включая сделки, созданные вне периода отчета.

### Решение
Для automation-3 numerator должен быть количеством уникальных сделок, созданных в целевой день и дошедших до stage `C1:UC_9NU15J`. Переходы за день по сделкам, созданным вне периода, не входят в numerator. Колонка AB за 2026-06-16 исправлена: Винокурова 100%, Ковалева 56%, Клец 50%.

### Автор: codex
### Теги: automation-3, bitrix, formula, stage-history, google-sheets
## 2026-06-18 - Активная связка сведена к Codex + Claude Code + Gemini CLI

### Контекст
Аудит проекта (Claude Code) на живых данных SML показал расхождение между декларацией и фактом: «7 авторов» в дашборде были артефактом расщепления имён (codex/Codex, gemini/Gemini-CLI), витрина `aion-data.json` отстала от БД на месяц (watcher не пересобирал экспорт), а Cursor/Kiro/MiMo числились в схеме, но не использовались.

### Решение
Активная рабочая связка — Codex + Claude Code + Gemini CLI. Cursor, Kiro и MiMo Code выведены из схемы, их конфиги (`.cursor/`, `.kiro/`, `.mimocode/`) и запускатели удалены. Ценные спецификации из `.kiro/specs/` (в т.ч. ядро SML `agents-shared-memory-layer`) перенесены в `docs/specs/`; историческая память о работе инструментов сохранена в SML и `docs/agent-log/`.

### Последствие
Имена агентов нормализуются на входе (`tools/sml/validation.normalize_author` в `make_new_record`) и разово через `tools/normalize-sml-authors.py`. Watcher теперь дополнительно пересобирает экспорт дашборда и делает ежедневный бэкап БД (`tools/backup-sml.py` → `var/sml/backups/`). Чтобы нормализация применялась к новым записям, MCP-сервер `sml` нужно перезапустить у активных клиентов (живой процесс держит старый код).

### Автор: Claude Code
### Теги: agents, sml, normalization, dashboard, backup, cleanup
## 2026-06-18 - Усиление надёжности SML: FTS5-фоллбэк, heartbeat, verify бэкапа, CI

### Контекст
После аудита (топ-3 по эффект/риск) определены три слабых места: семантический поиск падал целиком при недоступности Ollama; watcher мог молча умереть без сигнала; бэкап не проверялся восстановлением; регрессии ловились только вручную.

### Решение
1. **FTS5-фоллбэк**: миграция схемы v2 добавляет `records_fts` (SQLite FTS5, unicode61) с триггерами синхронизации. `sml.semantic_query` при `engine=None` или отказе Ollama в рантайме деградирует на полнотекстовый поиск (`mode="text"`, `degraded=true`) вместо ошибки. Поиск остаётся живым без Ollama.
2. **Heartbeat**: `tools/watch-memory.ps1` пишет `logs/memory-auto.heartbeat` каждый цикл; `tools/status-memory-auto.ps1` поднимает тревогу, если метка старше 120 c.
3. **Verify бэкапа**: `tools/backup-sml.py --verify` проверяет `integrity_check` и совпадение числа записей копии с оригиналом; watcher вызывает `--if-stale --verify`.
4. **CI**: `.github/workflows/ci.yml` гоняет `selfcheck` + pytest на push/PR; добавлен `test_validation.py` на `normalize_author`. Тесты с живой Ollama скипаются автоматически.

### Последствие
163 теста зелёные (+21). Схема БД теперь версии 2 — миграция применяется автоматически при открытии store. Память искабельна даже без Ollama; отказ watcher виден; бэкап проверяем; регрессии ядра ловит CI.

### Автор: Claude Code
### Теги: sml, fts5, fallback, heartbeat, backup, ci, reliability
## 2026-06-18 - Aion Vision: живые данные и семантический поиск по памяти

### Контекст
Блок «мощнее»: дашборд только отображал статичный снимок и не давал искать по памяти. При этом live API `/api/sml-dashboard` уже существовал как vite middleware (spawn `export-sml-dashboard.py`), но клиент его не использовал (был убран как «мёртвый»).

### Решение
1. **Живые данные**: `loadDashboardData` снова обращается к `/api/sml-dashboard` первым, с откатом на снимок `aion-data.json` (для прод-сборки без dev-сервера).
2. **Поиск по памяти**: новый backend `apps/aion-vision/scripts/search-sml.py` (только чтение, без записи в op_log) — семантика через Ollama/LanceDB с автоматическим FTS5-фоллбэком (`mode` = semantic|text). Новый vite middleware `/api/search` (тот же spawn-паттерн, аргументы массивом — без shell-инъекций, limit clamp 1..50). Клиент: `searchMemory()` + UI-компонент `MemorySearch` (строка поиска, бейдж режима, карточки результатов с % релевантности).

### Последствие
Дашборд показывает актуальное состояние БД и позволяет спрашивать общую память прямо из UI; поиск надёжен в обоих режимах (с Ollama и без). Поиск работает только при запущенном dev-сервере Aion Vision (middleware); прод-сборка использует снимок и поиск отключён.

### Проверка
`search-sml.py` напрямую → mode=semantic с косинусной релевантностью; цепочка middleware Node→python проверена (mode/limit-clamp/пустой запрос); ESLint + `vite build` зелёные. Полный e2e через поднятый dev-сервер в фоновом окружении не удался по инфраструктурной причине (vite не биндился к порту в детачнутом контексте), но HTTP-слой идентичен рабочему `/api/sml-dashboard`.

### Автор: Claude Code
### Теги: aion-vision, search, semantic, live-api, vite, dashboard
## 2026-06-18 - Aion Vision: постоянный HTTP-сервис для прода (поиск вне dev)

### Контекст
Поиск и live API через vite middleware работали только в `npm run dev`. Прод-сборка отдавала статику без живых данных и без поиска. Нужен путь, который не зависит от dev-сервера.

### Решение
Добавлен `apps/aion-vision/scripts/serve-sml.py` — постоянный HTTP-сервис на stdlib (`ThreadingHTTPServer`, без новых зависимостей). Отдаёт статику из `dist/` с SPA-фоллбэком и те же API `/api/sml-dashboard` и `/api/search` (бэкенд-логика переиспользуется из `export-sml-dashboard.py` и `search-sml.py` через importlib, без подпроцессов на запрос). Запускатель `START-AION-VISION-SERVE.cmd` собирает статику и поднимает сервис на `127.0.0.1:8787`.

### Последствие
Поиск по памяти и живые данные доступны и без dev-сервера. Дашборд и API отдаются из одного origin (клиентские относительные `/api/...` работают без изменений).

### Проверка
curl ко всем эндпоинтам: `/api/sml-dashboard` (status=live, 230 записей), `/api/search` (mode=text, FTS5-фоллбэк сработал при недоступной Ollama), статика `/` (HTTP 200). Визуальная проверка через Playwright: дашборд открылся (0 console errors), запрос «конверсия за неделю» вернул 10 релевантных результатов (99%→55%) с бейджем режима «текст». Скриншот: `apps/aion-vision/.playwright-mcp/memory-search-result.png`.

### Автор: Claude Code
### Теги: aion-vision, http-service, production, search, playwright
## 2026-06-18 - Ollama опциональна; панель здоровья системы в дашборде

### Контекст
После FTS5-фоллбэка возник вопрос: нужна ли Ollama. И не хватало видимого индикатора операционного здоровья (жив ли watcher, в каком режиме поиск, когда бэкап).

### Решение
1. **Ollama опциональна**: проект полностью работает без неё — `sml.semantic_query` и поиск в дашборде деградируют на FTS5 (поиск по словам/префиксам). Сносить Ollama безопасно, но теряется поиск по смыслу и новые записи перестают получать эмбеддинги (при возврате Ollama старые записи нужно реиндексировать). Рекомендация: оставить, если ресурсы позволяют (~1.5 ГБ).
2. **Панель здоровья**: `export-sml-dashboard.py` добавляет в payload секцию `health` (watcher heartbeat, доступность Ollama → режим поиска, последний бэкап). Новый компонент `SystemHealth` показывает три индикатора (зелёный/жёлтый/красный) в дашборде.

### Последствие
Состояние системы видно с одного взгляда: завис ли наблюдатель, идёт ли поиск семантикой или текстом, свежий ли бэкап. Для новичков добавлен гайд `docs/HOW-TO-USE.md`.

### Автор: Claude Code
### Теги: ollama, optional, fts5, health, dashboard, onboarding
## 2026-06-18 - Аналитика памяти в дашборде и устойчивый автозапуск watcher

### Контекст
Нужны были тренды записей по неделям и разбивка активности по агентам/типам, а также чтобы heartbeat был всегда зелёным (фоновый watcher держал старый код и метка устаревала). Плюс кракозябры в `echo` запускателей `.cmd` из-за кодировки консоли.

### Решение
1. **Аналитика**: `export-sml-dashboard.py` отдаёт `weeklyActivity` (записей по ISO-неделям, последние 10, понедельник как старт). Компонент `MemoryAnalytics` показывает недельный bar-chart (recharts) + разбивку по агентам и по типам (доли в %). Данные agents/typeCounts уже были в payload.
2. **Автозапуск watcher**: задача планировщика `Aion File Memory Auto` (триггер AtLogOn) перезапущена, чтобы подхватить heartbeat-код; `install-memory-autostart.ps1` усилен — `RestartCount=100`, без лимита времени выполнения, `MultipleInstances IgnoreNew`. Heartbeat стал зелёным (age ~6 c).
3. **Кодировка .cmd**: в `START-AION-VISION-SERVE.cmd` и `START-AION-VISION.cmd` добавлен `chcp 65001` — русские сообщения больше не выводятся кракозябрами (сам сервис всегда работал, проблема была только в echo батника).

### Проверка
`export --json` → `weeklyActivity` 6 недель (32→60→43). ESLint + `vite build` зелёные. Playwright: дашборд открылся (0 console errors), блок «Аналитика памяти» отрисовал недельный график и разбивки (Codex 92%, agent_log 77%). Задача планировщика `Running`, heartbeat зелёный.

### Автор: Claude Code
### Теги: aion-vision, analytics, recharts, watcher, task-scheduler, heartbeat, encoding

## 2026-06-18 - Глобальный bootstrap памяти для Codex, Claude Code и Gemini CLI

### Контекст

Пользователь уточнил, что агенты не должны подтягивать память только при запуске из `D:\AionUi-Paperclip` или после отдельной просьбы. Нужно, чтобы у каждого активного агента было правило/skill: автоматически искать общую память, контекст и похожие решения по теме запроса.

### Решение

Считать `D:\AionUi-Paperclip` абсолютным корнем общей памяти для активных агентов независимо от текущей рабочей папки. Добавлены:

- `docs/agent-memory-bootstrap.md` — каноническое правило автоподхвата памяти;
- `tools/agent-memory-bootstrap.ps1` — команда bootstrap из любой папки;
- `LOAD-SML-MEMORY.cmd` — ручная проверка bootstrap;
- Codex skill `C:\Users\koval\.codex\skills\sml-memory-bootstrap`;
- глобальные инструкции `C:\Users\koval\.codex\AGENTS.md`, `C:\Users\koval\.claude\CLAUDE.md`, `C:\Users\koval\.gemini\GEMINI.md`;
- user-scope MCP `sml` для Claude Code через `claude mcp add --scope user`.

Перед содержательной задачей агент должен запускать:

```powershell
& "D:\AionUi-Paperclip\tools\agent-memory-bootstrap.ps1" -Agent "<имя агента>" -Query "<тема>"
```

Затем использовать `sml.startup_pack`, `sml.semantic_query`, context-pack, relationship-map и документы памяти.

### Проверка

- Bootstrap успешно запущен из внешней папки `C:\Users\koval\Documents\Bitrix24` и нашел context-pack + relationship-map.
- `C:\Users\koval\.codex\skills\sml-memory-bootstrap` прошел `quick_validate.py`.
- `claude mcp list` из внешней папки показывает `sml` как `Connected`.

### Последствие

Активный контур Codex + Claude Code + Gemini CLI больше не зависит только от запуска из рабочей папки. Cursor, Kiro и MiMo Code остаются выведенными из схемы и не возвращаются этим решением.

### Автор: Codex
### Теги: bootstrap, shared-memory, sml, codex, claude-code, gemini-cli
## 2026-06-19 - Иерархические agent-workflows вместо параллельной рассылки запросов

### Контекст
Пользователь уточнил, что цель — запускать отдельную задачу через разные уровни агентов и субагентов, где каждый уровень выполняет свою роль, передает структурированный handoff выше, а финальная инстанция видит всю историю без искажения смысла.

### Решение
Для сложных задач использовать иерархическую схему отделов L1-L5: Gemini CLI выполняет первичную аналитику, Codex проверяет и прорабатывает инженерные уровни L2/L3, Claude Code делает архитектурный синтез L4, Codex формирует финальный отчет пользователю L5. Один запрос в несколько моделей не является целевой постоянной схемой.

### Статус
Заменено решением от 2026-06-19 "Очередность agent-workflow изменена: Gemini L2, Codex L3/L4, Claude L5".

### Автор: Codex
### Теги: agent-workflows, codex, gemini-cli, claude-code, coordination

## 2026-06-19 - MiMo AUTO добавлен как нижний подшаг L1.0

### Контекст
Пользователь попросил добавить MIMO от Xiaomi в режиме AUTO на самый первый, нижний уровень иерархической схемы. Ранее MiMo Code был выведен из общей активной схемы, поэтому нужно было не откатить старую интеграцию целиком, а добавить узкое исключение.

### Решение
В `docs/agent-workflows/` использовать `MiMo AUTO` только как логический подшаг `L1.0`: он делает первичный AUTO-проход, после чего `Gemini CLI` как `L1.1` обязан проверить, расширить и очистить результат перед передачей на `L2 Codex`. Старые проектные конфиги `.mimocode/`, запускатели и собственная MiMo-память не возвращаются.

### Последствие
Новый стандартный путь workflow: `MiMo AUTO L1.0 -> Gemini CLI L1.1 -> Codex L2 -> Codex L3 -> Claude Code L4 -> Codex L5`. `contract.json.allowed_next_agents` остается gate-механизмом: каждый подшаг ждет своего разрешенного следующего участника.

### Статус
Порядок уровней заменен решением от 2026-06-19 "Очередность agent-workflow изменена: Gemini L2, Codex L3/L4, Claude L5". Ограничение про MiMo AUTO только как `L1.0` остается актуальным.

### Автор: Codex
### Теги: agent-workflows, mimo-auto, gemini-cli, codex, claude-code

## 2026-06-19 - Очередность agent-workflow изменена: Gemini L2, Codex L3/L4, Claude L5

### Контекст
Пользователь явно задал новую последовательность: `L1.0 MiMo AUTO -> L1.1 Gemini CLI -> L2 Gemini CLI -> L3 Codex -> L4 Codex -> L5 Claude Code`. Также нужно прописать субагентов под каждый уровень.

### Решение
Стандартный workflow теперь идет в такой очередности:

- `L1.0 MiMo AUTO` — первичный AUTO-проход.
- `L1.1 Gemini CLI` — проверка MiMo, расширение фактов, чистый L1 handoff.
- `L2 Gemini CLI` — инженерная проверка, ограничения, edge cases, revision gate.
- `L3 Codex` — декомпозиция реализации, тесты, automation, integration readiness.
- `L4 Codex` — архитектурный синтез, contract audit, risk gate, maintainability review.
- `L5 Claude Code` — независимая финальная техническая проверка и `final-report.md` для пользователя.

Субагенты записываются в `contract.json` как role metadata уровня. Они не являются отдельными workflow-ходами, кроме явных подшагов `L1.0` и `L1.1`.

### Автор: Codex
### Теги: agent-workflows, subagents, mimo-auto, gemini-cli, codex, claude-code

## 2026-06-19 - Model policy закреплена для всех субагентов workflow

### Контекст
Пользователь задал конкретные модели и effort для каждого субагента в иерархическом workflow.

### Решение
Считать `docs/agent-workflows/model-policy.md` источником истины по model aliases субагентов. Новые `contract.json` через `tools/agent_workflow.py` должны включать `subagent.model` для каждого субагента.

Ключевая матрица:

- `L1.0 MiMo AUTO`: все субагенты используют `MiMo AUTO / Xiaomi API AUTO`.
- `L1.1 Gemini CLI`: `Gemini 3.1 Pro` для source/context, `Gemini 3.5 Flash` для noise/handoff с effort `High/Low/Medium` по роли.
- `L2 Gemini CLI`: все engineering-review субагенты используют `Gemini 3.5 Flash / High`.
- `L3 Codex`: `codex-5.3`, `gpt-5.5`, `gpt-5.4 mini`, `gpt-5.4` с effort `xhigh` по роли.
- `L4 Codex`: все архитектурные субагенты используют `gpt-5.5 / xhigh`.
- `L5 Claude Code`: `Claude Opus 4.7 alias`, `Claude Haiku 4.5 alias`, `Claude Sonnet 4.6 alias`, `Claude Opus 4.8 alias` с effort `xhigh` по роли.

### Последствие
Если реальный CLI/провайдер не поддерживает указанный alias, агент не должен молча подменять модель. Нужно записать mismatch в handoff и запросить approved fallback.

### Автор: Codex
### Теги: agent-workflows, model-policy, subagents, gemini, codex, claude, mimo

## 2026-06-19 - Antigravity CLI заменяет Gemini CLI в активном workflow

### Контекст
Официальный `@google/gemini-cli` был восстановлен, но Google login для Gemini Code Assist повторно блокировался ошибкой `UNSUPPORTED_LOCATION`. Пользователь предложил перейти на Antigravity и попросил после успешного теста удалить Gemini CLI.

### Решение
Считать активной связкой `Codex + Claude Code + Antigravity CLI`. В `docs/agent-workflows/` уровни `L1.1` и `L2` теперь выполняет `Antigravity CLI`; `Gemini CLI` выведен из активного runtime.

Удалены активные Gemini CLI артефакты: глобальные npm-пакеты `@google/gemini-cli` и `codex-gemini-helper`, shims `gemini`/`ask-gemini`, проектная `.gemini/`, `GEMINI.md`, Gemini launchers, `docs/gemini-sml.md`, `docs/cursor-gemini-model.md`, старый каталог `D:\Gemini`, root-файлы `C:\Users\koval\.gemini` без удаления `C:\Users\koval\.gemini\antigravity-cli`.

### Последствие
Новый стандартный путь workflow: `MiMo AUTO L1.0 -> Antigravity CLI L1.1 -> Antigravity CLI L2 -> Codex L3 -> Codex L4 -> Claude Code L5`.

`agy` live smoke-test прошел на уровне авторизации/model call: в логах есть keyring auth и `streamGenerateContent`, в conversation DB найден ответ `OK`. Ограничение: `agy --print` завершился с кодом 0, но stdout пустой, поэтому для полностью автоматического handoff нужен wrapper или другой надежный способ извлечения ответа.

### Автор: Codex
### Теги: agent-workflows, antigravity-cli, agy, gemini-cli, codex, claude-code

## 2026-06-19 - Antigravity labels переведены на runtime AUTO

### Контекст
Тестовый workflow показал, что уровни `L1.1` и `L2` уже выполняет `Antigravity CLI`, но `contract.json`, `status` и `final-report.md` новых workflow продолжали показывать старые labels `Gemini 3.1/3.5`.

### Решение
Для субагентов `L1.1` и `L2` закреплен model label `Antigravity CLI AUTO` с прежними effort (`High`, `Low`, `Medium`). Это не named model Gemini, а runtime alias для текущего `agy`.

Добавлен `tools/antigravity_print.py`: wrapper запускает raw `agy --print`, а при пустом stdout восстанавливает свежий ответ из Antigravity conversation DB.

### Последствие
Новые workflow больше не создают Antigravity subagents со старыми Gemini labels. Если позже `agy models` стабильно покажет точные named models, их можно закрепить отдельным решением и обновить `docs/agent-workflows/model-policy.md`.

### Автор: Codex
### Теги: agent-workflows, model-policy, antigravity-cli, agy

## 2026-06-21 - HH avatar-only не выбран как основной продукт

### Контекст
Пользователь попросил через workflow проверить российский рынок идеи: сервис улучшения аватарки резюме для HeadHunter, занятость ниши, востребованность, конкуренцию и возможные альтернативы.

### Решение
Не считать standalone "улучшатель аватарки для hh.ru" основной ставкой продукта. Фото в резюме важно, но avatar-only value легко заменяется generic AI headshot/photo editor инструментами.

Основной MVP формулировать как `HH Resume Booster`: модуль фото + аудит резюме + адаптация под вакансию + сопроводительное письмо + чеклист перед откликом.

### Последствие
Перед разработкой нужен validation sprint: landing с тремя офферами (`avatar-only`, `full resume audit`, `vacancy response pack`), concierge MVP на 30 пользователях, замер paid intent и user-reported views/invitations.

### Автор: Codex
### Теги: product, headhunter, market-analysis, resume-booster, agent-workflows

## 2026-06-21 - HH Resume Booster validation test запускается local-only

### Контекст
После market workflow был выполнен практический шаг: подготовить 14-дневный landing/concierge test для трех офферов.

### Решение
Первый validation surface реализован в Aion Vision как local-only экран `/#hh-booster`. Данные заявок хранятся только в `localStorage` браузера под ключом `aion.hhResumeBooster.leads.v1`, экспортируются JSON и считаются через `tools/hh_resume_booster_metrics.py`.

Strong paid intent считается только явный выбор `Готов оплатить`. Фото и резюме в этом прототипе не собираются, чтобы не расширять privacy scope.

### Последствие
До публичного запуска нужен отдельный privacy/delete policy и нормальное хранилище. До фактического 14-дневного сбора данных цель не считается полностью завершенной.

### Автор: Codex
### Теги: product, headhunter, validation, privacy, aion-vision

## 2026-06-23 - Локальный agent-workflow-router принят как маршрутизатор рабочих режимов

### Контекст
После установки frontend/design, Superpowers, verification, security и skill-creator пользователь спросил, что из этого реально полезно, и согласился сделать общий рабочий протокол выбора навыков.

### Решение
Создан локальный skill `agent-workflow-router`. Он должен использоваться как легкий первый шаг для инженерных задач: классифицировать тип работы и риск, выбрать минимальный достаточный набор downstream skills/MCP, затем завершать работу через свежую проверку `verification-before-completion`.

Skill установлен в Codex, Claude Code, `.agents` и shared `agent-skills`.

### Последствие
Новый стандарт для задач: не грузить все навыки подряд, а маршрутизировать по типу задачи. UI-задачи идут через frontend/design route, баги через systematic debugging/TDD, security через codex-security/Semgrep/Snyk/CodeQL по scope, повторяемые процессы через skill-creator.

### Автор: Codex
### Теги: agent-skills, workflow-router, codex, claude-code, antigravity-cli, verification

## 2026-06-23 - Единая команда запуска роя агентов

### Контекст
Пользователь спросил, можно ли сделать одно написание/команду, по которой чат понимает, что нужно запускать Codex и общий рой агентов.

### Решение
Считать `Рой: <задача>`, `Рой, <задача>`, `РОЙ: <задача>`, `РОЙ, <задача>`, `рой: <задача>`, `/swarm <задача>`, `Запусти рой: <задача>` и `Workflow: <задача>` явными триггерами иерархического agent workflow. Регистр слова `Рой` не важен.

Для локального терминального запуска добавлены:

- `tools/start-agent-swarm.ps1`
- `START-AGENT-SWARM.cmd`
- `docs/agent-workflows/SWARM-COMMAND.md`

Триггер создает auditable workflow через `tools/agent_workflow.py new`, выполняет Aion SML bootstrap, сохраняет исходный brief, показывает `workflow_id`, текущий уровень и следующего разрешенного агента.

### Последствие
Пользователь может писать в чате `Рой: ...`, а агент обязан включить workflow-протокол. Из терминала можно запускать:

```powershell
.\START-AGENT-SWARM.cmd -Title "<название>" -Brief "<задача>"
```

Команда не означает параллельный запрос во все модели, не обходит `allowed_next_agents`, не запускает long-running/external/destructive действия без risk gate и явного подтверждения пользователя.

### Автор: Codex
### Теги: agent-workflows, swarm-trigger, codex, claude-code, antigravity-cli, mimo-auto

## 2026-06-24 - MiMo AUTO выведен из новых agent-workflows

### Контекст
Пользователь попросил убрать MiMo, потому что с 2026-06-25 он становится платным. Ранее `MiMo AUTO` был добавлен как нижний подшаг `L1.0`, но это было временное исключение поверх уже выведенного MiMo Code.

### Решение
Отменить исключение `MiMo AUTO L1.0` для новых workflow. Стандартная цепочка теперь:

```text
L1 Antigravity CLI -> L2 Antigravity CLI -> L3 Codex -> L4 Codex -> L5 Claude Code
```

Новые `contract.json` не должны содержать `L1.0`, `L1.1`, `MiMo AUTO` или Xiaomi model aliases. `tools/agent_limit_monitor.py` больше не вызывает `mimo stats` в дефолтном сборе лимитов. `tools/check-agent-runtimes.ps1` больше не проверяет `mimo`, `tools/install-agent-cli-shims.ps1` больше не создает `mimo.cmd`, глобальный npm-пакет `@mimo-ai/cli` удален. Задачу по исправлению MiMo headless runtime считать obsolete, а не активным блокером.

### Последствие
Старые workflow с `L1.0 MiMo AUTO` не переписывать: это архивная история и доказательства прошлых прогонов. На 2026-06-24 новые workflow, команда `Рой:` и документы политики стартовали с `Antigravity CLI L1`; это решение superseded решением 2026-07-02 о дефолтном `gemini-vertex` и решением 2026-07-03 о case-insensitive `РОЙ`.

### Автор: Codex
### Теги: agent-workflows, mimo-auto, antigravity-cli, codex, claude-code, limits

## 2026-06-24 - Telegram default layer: Bot API project first, MCP/MTProto only read-only pilot

### Контекст
После установки `telegram-workflow-router` и локальной инвентаризации пользователь подтвердил рабочий порядок: использовать текущий Bot API проект как основной Telegram-слой, Telegram Web как QA/manual слой, а MCP/MTProto оставлять только для отдельного read-only pilot, когда Bot API реально не хватает.

### Решение
Основной Telegram runtime для агентской работы: `C:\Users\koval\Documents\New project`.

Порядок выбора:

```text
Bot API via existing local project -> Telegram Web QA/manual evidence -> n8n/Make for concrete no-code workflow -> MCP/MTProto read-only pilot only when Bot API is insufficient
```

`telegram-workflow-router` должен направлять текущие Telegram bot/channel/group/Mini App/Web/MCP задачи через этот порядок. MCP/MTProto не добавлять в default setup, не создавать user-account session и не выполнять send/edit/delete/publish без отдельного явного подтверждения пользователя.

### Последствие
Перед Telegram-работой агенты должны читать `telegram-workflow-router` и проверять setup командой:

```powershell
& "C:\Program Files\PowerShell\7\pwsh.exe" -NoProfile -ExecutionPolicy Bypass -File "C:\Users\koval\Documents\Codex\2026-05-18\npx-skills-add-anthropics-claude-code\agent-skills\scripts\verify-telegram-bot-api-setup.ps1" -ProjectRoot "C:\Users\koval\Documents\New project" -CheckHealth
```

Для рестартов использовать только visible monitor flow проекта. Telegram Web остается подтверждающим/ручным слоем. MCP/MTProto оформлять отдельной задачей с allowlist, read-only first probe и отдельным risk gate.

### Автор: Codex
### Теги: telegram, bot-api, mcp, mtproto, agent-skills, safety
## 2026-07-02 - automation-3: writer выбирает месячный лист по metadata

### Контекст
Запуск 2026-07-02 показал, что `write_daily.py` был привязан к `Июнь 2026 ОП`/sheetId 1165391656 и возвращал run_date_not_found_in_calendar для 2026-07-02.

### Решение
Для automation-3 writer должен получать metadata всех листов и выбирать месячный лист по дате запуска, например `Июль 2026 ОП` для июля; старый июньский sheetId использовать только как fallback. Не возвращаться к single-sheet календарю.

### Автор: Codex
### Теги: okru, automation-3, google-sheets, calendar, monthly-sheet

## 2026-07-02 - Default workflow L1/L2 переведен на Gemini Vertex

### Контекст
Antigravity OAuth был восстановлен, но live model call продолжает падать с `FAILED_PRECONDITION (code 400): User location is not supported for the API use`. Проверки через HAPP/proxy показали, что это не только отсутствие авторизации и не простое игнорирование proxy. Параллельно Vertex Gemini уже прошел live smoke через Google ADC, `GOOGLE_CLOUD_PROJECT`, `GOOGLE_CLOUD_LOCATION` и модель `gemini-2.5-flash`.

### Решение
Новые agent-workflows и команда `Рой:` по умолчанию используют профиль `gemini-vertex`:

```text
L1 Gemini Vertex -> L2 Gemini Vertex -> L3 Codex -> L4 Codex -> L5 Claude Code
```

Профиль `antigravity` сохранен для явного запуска (`--profile antigravity` / `-Profile antigravity`) только после свежего успешного Antigravity smoke. Gemini CLI не возвращается в активную схему; используется именно Vertex AI runtime через `tools/gemini_vertex_workflow_review.py`.

### Последствие
`tools/agent_workflow.py new` и `tools/start-agent-swarm.ps1` создают новые workflow с `workflow_profile: gemini-vertex` и `allowed_next_agents: ["Gemini Vertex"]`. `Gemini Vertex` и `Antigravity CLI` считаются review-only участниками: handoff генерируется отдельным runner, а state mutations выполняет Codex через `--executor Codex`.

### Автор: Codex
### Теги: agent-workflows, gemini-vertex, antigravity-cli, codex, claude-code

## 2026-07-03 - Antigravity optional profile smoke восстановлен, команда РОЙ нормализована

### Контекст
Пользователь попросил проверить доступ к Antigravity, корректировки workflow и настроить запуск через команду `РОЙ`.

### Решение
Свежий локальный smoke Antigravity считать успешным:

- `tools/check-agent-runtimes.ps1` видит `agy`;
- `tools/antigravity_print.py --process-timeout-seconds 90 "Ответь ровно одним словом: OK"` вернул `OK`;
- `tools/antigravity_workflow_review.py` на временном workflow профиля `antigravity` вернул валидный handoff с `## Решение approve`.

При этом дефолтная команда `Рой` / `РОЙ` остается на профиле `gemini-vertex`:

```text
L1 Gemini Vertex -> L2 Gemini Vertex -> L3 Codex -> L4 Codex -> L5 Claude Code
```

Antigravity включается только явно через `-Profile antigravity` / `--profile antigravity`.

### Последствие
Триггеры `Рой:`, `Рой,`, `РОЙ:`, `РОЙ,`, `рой:`, `/swarm`, `Запусти рой:` и `Workflow:` считаются запуском иерархического workflow. Регистр слова `Рой` не важен. Документы политики и запускатель синхронизированы с этим правилом.

### Автор: Codex
### Теги: agent-workflows, swarm-trigger, antigravity-cli, gemini-vertex, codex

## 2026-07-03 - Default workflow возвращен на Antigravity/agy, Gemini Vertex стал fallback

### Контекст
Пользователь явно попросил сделать запуск через `agy`/Antigravity дефолтным, а Gemini Vertex оставить запасным вариантом. До этого 2026-07-02 default был временно переведен на `gemini-vertex` из-за Antigravity regional/eligibility blocker, но свежий локальный smoke 2026-07-03 уже подтвердил доступность `agy`.

### Решение
Новые agent-workflows и команда `Рой:` / `РОЙ:` по умолчанию используют профиль `antigravity`:

```text
L1 Antigravity CLI -> L2 Antigravity CLI -> L3 Codex -> L4 Codex -> L5 Claude Code
```

Профиль `gemini-vertex` остается резервным явным запуском:

```powershell
& "D:\AionUi-Paperclip\tools\start-agent-swarm.ps1" -Title "<задача>" -Brief "<brief>" -Profile gemini-vertex
```

### Последствие
`tools/agent_workflow.py new` и `tools/start-agent-swarm.ps1` создают новые workflow с `workflow_profile: antigravity` и `allowed_next_agents: ["Antigravity CLI"]`, если профиль не задан явно. `Antigravity CLI` и `Gemini Vertex` остаются review-only участниками: handoff генерируется отдельным isolated runner, а state mutations выполняет Codex/Claude через trusted executor.

### Автор: Codex
### Теги: agent-workflows, antigravity-cli, agy, gemini-vertex, swarm-trigger

## 2026-07-06 - Grok Build 0.2.87 добавлен как кандидат, не как активный workflow-уровень

### Контекст
Пользователь сообщил, что появился новый агент `Grok 0.2.87`. Официальная страница xAI CLI описывает Grok Build как terminal/coding agent с поддержкой `AGENTS.md`, MCP servers, skills, hooks и memory, что делает его совместимым с концепцией общей SML-памяти.

### Решение
Зафиксировать `Grok Build 0.2.87` как нового кандидата/резервного агента, но не включать его в дефолтный `Рой` и не заменять им Antigravity CLI или Gemini Vertex до локального smoke-теста.

Минимальный gate перед активацией:

- команда `grok --version` доступна из PowerShell;
- auth завершен без записи секретов в docs/SML;
- запуск из `D:\AionUi-Paperclip` читает `AGENTS.md`;
- Grok выполняет SML bootstrap или использует MCP `sml`;
- короткий тест на русском оставляет отчет в `docs/agent-log/`;
- долгие процессы соблюдают Visible Run Rule.

### Последствие
Текущая активная связка остается `Codex + Antigravity CLI + Claude Code`, `Gemini Vertex` остается fallback profile `gemini-vertex`. Grok учитывается в реестре и задачах как кандидат на отдельный fallback/profile после проверки.

### Автор: Codex
### Теги: grok-build, xai-cli, agent-workflows, sml, candidate-agent

## 2026-07-06 - Добавлен experimental profile grok-gemini для Роя

### Контекст
Пользователь уточнил, что Grok не должен заменять других агентов. Нужна цепочка, где Grok является самым нижним/первым уровнем, затем Gemini, затем Codex, затем Claude.

### Решение
Добавить отдельный workflow profile `grok-gemini`:

```text
L1 Grok Build -> L2 Gemini Vertex -> L3 Codex -> L4 Codex -> L5 Claude Code
```

Grok Build получает собственный набор L1-субагентов:

- `grok-memory-bootstrapper`;
- `grok-problem-framer`;
- `grok-source-scout`;
- `grok-handoff-editor`.

Grok Build, как и Gemini Vertex/Antigravity CLI, является review-only агентом для workflow state mutations. Codex остается trusted executor для `claim`, `submit-work`, `approve-level`.

### Последствие
Профиль можно создать командой:

```powershell
& "D:\AionUi-Paperclip\tools\start-agent-swarm.ps1" -Title "<задача>" -Brief "<brief>" -Profile grok-gemini
```

Дефолтный `Рой` пока не переключается на `grok-gemini`, потому что локальный `grok` CLI еще не найден и не прошел auth/smoke. После `grok version`, auth, `grok inspect` и успешного русского smoke можно отдельно решить, делать ли `grok-gemini` дефолтом.

### Автор: Codex
### Теги: grok-build, grok-gemini, agent-workflows, swarm-trigger, gemini-vertex, codex, claude-code

## 2026-07-06 - Grok Build runtime подтвержден для experimental profile grok-gemini

### Контекст
После добавления профиля `grok-gemini` нужно было пройти live gate: установка CLI, авторизация, проверка модели, подключение SML и smoke L1 runner.

### Решение
Считать локальный runtime `Grok Build 0.2.87` подтвержденным для явного экспериментального профиля `grok-gemini`.

Проверено:

- установлен `@xai-official/grok@0.2.87`, `grok version` вернул `grok 0.2.87`;
- auth через `grok.com` завершен, `grok models` показывает `grok-build`;
- проектный MCP `sml` добавлен в `D:\AionUi-Paperclip\.grok\config.toml`;
- для совместимости с Grok SML публикует alias-имена `sml_ping`, `sml_startup_pack`, `sml_semantic_query` и т.д. через `SML_MCP_TOOL_NAME_MODE=grok-safe`;
- `sml_ping` из Grok вернул `ok=true`, `version sml-0.1.0`, `degraded=false`;
- `tools/grok_build_workflow_review.py` использует `grok-build`, `--prompt-file`, `--disable-web-search`, `--no-subagents`, подставляет PATH для Git/Node и фильтрует внешний MCP stderr-шум на успешном запуске;
- smoke workflow `2026-07-06-225247-147230-smoke-grok-gemini` получил валидный русский L1 handoff и перешел в `waiting_for_approval` с `allowed_next_agents=["Gemini Vertex"]`.

### Последствие
`grok-gemini` можно запускать явно:

```powershell
& "D:\AionUi-Paperclip\tools\start-agent-swarm.ps1" -Title "<задача>" -Brief "<brief>" -Profile grok-gemini
```

Дефолтный `Рой` не изменяется и остается `antigravity`. Grok Build остается review-only участником: state mutations выполняет Codex/Claude через trusted executor.

### Автор: Codex
### Теги: grok-build, grok-gemini, xai-cli, sml, mcp, workflow-smoke

## 2026-07-07 - find-skills становится discovery-слоем для agent skills

### Контекст
После разбора YouTube Short `XfifNCHY93I` выяснено, что речь идет о `find-skills` из `vercel-labs/skills`: скилле и CLI-маршруте для поиска существующих agent skills в open skills ecosystem.

### Решение
Установить `find-skills` и использовать его как первый discovery/ranking слой, когда пользователь просит найти, выбрать, установить или сравнить skill/tool/workflow под задачу.

Политика:

- искать через `find-skills` / `npx skills find`;
- не устанавливать найденные skills вслепую;
- перед установкой проверять источник, install count, repo/SKILL.md, scripts/MCP/network behavior и локальную пользу;
- для неизвестных авторов, низких install count или сетевых/MCP/scripts capabilities сначала делать review, а не auto-install.

### Последствие
`agent-workflow-router` получил `Skill Discovery Route Detail`. `find-skills` установлен в `.agents`, `.claude`, `.codex` и shared `agent-skills`.

### Автор: Codex
### Теги: find-skills, vercel-labs-skills, agent-skills, skill-discovery, supply-chain

## 2026-07-07 - Default РОЙ переведен на Grok -> Antigravity -> Codex -> Claude

### Контекст
Пользователь уточнил, что по команде `Рой` нужна не прежняя цепочка с Antigravity на L1 и не legacy `grok-gemini`, а последовательность:

```text
L1 Grok -> L2 Antigravity CLI -> L3 Codex -> L4 Codex -> L5 Claude Code
```

### Решение
Сделать workflow profile `grok-antigravity` профилем по умолчанию для новых workflow и для `tools/start-agent-swarm.ps1` / `START-AGENT-SWARM.cmd`.

Текущая default-цепочка:

```text
L1 Grok Build -> L2 Antigravity CLI -> L3 Codex -> L4 Codex -> L5 Claude Code
```

Профили сохранены:

- `antigravity` - явный запуск `L1/L2 Antigravity CLI`;
- `gemini-vertex` - fallback через Google Vertex AI;
- `grok-gemini` - legacy route `L1 Grok Build -> L2 Gemini Vertex`.

`Grok Build`, `Antigravity CLI` и `Gemini Vertex` остаются review-only участниками для workflow state mutations; `Codex` или `Claude Code` выполняют `claim`, `submit-work`, `approve-level` как trusted executor.

### Проверка

- `py_compile` для `tools/agent_workflow.py`, `tools/grok_build_workflow_review.py`, `tools/antigravity_workflow_review.py`, `tools/gemini_vertex_workflow_review.py` прошел.
- `pytest` для workflow/runner тестов: `33 passed`.
- Smoke без явного `-Profile`: `tmp/swarm-default-grok-antigravity-smoke/2026-07-07-130352-778636-рой-default-grok-antigravity-smoke`.
- Smoke contract подтвердил `workflow_profile=grok-antigravity`, `L1=Grok Build`, `L2=Antigravity CLI`, `L3=Codex`, `L4=Codex`, `L5=Claude Code`.

### Последствие
Команды `Рой: <задача>`, `Рой, <задача>` и прямой запуск `tools/start-agent-swarm.ps1` без `-Profile` должны создавать именно `grok-antigravity`. Для возврата к старым цепочкам нужен явный `-Profile`.

### Автор: Codex
### Теги: roy, swarm, grok-antigravity, grok-build, antigravity-cli, codex, claude-code

## 2026-07-07 - РОЙ получил явный run-next вместо скрытого полного автопрогона

### Контекст
После переключения default `Рой` на `grok-antigravity` пользователь увидел, что в консоли "как будто ничего не происходит". Диагностика показала, что `tools/start-agent-swarm.ps1` создавал workflow и оставлял его в `planned`, но не запускал `Grok Build L1`.

### Решение
Добавить отдельный one-step runner:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File D:\AionUi-Paperclip\tools\run-agent-workflow-next.ps1 -Root D:\AionUi-Paperclip\docs\agent-workflows -WorkflowId <workflow-id>
```

`tools/start-agent-swarm.ps1` теперь печатает `Run L1` command и поддерживает `-RunNext`.

Политика выполнения:

- `start-agent-swarm.ps1` без `-RunNext` только создает workflow и показывает команды;
- `-RunNext` выполняет первый текущий шаг в той же консоли;
- `run-agent-workflow-next.ps1` выполняет ровно один текущий шаг по `allowed_next_agents`;
- скрытый полный автопрогон L1-L5 не включать по умолчанию, чтобы не жечь лимиты и не обходить gates.

### Проверка

- PowerShell AST parse прошел для `run-agent-workflow-next.ps1` и `start-agent-swarm.ps1`.
- `pytest` для workflow/Grok tests: `21 passed`.
- Smoke `run-agent-workflow-next.ps1` на `tmp/swarm-default-grok-antigravity-smoke/2026-07-07-130352-778636-рой-default-grok-antigravity-smoke` выполнил `Grok Build L1`, submit-work и перевел state в `waiting_for_approval`, next agent `Antigravity CLI`.

### Автор: Codex
### Теги: roy, run-next, workflow-ux, grok-build, antigravity-cli
