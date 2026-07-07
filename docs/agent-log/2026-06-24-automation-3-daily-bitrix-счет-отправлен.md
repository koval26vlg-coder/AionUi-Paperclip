# Запрос

Ежедневный запуск automation-3 для `ОК.ру`: записать Bitrix `Счет отправлен, %` в Google Sheet `Дашборд ОП`.

# Результат

- Дата запуска: `2026-06-24`.
- Целевая дата: `2026-06-23`.
- Лист: `Июнь 2026 ОП`, колонка `AI`.
- Записанные значения: Юлианна Винокурова `50%`, Алена Ковалева `60%`, Екатерина Коваленко `50%`, Юлия Ковалева `50%`, Павел Клец `80%`, Максим Волынкин пусто, Даниил Никушин `50%`, Татьяна Петренко `0%`.
- Максим Волынкин пропущен в записи значения как процент, потому что denominator `new_deals=0`; ячейка `AI100` оставлена пустой.

# Проверки

- SML старт выполнен: `sml.ping`, `sml.startup_pack`, `sml.semantic_query`.
- Project preflight вернул `ok=true`.
- Основной wrapper `run_and_write_daily.ps1 -RunDate 2026-06-24` завершился успешно.
- Google Sheets writer вернул `updated_cells=8`.
- Readback подтвердил: `AI18=50%`, `AI34=60%`, `AI50=50%`, `AI66=50%`, `AI84=80%`, `AI100=`, `AI116=50%`, `AI132=0%`.
- Artifact: `C:\Users\koval\Documents\ОК.ру\exports\sheets\automation-3-conversion-invoices-2026-06-24.json`.

# Риски

- Для automation-3 нельзя использовать stage-history переходы всех сделок дня: нужен cohort numerator по сделкам, созданным в целевую дату.
- Старые статические строки метрики не использовать.
- Для автономной проверки writer нужен проектный `.venv`, потому что bundled Python без `google.oauth2`.

# Следующему

- Следующий запуск начинать с SML/preflight и запускать только `C:\Users\koval\Documents\ОК.ру\automations\conversion_invoices\run_and_write_daily.ps1 -RunDate YYYY-MM-DD`.
- Не использовать браузерные способы записи; рабочий метод - service account Google Sheets API.
