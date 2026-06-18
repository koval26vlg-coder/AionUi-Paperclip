# Design Document: bitrix24-automation-hygiene

## Overview

Итерация «гигиена» приводит репозиторий `C:\Users\koval\bat\bitrix24-automation` в управляемое инженерное состояние без изменения поведения пайплайна и контракта `.bat`-скриптов. Работа выполняется «на месте» в целевом каталоге вне рабочего пространства Kiro. Платформа — Windows, оболочка — `cmd`/PowerShell, язык документации — русский. Python-команды в примерах даны для запуска из корня Target_Repo.

Дизайн расширен относительно предыдущей версии под обновлённые requirements.md от итерации 2026-05-10 и раскрывает:

- Структуру Archive_Directory и перечень перемещаемых/защищённых файлов.
- Идемпотентные правки `.gitignore`.
- Политику чистки `Reports_Directory`: Transient_Artifacts удаляются целиком; для `Report_Outputs` применяется TTL 30 дней (`Reports_TTL_Days`) с защитой `Latest_Report_Files` (`latest_bitnewton_report.*`) и `Singleton_Report_Files` (`state_cache.json`, `deal_filter.json`).
- Facade_Decision в `docs/_archive/FACADE_DECISION.md`.
- Алгоритм grep-проверки и удаления `Facade_Stub_Files` (`bitrix/__init__.py`, `asr/__init__.py`, `ui/__init__.py`) с особым кейсом для `bitrix/__init__.py`, который в текущей версии делает `from bitrix24_api import Bitrix24API` (см. C8).
- Структуру `pyproject.toml` с секциями `ruff` и `black`.
- Модуль `logging_setup.py` с `RotatingFileHandler` + `StreamHandler` и механикой идемпотентной регистрации хендлеров.
- Алгоритм замены `print(...)` на `logger.<level>(...)` во всех файлах `Scope_Python_Files`, кроме `pipelines/bitnewton_sync.py`, `logging_setup.py` и `Stdout_Contract_Scripts`.
- Порядок 7 коммитов с разбиением S7 на под-коммиты S7.1..S7.5.
- Correctness Properties P1..P12.
- Риски R1..R12 и план проверки с блоком после каждого шага.

Решения фазы Clarify (Requirement 9.1, 9.2), на которые опирается дизайн:

- `kriterii_ocenki.txt` остаётся в корне Target_Repo.
- `pipelines/bitnewton_sync.py` в итерации не модифицируется.
- `Bat_Contract` (`.bat`-файлы) в итерации не модифицируется по содержимому и путям.
- Работа ведётся «на месте» в Target_Repo, вне рабочего пространства Kiro.
- Платформа — Windows, оболочка — `cmd`/PowerShell.

## Architecture

### Target_Repo после итерации (корневой уровень, укрупнённо)

```
C:\Users\koval\bat\bitrix24-automation\
├── .git\                       # создаётся S1
├── .gitignore                  # дополняется S1 (tooling) и S3 (reports transient)
├── bitrix24_api.py             # правится S7.1 (импорт logger + print → logger.*)
├── bit_newton_asr.py           # S7.1
├── bitnewton_sync_to_api.py    # S7.1 (тонкая CLI-обёртка Sync_Facade остаётся)
├── config.py                   # S7.1
├── download_resolver.py        # S7.1
├── download_ffmpeg.py          # S7.5 (если print найден)
├── dump_one_call.py            # S7.5 или исключается как Stdout_Contract_Script
├── crm_contacts.py             # S7.2
├── crm_deals.py                # S7.2
├── crm_leads.py                # S7.2
├── crm_report.py               # S7.2
├── custom_period_report.py     # S7.2
├── detailed_calls_analysis.py  # S7.2
├── detailed_managers_report.py # S7.2
├── managers_call_stats.py      # S7.2
├── managers_call_stats_auto.py # S7.2
├── op_deals_analytics.py       # S7.2
├── op_full_analytics.py        # S7.2
├── op_lost_deals_analysis.py   # S7.2
├── yesterday_leads.py          # S7.2
├── yesterday_leads_stats.py    # S7.2
├── web_ui.py                   # S7.3
├── ui_audio_downloader.py      # S7.3
├── logging_setup.py            # создаётся S7.1 (Logging_Module)
├── pyproject.toml              # создаётся S6 (Build_Config)
├── kriterii_ocenki.txt         # Protected_Txt
├── requirements.txt            # Protected_Txt
├── requirements_ui.txt         # Protected_Txt
├── bitrix\                     # пакет; __init__.py обрабатывается S5; *.py правится S7.4
│   ├── __init__.py             # кандидат на удаление S5 (см. C8, особый кейс)
│   ├── api.py                  # S7.4
│   ├── recordings.py           # S7.4
│   └── dump_one_call_debug.py  # S7.4 (если не Stdout_Contract)
├── asr\                        # пакет
│   ├── __init__.py             # кандидат на удаление S5
│   └── bitnewton.py            # S7.4 (если print найден)
├── ui\                         # пакет
│   ├── __init__.py             # кандидат на удаление S5
│   └── audio_downloader.py     # S7.3 (если существует)
├── pipelines\
│   └── bitnewton_sync.py       # НЕ ТРОГАЕМ (Requirement 4.1, 7.10)
├── reports\
│   ├── logs\                   # создаётся при первом get_logger
│   │   └── bitrix24.log
│   ├── bitnewton_sync_report_*.json    # TTL 30д, кроме новых
│   ├── bitnewton_sync_report_*.xlsx    # TTL 30д
│   ├── bitnewton_reevaluated_report_*.json  # TTL 30д
│   ├── latest_bitnewton_report.json    # защищён от TTL (Latest_Report_Files)
│   ├── latest_bitnewton_report.xlsx    # защищён от TTL
│   ├── state_cache.json                # Singleton_Report_Files
│   └── deal_filter.json                # Singleton_Report_Files
├── docs\                       # создаётся S2 (если нет)
│   └── _archive\               # Archive_Directory
│       ├── FIXED.txt … TROUBLESHOOTING.txt   # 11 файлов Hygiene_Notes (S2)
│       └── FACADE_DECISION.md  # Facade_Decision (S4)
└── run_*.bat, menu.bat, setup_*.bat, install.bat, test_connection.bat,
    check_python*.bat           # Bat_Contract — НЕ ТРОГАЕМ
```

### Archive_Directory

- Путь: `docs/_archive/` в корне Target_Repo.
- Если каталога `docs/` нет — создаётся на S2 перед перемещением.
- `FACADE_DECISION.md` ложится в `docs/_archive/` как исторический артефакт итерации.
- Альтернатива `archive/notes/` отвергнута: не согласуется с исходной формулировкой пользователя и уводит документацию из канонического места `docs/`.

### Поток работ итерации (7 коммитов, S7 разбит на под-коммиты)

```
[S1] init repo
      └─ .git/ (создание), .gitignore (tooling-блок)
[S2] archive legacy .txt notes → docs/_archive/
      └─ 11 файлов Hygiene_Notes + docs/_archive/ (создание)
[S3] cleanup transient + TTL 30 дней для Report_Outputs
      └─ reports/ (удаления Transient_Artifacts + просроченных Report_Outputs),
         .gitignore (reports-блок)
[S4] facade decision
      └─ docs/_archive/FACADE_DECISION.md
[S5] remove unused facade __init__.py (bitrix/asr/ui) — может быть пропущен
      └─ для каждого пакета: grep → решение об удалении
[S6] pyproject + ruff + black
      └─ pyproject.toml
[S7] logging_setup + print → logging для Scope_Python_Files
      ├─ S7.1 refactor(hygiene): add logging_setup and convert core api modules
      │    logging_setup.py, bitrix24_api.py, bit_newton_asr.py, config.py,
      │    bitnewton_sync_to_api.py, download_resolver.py
      ├─ S7.2 refactor(hygiene): convert crm reporting modules to logging
      │    crm_contacts.py … yesterday_leads_stats.py (14 файлов)
      ├─ S7.3 refactor(hygiene): convert UI modules to logging
      │    web_ui.py, ui_audio_downloader.py, ui/audio_downloader.py (если есть)
      ├─ S7.4 refactor(hygiene): convert bitrix/asr package helpers to logging
      │    bitrix/api.py, bitrix/recordings.py, bitrix/dump_one_call_debug.py
      │    (если не Stdout_Contract), asr/bitnewton.py + оставшиеся __init__.py
      │    пакетов, если они не удалены в S5
      └─ S7.5 refactor(hygiene): convert remaining utility scripts to logging
           download_ffmpeg.py, dump_one_call.py (если не Stdout_Contract)
```

Позиционные номера S1..S7 не сдвигаются при пропуске шага (Requirement 8.5). Под-коммиты S7.1..S7.5 считаются одной логической итерацией в рамках Requirement 7.14.

## Components

### C1. Archive_Directory (S2)

- Путь: `docs/_archive/`.
- `Hygiene_Notes` (перемещаемые, 11 файлов):
  1. `FIXED.txt`
  2. `FIXED_ENCODING.txt`
  3. `INSTALL_FFMPEG.txt`
  4. `NEXT_STEP.txt`
  5. `PROJECT_STRUCTURE.txt`
  6. `PROJECT_SUMMARY.txt`
  7. `README_FIRST.txt`
  8. `SETUP_READY.txt`
  9. `START_HERE.txt`
  10. `SUCCESS.txt`
  11. `TROUBLESHOOTING.txt`
