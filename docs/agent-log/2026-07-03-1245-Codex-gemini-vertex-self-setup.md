# 2026-07-03 12:45 +03 - Codex - Gemini/Vertex self setup

## Исходный запрос

Пользователь попросил перестать вести его по Google Cloud UI и сделать настройку самостоятельно.

## План

- Проверить фактический активный Google Cloud project через `gcloud`.
- Проверить billing, enabled APIs, API keys, service account и ADC.
- Сохранить рабочие переменные окружения без печати секретов.
- Проверить live API/Vertex health.
- Закрепить рабочий route в `video-watch` skill.

## Сделано

- Найден реальный `gcloud`: `C:\Users\koval\.local\google-cloud-sdk-575\google-cloud-sdk\bin\gcloud.cmd`.
- Подтвержден активный account: `koval26vlg@gmail.com`.
- Подтвержден активный project: `project-4a65d058-0aed-49b3-8b8` (`My First Project`, number `790608621898`).
- Billing на проекте включен: `billingAccounts/01890D-228A11-202E4B`.
- Подтверждены enabled APIs: `aiplatform.googleapis.com`, `apikeys.googleapis.com`, `generativelanguage.googleapis.com`, `iam.googleapis.com`, `serviceusage.googleapis.com`.
- Найден существующий API key `video-watch-gemini`, uid `971a9eb3-8572-4842-94b4-92d09943f76e`, restricted to `generativelanguage.googleapis.com`.
- Значение ключа получено через `gcloud services api-keys get-key-string` и сохранено в Windows User env как `GEMINI_API_KEY` и `GOOGLE_API_KEY`; значение не печаталось.
- ADC quota project установлен на `project-4a65d058-0aed-49b3-8b8`.
- Windows User env обновлены:
  - `GOOGLE_CLOUD_PROJECT=project-4a65d058-0aed-49b3-8b8`
  - `GOOGLE_CLOUD_LOCATION=us-central1`
  - `GOOGLE_GENAI_USE_VERTEXAI=true`
- `video-watch` обновлен: в `auto` route теперь предпочитает Vertex/ADC, если задан `GOOGLE_CLOUD_PROJECT`; Gemini API key остается fallback/diagnostic route.
- Исправлена частичная правка direct-frame path: Python parser теперь принимает `--frame-download-max-height`, wrapper передает `-NativeVideoRoute`.
- Обновления синхронизированы в:
  - `agent-skills\video-watch`
  - `C:\Users\koval\.codex\skills\video-watch`
  - `C:\Users\koval\.agents\skills\video-watch`
  - `C:\Users\koval\.claude\skills\video-watch`

## Проверки

- `gcloud billing projects describe project-4a65d058-0aed-49b3-8b8`: billing enabled.
- `gcloud services api-keys list`: key `video-watch-gemini` exists.
- `check-video-stack.ps1 -CheckApiHealth`:
  - OpenAI models endpoint OK.
  - Gemini API key `generateContent` still returns `429 free_tier_quota_or_billing`.
  - Vertex Gemini OK: `gemini-2.5-flash`, `us-central1`, project `project-4a65d058-0aed-49b3-8b8`.
- `verify-video-access.ps1`: Vertex Gemini OK; API-key route still blocked by quota/billing tier.
- `C:\Program Files\Python313\python.exe -m py_compile .\agent-skills\video-watch\scripts\watch_video.py`: OK.
- Short YouTube smoke without native model:
  `watch-video.ps1 -Source https://www.youtube.com/watch?v=So3srrfKiWg -Backend auto -NoFrames -SkipNativeVideoAnalysis`
  created `C:\Users\koval\Documents\Команда\artifacts\video-watch\20260703-124316-www.youtube.com-watch-v-so3srrfkiwg\training_pack.md`.
- Hash verification confirmed synced files are identical across shared/Codex/.agents/Claude roots.

## Риски и ограничения

- Google Developer API-key route remains blocked by `generate_content_free_tier_* limit=0`. This is not fixed by local CLI once billing and key exist; it likely requires Google AI Studio paid tier/project eligibility propagation or full billing upgrade.
- Vertex/ADC route is the working route and should be used by default for video/native model analysis.
- A full native YouTube smoke was started hidden and exceeded the tool timeout; its leftover `pwsh/python` processes were identified and stopped. Do not use hidden long native video runs; use visible-run policy for long media analysis.

## Следующий агент

Use Vertex/ADC first for Gemini work. Do not send the user back through API-key UI unless specifically troubleshooting Google AI Studio paid tier. For video analysis, use `video-watch` and verify with `verify-video-access.ps1`; treat `vertex-gemini=True` as sufficient for native video model availability.
