# HH Resume Booster validation test

## Цель

За 14 дней проверить, какой оффер дает лучший paid intent среди трех вариантов:

1. `avatar-only` - улучшение аватарки/фото для hh.ru.
2. `full-resume-audit` - полный аудит резюме и фото.
3. `vacancy-response-pack` - пакет отклика под конкретную вакансию: резюме, фото-рекомендации, сопроводительное письмо и чеклист.

Рабочая гипотеза: avatar-only лучше использовать как лид-магнит, а основной платный спрос должен быть выше у `full-resume-audit` или `vacancy-response-pack`.

## Где запускать

Экран добавлен в Aion Vision:

```text
http://127.0.0.1:5174/#hh-booster
```

Публичная форма для кандидата:

```text
http://127.0.0.1:5174/#hh-booster-public
```

Форма поддерживает прямой выбор оффера через query-параметр `offer`, чтобы раздавать ссылки не только по каналам, но и под конкретный вариант теста:

```text
http://127.0.0.1:5174/#hh-booster-public?offer=avatar
http://127.0.0.1:5174/#hh-booster-public?offer=audit
http://127.0.0.1:5174/#hh-booster-public?offer=response
```

Для честного per-offer coverage использовать ссылки формата `#hh-booster-public?channel=Telegram&offer=response`, а не только channel-only ссылки.

Рекомендуемый видимый запуск 14-дневного теста:

```powershell
& "D:\AionUi-Paperclip\apps\aion-vision\scripts\start-hh-booster-test.ps1" -Port 8787
```

Скрипт:

- собирает Aion Vision через `npm run build`;
- печатает операторскую ссылку, публичную форму, канальные ссылки, прямые offer-ссылки, примеры `offer + channel` и команду ежедневных метрик;
- показывает путь к server JSONL и server experiment state;
- показывает команду launch preflight после старта сервера;
- показывает команду launch manifest / freeze;
- показывает команду prelaunch GO/NO-GO перед публикацией ссылок;
- показывает команду финального decision report;
- показывает команду видимого status/monitor;
- показывает команду data quality audit;
- показывает команду daily outreach plan;
- показывает команду concierge packet с готовыми сообщениями и mark-командами;
- показывает команду concierge follow-up queue;
- показывает команды follow-up outcome tracker;
- показывает команду daily snapshot;
- показывает команды privacy/delete dry-run и write;
- не запускает reverse tunnel скрыто;
- запускает production-сервис в текущем видимом терминале, остановка через `Ctrl+C`.

Если уже есть публичный домен, tunnel или reverse proxy, передать его явно:

```powershell
& "D:\AionUi-Paperclip\apps\aion-vision\scripts\start-hh-booster-test.ps1" -Port 8787 -PublicBaseUrl "https://PUBLIC_HOST"
```

`https://PUBLIC_HOST`, `https://example.test` и похожие placeholder URL нужны только как пример. Перед публикацией ссылок prelaunch GO/NO-GO должен видеть реальный публичный tunnel/domain, иначе будет `NO-GO`.

Внешней аудитории нельзя отправлять `127.0.0.1`; публиковать нужно только URL из `-PublicBaseUrl` или проводить тест вживую с экрана.

Если server уже запущен без `-PublicBaseUrl`, операторскую панель можно открыть с query override. Панель сохранит внешний host в `localStorage` и блок `Ссылки и тексты` будет строить candidate links на публичном URL, а не на `127.0.0.1`:

```text
http://127.0.0.1:8787/?publicBaseUrl=https%3A%2F%2FREAL_PUBLIC_HOST#hh-booster
```

В самой панели в блоке `Ссылки и тексты` есть поле `Public host для candidate links`. Если там пусто и панель открыта локально, candidate links будут локальными; перед публикацией обязательно вставить public host или открыть панель по ссылке выше.

Для безопасной подготовки публикации использовать helper. Он не поднимает tunnel скрыто: без `-PublicBaseUrl` печатает видимые tunnel-варианты, а с реальным URL сначала проверяет публичный host/API. Без `-StartExperiment` helper требует, чтобы 14-дневный experiment уже стартовал, и только после этого сохраняет launch manifest и запускает prelaunch GO/NO-GO. Если `startedAt` пустой, helper возвращает `NO-GO` и не пишет manifest, чтобы не заморозить неправильный день 0.

```powershell
& "D:\AionUi-Paperclip\apps\aion-vision\scripts\prepare-hh-booster-public-launch.ps1"
& "D:\AionUi-Paperclip\apps\aion-vision\scripts\prepare-hh-booster-public-launch.ps1" -PublicBaseUrl "https://REAL_PUBLIC_HOST"
```

Если оператор готов реально начать сбор, можно использовать one-command launch. В этом режиме helper до записи `startedAt` запускает pre-start readiness check и допускает только ожидаемые блокеры `experiment_started`/`launch_manifest`; любые проблемы публичного tunnel/API блокируют старт 14-дневного таймера:

```powershell
& "D:\AionUi-Paperclip\apps\aion-vision\scripts\prepare-hh-booster-public-launch.ps1" -PublicBaseUrl "https://REAL_PUBLIC_HOST" -OperatorBaseUrl "http://127.0.0.1:8787" -CheckPublicHttp -StartExperiment
```

