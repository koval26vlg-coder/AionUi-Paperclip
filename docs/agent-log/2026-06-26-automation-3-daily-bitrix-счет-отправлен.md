# Запрос

Ежедневный heartbeat automation-3: записать Bitrix `Счет отправлен, %` в Google Sheet `Дашборд ОП`.

# Результат

- Дата запуска: `2026-06-26`.
- Целевая дата: `2026-06-25`.
- Лист: `Июнь 2026 ОП`, колонка `AK`.
- Записанные значения: Юлианна Винокурова `100%`, Алена Ковалева `57%`, Екатерина Коваленко `60%`, Юлия Ковалева `0%`, Павел Клец `25%`, Максим Волынкин `67%`, Даниил Никушин `100%`, Татьяна Петренко `50%`.
- Вне структуры листа: Елена Гаус (`user_id=975`), `new_deals=1`, `sent_invoice_transitions=0`; запись не выполнялась, потому что нет строки метрики.

# Проверки

- SML ping/startup/semantic выполнены; semantic_query degraded/text, без блокера.
- Preflight ok=true.
- `run_and_write_daily.ps1 -RunDate 2026-06-26` завершился успешно.
- Google Sheets writer вернул `updated_cells=8`.
- Отдельный readback подтвердил: `AK18=100%`, `AK34=57%`, `AK50=60%`, `AK66=0%`, `AK84=25%`, `AK100=67%`, `AK116=100%`, `AK132=50%`.
- Artifact: `C:\Users\koval\Documents\ОК.ру\exports\sheets\automation-3-conversion-invoices-2026-06-26.json`.

# Риски

- Aion file-memory watcher heartbeat stale, но SML MCP работает.
- Старые статические строки automation-3 не использовать.

# Следующему

- Следующий запуск начинать с SML/preflight и запускать `C:\Users\koval\Documents\ОК.ру\automations\conversion_invoices\run_and_write_daily.ps1 -RunDate YYYY-MM-DD`.
- При наличии менеджеров вне структуры листа фиксировать их в отчете, но не добавлять строки без явного изменения таблицы.
