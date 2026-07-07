# Финальный отчёт — Drift-agent dashboard: reference renders

**Workflow:** `2026-06-20-091104-901407-drift-agent-dashboard-reference-renders`
**Статус прогона:** `ready_for_final` · L1.0 → L1.1 → L2 → L3 → L4 пройдены и одобрены · L5 (этот отчёт)
**Уровень-инстанция:** L5 Claude Code — финальная техпроверка и заключение для пользователя

---

## 1. Executive summary

Вы просили визуализировать работу продукта как dashboard с дрифт-машинками: каждый агент — отдельная стилизованная машина, на одном экране видно, **кто сейчас работает, кто следующий, кто ждёт**, какая у каждого роль и как результат передаётся (handoff) по цепочке уровней. Задачу нужно было прогнать через сам hierarchical agent workflow как тестовый прогон.

Это сделано. Тестовый прогон прошёл по всей цепочке `L1.0 MiMo AUTO → L1.1 Antigravity → L2 Antigravity → L3 Codex → L4 Codex → L5 Claude Code`, каждый уровень вынес решение **approve**. Получены **6 reference renders** (концепт-направления dashboard), под них проработаны: стилизация машинок по агентам, матрица из 6 состояний (`active / next / waiting / blocked / revision / done`), архитектура чтения данных и план тестов.

Важно по сути: на этом этапе создан **набор референс-рендеров плюс архитектурный и тестовый план**, а не готовый интерактивный продукт. UI как работающее приложение ещё не реализован — это следующий шаг, если вы его подтвердите.

Рекомендация всех инженерных уровней единодушна: первым прототипом брать **Relay Race Track** (линейная эстафета) в режиме read-only.

---

## 2. Шесть созданных reference renders

Файлы лежат в `…/renders/`:

| # | Файл | Концепция | Назначение |
|---|------|-----------|------------|
| 1 | `relay-race-track.png` | **Relay Race Track** — линейная эстафета L1.0 → L5 с зонами передачи | Прямое попадание в природу workflow: текущий уровень, следующий разрешённый агент, ожидание и handoff читаются без сложной камеры. **Кандидат №1 на MVP.** |
| 2 | `circuit-ring.png` | **Circuit Ring** — кольцевая трасса, 6 секторов, pit/queue в центре | Самая выразительная drift-метафора и наглядная очередь уровней. Минус: кольцо намекает на бесконечный цикл, а не на линейную передачу. |
| 3 | `city-drift.png` | **City Drift** — городские кварталы как отделы/уровни, перекрёстки как handoff | Лучше всех стилизует разные роли и «отделы», но дороже по арту и легко превращается в красивый фон, где состояние хуже считывается. |
| 4 | `vertical-tower.png` | **Vertical Tower** — башня-паркинг, этаж = уровень, рампы = handoff | Сильнее всех показывает иерархию и «подъём» результата наверх. Минус: сложнее для responsive desktop/mobile. |
| 5 | `mountain-pass.png` | **Mountain Pass** — серпантин снизу вверх как рост ответственности L1.0 → L5 | Хорошая метафора роста ответственности. Минус: узкие полосы, склонность стать декоративной сценой. |
| 6 | `drift-arena.png` | **Drift Arena** — арена/gymkhana с активным агентом в центре | Максимальный фокус на текущем активном агенте. Минус: хаотичные траектории, высокая нагрузка отрисовки, слабее как рабочий dashboard. |

Под все варианты закреплён единый язык машинок по агентам: **MiMo AUTO** — Toyota AE86, **Antigravity CLI** — маслкар Mustang, **Codex** — Nissan GT-R, **Claude Code** — гиперкар Rimac. Субагенты рендерятся как micro-cars/дроны эскорта («drift train») вокруг машины своего уровня и не конкурируют с главным состоянием.

---

## 3. Рекомендация: что брать первым

**Брать Relay Race Track как первый интерактивный прототип, в режиме read-only.**

Почему именно он:

- Линейная эстафета 1:1 ложится на реальный contract-state: `current_level`, `allowed_next_agents`, `blockers`, последний event и handoff видны сразу, без сложной камеры и зума.
- Самый дешёвый и масштабируемый рендер: чистый 2D SVG/CSS + `requestAnimationFrame`, без WebGL/3D — стабильные 60 FPS даже на слабых устройствах, простая интеграция.
- Раскладка экрана **60% трек / 40% панель аудита** (события, handoff, blockers, allowed next agents, лимиты), с двусторонней подсветкой «машина ↔ запись лога».
- Остальные 5 направлений остаются как **reference gallery** (переключаемые концепты), а не равноправные кандидаты на первую реализацию.

