# Запрос

Ежедневный heartbeat automation-3: записать Bitrix `Счет отправлен, %` в Google Sheet `Дашборд ОП`.

# Результат

- Дата запуска: `2026-06-30`.
- Целевая дата: `2026-06-29`.
- Лист: `Июнь 2026 ОП`, колонка `AO`.
- Записанные значения: Юлианна Винокурова `17%`, Алена Ковалева `78%`, Екатерина Коваленко `100%`, Юлия Ковалева `60%`, Павел Клец `62%`, Максим Волынкин `43%`, Даниил Никушин `60%`, Татьяна Петренко `50%`.
- Вне структуры листа: Гулина Яна Сергеевна (`user_id=985`), `new_deals=1`, `sent_invoice_transitions=0`; запись не выполнялась, потому что нет строки метрики.

# Проверки

- SML ping/startup/semantic выполнены; semantic_query degraded/text, без блокера.
- Preflight ok=true.
- `run_and_write_daily.ps1 -RunDate 2026-06-30` завершился успешно.
- Google Sheets writer вернул `updated_cells=8`.
- Отдельный readback подтвердил: `AO18=17%`, `AO34=78%`, `AO50=100%`, `AO66=60%`, `AO84=62%`, `AO100=43%`, `AO116=60%`, `AO132=50%`.
- Имя `unknown_assigned_by` проверено через Bitrix `user.get`.
- Artifact: `C:\Users\koval\Documents\ОК.ру\exports\sheets\automation-3-conversion-invoices-2026-06-30.json`.

# Риски

- Есть активный Bitrix-пользователь вне структуры листа; не добавлять строки без явного изменения таблицы.
- Старые статические строки automation-3 не использовать.

# Следующему

- Следующий запуск начинать с SML/preflight и запускать `C:\Users\koval\Documents\ОК.ру\automations\conversion_invoices\run_and_write_daily.ps1 -RunDate YYYY-MM-DD`.
- При наличии менеджеров вне структуры листа фиксировать их в отчете, но не писать в неподписанные дублирующие подблоки.