Если нужен временный public URL, использовать видимый localtunnel launcher. Он проверяет локальный server, запускает `npx --yes localtunnel` в текущем терминале и пишет вывод в `apps/aion-vision/data/hh-booster-public-tunnel.log`:

```powershell
& "D:\AionUi-Paperclip\apps\aion-vision\scripts\start-hh-booster-public-tunnel.ps1" -Port 8787
```

После появления публичного URL из localtunnel передать его в monitor и public launch helper. Не публиковать URL, пока prelaunch не вернет `Status: GO`.

Для репетиции дня 0 без старта 14-дневного таймера использовать one-command rehearsal launcher. Он поднимает только видимые окна сервера/tunnel, ждет local/public API, запускает preflight, генерирует publish kit и metadata, но не пишет `startedAt` и не создает launch manifest:

```powershell
& "D:\AionUi-Paperclip\apps\aion-vision\scripts\start-hh-booster-day0-rehearsal.ps1" -SkipBuild -WriteSmoke
```

Если уже есть стабильный внешний домен или tunnel, передать его явно:

```powershell
& "D:\AionUi-Paperclip\apps\aion-vision\scripts\start-hh-booster-day0-rehearsal.ps1" -PublicBaseUrl "https://REAL_PUBLIC_HOST" -SkipBuild -WriteSmoke
```

Rehearsal считается успешным только если все prelaunch-блокеры, кроме ожидаемых `experiment_started` и `launch_manifest`, устранены. При временных tunnel hosts (`*.loca.lt`, `*.ngrok-free.app`, `*.trycloudflare.com`, `*.localhost.run`) launcher оставляет предупреждение: перед рассылкой ссылок нужно заново проверить public API/prelaunch, потому что такой URL может умереть через несколько минут.

Если операторская панель недоступна, 14-дневное окно можно стартовать через CLI. Сначала dry-run, затем явная запись:

```powershell
& "D:\AionUi-Paperclip\.venv-sml\Scripts\python.exe" "D:\AionUi-Paperclip\tools\hh_resume_booster_experiment_state.py" --state "D:\AionUi-Paperclip\apps\aion-vision\data\hh-booster-experiment.json" --data "D:\AionUi-Paperclip\apps\aion-vision\data\hh-booster-leads.jsonl" start
& "D:\AionUi-Paperclip\.venv-sml\Scripts\python.exe" "D:\AionUi-Paperclip\tools\hh_resume_booster_experiment_state.py" --state "D:\AionUi-Paperclip\apps\aion-vision\data\hh-booster-experiment.json" --data "D:\AionUi-Paperclip\apps\aion-vision\data\hh-booster-leads.jsonl" start --write
```

Если лиды уже есть, CLI намеренно блокирует старт без `--allow-existing-leads`, чтобы не искажать день 1.

После запуска production-сервера в отдельном видимом терминале проверить готовность:

```powershell
& "D:\AionUi-Paperclip\apps\aion-vision\scripts\preflight-hh-booster-test.ps1" -BaseUrl "http://127.0.0.1:8787"
```

Если используется внешний URL:

```powershell
& "D:\AionUi-Paperclip\apps\aion-vision\scripts\preflight-hh-booster-test.ps1" -BaseUrl "http://127.0.0.1:8787" -PublicBaseUrl "https://PUBLIC_HOST"
```

С `-PublicBaseUrl` preflight должен показывать candidate `Public form` именно на внешнем host, проверять не только HTML root, но и публичные `GET /api/hh-booster/leads` / `GET /api/hh-booster/experiment`. Если tunnel отдает interstitial/password page вместо Aion Vision app shell, это считается `fail`.

Preflight по умолчанию ничего не пишет. Для явной проверки приема заявок можно сделать временный write-smoke; он отправит QA-заявку и удалит ее из локального JSONL с backup:

```powershell
& "D:\AionUi-Paperclip\apps\aion-vision\scripts\preflight-hh-booster-test.ps1" -BaseUrl "http://127.0.0.1:8787" -WriteSmoke
```

Чтобы проверить именно внешний путь кандидата, можно временно поставить `-BaseUrl` в public tunnel URL; write-smoke должен пройти через публичный endpoint и очистить QA-заявку из локального JSONL:

```powershell
& "D:\AionUi-Paperclip\apps\aion-vision\scripts\preflight-hh-booster-test.ps1" -BaseUrl "https://REAL_PUBLIC_HOST" -WriteSmoke
```

Перед ручной раздачей ссылок можно сгенерировать publish kit. Он не стартует эксперимент, не пишет заявки и не заменяет prelaunch, но собирает в один Markdown-файл direct offer links, полную матрицу `offer + channel`, готовые тексты и команды daily loop:

```powershell
& "D:\AionUi-Paperclip\.venv-sml\Scripts\python.exe" "D:\AionUi-Paperclip\tools\hh_resume_booster_publish_kit.py" --public-base-url "https://REAL_PUBLIC_HOST" --operator-base-url "http://127.0.0.1:8787" --out "D:\AionUi-Paperclip\apps\aion-vision\data\hh-booster-publish-kit.md" --write
```

Если tunnel сменился, publish kit нужно пересобрать с новым `--public-base-url`.

После успешного preflight и перед публикацией ссылок сохранить launch manifest:

```powershell
& "D:\AionUi-Paperclip\.venv-sml\Scripts\python.exe" "D:\AionUi-Paperclip\tools\hh_resume_booster_launch_manifest.py" --public-base-url "https://PUBLIC_HOST" --out "D:\AionUi-Paperclip\apps\aion-vision\data\hh-booster-launch-manifest.md"
```