Архитектурный каркас под прототип уже описан: `WorkflowStateAdapter → NormalizedWorkflowSnapshot → TrackRenderer / AuditPanel / LimitPanel`. Ключевое правило заложено: **UI никогда не выдумывает состояние** — при неполных данных показывает `unknown/pending`, а не красивую вымышленную анимацию.

---

## 4. Риски и ограничения

- **AI-псевдотекст в рендерах.** Часть PNG местами содержит сгенерированный псевдотекст. Это допустимо как визуальное направление, но эти файлы **нельзя брать как финальные UI-ассеты** — для продакшна машинки и трек нужно перерисовать как детерминированные SVG/Canvas-ассеты.
- **Это read-only MVP, а не продукт.** Рекомендованный прототип только **наблюдает** workflow. Управляющие действия (`submit/approve/finalize`) обязаны остаться в `tools/agent_workflow.py`. Если дать dashboard возможность менять state, нужно повторно провести DEF-01-style аудит, иначе появится неконтролируемый путь изменения состояния.
- **Лимиты доступны неполно.** Локально честно показывается только **observed usage** (наблюдаемый расход) — и то неравномерно: Codex/Claude/MiMo дают цифры, у Antigravity надёжных numeric tokens пока нет. Официальные **remaining/reset** подписок локально недоступны. В отчёте и в UI нельзя заявлять, что остатки лимитов полностью известны.
- **Эстетика против читаемости.** Дым, неон и постоянный занос могут перегрузить экран и просадить производительность; при росте числа субагентов кольцо и арена переполняются. Нужны лимиты на эффекты (например, ≤100 сегментов следа на машину) и обязательный режим **Clean / Performance** с отключением дыма и тяжёлых анимаций.
- **Искажение смысла отдельными layout-ами.** `Circuit Ring` и `Drift Arena` эффектны, но искажают линейную природу workflow; `City Drift`, `Mountain Pass`, `Vertical Tower` легко уходят в декоративный фон. Поэтому MVP — именно линейный трек.

---

## 5. Заключение

### Решение: **APPROVE**

Прогон по workflow завершён корректно, brief выполнен без искажений: представлено 6 визуальных концепций (требовалось ≥5), по каждой ясно «кто работает / следующий / ждёт / роль / handoff», зафиксированы риски и дана однозначная рекомендация. Контракт не нарушен, risk-flags все `false`, нерешённых `revise`/`block` нет.

**Что это значит на практике:** этап reference renders + architecture/test plan закрыт и принят. Готовый интерактивный dashboard ещё не построен — это сознательно следующий шаг.

**Следующий шаг (на ваше подтверждение):** дать старт реализации интерактивного прототипа **read-only Relay Race Track** (2D SVG/CSS, экран 60/40, чтение только из workflow-файлов), с заменой AI-PNG на детерминированные SVG/Canvas-ассеты и режимом Clean/Performance. Остальные 5 направлений — как переключаемая reference gallery.

Скажите, переходим ли от рендеров к коду прототипа — и я зафиксирую это как отдельный этап реализации.

## История прохождения уровней

- L1 Нижний авто-уровень и исследовательский отдел: status=approved, agent=Antigravity CLI, handoff=levels/L1/L1.1/handoff.md
  - L1.0 AUTO-первичная разведка: status=approved, agent=MiMo AUTO, mode=AUTO, handoff=levels/L1/L1.0/handoff.md
    - subagent mimo-intake-scanner: Сканер постановки - Вытащить исходную цель, ограничения, входные данные и явные критерии успеха. [MiMo AUTO / AUTO / Xiaomi API AUTO]
    - subagent mimo-hypothesis-generator: Генератор первичных гипотез - Дать быстрые варианты решения, не выдавая их за проверенные выводы. [MiMo AUTO / AUTO / Xiaomi API AUTO]
    - subagent mimo-risk-sentinel: Сигнальщик очевидных рисков - Отметить пробелы, противоречия, опасные допущения и что нельзя потерять дальше. [MiMo AUTO / AUTO / Xiaomi API AUTO]
  - L1.1 Исследовательский lead: status=approved, agent=Antigravity CLI, mode=reviewed, handoff=levels/L1/L1.1/handoff.md
    - subagent antigravity-source-verifier: Проверяющий фактов - Сверить тезисы MiMo с brief, handoff, событиями и доступными источниками. [Antigravity CLI AUTO / High]
    - subagent antigravity-context-expander: Расширитель контекста - Добавить недостающие альтернативы, ограничения, зависимости и edge cases. [Antigravity CLI AUTO / Low]
    - subagent antigravity-noise-filter: Фильтр шума - Убрать неподтвержденные или лишние идеи, чтобы L1 не передал искажение выше. [Antigravity CLI AUTO / Low]
    - subagent antigravity-handoff-editor: Редактор L1-handoff - Собрать проверенный handoff с явным решением approve/revise/escalate/block. [Antigravity CLI AUTO / Medium]
