# Отчет агента

## Дата и время

2026-06-21 21:52 +03

## Агент

Codex

## Исходный запрос пользователя

Активная цель: сделать landing/concierge test на 2 недели с тремя офферами `avatar-only`, `full resume audit`, `vacancy response pack`, сравнить paid intent и понять, оставлять ли аватарку лид-магнитом или модулем большого продукта.

## Контекст перед началом

Предыдущие temporary localtunnel URL для HH Resume Booster быстро перестали отвечать. Последняя проверка показала, что `https://tangy-peaches-like.loca.lt` уже возвращает `503`, локальный порт `8787` свободен, `startedAt=null`, server leads JSONL пустой. Нужен безопасный предзапусковой шаг, который можно повторять без случайного старта 14-дневного таймера.

## План

1. Проверить текущий day-0 rehearsal launcher.
2. Убедиться, что `-PrintOnly` не стартует процессы и не меняет experiment state.
3. Задокументировать launcher в runbook и общей памяти.
4. Оставить реальный launch заблокированным до явного решения пользователя.

## Что сделано

- Проверен `apps/aion-vision/scripts/start-hh-booster-day0-rehearsal.ps1`.
- Добавлен раздел про one-command day-0 rehearsal в `docs/experiments/hh-resume-booster-validation.md`.
- Обновлены `docs/tasks.md` и `docs/current-context.md`.
- Зафиксировано, что rehearsal launcher не заменяет guarded launch и не должен считаться стартом эксперимента.

## Измененные файлы

- `apps/aion-vision/scripts/start-hh-booster-day0-rehearsal.ps1`
- `docs/experiments/hh-resume-booster-validation.md`
- `docs/tasks.md`
- `docs/current-context.md`
- `docs/agent-log/2026-06-21-2152-codex-hh-booster-day0-rehearsal-launcher.md`

## Проверки

- `powershell.exe -NoProfile -ExecutionPolicy Bypass -File apps/aion-vision/scripts/start-hh-booster-day0-rehearsal.ps1 -PrintOnly -SkipBuild`
- `powershell.exe -NoProfile -ExecutionPolicy Bypass -File apps/aion-vision/scripts/start-hh-booster-day0-rehearsal.ps1 -PublicBaseUrl "https://stable.example.com" -PrintOnly -SkipBuild`
- `.venv-sml/Scripts/python.exe -m py_compile tools/hh_resume_booster_launch_manifest.py tools/hh_resume_booster_prelaunch_check.py tools/hh_resume_booster_publish_kit.py`

## Решения

- Перед настоящей публикацией candidate links использовать day-0 rehearsal как безопасную проверку видимого server/tunnel/runtime.
- `startedAt` писать только через явный guarded launch или явное действие пользователя в операторской панели.
- Temporary tunnel warning сохраняется: для `*.loca.lt`, `*.ngrok-free.app`, `*.trycloudflare.com`, `*.localhost.run` public API/prelaunch нужно перепроверять прямо перед рассылкой.

## Риски и ограничения

- Реальный 14-дневный тест не начат: `startedAt=null`.
- Реальных лидов нет: `hh-booster-leads.jsonl` пустой.
- Живого public URL сейчас нет; старые localtunnel URL не использовать.
- Цель не завершена до фактического 14-дневного сбора и paid-intent сравнения.

## Что должен проверить следующий агент

- Перед стартом выполнить новый visible runtime через day-0 rehearsal или стабильный public domain.
- Проверить public API и prelaunch непосредственно перед публикацией candidate links.
- После явного решения пользователя выполнить guarded launch: `prepare-hh-booster-public-launch.ps1 -PublicBaseUrl ... -OperatorBaseUrl "http://127.0.0.1:8787" -CheckPublicHttp -StartExperiment`.
- Не отмечать цель завершенной без 14 дней, 30+ лидов, 10+ strong paid intent, 2+ каналов, 5+ ролей, минимум 5 лидов по каждому офферу и чистого data-quality gate.