- `Protected_Txt` (остаются в корне, 3 файла):
  1. `kriterii_ocenki.txt`
  2. `requirements.txt`
  3. `requirements_ui.txt`
- Перед перемещением — grep по `*.bat` и `*.py` на каждое имя Hygiene_Notes (Requirement 2.4). Если имя упомянуто — файл исключается из перемещения, запись в отчёт итерации.
- Используется `git mv` (репозиторий уже инициализирован на S1), чтобы сохранить историю:

```powershell
New-Item -ItemType Directory -Force -Path docs\_archive | Out-Null
$notes = @(
  'FIXED.txt','FIXED_ENCODING.txt','INSTALL_FFMPEG.txt','NEXT_STEP.txt',
  'PROJECT_STRUCTURE.txt','PROJECT_SUMMARY.txt','README_FIRST.txt',
  'SETUP_READY.txt','START_HERE.txt','SUCCESS.txt','TROUBLESHOOTING.txt'
)
foreach ($n in $notes) {
  if (-not (Test-Path $n)) { continue }
  # grep по .bat и .py
  $hits = Select-String -Path (Get-ChildItem -Recurse -Include *.bat,*.py `
            -Exclude __pycache__,venv,.venv,reports,system--diarize,docs) `
          -Pattern ([regex]::Escape($n)) -SimpleMatch -ErrorAction SilentlyContinue
  if ($hits) {
    Write-Host "SKIP $n: mentioned in $($hits.Count) file(s)" -ForegroundColor Yellow
    continue
  }
  git mv $n "docs\_archive\$n"
}
```

### C2. Обновление `.gitignore` (S1 и S3, идемпотентно)

На S1 добавляется tooling-блок:

```
# --- hygiene: tooling caches ---
.ruff_cache/
.pytest_cache/
.mypy_cache/
.cache/
*.log
.venv/
venv/
__pycache__/
```

На S3 добавляется блок Transient_Artifacts (см. C3):

```
# --- hygiene: transient artifacts in reports/ ---
reports/debug_download_*.html
reports/debug_download_link_*.html
reports/selenium_download_*/
reports/streamlit_bitnewton.*.log
reports/chrome_profile/
reports/call.mp3
reports/logs/*.log
reports/logs/*.log.*
```

Правила применения:

- Существующие строки `.gitignore` не удаляются (Requirement 1.3).
- Каждая строка добавляется только если отсутствует (Requirement 1.4, 3.3) — идемпотентно (свойство P1).
- Повторный прогон не меняет файл.

```powershell
function Add-GitignoreLines {
  param([string]$Path, [string[]]$Lines)
  if (-not (Test-Path $Path)) { New-Item -ItemType File -Path $Path | Out-Null }
  $current = Get-Content $Path -ErrorAction SilentlyContinue
  $missing = @()
  foreach ($line in $Lines) {
    if ($current -notcontains $line) { $missing += $line }
  }
  if ($missing.Count -gt 0) {
    Add-Content -Path $Path -Value $missing
  }
}
```

### C3. Чистка Reports_Directory (S3)

Transient_Artifacts — шаблоны для безусловного удаления:

- `reports\debug_download_*.html`
- `reports\debug_download_link_*.html`
- `reports\selenium_download_*\` (каталоги)
- `reports\streamlit_bitnewton.err.log`, `reports\streamlit_bitnewton.out.log` (и шире — `streamlit_bitnewton.*.log`)
- `reports\chrome_profile\` (каталог)
- `reports\call.mp3`

Report_Outputs — семейства, к которым применяется политика TTL `Reports_TTL_Days`:

| Семейство | Паттерн | Политика |
|---|---|---|
| bitnewton sync JSON | `reports\bitnewton_sync_report_*.json` | TTL 30 дней |
| bitnewton sync XLSX | `reports\bitnewton_sync_report_*.xlsx` | TTL 30 дней |
| bitnewton reevaluated | `reports\bitnewton_reevaluated_report_*.json` | TTL 30 дней |
| latest bitnewton report | `reports\latest_bitnewton_report.*` | **Защищён** (Latest_Report_Files) |
| state_cache / deal_filter | `reports\state_cache.json`, `reports\deal_filter.json` | **Защищён** (Singleton_Report_Files) |

Константа по умолчанию:

```powershell
$REPORTS_TTL_DAYS = 30
```

`REPORTS_TTL_DAYS` параметризуется — значение можно переопределить для будущих итераций (Requirement 3.6). В текущей итерации применяется `30`.

Функция `Remove-ExpiredReports` (PowerShell, S3):

```powershell
function Remove-ExpiredReports {
  param(
    [Parameter(Mandatory=$true)][string]$Pattern,
    [int]$TtlDays = 30
  )
  $cutoff = (Get-Date).AddDays(-$TtlDays)
  $files = Get-ChildItem -Path $Pattern -File -ErrorAction SilentlyContinue |
           Where-Object { $_.LastWriteTime -lt $cutoff }
  foreach ($f in $files) {
    # latest_bitnewton_report.* защищён отдельной проверкой имени
    if ($f.Name -like 'latest_bitnewton_report.*') { continue }
    # Singleton тоже защищён именем
    if ($f.Name -eq 'state_cache.json' -or $f.Name -eq 'deal_filter.json') { continue }
    git rm --quiet -- $f.FullName 2>$null
    if (Test-Path $f.FullName) { Remove-Item -Force $f.FullName }
  }
}

