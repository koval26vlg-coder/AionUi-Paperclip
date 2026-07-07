# 2026-07-03 16:50 +03 — Codex — video-watch provider repair

## Исходный запрос

Пользователь попросил исправить оставшиеся blocked-части video-watch:

- OpenAI transcription требует billing/quota.
- Newton fetch требует новый валидный `NEWTON_TOKEN`.
- Gemini API-key route требует paid/quota eligibility; рабочий Gemini route сейчас Vertex/ADC.

## План

1. Повторно проверить фактический статус provider routes.
2. Поискать локальные альтернативные ключи/токены без вывода секретов.
3. Автоматизировать безопасный repair/doctor-flow для дальнейшей замены ключей.
4. Подтвердить Google Cloud project state через `gcloud`.
5. Синхронизировать skill во все roots и зафиксировать ограничения.

## Сделано

- Повторно выполнен `check-video-stack.ps1 -CheckApiHealth`.
- Повторно выполнен `verify-video-access.ps1 -CheckNewtonFetch -RunOpenAITranscriptionSmoke -Json`.
- Выполнен безопасный локальный поиск кандидатов `OPENAI_API_KEY`, `GEMINI_API_KEY`, `GOOGLE_API_KEY`, `NEWTON_TOKEN` с выводом только длины и SHA-256 fingerprint.
- Альтернативные рабочие секреты не найдены:
  - `NEWTON_TOKEN` найден только один, тот же fingerprint, fetch возвращает HTTP 401 `Invalid token`.
  - `BITNEWTON_TOKEN` как legacy-переменная Bitrix24 Automation проверен отдельно; отдельного реального токена не найдено, только placeholders/упоминания переменной.
  - `OPENAI_API_KEY` один валидный по формату, `/v1/models` OK, transcription smoke возвращает quota blocker.
  - `GEMINI_API_KEY`/`GOOGLE_API_KEY` один fingerprint, API-key `generateContent` возвращает 429 quota/free-tier.
- Проверен Google Cloud project:
  - active project `project-4a65d058-0aed-49b3-8b8`;
  - billing enabled;
  - enabled APIs: `aiplatform.googleapis.com`, `apikeys.googleapis.com`, `generativelanguage.googleapis.com`, `iam.googleapis.com`, `serviceusage.googleapis.com`;
  - API key `video-watch-gemini` exists and is restricted to `generativelanguage.googleapis.com`.
- Добавлен `agent-skills/video-watch/scripts/repair-video-provider-access.ps1`.
- Обновлены `SKILL.md`, `ACCESS_STATUS.md`, `set-video-api-keys.ps1`.
- Изменения синхронизированы в:
  - `agent-skills/video-watch`
  - `C:\Users\koval\.codex\skills\video-watch`
  - `C:\Users\koval\.agents\skills\video-watch`
  - `C:\Users\koval\.claude\skills\video-watch`

## Измененные файлы

- `agent-skills/video-watch/scripts/repair-video-provider-access.ps1`
- `agent-skills/video-watch/scripts/set-video-api-keys.ps1`
- `agent-skills/video-watch/SKILL.md`
- `agent-skills/video-watch/ACCESS_STATUS.md`
- synced copies under `.codex`, `.agents`, `.claude`

## Проверки

- `repair-video-provider-access.ps1` default run completed.
- `repair-video-provider-access.ps1 -Verify -CheckOpenAITranscription -Json` returned notes:
  - Vertex/ADC is the working Gemini route.
  - OpenAI models endpoint works but transcription smoke is quota-blocked.
  - Newton fetch auth returns HTTP 401 and needs token replacement.
- Sync hash check for changed files: all four roots matched.

## Риски и ограничения

- OpenAI billing/quota cannot be fixed by local code. A billed/quota-enabled OpenAI project key or account/project billing action is required.
- Newton CLI has no local `auth` command; `NEWTON_TOKEN` must be replaced from the Newton/Bit.Newton account/source.
- Gemini API-key route is project-configured locally but still quota-blocked. Production Gemini path is Vertex/ADC unless AI Studio API-key paid/quota eligibility is specifically needed.
- A separate visible ASR run under `C:\Users\koval\Documents\ОК.ру` was observed and intentionally not touched.

## Next

- For immediate video work use:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File .\agent-skills\video-watch\scripts\watch-video.ps1 -Source "<youtube-url>" -Backend auto
```

- To replace Newton token safely:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File .\agent-skills\video-watch\scripts\repair-video-provider-access.ps1 -SetNewton -Verify
```

- To replace OpenAI key safely with a manually available billed key:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File .\agent-skills\video-watch\scripts\repair-video-provider-access.ps1 -SetOpenAI -Verify -CheckOpenAITranscription
```
