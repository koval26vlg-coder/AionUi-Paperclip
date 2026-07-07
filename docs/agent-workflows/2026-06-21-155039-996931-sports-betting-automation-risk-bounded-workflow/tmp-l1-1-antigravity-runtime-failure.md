# L1.1 Antigravity runtime failure

## Что было сделано

После submitted L1.0 MiMo AUTO была предпринята попытка получить L1.1 review от Antigravity CLI в изолированном review-only режиме.

Проверенные маршруты:

- `tools/antigravity_workflow_review.py` с packet из `brief.md`, `contract.json`, последнего `handoff.md` и `events.jsonl`.
- raw `agy --print` из `C:\Users\koval\AppData\Local\Temp`.
- `tools/antigravity_print.py` с DB fallback.

## На чем основан вывод

- Isolated runner завершился с ошибкой validation: обязательные handoff headings отсутствовали, stdout содержал невалидный/мусорный вывод.
- raw `agy --print` завершился с code 0, но без stdout.
- DB fallback восстановил ответ из свежего DB, но ответ был про чужой старый workflow `2026-06-19-190057-983922-label-check`, а не про текущий `sports-betting-automation-risk-bounded-workflow`.
- В DB видно, что Antigravity начал читать/искать в `C:\Users\koval\AppData\Local\Temp`, несмотря на review-only prompt, поэтому этот результат нельзя считать валидным L1.1.

## Что получилось хорошо

- L1.0 MiMo AUTO успешно выполнен через `mimo run -m mimo/mimo-auto`.
- MiMo handoff сохранен и submitted в workflow.
- Невалидный Antigravity output не был принят как handoff.
- Workflow не был продвинут через подмену агента.

## Что требует доработки

- Нужен Antigravity runner с жесткой session correlation, чтобы DB fallback мог брать только ответ от текущего prompt/session.
- Нужно запретить или технически обнулить tool-use в Antigravity review-only режиме, потому что текущий runtime начал смотреть файлы в Temp.
- Нужен явный пользовательский approve fallback, если L1.1/L2 разрешено выполнять через Codex вместо Antigravity.

## Какие есть риски

- Если принять stale DB response как валидный handoff, workflow получит "испорченный телефон".
- Если молча заменить Antigravity на Codex, будет нарушена `docs/agent-workflows/model-policy.md`.
- Если продолжить без L1.1/L2, L3/L4 архитектура может не иметь независимой проверки safety/compliance.

## Что нельзя потерять/исказить дальше

- Real-money hidden auto-betting, обход правил БК, KYC, CAPTCHA, лимитов и anti-bot должны оставаться заблокированными.
- Разрешенная зона для продолжения: decision-support, paper-trading, alerting, backtest, probabilistic modeling, risk controls.
- L1.1 Antigravity не выполнен. Его нельзя указывать как completed.

## Решение

block
