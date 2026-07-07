# L1 handoff: Antigravity runtime failure

## Что было сделано

- Workflow создан и принят в работу на уровне L1 от имени `Antigravity CLI` через `Codex` как trusted executor.
- Выполнены две попытки получить L1 review-only handoff:
  - raw `antigravity_print.py --sandbox` вернул нечитаемый payload; wrapper сообщил recovery из conversation DB, но пригодного Markdown handoff не было.
  - `antigravity_workflow_review.py` в изолированном пакете завершился ошибкой `agy --print returned empty stdout and no DB response was recovered`.
- Проверка runtime: `agy --version` вернул `1.0.12`; `agy models` не вывел доступные модели.

## На чем основан вывод

- `contract.json` workflow: `current_level=L1`, `allowed_next_agents=["Antigravity CLI"]`, risk flags `trading=true`, `long_running=true`.
- `events.jsonl`: workflow создан и L1 claimed.
- Локальные команды Antigravity runtime выше не дали валидного review output.
- Model policy workflow запрещает молча подменять `Antigravity CLI AUTO` другим агентом или моделью.

## Что получилось хорошо

- Workflow создан штатно с правильными risk flags.
- Исходный brief сохранен без расширения и без реальных торговых действий.
- Запреты на ставки, задатки, внешние записи, secrets и длительные collectors сохранены в brief.
- Active-run gate по `trading_mvp` учтен: текущий статус `RUNNING`, поэтому collectors/postprocess/grid-search не запускались.

## Что требует доработки

- Нужен валидный L1 handoff от `Antigravity CLI` или явное разрешение пользователя на fallback через другого агента.
- Нужно восстановить вывод `agy --print` или утвердить временную замену L1/L2 на Codex/Claude review.
- После валидного L1 нужно продолжить стандартную цепочку: L2 Antigravity CLI -> L3 Codex -> L4 Codex -> L5 Claude Code.

## Какие есть риски

- Если пропустить L1/L2 без фиксации, workflow потеряет смысл независимой проверки.
- Если Codex сам заполнит L1 вместо Antigravity без разрешения, это нарушит model policy и создаст ложную уверенность.
- Тема связана с торгами и потенциальными деньгами, поэтому risk gate обязателен.
- Длительные сборщики лотов нельзя запускать скрыто; при будущем запуске нужен видимый терминал или monitor-script.

## Что нельзя потерять/исказить дальше

- MVP остается paper-trading: никаких реальных ставок, задатков, заявок и юридически значимых действий.
- Первый фокус: авто/спецтехника, ROI/risk scoring, таблица + ежедневный отчет.
- ROI должен учитывать all-in cost, срок оборота денег, risk-adjusted discount и stop factors.
- Источники v1 должны быть адаптерами, без жесткой зависимости от одного API.
- Active-run gate `RUNNING` по `trading_mvp` запрещает новые длительные collectors/postprocess/grid-search по активной цели.

## Решение

escalate