Если тест проводится локально с экрана, можно сгенерировать manifest без внешнего URL; он явно отметит `Local URL warning`:

```powershell
& "D:\AionUi-Paperclip\.venv-sml\Scripts\python.exe" "D:\AionUi-Paperclip\tools\hh_resume_booster_launch_manifest.py" --out "D:\AionUi-Paperclip\apps\aion-vision\data\hh-booster-launch-manifest.md"
```

Manifest фиксирует офферы, цены, gates, текущий experiment state, ссылки, команды ежедневного контроля и правила, которые нельзя менять в середине теста без отдельной пометки.

Перед публикацией ссылок запустить read-only prelaunch GO/NO-GO. Команда должна выполняться после старта production-сервера, нажатия `Старт теста` в операторской панели и сохранения launch manifest. Проверка также валидирует прямые offer-ссылки и матрицу `offer + channel`, чтобы candidate links не потеряли выбранный оффер:

```powershell
& "D:\AionUi-Paperclip\.venv-sml\Scripts\python.exe" "D:\AionUi-Paperclip\tools\hh_resume_booster_prelaunch_check.py" --operator-base-url "http://127.0.0.1:8787" --public-base-url "https://PUBLIC_HOST" --check-public-http
```

Публиковать candidate links можно только при `Status: GO`. `NO-GO` означает, что нужно исправить публичный URL, сервер/API, experiment start, launch manifest или data quality до раздачи ссылок.

Запуск из `D:\AionUi-Paperclip\apps\aion-vision`:

```powershell
npm run dev -- --host 127.0.0.1 --port 5174
```

Dev-сервер удобен для проверки интерфейса, но публичная форма в этом режиме сохраняет заявки только в браузерный `localStorage`, потому что Vite не принимает POST-заявки.

Для серверного приема заявок использовать production-сервис Aion Vision после сборки:

```powershell
Set-Location "D:\AionUi-Paperclip\apps\aion-vision"
npm run build
& "D:\AionUi-Paperclip\.venv-sml\Scripts\python.exe" ".\scripts\serve-sml.py" --host 127.0.0.1 --port 8787
```

Эта ручная команда оставлена как fallback; для реального теста предпочтительнее `start-hh-booster-test.ps1`, потому что он печатает ссылки, метрики и tunnel-подсказки перед запуском сервера.

Тогда публичная форма доступна здесь:

```text
http://127.0.0.1:8787/#hh-booster-public
```

POST endpoint:

```text
POST /api/hh-booster/leads
```

Чтение серверных заявок:

```text
GET /api/hh-booster/leads?limit=5000
```

Синхронизация даты старта и порогов теста:

```text
GET /api/hh-booster/experiment
POST /api/hh-booster/experiment
```

Публичная форма отправляет заявку на сервер только если отмечено согласие на обработку контакта и описания ситуации. Без `consentAccepted=true` серверный endpoint возвращает `400 consent required`.

Серверные заявки пишутся локально в JSONL:

```text
D:\AionUi-Paperclip\apps\aion-vision\data\hh-booster-leads.jsonl
```

Дата старта и пороги теста в production-режиме пишутся рядом:

```text
D:\AionUi-Paperclip\apps\aion-vision\data\hh-booster-experiment.json
```

Папка `apps/aion-vision/data/` исключена из git, потому что там могут быть контакты и заметки пользователей.

Экран хранит заявки только в `localStorage` браузера под ключом:

```text
aion.hhResumeBooster.leads.v1
```

Дата старта и пороги эксперимента хранятся отдельно:

```text
aion.hhResumeBooster.experiment.v1
```

В production-режиме кнопка `Старт теста` также синхронизирует experiment state на сервер. Это нужно, чтобы финальный подсчет по server JSONL мог доказать, что прошло 14 дней, даже если браузерный `localStorage` недоступен.

Внешних записей, платежей, hh.ru login, scraping, API или автооткликов нет.

## Как начать тест

1. Открыть операторскую панель `http://127.0.0.1:5174/#hh-booster` или `http://127.0.0.1:8787/#hh-booster`.
2. Нажать `Старт теста`.
3. Проверить, что статус стал `День 1 из 14`.
4. В блоке `Ссылки и тексты` скопировать ссылку нужного канала и outreach-текст.
5. Для добора конкретного оффера копировать ссылку из блока `Прямые ссылки на офферы` или использовать `?offer=avatar|audit|response`.
6. Для кандидатов использовать публичную форму `#hh-booster-public`, а не операторскую панель.
7. Удалить QA/smoke-заявки через `Очистить`, если они остались.
8. Собирать только реальные контакты и ответы.
9. В операторской панели нажимать `Сервер`, если заявки собирались через `serve-sml.py`, чтобы подтянуть server JSONL и server experiment state в панель.
10. В конце каждого дня смотреть блок `Ежедневный темп` и экспортировать JSON/CSV или считать серверный JSONL.

## Что фиксировать

Минимальные поля:

- контакт: email или Telegram;
- профессия/роль;
- выбранный оффер;
- готовность платить: `Готов оплатить`, `Интересно`, `Не готов платить`;
- канал;
- заметки: цена, возражение, что зацепило, контекст поиска работы.

