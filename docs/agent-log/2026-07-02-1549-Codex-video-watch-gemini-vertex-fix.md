# 2026-07-02 15:49 +03 - Codex - video-watch Gemini/Vertex recovery

## Исходный запрос
Пользователь попросил перестать вести его по Google Cloud UI вручную и сделать настройку Gemini для video-watch самостоятельно.

## Краткий план
- Найти или поставить Google Cloud CLI без админского установщика.
- Авторизовать `gcloud` и ADC.
- Включить нужные API в проекте `project-4a65d058-0aed-49b3-8b8`.
- Создать service-account-bound API key без вывода секрета.
- Проверить Gemini/OpenAI/Newton live health.
- Если Gemini API key route заблокирован, включить рабочий Vertex AI fallback.

## Что сделано
- Установлен portable Google Cloud SDK 575.0.0 в `C:\Users\koval\.local\google-cloud-sdk-575`.
- `gcloud auth login` выполнен для `koval26vlg@gmail.com`.
- Активный проект установлен: `project-4a65d058-0aed-49b3-8b8`.
- Включены API:
  - `serviceusage.googleapis.com`
  - `apikeys.googleapis.com`
  - `generativelanguage.googleapis.com`
  - `aiplatform.googleapis.com`
- Создан API key `video-watch-gemini`, uid `971a9eb3-8572-4842-94b4-92d09943f76e`, ограничение `generativelanguage.googleapis.com`, привязка к service account `790608621898-compute@developer.gserviceaccount.com`. Значение ключа не печаталось.
- Ключ сохранен в Windows User env как `GEMINI_API_KEY` и `GOOGLE_API_KEY`.
- Выполнен `gcloud auth application-default login`; ADC сохранен штатно, quota project привязан к `project-4a65d058-0aed-49b3-8b8`.
- В Windows User env добавлены не секретные `GOOGLE_CLOUD_PROJECT=project-4a65d058-0aed-49b3-8b8` и `GOOGLE_CLOUD_LOCATION=us-central1`.
- `agent-skills/video-watch` обновлен:
  - `check-video-stack.ps1` показывает `gcloud`, `GOOGLE_CLOUD_PROJECT`, `GOOGLE_CLOUD_LOCATION`, отдельную строку `Vertex Gemini`.
  - `watch-video.ps1` подтягивает project/location и active `gcloud` project.
  - `watch_video.py` сначала пробует Gemini API key URL, затем fallback `vertex-gemini-url` через Google ADC.
  - `training_pack.md` теперь учитывает `vertex_gemini_analysis.md`.
- Обновления синхронизированы в:
  - `C:\Users\koval\.codex\skills\video-watch`
  - `C:\Users\koval\.agents\skills\video-watch`
  - `C:\Users\koval\.claude\skills\video-watch`

## Проверки
- SHA256 portable SDK проверен перед распаковкой.
- `gcloud --version` показал Google Cloud SDK 575.0.0.
- `check-video-stack.ps1 -CheckNewtonHealth -CheckApiHealth`:
  - OpenAI OK, status 200, models 112.
  - Newton health OK.
  - Gemini API key route blocked: 429 `free_tier_quota_or_billing`, limit 0 / prepay depleted.
  - Vertex Gemini OK, status 200, project `project-4a65d058-0aed-49b3-8b8`, location `us-central1`, model `gemini-2.5-flash`.
- Реальный `watch-video` smoke:
  - Source: `https://www.youtube.com/watch?v=So3srrfKiWg`
  - Command: `watch-video.ps1 -Backend gemini -NoFrames`
  - `gemini-api-key-url` заблокирован 429 prepay depleted.
  - `vertex-gemini-url` OK.
  - Артефакты: `C:\Users\koval\Documents\Команда\artifacts\video-watch\20260702-154337-www.youtube.com-watch-v-so3srrfkiwg`
  - `vertex_gemini_analysis.md` создан, `training_pack.md` пересобран и видит native video analysis.

## Риски и ограничения
- Gemini API key route остается нерабочим из-за AI Studio/Gemini API prepay/quota, несмотря на созданный ключ и GCP free trial billing. Рабочий путь для video-watch сейчас Vertex AI через ADC.
- Для новых процессов Codex/Claude/Antigravity иногда нужен перезапуск, чтобы они унаследовали свежие User env.
- Значения ключей, токенов и ADC не печатались и не должны попадать в логи.

## Следующий агент
Использовать Vertex Gemini route как основной Gemini fallback для video-watch. Если нужна именно Gemini API key billing route, отдельно пополнить/активировать AI Studio prepay/paid plan; но для текущей задачи рабочий production path уже есть через Vertex/ADC.
