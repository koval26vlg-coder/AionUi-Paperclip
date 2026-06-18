# Отчёт агента

- Дата и время: 2026-06-18
- Агент: Claude Code

## Запрос пользователя

Вынести API в отдельный постоянный HTTP-сервис (поиск и живые данные вне dev-сервера) и проверить дашборд в браузере.

## Что сделано

- **Постоянный HTTP-сервис**: `apps/aion-vision/scripts/serve-sml.py` на stdlib (`ThreadingHTTPServer`, без новых зависимостей). Отдаёт статику из `dist/` с SPA-фоллбэком и API `/api/sml-dashboard` + `/api/search`. Бэкенд переиспользуется из `export-sml-dashboard.py` и `search-sml.py` через importlib (без подпроцессов на запрос). Защита от выхода за пределы `dist/`, CORS, `no-store`.
- **Запускатель**: `START-AION-VISION-SERVE.cmd` — `npm run build` + запуск сервиса на `127.0.0.1:8787`.

## Изменённые файлы

- `apps/aion-vision/scripts/serve-sml.py` (новый)
- `START-AION-VISION-SERVE.cmd` (новый)
- `docs/decisions.md`, `docs/current-context.md`

## Проверки

- curl ко всем эндпоинтам сервиса: `/api/sml-dashboard` → status=live, 230 записей, 4 агента; `/api/search?q=бэкап памяти` → mode=text (FTS5-фоллбэк при недоступной Ollama), результаты 99%/74%; `/` → HTTP 200 text/html (статика); пустой запрос → mode=none.
- **Playwright (визуально)**: дашборд открылся (0 console errors), все секции на месте (метрики, граф с 4 нормализованными агентами, типы записей с цветами). Запрос «конверсия за неделю» в строке «Поиск по памяти» вернул 10 релевантных результатов (релевантность 99%→55%) с бейджем режима «текст». Скриншот: `apps/aion-vision/.playwright-mcp/memory-search-result.png`.

## Риски и ограничения

- Сервис слушает только loopback (127.0.0.1) — это правильно для локального инструмента, но для доступа с других машин понадобится явная настройка.
- Ollama в момент проверки не отвечала, поэтому поиск шёл в режиме `text` (FTS5). Это и есть подтверждение надёжности фоллбэка; при живой Ollama режим будет `semantic`.
- Скриншот и снапшоты Playwright сохранены в `apps/aion-vision/.playwright-mcp/` (артефакты, не часть приложения).

## Что проверить следующему агенту

- Для прод-режима использовать `START-AION-VISION-SERVE.cmd`; для разработки — `START-AION-VISION.cmd` (vite dev).
- При живой Ollama убедиться, что поиск возвращает `mode=semantic`.
