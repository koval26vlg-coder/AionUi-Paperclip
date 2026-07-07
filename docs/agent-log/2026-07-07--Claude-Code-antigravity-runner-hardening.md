# 2026-07-07 — Claude Code — Hardening Antigravity L1/L2 runner

## Запрос пользователя

Взяться за отдельный hardening Antigravity L1/L2 runner (последний открытый дефект из аудита).

## Что сделано

Реализованы три меры из задачи, каждая с тестами.

### 1. Process-tree timeout (`tools/antigravity_print.py`)

`subprocess.run(timeout=)` убивал только прямой процесс, а `agy` порождает детей (node и т.п.),
которые оставались висеть при зависании (>180с в наблюдавшемся баге). Добавлены
`ProcessResult`, `run_process_with_tree_timeout` и `_kill_process_tree`: запуск через `Popen`,
при таймауте убивается всё дерево (Windows `taskkill /F /T /PID`, POSIX `os.killpg`). `main`
переведён на хелпер, при таймауте возвращает 124 с сообщением «killed process tree».

### 2. Жёсткая корреляция сессии (`tools/antigravity_print.py`)

`recent_conversation_dbs` при отсутствии свежей БД брал `recent or dbs` — то есть ЛЮБУЮ БД,
из-за чего DB-fallback подтягивал ответ ЧУЖОГО workflow (баг `label-check`). Grab-all убран:
теперь принимаются только БД с `mtime >= started_at - 2` (slack на granularity ФС). Если этот
запуск не записал БД — восстановление возвращает пусто, без межворкфлоу-протечки.

### 3. Запрет tool-use/внешнего поиска в review-only

- Промпт `build_prompt` (`antigravity_workflow_review.py`) явно запрещает веб-поиск, интернет
  и внешние инструменты.
- Флаг `--review-only` в `antigravity_print.py` + `review_violation()`: fail-closed (exit 5)
  при однозначных сигналах реального выполнения — payload `run_command`
  (`CommandLine`+`WaitMsBeforeAsync`) или call-style external-search токены (`google_search(` и т.п.).
  Простое упоминание имени инструмента в рассуждении НЕ триггерит (нет ложных срабатываний).
- `run_antigravity` передаёт `--review-only`; `main` раннера ясно репортит отказ по коду 5.
  Проверка мутации workflow-дерева (snapshot, exit 4) сохранена как отдельный жёсткий guard.

## Проверки

- Новые тесты: session correlation (2), review_violation (3), process-tree timeout (2),
  усиленный промпт (1). `pytest test_antigravity_print.py test_antigravity_workflow_review.py`
  → 15 passed (было 7).
- Полный `pytest tools/sml/tests` → 217 passed, 1 failed — только известный флак
  `test_ollama_embed_russian_text_returns_1024` (нужен живой Ollama; в изоляции проходит,
  в CI скипается). Мои изменения embedding не касаются.
- py_compile OK.

## Заметки

- `--sandbox` намеренно НЕ форсируется: по хронике 2026-06 `agy --sandbox --print` давал пустой
  stdout, то есть ненадёжен. Контроль строится на изоляции cwd + snapshot-проверке мутаций +
  fail-closed детекции выполнения, а не на sandbox-флаге.

## Следующему агенту

Все пункты аудита хаба закрыты. Открытых дефектов workflow нет. Отложен только HH Booster
(ждёт готовности к outreach).