# Применение на S3:
Remove-ExpiredReports -Pattern 'reports\bitnewton_sync_report_*.json' -TtlDays $REPORTS_TTL_DAYS
Remove-ExpiredReports -Pattern 'reports\bitnewton_sync_report_*.xlsx' -TtlDays $REPORTS_TTL_DAYS
Remove-ExpiredReports -Pattern 'reports\bitnewton_reevaluated_report_*.json' -TtlDays $REPORTS_TTL_DAYS
```

Удаление Transient_Artifacts — прямое (каталоги рекурсивно):

```powershell
Remove-Item -Force -ErrorAction SilentlyContinue reports\debug_download_*.html
Remove-Item -Force -ErrorAction SilentlyContinue reports\debug_download_link_*.html
Remove-Item -Force -Recurse -ErrorAction SilentlyContinue reports\selenium_download_*
Remove-Item -Force -ErrorAction SilentlyContinue reports\streamlit_bitnewton.*.log
Remove-Item -Force -Recurse -ErrorAction SilentlyContinue reports\chrome_profile
Remove-Item -Force -ErrorAction SilentlyContinue reports\call.mp3
```

Файлы в `reports/`, не попавшие ни в Transient_Artifacts, ни в Report_Outputs, ни в Singleton/Latest — не трогаются (Requirement 3.7, свойство P4). Решение фиксируется в отчёте итерации.

### C4. Facade_Decision (S4)

Артефакт: `docs/_archive/FACADE_DECISION.md`.

Структура документа:

- **Роль `bitrix24_api.py` (Bitrix_API_Module).** Основная точка входа к Bitrix24 REST API на момент итерации. Содержит класс `Bitrix24API` с публичными методами, используемыми внешними скриптами проекта и Bat_Contract.
- **Роль пакета `bitrix/` (Bitrix_Package).** На момент итерации содержит частично дублирующую функциональность (`bitrix/api.py`, `bitrix/recordings.py`, `bitrix/dump_one_call_debug.py`). Кандидат на превращение в тонкий re-export shim поверх `bitrix24_api.py` в будущих итерациях. В текущей итерации дубликаты не удаляются (Requirement 5.4).
- **Роль `bitnewton_sync_to_api.py` (Sync_Facade).** Тонкая CLI-обёртка для Bat_Contract. Остаётся без изменений по путям и сигнатурам; правки S7.1 ограничены заменой `print(...)` на `logger.*(...)`.
- **Перечень дубликатов** (конкретные функции/методы между `bitrix24_api.py` и `bitrix/*.py`) — фиксируется grep-сверкой в рамках S4, без удаления в этой итерации.
- **План устранения на следующие итерации.** (1) Инвентаризация публичных символов обоих модулей; (2) выделение канонического API в `bitrix24_api.py`; (3) превращение `bitrix/` в shim, реэкспортирующий символы из `bitrix24_api.py`; (4) удаление дублирующего кода внутри `bitrix/`; (5) миграция Sync_Facade на прямой импорт из канонического API, если это не ломает Bat_Contract.

### C5. Build_Config (`pyproject.toml`, S6)

Формат — PEP 621 с секциями инструментов. Автоформат и автофиксы линтера на существующем коде не запускаются (Requirement 6.6).

```toml
[project]
name = "bitrix24-automation"
version = "0.1.0"
requires-python = ">=3.10"
# NOTE: версия сверена с check_python*.bat в рамках S6.
# Если .bat ожидают иную версию — скорректировать перед коммитом.

[tool.ruff]
line-length = 100
target-version = "py310"
exclude = [
  "reports",
  "venv",
  ".venv",
  "__pycache__",
  "system--diarize",
  "asr",
  "ui",
  "docs",
]

[tool.ruff.lint]
select = ["E", "F", "W", "I", "UP", "B"]

[tool.black]
line-length = 100
target-version = ["py310"]
extend-exclude = '''
/(
    reports
  | venv
  | \.venv
  | __pycache__
  | system--diarize
  | asr
  | ui
  | docs
)/
'''
```

Замечания:

- `line-length` одинаков для Ruff и Black — 100 (Requirement 6.4).
- Exclude покрывает `reports/`, `venv/`, `.venv/`, `__pycache__/`, `system--diarize/`, `asr/`, `ui/`, `docs/` (Requirement 6.5). `asr/` и `ui/` в exclude, чтобы автофиксы Ruff не затрагивали эти каталоги вне итераций S7.3/S7.4.
- Перед коммитом S6 сверяется `requires-python` с ожиданиями `check_python*.bat` (риск R4).

### C6. Logging_Module (`logging_setup.py`, S7.1)

Требования Requirement 7.2, 7.3 + фиксированное решение по ротации: `RotatingFileHandler` по размеру + `StreamHandler` на stderr.

Сигнатура:

```python
def get_logger(name: str, level: int = logging.INFO) -> logging.Logger: ...
```

Поведение:

- Формат: `%(asctime)s %(levelname)s %(name)s %(message)s`.
- `StreamHandler` → `sys.stderr`.
- `RotatingFileHandler` → `reports/logs/bitrix24.log`, `maxBytes=2_000_000`, `backupCount=5`, `encoding='utf-8'`.
- Ротация по размеру, не по времени. Дата — внутри строки лога через `%(asctime)s`, а не в имени файла.
- Авто-создание каталога `reports/logs/` при первом вызове.
- Идемпотентность: если логгер уже настроен этим модулем, повторное добавление хендлеров не выполняется.
- `logger.propagate = False`, чтобы сообщения не дублировались в root-логгер.

Реализация:

```python
from __future__ import annotations

import logging
import os
import sys
from logging.handlers import RotatingFileHandler

_LOG_DIR = os.path.join("reports", "logs")
_LOG_FILE = os.path.join(_LOG_DIR, "bitrix24.log")
_FORMAT = "%(asctime)s %(levelname)s %(name)s %(message)s"
_HANDLER_MARK = "_bitrix24_hygiene_handler"


def _already_configured(logger: logging.Logger) -> bool:
    return any(getattr(h, _HANDLER_MARK, False) for h in logger.handlers)


def get_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(level)

    if _already_configured(logger):
        return logger

    os.makedirs(_LOG_DIR, exist_ok=True)
    formatter = logging.Formatter(_FORMAT)

    stream_handler = logging.StreamHandler(stream=sys.stderr)
    stream_handler.setFormatter(formatter)
    setattr(stream_handler, _HANDLER_MARK, True)
    logger.addHandler(stream_handler)

    file_handler = RotatingFileHandler(
        _LOG_FILE,
        maxBytes=2_000_000,
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)
    setattr(file_handler, _HANDLER_MARK, True)
    logger.addHandler(file_handler)

    logger.propagate = False
    return logger
```

### C7. Замена `print` в Scope_Python_Files (S7.1..S7.5)

#### Scope_Python_Files

Множество Python-файлов под замену (Requirement 7, Glossary Scope_Python_Files):

- Все `*.py` в корне Target_Repo.
- Все `*.py` (рекурсивно) в `bitrix/`, `asr/`, `ui/`, `pipelines/`.

Исключения:

- `pipelines/bitnewton_sync.py` (Requirement 4.1, 7.10).
- `logging_setup.py` (Logging_Module — источник логгера, Requirement 7.12).
- `Stdout_Contract_Scripts` — определяются в ходе S7 grep-сверкой `.bat`-файлов (см. ниже).

#### Алгоритм для каждого файла `F` в Scope_Python_Files (после исключений)

1. grep на `print(` в `F`:
   ```powershell
   $prints = Select-String -Path $F -Pattern 'print\(' -ErrorAction SilentlyContinue
   ```
2. **Если 0 совпадений — пропустить файл.** Импорт `logging_setup` не добавляется, пустой диф не создаётся. (Свойство P12.)
3. **Если ≥1 совпадение:**
   - Добавить импорт + инициализацию логгера:
     ```python
     from logging_setup import get_logger

     logger = get_logger(__name__)
     ```
   - Место вставки:
     - После блока `from __future__ import ...`, если он есть (строго после последней `from __future__` строки, с пустой строкой-разделителем).
     - Иначе — в начало файла, после модульного docstring (если есть), иначе в самое начало.
   - Заменить каждый `print(...)` на `logger.<level>(...)` согласно контексту:
     | Уровень   | Эвристика контекста |
     |-----------|---------------------|
     | `WARNING` | «retry», «повтор», «backoff», «rate limit», «trying again», «пытаемся» |
     | `ERROR`   | «ошибка», «exception», «failed», «не удалось», «error», «не получилось» |
     | `INFO`    | «успех», «OK», «ready», «done», «подключение установлено», «готов», «завершено» |
     | `DEBUG`   | «DEBUG», «dump», «отладочный вывод», «debug info» |
   - При наличии активного исключения (внутри `except`-блока) для контекста ERROR допускается `logger.exception(...)` вместо `logger.error(...)`.
4. Запустить `python -m py_compile $F` после правки — синтаксическая проверка.

#### Stdout_Contract_Scripts — алгоритм определения

Файл `F.py` из Scope_Python_Files квалифицируется как Stdout_Contract_Script (и исключается из замены), если одновременно выполняются:

- (а) существует `*.bat` в Target_Repo, который вызывает `python F.py` (или `F.py` напрямую);
- (б) этот `.bat` потребляет stdout `F.py` (конструкции `for /f ... in ('python F.py ...') do ...`, `>`, `>>`, `|`).

Процедура:

```powershell
$scope = Get-ChildItem -Recurse -Include *.py `
  -Path .,bitrix,asr,ui,pipelines -ErrorAction SilentlyContinue |
  Where-Object { $_.FullName -notmatch '__pycache__' -and
                 $_.FullName -notmatch '\\venv\\|\\.venv\\|\\system--diarize\\|\\reports\\|\\docs\\' }

$batFiles = Get-ChildItem -Path . -Filter *.bat

foreach ($py in $scope) {
  $name = $py.Name
  $callers = $batFiles |
    Where-Object { (Get-Content $_.FullName -Raw) -match [regex]::Escape($name) }
  foreach ($bat in $callers) {
    $content = Get-Content $bat.FullName -Raw
    # признаки потребления stdout
    if ($content -match "for\s+/f[^\r\n]*['""]python[^'""]*$([regex]::Escape($name))" -or
        $content -match "$([regex]::Escape($name))[^\r\n]*\s*\>" -or
        $content -match "$([regex]::Escape($name))[^\r\n]*\s*\|") {
      Write-Host "STDOUT_CONTRACT $name via $($bat.Name)" -ForegroundColor Cyan
    }
  }
}
```

**Кандидаты Stdout_Contract_Scripts** (реальный список определяется в ходе S7):

- `dump_one_call.py` — с очень высокой вероятностью является stdout-дампом для `.bat`-обёртки; исключается из замены, если grep подтверждает.
- `check_python.py` (если существует и `check_python*.bat` анализирует его stdout) — проверяется в ходе S7.

Итоговый список фиксируется в отчёте итерации и в разделе «Открытые вопросы».

#### Под-коммиты S7.1..S7.5 (Requirement 7.14)

**S7.1 `refactor(hygiene): add logging_setup and convert core api modules`**

- `logging_setup.py` — новый (Requirement 7.1, 7.2, 7.3).
- `bitrix24_api.py`
- `bit_newton_asr.py`
- `config.py`
- `bitnewton_sync_to_api.py`
- `download_resolver.py`

Для каждого (кроме `logging_setup.py`) — алгоритм из раздела выше; `logging_setup.py` добавляется единоразово.

**S7.2 `refactor(hygiene): convert crm reporting modules to logging`**

- `crm_contacts.py`
- `crm_deals.py`
- `crm_leads.py`
- `crm_report.py`
- `custom_period_report.py`
- `detailed_calls_analysis.py`
- `detailed_managers_report.py`
- `managers_call_stats.py`
- `managers_call_stats_auto.py`
- `op_deals_analytics.py`
- `op_full_analytics.py`
- `op_lost_deals_analysis.py`
- `yesterday_leads.py`
- `yesterday_leads_stats.py`

**S7.3 `refactor(hygiene): convert UI modules to logging`**

- `web_ui.py`
- `ui_audio_downloader.py`
- `ui/audio_downloader.py` (если файл существует)

**S7.4 `refactor(hygiene): convert bitrix/asr package helpers to logging`**

- `bitrix/api.py`
- `bitrix/recordings.py`
- `bitrix/dump_one_call_debug.py` (если не Stdout_Contract)
- `asr/bitnewton.py`
- Оставшиеся `bitrix/__init__.py`, `asr/__init__.py`, `ui/__init__.py`, если они не удалены в S5 (для этих файлов проверяется `print(` — как правило, будет 0, файл пропускается).

**S7.5 `refactor(hygiene): convert remaining utility scripts to logging`**

- `download_ffmpeg.py`
- `dump_one_call.py` (если не Stdout_Contract)
- Любые другие `*.py` Scope_Python_Files, не вошедшие в S7.1..S7.4.

Каждый под-коммит — отдельный коммит в git, но S7.1..S7.5 логически соответствуют одной итерации Requirement 7.

### C8. Facade_Stub_Removal (S5)

Множество кандидатов на удаление — `Facade_Stub_Files`:

- `bitrix/__init__.py`
- `asr/__init__.py`
- `ui/__init__.py`

#### Алгоритм grep (для каждого `<name>` из `{bitrix, asr, ui}`)

Facade_Package_Import_Patterns (регексы, с учётом ведущих пробелов — отступы внутри функций/try-блоков):

1. `^\s*import <name>\b`
2. `^\s*from <name>\b`
3. `^\s*from <name>\.`
4. `^\s*import <name>\s+as\b`

Команда PowerShell:

```powershell
$pkg = 'bitrix'  # повторить для 'asr' и 'ui'
$pyFiles = Get-ChildItem -Recurse -Include *.py `
  -Exclude __pycache__,venv,.venv,reports,system--diarize,docs `
  -ErrorAction SilentlyContinue |
  Where-Object { $_.FullName -notmatch "\\$pkg\\__init__\.py$" }

$patterns = @(
  "^\s*import $pkg\b",
  "^\s*from $pkg\b",
  "^\s*from $pkg\.",
  "^\s*import $pkg\s+as\b"
)

$hits = foreach ($p in $patterns) {
  Select-String -Path $pyFiles -Pattern $p -ErrorAction SilentlyContinue
}

if (-not $hits) {
  Write-Host "$pkg: 0 hits, removing $pkg/__init__.py" -ForegroundColor Yellow
  git rm "$pkg/__init__.py"
} else {
  Write-Host "$pkg: $($hits.Count) hits, keeping $pkg/__init__.py" -ForegroundColor Green
  $hits | ForEach-Object { Write-Host "  $($_.Path):$($_.LineNumber): $($_.Line.Trim())" }
}
```

#### Алгоритм решения

- **0 совпадений** → `git rm <name>/__init__.py` (Requirement 10.2).
- **≥1 совпадение** → сохраняем файл, фиксируем список использований в отчёте итерации (Requirement 10.3).
- grep-отчёт собирается по всем трём пакетам в память итерации (не коммитится в репозиторий).

#### Особый кейс: `bitrix/__init__.py` с re-export

Текущий `bitrix/__init__.py` известен тем, что содержит строку:

```python
from bitrix24_api import Bitrix24API
```

Это означает, что модуль-пакет `bitrix` фактически **re-export-ит** имя `Bitrix24API` из корневого `bitrix24_api.py`, превращая `from bitrix import Bitrix24API` в рабочий импорт.

Правило для `bitrix/__init__.py`:

1. Выполнить grep по Facade_Package_Import_Patterns над Target_Repo.
2. Дополнительно выполнить grep по специальному паттерну `^\s*from\s+bitrix\s+import\s+Bitrix24API\b` (именно через пакет `bitrix`, а не через модуль `bitrix24_api`).
3. Если найдено хотя бы одно использование `from bitrix import Bitrix24API` — **сохраняем** `bitrix/__init__.py`, потому что без него этот импорт не сработает (в Python 3 namespace-package не переносит символы из других файлов без явного `__init__.py`).
4. Если таких использований нет и общий grep по пакету `bitrix` тоже пуст — удаляем.
5. Результат фиксируется в отчёте итерации.

#### Коммит S5

- Сообщение: `chore(hygiene): remove unused facade __init__.py files`.
- Файлы: удаление `<name>/__init__.py` только для пакетов с 0 совпадений.
- Если все три пакета сохранены — S5 **пропускается**, позиция в Commit_History остаётся пустой (Requirement 8.5, 8.6, 10.8). grep-отчёт фиксируется в отчёте итерации как обоснование пропуска.

#### Namespace-packages (Requirement 10.6)

В Python 3 при отсутствии `__init__.py` каталог с `*.py` становится namespace-package; импорты вида `from bitrix.api import X` продолжают работать, если по-прежнему существует `bitrix/api.py`. Заменитель `__init__.py` после удаления создавать не нужно. Это не противоречит особому кейсу выше: если использовался именно `from bitrix import Bitrix24API` — `__init__.py` сохраняется, и namespace-package режим не активируется.


## Data Models

Итерация не вводит персистентных моделей данных и не меняет форматы Report_Outputs. Ниже — служебные структуры, необходимые для корректности шагов и проверок.

### DM1. Карта Requirement → Files (для свойства P8 «локальность коммита»)

Под 7 коммитов (S1..S7, последний разбит на S7.1..S7.5):

| Коммит | Requirement | Ожидаемые изменённые пути |
|---|---|---|
| S1 | R1 (init) | `.git/` (создание), `.gitignore` (добавление tooling-блока) |
| S2 | R2 (archive) | `docs/_archive/` (создание при отсутствии), `docs/_archive/<файл>` (добавление), `<root>/<файл>` (удаление) — для 11 Hygiene_Notes минус исключённые по grep |
| S3 | R3 (reports cleanup) | `reports/<Transient_Artifact>` (удаление), `reports/<expired Report_Output>` (удаление), `.gitignore` (добавление reports-блока) |
| S4 | R5 (facade decision) | `docs/_archive/FACADE_DECISION.md` (добавление) |
| S5 | R10 (facade stub removal) | `bitrix/__init__.py`, `asr/__init__.py`, `ui/__init__.py` — удаляются только те, по которым grep дал 0 совпадений; S5 пропускается, если таких нет |
| S6 | R6 (pyproject) | `pyproject.toml` (добавление) |
| S7.1 | R7 (logging, core api) | `logging_setup.py` (новый), `bitrix24_api.py`, `bit_newton_asr.py`, `config.py`, `bitnewton_sync_to_api.py`, `download_resolver.py` — только файлы, в которых был `print(` |
| S7.2 | R7 (crm reporting) | `crm_contacts.py`, `crm_deals.py`, `crm_leads.py`, `crm_report.py`, `custom_period_report.py`, `detailed_calls_analysis.py`, `detailed_managers_report.py`, `managers_call_stats.py`, `managers_call_stats_auto.py`, `op_deals_analytics.py`, `op_full_analytics.py`, `op_lost_deals_analysis.py`, `yesterday_leads.py`, `yesterday_leads_stats.py` — только файлы с `print(` |
| S7.3 | R7 (UI) | `web_ui.py`, `ui_audio_downloader.py`, `ui/audio_downloader.py` (если существует) — только с `print(` |
| S7.4 | R7 (bitrix/asr packages) | `bitrix/api.py`, `bitrix/recordings.py`, `bitrix/dump_one_call_debug.py` (если не Stdout_Contract), `asr/bitnewton.py`, оставшиеся `__init__.py` пакетов если не удалены в S5 |
| S7.5 | R7 (utilities) | `download_ffmpeg.py`, `dump_one_call.py` (если не Stdout_Contract), прочие Scope_Python_Files |

Свойство P8: для любого коммита `c` множество `git show --name-only c` ⊆ строки DM1 для соответствующего Requirement.

### DM2. Запись лога

- Каналы: stderr + `reports/logs/bitrix24.log` (+ ротированные `.1..5`).
- Формат: `YYYY-MM-DD HH:MM:SS,ms LEVEL logger.name message`.
- Пример: `2026-05-10 16:20:00,123 WARNING bitrix24_api Retry 2/5 for GET crm.deal.list`.

### DM3. Stdout_Contract_Report (ведётся в отчёте итерации)

Структура записи:

```
{
  "script": "dump_one_call.py",
  "bat_callers": ["run_dump_one_call.bat"],
  "stdout_consumption_evidence": "for /f \"delims=\" %%o in ('python dump_one_call.py %1') do ...",
  "decision": "exclude_from_print_replacement"
}
```

Список фиксируется по результатам grep в S7.1 и используется всеми последующими под-коммитами S7.*.

### DM4. Gitignore_Lines_Registry (внутреннее)

- `tooling_lines` (S1): `.ruff_cache/`, `.pytest_cache/`, `.mypy_cache/`, `.cache/`, `*.log`, `.venv/`, `venv/`, `__pycache__/`.
- `reports_transient_lines` (S3): `reports/debug_download_*.html`, `reports/debug_download_link_*.html`, `reports/selenium_download_*/`, `reports/streamlit_bitnewton.*.log`, `reports/chrome_profile/`, `reports/call.mp3`, `reports/logs/*.log`, `reports/logs/*.log.*`.

Добавление каждой строки — идемпотентно через `Add-GitignoreLines` (C2).

## Error Handling

### EH1. Отсутствие `git` в PATH (Риск R1)

- Симптом: `git : команда не найдена` при вызове `git init` на S1.
- Обработка: итерация останавливается, S1 не считается успешным, в отчёте итерации фиксируется причина. Пользователю предлагается установить Git for Windows или скорректировать PATH.
- Обратимость: S1 не делает разрушительных действий до успешного `git init`.

### EH2. `.git` уже существует (Requirement 1.5)

- Симптом: `Test-Path .git` возвращает `True` до S1.
- Обработка: S1 пропускается в части `git init`, но продолжает дополнять `.gitignore` (идемпотентно). Факт существующего репозитория фиксируется в отчёте.

### EH3. Конфликт имён в `docs/_archive/` (Риск R2)

- Симптом: при `git mv <name>` целевой файл уже существует в `docs/_archive/`.
- Обработка: операция для конкретного файла пропускается, остальные перемещения продолжаются. Конфликт записывается в отчёт.

### EH4. Hygiene_Notes упомянут в Bat_Contract (Requirement 2.4, 2.5)

- Симптом: grep по `*.bat`/`*.py` находит имя из Hygiene_Notes.
- Обработка: файл исключается из перемещения; если перемещение уже выполнено — возврат через `git mv` обратно. Фиксация в отчёте.

### EH5. Расхождение версии Python между `pyproject.toml` и `check_python*.bat` (Риск R4)

- Симптом: `check_python*.bat` ожидает версию, отличную от `requires-python = ">=3.10"`.
- Обработка: на S6 — ручная сверка. Значение `requires-python` корректируется до коммита.

### EH6. Случайный автоформат на S6 (Риск R5)

- Симптом: `git diff --stat` после S6 показывает изменения в `.py`.
- Обработка: изменения откатываются (`git checkout -- <path>`). В коммит S6 попадает только `pyproject.toml`.

### EH7. Логирование при отсутствии каталога `reports/logs/`

- Обработка в `logging_setup.py`: `os.makedirs(_LOG_DIR, exist_ok=True)` перед созданием `RotatingFileHandler`. Отсутствие каталога — не ошибка.

### EH8. Ошибки удаления Transient_Artifacts

- Симптом: файл заблокирован процессом Chrome/Selenium, `Remove-Item` падает.
- Обработка: `-ErrorAction SilentlyContinue`, оставшиеся файлы фиксируются в отчёте, пользователь закрывает процесс и повторяет S3 (операция идемпотентна).

### EH9. Ошибочная классификация файла как Stdout_Contract_Script (Риск R10)

- Симптом: после S7 `.bat`, потребляющий stdout Python-скрипта, перестал получать ожидаемый вывод.
- Обработка: выявление через smoke-запуск `.bat` (если безопасно); при обнаружении — `git revert <S7.x>` соответствующего под-коммита или точечная правка, возвращающая `print(...)`. Список Stdout_Contract_Scripts корректируется, итерация повторяется.

### EH10. Цикл импорта `logging_setup` → `<module>` → `logging_setup` (Риск R11)

- Симптом: `ImportError: cannot import name 'get_logger' from partially initialized module`.
- Обработка: `logging_setup.py` не должен импортировать ничего из Scope_Python_Files; единственные зависимости — стандартная библиотека (`logging`, `logging.handlers`, `os`, `sys`). Это обеспечивает отсутствие цикла.

### EH11. Запуск Python не из корня Target_Repo (Риск R12)

- Симптом: `ModuleNotFoundError: No module named 'logging_setup'` при запуске скрипта из подкаталога или через абсолютный путь.
- Причина: `logging_setup.py` лежит в корне Target_Repo, и `from logging_setup import get_logger` требует, чтобы `sys.path` содержал корень.
- Митигация: все `.bat` из Bat_Contract уже выполняют `cd /d <root>` перед `python`. На этапе S7 это поведение проверяется:
  ```powershell
  Select-String -Path *.bat -Pattern 'cd\s+/d\s+%~dp0|cd\s+/d\s+"%~dp0"|pushd\s+%~dp0'
  ```
- Если какой-то `.bat` запускает Python из другого рабочего каталога — этот `.bat` фиксируется в отчёте; правка Bat_Contract запрещена (Requirement 4.2), поэтому соответствующий Python-скрипт добавляется в Stdout_Contract_Scripts или sys.path-совместимый импорт решается в будущей итерации.

### EH12. Нарушение публичного интерфейса при замене print (Риск R7)

- Симптом: `inspect.signature(...)` для публичных методов отличается от baseline.
- Обработка: правка локализуется через `git diff HEAD~1 -- <file>`, лишние изменения откатываются. В коммит под-коммита S7.x попадают только импорт + замены `print`.


## Correctness Properties

*Свойство — характеристика или поведение, которое должно оставаться истинным во всех валидных исполнениях системы. Свойства — это мост между человекочитаемой спецификацией и машинно-проверяемыми гарантиями корректности.*

### Property 1: Идемпотентность обновления `.gitignore`

*Для любого* начального содержимого файла `.gitignore` и любого множества целевых строк `L`, операция «добавить строки из `L`, отсутствующие в файле» после двух последовательных применений даёт то же содержимое, что и после одного применения, и каждая строка из `L` присутствует в файле ровно один раз.

**Validates: Requirements 1.4, 3.3**

### Property 2: Инвариантность содержимого Hygiene_Notes при перемещении

*Для любого* файла `f` из Hygiene_Notes, попавшего в перемещение (не исключённого по Requirement 2.4), содержимое `f` (байты) до перемещения в `docs/_archive/` равно содержимому `f` после перемещения, и имя файла сохраняется.

**Validates: Requirements 2.1, 2.3**

### Property 3: Чистка удаляет ровно Transient_Artifacts

*Для любого* файла в `Reports_Directory`, соответствующего хотя бы одному шаблону Transient_Artifacts, этот файл отсутствует после S3; и для любого файла вне Transient_Artifacts, не попадающего под TTL-политику Report_Outputs, его имя и содержимое после S3 совпадают с теми, что были до S3.

**Validates: Requirements 3.1, 3.3**

### Property 4: Консервативность чистки Reports_Directory

*Для любого* файла `f` в `Reports_Directory`, который не соответствует ни одному шаблону Transient_Artifacts, не подпадает под TTL-политику Report_Outputs и не является Singleton/Latest, имя, путь и содержимое `f` после S3 совпадают с теми, что были до S3.

**Validates: Requirements 3.5, 3.7**

### Property 5: Инвариантность Pipeline_Script, Bat_Contract и файлов вне Scope

*Для любого* файла `f` из множества

- `{pipelines/bitnewton_sync.py}` (Pipeline_Script),
- Bat_Contract (все `*.bat` в корне Target_Repo),
- 17 Python-скриптов Bat_Contract из Requirement 4.3,
- `{bitrix24_api.py}` до шага S7.1 (включительно до момента замены `print`),
- `{bitrix/api.py, bitrix/recordings.py, bitrix/dump_one_call_debug.py}` до S7.4,
- `{bitnewton_sync_to_api.py}` до S7.1,
- все прочие `*.py` вне Scope_Python_Files,

путь и SHA-256 `f` остаются неизменными в течение всех шагов итерации, за исключением точечных правок соответствующих файлов на S7.x, ограниченных импортом `logging_setup` и заменой `print(...)` на `logger.*(...)` без изменения публичных сигнатур.

**Validates: Requirements 4.1, 4.2, 4.3, 4.5, 5.4, 6.6, 7.10**

### Property 6: Отсутствие `print` в Bitrix_API_Module после S7.1

*Для любого* вхождения шаблона `print(` в исходнике `bitrix24_api.py` вне комментариев и строковых литералов после S7.1 — множество таких вхождений пусто.

**Validates: Requirements 7.5 (по bitrix24_api.py)**

### Property 7: Инвариантность публичного интерфейса Scope_Python_Files

*Для любой* публичной функции, метода или класса (имя которого не начинается с `_`) в любом файле из Scope_Python_Files, имя, позиционные и именованные параметры, значения по умолчанию и возвращаемый тип (если заявлен) после соответствующего под-коммита S7.x совпадают с теми, что были до итерации.

**Validates: Requirements 7.13**

### Property 8: Локальность коммита по DM1

*Для любого* коммита `c` из 7 позиционных коммитов итерации (S1..S7, где S7 представлен под-коммитами S7.1..S7.5), множество файлов, затронутых `c` (`git show --name-only`), является подмножеством ожидаемых файлов соответствующего Requirement согласно карте DM1, и порядок коммитов в Commit_History совпадает с S1 → S2 → S3 → S4 → (S5) → S6 → S7.1 → S7.2 → S7.3 → S7.4 → S7.5 (с возможным пропуском S5 и/или отдельных под-коммитов S7.x, если ни один файл в их наборе не содержал `print(`).

**Validates: Requirements 6.6, 7.14, 8.1, 8.2, 8.4, 10.9**

### Property 9: TTL Report_Outputs с защитой Latest и Singleton

*Для любого* файла `F` в `Reports_Directory` после S3:

- если `F` соответствует шаблону одного из семейств Report_Outputs (`bitnewton_sync_report_*.json`, `bitnewton_sync_report_*.xlsx`, `bitnewton_reevaluated_report_*.json`) и имя `F` **не** совпадает с `latest_bitnewton_report.*`, `state_cache.json`, `deal_filter.json`, то `LastWriteTime(F) >= now(S3) - Reports_TTL_Days`;
- если имя `F` совпадает с `latest_bitnewton_report.*`, `state_cache.json` или `deal_filter.json`, то `F` присутствует в `Reports_Directory` после S3 независимо от `LastWriteTime(F)`.

**Validates: Requirements 3.2, 3.4, 3.5, 3.6**

### Property 10: Удаление Facade_Stub ⟺ 0 использований пакета

*Для любого* имени пакета `name ∈ {bitrix, asr, ui}`:

- если grep по Facade_Package_Import_Patterns над `*.py` Target_Repo (с исключениями каталогов `venv/`, `.venv/`, `__pycache__/`, `reports/`, `system--diarize/`, `docs/` и самого `<name>/__init__.py`) возвращает 0 совпадений, **И** для `name = 'bitrix'` дополнительно grep по `from bitrix import Bitrix24API` возвращает 0 совпадений — то после S5 `<name>/__init__.py` отсутствует;
- если grep возвращает ≥ 1 совпадение (либо обнаружен re-export `from bitrix import Bitrix24API` для `bitrix`) — после S5 `<name>/__init__.py` присутствует с теми же байтами, что и до S5.

**Validates: Requirements 10.1, 10.2, 10.3**

### Property 11: Нет `print` в Scope_Python_Files после S7

*Для любого* файла `F` из Scope_Python_Files после выполнения всех под-коммитов S7.1..S7.5, множество вхождений шаблона `print(` в `F` (вне комментариев `# ...` и вне строковых литералов) пусто, **при условии** что `F` не входит в множество исключений `{pipelines/bitnewton_sync.py, logging_setup.py} ∪ Stdout_Contract_Scripts`.

**Validates: Requirements 7.5, 7.10, 7.11, 7.12**

### Property 12: Импорт `logging_setup` ⟺ был `print` до S7

*Для любого* файла `F` из Scope_Python_Files (после исключений):

- если до S7 в `F` был хотя бы один вызов `print(...)`, то после соответствующего под-коммита S7.x в `F` присутствует строка `from logging_setup import get_logger` и модульная инициализация `logger = get_logger(__name__)`;
- если до S7 в `F` не было ни одного `print(...)`, то `F` не изменяется на S7 (диф пуст), импорт `logging_setup` не добавляется.

**Validates: Requirements 7.4, 7.5**


## Порядок коммитов

Семь позиционных коммитов (S1..S7), последний разбит на серию под-коммитов S7.1..S7.5 (Requirement 7.14). Строгий порядок по Requirement 8.2; любой позиционный коммит, не внёсший изменений, пропускается без сдвига номеров (Requirement 8.5). Под-коммиты S7.x тоже могут пропускаться независимо, если ни в одном файле набора нет `print(`.

1. **S1 — init repo**
   - Сообщение: `chore(hygiene): init local git and baseline .gitignore`.
   - Файлы: `.git/` (создание), `.gitignore` (добавление tooling-блока).

2. **S2 — archive legacy .txt notes → `docs/_archive/`**
   - Сообщение: `chore(hygiene): archive legacy .txt notes into docs/_archive/`.
   - Файлы: 11 перемещений `git mv <file> docs/_archive/<file>` (минус исключения по Requirement 2.4).

3. **S3 — cleanup transient + TTL 30 дней для Report_Outputs (кроме `latest_bitnewton_report.*` и `state_cache.json/deal_filter.json`)**
   - Сообщение: `chore(hygiene): cleanup transient artifacts and expire old reports (TTL 30d)`.
   - Файлы: удаления в `reports/` (Transient_Artifacts + просроченные Report_Outputs), `.gitignore` (reports-блок).

4. **S4 — facade decision → `docs/_archive/FACADE_DECISION.md`**
   - Сообщение: `docs(hygiene): record facade decision for bitrix24_api / bitrix / bitnewton_sync_to_api`.
   - Файлы: `docs/_archive/FACADE_DECISION.md`.

5. **S5 — remove unused facade `__init__.py` (bitrix/asr/ui) — может быть пропущен**
   - Сообщение: `chore(hygiene): remove unused facade __init__.py files`.
   - Файлы: удаляются только те из `{bitrix/__init__.py, asr/__init__.py, ui/__init__.py}`, по которым grep дал 0 совпадений (с учётом особого кейса `from bitrix import Bitrix24API`).
   - Условие пропуска: если все три сохранены — коммит S5 не создаётся, grep-отчёт фиксируется в отчёте итерации (Requirement 8.6, 10.8).

6. **S6 — pyproject + ruff + black**
   - Сообщение: `build(hygiene): add pyproject.toml with ruff and black config`.
   - Файлы: `pyproject.toml`.

7. **S7 — logging_setup + `print` → `logging` для Scope_Python_Files** (разбит на S7.1..S7.5)

   7.1 `refactor(hygiene): add logging_setup and convert core api modules`
       - `logging_setup.py` (новый) + `bitrix24_api.py` + `bit_newton_asr.py` + `config.py` + `bitnewton_sync_to_api.py` + `download_resolver.py`.
       - Файлы правятся только при наличии `print(`; `logging_setup.py` добавляется всегда.

   7.2 `refactor(hygiene): convert crm reporting modules to logging`
       - 14 файлов из `crm_contacts.py` … `yesterday_leads_stats.py` (см. список в C7 / DM1).

   7.3 `refactor(hygiene): convert UI modules to logging`
       - `web_ui.py`, `ui_audio_downloader.py`, `ui/audio_downloader.py` (если существует).

   7.4 `refactor(hygiene): convert bitrix/asr package helpers to logging`
       - `bitrix/api.py`, `bitrix/recordings.py`, `bitrix/dump_one_call_debug.py` (если не Stdout_Contract), `asr/bitnewton.py`, оставшиеся `__init__.py` пакетов если не удалены в S5.

   7.5 `refactor(hygiene): convert remaining utility scripts to logging`
       - `download_ffmpeg.py`, `dump_one_call.py` (если не Stdout_Contract), прочие Scope_Python_Files, не вошедшие в S7.1..S7.4.

### Проверка порядка

```powershell
git log --oneline --reverse | Select-Object -First 12
# Ожидание (с возможными пропусками S5 и отдельных S7.x):
# <sha> chore(hygiene): init local git and baseline .gitignore
# <sha> chore(hygiene): archive legacy .txt notes into docs/_archive/
# <sha> chore(hygiene): cleanup transient artifacts and expire old reports (TTL 30d)
# <sha> docs(hygiene): record facade decision for bitrix24_api / bitrix / bitnewton_sync_to_api
# <sha> chore(hygiene): remove unused facade __init__.py files                 # может отсутствовать
# <sha> build(hygiene): add pyproject.toml with ruff and black config
# <sha> refactor(hygiene): add logging_setup and convert core api modules
# <sha> refactor(hygiene): convert crm reporting modules to logging
# <sha> refactor(hygiene): convert UI modules to logging
# <sha> refactor(hygiene): convert bitrix/asr package helpers to logging
# <sha> refactor(hygiene): convert remaining utility scripts to logging
```

## Риски

### R1. Отсутствие `git` в PATH

- Влияние: S1 не может быть выполнен.
- Митигация: перед S1 выполняется `git --version`; при отсутствии — итерация останавливается, в отчёте фиксируется причина.

### R2. Конфликт имён в `docs/_archive/`

- Влияние: `git mv` падает для отдельного файла из Hygiene_Notes.
- Митигация: перед каждым `git mv` — `Test-Path` целевого файла в `docs/_archive/`; при конфликте конкретный файл пропускается, остальные продолжают перемещаться.

### R3. Hygiene_Notes упомянут в `.bat`/`.py`

- Влияние: перемещение может сломать существующие сценарии Bat_Contract или Python-скриптов.
- Митигация: grep по `*.bat` и `*.py` на каждое имя Hygiene_Notes перед S2; совпадения исключаются из перемещения (EH4).

### R4. Расхождение версии Python между `pyproject.toml` и `check_python*.bat`

- Влияние: `requires-python` может расходиться с тем, что ожидают `.bat`.
- Митигация: ручная сверка на S6 до коммита; корректировка `requires-python` при расхождении (EH5).

### R5. Случайный автоформат на S6

- Влияние: Ruff/Black запускаются по привычке и переформатируют существующий код, нарушая Property 5.
- Митигация: S6 ограничен только созданием `pyproject.toml`; ни `ruff check --fix`, ни `black` не запускаются на существующем коде (Requirement 6.6); `git diff --stat` проверяется перед коммитом.

### R6. Блокировка Transient_Artifacts процессом Chrome/Selenium

- Влияние: `chrome_profile/` или `selenium_download_*/` не удаляются.
- Митигация: `-ErrorAction SilentlyContinue`; повтор S3 после закрытия процессов; операция идемпотентна.

### R7. Изменение публичного API при замене `print`

- Влияние: случайная правка сигнатуры метода в одном из файлов Scope_Python_Files.
- Митигация: диапазон правок на каждом под-коммите S7.x строго ограничен импортом `logging_setup` + заменой `print(...)` → `logger.*(...)`; после каждого под-коммита — `inspect.signature` сверка с baseline (Property 7, EH12).

### R8. Отсутствие каталога `docs/`

- Влияние: минимальное; фиксируется для прозрачности.
- Митигация: `New-Item -ItemType Directory -Force -Path docs\_archive` на S2.

### R9. Ошибка в grep-регексах Facade_Package_Import_Patterns

- Влияние: неправильная классификация пакета как неиспользуемого — удаление нужного `__init__.py` и слом импортов.
- Митигация:
  - Паттерны включают ведущие `^\s*` (для импортов внутри функций / `try`-блоков).
  - Паттерны перечислены явно: `import <name>`, `from <name>`, `from <name>.`, `import <name> as`.
  - Для `bitrix` дополнительно проверяется `from bitrix import Bitrix24API` (особый кейс re-export).
  - Для каждого пакета фиксируется grep-отчёт в отчёте итерации независимо от результата (Requirement 10.4).
  - Перед S5 — smoke-импорт: `python -c "import bitrix; import bitrix.api; from bitrix import Bitrix24API"` (только если ожидается, что эти импорты используются).

### R10. Ошибочная классификация Stdout_Contract_Scripts

- Влияние: `.bat`, потребляющий stdout Python-скрипта, перестаёт получать данные после замены `print` на `logger.*` (stderr вместо stdout).
- Митигация:
  - Фиксированный алгоритм определения (C7, подраздел «Stdout_Contract_Scripts»): `.bat` вызывает скрипт **И** использует `for /f`, `>`, `|`.
  - Перед каждым под-коммитом S7.x — smoke-запуск соответствующих `.bat`-обёрток, если возможно.
  - Если классификация ошибочна — EH9 (`git revert` под-коммита + точечная правка).
  - Список кандидатов фиксируется в «Открытых вопросах».

### R11. Цикл импорта `logging_setup`

- Влияние: `logging_setup.py` импортирует что-то из файлов, которые сами импортируют `logging_setup` → `ImportError` при старте.
- Митигация: `logging_setup.py` зависит только от стандартной библиотеки (`logging`, `logging.handlers`, `os`, `sys`). Никаких импортов из Scope_Python_Files (EH10).

### R12. Запуск Python не из корня Target_Repo

- Влияние: `from logging_setup import get_logger` падает `ModuleNotFoundError`, если рабочий каталог — не корень Target_Repo.
- Митигация:
  - На S7.1 проверяется, что все `.bat` из Bat_Contract выполняют `cd /d %~dp0` (или `pushd %~dp0`) перед `python`:
    ```powershell
    Select-String -Path *.bat -Pattern 'cd\s+/d\s+%~dp0|pushd\s+%~dp0'
    ```
  - `.bat`, запускающие Python без `cd` в корень, фиксируются в отчёте; соответствующие Python-скрипты либо добавляются в Stdout_Contract_Scripts (если они и так stdout-контрактны), либо получают рекомендацию для будущей итерации (правка Bat_Contract в текущей итерации запрещена Requirement 4.2).
  - Подкаталоги `bitrix/`, `asr/`, `ui/`, `pipelines/` в текущей итерации не содержат самостоятельных входных точек через Bat_Contract, поэтому для них достаточно положиться на корневой запуск (EH11).


## План проверки

После каждого шага — минимальный набор проверок в PowerShell, запускаемых в корне Target_Repo.

### Baseline (до S1)

```powershell
git --version                          # наличие git
Test-Path .git                          # ожидается False (иначе EH2)

