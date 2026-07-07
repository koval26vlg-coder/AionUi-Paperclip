# План задач: bitrix24-automation-hygiene

> Статус на 2026-07-06 (Claude Code): задачи 1-9, 11, 12 выполнены, подтверждено git-историей
> bitrix24-automation (коммиты fd08574, 5303f29, 7b5afa7, 24dc451, e634d77, ac4cea0, 632227b,
> 00b89b3, 4137b1e). Открыты: задача 10 (S7.3 - web_ui.py и ui_audio_downloader.py еще на print)
> и задача 13 (финальная сверка инвариантов).

## Обзор

План реализации итерации «гигиена» в целевом каталоге `C:\Users\koval\bat\bitrix24-automation` в 7 позиционных коммитов (S1..S7) согласно `design.md`, с разбиением S7 на серию под-коммитов S7.1..S7.5 по Requirement 7.14. Работа выполняется «на месте» вне рабочего пространства Kiro, платформа — Windows, оболочка — `cmd`/PowerShell. Язык изменений — Python (для `logging_setup.py` и точечных правок Scope_Python_Files), TOML (`pyproject.toml`), Markdown (`FACADE_DECISION.md`) и PowerShell (для файловых операций). Автоформатирование и автофиксы линтера по существующему коду запрещены на протяжении всей итерации (Requirement 6.6, Риск R5, EH6).

Перед S1 фиксируется read-only baseline: проверка `git --version`, проверка отсутствия `.git`, снимок SHA-256 по защищаемым файлам (Pipeline_Script, Bat_Contract, 17 Python-скриптов из Requirement 4.3, `bitrix24_api.py`, файлы пакетов `bitrix/`, `asr/`, `ui/`, Sync_Facade), снимок публичного API `Bitrix24API` для Property 7, а также snapshot наличия `print(` в каждом файле Scope_Python_Files для Property 12. После каждого позиционного коммита — отдельная проверочная задача с командами из раздела «План проверки» дизайна. В начале S7.1 — отдельная задача «Определение `Stdout_Contract_Scripts`», результат которой фиксируется в отчёте итерации и используется всеми под-коммитами S7.1..S7.5.

Каждая задача ссылается на конкретные Requirements (см. `requirements.md`) и компоненты дизайна (C1..C8, DM1..DM4, EH1..EH12, R1..R12, P1..P12, S1..S7). Каждая модифицирующая задача содержит блок `Rollback`. Задачи не трогают `pipelines\bitnewton_sync.py` (Requirement 4.1, 7.10), Bat_Contract (`.bat`-файлы, Requirement 4.2) и `.env` ни в одном шаге. Обязательный порядок коммитов: S1 → S2 → S3 → S4 → (S5) → S6 → S7.1 → S7.2 → S7.3 → S7.4 → S7.5; любой позиционный коммит или под-коммит S7.x пропускается без сдвига номеров, если в его наборе файлов нет кандидатов на изменение (Requirement 8.5).

## Задачи

