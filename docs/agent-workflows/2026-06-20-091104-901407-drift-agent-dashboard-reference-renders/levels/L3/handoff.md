## Что было сделано

Codex на уровне L3 выполнил декомпозицию реализации, тестов и automation для drift-agent dashboard. Также подготовлены и сохранены reference renders в workspace, чтобы они были доступны следующим уровням workflow, а не только как временные превью генерации.

Сгенерированы 6 визуальных направлений:

1. `renders/relay-race-track.png` — линейная эстафета уровней L1.0 -> L5.
2. `renders/circuit-ring.png` — кольцевая трасса с секторами и pit/queue.
3. `renders/city-drift.png` — городские кварталы как отделы workflow.
4. `renders/vertical-tower.png` — многоуровневая башня/паркинг как иерархия.
5. `renders/mountain-pass.png` — серпантин снизу вверх как рост ответственности.
6. `renders/drift-arena.png` — арена/gymkhana с центральным активным агентом.

Рекомендация L3: первым прототипом брать `Relay Race Track`. Он лучше всего совпадает с реальным contract-state workflow: текущий уровень, следующий разрешенный агент, ожидание, handoff и audit panel считываются без сложной камеры и без перегруза.

## На чем основан вывод

Вывод основан на:

- `brief.md` workflow;
- L1.0 MiMo AUTO handoff с 6 базовыми моделями;
- L1.1 Antigravity handoff с фильтрацией шума и стилизацией машин;
- L2 Antigravity engineering review с выбором 2D SVG/CSS вместо WebGL для MVP;
- фактической визуальной проверке 6 сгенерированных PNG.

L3 не менял исходный смысл задачи: это должен быть продуктовый dashboard мониторинга workflow, а не игра или декоративная гоночная сцена.

## Что получилось хорошо

### codex-implementation-decomposer

Предлагаемая структура MVP:

- `WorkflowStateSource` — читает `contract.json`, `events.jsonl`, последний `handoff.md`, future `final-report.md`.
- `StateMapper` — переводит workflow state в визуальные состояния `active`, `next`, `waiting`, `blocked`, `revision`, `done`.
- `AgentCarRegistry` — хранит стиль машин и субагентов: MiMo, Antigravity, Codex, Claude.
- `TrackLayoutAdapter` — отдельные layout-адаптеры: `relay`, `ring`, `city`, `tower`, `mountain`, `arena`.
- `DriftMotionEngine` — расчет позиции, угла заноса, дыма, следов шин и follow-trail субагентов.
- `AuditPanel` — панель справа/снизу с событиями, handoff, blockers, allowed next agents и лимитами.
- `LimitPanel` — виджет лимитов и observed token/cost deltas из `tools/agent_limit_monitor.py`.
- `ReferenceGallery` — переключение между 6 концептами без изменения workflow state.

### codex-test-planner

Минимальный набор проверок:

- unit: `StateMapper` строго берет `current_level`, `allowed_next_agents`, `blockers` и последний event, а не домысливает состояние;
- unit: L1.0/L1.1/L2/L3/L4/L5 мапятся в правильные машины и роли;
- unit: `allowed_next_agents` подсвечивает только следующего агента;
- unit: `blocked` и `revision` перекрывают обычные `active/next` состояния;
- unit: skidmarks/particles ограничены лимитами, например не больше 100 сегментов на машину;
- smoke: dashboard открывается с реальным workflow directory и показывает текущий L3/L4/L5 без ручного JSON;
- Playwright visual: desktop/mobile viewports, нет наложения текста и панелей, clean/performance режим отключает дым и тяжелые эффекты.

### codex-automation-builder

Automation для следующего шага:

- добавить CLI/скрипт `tools/render-agent-dashboard-state.py` или frontend route, который принимает `--workflow-id`;
- добавить watcher/monitor, который читает workflow dir и обновляет dashboard после изменения `contract.json` или `events.jsonl`;
- интегрировать `tools/agent_limit_monitor.py --json`, чтобы dashboard показывал observed usage deltas по Codex, Claude, MiMo, Antigravity;
- добавить snapshot/demo fixture с этим workflow, чтобы не гонять реальных агентов для UI-тестов.

### codex-integration-checker

Интеграционно safest path:

- не менять `agent_workflow.py` ради визуализации;
- dashboard должен быть read-only consumer workflow files;
- любые actions `approve/submit/finalize` остаются только через CLI workflow;
- Antigravity остается review-only runtime и не получает write-path через dashboard;
- для MVP использовать 2D SVG/CSS + `requestAnimationFrame`, без WebGL/3D.

## Что требует доработки

- Выбрать место реализации: отдельный `tools/` preview, страница в существующем UI или standalone dashboard app.
- Для production UI перерисовать машинки как контролируемые SVG/Canvas assets; текущие PNG — reference renders, не финальные элементы интерфейса.
- Сформировать точный schema contract для dashboard input: какие поля нужны из `contract.json`, `events.jsonl`, handoff и лимит-монитора.
- Уточнить, надо ли dashboard только наблюдать workflow или также давать кнопки действия. L3 рекомендует MVP read-only, чтобы не открыть новый путь самовольного изменения state.

## Какие есть риски

- Reference renders местами содержат AI-псевдотекст. Это допустимо для визуального направления, но нельзя брать эти PNG как финальный UI.
- City/Mountain/Arena красивее, но слабее как рабочий MVP: больше визуального шума, хуже масштабирование, выше стоимость отрисовки.
- Circuit Ring может искажать смысл workflow, потому что кольцо визуально намекает на бесконечный цикл вместо линейной передачи L1.0 -> L5.
- Если добавить action buttons в dashboard до read-only прототипа, можно повторить риск DEF-01: агент или UI начнет менять state не через контролируемый executor.
- Лимиты разных CLI сейчас доступны неравномерно: Codex/Claude/MiMo дают observed usage, Antigravity пока без надежных numeric tokens.

## Что нельзя потерять/исказить дальше

- Dashboard обязан отображать реальное состояние из `contract.json` и `events.jsonl`, а не красивую независимую анимацию.
- Активный агент, следующий разрешенный агент и blocked/revision должны быть важнее дыма, дрифта и декоративной сцены.
- Субагенты должны быть видны как escort/micro-cars/drones вокруг главной машины уровня, но не конкурировать с главным state.
- Рекомендуемый MVP — read-only Relay Race Track + audit panel + limit panel.
- Остальные 5 направлений являются reference gallery, а не равноправными кандидатами для первой реализации.

## Решение

approve