Strong paid intent считается только значение `Готов оплатить`.

## 14-дневный план

### День 1-2

- Запустить экран.
- Подготовить короткий текст для публикации в карьерных чатах.
- Получить первые 5-10 контактов без рекламы, вручную.

### День 3-7

- Раздать ссылку или показать экран в Telegram/VK/чатах курсов/карьерных сообществах.
- Собирать не только лиды, но и возражения.
- Не обещать рост приглашений; формулировка: "проверим, что мешает первому впечатлению".

### День 8-12

- Сделать 10-15 ручных concierge-разборов.
- Для каждого участника спросить, за какой пакет он реально готов заплатить сейчас.
- Фиксировать профессию, текущую активность поиска и цену.

### День 13-14

- Экспортировать JSON из экрана.
- Посчитать метрики через `tools/hh_resume_booster_metrics.py`.
- Принять решение по главному офферу.

## Критерии решения

Минимум для первичного вывода:

- 30+ лидов;
- 10+ strong paid intent;
- минимум два канала привлечения;
- не менее 5 профессий/ролей.
- не менее 5 лидов по каждому офферу: `avatar`, `audit`, `response`;
- истекли 14 дней с момента нажатия `Старт теста`.

Решение:

- Если `avatar-only` дает меньше paid intent, чем full audit/response pack, оставляем аватарку как лид-магнит.
- Если `full-resume-audit` выигрывает, MVP строим как аудит профиля hh.ru.
- Если `vacancy-response-pack` выигрывает, MVP строим вокруг конкретной вакансии и отклика.
- Если все офферы слабые, меняем сегмент или боль: например, трекер откликов, анти-фильтр резюме, career coach assistant.

## Тексты для ручного outreach

Операторская панель `#hh-booster` содержит блок `Ссылки и тексты`:

- канальные ссылки для `hh.ru`, `Telegram`, `VK`, `Авито Работа`, `Рекомендация`, `Другое`;
- готовый текст для карьерного чата;
- готовый текст для личного сообщения;
- готовый текст для VK/поста;
- кнопки копирования для ссылок и текстов.

Если публикуется внешний URL, заменить домен локальной ссылки на публичный домен, но сохранить hash и `channel`:

```text
https://PUBLIC_HOST/#hh-booster-public?channel=Telegram
```

### Telegram/VK карьерный чат

```text
Тестирую маленький сервис для соискателей на hh.ru: проверка фото, резюме и отклика перед отправкой работодателю.
Нужно 5 минут: выбрать, за какой формат вы реально готовы заплатить 199/399/799 ₽, и оставить контакт для ручного разбора.
Не обещаю "гарантированное приглашение", проверяем именно первое впечатление и качество отклика.
Ссылка: http://127.0.0.1:8787/#hh-booster-public?channel=Telegram
```

Для внешней аудитории локальную ссылку нужно заменить на публичный URL, reverse tunnel или проводить тест вживую с экрана. Не публиковать локальный `127.0.0.1` как внешнюю ссылку.

### Личное сообщение соискателю

```text
Привет. Я проверяю идею сервиса для hh.ru: фото + резюме + отклик под вакансию.
Можешь выбрать, какой формат тебе был бы реально полезен: только фото, аудит резюме или полный отклик под вакансию?
Это не продажа сейчас, мне важно понять, за что люди готовы платить.
```

## Daily checklist

- Сколько новых лидов сегодня?
- Есть ли data quality warnings/errors: QA/preflight, дубликаты, битые поля, consent?
- Сколько `Готов оплатить`?
- Что показывает daily outreach plan: какой оффер/канал/роль нужно добирать сегодня?
- Кому нужно написать первым в concierge follow-up?
- Какие исходы follow-up появились: подтвердил оплату, оплатил, отказался, не ответил?
- Сохранен ли daily snapshot без персональных данных?
- Какой текущий темп: лиды/день и paid intent/день?
- Сколько нужно добирать в день до конца 14-дневного окна?
- По каждому ли офферу набрано минимум 5 лидов?
- Какой оффер выбирали чаще?
- Какие профессии повторяются?
- Какие возражения звучали?
- Нужно ли менять цену или формулировку оффера?

## Data quality audit

Перед ежедневными метриками и перед финальным отчетом запускать read-only аудит качества данных:

```powershell
& "D:\AionUi-Paperclip\.venv-sml\Scripts\python.exe" "D:\AionUi-Paperclip\tools\hh_resume_booster_data_quality.py" "D:\AionUi-Paperclip\apps\aion-vision\data\hh-booster-leads.jsonl" --experiment-state "D:\AionUi-Paperclip\apps\aion-vision\data\hh-booster-experiment.json"
```

Строгий режим для финальной проверки:

```powershell
& "D:\AionUi-Paperclip\.venv-sml\Scripts\python.exe" "D:\AionUi-Paperclip\tools\hh_resume_booster_data_quality.py" "D:\AionUi-Paperclip\apps\aion-vision\data\hh-booster-leads.jsonl" --experiment-state "D:\AionUi-Paperclip\apps\aion-vision\data\hh-booster-experiment.json" --strict
```

Audit ничего не пишет. Он показывает:

- битые JSON/CSV/JSONL строки;
- неизвестные `offer`/`intent`;
- отсутствующие обязательные поля;
- дубликаты `id`;
- дубликаты контактов для ручной проверки;
- QA/preflight/test-like заявки;
- `createdAt` до старта или после конца эксперимента;
- `consentAccepted` не `true` для серверных заявок.

