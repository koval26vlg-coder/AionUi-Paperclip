# Запрос

automation-3: daily Bitrix `Счет отправлен, %` -> Google Sheet за предыдущий рабочий день.

# Результат

2026-06-23 выполнено: target `2026-06-22`, лист `Июнь 2026 ОП`, колонка `AH`. Записано и проверено в реальные строки `Счет отправлен, %`: `AH18=25%`, `AH34=0%`, `AH50=83%`, `AH66=0%`, `AH84=40%`, `AH100=29%`, `AH116=29%`, `AH132=57%`.

Расчет шел по cohort-формуле: `45` новых сделок `CATEGORY_ID=1`, `16` дошли до `C1:UC_9NU15J`; `2` stage-history перехода вне периода создания отсечены. Все новые сделки попали в текущий набор восьми строк менеджеров, `unknown_assigned_by=[]`.

# Проверки

SML ping/startup/semantic ok. Preflight ok=true. Helper `run_and_write_daily.ps1 -RunDate 2026-06-23` успешно сделал calendar-check, расчет и service-account write. Writer обновил `8` ячеек, контрольное и дополнительное чтение подтвердили значения. `py_compile` для `calc_invoice_conversion.py` и `write_daily.py` ok.

# Риски

В SML остаются старые исторические записи до ретро-аудита, но актуальный prompt и память automation-3 требуют wrapper и динамические строки. Active-run gate отдельного проекта `trading_mvp` был RUNNING; по нему действий не запускалось.

# Следующему

Продолжать только через `automations/conversion_invoices/run_and_write_daily.ps1`.
