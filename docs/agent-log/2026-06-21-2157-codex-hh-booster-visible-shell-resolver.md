# Отчет агента

## Дата и время

2026-06-21 21:57 +03

## Агент

Codex

## Исходный запрос пользователя

Активная цель: довести HH Resume Booster landing/concierge test до реального 14-дневного запуска и последующего сравнения paid intent по трем офферам.

## Контекст перед началом

Во время read-only проверки HH launch readiness текущий shell не смог найти `powershell.exe` через PATH. Это создавало риск, что `start-hh-booster-day0-rehearsal.ps1` не сможет открыть видимые server/tunnel окна, хотя сам Windows PowerShell 5.1 существует по стандартному пути.

## План

1. Найти все прямые вызовы `powershell.exe` в HH launch scripts.
2. Убрать зависимость от PATH в day-0 rehearsal launcher.
3. Проверить launcher в dry-run режиме без старта процессов и без записи данных.
4. Зафиксировать результат в общей памяти.

## Что сделано

- В `apps/aion-vision/scripts/start-hh-booster-day0-rehearsal.ps1` добавлен `Resolve-WindowsPowerShellExe`.
- Resolver сначала использует `Get-Command powershell.exe`, затем проверяет стандартные пути:
  - `C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe`
  - `C:\Windows\Sysnative\WindowsPowerShell\v1.0\powershell.exe`
- `Start-VisiblePowerShell` теперь стартует видимое окно через найденный полный путь.
- `-PrintOnly` теперь печатает `Visible shell`, чтобы dry-run ловил этот класс проблем заранее.

## Измененные файлы

- `apps/aion-vision/scripts/start-hh-booster-day0-rehearsal.ps1`
- `docs/tasks.md`
- `docs/current-context.md`
- `docs/agent-log/2026-06-21-2157-codex-hh-booster-visible-shell-resolver.md`

## Проверки

- `C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe -NoProfile -ExecutionPolicy Bypass -File apps/aion-vision/scripts/start-hh-booster-day0-rehearsal.ps1 -PrintOnly -SkipBuild`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File apps/aion-vision/scripts/start-hh-booster-day0-rehearsal.ps1 -PrintOnly -SkipBuild`
- `tools/hh_resume_booster_experiment_state.py ... status --json`

Оба dry-run запуска показали:

- `Visible shell: C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe`
- `Start timer: no`
- `Write manifest: no`
- `PrintOnly: no server/tunnel/process started`

Experiment state после проверок: `startedAt=null`, leads `0`.

## Решения

- HH day-0 rehearsal launcher не должен зависеть от PATH для `powershell.exe`.
- Настоящий 14-дневный старт остается только через явный guarded launch или действие пользователя в операторской панели.

## Риски и ограничения

- Реальный public URL сейчас отсутствует.
- Локальный server на `127.0.0.1:8787` сейчас не слушает.
- Prelaunch закономерно `NO-GO` до visible runtime, public URL, `Старт теста` и launch manifest.
- Цель не завершена до фактических 14 дней сбора и paid-intent данных.

## Что должен проверить следующий агент

- Перед реальным запуском выполнить day-0 rehearsal через видимый launcher.
- Если используется temporary tunnel, перепроверить public API/prelaunch непосредственно перед рассылкой.
- Не считать dry-run или rehearsal стартом эксперимента.