Если audit нашел QA/preflight или явный мусор, сначала использовать privacy/data-admin dry-run, затем `--write` только после проверки:

```powershell
& "D:\AionUi-Paperclip\.venv-sml\Scripts\python.exe" "D:\AionUi-Paperclip\tools\hh_resume_booster_data_admin.py" --id "LEAD_ID"
```

Рабочее правило: финальный decision report нельзя считать чистым, если strict audit падает.

## Daily outreach plan

Перед ручной обработкой заявок запускать read-only план добора:

```powershell
& "D:\AionUi-Paperclip\.venv-sml\Scripts\python.exe" "D:\AionUi-Paperclip\tools\hh_resume_booster_outreach_plan.py" "D:\AionUi-Paperclip\apps\aion-vision\data\hh-booster-leads.jsonl" --experiment-state "D:\AionUi-Paperclip\apps\aion-vision\data\hh-booster-experiment.json"
```

Если есть внешний URL:

```powershell
& "D:\AionUi-Paperclip\.venv-sml\Scripts\python.exe" "D:\AionUi-Paperclip\tools\hh_resume_booster_outreach_plan.py" "D:\AionUi-Paperclip\apps\aion-vision\data\hh-booster-leads.jsonl" --experiment-state "D:\AionUi-Paperclip\apps\aion-vision\data\hh-booster-experiment.json" --public-base-url "https://PUBLIC_HOST"
```

Planner ничего не пишет в JSONL. Он показывает:

- сколько лидов, paid intent, каналов, ролей и coverage еще не хватает;
- какой минимум лидов нужен сегодня;
- какие офферы недособраны;
- какие каналы еще не использовались;
- список конкретных next actions.

Рабочее правило: если planner показывает deficit по офферу, дневной outreach сначала направлять на этот оффер, даже если общий темп лидов выглядит нормальным.

## Outreach activity log

После ручной раздачи ссылок фиксировать, сколько outreach реально сделано. Это denominator для будущего сравнения: если у оффера мало paid intent, нужно понимать, его плохо выбрали пользователи или его просто мало показывали.

Dry-run:

```powershell
& "D:\AionUi-Paperclip\.venv-sml\Scripts\python.exe" "D:\AionUi-Paperclip\tools\hh_resume_booster_outreach_log.py" --state "D:\AionUi-Paperclip\apps\aion-vision\data\hh-booster-outreach.jsonl" --leads "D:\AionUi-Paperclip\apps\aion-vision\data\hh-booster-leads.jsonl" add --channel Telegram --type direct_message --offer response --messages-sent 10 --audience-count 10 --note "no personal data"
```

Запись:

```powershell
& "D:\AionUi-Paperclip\.venv-sml\Scripts\python.exe" "D:\AionUi-Paperclip\tools\hh_resume_booster_outreach_log.py" --state "D:\AionUi-Paperclip\apps\aion-vision\data\hh-booster-outreach.jsonl" --leads "D:\AionUi-Paperclip\apps\aion-vision\data\hh-booster-leads.jsonl" add --channel Telegram --type direct_message --offer response --messages-sent 10 --audience-count 10 --note "no personal data" --write
```

Summary:

```powershell
& "D:\AionUi-Paperclip\.venv-sml\Scripts\python.exe" "D:\AionUi-Paperclip\tools\hh_resume_booster_outreach_log.py" --state "D:\AionUi-Paperclip\apps\aion-vision\data\hh-booster-outreach.jsonl" --leads "D:\AionUi-Paperclip\apps\aion-vision\data\hh-booster-leads.jsonl" summary
```

В `note` нельзя писать контакты, ФИО, ссылки на резюме или личные детали кандидата. Журнал хранит только канал, тип активности, фокус-оффер, количество отправок/охват и неперсональную заметку.

## Concierge packet

Ежедневно после outreach plan сначала собрать copy-ready пакет для ручной обработки. Он читает `hh-booster-leads.jsonl`, учитывает `hh-booster-followups.jsonl`, по умолчанию маскирует контакты, расставляет приоритеты `P0/P1`, генерирует первое сообщение под выбранный оффер и дает команды, которыми затем отметить исход:

```powershell
& "D:\AionUi-Paperclip\.venv-sml\Scripts\python.exe" "D:\AionUi-Paperclip\tools\hh_resume_booster_concierge_packet.py" "D:\AionUi-Paperclip\apps\aion-vision\data\hh-booster-leads.jsonl"
```

Для реальной ручной обработки можно открыть контакты и получить Markdown-пакет:

```powershell
& "D:\AionUi-Paperclip\.venv-sml\Scripts\python.exe" "D:\AionUi-Paperclip\tools\hh_resume_booster_concierge_packet.py" "D:\AionUi-Paperclip\apps\aion-vision\data\hh-booster-leads.jsonl" --intent ready --show-contact --markdown
```

Правило приватности: `--show-contact` использовать только в момент реального follow-up. Не сохранять Markdown с открытыми контактами в `docs/` или SML.

## Concierge follow-up queue

Ежедневно после проверки метрик запускать read-only очередь ручной обработки лидов:

