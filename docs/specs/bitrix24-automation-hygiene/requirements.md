# Requirements Document

## Introduction

Итерация «гигиена» репозитория `C:\Users\koval\bat\bitrix24-automation` приводит проект в управляемое инженерное состояние без изменения поведения пайплайна и контракта .bat-скриптов. В рамках итерации вводится локальный git, упорядочиваются корневые .txt-заметки, очищаются временные артефакты в `reports/`, фиксируется решение по «фасадам» между `bitrix24_api.py` и пакетом `bitrix/`, удаляются неиспользуемые фасадные `__init__.py` пакетов `bitrix/`, `asr/`, `ui/`, добавляется `pyproject.toml` с конфигурацией `ruff` и `black`, вводится модуль логирования `logging_setup` с заменой `print` на вызовы логгера во всех Python-файлах Scope_Python_Files, все изменения оформляются осмысленными коммитами.

Работа выполняется «на месте» в целевом каталоге вне рабочего пространства Kiro. Платформа — Windows, командная оболочка — `cmd`/PowerShell. Файл `pipelines/bitnewton_sync.py` в рамках итерации не модифицируется, файл `kriterii_ocenki.txt` остаётся в корне целевого каталога.

## Glossary

- **Target_Repo**: локальный каталог проекта `C:\Users\koval\bat\bitrix24-automation`.
- **Hygiene_Iteration**: текущая итерация по организационной гигиене Target_Repo без изменения поведения пайплайна.
- **Pipeline_Script**: файл `pipelines/bitnewton_sync.py` в Target_Repo, основной пайплайн синхронизации.
- **Bat_Contract**: множество .bat-файлов в корне Target_Repo (`run_*.bat`, `menu.bat`, `setup_*.bat`, `install.bat`, `test_connection.bat`, `check_python*.bat`) и набор имён, путей и аргументов, которые они ожидают от Python-скриптов.
- **Bitrix_API_Module**: файл `bitrix24_api.py` в корне Target_Repo, содержащий класс `Bitrix24API`.
- **Bitrix_Package**: пакет `bitrix/` в Target_Repo (`bitrix/__init__.py`, `bitrix/api.py`, `bitrix/recordings.py`, `bitrix/dump_one_call_debug.py`).
- **Sync_Facade**: файл `bitnewton_sync_to_api.py` в корне Target_Repo.
- **Reports_Directory**: каталог `reports/` в Target_Repo.
- **Archive_Directory**: подкаталог `docs/_archive/` в Target_Repo для архивных заметок и документов итерации.
- **Hygiene_Notes**: .txt-файлы в корне Target_Repo, которые не являются контрактом сборки и относятся к устаревшим заметкам — `FIXED.txt`, `FIXED_ENCODING.txt`, `INSTALL_FFMPEG.txt`, `NEXT_STEP.txt`, `PROJECT_STRUCTURE.txt`, `PROJECT_SUMMARY.txt`, `README_FIRST.txt`, `SETUP_READY.txt`, `START_HERE.txt`, `SUCCESS.txt`, `TROUBLESHOOTING.txt`.
- **Protected_Txt**: .txt-файлы, которые остаются в корне Target_Repo без перемещения — `kriterii_ocenki.txt`, `requirements.txt`, `requirements_ui.txt`.
- **Build_Config**: файл `pyproject.toml` в корне Target_Repo.
- **Linter**: инструмент `ruff`, сконфигурированный через Build_Config.
- **Formatter**: инструмент `black`, сконфигурированный через Build_Config.
- **Logging_Module**: новый модуль `logging_setup.py` в корне Target_Repo, предоставляющий функцию инициализации логгера.
- **Transient_Artifacts**: временные и отладочные файлы в Reports_Directory — файлы вида `debug_download_*.html`, `debug_download_link_*.html`, `selenium_download_*/`, `streamlit_bitnewton.err.log`, `streamlit_bitnewton.out.log`, `chrome_profile/`, `call.mp3`.
- **Report_Outputs**: файлы отчётов в Reports_Directory вида `bitnewton_sync_report_*.json`, `bitnewton_sync_report_*.xlsx`, `bitnewton_reevaluated_report_*.json`, `latest_bitnewton_report.json`, `latest_bitnewton_report.xlsx`, `state_cache.json`, `deal_filter.json`.
- **Reports_TTL_Days**: параметр «время жизни» старых Report_Outputs в днях, по умолчанию `30`. Файлы Report_Outputs, чей `LastWriteTime` старше текущего момента на Reports_TTL_Days и более, подлежат удалению за исключениями, зафиксированными в Requirement 3.
- **Latest_Report_Files**: множество файлов в Reports_Directory, имена которых соответствуют шаблону `latest_bitnewton_report.*` (включая `latest_bitnewton_report.json`, `latest_bitnewton_report.xlsx`). Эти файлы семантически являются «указателями на последний отчёт» и не подлежат TTL-чистке по Reports_TTL_Days.
- **Singleton_Report_Files**: одиночные конфигурационно-состоянческие файлы в Reports_Directory — `state_cache.json`, `deal_filter.json`. Не подлежат ни TTL-чистке, ни чистке Transient_Artifacts.
- **Commit_History**: локальная история коммитов git-репозитория Target_Repo.
- **Facade_Decision**: задокументированное решение по роли `Bitrix_API_Module`, `Bitrix_Package` и `Sync_Facade`, закреплённое в дизайн-документе итерации.
- **Facade_Stub_Files**: множество файлов-«пустышек» пакетов — `bitrix/__init__.py`, `asr/__init__.py`, `ui/__init__.py`. Каждый из них проверяется отдельно и удаляется только при отсутствии использования имени пакета в импортах (см. Requirement 10).
- **Facade_Package_Import_Patterns**: регулярные паттерны импорта, по которым определяется использование пакета как пакета: для пакета `<name>` — вхождения `import <name>` (с последующей границей слова или концом строки), `from <name> import`, `import <name> as`, `from <name>.` в .py-файлах Target_Repo.
- **Scope_Python_Files**: множество Python-файлов, подпадающих под замену `print(...)` на вызовы логгера согласно Requirement 7 — все `*.py` в корне Target_Repo плюс рекурсивно все `*.py` в подкаталогах `bitrix/`, `asr/`, `ui/`, `pipelines/`. Из Scope_Python_Files явно исключаются: `pipelines/bitnewton_sync.py` (Requirement 4.1, неприкосновенность Pipeline_Script), `logging_setup.py` (Logging_Module — источник логгера), а также диагностические CLI-скрипты, у которых `print` является частью stdout-контракта с Bat_Contract (см. Requirement 7.11).
- **Stdout_Contract_Scripts**: подмножество Python-файлов, для которых `print(...)` является частью наблюдаемого stdout-контракта с внешними потребителями (Bat_Contract или иной парсер). Файл квалифицируется как Stdout_Contract_Script, если одновременно выполняются два условия: (а) существует `*.bat` в Target_Repo, который вызывает этот `*.py` файл, и (б) этот `*.bat` использует stdout вызываемого скрипта (через `for /f`, перенаправление `>`, `|`, или последующий анализ вывода). Примеры-кандидаты: `dump_one_call.py`, `check_python.py` при наличии соответствующих `.bat`-обёрток.