- L2 Инженерная проверка: status=approved, agent=Antigravity CLI, handoff=levels/L2/handoff.md
  - subagent antigravity-engineering-reviewer: Инженерный ревьюер - Проверить применимость L1-выводов к реальной реализации. [Antigravity CLI AUTO / High]
  - subagent antigravity-constraint-checker: Проверяющий ограничений - Сверить решение с brief, контрактом, risk flags, allowed_next_agents и контекстными лимитами. [Antigravity CLI AUTO / High]
  - subagent antigravity-edge-case-scout: Разведчик крайних случаев - Найти скрытые сценарии, неполные данные, конфликтующие требования и слабые места. [Antigravity CLI AUTO / High]
  - subagent antigravity-revision-gate: Gate ревизии - Решить, можно ли передавать работу на Codex L3 или нужно вернуть на доработку. [Antigravity CLI AUTO / High]
- L3 Декомпозиция реализации, тесты и automation: status=approved, agent=Codex, handoff=levels/L3/handoff.md
  - subagent codex-implementation-decomposer: Декомпозитор реализации - Разбить задачу на исполнимые шаги, файлы, интерфейсы и критерии готовности. [codex-5.3 / xhigh]
  - subagent codex-test-planner: Планировщик тестов - Определить unit/smoke/integration проверки и негативные сценарии. [gpt-5.5 / xhigh]
  - subagent codex-automation-builder: Инженер automation - Предложить или реализовать CLI/скрипты/мониторы для повторяемого выполнения. [gpt-5.4 mini / xhigh]
  - subagent codex-integration-checker: Проверяющий интеграции - Проверить совместимость с существующей структурой, SML, файлами памяти и политиками запуска. [gpt-5.4 / xhigh]
- L4 Архитектурный синтез: status=approved, agent=Codex, handoff=levels/L4/handoff.md
  - subagent codex-architecture-synthesizer: Архитектурный синтезатор - Собрать L1-L3 в целостное техническое решение без противоречий. [gpt-5.5 / xhigh]
  - subagent codex-contract-auditor: Аудитор контракта - Проверить, что contract, handoff, events и итоговые выводы согласованы. [gpt-5.5 / xhigh]
  - subagent codex-risk-gate: Risk gate - Отдельно оценить риски trading/long-running/secrets/external writes/destructive действий. [gpt-5.5 / xhigh]
  - subagent codex-maintainability-reviewer: Ревьюер сопровождения - Оценить простоту поддержки, расширения и передачи следующему агенту. [gpt-5.5 / xhigh]
- L5 Финальная инстанция для пользователя: status=approved, agent=Claude Code, handoff=final-report.md
  - subagent claude-executive-summarizer: Executive summarizer - Сжато объяснить пользователю итог, решение и оставшиеся риски. [Claude Opus 4.7 alias / xhigh]
  - subagent claude-technical-verifier: Финальный техпроверяющий - Независимо проверить техническую связность L1-L4 перед финальным отчетом. [Claude Haiku 4.5 alias / xhigh]
  - subagent claude-anti-distortion-auditor: Аудитор против искажения - Сверить final-report с brief, handoff и events, чтобы не было испорченного телефона. [Claude Sonnet 4.6 alias / xhigh]
  - subagent claude-final-decision-writer: Автор заключения - Сформировать final-report.md для пользователя с понятным решением approve/revise/escalate/block. [Claude Opus 4.8 alias / xhigh]