# Снапшот SHA-256 для Property 5:
$baseline = @(
  'pipelines\bitnewton_sync.py',
  'bitrix24_api.py',
  'bitnewton_sync_to_api.py',
  'bitrix\__init__.py','bitrix\api.py','bitrix\recordings.py','bitrix\dump_one_call_debug.py'
) + (Get-ChildItem -Path . -Filter *.bat | ForEach-Object { $_.Name }) + @(
  'bit_newton_asr.py','crm_contacts.py','crm_deals.py','crm_leads.py','crm_report.py',
  'custom_period_report.py','detailed_calls_analysis.py','detailed_managers_report.py',
  'managers_call_stats.py','managers_call_stats_auto.py','op_deals_analytics.py',
  'op_full_analytics.py','op_lost_deals_analysis.py','ui_audio_downloader.py',
  'web_ui.py','yesterday_leads.py','yesterday_leads_stats.py'
)
$baseline | Where-Object { Test-Path $_ } | ForEach-Object {
  "$((Get-FileHash $_ -Algorithm SHA256).Hash)  $_"
} | Out-File reports\_hygiene_baseline_sha256.txt -Encoding utf8
# Примечание: файл-снапшот хранится в reports\, но не коммитится (reports\_hygiene_* добавить в .gitignore при необходимости).
```

### После S1 (init repo)

```powershell
Test-Path .git                                              # -> True
git log --oneline                                           # 1 коммит S1
Get-Content .gitignore |
  Select-String -Pattern '\.ruff_cache','\.pytest_cache','\.mypy_cache',
                          '__pycache__','venv','\.venv','\.cache','\*\.log'
