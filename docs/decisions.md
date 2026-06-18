# Журнал решений

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
