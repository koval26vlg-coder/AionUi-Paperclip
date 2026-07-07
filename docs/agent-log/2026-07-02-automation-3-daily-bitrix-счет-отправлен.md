# Запрос

automation-3: ежедневный запуск конверсии по счетам Bitrix -> Google Sheets для метрики `Счет отправлен, %`.

# Результат

Выполнено. Дата запуска `2026-07-02`, целевая дата `2026-07-01`, таблица `Дашборд ОП`, лист `Июль 2026 ОП`, колонка `M`.

Записано и проверено:

- `M18=86%` Юлианна Винокурова
- `M34=33%` Алена Ковалева
- `M50=62%` Екатерина Коваленко
- `M66=0%` Юлия Ковалева
- `M84=60%` Павел Клец
- `M100=67%` Максим Волынкин
- `M116=50%` Даниил Никушин
- `M132=60%` Татьяна Петренко

`unknown_assigned_by=[]`.

Также исправлен переход месяца в `write_daily.py`: вместо жесткой привязки к `Июнь 2026 ОП` writer теперь берет metadata всех листов и выбирает месячный лист по дате запуска.

# Проверки

- SML ping/startup ok; semantic_query ok в `degraded/text` режиме.
- Preflight ok=true, Bitrix/VibeCode checks ok.
- Pending-write не найден.
- Calendar check после правки: `Июль 2026 ОП`, `run_column=N`, `target_column=M`.
- `run_and_write_daily.ps1 -RunDate 2026-07-02` выполнил расчет, запись и readback.
- Writer: `updated_cells=8`, verified readback совпал.
- Артефакт: `C:/Users/koval/Documents/ОК.ру/exports/sheets/automation-3-conversion-invoices-2026-07-02.json`.

# Риски

- Aion file-memory watcher показал stale heartbeat после ошибки доступа к heartbeat-файлу; SML MCP работал.
- Праздники нужно вынести в общий календарь, чтобы не поддерживать их вручную в writer.

# Следующему

Продолжать helper-route: SML -> preflight -> pending -> `run_and_write_daily.ps1` -> verified readback -> журнал/SML. Не возвращать старый single-sheet route.
