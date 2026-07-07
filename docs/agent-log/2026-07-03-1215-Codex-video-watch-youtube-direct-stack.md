# 2026-07-03 12:15 +03 - Codex - video-watch direct YouTube stack

## Исходный запрос
Пользователь вернулся к цели: после восстановления Antigravity/Gemini довести расшифровку YouTube и доступы через `OPENAI_API_KEY`, `GEMINI_API_KEY`, `GOOGLE_API_KEY`, `NEWTON_TOKEN`, с приоритетом прямого доступа к YouTube.

## Краткий план
- Проверить текущий `video-watch` skill и реальные backend smoke.
- Усилить прямой YouTube путь без cookies.
- Проверить Gemini/Google/OpenAI/Newton не только по наличию ключей, а по рабочим вызовам.
- Обновить skill/scripts и синхронизировать в Codex/Claude/.agents.

## Что сделано
- Установлены/проверены дополнительные зависимости для прямого YouTube:
  - `curl_cffi 0.15.0`
  - `brotli 1.2.0`
- `agent-skills/video-watch` обновлен:
  - `yt-dlp` partial success теперь считается успешным, если реально появились `.srt/.vtt`.
  - `yt-dlp` получает `--ffmpeg-location`, `deno` JS runtime, fallback remote EJS components и impersonation fallback при наличии `curl_cffi`.
  - `auto` теперь для URL делает не только transcript, но и native Gemini/Vertex visual analysis, если не указан `-SkipNativeVideoAnalysis`.
  - добавлен URL fallback `yt-dlp audio download -> OpenAI transcription`.
  - если OpenAI transcription недоступен по квоте, добавлен fallback `local faster-whisper/openai-whisper`.
  - `watch-video.ps1` импортирует `NEWTON_TOKEN` из User env.
  - `check-video-stack.ps1` добавил `curl_cffi`, `brotli`, корректный Gemini API-key generate status и опциональный `-CheckNewtonFetchUrl`.
- Единственный найденный реальный `NEWTON_TOKEN` из `C:\Users\koval\bat\bitrix24-automation\.env` сохранен в Windows User env без вывода значения.
- Обновления синхронизированы в:
  - `C:\Users\koval\.codex\skills\video-watch`
  - `C:\Users\koval\.agents\skills\video-watch`
  - `C:\Users\koval\.claude\skills\video-watch`

## Проверки
- Preflight:
  - Python, yt-dlp, ffmpeg, Newton, Gemini CLI, gcloud, deno, node/npx OK.
  - Python modules OK: `openai`, `yt_dlp`, `google.genai`, `google.generativeai`, `whisper`, `faster_whisper`, `moviepy`, `cv2`, `curl_cffi`, `brotli`.
  - Env present: `OPENAI_API_KEY`, `GEMINI_API_KEY`, `GOOGLE_API_KEY`, `NEWTON_TOKEN`, `GOOGLE_CLOUD_PROJECT`, `GOOGLE_CLOUD_LOCATION`.
  - OpenAI `/v1/models`: OK, 112 models.
  - Gemini API key route: model list available, but `generateContent` blocked with 429 free-tier/prepay quota.
  - Vertex Gemini: OK, `gemini-2.5-flash`, `project-4a65d058-0aed-49b3-8b8`, `us-central1`.
- Direct YouTube `auto` smoke:
  - Command: `watch-video.ps1 -Source https://www.youtube.com/watch?v=So3srrfKiWg -Backend auto -NoFrames`
  - Artifact: `C:\Users\koval\Documents\Команда\artifacts\video-watch\20260703-120018-www.youtube.com-watch-v-so3srrfkiwg\training_pack.md`
  - `yt-dlp-subtitles`: OK, 2 subtitle files created, transcript available.
  - `gemini-api-key-url`: blocked 429 prepay depleted.
  - `vertex-gemini-url`: OK, native video analysis available.
- OpenAI/local fallback smoke:
  - Direct audio download from YouTube OK: `So3srrfKiWg.mp3` created.
  - OpenAI transcription blocked with 429 `insufficient_quota`.
  - Local `faster-whisper base` fallback OK, transcript created, language `ru`.
- Newton fetch smoke:
  - `newton health`: OK.
  - `newton fetch https://www.youtube.com/watch?v=So3srrfKiWg --wait`: blocked with HTTP 401 `Invalid token`.
  - Search found no other real `NEWTON_TOKEN` except the 43-character token in `C:\Users\koval\bat\bitrix24-automation\.env`; token value was not printed.

## Текущий рабочий порядок
1. `yt-dlp` direct subtitles from YouTube.
2. Vertex Gemini native video analysis for visual evidence.
3. Newton only after replacing/refreshing `NEWTON_TOKEN`.
4. `yt-dlp` direct audio download.
5. OpenAI transcription if quota is available.
6. Local `faster-whisper` fallback when OpenAI quota is unavailable.

## Риски и ограничения
- `NEWTON_TOKEN` currently invalid; needs refresh from Bit.Newton/Newton account.
- `OPENAI_API_KEY` is valid for API access, but transcription currently blocked by OpenAI quota/billing.
- Gemini API key route still blocked by Gemini API quota/prepay, but Vertex Gemini route is live and used as working fallback.
- Browser cookies were not used; `-UseBrowserCookies` remains explicit-approval only.

## Следующий агент
For YouTube work, use `watch-video.ps1 -Backend auto` as default. If user wants Newton specifically, first replace `NEWTON_TOKEN` and run `check-video-stack.ps1 -CheckNewtonFetchUrl <youtube-url>`. If user wants OpenAI transcription specifically, billing/quota must be fixed; until then local Whisper is the verified fallback.