# все 8 шаблонов должны присутствовать

# Property 1 — идемпотентность:
$h1 = Get-FileHash .gitignore -Algorithm SHA256
# Повторный вызов Add-GitignoreLines для того же набора строк:
# ... (функция вызывается второй раз)
$h2 = Get-FileHash .gitignore -Algorithm SHA256
$h1.Hash -eq $h2.Hash                                       # -> True
```

### После S2 (archive legacy txt notes)

```powershell
Test-Path docs\_archive                                     # -> True
$notes = @(
  'FIXED.txt','FIXED_ENCODING.txt','INSTALL_FFMPEG.txt','NEXT_STEP.txt',
  'PROJECT_STRUCTURE.txt','PROJECT_SUMMARY.txt','README_FIRST.txt',
  'SETUP_READY.txt','START_HERE.txt','SUCCESS.txt','TROUBLESHOOTING.txt'
)
foreach ($n in $notes) {
  $root = Test-Path $n
  $arc  = Test-Path "docs\_archive\$n"
  "$n : root=$root archive=$arc"
}

Test-Path kriterii_ocenki.txt                               # -> True (Protected_Txt)
Test-Path requirements.txt                                  # -> True
Test-Path requirements_ui.txt                               # -> True

git log --oneline                                           # 2 коммита
```

- Property 2 — для каждого перемещённого файла сверить SHA-256 с baseline.

### После S3 (cleanup reports + TTL)

```powershell
# Property 3 — Transient_Artifacts удалены:
Get-ChildItem -Path reports\debug_download_*.html,
                    reports\debug_download_link_*.html,
                    reports\selenium_download_*,
                    reports\streamlit_bitnewton.*.log,
                    reports\chrome_profile,
                    reports\call.mp3 -ErrorAction SilentlyContinue