## Requirements

### Requirement 1: Инициализация локального git в целевом каталоге

**User Story:** Как сопровождающий Target_Repo, я хочу иметь локальный git-репозиторий в целевом каталоге, чтобы фиксировать организационные изменения итерации отдельными коммитами.

#### Acceptance Criteria

1. WHEN Hygiene_Iteration инициализирует репозиторий, THE Target_Repo SHALL содержать каталог `.git` в своём корне.
2. THE Hygiene_Iteration SHALL выполнять `git init` только в корне Target_Repo и SHALL NOT создавать git-репозитории в подкаталогах Target_Repo.
3. THE Hygiene_Iteration SHALL сохранить существующий файл `.gitignore` в корне Target_Repo без удаления строк, присутствовавших до итерации.
4. WHEN Hygiene_Iteration дополняет `.gitignore`, THE Hygiene_Iteration SHALL добавить записи для `pyproject.toml`-кэшей и каталогов инструментов (`.ruff_cache/`, `.pytest_cache/`, `.mypy_cache/`, `.venv/`, `venv/`, `__pycache__/`) только если такие записи отсутствуют.
5. IF в корне Target_Repo уже присутствует каталог `.git` на момент запуска итерации, THEN THE Hygiene_Iteration SHALL прекратить инициализацию и SHALL зафиксировать этот факт в отчёте итерации.
6. THE Hygiene_Iteration SHALL выполнить первичный коммит в Commit_History, содержащий только существующее на момент инициализации состояние Target_Repo и имеющий сообщение, отражающее старт итерации гигиены.

