## Что было сделано

Реализованы артефакты 2-недельного landing/concierge test:
- экран `HH Resume Booster` в Aion Vision;
- навигация `HH Booster`;
- hash route `/#hh-booster`;
- локальная форма заявок;
- localStorage key `aion.hhResumeBooster.leads.v1`;
- экспорт JSON;
- сравнение paid intent по трем офферам;
- runbook эксперимента;
- CLI `tools/hh_resume_booster_metrics.py`.

## На чем основан вывод

Измененные файлы:
- `apps/aion-vision/src/components/dashboard/HhBoosterValidation.tsx`;
- `apps/aion-vision/src/App.tsx`;
- `apps/aion-vision/src/components/layout/DashboardLayout.tsx`;
- `apps/aion-vision/src/index.css`;
- `docs/experiments/hh-resume-booster-validation.md`;
- `tools/hh_resume_booster_metrics.py`.

## Что получилось хорошо

Экран не использует fake charts: счетчики строятся только из фактических localStorage-заявок. Форма не отправляет данные наружу.

## Что требует доработки

Для публичного запуска потребуется backend/storage, согласие на обработку данных, удаление данных и реальный канал сбора платежного intent.

## Какие есть риски

Пока это локальный concierge-прототип. Он доказывает механику теста, но не заменяет production landing.

## Что нельзя потерять/исказить дальше

Не считать экспортированные smoke-заявки реальными данными эксперимента.

## Решение

approve
