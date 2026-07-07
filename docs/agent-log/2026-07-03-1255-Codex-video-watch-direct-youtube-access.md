# 2026-07-03 12:55 +03 - Codex - video-watch direct YouTube access

## Исходный запрос

Продолжить активную цель: довести расшифровку YouTube/video-watch и доступы `OPENAI_API_KEY`, `GEMINI_API_KEY`, `GOOGLE_API_KEY`, `NEWTON_TOKEN`, с приоритетом прямого доступа к YouTube.

## План

- Проверить текущий `video-watch` skill и verifier.
- Исправить прямой YouTube video/frame path так, чтобы smoke не запускал скрытый полный download.
- Добавить отдельный direct audio smoke без OpenAI/Whisper transcription spend.
- Проверить все основные слои access verifier.
- Синхронизировать Codex/.agents/Claude skill roots.

## Сделано

- `agent-skills/video-watch/scripts/watch_video.py`:
  - добавлен `--download-audio-only` для проверки прямого YouTube audio download без транскрибации;
  - bounded `--download-sections` frame smoke больше не делает silent full-video fallback;
  - frame extraction теперь использует scene detection first, а при 0 кадров делает interval fallback `fps=1/2`;
  - `frames_manifest.json` теперь содержит реальные кадры даже на статичном начале клипа.
- `agent-skills/video-watch/scripts/watch-video.ps1`:
  - добавлен `-DownloadAudioOnly`.
- `agent-skills/video-watch/scripts/verify-video-access.ps1`:
  - добавлен `-RunDirectAudioSmoke`;
  - прямые smoke checks разделены на subtitles, audio, frames.
- `agent-skills/video-watch/SKILL.md` обновлен: direct audio smoke, bounded frame policy, interval fallback.
- Создан `agent-skills/video-watch/ACCESS_STATUS.md` с текущей картой доступа и командами проверки.
- Все изменения синхронизированы в:
  - `C:\Users\koval\.codex\skills\video-watch`
  - `C:\Users\koval\.agents\skills\video-watch`
  - `C:\Users\koval\.claude\skills\video-watch`

## Проверки

- `C:\Program Files\Python313\python.exe -m py_compile .\agent-skills\video-watch\scripts\watch_video.py`: OK.
- `verify-video-access.ps1 -Json`:
  - `direct-youtube-tools=True`
  - `youtube-impersonation=True`
  - `openai-api=True` (`/v1/models`, not transcription quota)
  - `gemini-api-key=False`, `429 free_tier_quota_or_billing`
  - `vertex-gemini=True`, `gemini-2.5-flash`, `us-central1`
  - `newton-health=True`
  - `local-whisper=True`
- `verify-video-access.ps1 -CheckNewtonFetch -RunDirectYouTubeSmoke -RunDirectAudioSmoke -RunDirectFrameSmoke`:
  - direct subtitles OK: `C:\Users\koval\Documents\Команда\artifacts\video-watch\20260703-125329-www.youtube.com-watch-v-so3srrfkiwg\training_pack.md`
  - direct audio OK: `C:\Users\koval\Documents\Команда\artifacts\video-watch\20260703-125336-www.youtube.com-watch-v-so3srrfkiwg\training_pack.md`
  - direct frames OK: `C:\Users\koval\Documents\Команда\artifacts\video-watch\20260703-125350-www.youtube.com-watch-v-so3srrfkiwg\training_pack.md`
  - Newton fetch failed: HTTP `401 Invalid token`.
- Hash verification: `SKILL.md`, `ACCESS_STATUS.md`, `watch_video.py`, `watch-video.ps1`, `verify-video-access.ps1` match across shared/Codex/.agents/Claude roots.
- Process check: no leftover `watch-video`, `watch_video`, `verify-video-access`, `yt-dlp`, or `ffmpeg` processes.

## Текущий статус

Прямой YouTube path теперь рабочий для:

- captions/subtitles;
- audio download;
- bounded video section download;
- local frame extraction.

Практический production route для анализа:

- direct YouTube subtitles/audio/frames first;
- Vertex Gemini through ADC for native video analysis;
- local Whisper fallback when OpenAI transcription quota is unavailable.

## Остаточные ограничения

- `NEWTON_TOKEN` есть, но `newton fetch` возвращает HTTP `401 Invalid token`; нужен новый/валидный Newton token, если нужен именно Newton backend.
- `GEMINI_API_KEY`/`GOOGLE_API_KEY` есть, но Gemini API-key `generateContent` остается blocked by `429 free_tier_quota_or_billing`; рабочий Gemini route сейчас Vertex/ADC.
- `OPENAI_API_KEY` проходит `/v1/models`, но OpenAI transcription ранее возвращал quota blocker; для ASR без OpenAI использовать local Whisper.

## Следующий агент

Не возвращаться к ручному Google Cloud UI для базового video-watch. Использовать `agent-skills/video-watch/ACCESS_STATUS.md` и `verify-video-access.ps1`. Для длинных видео/полного download/transcription соблюдать visible-run rule.