# ожидается пустой результат

# Property 9 — TTL 30 дней:
$cutoff = (Get-Date).AddDays(-30)
Get-ChildItem reports\bitnewton_sync_report_*.json,
              reports\bitnewton_sync_report_*.xlsx,
              reports\bitnewton_reevaluated_report_*.json -ErrorAction SilentlyContinue |
  Where-Object { $_.LastWriteTime -lt $cutoff }
# ожидается пустой результат (не осталось Report_Outputs старше 30 дней)

# Latest_Report_Files — защищены:
Get-ChildItem reports\latest_bitnewton_report.* -ErrorAction SilentlyContinue
# ожидается непустой список, даже если файлы старые

# Singleton_Report_Files — защищены:
Test-Path reports\state_cache.json                          # -> True
Test-Path reports\deal_filter.json                          # -> True

# .gitignore расширен:
Get-Content .gitignore |
  Select-String -Pattern 'reports/debug_download','reports/selenium_download',
                          'streamlit_bitnewton','reports/chrome_profile',
                          'reports/call\.mp3','reports/logs'

git log --oneline                                           # 3 коммита
```

### После S4 (facade decision)

```powershell
Test-Path docs\_archive\FACADE_DECISION.md                  # -> True
Select-String -Path docs\_archive\FACADE_DECISION.md `
  -Pattern 'bitrix24_api','bitrix[/\\]','bitnewton_sync_to_api'
git log --oneline                                           # 4 коммита
```