### Requirement 2: Архивирование устаревших .txt-заметок без изменения Bat_Contract

**User Story:** Как сопровождающий Target_Repo, я хочу переместить устаревшие корневые .txt-заметки в архивный подкаталог, чтобы корень проекта оставался читаемым и не смешивал документацию и контракт сборки.

#### Acceptance Criteria

1. THE Hygiene_Iteration SHALL переместить каждый файл из Hygiene_Notes в Archive_Directory с сохранением имени файла.
2. THE Hygiene_Iteration SHALL оставить каждый файл из Protected_Txt в корне Target_Repo без изменения пути и содержимого.
3. THE Hygiene_Iteration SHALL NOT изменять содержимое перемещённых Hygiene_Notes.
4. WHERE файл из Hygiene_Notes читается Bat_Contract или Python-скриптом, запускаемым Bat_Contract, THE Hygiene_Iteration SHALL исключить такой файл из перемещения и SHALL зафиксировать исключение в отчёте итерации.
5. IF после перемещения обнаруживается, что Bat_Contract ссылается на перемещённый файл Hygiene_Notes, THEN THE Hygiene_Iteration SHALL вернуть файл в корень Target_Repo до завершения итерации.
6. THE Hygiene_Iteration SHALL зафиксировать перемещение Hygiene_Notes отдельным коммитом в Commit_History с сообщением, описывающим архивирование заметок.

### Requirement 3: Чистка временных артефактов и устаревших отчётов в Reports_Directory

**User Story:** Как сопровождающий Target_Repo, я хочу удалить временные и отладочные артефакты и устаревшие по времени отчёты из Reports_Directory, чтобы каталог отчётов содержал только файлы, имеющие ценность, и не накапливал мусор.

#### Acceptance Criteria

1. THE Hygiene_Iteration SHALL удалить из Reports_Directory все файлы, соответствующие Transient_Artifacts.
2. THE Hygiene_Iteration SHALL сохранить в Reports_Directory все файлы, соответствующие Singleton_Report_Files, независимо от их возраста и содержимого.
3. THE Hygiene_Iteration SHALL расширить `.gitignore` в корне Target_Repo шаблонами, исключающими Transient_Artifacts из будущего отслеживания git, если такие шаблоны отсутствуют.
4. WHERE файл в Reports_Directory принадлежит семейству Report_Outputs (`bitnewton_sync_report_*.json`, `bitnewton_sync_report_*.xlsx`, `bitnewton_reevaluated_report_*.json`) и WHERE разница между текущим моментом выполнения итерации и значением `LastWriteTime` файла составляет Reports_TTL_Days дней или более, THE Hygiene_Iteration SHALL удалить этот файл.
5. THE Hygiene_Iteration SHALL сохранять каждый файл, принадлежащий Latest_Report_Files (шаблон `latest_bitnewton_report.*`), независимо от его `LastWriteTime` и независимо от значения Reports_TTL_Days.
6. THE Hygiene_Iteration SHALL использовать значение Reports_TTL_Days = 30 дней по умолчанию, с возможностью переопределения через параметр (константу), фиксируемый в дизайн-документе итерации.
7. IF файл в Reports_Directory не соответствует ни Transient_Artifacts, ни Report_Outputs, ни Singleton_Report_Files, ни Latest_Report_Files, THEN THE Hygiene_Iteration SHALL оставить файл без изменений и SHALL зафиксировать решение в отчёте итерации.
8. THE Hygiene_Iteration SHALL зафиксировать чистку Reports_Directory отдельным коммитом в Commit_History с сообщением, описывающим удаление временных артефактов и устаревших отчётов.

### Requirement 4: Сохранность Pipeline_Script и Bat_Contract

**User Story:** Как сопровождающий Target_Repo, я хочу гарантии, что итерация гигиены не изменит поведение пайплайна и контракт .bat-файлов, чтобы существующие сценарии запуска работали без правок.

#### Acceptance Criteria

