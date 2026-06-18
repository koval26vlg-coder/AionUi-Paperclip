# Карты связей

Этот раздел описывает постоянный способ строить карты связей для проекта `D:\AionUi-Paperclip` и других рабочих папок.

## Назначение

Карты связей нужны, чтобы Codex и Gemini могли быстро увидеть:

- какие агенты, документы, инструменты, решения и задачи связаны между собой;
- какие файлы являются источниками истины;
- какие узлы являются центральными;
- какие связи явные, а какие только предположительные;
- где находятся мосты между SML, документами, Aion Vision и внешними задачами.

## Текущий стандарт

Основной постоянный skill:

```text
C:\Users\koval\.codex\skills\relationship-map-builder
```

Он использует идеи Graphify, но адаптирован под SML:

- сначала читается SML и проектные документы;
- граф содержит typed nodes и typed edges;
- связи маркируются `EXTRACTED`, `INFERRED`, `AMBIGUOUS`;
- Markdown-отчет и JSON-граф кладутся рядом;
- результат можно использовать как вход для следующего агента.

## Текущие артефакты

```text
docs/relationship-maps/graphify-sml-relationship-map.md
docs/relationship-maps/graphify-sml-relationship-map.json
```

Markdown нужен для человека и быстрого чтения агентом. JSON нужен для повторной обработки, поиска, визуализации или будущей интеграции с Aion Vision.

## Автоматическое обновление

Карта связей является автоматическим слоем памяти. Ее пересобирает существующий watcher:

```text
tools/watch-memory.ps1
```

Когда меняются `AGENTS.md`, `GEMINI.md`, `docs/`, `.cursor/`, `.kiro/` или `tools/`, watcher после debounce пересобирает:

```text
docs/context-packs/context-pack-latest.md
docs/relationship-maps/graphify-sml-relationship-map.md
docs/relationship-maps/graphify-sml-relationship-map.json
```

Generated-файлы `docs/relationship-maps/` исключены из fingerprint watcher-а, чтобы карта не запускала бесконечную пересборку сама себя.

## Быстрый поиск по карте

Агент не должен читать весь JSON. Для экономии токенов использовать query-утилиту:

```powershell
& "D:\AionUi-Paperclip\.venv-sml\Scripts\python.exe" "D:\AionUi-Paperclip\tools\query-relationship-map.py" "Codex Gemini SML"
```

Утилита возвращает только релевантные узлы и ближайшие связи. Это первый навигационный шаг перед широким поиском по файлам.

## Как обновить карту вручную

```powershell
& "D:\AionUi-Paperclip\tools\build-relationship-map.ps1"
```

## Когда использовать upstream Graphify

Внешний `safishamsi/graphify` полезен для глубокого анализа больших codebase: AST, code imports, docs, PDF, image/video, `graph.html`, `graph.json`, `GRAPH_REPORT.md`.

Для общей памяти Aion/SML не нужно слепо ставить Graphify hooks поверх `AGENTS.md` или `GEMINI.md`. Сначала должен сохраняться наш главный принцип: SML остается основной памятью, а карта связей является производным артефактом.

Если нужен полный Graphify:

```powershell
uv tool install graphifyy
graphify install --project --platform codex
graphify install --project --platform gemini
graphify . --no-viz
```

Перед установкой hooks обязательно проверить, не перетираются ли русские SML-правила в `AGENTS.md` и `GEMINI.md`.