### После S5 (удаление Facade_Stub_Files, может быть пропущен)

```powershell
# Для каждого пакета — соответствие grep и Test-Path:
foreach ($pkg in @('bitrix','asr','ui')) {
  $patterns = @(
    "^\s*import $pkg\b",
    "^\s*from $pkg\b",
    "^\s*from $pkg\.",
    "^\s*import $pkg\s+as\b"
  )
  $pyFiles = Get-ChildItem -Recurse -Include *.py `
    -Exclude __pycache__,venv,.venv,reports,system--diarize,docs `
    -ErrorAction SilentlyContinue |
    Where-Object { $_.FullName -notmatch "\\$pkg\\__init__\.py$" }
  $hits = foreach ($p in $patterns) {
    Select-String -Path $pyFiles -Pattern $p -ErrorAction SilentlyContinue
  }
  if ($pkg -eq 'bitrix') {
    $hits += Select-String -Path $pyFiles -Pattern '^\s*from\s+bitrix\s+import\s+Bitrix24API\b' -ErrorAction SilentlyContinue
  }
  $exists = Test-Path "$pkg\__init__.py"
  if (-not $hits) {
    # Property 10: 0 hits ⇒ __init__.py удалён
    $exists -eq $false
  } else {
    # Property 10: ≥1 hit ⇒ __init__.py сохранён
    $exists -eq $true
  }
}

git log --oneline   # 5 коммитов, если хотя бы один __init__.py удалён; иначе 4
```