1. THE Hygiene_Iteration SHALL NOT изменять содержимое Pipeline_Script.
2. THE Hygiene_Iteration SHALL NOT изменять содержимое и пути файлов, входящих в Bat_Contract.
3. THE Hygiene_Iteration SHALL NOT перемещать, переименовывать или удалять Python-скрипты, на которые ссылается Bat_Contract, включая `bit_newton_asr.py`, `bitnewton_sync_to_api.py`, `crm_contacts.py`, `crm_deals.py`, `crm_leads.py`, `crm_report.py`, `custom_period_report.py`, `detailed_calls_analysis.py`, `detailed_managers_report.py`, `managers_call_stats.py`, `managers_call_stats_auto.py`, `op_deals_analytics.py`, `op_full_analytics.py`, `op_lost_deals_analysis.py`, `ui_audio_downloader.py`, `web_ui.py`, `yesterday_leads.py`, `yesterday_leads_stats.py`.
4. IF в ходе итерации выявляется конфликт между требованием гигиены и сохранением Bat_Contract, THEN THE Hygiene_Iteration SHALL отложить соответствующее изменение и SHALL зафиксировать конфликт в отчёте итерации.
5. THE Hygiene_Iteration SHALL оставить файл `kriterii_ocenki.txt` в корне Target_Repo без перемещения и без изменения содержимого.

### Requirement 5: Фиксация решения по фасадам Bitrix

**User Story:** Как сопровождающий Target_Repo, я хочу зафиксированное решение о роли `bitrix24_api.py`, пакета `bitrix/` и `bitnewton_sync_to_api.py`, чтобы в следующих итерациях можно было осознанно удалять дублирование.

#### Acceptance Criteria

1. THE Hygiene_Iteration SHALL сформировать Facade_Decision, описывающий текущую роль Bitrix_API_Module, Bitrix_Package и Sync_Facade.
2. THE Facade_Decision SHALL указывать, какой модуль считается основным интерфейсом к Bitrix24 API на момент итерации.
3. THE Facade_Decision SHALL перечислять дубликаты функциональности между Bitrix_API_Module и Bitrix_Package и SHALL фиксировать план их устранения в будущих итерациях.
4. THE Hygiene_Iteration SHALL NOT удалять Bitrix_API_Module, `bitrix/api.py`, `bitrix/recordings.py`, `bitrix/dump_one_call_debug.py` или Sync_Facade в рамках текущей итерации. Удаление Facade_Stub_Files регулируется отдельно Requirement 10.
5. THE Hygiene_Iteration SHALL зафиксировать Facade_Decision в дизайн-документе итерации и SHALL оформить отдельный коммит в Commit_History, добавляющий документ решения.

### Requirement 6: Введение Build_Config с конфигурацией Linter и Formatter

**User Story:** Как сопровождающий Target_Repo, я хочу единый Build_Config с настройками `ruff` и `black`, чтобы линтинг и форматирование в проекте выполнялись одинаково у разных участников.

#### Acceptance Criteria

1. THE Hygiene_Iteration SHALL создать Build_Config в корне Target_Repo.
2. THE Build_Config SHALL содержать секцию конфигурации Linter и секцию конфигурации Formatter.
3. THE Build_Config SHALL задавать целевую версию Python, совпадающую с версией, ожидаемой существующими `check_python*.bat`, и зафиксированной в дизайн-документе итерации.
4. THE Build_Config SHALL задавать длину строки, одинаковую для Linter и Formatter.
5. THE Build_Config SHALL исключать из проверки каталоги `reports/`, `venv/`, `.venv/`, `__pycache__/`, `system--diarize/`, `asr/`, `ui/` и Archive_Directory.
6. THE Hygiene_Iteration SHALL NOT запускать автоформатирование или автоисправления Linter по существующему коду в рамках текущей итерации, за исключением Logging_Module и изменений в Scope_Python_Files, требуемых Requirement 7.
7. THE Hygiene_Iteration SHALL зафиксировать создание Build_Config отдельным коммитом в Commit_History с сообщением, описывающим введение конфигурации Linter и Formatter.

### Requirement 7: Logging_Module и замена print в Scope_Python_Files

**User Story:** Как сопровождающий Target_Repo, я хочу единую точку инициализации логирования и отсутствие `print` во всех файлах Scope_Python_Files, чтобы диагностика проекта шла через стандартный logging, а не через stdout-печать.

#### Acceptance Criteria

