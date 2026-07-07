# HH Resume Booster landing/concierge test

Оператор: Codex. Внешний runtime Claude Code не вызывался; финализация выполняется через delegated executor с явной фиксацией ограничения.

## Итог

Практический шаг выполнен: в Aion Vision добавлен рабочий экран для 2-недельного validation test по трем офферам:

- `avatar-only` / Аватарка;
- `full resume audit` / Аудит резюме;
- `vacancy response pack` / Отклик под вакансию.

Экран доступен локально:

```text
http://127.0.0.1:5174/#hh-booster
```

## Что реализовано

- Три offer cards с ценами 199/399/799 RUB.
- Concierge form для фиксации контакта, профессии, канала, оффера и готовности платить.
- Strong paid intent считается только как `Готов оплатить`.
- Данные хранятся локально в браузере: `aion.hhResumeBooster.leads.v1`.
- Есть export JSON.
- Есть comparison panel по офферам.
- Есть runbook 14-дневного теста: `docs/experiments/hh-resume-booster-validation.md`.
- Есть CLI подсчета: `tools/hh_resume_booster_metrics.py`.

## Проверки

- `npm run lint` - passed.
- `npm run build` - passed.
- CLI metrics smoke-test на временном JSON - passed.
- Playwright fallback через Edge - passed: страница открылась, форма сохранила lead, localStorage содержит запись, console errors 0.

## Решение

approve

Следующий шаг - провести реальный 14-дневный сбор заявок и после экспорта JSON сравнить paid intent по трем офферам.
