# Внешний проект: bitrix24-automation

Этот документ хранит память и backlog по внешнему прикладному проекту. Сам код проекта находится отдельно:

```text
C:\Users\koval\bat\bitrix24-automation
```

`D:\AionUi-Paperclip` не является Bitrix-проектом. Здесь остаются только контекст, решения, задачи и журналы агентов, чтобы Codex, Cursor, Kiro и Gemini могли продолжать работу без потери истории.

Временные фрагменты Bitrix-кода, которые раньше лежали в корне workspace, перенесены в архив:

```text
docs\projects\_archive\bitrix-temp-code
```

Они не считаются активным исходным кодом.

## Backlog: средний блок после гигиены

Порядок — жёсткий. Каждый пункт заводится как отдельный spec перед началом работ.

1. `bitnewton-typing-and-tests` — типизация monolith + тесты KPI.
   - Добавить аннотации типов в `bitnewton_sync.py` и связанные модули; прогнать `mypy` (strict там, где реалистично).
   - Создать `tests/` c фикстурами синтетических транскриптов (`tests/fixtures/transcripts/*.txt`) и эталонными ожиданиями по KPI.
   - Минимум по одному тесту на функцию из `scoring/` (checklist, objections, discipline, quality).
   - Обоснование: без тестов и типов декомпозиция монолита слепая.
2. `bitnewton-pipeline-decomposition` — декомпозиция `pipelines/bitnewton_sync.py` (4290 строк).
   - Разбить на: `pipelines/cli.py`, `deals.py`, `calls.py`, `audio.py`, `asr.py`, `reporting.py`, `attach.py`.
   - `pipelines/scoring/` с модулями `checklist.py`, `objections.py`, `discipline.py`, `quality.py` — каждый <=300 строк.
   - Зависит от #1: тесты KPI должны существовать и зелёно проходить до и после.
3. `bitnewton-kpi-schema-validation` — валидация `kpi_config*.json` через `pydantic` или `jsonschema`.
   - Схема, покрывающая все ключи профилей; строгая валидация при старте CLI и Streamlit UI.
   - Вписывается в `pipelines/scoring/` после #2 либо делается параллельно как stand-alone.
4. `bitnewton-idempotency-statedb` — SQLite `state.db` для дедупа обработки.
   - Таблица `processed_calls(call_id, activity_id, deal_id, status, transcript_hash, attached_at)`.
   - Проверка перед ASR; запись после успешного `telephony.call.attachtranscription`.
   - Независим от #1–#3, можно катать параллельно.
5. `bitnewton-asr-client-hardening` — ретраи и прогресс в `bit_newton_asr.py`.
   - Выровнять с паттерном из `bitrix24_api.py` (ретраи 429/5xx, backoff + jitter, Retry-After, таймауты, request_id в логах).
   - Прогресс-индикатор (оценка длительности/байт) — опционально.
   - Независим, можно делать параллельно.

## Риски

- `bitnewton_sync.py` не покрыт тестами — любая ошибка при переносе функции обнаружится только на живом звонке. Поэтому `bitnewton-typing-and-tests` обязателен до декомпозиции.
- KPI-профили сейчас без схемы — тюнинг может молча деградировать метрики.
- Перезапуск пайплайна без idempotency может приводить к двойной отправке в Bit.Newton и двойному `attachtranscription`.