### После S6 (pyproject)

```powershell
Test-Path pyproject.toml                                    # -> True
Select-String -Path pyproject.toml `
  -Pattern '\[tool\.ruff\]','\[tool\.ruff\.lint\]','\[tool\.black\]',
           'line-length\s*=\s*100','target-version',
           '"reports"','"venv"','"\.venv"','"system--diarize"','"asr"','"ui"','"docs"'

git show --stat HEAD                                        # только pyproject.toml
git log --oneline                                           # 5 или 6 коммитов
```

### После S7.1..S7.5 (logging_setup + print→logging)

```powershell
# Logging_Module:
Test-Path logging_setup.py                                  # -> True
Select-String -Path logging_setup.py `
  -Pattern 'def get_logger','RotatingFileHandler','%\(asctime\)s','%\(levelname\)s','%\(name\)s'

# Property 11 — нет print в Scope_Python_Files (вне исключений):
$scope = Get-ChildItem -Recurse -Include *.py `
  -Path .,bitrix,asr,ui,pipelines -ErrorAction SilentlyContinue |
  Where-Object {
    $_.FullName -notmatch '__pycache__' -and
    $_.FullName -notmatch '\\venv\\|\\.venv\\|\\system--diarize\\|\\reports\\|\\docs\\' -and
    $_.Name -notin @('bitnewton_sync.py','logging_setup.py') -and
    $_.Name -notin $StdoutContractScripts
  }
$leftoverPrints = Select-String -Path $scope -Pattern '^\s*print\(' -ErrorAction SilentlyContinue
$leftoverPrints   # ожидается пустой результат

# Property 12 — импорт logging_setup ⟺ был print:
foreach ($f in $scope) {
  $hasLogger = (Select-String -Path $f -Pattern 'from logging_setup import get_logger').Count -ge 1
  # если в git diff HEAD~N до S7.x были print — hasLogger должен быть True
  # (сверка с baseline snapshot before/after)
}

# Property 7 — публичный интерфейс не изменился:
python -c "import bitrix24_api; import inspect; from bitrix24_api import Bitrix24API; print([(n, str(inspect.signature(getattr(Bitrix24API,n)))) for n in dir(Bitrix24API) if not n.startswith('_') and callable(getattr(Bitrix24API,n))])"
# сравнить с baseline, записанным до S7.1

# Smoke-проверка логирования:
python -c "from logging_setup import get_logger; get_logger('smoke').info('hello')"
Test-Path reports\logs\bitrix24.log                         # -> True

# Синтаксическая проверка всех затронутых файлов:
$scope | ForEach-Object { python -m py_compile $_.FullName }

git show --stat HEAD~4..HEAD                                # набор изменений S7.1..S7.5
git log --oneline                                           # 9..11 коммитов (в зависимости от пропусков)
```

### Финальная сверка (Property 5, Property 8)

```powershell
# Property 5 — SHA-256 инвариант для Pipeline_Script, Bat_Contract, 17 Python-скриптов:
# (сравнить с reports\_hygiene_baseline_sha256.txt)
$after = @('pipelines\bitnewton_sync.py') +
         (Get-ChildItem -Path . -Filter *.bat | ForEach-Object { $_.Name })
$after | Where-Object { Test-Path $_ } | ForEach-Object {
  "$((Get-FileHash $_ -Algorithm SHA256).Hash)  $_"
}
# Сравнить построчно с baseline — все SHA должны совпасть.

# Property 8 — локальность коммитов:
foreach ($sha in (git log --pretty=format:%H S1..HEAD)) {
  git show --name-only $sha
  # Проверить, что множество файлов ⊆ DM1 для соответствующего коммита.
}
```

### Опциональный smoke Bat_Contract

- `test_connection.bat` — опциональная проверка, что контракт не сломан.
- Запуск 1–2 «безопасных» `.bat` (без побочных эффектов на Bitrix24), например `check_python.bat`.

## Что передать Codex

- Выполнить итерацию в `C:\Users\koval\bat\bitrix24-automation` в 7 позиционных коммитов (S7 — серия под-коммитов S7.1..S7.5) по данному дизайну.
- Строго соблюдать порядок шагов и сообщения коммитов (`Порядок коммитов`).
- На S1 — проверить `git --version` перед `git init`.
- На S2 — grep Hygiene_Notes по `*.bat` и `*.py`; исключения перемещения фиксировать в отчёте итерации.
- На S3 — использовать `Remove-ExpiredReports -Pattern <glob> -TtlDays 30`; явно защитить `latest_bitnewton_report.*`, `state_cache.json`, `deal_filter.json` от TTL-удаления; обновить `.gitignore` идемпотентно.
- На S4 — заполнить `docs/_archive/FACADE_DECISION.md` по структуре из C4 с реальными именами методов после grep-сверки.
- На S5 — для каждого из `{bitrix, asr, ui}` выполнить полный grep по Facade_Package_Import_Patterns; для `bitrix` — дополнительно проверить `from bitrix import Bitrix24API`. Удалять `__init__.py` только при 0 совпадений. grep-отчёт зафиксировать в отчёте итерации независимо от решения. Если все три пакета сохраняются — пропустить коммит S5.
- На S6 — сверить `requires-python` с `check_python*.bat`; корректировать значение при расхождении. `ruff check --fix` и `black` НЕ запускать.
- На S7 — строго по под-коммитам S7.1..S7.5:
  - для каждого файла из соответствующего списка (C7, DM1) выполнить grep `print(`;
  - если 0 — пропустить файл;
  - если ≥1 — вставить `from logging_setup import get_logger` + `logger = get_logger(__name__)` после `from __future__`-блока или в начало файла после docstring;
  - заменить `print(...)` на `logger.<level>(...)` по эвристикам WARNING/ERROR/INFO/DEBUG (C7);
  - выполнить `python -m py_compile <file>` после правки.
- Stdout_Contract_Scripts определять в начале S7.1 по алгоритму (C7): grep `.bat` на имя `.py` + признаки потребления stdout (`for /f`, `>`, `|`). Кандидат: `dump_one_call.py`. Список фиксировать в отчёте итерации и исключать из замены.
- После каждого коммита — прогнать соответствующий блок плана проверки.
- Перед финалом — сверить SHA-256 с `reports\_hygiene_baseline_sha256.txt` для файлов Property 5.
- По завершении — создать запись в `docs/agent-log/` с маршрутом исполнения, grep-отчётом по пакетам и списком Stdout_Contract_Scripts.

## Что передать Cursor

- При необходимости точечных правок в файлах Scope_Python_Files использовать семантический поиск по `print(` и удерживать правку в рамках: импорт `logging_setup` + замена `print` на `logger.<level>`. Сигнатуры классов и функций не трогать.
- Не запускать автоформат Ruff/Black по всему проекту; только точечная ручная проверка `python -m py_compile`.
- Навигация:
  - `docs/_archive/FACADE_DECISION.md` — единое место фиксации решения по фасадам.
  - `logging_setup.py` — единственная точка конфигурации логирования.
  - `pyproject.toml` — настройки линтера и форматтера; правка только через согласованный diff.
- При обнаружении импорта вида `from bitrix import Bitrix24API` — НЕ удалять `bitrix/__init__.py`. Это особый кейс (C8).
- При обнаружении `.bat`, запускающего Python из подкаталога (без `cd /d %~dp0`), — зафиксировать в отчёте; правку Bat_Contract не выполнять в текущей итерации (Requirement 4.2).

## Открытые вопросы

На момент написания дизайна противоречий с `requirements.md` не выявлено. Точки, требующие уточнения в ходе исполнения:

1. **Точная версия Python в `check_python*.bat`.** Подтвердить на S6 (Риск R4). В дизайне зафиксирован диапазон `>=3.10` с оговоркой о корректировке при расхождении.
2. **Конкретный список Stdout_Contract_Scripts.** Определяется в S7 через grep `.bat` на вызов `<script>.py` + анализ, использует ли `.bat` stdout (`for /f`, `|`, `>`). Очень вероятный кандидат: `dump_one_call.py`. Итоговый список фиксируется в отчёте итерации.
3. **Решение по импорту `logging_setup` из подкаталогов.** Дизайн полагается на то, что `.bat` из Bat_Contract всегда делают `cd /d %~dp0` перед `python`. Если какой-то `.bat` нарушает это — соответствующий Python-скрипт помечается и выводится в отдельное решение будущей итерации (правка Bat_Contract в текущей итерации запрещена).
4. **Полный список дубликатов между `bitrix24_api.py` и `bitrix/*.py`.** Уточняется grep-сверкой на S4 и отражается в `FACADE_DECISION.md`; план устранения остаётся за следующими итерациями (Requirement 5.4).
5. **Количество Report_Outputs, попадающих под TTL 30 дней в момент S3.** Зависит от текущего состояния `reports/`. Фиксируется в отчёте итерации (сколько файлов удалено, сколько сохранено по Latest/Singleton).
