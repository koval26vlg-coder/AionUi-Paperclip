# Codex — 2026-06-23

## Запрос
Добавить отдельную Telegram-команду для прогноза по остальным событиям.

## План
TDD: тесты на formatter и command route; реализация /events; docs; verification.

## Результат
Готово. Добавлена команда /events с alias /other,/others,/события,/прочее. /events или /events 5 показывает прогноз по не-1X2 рынкам в горизонте: тоталы, форы, ОЗ, индивидуальные тоталы. /events <команды> показывает эти события по матчу. Карточки включают ссылку PARI, причины/риски из real-context и сортировку по adjusted probability/data_quality/delta. Проверка: py_compile OK, unittest discover 66 OK, direct render /events 3 OK.

## Изменённые файлы
- New project/src/sports_betting_analytics/telegram_bot.py
- New project/tests/test_core.py
- New project/README.md
- New project/КАК_РАБОТАТЬ.md

## Риски и ограничения
Текущий топ может включать очень низкие коэффициенты вроде тотал больше 0.5; бот явно помечает низкий коэффициент. Это прогноз вероятности, не команда к ставке.

## Что следующему агенту
Если нужно, добавить режим /events value для отсечения кэфов ниже 1.30 и выбора баланса вероятность/коэффициент.
