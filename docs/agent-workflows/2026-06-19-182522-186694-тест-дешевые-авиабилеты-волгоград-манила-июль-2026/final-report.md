# Финальный отчет L5 - Авиабилеты VOG -> MNL, июль 2026

Дата проверки: 19 июня 2026, около 18:20-18:34 МСК

Workflow: `2026-06-19-182522-186694-тест-дешевые-авиабилеты-волгоград-манила-июль-2026`

## Лучший найденный вариант

| Параметр | Значение |
| --- | --- |
| Маршрут туда | VOG 09:35 15 июля -> SVO -> PVG -> MNL 01:20 17 июля |
| Маршрут обратно | MNL 02:25 25 июля -> PVG -> SVO -> VOG 21:30 25 июля |
| Пересадки | 2 в каждую сторону: Москва Шереметьево + Шанхай Пудун |
| Время в пути туда | 34 ч 45 м |
| Время в пути обратно | 24 ч 05 м |
| Цена без багажа | 71 903 RUB |
| Цена с багажом 10 кг | 74 500 RUB |
| Источник | https://www.aviasales.ru/search/VOG1507MNL25071 |

Важно: это цена Aviasales на момент проверки 19 июня 2026. Авиабилеты динамические, к моменту покупки цена может быть другой.

## Почему выбран этот вариант

Проверена полная матрица 5 x 5: вылеты 13-17 июля 2026 и возвраты 23-27 июля 2026. Лучшая цена оказалась на базовые даты запроса: 15 июля - 25 июля. Сдвиг на +/- 2 дня цену не улучшил.

Топ-5 комбинаций:

| Вылет | Возврат | Без багажа | С багажом |
| --- | --- | ---: | ---: |
| 2026-07-15 | 2026-07-25 | 71 903 | 74 500 |
| 2026-07-15 | 2026-07-27 | 73 223 | 99 298 |
| 2026-07-15 | 2026-07-26 | 74 107 | 102 440 |
| 2026-07-15 | 2026-07-23 | 74 655 | 97 575 |
| 2026-07-16 | 2026-07-25 | 74 850 | 107 737 |

## Риски

1. Ценовой риск: Aviasales - агрегатор, а не финальный продавец. Цена может измениться на checkout.
2. Транзитный риск `PVG`: нужно проверить 24-часовой безвизовый транзит, терминалы, багаж и единый PNR.
3. Багажный риск: `10 кг` может оказаться не классическим зарегистрированным багажом, а расширенной ручной кладью.
4. PNR-риск: если маршрут составной, пассажир сам отвечает за получение багажа и повторную регистрацию на стыковках.
5. Риск оплаты: у самого дешевого продавца может не пройти российская карта.
6. Комфортный риск: перелет туда почти 35 часов, прибытие в Манилу ночью 17 июля.

## Что проверить перед покупкой

1. Открыть ссылку и дойти до checkout.
2. Проверить итоговую цену у конкретного продавца.
3. Проверить, единый ли билет/PNR.
4. Проверить, что именно входит в багаж 10 кг.
5. Проверить транзит через `PVG`.
6. Проверить способ оплаты.
7. Проверить возвратность и обмен.

## Как прошел тест workflow

Workflow отработал по цепочке:

- L1.0 MiMo AUTO: формальный старт и первичная матрица; реальный MiMo AUTO runtime не подтвержден.
- L1.1 Antigravity CLI: независимая верификация данных.
- L2 Antigravity CLI: инженерный risk review.
- L3 Codex: проверка пригодности результата и automation gaps.
- L4 Codex: синтез и anti-distortion review.
- L5 Claude Code: финальный отчет.

Ключевые факты не исказились между уровнями:

- даты: 2026-07-15 - 2026-07-25;
- цена без багажа: 71 903 RUB;
- цена с багажом 10 кг: 74 500 RUB;
- маршрут: `VOG -> SVO -> PVG -> MNL`, обратно `MNL -> PVG -> SVO -> VOG`.

## Найденные технические проблемы workflow

- `submit-work` падает `SameFileError`, если передать уже целевой `levels/.../handoff.md`.
- `agy --print` не выводит stdout, хотя работу выполняет; результат приходится проверять через files/events/conversation DB.
- Model labels Antigravity subagents устарели и отображают `Gemini 3.1/3.5`.

## Вердикт L5

approve.

Результат годится как отправная точка для ручной покупки, но покупать без проверки checkout, PNR, багажа, транзита и оплаты не рекомендуется.

## История прохождения уровней

- L1 Нижний авто-уровень и исследовательский отдел: status=approved, agent=Antigravity CLI, handoff=levels/L1/L1.1/handoff.md
  - L1.0 AUTO-первичная разведка: status=approved, agent=MiMo AUTO, mode=AUTO, handoff=levels/L1/L1.0/handoff.md
    - subagent mimo-intake-scanner: Сканер постановки - Вытащить исходную цель, ограничения, входные данные и явные критерии успеха. [MiMo AUTO / AUTO / Xiaomi API AUTO]
    - subagent mimo-hypothesis-generator: Генератор первичных гипотез - Дать быстрые варианты решения, не выдавая их за проверенные выводы. [MiMo AUTO / AUTO / Xiaomi API AUTO]
    - subagent mimo-risk-sentinel: Сигнальщик очевидных рисков - Отметить пробелы, противоречия, опасные допущения и что нельзя потерять дальше. [MiMo AUTO / AUTO / Xiaomi API AUTO]
  - L1.1 Исследовательский lead: status=approved, agent=Antigravity CLI, mode=reviewed, handoff=levels/L1/L1.1/handoff.md
    - subagent antigravity-source-verifier: Проверяющий фактов - Сверить тезисы MiMo с brief, handoff, событиями и доступными источниками. [Gemini 3.1 Pro / High]
    - subagent antigravity-context-expander: Расширитель контекста - Добавить недостающие альтернативы, ограничения, зависимости и edge cases. [Gemini 3.1 Pro / Low]
    - subagent antigravity-noise-filter: Фильтр шума - Убрать неподтвержденные или лишние идеи, чтобы L1 не передал искажение выше. [Gemini 3.5 Flash / Low]
    - subagent antigravity-handoff-editor: Редактор L1-handoff - Собрать проверенный handoff с явным решением approve/revise/escalate/block. [Gemini 3.5 Flash / Medium]
- L2 Инженерная проверка: status=approved, agent=Antigravity CLI, handoff=levels/L2/handoff.md
  - subagent antigravity-engineering-reviewer: Инженерный ревьюер - Проверить применимость L1-выводов к реальной реализации. [Gemini 3.5 Flash / High]
  - subagent antigravity-constraint-checker: Проверяющий ограничений - Сверить решение с brief, контрактом, risk flags, allowed_next_agents и контекстными лимитами. [Gemini 3.5 Flash / High]
  - subagent antigravity-edge-case-scout: Разведчик крайних случаев - Найти скрытые сценарии, неполные данные, конфликтующие требования и слабые места. [Gemini 3.5 Flash / High]
  - subagent antigravity-revision-gate: Gate ревизии - Решить, можно ли передавать работу на Codex L3 или нужно вернуть на доработку. [Gemini 3.5 Flash / High]
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
