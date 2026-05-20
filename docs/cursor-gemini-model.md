# Gemini как модель внутри Cursor

Дата создания: 2026-05-14.

## Что это дает

Это отдельный путь от Gemini CLI.

После настройки Cursor сможет использовать модели Gemini напрямую через Google AI API. При этом наша общая память SML продолжит работать отдельно через `.cursor/mcp.json`.

Итоговая схема:

- Cursor отвечает за IDE, правки и Agent/Chat;
- Gemini может быть выбран как модель в Cursor;
- SML остается общей памятью и источником контекста;
- Gemini CLI остается отдельным агентом, которого можно запускать из терминала.

## Важные ограничения

- Нужен API-ключ Google AI Studio.
- Google AI Pro подписка и Google AI API key — не одно и то же. В Cursor обычно нужен именно API key.
- На бесплатном плане Cursor может блокировать выбор конкретной named model. Если появляется сообщение `Named models unavailable. Free plans can only use Auto`, значит в текущем плане Cursor можно выбрать только `Auto`, даже если в списке видна `Gemini 3.1 Pro`.
- Собственные API-ключи Cursor использует для стандартных chat-моделей. Специализированные функции вроде Tab Completion могут продолжать использовать встроенные модели Cursor.
- API-ключ нельзя записывать в `docs/`, `.cursor/`, `AGENTS.md`, чат или SML.
- Расходы и лимиты идут по Google AI API, а не по SML.

## Шаг 1. Получить Google AI API key

1. Открыть:

```text
https://aistudio.google.com/app/apikey
```

2. Войти в Google-аккаунт.
3. Нажать создание API key.
4. Скопировать ключ.

Не вставлять ключ в документы проекта.

## Шаг 2. Добавить ключ в Cursor

1. Открыть Cursor.
2. Открыть настройки:

```text
Cursor Settings
```

3. Перейти в:

```text
Models
```

4. Найти блок API keys / Google / Gemini.
5. Вставить Google AI API key.
6. Нажать:

```text
Verify
```

7. После успешной проверки в списке моделей должны появиться доступные Gemini-модели.

## Шаг 3. Выбрать модель Gemini

В Cursor Chat или Agent выбрать Gemini из списка моделей.

Если Cursor показывает ошибку:

```text
Named models unavailable
Free plans can only use Auto. Switch to Auto or upgrade plans to continue.
```

то доступны только два варианта:

1. выбрать `Auto` в выпадающем списке моделей Cursor;
2. перейти на платный план Cursor, если нужен выбор конкретной модели вроде `Gemini 3.1 Pro`.

Это ограничение Cursor, а не SML. Даже в режиме `Auto` Cursor должен видеть SML через `.cursor/mcp.json`.

Практически:

- для сложного анализа и ревью выбирать Gemini Pro, если он доступен;
- для быстрых и дешевых проверок выбирать Gemini Flash, если он доступен;
- для работы с большим контекстом использовать Max Mode только когда реально нужен большой контекст, потому что он может быть дороже.

## Шаг 4. Проверить, что SML доступен Cursor

В Cursor открыть проект:

```text
D:\AionUi-Paperclip
```

Затем спросить Cursor:

```text
Проверь MCP SML: вызови sml.ping и sml.startup_pack. Ответь по-русски, видишь ли ты общую память.
```

Ожидаемый результат:

- `sml.ping` возвращает `ok=true`;
- `startup_pack` возвращает общий контекст проекта;
- Cursor может записать отчет через `sml.add_log`.

## Рекомендуемый рабочий сценарий

Использовать Gemini внутри Cursor так:

1. Cursor открывает задачу и читает SML.
2. В качестве модели Cursor выбирается Gemini.
3. Gemini внутри Cursor анализирует задачу, но контекст берет через SML.
4. Cursor выполняет или предлагает правки.
5. После работы Cursor пишет отчет в SML.
6. Если задача рискованная, Codex или Gemini CLI дают независимое ревью.

Если Cursor находится на бесплатном плане и разрешает только `Auto`, использовать так:

1. В Cursor выбрать `Auto`.
2. Через Cursor работать с SML как обычно.
3. Если нужен именно Gemini, запускать Gemini CLI из терминала Cursor:

```powershell
cd D:\AionUi-Paperclip
gemini -p "Прочитай общий контекст через SML и дай ревью по-русски." --allowed-mcp-server-names sml --approval-mode yolo --skip-trust --output-format text
```

## Чем это отличается от Gemini CLI

| Вариант | Где работает | Для чего лучше |
| --- | --- | --- |
| Gemini в Cursor | Внутри Cursor Chat/Agent | Удобно работать прямо в IDE |
| Gemini CLI | В терминале | Независимый агент, ревьюер, отдельные smoke-тесты |
| SML | Общая память | Делает всех агентов взаимозаменяемыми |

## Проверочная фраза для Cursor

```text
Работай на модели Gemini. Перед ответом используй SML: вызови sml.startup_pack и semantic_query по теме. Затем дай решение по-русски и после работы запиши краткий отчет через sml.add_log.
```
