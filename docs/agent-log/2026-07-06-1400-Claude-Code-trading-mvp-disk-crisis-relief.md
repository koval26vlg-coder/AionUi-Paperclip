# trading_mvp: разбор статуса 06.07 + освобождение диска C: после смерти 72ч рана

Дата: 2026-07-06 ~14:00 +03
Агент: Claude Code

## Контекст

Статус-проверка по запросу пользователя показала:

1. **Durable-протокол отработал в бою.** Codex интегрировал guards/resume в `start_ws_collect_durable.ps1` (лог `2026-07-03-codex-trading-mvp-durable-ws-guards-resume.md`), прогнал 2ч verification и запустил 72ч ран `ws_durable_72h_20260704_000015`. Ран прожил ~60 часов: **19 полных сегментов с манифестами, 62.9 млн событий, 28.9 GB, coverage 0.833, gaps 0.1с** — данные сохранены, gate закрыт штатно (`segment_20_incomplete`). Против июльских катастроф (7.7M и 1.86M событий потеряны целиком) — прямое подтверждение ценности сегментации.
2. **Причина смерти сегмента 20: `OSError [Errno 28] No space left on device`** (+ сетевые флапы). На C: оставалось 1.7 GB из ~306. Это слабость A3 из аудита 2026-07-02 (raw без ротации/компрессии), ударившая по-настоящему.
3. **Weekly forward отработал автоматически** (пн 09:05): отчёт создан, новый кандидат GIGGLE (E ~10%/год); 5/400 символов упали на DNS — дозабрать resume'ом. Следующий запуск 13.07.

## Операция освобождения диска (одобрена пользователем)

1. `raw-durable` (29.91 GB, включая ценный 60ч датасет) **скопирован** на `D:\ZolotyayLopata-data\raw-durable` (robocopy: 120/120 файлов, FAILED=0), **сверен пофайлово** (путь+размер), источник удалён, на его месте **junction** `exports\trading-mvp\raw-durable -> D:\ZolotyayLopata-data\raw-durable` — все пути в манифестах/gate/логах продолжают работать; проверено чтением state.json через старый путь.
2. Старый `raw` (21.4 GB, два July-2 partial датасета, replay_allowed=false) заархивирован: `D:\ZolotyayLopata-data\raw-archive-20260706.zip` (1.83 GB, 50/50 файлов сверено списком tar).
3. Удаление оригиналов `raw\*` и `normalized\*` (12.3 GB, регенерируется) — ожидает явного подтверждения пользователя с именованием каталогов (auto-mode security classifier корректно требует явности для irreversible deletion).

Диск C:: было 1.7 GB свободно → сейчас 31.6 GB → после финальной зачистки будет ~65 GB.

## Следующие шаги

1. Пользователь: подтвердить удаление `exports\trading-mvp\raw\*` и `exports\trading-mvp\normalized\*` (архив и junction уже на месте).
2. Resume 72ч рана (у Codex-обёртки есть `-Resume`): добрать ~4-5 сегментов до полного coverage; писаться будут через junction на D: (там ~21 GB свободно — хватает).
3. Systemic fix: добавить в durable-коллектор pre-segment disk-space check (отказ от старта сегмента при < N GB) и компрессию сегментов по завершении — кандидат на следующую итерацию v1.1.
4. Постпроцесс 19 готовых сегментов (данные уже пригодны для spot sweep/reversal ветки после data-quality gate по stitched manifest).

## Изменённые артефакты

- `D:\ZolotyayLopata-data\raw-durable\` (перенос), `raw-archive-20260706.zip` (новый архив)
- junction `C:\Users\koval\Documents\ZolotyayLopata\exports\trading-mvp\raw-durable`
- Код проекта не менялся; live trading не затрагивался.
