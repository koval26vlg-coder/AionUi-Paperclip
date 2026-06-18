# Отчёт агента

- Дата и время: 2026-06-18
- Агент: Claude Code

## Запрос пользователя

Продолжить развитие; ответить, можно ли сносить Ollama; дать подробный гайд для новичка.

## Что сделано

- **Ответ про Ollama**: опциональна. Без неё проект работает — поиск деградирует на FTS5 (по словам). Снос безопасен, но теряется поиск по смыслу; зафиксировано в `decisions.md` и `constraints.md`.
- **Панель здоровья системы** (следующий слой развития): `export-sml-dashboard.py` отдаёт секцию `health` — статус watcher (heartbeat), доступность Ollama (→ режим поиска), последний бэкап. Компонент `SystemHealth.tsx` показывает три индикатора (зелёный/жёлтый/красный) в правой колонке дашборда. Связывает воедино надёжность, сделанную ранее (heartbeat, FTS5-фоллбэк, бэкапы), в один видимый блок.
- **Гайд для новичка**: `docs/HOW-TO-USE.md` — простым языком: что это, как запускать агентов и панель, как искать в памяти, обслуживание, troubleshooting, шпаргалка команд.

## Изменённые файлы

- `apps/aion-vision/scripts/export-sml-dashboard.py` (секция `_health` + в payload)
- `apps/aion-vision/src/types/dashboard.ts` (`SystemHealth`)
- `apps/aion-vision/src/components/dashboard/SystemHealth.tsx` (новый)
- `apps/aion-vision/src/App.tsx` (интеграция)
- `docs/HOW-TO-USE.md` (новый)
- `docs/decisions.md`, `docs/memory/layers/constraints.md`, `docs/current-context.md`

## Проверки

- `export-sml-dashboard.py --json` → `health` корректен: watcher (status/age), search (mode=semantic, ollama=true), backup (last/count).
- ESLint чист; `vite build` успешен.

## Риски и ограничения

- Индикатор watcher честно показал `stale`: фоновый наблюдатель Task Scheduler в этой сессии не крутится (только ручные запуски). Это и есть назначение панели — делать такие вещи видимыми.
- Health-проверка Ollama добавляет ~1.5 c таймаута к сборке payload, когда Ollama недоступна (короткий timeout).

## Что проверить следующему агенту

- Открыть дашборд (`START-AION-VISION-SERVE.cmd`), убедиться что блок «Здоровье системы» отражает реальность (watcher/поиск/бэкап).
- Дать `docs/HOW-TO-USE.md` любому новичку как точку входа.