1. THE Hygiene_Iteration SHALL создать Logging_Module в корне Target_Repo.
2. THE Logging_Module SHALL предоставлять функцию инициализации логгера, принимающую имя логгера и уровень логирования.
3. THE Logging_Module SHALL настраивать вывод логов в стандартный поток ошибок с форматом, включающим временную метку, уровень и имя логгера.
4. WHEN любой файл из Scope_Python_Files импортируется, THE файл SHALL получать логгер через Logging_Module через конструкцию `from logging_setup import get_logger` и модульный `logger = get_logger(__name__)`.
5. THE Hygiene_Iteration SHALL заменить каждый вызов `print(...)` на вызов `logger.<level>(...)` в каждом файле, входящем в Scope_Python_Files.
6. WHEN файл из Scope_Python_Files фиксирует предупреждение о повторной попытке запроса или иной неблокирующей аномалии, THE файл SHALL вызывать логгер с уровнем `WARNING`.
7. WHEN файл из Scope_Python_Files фиксирует ошибку подключения, исключение сети или иной неуспешный результат операции, THE файл SHALL вызывать логгер с уровнем `ERROR` (допускается `logger.exception(...)` при наличии активного исключения).
8. WHEN файл из Scope_Python_Files фиксирует успешное завершение операции, подключение или значимое информационное событие, THE файл SHALL вызывать логгер с уровнем `INFO`.
9. WHERE файл из Scope_Python_Files фиксирует отладочный дамп или диагностическое содержимое, предназначенное только для разработчика, THE файл SHALL вызывать логгер с уровнем `DEBUG`.
10. THE Hygiene_Iteration SHALL NOT модифицировать файл `pipelines/bitnewton_sync.py` в рамках Requirement 7 (исключение по Requirement 4.1, приоритет Pipeline_Script).
11. IF файл из Scope_Python_Files квалифицируется как Stdout_Contract_Script (см. Glossary), THEN THE Hygiene_Iteration SHALL исключить этот файл из замены `print` и SHALL зафиксировать исключение в отчёте итерации с указанием `.bat`-файла, использующего его stdout.
12. THE Hygiene_Iteration SHALL NOT модифицировать файл `logging_setup.py` в рамках замены `print` (Logging_Module — источник логгера, исключение фиксируется в дизайн-документе).
13. THE Hygiene_Iteration SHALL сохранять публичный интерфейс каждого класса и модульной функции в каждом файле Scope_Python_Files без изменения сигнатур, имён и возвращаемых типов.
14. THE Hygiene_Iteration SHALL оформить изменения, описанные в Requirement 7, в рамках одной логической итерации коммитов — единым коммитом S7 «logging» либо серией связанных под-коммитов, выбор закрепляется в дизайн-документе итерации.
15. THE Hygiene_Iteration SHALL зафиксировать введение Logging_Module и замену `print` в Scope_Python_Files коммитом S7 (или серией под-коммитов S7.*) в Commit_History с сообщением, описывающим переход на logging.

### Requirement 8: Осмысленная структура Commit_History итерации

**User Story:** Как сопровождающий Target_Repo, я хочу, чтобы история коммитов итерации отражала отдельные логические изменения, чтобы последующий анализ и откат были простыми.

#### Acceptance Criteria

1. THE Hygiene_Iteration SHALL оформлять изменения, описанные в Requirements 1, 2, 3, 5, 6, 7 и 10, отдельными коммитами в Commit_History.
2. THE Commit_History SHALL содержать коммиты в следующем позиционном порядке: S1 — инициализация репозитория (Requirement 1), S2 — архивирование Hygiene_Notes (Requirement 2), S3 — чистка Reports_Directory (Requirement 3), S4 — фиксация Facade_Decision (Requirement 5), S5 — удаление Facade_Stub_Files с сообщением `chore(hygiene): remove unused facade __init__.py files` (Requirement 10), S6 — введение Build_Config (Requirement 6), S7 — введение Logging_Module и замена `print` в Scope_Python_Files (Requirement 7).
3. THE Commit_History SHALL содержать сообщения коммитов на русском или английском языке, каждое из которых однозначно отражает содержание соответствующего шага итерации.
4. THE Hygiene_Iteration SHALL NOT объединять изменения из разных Requirements в один коммит, за исключением серии под-коммитов S7.* в рамках одной логической итерации замены `print` (Requirement 7.14).
5. IF один из шагов итерации не вносит изменений в Target_Repo, THEN THE Hygiene_Iteration SHALL пропустить соответствующий коммит и SHALL зафиксировать причину пропуска в отчёте итерации; позиционные номера S1..S7 при этом не сдвигаются, пропущенная позиция остаётся пустой.
6. IF коммит S5 пропускается по Requirement 8.5 (ни один из Facade_Stub_Files не подлежит удалению по условиям Requirement 10), THEN THE Hygiene_Iteration SHALL зафиксировать grep-отчёт по трём пакетам `bitrix`, `asr`, `ui` в отчёте итерации в качестве обоснования пропуска.

