# Анализ рынка: улучшение аватарки для HeadHunter

Оператор: Codex. Финальный внешний runtime Claude Code не вызывался; отчет сформирован через delegated executor, чтобы завершить workflow state machine без ложного указания внешнего выполнения.

## Короткий вывод

Standalone-продукт "улучшить аватарку для hh.ru" я не считаю сильной основной ставкой. Боль есть, но она слишком узкая и уже частично закрывается универсальными AI headshot/background remover сервисами.

Более перспективная ставка: "HH Resume Booster" - сервис, который улучшает не только фото, а весь первый контакт с работодателем: фото, заголовок резюме, блок "о себе", релевантность под вакансию, сопроводительное письмо и чеклист перед откликом.

## Что показывает рынок

На стороне спроса:
- hh.ru публикует ежемесячные обзоры рынка труда, где отслеживает спрос работодателей и активность соискателей: https://hh.ru/article/26641
- В марте 2026 hh.индекс составил 11,4, активные вакансии снизились на 27% год к году, активные резюме выросли на 41% год к году: https://stats.hh.ru/api/v1/monthly-report/f-983c2f9a-0568-4976-8b30-83bce102140b
- hh.ru прямо рекомендует качественное фото, где видно лицо, и объясняет, какие фото не подходят для делового образа: https://hh.ru/article/23994
- hh.ru описывает хорошее резюме как структурированный документ, дополненный фотографией, контактами и важной информацией: https://hh.ru/article/kak-sostavit-rezyume
- По материалам hh.ru, фотография влияет на восприятие вкуса и соответствия корпоративной культуре: https://hh.ru/article/301522

На стороне конкуренции:
- AIQA, HeadshotMaster, Fotor, remove.bg, Canva уже закрывают значительную часть задач по AI-портрету, ретуши, удалению фона и деловой фотографии.
- HHBro и похожие продукты работают ближе к реальной боли соискателя: анализ вакансии, соответствие резюме, AI-сопроводительные письма, работа прямо на hh.ru.

## Насколько ниша занята

HH-only avatar enhancer как отдельная категория выглядит слабо занятой. Но это не значит, что ниша свободна в коммерческом смысле.

Реальная конкуренция идет не с прямыми HH-фоторедакторами, а с:
- универсальными AI headshot сервисами;
- редакторами фона и фото;
- карьерными консультантами;
- сервисами резюме;
- расширениями для hh.ru;
- AI-инструментами для сопроводительных писем и откликов.

Итог: окно есть только при HH-specific упаковке и доказуемой пользе. Просто "сделать фото красивее" - слабая позиция.

## Будет ли востребовано

Avatar-only может быть востребован как бесплатный или недорогой лид-магнит. Платежеспособный спрос вероятнее у более широкого пакета:
- "проверь мое резюме перед откликом";
- "сделай мой профиль более убедительным";
- "адаптируй резюме и письмо под вакансию";
- "покажи, почему меня не зовут".

Самые вероятные сегменты:
- офисные специалисты;
- продажи и клиентские роли;
- HR, администраторы, менеджеры;
- начинающие специалисты;
- люди после долгого перерыва;
- соискатели, которые активно откликаются и не получают приглашений.

## Рекомендованный продукт

Название для MVP: HH Resume Booster.

Модули:
1. Photo check: качество, лицо, фон, кадрирование, деловой стиль, риски неуместности.
2. Resume check: заголовок, опыт, "о себе", ключевые слова, избыточность, ошибки.
3. Vacancy fit: сравнение резюме с вакансией.
4. Cover letter: сопроводительное письмо под конкретную вакансию.
5. Action checklist: что исправить перед откликом.

Начинать без интеграции с hh.ru API: upload/copy-paste, без автооткликов и без логина на hh.ru.

## Альтернативные продукты, которые могут быть сильнее

1. AI-аудит резюме под hh.ru.
Пользователь вставляет резюме и получает приоритетный список правок.

2. Генератор отклика под вакансию.
Пользователь вставляет вакансию и резюме, получает cover letter и правки под требования.

3. Карьерный "анти-фильтр".
Показывает, где резюме выглядит нерелевантным, слабым или подозрительным для рекрутера.

4. Пакеты по профессиям.
Например: sales, junior developer, product manager, HR, администратор, бухгалтер. В каждом пакете свои фото-рекомендации, тон резюме и шаблоны откликов.

5. Трекер эффективности откликов.
Пользователь вручную вносит просмотры, отклики, приглашения. Сервис предлагает A/B-версии заголовка, фото и письма.

## Проверка спроса

За 2 недели:
1. Сделать landing с тремя офферами: avatar-only, full resume audit, vacancy response pack.
2. Собрать email/waitlist и paid intent.
3. Провести 20 интервью с соискателями и 5-10 с HR.
4. Ручной concierge MVP на 30 пользователях.
5. Сравнить, что покупают чаще: фото отдельно или полный пакет.

## Решение

approve

Идти в avatar-only как главный продукт не рекомендую. Использовать аватарку как входной модуль и маркетинговый крючок - да. Основной продукт лучше строить вокруг повышения конверсии резюме и отклика на hh.ru.

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