```powershell
& "D:\AionUi-Paperclip\.venv-sml\Scripts\python.exe" "D:\AionUi-Paperclip\tools\hh_resume_booster_followup_queue.py" "D:\AionUi-Paperclip\apps\aion-vision\data\hh-booster-leads.jsonl"
```

По умолчанию очередь:

- ничего не пишет и не меняет в JSONL;
- показывает только `ready` и `maybe`;
- сортирует сначала `Готов оплатить`, затем `Интересно`;
- маскирует контакты;
- показывает короткую подсказку следующего ручного действия.

Для реального контакта с кандидатами явно раскрыть контакт:

```powershell
& "D:\AionUi-Paperclip\.venv-sml\Scripts\python.exe" "D:\AionUi-Paperclip\tools\hh_resume_booster_followup_queue.py" "D:\AionUi-Paperclip\apps\aion-vision\data\hh-booster-leads.jsonl" --intent ready --show-contact
```

Полезные фильтры:

```powershell
& "D:\AionUi-Paperclip\.venv-sml\Scripts\python.exe" "D:\AionUi-Paperclip\tools\hh_resume_booster_followup_queue.py" "D:\AionUi-Paperclip\apps\aion-vision\data\hh-booster-leads.jsonl" --offer response --intent ready,maybe
& "D:\AionUi-Paperclip\.venv-sml\Scripts\python.exe" "D:\AionUi-Paperclip\tools\hh_resume_booster_followup_queue.py" "D:\AionUi-Paperclip\apps\aion-vision\data\hh-booster-leads.jsonl" --channel Telegram --days 2
& "D:\AionUi-Paperclip\.venv-sml\Scripts\python.exe" "D:\AionUi-Paperclip\tools\hh_resume_booster_followup_queue.py" "D:\AionUi-Paperclip\apps\aion-vision\data\hh-booster-leads.jsonl" --json
```

Рабочее правило: `ready + response` обрабатывать первым, потому что там можно быстрее проверить реальную готовность платить за пакет под вакансию. `maybe` использовать для уточнения возражения: цена, доверие к фото, непонимание пользы аудита или отсутствие срочного поиска работы.

## Daily snapshot

В конце каждого рабочего дня сохранять агрегированный снимок без контактов и персональных данных:

```powershell
& "D:\AionUi-Paperclip\.venv-sml\Scripts\python.exe" "D:\AionUi-Paperclip\tools\hh_resume_booster_daily_snapshot.py" "D:\AionUi-Paperclip\apps\aion-vision\data\hh-booster-leads.jsonl" --experiment-state "D:\AionUi-Paperclip\apps\aion-vision\data\hh-booster-experiment.json" --followup-state "D:\AionUi-Paperclip\apps\aion-vision\data\hh-booster-followups.jsonl" --outreach-state "D:\AionUi-Paperclip\apps\aion-vision\data\hh-booster-outreach.jsonl" --default-out --strict-data-quality
```

Если есть внешний URL, передать его для проверки `local_url_warning`:

```powershell
& "D:\AionUi-Paperclip\.venv-sml\Scripts\python.exe" "D:\AionUi-Paperclip\tools\hh_resume_booster_daily_snapshot.py" "D:\AionUi-Paperclip\apps\aion-vision\data\hh-booster-leads.jsonl" --experiment-state "D:\AionUi-Paperclip\apps\aion-vision\data\hh-booster-experiment.json" --followup-state "D:\AionUi-Paperclip\apps\aion-vision\data\hh-booster-followups.jsonl" --outreach-state "D:\AionUi-Paperclip\apps\aion-vision\data\hh-booster-outreach.jsonl" --public-base-url "https://PUBLIC_HOST" --default-out --strict-data-quality
```

Snapshot пишется в:

```text
D:\AionUi-Paperclip\apps\aion-vision\data\daily\
```

Он фиксирует метрики дня, data quality state/counts/blocking issues с маскированными контактами, outreach activity denominator, coverage, daily outreach plan actions и follow-up outcomes. Контакты и заметки кандидатов туда не попадают.

Если указан `--strict-data-quality`, snapshot все равно сохраняется, но команда возвращает exit code `2`, если audit нашел errors/warnings. В этом случае сначала очистить QA/preflight/test-like или битые строки через data-admin flow, затем повторить daily snapshot.

## Concierge follow-up outcomes

Очередь показывает, кому писать. Отдельный append-only state фиксирует, что произошло после ручного контакта:

```text
D:\AionUi-Paperclip\apps\aion-vision\data\hh-booster-followups.jsonl
```

Исходный `hh-booster-leads.jsonl` при этом не меняется.

После контакта с кандидатом сначала сделать dry-run:

```powershell
& "D:\AionUi-Paperclip\.venv-sml\Scripts\python.exe" "D:\AionUi-Paperclip\tools\hh_resume_booster_followup_state.py" --leads "D:\AionUi-Paperclip\apps\aion-vision\data\hh-booster-leads.jsonl" mark "LEAD_ID" --status contacted --note "короткая заметка без лишних персональных данных"
```

Записать событие в follow-up state:

```powershell
& "D:\AionUi-Paperclip\.venv-sml\Scripts\python.exe" "D:\AionUi-Paperclip\tools\hh_resume_booster_followup_state.py" --leads "D:\AionUi-Paperclip\apps\aion-vision\data\hh-booster-leads.jsonl" mark "LEAD_ID" --status confirmed_paid_intent --note "готов оплатить response pack после примера" --write
```