### Requirement 9: Документирование решений фазы Clarify

**User Story:** Как сопровождающий Target_Repo, я хочу, чтобы зафиксированные в фазе Clarify решения были отражены в артефактах спека, чтобы следующий агент мог продолжить итерацию без потери контекста.

#### Acceptance Criteria

1. THE Hygiene_Iteration SHALL зафиксировать в артефактах спека следующие решения фазы Clarify: файл `kriterii_ocenki.txt` остаётся в корне Target_Repo; Pipeline_Script в итерации не модифицируется; Bat_Contract в итерации не модифицируется; работа ведётся «на месте» в Target_Repo вне рабочего пространства Kiro; платформа — Windows, оболочка — `cmd`/PowerShell.
2. THE Hygiene_Iteration SHALL отражать ограничения Requirement 4 в дизайн-документе итерации перед началом реализации.
3. WHERE решение фазы Clarify противоречит последующему запросу пользователя, THE Hygiene_Iteration SHALL остановиться и SHALL запросить уточнение до внесения изменений.

### Requirement 10: Удаление неиспользуемых Facade_Stub_Files

**User Story:** Как сопровождающий Target_Repo, я хочу удалить физически пустые `__init__.py` пакетов `bitrix/`, `asr/`, `ui/`, если ни один из этих пакетов фактически не импортируется как пакет, чтобы не поддерживать фасадные файлы, существование которых не нужно ни Python-импорту, ни Bat_Contract. Семантически это продолжение Facade_Decision (Requirement 5), позиционно в Commit_History — коммит S5.

#### Acceptance Criteria

1. THE Hygiene_Iteration SHALL выполнить grep-проверку использования имени каждого пакета из множества `{bitrix, asr, ui}` по Facade_Package_Import_Patterns во всех `*.py`-файлах Target_Repo (исключая файл самого проверяемого `__init__.py` и каталоги `venv/`, `.venv/`, `__pycache__/`, `reports/`, `system--diarize/`, `docs/`).
2. WHERE grep-проверка пакета `<name>` из `{bitrix, asr, ui}` не находит ни одного совпадения по Facade_Package_Import_Patterns, THE Hygiene_Iteration SHALL удалить файл `<name>/__init__.py` из Target_Repo.
3. IF grep-проверка пакета `<name>` из `{bitrix, asr, ui}` находит хотя бы одно совпадение по Facade_Package_Import_Patterns, THEN THE Hygiene_Iteration SHALL отменить удаление `<name>/__init__.py`, сохранить файл без изменений, SHALL зафиксировать факт и пути найденных использований в отчёте итерации.
4. THE Hygiene_Iteration SHALL зафиксировать в отчёте итерации grep-отчёт для каждого из трёх пакетов `bitrix`, `asr`, `ui` независимо от того, был ли удалён соответствующий `__init__.py`.
5. THE Hygiene_Iteration SHALL NOT удалять файлы `bitrix/api.py`, `bitrix/recordings.py`, `bitrix/dump_one_call_debug.py` и любые другие `*.py` внутри каталогов `bitrix/`, `asr/`, `ui/` в рамках Requirement 10.
6. WHERE удаление `bitrix/__init__.py` выполнено по Requirement 10.2 и каталог `bitrix/` содержит другие `*.py` файлы (например, `bitrix/api.py`), THE Hygiene_Iteration SHALL полагаться на поведение namespace packages (Python 3) и SHALL NOT создавать заменитель `__init__.py` для восстановления статуса пакета. Импорт вида `from bitrix.api import X` в Python 3 не зависит от наличия `__init__.py`.
7. THE Hygiene_Iteration SHALL зафиксировать удаление Facade_Stub_Files отдельным коммитом S5 в Commit_History с сообщением `chore(hygiene): remove unused facade __init__.py files`.
8. IF все три файла Facade_Stub_Files сохранены по Requirement 10.3 (каждый из пакетов реально используется как пакет), THEN THE Hygiene_Iteration SHALL пропустить коммит S5 согласно Requirement 8.5 и SHALL зафиксировать grep-отчёт как обоснование пропуска согласно Requirement 8.6.
9. THE Hygiene_Iteration SHALL выполнить коммит S5 строго после коммита S4 (Facade_Decision, Requirement 5) и строго до коммита S6 (Build_Config, Requirement 6) в позиционном порядке Commit_History.
