# 2026-06-21 20:14 - Codex - HH Booster offer-specific links

## Исходный запрос пользователя

Продолжить активную цель: подготовить landing/concierge test на 2 недели с тремя офферами `avatar-only`, `full resume audit`, `vacancy response pack`, чтобы сравнить paid intent и понять роль аватарки в продукте.

## Краткий план

1. Проверить текущие файлы HH Resume Booster после предыдущего незавершенного patch.
2. Доделать прямые ссылки на конкретные офферы и матрицу `offer + channel`.
3. Обновить runbook, текущий контекст и задачи.
4. Прогнать compile/build/smoke проверки без записи реальных лидов.

## Что было сделано

- Публичная форма `#hh-booster-public` уже читала `offer` из URL; проверено, что это сохранено в `HhBoosterLanding.tsx`.
- Операторская панель `#hh-booster` показывает матрицу прямых ссылок `offer + channel`; подпись блока приведена к русскому тексту `Прямые ссылки на офферы`.
- `tools/hh_resume_booster_launch_manifest.py` теперь экспортирует:
  - `urls.offer_links` - 3 прямые ссылки по офферам;
  - `urls.offer_channel_links` - 18 ссылок `3 оффера x 6 каналов`.
- `tools/hh_resume_booster_outreach_plan.py` теперь возвращает `offer_links` и `offer_channel_links` в JSON и показывает их в текстовом daily plan.
- `apps/aion-vision/scripts/start-hh-booster-test.ps1` печатает `Offer links` и `Offer + channel examples`.
- `docs/experiments/hh-resume-booster-validation.md` обновлен правилом `?offer=avatar|audit|response`.
- `docs/current-context.md` и `docs/tasks.md` обновлены, чтобы следующий агент видел offer-specific links как часть текущего состояния.

## Измененные файлы

- `apps/aion-vision/src/components/dashboard/HhBoosterLanding.tsx`
- `apps/aion-vision/src/components/dashboard/HhBoosterValidation.tsx`
- `apps/aion-vision/scripts/start-hh-booster-test.ps1`
- `tools/hh_resume_booster_launch_manifest.py`
- `tools/hh_resume_booster_outreach_plan.py`
- `docs/experiments/hh-resume-booster-validation.md`
- `docs/current-context.md`
- `docs/tasks.md`
- `docs/agent-log/2026-06-21-2014-codex-hh-booster-offer-specific-links.md`

## Проверки

- `python -m py_compile tools/hh_resume_booster_launch_manifest.py tools/hh_resume_booster_outreach_plan.py` - прошло.
- Manifest JSON smoke с `https://hh-booster.ngrok-free.app` - `offer_links=3`, `offer_channel_links=18`, есть `offer=response`.
- Outreach plan JSON smoke с `https://hh-booster.ngrok-free.app` - `offer_links=3`, `offer_channel_links=18`, есть `offer=avatar`.
- Windows PowerShell 5.1 `start-hh-booster-test.ps1 -PrintOnly` - выводит `Offer links`, `Offer + channel examples`, `offer=avatar`, `channel=Telegram&offer=response`.
- `npm run lint` в `apps/aion-vision` - прошло без warnings.
- `npm run build` в `apps/aion-vision` - прошло; остался штатный Vite warning о chunk size.

## Риски и ограничения

- Реальный 14-дневный сбор не стартовал и не завершен.
- `127.0.0.1` нельзя раздавать внешним кандидатам; нужен реальный `-PublicBaseUrl` и prelaunch GO/NO-GO.
- Ссылки помогают закрывать per-offer coverage, но не заменяют фактический outreach denominator и follow-up outcomes.

## Что должен проверить следующий агент

- Перед публичной раздачей запустить production-сервис видимо, нажать `Старт теста`, выполнить preflight/write-smoke, сохранить launch manifest и пройти prelaunch GO/NO-GO.
- Для каждого канала использовать ссылки с явным `offer`, чтобы не перекосить paid intent default-оффером.
- После начала сбора ежедневно запускать data quality audit, outreach plan, outreach log, follow-up queue/state и daily snapshot.
