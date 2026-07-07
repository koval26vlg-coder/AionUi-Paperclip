# Final Report: Drift Workflow Control

## Решение

approve

Прототип можно считать рабочим для текущего этапа: `Drift Workflow Control` показывает иерархический workflow как drift-arena, не мутирует состояние из UI и сохраняет цепочку `brief -> handoff -> events -> final-report`.

## Проверено

- L1.0/L1.1/L2/L3/L4 прошли через `tools/agent_workflow.py`, а не через ручное продвижение `contract.json`.
- После замечания пользователя car policy исправлена: `L1.0` = tuned kei scout, `L1.1` = Toyota AE86 Trueno, `L2` = Nissan 180SX Type X, `L3` = Toyota Chaser JZX100, `L4` = Nissan Silvia S15, `L5` = Toyota Supra A80.
- Dashboard оставлен read-only: управление workflow остается в CLI, визуализация только отображает состояние.
- Убраны декоративные fake charts; оставлены arena, компактные markers, реальные workflow-метрики, handoff/audit и limits/usage panel с честным `unknown`, где нет источника данных.
- Проверки пройдены: `npm run lint`, `npm run build`, `python -m pytest tools/sml/tests/test_agent_workflow.py` = 10 passed.

## Что нельзя исказить

- Это не схема "один запрос в несколько моделей". Это последовательная иерархия отделов, где каждый уровень принимает handoff предыдущего уровня и фиксирует свое решение.
- `Drift Workflow Control` не переводить.
- Имена агентов, моделей и car policy не переименовывать без нового решения пользователя.
- Не возвращать большие overlay-плашки поверх машин и не добавлять бессмысленные графики без чисел и источников.
- Не утверждать, что fixture является live adapter: текущие данные dashboard еще статические.

## Остаточные риски

- `DRIFT_WORKFLOW_SNAPSHOT` пока fixture, поэтому следующий технический этап должен подключить read-only adapter к `contract.json`, `events.jsonl`, handoff и usage snapshots.
- PNG arena asset является прототипной технической заменой, а не полноценным фотореалистичным inpaint. Для production лучше сгенерировать новый цельный render или вынести роли в аккуратный canvas/WebGL слой.
- Claude Code runtime не прошел стабильный L5 smoke-test в этой итерации: одна попытка была остановлена бюджетом `$0.30`, короткая попытка `haiku` завершилась timeout за 124 секунды. Поэтому L5 фиксируется как `Claude Code` по контракту, но с `executor=Codex` и runtime/cost constraint в отчете.
- Vite build проходит, но оставляет warning о крупном chunk. Для прототипа это не блокер.

## Следующий шаг

Следующий полезный шаг: заменить fixture на live read-only adapter, чтобы dashboard показывал текущий workflow напрямую из файлов `docs/agent-workflows/<workflow>/contract.json`, `events.jsonl`, последнего `handoff.md` и `docs/agent-limits/limits-config.json`.