- [x] 1. Baseline — read-only подготовка перед S1
  - [-] 1.1 Проверить наличие `git` в PATH
    - Выполнить в корне Target_Repo: `git --version`.
    - Если команда не найдена — остановить итерацию, зафиксировать причину в отчёте итерации (EH1, Риск R1). Пользователю рекомендуется установить Git for Windows или скорректировать PATH.
    - Ожидаемый результат: в отчёте итерации строка версии вида `git version 2.x.y.windows.z`.
    - Rollback: не требуется (read-only).
    - _Компонент: EH1, Риск R1_
    - _Requirements: 1.1, 9.1_
  - [-] 1.2 Проверить отсутствие каталога `.git` в корне Target_Repo
    - Выполнить: `Test-Path .git`.
    - Ожидаемое значение: `False`. Если `True` — применить EH2: пропустить `git init` в 2.1, но продолжить идемпотентное дополнение `.gitignore` в 2.2; зафиксировать факт в отчёте итерации (Requirement 1.5).
    - Rollback: не требуется (read-only).
    - _Компонент: EH2_
    - _Requirements: 1.2, 1.5_
  - [-] 1.3 Снять SHA-256 снапшот защищаемых файлов для Property 5
    - Посчитать `Get-FileHash -Algorithm SHA256` для набора:
      - `pipelines\bitnewton_sync.py` (Pipeline_Script),
      - все файлы Bat_Contract: `run_*.bat`, `menu.bat`, `setup_*.bat`, `install.bat`, `test_connection.bat`, `check_python*.bat`,
      - 17 Python-скриптов Bat_Contract из Requirement 4.3 (`bit_newton_asr.py`, `bitnewton_sync_to_api.py`, `crm_contacts.py`, `crm_deals.py`, `crm_leads.py`, `crm_report.py`, `custom_period_report.py`, `detailed_calls_analysis.py`, `detailed_managers_report.py`, `managers_call_stats.py`, `managers_call_stats_auto.py`, `op_deals_analytics.py`, `op_full_analytics.py`, `op_lost_deals_analysis.py`, `ui_audio_downloader.py`, `web_ui.py`, `yesterday_leads.py`, `yesterday_leads_stats.py`),
      - `bitrix24_api.py`,
      - `bitrix\__init__.py`, `bitrix\api.py`, `bitrix\recordings.py`, `bitrix\dump_one_call_debug.py`,
      - `asr\__init__.py`, `asr\bitnewton.py`,
      - `ui\__init__.py`, `ui\audio_downloader.py` (если существует).
    - Сохранить результат в файл вне Target_Repo (например, `C:\Users\koval\bat\_hygiene-baseline\sha256.txt`) или в `reports\_hygiene_baseline_sha256.txt` внутри Target_Repo с добавлением `reports\_hygiene_*` в `.gitignore` при необходимости.
    - Rollback: не требуется (read-only).
    - _Компонент: P5, DM1, Риск R7_
    - _Requirements: 4.1, 4.2, 4.3, 4.5, 5.4_
  - [-] 1.4 Снять baseline публичного API класса `Bitrix24API` (Property 7)
    - Выполнить: `python -c "from bitrix24_api import Bitrix24API; import inspect; [print(n, inspect.signature(getattr(Bitrix24API,n))) for n in dir(Bitrix24API) if not n.startswith('_') and callable(getattr(Bitrix24API,n))]"`.
    - Сохранить вывод в файл вне Target_Repo или в `reports\_hygiene_baseline_api.txt` для сверки после S7.1.
    - Rollback: не требуется (read-only).
    - _Компонент: P7, Риск R7_
    - _Requirements: 7.13_
  - [-] 1.5 Снять baseline наличия `print(` в каждом файле Scope_Python_Files (Property 12)
    - Собрать список Scope_Python_Files: все `*.py` в корне Target_Repo + рекурсивно `bitrix\`, `asr\`, `ui\`, `pipelines\`, исключая `__pycache__\`, `venv\`, `.venv\`, `system--diarize\`, `reports\`, `docs\`, `logging_setup.py` (ещё не существует) и `pipelines\bitnewton_sync.py`.
    - Для каждого файла выполнить: `Select-String -Path <file> -Pattern '^\s*print\(' | Measure-Object`.
    - Сохранить таблицу `(файл, count_print)` в `reports\_hygiene_baseline_prints.txt` (или вне репозитория) для последующей сверки Property 12 после S7.1..S7.5.
    - Rollback: не требуется (read-only).
    - _Компонент: P12, DM1, C7_
    - _Requirements: 7.4, 7.5_

- [x] 2. S1 — инициализация локального git и baseline `.gitignore`
  - [~] 2.1 Выполнить `git init` в корне Target_Repo
    - Предусловие: задачи 1.1 и 1.2 пройдены, `.git` отсутствует.
    - Команда: `git init` в корне Target_Repo.
    - Если `.git` уже существует (EH2) — шаг пропускается, но 2.2 выполняется идемпотентно.
    - Rollback: `Remove-Item -Recurse -Force .git` (только если `.git` был создан этой задачей и до коммита S1).
    - _Компонент: S1, EH2_
    - _Requirements: 1.1, 1.2_
  - [~] 2.2 Дополнить `.gitignore` идемпотентным tooling-блоком
    - Использовать функцию `Add-GitignoreLines` (C2). Добавить только отсутствующие строки:
      - `.ruff_cache/`, `.pytest_cache/`, `.mypy_cache/`, `.cache/`, `*.log`, `.venv/`, `venv/`, `__pycache__/`.
    - Существующие строки `.gitignore` не удалять (Requirement 1.3).
    - Повторный прогон не должен менять файл (Property 1).
    - Rollback: `git restore .gitignore` (до коммита S1) либо удаление добавленных строк вручную.
    - _Компонент: C2, DM4, P1_
    - _Requirements: 1.3, 1.4_
  - [~] 2.3 Создать коммит S1 с сообщением `chore(hygiene): init local git and baseline .gitignore`
    - `git add -A`; `git commit -m "chore(hygiene): init local git and baseline .gitignore"`.
    - В первый коммит попадает существующее на момент инициализации состояние Target_Repo (Requirement 1.6) плюс обновлённый `.gitignore`.
    - Rollback: `git update-ref -d HEAD` (откат первого коммита) либо `git reset --soft HEAD~1` для последующих; при необходимости — `Remove-Item -Recurse -Force .git`.
    - _Компонент: S1, DM1, P8_
    - _Requirements: 1.6, 8.1, 8.2, 8.3, 8.4_
  - [~] 2.4 Проверки после S1
    - `Test-Path .git` → `True`.
    - `git log --oneline` → 1 коммит, сообщение соответствует S1.
    - `Get-Content .gitignore | Select-String -Pattern '\.ruff_cache','\.pytest_cache','\.mypy_cache','__pycache__','venv','\.venv','\.cache','\*\.log'` → все 8 шаблонов найдены.
    - Property 1: повторный вызов `Add-GitignoreLines` с тем же набором строк не меняет SHA-256 файла (`Get-FileHash .gitignore -Algorithm SHA256` до и после — одинаковый).
    - Расхождения фиксируются в отчёте итерации.
    - Rollback: не требуется (read-only).
    - _Компонент: План проверки «После S1», P1_
    - _Requirements: 1.1, 1.4, 1.6_

- [x] 3. S2 — архивирование устаревших `.txt`-заметок в `docs\_archive\`
  - [~] 3.1 Grep Hygiene_Notes по `*.bat` и `*.py` перед перемещением
    - Для каждого имени из Hygiene_Notes (11 файлов по C1): `FIXED.txt`, `FIXED_ENCODING.txt`, `INSTALL_FFMPEG.txt`, `NEXT_STEP.txt`, `PROJECT_STRUCTURE.txt`, `PROJECT_SUMMARY.txt`, `README_FIRST.txt`, `SETUP_READY.txt`, `START_HERE.txt`, `SUCCESS.txt`, `TROUBLESHOOTING.txt` — выполнить: `Get-ChildItem -Recurse -Include *.bat,*.py -Exclude __pycache__,venv,.venv,reports,system--diarize,docs | Select-String -Pattern ([regex]::Escape('<имя>')) -SimpleMatch`.
    - Имена с ≥1 совпадением — исключить из перемещения и зафиксировать в отчёте итерации (Requirement 2.4, EH4, Риск R3).
    - Rollback: не требуется (read-only).
    - _Компонент: C1, EH4, Риск R3_
    - _Requirements: 2.4, 2.5_
  - [~] 3.2 Создать каталог `docs\_archive\` в корне Target_Repo
    - `New-Item -ItemType Directory -Force -Path docs\_archive | Out-Null` (идемпотентно, Риск R8).
    - Rollback: `Remove-Item -Recurse -Force docs\_archive` (только если каталог пуст и создан этой задачей, до коммита S2).
    - _Компонент: C1, Риск R8_
    - _Requirements: 2.1_
  - [~] 3.3 Переместить Hygiene_Notes в `docs\_archive\` через `git mv`
    - Для каждого имени, прошедшего 3.1: проверить `Test-Path docs\_archive\<имя>` → если уже существует, пропустить с фиксацией в отчёте (EH3, Риск R2); иначе `git mv <имя> docs\_archive\<имя>`.
    - Protected_Txt (`kriterii_ocenki.txt`, `requirements.txt`, `requirements_ui.txt`) не трогать (Requirement 2.2, 4.5, 9.1).
    - Содержимое перемещаемых файлов не изменять (Requirement 2.3, Property 2).
    - Rollback: для каждого перемещённого файла `git mv docs\_archive\<имя> <имя>` (до коммита S2) либо `git restore --staged --worktree .`.
    - _Компонент: C1, P2, EH3, Риск R2_
    - _Requirements: 2.1, 2.2, 2.3, 4.5_
  - [~] 3.4 Создать коммит S2 с сообщением `chore(hygiene): archive legacy .txt notes into docs/_archive/`
    - `git add docs\_archive` и удалённые пути; `git commit -m "chore(hygiene): archive legacy .txt notes into docs/_archive/"`.
    - В коммит попадают только перемещения Hygiene_Notes (DM1, Property 8).
    - Если все файлы исключены в 3.1 — пропустить коммит и зафиксировать причину (Requirement 8.5); позиционный номер S2 остаётся пустым.
    - Rollback: `git reset --soft HEAD~1` и `git restore --staged .`; вручную вернуть файлы `git mv docs\_archive\<имя> <имя>`.
    - _Компонент: S2, DM1, P8_
    - _Requirements: 2.6, 8.1, 8.2, 8.4, 8.5_
  - [~] 3.5 Проверки после S2
    - `Test-Path docs\_archive` → `True`.
    - Для каждого перенесённого `<имя>` из Hygiene_Notes: `Test-Path <имя>` → `False`, `Test-Path docs\_archive\<имя>` → `True`.
    - Property 2: SHA-256 каждого перемещённого файла в `docs\_archive\<имя>` равен baseline-значению из 1.3.
    - `Test-Path kriterii_ocenki.txt`, `Test-Path requirements.txt`, `Test-Path requirements_ui.txt` → все `True` (Protected_Txt).
    - `git log --oneline` → 2 коммита (или 1, если S2 пропущен).
    - Rollback: не требуется (read-only).
    - _Компонент: План проверки «После S2», P2_
    - _Requirements: 2.1, 2.2, 2.3, 4.5_

- [x] 4. S3 — чистка `reports\` (Transient_Artifacts + TTL 30 дней для Report_Outputs)
  - [~] 4.1 Удалить Transient_Artifacts в `reports\`
    - Выполнить набор из C3 (идемпотентно):
      - `Remove-Item -Force -ErrorAction SilentlyContinue reports\debug_download_*.html`
      - `Remove-Item -Force -ErrorAction SilentlyContinue reports\debug_download_link_*.html`
      - `Remove-Item -Force -Recurse -ErrorAction SilentlyContinue reports\selenium_download_*`
      - `Remove-Item -Force -ErrorAction SilentlyContinue reports\streamlit_bitnewton.*.log`
      - `Remove-Item -Force -Recurse -ErrorAction SilentlyContinue reports\chrome_profile`
      - `Remove-Item -Force -ErrorAction SilentlyContinue reports\call.mp3`
    - Заблокированные процессом Chrome/Selenium файлы — по EH8 (закрыть процесс и повторить; операция идемпотентна, Риск R6).
    - Rollback: не требуется — Transient_Artifacts не версионируются и не восстанавливаются; до коммита S3 — `git restore --worktree -- reports` для случайно удалённых отслеживаемых файлов.
    - _Компонент: C3, EH8, Риск R6_
    - _Requirements: 3.1_
  - [~] 4.2 Удалить каталог `reports\Transient_Artifacts\` (если присутствует отдельной папкой)
    - Проверить `Test-Path reports\Transient_Artifacts` (исторический каталог, если был создан в предыдущей итерации). Если существует — `Remove-Item -Force -Recurse reports\Transient_Artifacts`.
    - Если каталог отсутствует — задача no-op; зафиксировать в отчёте итерации.
    - Rollback: не требуется (Transient_Artifacts не версионируются).
    - _Компонент: C3_
    - _Requirements: 3.1_
  - [~] 4.3 Применить `Remove-ExpiredReports` к `reports\bitnewton_sync_report_*.json` (TTL 30 дней)
    - Использовать функцию `Remove-ExpiredReports -Pattern 'reports\bitnewton_sync_report_*.json' -TtlDays 30` (C3).
    - Функция явно защищает файлы `latest_bitnewton_report.*` (Latest_Report_Files) и `state_cache.json`/`deal_filter.json` (Singleton_Report_Files) именем.
    - Удаляются только файлы, чей `LastWriteTime < now - 30д`.
    - Rollback: до коммита S3 — `git restore --worktree --staged -- reports` для отслеживаемых файлов; не версионированные отчёты восстановлению не подлежат.
    - _Компонент: C3, P9_
    - _Requirements: 3.4, 3.5, 3.6_
  - [~] 4.4 Применить `Remove-ExpiredReports` к `reports\bitnewton_sync_report_*.xlsx` (TTL 30 дней)
    - `Remove-ExpiredReports -Pattern 'reports\bitnewton_sync_report_*.xlsx' -TtlDays 30` (C3).
    - Защищены Latest_Report_Files и Singleton_Report_Files по имени.
    - Rollback: до коммита S3 — `git restore --worktree --staged -- reports`.
    - _Компонент: C3, P9_
    - _Requirements: 3.4, 3.5, 3.6_
  - [~] 4.5 Применить `Remove-ExpiredReports` к `reports\bitnewton_reevaluated_report_*.json` (TTL 30 дней)
    - `Remove-ExpiredReports -Pattern 'reports\bitnewton_reevaluated_report_*.json' -TtlDays 30` (C3).
    - Защищены Latest_Report_Files и Singleton_Report_Files по имени.
    - Rollback: до коммита S3 — `git restore --worktree --staged -- reports`.
    - _Компонент: C3, P9_
    - _Requirements: 3.4, 3.5, 3.6_
  - [~] 4.6 Подтвердить консервативность: файлы вне категорий не тронуты (Property 4)
    - Выполнить перечисление `Get-ChildItem -Path reports -File` и сверить, что файлы, не соответствующие ни Transient_Artifacts, ни Report_Outputs, ни Latest_Report_Files, ни Singleton_Report_Files, присутствуют с теми же именами и SHA-256, что и до S3.
    - Зафиксировать такой перечень (с комментарием «оставлено без изменений») в отчёте итерации (Requirement 3.7, Property 4).
    - Rollback: не требуется (read-only).
    - _Компонент: C3, P4_
    - _Requirements: 3.7_
  - [~] 4.7 Дополнить `.gitignore` идемпотентным блоком для Transient_Artifacts
    - Использовать `Add-GitignoreLines` (C2). Добавить только отсутствующие строки:
      - `reports/debug_download_*.html`
      - `reports/debug_download_link_*.html`
      - `reports/selenium_download_*/`
      - `reports/streamlit_bitnewton.*.log`
      - `reports/chrome_profile/`
      - `reports/call.mp3`
      - `reports/logs/*.log`
      - `reports/logs/*.log.*`
    - Rollback: `git restore .gitignore` (до коммита S3).
    - _Компонент: C2, DM4, P1_
    - _Requirements: 3.3_
  - [~] 4.8 Создать коммит S3 с сообщением `chore(hygiene): cleanup transient artifacts and expire old reports (TTL 30d)`
    - `git add -A reports .gitignore`; `git commit -m "chore(hygiene): cleanup transient artifacts and expire old reports (TTL 30d)"`.
    - В коммит попадают только удаления в `reports\` (Transient_Artifacts + просроченные Report_Outputs) и добавления в `.gitignore` (DM1, Property 8).
    - Если не было ни одного удаления и `.gitignore` уже содержит все шаблоны — пропустить коммит и зафиксировать причину (Requirement 8.5).
    - Rollback: `git reset --soft HEAD~1` и `git restore --staged .`.
    - _Компонент: S3, DM1, P8_
    - _Requirements: 3.8, 8.1, 8.2, 8.4, 8.5_
  - [~] 4.9 Проверки после S3
    - `Get-ChildItem reports\debug_download_*.html, reports\debug_download_link_*.html, reports\selenium_download_*, reports\streamlit_bitnewton.*.log, reports\chrome_profile, reports\call.mp3 -ErrorAction SilentlyContinue` → пустой список (Property 3).
    - Property 9: `$cutoff = (Get-Date).AddDays(-30); Get-ChildItem reports\bitnewton_sync_report_*.json, reports\bitnewton_sync_report_*.xlsx, reports\bitnewton_reevaluated_report_*.json | Where-Object { $_.LastWriteTime -lt $cutoff -and $_.Name -notlike 'latest_bitnewton_report.*' -and $_.Name -ne 'state_cache.json' -and $_.Name -ne 'deal_filter.json' }` → пустой список.
    - Latest_Report_Files присутствуют: `Get-ChildItem reports\latest_bitnewton_report.* -ErrorAction SilentlyContinue` → непустой список, если такие файлы существовали до S3.
    - Singleton_Report_Files присутствуют: `Test-Path reports\state_cache.json` → `True`, `Test-Path reports\deal_filter.json` → `True`.
    - `.gitignore` расширен: `Get-Content .gitignore | Select-String -Pattern 'reports/debug_download','reports/selenium_download','streamlit_bitnewton','reports/chrome_profile','reports/call\.mp3','reports/logs'` → все шаблоны найдены.
    - `git log --oneline` → 3 коммита (или меньше при пропусках).
    - Rollback: не требуется (read-only).
    - _Компонент: План проверки «После S3», P3, P4, P9_
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7_

- [x] 5. S4 — фиксация решения по фасадам Bitrix (`FACADE_DECISION.md`)
  - [~] 5.1 Grep публичного API `bitrix24_api.py` и модулей пакета `bitrix\`
    - Выполнить: `Select-String -Path bitrix24_api.py -Pattern '^\s*def ','^\s*class '` и аналогично для `bitrix\api.py`, `bitrix\recordings.py`, `bitrix\dump_one_call_debug.py`.
    - Сформировать список публичных символов (имена, не начинающиеся с `_`) и выявить совпадающие имена между `bitrix24_api.py` и файлами пакета `bitrix\` — это «дубликаты» для раздела «Перечень дубликатов» в `FACADE_DECISION.md`.
    - Сохранить список в отчёт итерации.
    - Rollback: не требуется (read-only).
    - _Компонент: C4, Requirement 5.3_
    - _Requirements: 5.3_
  - [~] 5.2 Создать файл `docs\_archive\FACADE_DECISION.md`
    - Структура документа (C4):
      - Роль `bitrix24_api.py` (Bitrix_API_Module) — основная точка входа к Bitrix24 REST API (Requirement 5.2).
      - Роль пакета `bitrix\` (Bitrix_Package) — частичный дубликат, кандидат на превращение в re-export shim в будущих итерациях.
      - Роль `bitnewton_sync_to_api.py` (Sync_Facade) — тонкая CLI-обёртка для Bat_Contract.
      - Перечень дубликатов из 5.1.
      - План устранения (шаги 1..5 из C4): инвентаризация публичных символов, выделение канонического API, shim, удаление дублирующего кода, миграция Sync_Facade.
      - Явное указание: дубликаты не удаляются в этой итерации (Requirement 5.4).
    - Rollback: `Remove-Item -Force docs\_archive\FACADE_DECISION.md` (до коммита S4) или `git restore --staged --worktree docs\_archive\FACADE_DECISION.md`.
    - _Компонент: C4_
    - _Requirements: 5.1, 5.2, 5.3, 5.4_
  - [~] 5.3 Создать коммит S4 с сообщением `docs(hygiene): record facade decision for bitrix24_api / bitrix / bitnewton_sync_to_api`
    - `git add docs\_archive\FACADE_DECISION.md`; `git commit -m "docs(hygiene): record facade decision for bitrix24_api / bitrix / bitnewton_sync_to_api"`.
    - В коммит попадает только `docs\_archive\FACADE_DECISION.md` (DM1, Property 8).
    - Rollback: `git reset --soft HEAD~1` и `git restore --staged docs\_archive\FACADE_DECISION.md`.
    - _Компонент: S4, DM1, P8_
    - _Requirements: 5.5, 8.1, 8.2, 8.4_
  - [~] 5.4 Проверки после S4
    - `Test-Path docs\_archive\FACADE_DECISION.md` → `True`.
    - `Select-String -Path docs\_archive\FACADE_DECISION.md -Pattern 'bitrix24_api','bitrix[/\\]','bitnewton_sync_to_api'` → все три шаблона найдены.
    - `git show --stat HEAD` — изменён только `docs\_archive\FACADE_DECISION.md`.
    - `git log --oneline` → 4 коммита (или меньше при пропусках S2/S3).
    - Rollback: не требуется (read-only).
    - _Компонент: План проверки «После S4»_
    - _Requirements: 5.1, 5.2, 5.5_

- [x] 6. S5 — удаление неиспользуемых `Facade_Stub_Files` (может быть пропущен)
  - [~] 6.1 Grep по `Facade_Package_Import_Patterns` для пакета `bitrix`
    - Собрать список `*.py` в Target_Repo с исключениями: `__pycache__\`, `venv\`, `.venv\`, `reports\`, `system--diarize\`, `docs\` и сам файл `bitrix\__init__.py`.
    - Прогнать четыре паттерна (C8):
      1. `^\s*import bitrix\b`
      2. `^\s*from bitrix\b`
      3. `^\s*from bitrix\.`
      4. `^\s*import bitrix\s+as\b`
    - Дополнительно: `^\s*from\s+bitrix\s+import\s+Bitrix24API\b` (особый кейс re-export, C8).
    - Зафиксировать в отчёте итерации найденные совпадения построчно (`path:line`) независимо от итогового решения (Requirement 10.4).
    - Rollback: не требуется (read-only).
    - _Компонент: C8, Риск R9_
    - _Requirements: 10.1, 10.4_
  - [~] 6.2 Решение по `bitrix\__init__.py`
    - Если задача 6.1 нашла 0 совпадений по всем пяти паттернам — выполнить `git rm bitrix\__init__.py` (Requirement 10.2). Намечать к коммиту S5.
    - Если найден хотя бы один импорт по любому из паттернов (включая `from bitrix import Bitrix24API`) — файл сохранить без изменений, зафиксировать обоснование в отчёте итерации (Requirement 10.3, C8 особый кейс).
    - Для Python 3 при удалении `__init__.py` каталог `bitrix\` становится namespace-package; импорты `from bitrix.api import X` продолжают работать (Requirement 10.6).
    - НЕ удалять `bitrix\api.py`, `bitrix\recordings.py`, `bitrix\dump_one_call_debug.py` (Requirement 10.5).
    - Rollback: до коммита S5 — `git restore --staged --worktree bitrix\__init__.py`.
    - _Компонент: C8, P10, Риск R9_
    - _Requirements: 10.2, 10.3, 10.5, 10.6_
  - [~] 6.3 Grep по `Facade_Package_Import_Patterns` для пакета `asr`
    - Собрать список `*.py` с теми же исключениями, исключая `asr\__init__.py`.
    - Четыре паттерна: `^\s*import asr\b`, `^\s*from asr\b`, `^\s*from asr\.`, `^\s*import asr\s+as\b`.
    - Зафиксировать совпадения в отчёте итерации (Requirement 10.4).
    - Rollback: не требуется (read-only).
    - _Компонент: C8, Риск R9_
    - _Requirements: 10.1, 10.4_
  - [~] 6.4 Решение по `asr\__init__.py`
    - Если 0 совпадений — `git rm asr\__init__.py` (Requirement 10.2).
    - Если ≥1 совпадение — сохранить без изменений, зафиксировать обоснование.
    - Rollback: до коммита S5 — `git restore --staged --worktree asr\__init__.py`.
    - _Компонент: C8, P10_
    - _Requirements: 10.2, 10.3_
  - [~] 6.5 Grep по `Facade_Package_Import_Patterns` для пакета `ui`
    - Собрать список `*.py` с теми же исключениями, исключая `ui\__init__.py`.
    - Четыре паттерна: `^\s*import ui\b`, `^\s*from ui\b`, `^\s*from ui\.`, `^\s*import ui\s+as\b`.
    - Зафиксировать совпадения в отчёте итерации (Requirement 10.4).
    - Rollback: не требуется (read-only).
    - _Компонент: C8, Риск R9_
    - _Requirements: 10.1, 10.4_
  - [~] 6.6 Решение по `ui\__init__.py`
    - Если 0 совпадений — `git rm ui\__init__.py` (Requirement 10.2).
    - Если ≥1 совпадение — сохранить без изменений, зафиксировать обоснование.
    - Rollback: до коммита S5 — `git restore --staged --worktree ui\__init__.py`.
    - _Компонент: C8, P10_
    - _Requirements: 10.2, 10.3_
  - [~] 6.7 Smoke-импорт пакетов перед коммитом S5 (безопасная проверка Риска R9)
    - Если `bitrix\__init__.py` сохраняется — выполнить `python -c "import bitrix; print('ok')"` и, при наличии re-export, `python -c "from bitrix import Bitrix24API; print('ok')"`.
    - Если `bitrix\__init__.py` удалён — выполнить `python -c "from bitrix.api import *; print('ok')"` (namespace-package).
    - Аналогично для `asr` и `ui` при необходимости.
    - Любая ошибка — откат удалений через `git restore --staged --worktree <pkg>\__init__.py` и пересмотр решения 6.2/6.4/6.6.
    - Rollback: `git restore --staged --worktree bitrix\__init__.py asr\__init__.py ui\__init__.py`.
    - _Компонент: C8, Риск R9, EH_
    - _Requirements: 10.1, 10.3_
  - [~] 6.8 Создать коммит S5 с сообщением `chore(hygiene): remove unused facade __init__.py files`
    - Если хотя бы один `__init__.py` удалён (6.2 / 6.4 / 6.6) — `git add -A bitrix asr ui`; `git commit -m "chore(hygiene): remove unused facade __init__.py files"`.
    - Если все три сохранены — коммит S5 пропускается, grep-отчёт по трём пакетам фиксируется в отчёте итерации как обоснование пропуска (Requirement 8.5, 8.6, 10.8); позиционный номер S5 остаётся пустым.
    - Rollback: `git reset --soft HEAD~1` и `git restore --staged .`.
    - _Компонент: S5, DM1, P8_
    - _Requirements: 10.7, 10.8, 10.9, 8.1, 8.2, 8.4, 8.5, 8.6_
  - [~] 6.9 Проверки после S5
    - Для каждого `pkg` в `{bitrix, asr, ui}`: если результат grep из 6.1/6.3/6.5 был 0 — `Test-Path <pkg>\__init__.py` → `False`; иначе → `True` (Property 10).
    - Порядок коммитов: S5 (если создан) строго после S4 и до S6 (Requirement 10.9).
    - `git show --stat <S5>` — только удаления `<pkg>\__init__.py`, без других файлов (DM1, Property 8).
    - Smoke-импорты 6.7 проходят без ошибок.
    - Rollback: не требуется (read-only).
    - _Компонент: План проверки «После S5», P10_
    - _Requirements: 10.1, 10.2, 10.3, 10.9_

- [x] 7. S6 — добавление `pyproject.toml` с конфигурацией Ruff и Black
  - [~] 7.1 Сверить `requires-python` с ожиданиями `check_python*.bat`
    - Прочитать содержимое `check_python.bat` и `check_python_simple.bat` (и любых `check_python*.bat`) в корне Target_Repo.
    - Определить ожидаемую минимальную версию Python (Риск R4, EH5).
    - Если версия отличается от `>=3.10` — зафиксировать и использовать фактическое значение в 7.2.
    - Rollback: не требуется (read-only).
    - _Компонент: C5, EH5, Риск R4_
    - _Requirements: 6.3_
  - [~] 7.2 Создать `pyproject.toml` в корне Target_Repo
    - Содержимое — по C5: секция `[project]` (`name = "bitrix24-automation"`, `version = "0.1.0"`, `requires-python` согласованная с 7.1); секция `[tool.ruff]` с `line-length = 100`, `target-version = "py310"` (или согласованным), `exclude = ["reports", "venv", ".venv", "__pycache__", "system--diarize", "asr", "ui", "docs"]`; `[tool.ruff.lint]` с `select = ["E", "F", "W", "I", "UP", "B"]`; `[tool.black]` с `line-length = 100`, тем же `target-version` и `extend-exclude` на те же каталоги.
    - `line-length` одинаков для Ruff и Black — 100 (Requirement 6.4).
    - Каталоги `reports/`, `venv/`, `.venv/`, `__pycache__/`, `system--diarize/`, `asr/`, `ui/`, `docs/` исключены (Requirement 6.5).
    - НЕ запускать `ruff check --fix`, `black .` или иной автоформат существующего кода (Requirement 6.6, Риск R5, EH6).
    - Rollback: `Remove-Item -Force pyproject.toml` (до коммита S6).
    - _Компонент: C5_
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6_
  - [~] 7.3 Проверить локальность изменений перед коммитом S6 (`git diff --stat`)
    - Выполнить `git status` и `git diff --stat`.
    - Ожидание: единственный новый/изменённый файл — `pyproject.toml` (DM1, Property 8, EH6).
    - Если в worktree попали другие файлы (следы случайного автоформата) — откатить: `git checkout -- <path>` или `git restore --worktree -- <path>`.
    - Rollback: `git restore --staged .` и `git checkout -- .` (до коммита S6).
    - _Компонент: EH6, Риск R5, P8_
    - _Requirements: 6.6, 8.4_
  - [~] 7.4 Создать коммит S6 с сообщением `build(hygiene): add pyproject.toml with ruff and black config`
    - `git add pyproject.toml`; `git commit -m "build(hygiene): add pyproject.toml with ruff and black config"`.
    - Rollback: `git reset --soft HEAD~1` и `git restore --staged pyproject.toml`.
    - _Компонент: S6, DM1, P8_
    - _Requirements: 6.7, 8.1, 8.2, 8.4_
  - [~] 7.5 Проверки после S6
    - `Test-Path pyproject.toml` → `True`.
    - `Select-String -Path pyproject.toml -Pattern '\[tool\.ruff\]','\[tool\.ruff\.lint\]','\[tool\.black\]','line-length\s*=\s*100','target-version','"reports"','"venv"','"\.venv"','"system--diarize"','"asr"','"ui"','"docs"'` → все шаблоны найдены.
    - `git show --stat HEAD` → изменён только `pyproject.toml` (Property 8).
    - `git log --oneline` → 5 или 6 коммитов (в зависимости от пропуска S5).
    - Rollback: не требуется (read-only).
    - _Компонент: План проверки «После S6», P8_
    - _Requirements: 6.1, 6.2, 6.4, 8.4_

- [x] 8. S7.1 — добавить `logging_setup.py` и перевести core api-модули
  - [~] 8.1 Определить `Stdout_Contract_Scripts` (только один раз, в начале S7.1)
    - Собрать список Scope_Python_Files (см. 1.5) и все `*.bat` в корне Target_Repo.
    - Для каждого `*.py` проверить:
      - (а) существует ли `*.bat` с подстрокой имени `<script>.py` — `Select-String -Path *.bat -Pattern ([regex]::Escape($name))`.
      - (б) потребляет ли этот `.bat` stdout `.py` — признаки: `for\s+/f[^\r\n]*['""]python[^'""]*<script>\.py`, перенаправление `<script>\.py[^\r\n]*\s*>`, конвейер `<script>\.py[^\r\n]*\s*\|`.
    - Если оба условия выполнены — пометить `<script>.py` как Stdout_Contract_Script и исключить из замены `print` во всех последующих под-коммитах S7.1..S7.5.
    - Кандидаты: `dump_one_call.py` (почти наверняка), `check_python.py` (проверить `check_python*.bat`), любые другие скрипты, попавшие по алгоритму.
    - Дополнительно: проверить, что все `*.bat` в Bat_Contract выполняют `cd /d %~dp0` или `pushd %~dp0` перед вызовом Python (`Select-String -Path *.bat -Pattern 'cd\s+/d\s+%~dp0|pushd\s+%~dp0'`, EH11, Риск R12). `.bat` без `cd` зафиксировать в отчёте — соответствующие `.py` при необходимости пометить Stdout_Contract_Script.
    - Результат фиксируется в отчёте итерации в формате DM3 (`script`, `bat_callers`, `stdout_consumption_evidence`, `decision`) и используется всеми S7.x (один источник истины).
    - Rollback: не требуется (read-only).
    - _Компонент: C7 (Stdout_Contract_Scripts), DM3, EH9, EH11, Риски R10, R12_
    - _Requirements: 7.11_
  - [~] 8.2 Создать `logging_setup.py` в корне Target_Repo (Logging_Module)
    - Реализовать `get_logger(name: str, level: int = logging.INFO) -> logging.Logger` строго по C6.
    - Формат: `"%(asctime)s %(levelname)s %(name)s %(message)s"` (Requirement 7.3).
    - `StreamHandler` → `sys.stderr`; `RotatingFileHandler` → `reports/logs/bitrix24.log`, `maxBytes=2_000_000`, `backupCount=5`, `encoding="utf-8"` (C6).
    - `os.makedirs(_LOG_DIR, exist_ok=True)` при первом вызове (EH7).
    - Идемпотентность: атрибут `_HANDLER_MARK` на handler-ах, повторная регистрация не добавляет дубликатов.
    - `logger.propagate = False`.
    - Единственные зависимости — стандартная библиотека: `logging`, `logging.handlers`, `os`, `sys` (EH10, Риск R11).
    - Rollback: `Remove-Item -Force logging_setup.py` (до коммита S7.1).
    - _Компонент: C6, EH7, EH10, Риск R11_
    - _Requirements: 7.1, 7.2, 7.3, 7.12_
  - [~] 8.3 Smoke-тест `logging_setup.py`
    - Выполнить: `python -c "from logging_setup import get_logger; get_logger('smoke').info('hello'); get_logger('smoke').info('hello again')"`.
    - Проверить `Test-Path reports\logs\bitrix24.log` → `True`.
    - Содержимое файла — две строки формата DM2.
    - Повторный вызов не должен удваивать handler'ы (проверка идемпотентности).
    - Rollback: `Remove-Item -Force reports\logs\bitrix24.log` (не версионируется).
    - _Компонент: C6, DM2_
    - _Requirements: 7.2, 7.3, 7.12_
  - [~] 8.4 Обработать `bitrix24_api.py`
    - Grep: `Select-String -Path bitrix24_api.py -Pattern '^\s*print\('`. Если 0 совпадений — файл пропустить (Property 12), задача no-op.
    - При ≥1 совпадении:
      - Вставить после `from __future__`-блока (если есть) или после модульного docstring / в начало файла:
        ```python
        from logging_setup import get_logger

        logger = get_logger(__name__)
        ```
      - Заменить каждое `print(...)` на `logger.<level>(...)` по эвристикам C7: WARNING (retry/повтор/backoff), ERROR (ошибка/exception/failed — возможно `logger.exception(...)` внутри `except`), INFO (успех/OK/done), DEBUG (DEBUG/dump/отладочный).
      - Публичный интерфейс `Bitrix24API` не изменять (Requirement 7.13, Property 7).
    - `python -m py_compile bitrix24_api.py` (синтаксическая проверка).
    - Rollback: `git restore bitrix24_api.py` (до коммита S7.1).
    - _Компонент: C7, P6, P7, P11, P12, EH12, Риск R7_
    - _Requirements: 7.4, 7.5, 7.6, 7.7, 7.8, 7.9, 7.13_
  - [~] 8.5 Обработать `bit_newton_asr.py`
    - Grep `^\s*print\(` в файле. Если 0 — пропустить.
    - При ≥1: вставить импорт + `logger = get_logger(__name__)`, заменить `print` по эвристикам C7, `python -m py_compile bit_newton_asr.py`.
    - Сигнатуры публичных функций/классов не трогать (Property 7).
    - Rollback: `git restore bit_newton_asr.py`.
    - _Компонент: C7, P7, P11, P12_
    - _Requirements: 7.4, 7.5, 7.6, 7.7, 7.8, 7.9, 7.13_
  - [~] 8.6 Обработать `config.py`
    - Grep `^\s*print\(`. Если 0 — пропустить.
    - При ≥1: импорт + `logger = get_logger(__name__)`, замена `print` → `logger.*`, `python -m py_compile config.py`.
    - Rollback: `git restore config.py`.
    - _Компонент: C7, P7, P11, P12_
    - _Requirements: 7.4, 7.5, 7.13_
  - [~] 8.7 Обработать `bitnewton_sync_to_api.py`
    - Grep `^\s*print\(`. Если 0 — пропустить.
    - При ≥1: импорт + `logger`, замена `print` → `logger.*`, `python -m py_compile bitnewton_sync_to_api.py`.
    - Файл — Sync_Facade, CLI-обёртка; правки ограничены импортом и заменой `print` (Requirement 5.4, 7.13).
    - Rollback: `git restore bitnewton_sync_to_api.py`.
    - _Компонент: C7, P5, P7, P11, P12_
    - _Requirements: 7.4, 7.5, 7.13_
  - [~] 8.8 Обработать `download_resolver.py`
    - Grep `^\s*print\(`. Если 0 — пропустить.
    - При ≥1: импорт + `logger`, замена, `python -m py_compile download_resolver.py`.
    - Rollback: `git restore download_resolver.py`.
    - _Компонент: C7, P7, P11, P12_
    - _Requirements: 7.4, 7.5, 7.13_
  - [~] 8.9 Создать коммит S7.1 с сообщением `refactor(hygiene): add logging_setup and convert core api modules`
    - `git add logging_setup.py bitrix24_api.py bit_newton_asr.py config.py bitnewton_sync_to_api.py download_resolver.py`.
    - `git commit -m "refactor(hygiene): add logging_setup and convert core api modules"`.
    - В коммит попадают только файлы из DM1 для S7.1 (Property 8); файлы без изменений (0 `print` до S7.1) не попадают — `git add` их не затронет.
    - `git show --stat HEAD` — проверить локальность.
    - Rollback: `git reset --soft HEAD~1` и `git restore --staged <files>`; при необходимости `git restore <files>`.
    - _Компонент: S7.1, DM1, P8_
    - _Requirements: 7.14, 7.15, 8.1, 8.2, 8.4_
  - [~] 8.10 Проверки после S7.1
    - `Test-Path logging_setup.py` → `True`.
    - Property 6: `Select-String -Path bitrix24_api.py -Pattern '^\s*print\('` → пусто (если файл был в S7.1 и имел `print`).
    - Property 12: для каждого изменённого файла — `Select-String -Pattern 'from logging_setup import get_logger'` → найден; для неизменённых — не найден (соответствие baseline 1.5).
    - Property 7: повторить снимок API `Bitrix24API` и сравнить с baseline 1.4 — расхождений нет.
    - Smoke: `python -c "import bitrix24_api; import bit_newton_asr; import config; import bitnewton_sync_to_api; import download_resolver; print('ok')"` — без ошибок (если все импорты возможны; недоступные внешние зависимости документируются).
    - `git show --stat HEAD` — состав файлов ⊆ DM1[S7.1].
    - Rollback: не требуется (read-only).
    - _Компонент: План проверки «После S7.1..S7.5», P6, P7, P11, P12, EH12_
    - _Requirements: 7.4, 7.5, 7.13, 8.2_

- [x] 9. S7.2 — перевод CRM-модулей отчётности на logging
  - [~] 9.1 Обработать `crm_contacts.py`
    - Grep `^\s*print\(`. Если 0 — пропустить (Property 12).
    - При ≥1: вставить `from logging_setup import get_logger` + `logger = get_logger(__name__)` после `from __future__` или после docstring; заменить `print(...)` → `logger.<level>(...)` по эвристикам C7; `python -m py_compile crm_contacts.py`.
    - Публичный интерфейс не трогать (Property 7).
    - Rollback: `git restore crm_contacts.py`.
    - _Компонент: C7, P7, P11, P12_
    - _Requirements: 7.4, 7.5, 7.13_
  - [~] 9.2 Обработать `crm_deals.py`
    - Та же процедура (grep → пропуск или импорт+замена+py_compile).
    - Rollback: `git restore crm_deals.py`.
    - _Компонент: C7, P7, P11, P12_
    - _Requirements: 7.4, 7.5, 7.13_
  - [~] 9.3 Обработать `crm_leads.py`
    - Та же процедура.
    - Rollback: `git restore crm_leads.py`.
    - _Компонент: C7, P7, P11, P12_
    - _Requirements: 7.4, 7.5, 7.13_
  - [~] 9.4 Обработать `crm_report.py`
    - Та же процедура.
    - Rollback: `git restore crm_report.py`.
    - _Компонент: C7, P7, P11, P12_
    - _Requirements: 7.4, 7.5, 7.13_
  - [~] 9.5 Обработать `custom_period_report.py`
    - Та же процедура.
    - Rollback: `git restore custom_period_report.py`.
    - _Компонент: C7, P7, P11, P12_
    - _Requirements: 7.4, 7.5, 7.13_
  - [~] 9.6 Обработать `detailed_calls_analysis.py`
    - Та же процедура.
    - Rollback: `git restore detailed_calls_analysis.py`.
    - _Компонент: C7, P7, P11, P12_
    - _Requirements: 7.4, 7.5, 7.13_
  - [~] 9.7 Обработать `detailed_managers_report.py`
    - Та же процедура.
    - Rollback: `git restore detailed_managers_report.py`.
    - _Компонент: C7, P7, P11, P12_
    - _Requirements: 7.4, 7.5, 7.13_
  - [~] 9.8 Обработать `managers_call_stats.py`
    - Та же процедура.
    - Rollback: `git restore managers_call_stats.py`.
    - _Компонент: C7, P7, P11, P12_
    - _Requirements: 7.4, 7.5, 7.13_
  - [~] 9.9 Обработать `managers_call_stats_auto.py`
    - Та же процедура.
    - Rollback: `git restore managers_call_stats_auto.py`.
    - _Компонент: C7, P7, P11, P12_
    - _Requirements: 7.4, 7.5, 7.13_
  - [~] 9.10 Обработать `op_deals_analytics.py`
    - Та же процедура.
    - Rollback: `git restore op_deals_analytics.py`.
    - _Компонент: C7, P7, P11, P12_
    - _Requirements: 7.4, 7.5, 7.13_
  - [~] 9.11 Обработать `op_full_analytics.py`
    - Та же процедура.
    - Rollback: `git restore op_full_analytics.py`.
    - _Компонент: C7, P7, P11, P12_
    - _Requirements: 7.4, 7.5, 7.13_
  - [~] 9.12 Обработать `op_lost_deals_analysis.py`
    - Та же процедура.
    - Rollback: `git restore op_lost_deals_analysis.py`.
    - _Компонент: C7, P7, P11, P12_
    - _Requirements: 7.4, 7.5, 7.13_
  - [~] 9.13 Обработать `yesterday_leads.py`
    - Та же процедура.
    - Rollback: `git restore yesterday_leads.py`.
    - _Компонент: C7, P7, P11, P12_
    - _Requirements: 7.4, 7.5, 7.13_
  - [~] 9.14 Обработать `yesterday_leads_stats.py`
    - Та же процедура.
    - Rollback: `git restore yesterday_leads_stats.py`.
    - _Компонент: C7, P7, P11, P12_
    - _Requirements: 7.4, 7.5, 7.13_
  - [~] 9.15 Создать коммит S7.2 с сообщением `refactor(hygiene): convert crm reporting modules to logging`
    - `git add` только файлы 9.1..9.14, которые реально изменены (те, где был `print(`).
    - `git commit -m "refactor(hygiene): convert crm reporting modules to logging"`.
    - Если ни один файл из 9.1..9.14 не содержал `print(` — под-коммит S7.2 пропускается (Requirement 8.5), позиция S7.2 остаётся пустой.
    - `git show --stat HEAD` — состав ⊆ DM1[S7.2].
    - Rollback: `git reset --soft HEAD~1` и `git restore --staged <files>`; при необходимости `git restore <files>`.
    - _Компонент: S7.2, DM1, P8_
    - _Requirements: 7.14, 7.15, 8.1, 8.2, 8.4, 8.5_
  - [~] 9.16 Проверки после S7.2
    - Для каждого файла 9.1..9.14: если он был изменён, `Select-String -Pattern '^\s*print\('` → пусто; `Select-String -Pattern 'from logging_setup import get_logger'` → найден (Property 11, Property 12).
    - `python -m py_compile crm_contacts.py crm_deals.py crm_leads.py crm_report.py custom_period_report.py detailed_calls_analysis.py detailed_managers_report.py managers_call_stats.py managers_call_stats_auto.py op_deals_analytics.py op_full_analytics.py op_lost_deals_analysis.py yesterday_leads.py yesterday_leads_stats.py` — без ошибок для существующих файлов.
    - `git show --stat HEAD` — состав ⊆ DM1[S7.2] (Property 8).
    - Rollback: не требуется (read-only).
    - _Компонент: План проверки, P11, P12_
    - _Requirements: 7.5, 7.13, 8.2_

- [ ] 10. S7.3 — перевод UI-модулей на logging
  - [~] 10.1 Обработать `web_ui.py`
    - Grep `^\s*print\(`. Если 0 — пропустить.
    - При ≥1: импорт + `logger`, замена `print` → `logger.*` (WARNING/ERROR/INFO/DEBUG по C7), `python -m py_compile web_ui.py`.
    - Публичный интерфейс (функции/классы Streamlit-приложения) не трогать (Property 7).
    - Rollback: `git restore web_ui.py`.
    - _Компонент: C7, P7, P11, P12_
    - _Requirements: 7.4, 7.5, 7.13_
  - [~] 10.2 Обработать `ui_audio_downloader.py`
    - Та же процедура.
    - Rollback: `git restore ui_audio_downloader.py`.
    - _Компонент: C7, P7, P11, P12_
    - _Requirements: 7.4, 7.5, 7.13_
  - [~] 10.3 Обработать `ui\audio_downloader.py` (если файл существует)
    - Проверить `Test-Path ui\audio_downloader.py`. Если `False` — задача no-op.
    - Если `True`: grep `^\s*print\(` → пропуск или импорт+замена+`python -m py_compile ui\audio_downloader.py`.
    - Rollback: `git restore ui\audio_downloader.py`.
    - _Компонент: C7, P7, P11, P12_
    - _Requirements: 7.4, 7.5, 7.13_
  - [~] 10.4 Создать коммит S7.3 с сообщением `refactor(hygiene): convert UI modules to logging`
    - `git add` только изменённые файлы из 10.1..10.3.
    - `git commit -m "refactor(hygiene): convert UI modules to logging"`.
    - Если ни один не изменён — под-коммит пропускается (Requirement 8.5).
    - `git show --stat HEAD` — состав ⊆ DM1[S7.3].
    - Rollback: `git reset --soft HEAD~1` и `git restore --staged <files>`.
    - _Компонент: S7.3, DM1, P8_
    - _Requirements: 7.14, 7.15, 8.1, 8.2, 8.4, 8.5_
  - [~] 10.5 Проверки после S7.3
    - Для каждого изменённого файла: `Select-String -Pattern '^\s*print\('` → пусто; `Select-String -Pattern 'from logging_setup import get_logger'` → найден.
    - `python -m py_compile web_ui.py ui_audio_downloader.py` и `ui\audio_downloader.py` (если существует) — без ошибок.
    - `git show --stat HEAD` — состав ⊆ DM1[S7.3].
    - Rollback: не требуется (read-only).
    - _Компонент: План проверки, P11, P12, P8_
    - _Requirements: 7.5, 7.13, 8.2_

- [x] 11. S7.4 — перевод helper-модулей пакетов `bitrix\` и `asr\`
  - [~] 11.1 Обработать `bitrix\api.py`
    - Grep `^\s*print\(`. Если 0 — пропустить.
    - При ≥1: импорт + `logger`, замена, `python -m py_compile bitrix\api.py`.
    - Публичные функции/классы не трогать (Property 7, Requirement 7.13).
    - Rollback: `git restore bitrix\api.py`.
    - _Компонент: C7, P5, P7, P11, P12_
    - _Requirements: 5.4, 7.4, 7.5, 7.13_
  - [~] 11.2 Обработать `bitrix\recordings.py`
    - Та же процедура.
    - Rollback: `git restore bitrix\recordings.py`.
    - _Компонент: C7, P5, P7, P11, P12_
    - _Requirements: 5.4, 7.4, 7.5, 7.13_
  - [~] 11.3 Обработать `bitrix\dump_one_call_debug.py` (если не в `Stdout_Contract_Scripts`)
    - Проверить решение из 8.1 (`Stdout_Contract_Scripts`). Если файл помечен Stdout_Contract_Script — пропустить (Requirement 7.11), задача no-op.
    - Иначе: grep `^\s*print\(` → пропуск или импорт+замена+`python -m py_compile bitrix\dump_one_call_debug.py`.
    - Rollback: `git restore bitrix\dump_one_call_debug.py`.
    - _Компонент: C7 (Stdout_Contract), DM3, EH9, P11, P12_
    - _Requirements: 7.4, 7.5, 7.11, 7.13_
  - [~] 11.4 Обработать `asr\bitnewton.py`
    - Grep `^\s*print\(`. Если 0 — пропустить.
    - При ≥1: импорт + `logger`, замена, `python -m py_compile asr\bitnewton.py`.
    - Rollback: `git restore asr\bitnewton.py`.
    - _Компонент: C7, P7, P11, P12_
    - _Requirements: 7.4, 7.5, 7.13_
  - [~] 11.5 Обработать оставшиеся `__init__.py` пакетов, если не удалены в S5
    - Для каждого пакета `pkg` в `{bitrix, asr, ui}`: если `Test-Path <pkg>\__init__.py` → `True` (не удалён в 6.2/6.4/6.6), выполнить grep `^\s*print\(`.
    - Как правило результат 0 (файлы-пустышки / re-export); тогда файл пропускается (Property 12).
    - При ≥1: импорт + `logger`, замена, `python -m py_compile <pkg>\__init__.py`.
    - Rollback: `git restore <pkg>\__init__.py`.
    - _Компонент: C7, C8, P11, P12_
    - _Requirements: 7.4, 7.5, 7.13_
  - [~] 11.6 Создать коммит S7.4 с сообщением `refactor(hygiene): convert bitrix/asr package helpers to logging`
    - `git add` только изменённые файлы из 11.1..11.5.
    - `git commit -m "refactor(hygiene): convert bitrix/asr package helpers to logging"`.
    - Если ни один не изменён — под-коммит пропускается (Requirement 8.5).
    - `git show --stat HEAD` — состав ⊆ DM1[S7.4].
    - Rollback: `git reset --soft HEAD~1` и `git restore --staged <files>`.
    - _Компонент: S7.4, DM1, P8_
    - _Requirements: 7.14, 7.15, 8.1, 8.2, 8.4, 8.5_
  - [~] 11.7 Проверки после S7.4
    - Для каждого изменённого файла: `Select-String -Pattern '^\s*print\('` → пусто; `Select-String -Pattern 'from logging_setup import get_logger'` → найден (Property 11, Property 12).
    - `python -m py_compile bitrix\api.py bitrix\recordings.py asr\bitnewton.py` (и остальные, если изменены) — без ошибок.
    - `git show --stat HEAD` — состав ⊆ DM1[S7.4].
    - Rollback: не требуется (read-only).
    - _Компонент: План проверки, P11, P12, P8_
    - _Requirements: 7.5, 7.13, 8.2_

- [x] 12. S7.5 — перевод остальных утилитарных скриптов
  - [~] 12.1 Обработать `download_ffmpeg.py`
    - Grep `^\s*print\(`. Если 0 — пропустить.
    - При ≥1: импорт + `logger`, замена, `python -m py_compile download_ffmpeg.py`.
    - Публичный интерфейс не трогать (Property 7).
    - Rollback: `git restore download_ffmpeg.py`.
    - _Компонент: C7, P7, P11, P12_
    - _Requirements: 7.4, 7.5, 7.13_
  - [~] 12.2 Обработать `dump_one_call.py` (если не в `Stdout_Contract_Scripts`)
    - Проверить решение из 8.1. Если помечен Stdout_Contract_Script (высокая вероятность) — пропустить, задача no-op, зафиксировать в отчёте итерации (Requirement 7.11).
    - Иначе: grep `^\s*print\(` → пропуск или импорт+замена+`python -m py_compile dump_one_call.py`.
    - Rollback: `git restore dump_one_call.py`.
    - _Компонент: C7 (Stdout_Contract), DM3, EH9, Риск R10_
    - _Requirements: 7.4, 7.5, 7.11, 7.13_
  - [~] 12.3 Обработать оставшиеся `Scope_Python_Files`, не вошедшие в S7.1..S7.4
    - Выполнить `Compare-Object` между полным списком Scope_Python_Files (1.5) и файлами, обработанными в 8.4..8.8, 9.1..9.14, 10.1..10.3, 11.1..11.5 и 12.1..12.2. Получить остаток.
    - Для каждого файла-остатка: проверить, не помечен ли он Stdout_Contract_Script (8.1); если да — пропустить.
    - Иначе: grep `^\s*print\(` → пропуск или импорт+замена+`python -m py_compile <file>`.
    - Rollback: `git restore <file>` по каждому изменённому файлу.
    - _Компонент: C7, P7, P11, P12_
    - _Requirements: 7.4, 7.5, 7.11, 7.13_
  - [~] 12.4 Создать коммит S7.5 с сообщением `refactor(hygiene): convert remaining utility scripts to logging`
    - `git add` только изменённые файлы из 12.1..12.3.
    - `git commit -m "refactor(hygiene): convert remaining utility scripts to logging"`.
    - Если ни один не изменён — под-коммит пропускается (Requirement 8.5).
    - `git show --stat HEAD` — состав ⊆ DM1[S7.5].
    - Rollback: `git reset --soft HEAD~1` и `git restore --staged <files>`.
    - _Компонент: S7.5, DM1, P8_
    - _Requirements: 7.14, 7.15, 8.1, 8.2, 8.4, 8.5_
  - [~] 12.5 Проверки после S7.5
    - Для каждого изменённого файла: `Select-String -Pattern '^\s*print\('` → пусто; `Select-String -Pattern 'from logging_setup import get_logger'` → найден (Property 11, Property 12).
    - `python -m py_compile <каждый изменённый файл>` — без ошибок.
    - `git show --stat HEAD` — состав ⊆ DM1[S7.5].
    - Rollback: не требуется (read-only).
    - _Компонент: План проверки, P11, P12, P8_
    - _Requirements: 7.5, 7.13, 8.2_

- [ ] 13. Финальная сверка инвариантов итерации
  - [~] 13.1 Сверить SHA-256 защищаемых файлов с baseline из 1.3 (Property 5)
    - Пересчитать `Get-FileHash -Algorithm SHA256` по списку из 1.3.
    - Допустимые расхождения: только файлы, затронутые S7.x (т.е. те, в которых был `print(` до S7.1) из множества `{bitrix24_api.py, bit_newton_asr.py, bitnewton_sync_to_api.py, 14 CRM-файлов S7.2, 2–3 UI-файла S7.3, bitrix/api.py, bitrix/recordings.py, bitrix/dump_one_call_debug.py (если не Stdout_Contract), asr/bitnewton.py, download_ffmpeg.py, dump_one_call.py (если не Stdout_Contract), прочие Scope_Python_Files}`.
    - НЕ должны расходиться с baseline: `pipelines\bitnewton_sync.py`, все `*.bat` Bat_Contract, `.env` (если присутствует), файлы пакетов, не попавшие в S7.x.
    - Расхождение по запрещённому файлу — инцидент, выполнить `git restore <path>` и пересоздать соответствующий коммит без затронутого файла.
    - Rollback: не требуется (read-only).
    - _Компонент: P5, EH12, Риск R7_
    - _Requirements: 4.1, 4.2, 4.3, 4.5, 5.4, 7.10, 7.12, 7.13_
  - [~] 13.2 Проверить локальность каждого коммита итерации по карте DM1 (Property 8)
    - Для каждого коммита `c` из `git log --oneline` за период итерации (S1..S7.5) выполнить `git show --name-only <sha>`.
    - Сверить множество файлов с DM1:
      - S1: `.gitignore` (+ служебное создание `.git/`).
      - S2: `docs\_archive\*` и удаления Hygiene_Notes из корня.
      - S3: удаления в `reports\*` + `.gitignore`.
      - S4: `docs\_archive\FACADE_DECISION.md`.
      - S5 (если создан): удаления `<pkg>\__init__.py` для пакетов с 0 совпадений.
      - S6: `pyproject.toml`.
      - S7.1: `logging_setup.py` + 5 core api-модулей (с фильтром «был `print(`»).
      - S7.2: 14 CRM-модулей (с тем же фильтром).
      - S7.3: `web_ui.py`, `ui_audio_downloader.py`, `ui\audio_downloader.py` (если существует).
      - S7.4: `bitrix\api.py`, `bitrix\recordings.py`, `bitrix\dump_one_call_debug.py` (если не Stdout_Contract), `asr\bitnewton.py`, оставшиеся `__init__.py` пакетов.
      - S7.5: `download_ffmpeg.py`, `dump_one_call.py` (если не Stdout_Contract), прочие Scope_Python_Files.
    - При расхождении — зафиксировать инцидент в отчёте итерации, рассмотреть `git revert` соответствующего коммита.
    - Порядок коммитов: S1 → S2 → S3 → S4 → (S5) → S6 → S7.1 → S7.2 → S7.3 → S7.4 → S7.5 (допускаются пропуски, номера не сдвигаются).
    - Rollback: не требуется (read-only).
    - _Компонент: P8, DM1_
    - _Requirements: 8.1, 8.2, 8.4, 8.5, 10.9_
  - [~] 13.3 Финальная smoke-проверка логирования
    - `python -c "from logging_setup import get_logger; get_logger('final').info('final smoke')"`.
    - `Test-Path reports\logs\bitrix24.log` → `True`; последняя строка соответствует DM2.
    - `Select-String -Path *.py -Pattern 'from logging_setup import get_logger' -Recurse | Measure-Object` → число совпадений совпадает с числом файлов, у которых baseline 1.5 фиксировал ≥1 `print(` (Property 12).
    - `Select-String -Path *.py -Pattern '^\s*print\(' -Recurse | Where-Object { $_.Path -notmatch 'pipelines\\bitnewton_sync\.py|logging_setup\.py' -and $_.Filename -notin $Stdout_Contract_Scripts }` → пусто (Property 11).
    - Rollback: не требуется (read-only).
    - _Компонент: C6, DM2, P11, P12_
    - _Requirements: 7.2, 7.3, 7.5, 7.10, 7.11, 7.12_
  - [~] 13.4 Зафиксировать отчёт итерации
    - Создать запись в `docs/agent-log/` (шаблон `docs/templates/agent-report.md`) с содержанием:
      - результаты grep по `{bitrix, asr, ui}` из 6.1/6.3/6.5;
      - список `Stdout_Contract_Scripts` из 8.1 с DM3-структурой;
      - список пропущенных коммитов и причины (Requirement 8.5);
      - таблица «файл — `print(` count до / после» (сверка Property 12);
      - итоговая сверка SHA-256 (Property 5) и локальности коммитов (Property 8).
    - Обновить `docs/current-context.md` и `docs/tasks.md` при необходимости (согласно AGENTS.md).
    - Rollback: не требуется (документация; при ошибке — `git restore docs/agent-log/<file>.md` или правка вручную).
    - _Компонент: Отчёт итерации, DM3_
    - _Requirements: 8.5, 8.6, 9.1_

## Заметки

- Работа ведётся «на месте» в `C:\Users\koval\bat\bitrix24-automation` вне рабочего пространства Kiro. Все команды предполагают запуск в PowerShell в корне Target_Repo; `cmd /c` допустим как обёртка с теми же аргументами.
- **НЕ трогаются ни в одной задаче**: `pipelines\bitnewton_sync.py` (Pipeline_Script, Requirement 4.1, 7.10), все файлы Bat_Contract (`run_*.bat`, `menu.bat`, `setup_*.bat`, `install.bat`, `test_connection.bat`, `check_python*.bat`, Requirement 4.2), `.env` (если присутствует), 17 Python-скриптов Bat_Contract по путям и именам (Requirement 4.3), `kriterii_ocenki.txt`, `requirements.txt`, `requirements_ui.txt` (Protected_Txt, Requirement 4.5, 9.1). Единственные допустимые изменения в файлах из этого списка — точечные правки S7.x (импорт `logging_setup` + замена `print(...)` → `logger.*(...)`) в тех `.py`-скриптах Bat_Contract, которые входят в Scope_Python_Files и не квалифицированы как `Stdout_Contract_Scripts`.
- **Никаких автоформатов** (`ruff check --fix`, `ruff format`, `black .`, IDE-хуки автоформата) на существующем коде на протяжении всей итерации (Requirement 6.6, Риск R5, EH6). Допустимы только точечные правки по алгоритму C7.
- **Идемпотентность**: все правки `.gitignore` (2.2, 4.7) идемпотентны (Property 1). Повторные прогоны `Remove-ExpiredReports` (4.3..4.5) и `Remove-Item` по Transient_Artifacts (4.1, 4.2) идемпотентны — не существующие файлы игнорируются благодаря `-ErrorAction SilentlyContinue`. Повторные вызовы `get_logger` не удваивают handler'ы (`_HANDLER_MARK`).
- **Правило пропуска файла в S7.x**: перед любой правкой файла — grep `^\s*print\(`. Если 0 — файл пропускается, импорт `logging_setup` НЕ добавляется, диф пуст (Property 12). Это предотвращает появление ненужных изменений в коммитах S7.x.
- **Пропуск коммита**: если в позиции S1..S7 или в под-коммите S7.x ни один файл набора не содержит изменений, коммит не создаётся; позиционный номер остаётся пустым (Requirement 8.5). Для S5 при сохранении всех трёх `__init__.py` — фиксируется grep-отчёт как обоснование пропуска (Requirement 8.6, 10.8).
- **Особый кейс `bitrix/__init__.py`**: текущий `__init__.py` выполняет `from bitrix24_api import Bitrix24API` (re-export). Решение 6.2 учитывает дополнительный grep `^\s*from\s+bitrix\s+import\s+Bitrix24API\b` — при ≥1 совпадении файл сохраняется (иначе этот импорт перестанет работать в Python 3, т.к. namespace-package не переносит символы из других файлов).
- **`Stdout_Contract_Scripts` определяются один раз** в задаче 8.1 (начало S7.1) до любой правки файлов. Результат фиксируется в отчёте итерации и используется всеми S7.x (8.x, 11.3, 12.2, 12.3). Кандидаты: `dump_one_call.py`, `check_python.py`, `bitrix\dump_one_call_debug.py` — итоговый список определяется алгоритмом C7.
- **Проверочные задачи** (2.4, 3.5, 4.9, 5.4, 6.9, 7.5, 8.10, 9.16, 10.5, 11.7, 12.5, 13.1..13.4) — обязательные, не помечены опциональными.
- **Rollback** для большинства модифицирующих задач — `git restore <path>` до коммита или `git reset --soft HEAD~1` + `git restore --staged .` после коммита. Для удалённых Transient_Artifacts восстановление не предусмотрено (они не версионировались). Для удалённых просроченных Report_Outputs — восстановление из `git reset` только если файлы были версионированы до S3.
- **Цикл импорта**: `logging_setup.py` зависит только от стандартной библиотеки (`logging`, `logging.handlers`, `os`, `sys`); никаких импортов из Scope_Python_Files (EH10, Риск R11). Это обеспечивает отсутствие циклов.
- **Рабочий каталог Python**: модуль `logging_setup.py` лежит в корне Target_Repo, импорт `from logging_setup import get_logger` требует, чтобы `sys.path` содержал корень. Все `.bat` из Bat_Contract, по предположению, выполняют `cd /d %~dp0` или `pushd %~dp0` — это проверяется в 8.1 (EH11, Риск R12). `.bat`, нарушающие это правило, фиксируются в отчёте; правка Bat_Contract запрещена (Requirement 4.2).
- **Параметр `Reports_TTL_Days`**: значение по умолчанию — 30 (Requirement 3.6). Зафиксировано как константа в PowerShell `$REPORTS_TTL_DAYS = 30`; для будущих итераций может быть переопределено без изменения дизайна.
- **Фазы**: задачи группируются по 7 позиционным коммитам (S1..S7) с S7, разбитым на S7.1..S7.5 (Requirement 7.14). Порядок коммитов строгий: S1 → S2 → S3 → S4 → (S5) → S6 → S7.1 → S7.2 → S7.3 → S7.4 → S7.5 (Requirement 8.2, 10.9).

## Task Dependency Graph

```json
{
  "waves": [
    { "id": 0, "tasks": ["1.1", "1.2", "1.3", "1.4", "1.5"] },
    { "id": 1, "tasks": ["2.1"] },
    { "id": 2, "tasks": ["2.2"] },
    { "id": 3, "tasks": ["2.3"] },
    { "id": 4, "tasks": ["2.4", "3.1"] },
    { "id": 5, "tasks": ["3.2"] },
    { "id": 6, "tasks": ["3.3"] },
    { "id": 7, "tasks": ["3.4"] },
    { "id": 8, "tasks": ["3.5", "4.1", "4.2"] },
    { "id": 9, "tasks": ["4.3", "4.4", "4.5"] },
    { "id": 10, "tasks": ["4.6", "4.7"] },
    { "id": 11, "tasks": ["4.8"] },
    { "id": 12, "tasks": ["4.9", "5.1"] },
    { "id": 13, "tasks": ["5.2"] },
    { "id": 14, "tasks": ["5.3"] },
    { "id": 15, "tasks": ["5.4", "6.1", "6.3", "6.5"] },
    { "id": 16, "tasks": ["6.2", "6.4", "6.6"] },
    { "id": 17, "tasks": ["6.7"] },
    { "id": 18, "tasks": ["6.8"] },
    { "id": 19, "tasks": ["6.9", "7.1"] },
    { "id": 20, "tasks": ["7.2"] },
    { "id": 21, "tasks": ["7.3"] },
    { "id": 22, "tasks": ["7.4"] },
    { "id": 23, "tasks": ["7.5", "8.1"] },
    { "id": 24, "tasks": ["8.2"] },
    { "id": 25, "tasks": ["8.3"] },
    { "id": 26, "tasks": ["8.4", "8.5", "8.6", "8.7", "8.8"] },
    { "id": 27, "tasks": ["8.9"] },
    { "id": 28, "tasks": ["8.10"] },
    { "id": 29, "tasks": ["9.1", "9.2", "9.3", "9.4", "9.5", "9.6", "9.7", "9.8", "9.9", "9.10", "9.11", "9.12", "9.13", "9.14"] },
    { "id": 30, "tasks": ["9.15"] },
    { "id": 31, "tasks": ["9.16"] },
    { "id": 32, "tasks": ["10.1", "10.2", "10.3"] },
    { "id": 33, "tasks": ["10.4"] },
    { "id": 34, "tasks": ["10.5"] },
    { "id": 35, "tasks": ["11.1", "11.2", "11.3", "11.4", "11.5"] },
    { "id": 36, "tasks": ["11.6"] },
    { "id": 37, "tasks": ["11.7"] },
    { "id": 38, "tasks": ["12.1", "12.2", "12.3"] },
    { "id": 39, "tasks": ["12.4"] },
    { "id": 40, "tasks": ["12.5"] },
    { "id": 41, "tasks": ["13.1", "13.2", "13.3"] },
    { "id": 42, "tasks": ["13.4"] }
  ]
}
```