Статусы:

- `contacted` - написали кандидату;
- `responded` - кандидат ответил;
- `confirmed_paid_intent` - после диалога подтвердил готовность платить;
- `paid` - реально оплатил ручной разбор;
- `declined` - отказался;
- `no_response` - не ответил после разумного ожидания;
- `invalid` - контакт невалиден.

Сводка исходов:

```powershell
& "D:\AionUi-Paperclip\.venv-sml\Scripts\python.exe" "D:\AionUi-Paperclip\tools\hh_resume_booster_followup_state.py" --leads "D:\AionUi-Paperclip\apps\aion-vision\data\hh-booster-leads.jsonl" summary
```

Список последних статусов:

```powershell
& "D:\AionUi-Paperclip\.venv-sml\Scripts\python.exe" "D:\AionUi-Paperclip\tools\hh_resume_booster_followup_state.py" --leads "D:\AionUi-Paperclip\apps\aion-vision\data\hh-booster-leads.jsonl" list
```

Очередь follow-up автоматически читает `hh-booster-followups.jsonl` и скрывает закрытые лиды (`paid`, `declined`, `no_response`, `invalid`). Чтобы посмотреть все, включая закрытые:

```powershell
& "D:\AionUi-Paperclip\.venv-sml\Scripts\python.exe" "D:\AionUi-Paperclip\tools\hh_resume_booster_followup_queue.py" "D:\AionUi-Paperclip\apps\aion-vision\data\hh-booster-leads.jsonl" --include-closed
```

Для финального решения primary gate: 14 дней, 30+ лидов, 10+ `Готов оплатить`, 2+ канала, 5+ ролей и минимум 5 лидов по каждому офферу. Follow-up outcomes используются как более сильное качество сигнала: если первичный `ready` высокий, но `confirmed_paid_intent/paid` слабый, оффер требует перепозиционирования или другой цены.
Дополнительный coverage gate: каждый из трех офферов должен набрать минимум 5 лидов. Если один оффер недособран, финальный winner считается преждевременным даже при выполнении общего порога 30 лидов.

## Ежедневный учет в интерфейсе

Экран `#hh-booster` показывает:

- лиды сегодня;
- `Готов оплатить` сегодня;
- средний темп по активным дням;
- сколько лидов и paid intent нужно добирать в день до конца теста;
- таблицу последних 7 дней с разбивкой по трем офферам.

Кнопка `JSON` выгружает полный снимок: заявки, состояние эксперимента, gate progress, метрики по офферам и дневную агрегацию. Кнопка `CSV` выгружает только заявки в табличном виде для ручной проверки.

Кнопка `Сервер` в операторской панели подтягивает последние заявки из `GET /api/hh-booster/leads?limit=5000`, experiment state из `GET /api/hh-booster/experiment`, объединяет заявки с текущим `localStorage` по `id` и пересчитывает все метрики в панели.

## Видимый daily status

Разовый статус server JSONL и experiment state:

```powershell
& "D:\AionUi-Paperclip\apps\aion-vision\scripts\watch-hh-booster-test.ps1"
```

Если уже есть внешний URL, передать его в monitor, чтобы видеть day-0 launch checklist:

```powershell
& "D:\AionUi-Paperclip\apps\aion-vision\scripts\watch-hh-booster-test.ps1" -OperatorBaseUrl "http://127.0.0.1:8787" -PublicBaseUrl "https://REAL_PUBLIC_HOST"
```

Видимый monitor с обновлением раз в минуту:

```powershell
& "D:\AionUi-Paperclip\apps\aion-vision\scripts\watch-hh-booster-test.ps1" -Watch -IntervalSeconds 60
```

Monitor ничего не пишет и не запускает сервер. Он показывает:

- создан ли `hh-booster-experiment.json`;
- существует ли `hh-booster-leads.jsonl`;
- задан ли реальный public URL;
- для temporary tunnel - есть ли свежая successful day-0 rehearsal metadata для этого public URL и не протухло ли freshness-окно;
- сохранен ли launch manifest;
- нажата ли кнопка `Старт теста`;
- сколько строк/байт и когда была последняя запись;
- прогресс gate: лиды, paid intent, каналы, роли, день теста, `decision_ready`;
- coverage gate: минимум лидов по каждому из трех офферов;
- текущий темп и сколько нужно добирать в день;
- paid intent по офферам и последние дни.

## Риски

- Фото и резюме являются персональными данными. Для публичного запуска нужен privacy/delete policy.
- В текущем concierge-тесте форма собирает только контакт, профессию, намерение платить, канал и текстовый контекст. Фото/резюме не загружать в эту форму.
- Минимальный delete policy: если участник просит удалить заявку через указанный контакт, удалить строку из server JSONL или очистить соответствующую запись в экспортной таблице перед анализом.
- Нельзя автоматически входить в hh.ru, скрейпить или массово откликаться без отдельной юридической проверки.
- Нельзя обещать гарантированный рост приглашений без данных.
- Overedited photo может ухудшить доверие работодателя.

## Privacy/delete операции

Перед изменением server JSONL всегда делать dry-run. По контакту:

```powershell
& "D:\AionUi-Paperclip\.venv-sml\Scripts\python.exe" "D:\AionUi-Paperclip\tools\hh_resume_booster_data_admin.py" --contact "CONTACT_OR_TELEGRAM"
```

По `id` заявки:

```powershell
& "D:\AionUi-Paperclip\.venv-sml\Scripts\python.exe" "D:\AionUi-Paperclip\tools\hh_resume_booster_data_admin.py" --id "LEAD_ID"
```

Удалить строку из server JSONL с backup:

```powershell
& "D:\AionUi-Paperclip\.venv-sml\Scripts\python.exe" "D:\AionUi-Paperclip\tools\hh_resume_booster_data_admin.py" --contact "CONTACT_OR_TELEGRAM" --action delete --write
```

Альтернатива, если нужно сохранить агрегатную строку для метрик, но удалить контакт и заметки:

```powershell
& "D:\AionUi-Paperclip\.venv-sml\Scripts\python.exe" "D:\AionUi-Paperclip\tools\hh_resume_booster_data_admin.py" --contact "CONTACT_OR_TELEGRAM" --action redact --write
```

Инструмент по умолчанию не пишет файл, маскирует контакт в выводе и при `--write` создает backup в `apps/aion-vision/data/backups/`.

## Команда подсчета

После экспорта JSON:

```powershell
& "D:\AionUi-Paperclip\.venv-sml\Scripts\python.exe" "D:\AionUi-Paperclip\tools\hh_resume_booster_metrics.py" "C:\path\to\hh-resume-booster-leads-2026-06-21.json"
```

CLI также принимает CSV из интерфейса:

```powershell
& "D:\AionUi-Paperclip\.venv-sml\Scripts\python.exe" "D:\AionUi-Paperclip\tools\hh_resume_booster_metrics.py" "C:\path\to\hh-resume-booster-leads-2026-06-21.csv"
```

CLI также принимает серверный JSONL:

```powershell
& "D:\AionUi-Paperclip\.venv-sml\Scripts\python.exe" "D:\AionUi-Paperclip\tools\hh_resume_booster_metrics.py" "D:\AionUi-Paperclip\apps\aion-vision\data\hh-booster-leads.jsonl"
```

Для server JSONL CLI автоматически ищет соседний файл:

```text
D:\AionUi-Paperclip\apps\aion-vision\data\hh-booster-experiment.json
```

Если experiment state лежит в другом месте, передать его явно:

```powershell
& "D:\AionUi-Paperclip\.venv-sml\Scripts\python.exe" "D:\AionUi-Paperclip\tools\hh_resume_booster_metrics.py" "D:\AionUi-Paperclip\apps\aion-vision\data\hh-booster-leads.jsonl" --experiment-state "C:\path\to\hh-booster-experiment.json"
```

Для машинного вывода:

```powershell
& "D:\AionUi-Paperclip\.venv-sml\Scripts\python.exe" "D:\AionUi-Paperclip\tools\hh_resume_booster_metrics.py" "C:\path\to\export.json" --json
```

`decision_ready=true` валиден только если одновременно выполнены пороги лидов, paid intent, каналов, ролей, per-offer coverage и `days_complete=true`.

## Финальный decision report

После 14 дней и выполнения всех gate-порогов сгенерировать финальный Markdown-отчет:

```powershell
& "D:\AionUi-Paperclip\.venv-sml\Scripts\python.exe" "D:\AionUi-Paperclip\tools\hh_resume_booster_decision_report.py" "D:\AionUi-Paperclip\apps\aion-vision\data\hh-booster-leads.jsonl" --followup-state "D:\AionUi-Paperclip\apps\aion-vision\data\hh-booster-followups.jsonl" --out "D:\AionUi-Paperclip\apps\aion-vision\data\hh-booster-decision-report.md"
```

Строгий режим вернет exit code `2`, если gate еще не готов или встроенный data quality audit нашел errors/warnings. Для черновика до завершения теста:

```powershell
& "D:\AionUi-Paperclip\.venv-sml\Scripts\python.exe" "D:\AionUi-Paperclip\tools\hh_resume_booster_decision_report.py" "D:\AionUi-Paperclip\apps\aion-vision\data\hh-booster-leads.jsonl" --followup-state "D:\AionUi-Paperclip\apps\aion-vision\data\hh-booster-followups.jsonl" --draft --out "D:\AionUi-Paperclip\apps\aion-vision\data\hh-booster-decision-draft.md"
```

Decision report фиксирует:

- `ready` / `not_ready`;
- blockers, если gate не пройден;
- таблицу gate-порогов;
- встроенный `Data Quality` блок с errors/warnings/issue counts;
- таблицу coverage по каждому офферу;
- paid intent по трем офферам;
- follow-up outcomes по трем офферам: tracked, confirmed paid intent, paid, declined, open;
- текущего winner;
- продуктовый вывод: аватарка как самостоятельный front-offer, лид-магнит/модуль, MVP вокруг аудита резюме или MVP вокруг отклика под вакансию.

Если `--followup-state` не передан, CLI автоматически ищет соседний файл `hh-booster-followups.jsonl` рядом с `hh-booster-leads.jsonl`. Primary decision gate все равно считается по первичному paid intent из формы с учетом per-offer coverage, а follow-up outcomes используются как quality signal: подтверждают, усиливают или ставят под сомнение выбранный оффер.

Даже если все количественные gate-пороги пройдены, `Status: ready` невозможен при нечистом data quality audit. Сначала удалить или отредактировать QA/preflight/test-like заявки через data-admin dry-run/write flow, затем перезапустить report.
