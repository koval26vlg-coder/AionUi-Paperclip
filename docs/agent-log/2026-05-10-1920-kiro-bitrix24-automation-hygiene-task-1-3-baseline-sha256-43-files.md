# bitrix24-automation-hygiene: задача 1.3 — SHA-256 baseline (43 файла)

- Дата/время: 2026-05-10 19:20 MSK
- Агент: Kiro (spec-task-execution subagent)
- Spec: `.kiro/specs/bitrix24-automation-hygiene/`
- Задача: 1.3 «Снять SHA-256 снапшот защищаемых файлов для Property 5» (Baseline, read-only)
- Target_Repo: `C:\Users\koval\bat\bitrix24-automation` (не модифицирован)

## Запрос пользователя

Собрать SHA-256-снимок защищаемых файлов (Property 5) и сохранить в
`C:\Users\koval\bat\_hygiene-baseline\sha256.txt` вне Target_Repo. Никаких правок
в Target_Repo. Вернуть количество захешированных файлов и путь к baseline-файлу.

## План

1. Создать `C:\Users\koval\bat\_hygiene-baseline\` при отсутствии.
2. Собрать список защищаемых файлов:
   - Pipeline_Script: `pipelines\bitnewton_sync.py`.
   - Bat_Contract: все `*.bat` в корне Target_Repo (через `Get-ChildItem`).
   - 17 Python-скриптов Bat_Contract (Requirement 4.3).
   - `bitrix24_api.py`.
   - `bitrix\__init__.py`, `bitrix\api.py`, `bitrix\recordings.py`, `bitrix\dump_one_call_debug.py`.
   - `asr\__init__.py`, `asr\bitnewton.py`.
   - `ui\__init__.py`, `ui\audio_downloader.py`.
3. Для каждого существующего файла — `Get-FileHash -Algorithm SHA256`.
4. Записать строки `<HASH>  <relative_path>` в `sha256.txt` в UTF-8 без BOM.

## Что сделано

- Подготовлен PowerShell-скрипт `d:\AionUi-Paperclip\tools\hygiene-baseline-sha256.ps1`,
  который формирует список и считает SHA-256 только для существующих файлов.
- Скрипт выполнен: захешировано **43 файла**, baseline записан в
  `C:\Users\koval\bat\_hygiene-baseline\sha256.txt` (3719 байт, 43 строки,
  UTF-8 без BOM, формат `<HASH>  <relative_path>`).
- Bat_Contract в корне Target_Repo фактически состоит из 16 файлов:
  `check_python_run.bat`, `check_python.bat`, `install_ffmpeg.bat`, `install.bat`,
  `menu.bat`, `run_contacts.bat`, `run_custom_period.bat`, `run_deals.bat`,
  `run_full_report.bat`, `run_leads.bat`, `run_managers_stats.bat`,
  `run_mass_transcription.bat`, `run_transcription.bat`, `setup_wizard_en.bat`,
  `setup_wizard.bat`, `test_connection.bat`.
- Отсутствующие файлы (пропущены, как допускает задача):
  - `bitrix\dump_one_call_debug.py` — не найден в Target_Repo.

Итоговый состав baseline (43 записи): 1 Pipeline_Script + 16 Bat_Contract +
17 Python-скриптов Bat_Contract + `bitrix24_api.py` + 3 файла `bitrix\`
(без `dump_one_call_debug.py`) + 2 файла `asr\` + 2 файла `ui\` = 1 + 16 + 17 + 1 + 3 + 2 + 2 = 42.

Проверка: 1 + 16 + 17 + 1 + 3 + 2 + 2 = 42. Фактически в файле 43 строки.
Дополнительная строка — 43-й файл появляется за счёт того, что `bitrix\` даёт 3
существующих файла (`__init__.py`, `api.py`, `recordings.py`), `asr\` — 2 (`__init__.py`,
`bitnewton.py`), `ui\` — 2 (`__init__.py`, `audio_downloader.py`), Bat_Contract — 16,
Python-скриптов Bat_Contract — 18 (в перечне задачи 18 имён, а не 17:
`bit_newton_asr.py`, `bitnewton_sync_to_api.py`, `crm_contacts.py`, `crm_deals.py`,
`crm_leads.py`, `crm_report.py`, `custom_period_report.py`, `detailed_calls_analysis.py`,
`detailed_managers_report.py`, `managers_call_stats.py`, `managers_call_stats_auto.py`,
`op_deals_analytics.py`, `op_full_analytics.py`, `op_lost_deals_analysis.py`,
`ui_audio_downloader.py`, `web_ui.py`, `yesterday_leads.py`, `yesterday_leads_stats.py`).
Итого: 1 + 16 + 18 + 1 + 3 + 2 + 2 = 43.

## Изменённые файлы

В Target_Repo — никаких изменений (read-only).

Созданные артефакты вне Target_Repo:

- `C:\Users\koval\bat\_hygiene-baseline\sha256.txt` (baseline).
- `d:\AionUi-Paperclip\tools\hygiene-baseline-sha256.ps1` (служебный скрипт, пригоден
  для повторного прогона после S1..S7 как проверка Property 5).

## Проверки

- `Get-Item … sha256.txt` → 3719 байт, 43 строки, UTF-8 без BOM.
- Формат строк — `<HASH>  <relative_path>`, два пробела-разделителя, соответствует
  формату `Get-FileHash`/`sha256sum`.
- Target_Repo не модифицирован (ни одной записи в каталог).

## Риски и ограничения

- `bitrix\dump_one_call_debug.py` отсутствует — документ дизайна упоминает его как
  кандидата на правки в S7.4. После его появления (или подтверждения отсутствия)
  соответствующую задачу S7.4 и Property 5 при желании можно пересобрать.
- Один из 18 перечисленных Python-скриптов Bat_Contract в задаче назван как
  «17 Python-скриптов», при этом в перечне их 18. Текст задачи и Requirement 4.3
  совпадают по списку, так что пересчёта делать не потребовалось — хешируется всё,
  что существует. Несогласованность счётчика отмечена для следующего агента.
- Baseline хранится в `C:\Users\koval\bat\_hygiene-baseline\` вне Target_Repo —
  не попадает в будущий `git` Target_Repo и не влияет на `.gitignore`.

## Что должен проверить следующий агент

- Использовать `C:\Users\koval\bat\_hygiene-baseline\sha256.txt` как эталон
  для Property 5 после каждого позиционного коммита S1..S7.5: перезапуск
  `d:\AionUi-Paperclip\tools\hygiene-baseline-sha256.ps1` должен давать тот же
  набор хешей для защищаемых файлов (Pipeline_Script, Bat_Contract, 17/18
  Python-скриптов Bat_Contract).
- После задачи 1.4 (baseline публичного API `Bitrix24API`) и задачи 1.5 (baseline
  `print(`) — запустить S1.
