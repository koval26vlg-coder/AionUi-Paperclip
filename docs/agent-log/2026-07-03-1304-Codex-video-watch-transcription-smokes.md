# 2026-07-03 13:04 +03 - Codex - video-watch transcription smokes

## Исходный запрос

Продолжить активную цель по YouTube video transcription/access через `OPENAI_API_KEY`, `GEMINI_API_KEY`, `GOOGLE_API_KEY`, `NEWTON_TOKEN`, с приоритетом прямого доступа к YouTube.

## План

- Добавить bounded YouTube audio segment для коротких проверок транскрибации.
- Добавить выбор transcription route: `auto`, `openai`, `local`.
- Добавить verifier smoke для local Whisper и OpenAI transcription endpoint.
- Проверить результат и синхронизировать skill roots.

## Сделано

- `agent-skills/video-watch/scripts/watch_video.py`:
  - `try_ytdlp_audio_download` теперь принимает `section_seconds`;
  - добавлены CLI flags `--audio-download-seconds` и `--transcription-route auto|openai|local`;
  - URL transcription path может принудительно использовать local Whisper без OpenAI;
  - command output sanitizer теперь редактирует signed `googlevideo.com/videoplayback?...` URL перед записью в metadata.
- `agent-skills/video-watch/scripts/watch-video.ps1`:
  - добавлены `-AudioDownloadSeconds` и `-TranscriptionRoute`.
- `agent-skills/video-watch/scripts/verify-video-access.ps1`:
  - добавлен `-RunLocalTranscriptionSmoke`;
  - добавлен `-RunOpenAITranscriptionSmoke`.
- `agent-skills/video-watch/SKILL.md` и `ACCESS_STATUS.md` обновлены.
- Изменения синхронизированы в `.codex`, `.agents`, `.claude`; хэши совпадают.

## Проверки

- `C:\Program Files\Python313\python.exe -m py_compile .\agent-skills\video-watch\scripts\watch_video.py`: OK.
- `verify-video-access.ps1 -RunLocalTranscriptionSmoke`:
  - direct YouTube 12-sec audio segment download OK;
  - local faster-whisper transcript OK;
  - artifact: `C:\Users\koval\Documents\Команда\artifacts\video-watch\20260703-130001-www.youtube.com-watch-v-so3srrfkiwg\training_pack.md`;
  - transcript exists and starts with timestamped Russian text.
- `verify-video-access.ps1 -RunOpenAITranscriptionSmoke`:
  - direct YouTube 12-sec audio segment download OK;
  - OpenAI transcription failed with `RateLimitError 429 insufficient_quota`;
  - artifact: `C:\Users\koval\Documents\Команда\artifacts\video-watch\20260703-130133-www.youtube.com-watch-v-so3srrfkiwg\training_pack.md`.
- `verify-video-access.ps1 -RunDirectAudioSmoke` after sanitizer:
  - direct audio OK;
  - new metadata contains `<redacted-googlevideo-videoplayback-url>` and does not contain raw `googlevideo.com/videoplayback?`.
- Process check: no leftover `watch-video`, `watch_video`, `verify-video-access`, `yt-dlp`, or `ffmpeg` processes.

## Текущий статус

Working:

- direct YouTube subtitles/audio/video section/frames;
- YouTube -> bounded audio segment -> local Whisper transcript;
- Vertex Gemini through ADC;
- OpenAI `/v1/models`;
- local Whisper fallback.

Blocked externally:

- OpenAI transcription endpoint: `429 insufficient_quota`;
- Newton fetch: HTTP `401 Invalid token`;
- Gemini API-key `generateContent`: `429 free_tier_quota_or_billing`.

## Следующий агент

Use `ACCESS_STATUS.md` as current status. For real YouTube transcription without OpenAI quota, use:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File .\agent-skills\video-watch\scripts\watch-video.ps1 -Source "<youtube-url>" -Backend local -TranscriptionRoute local -NoFrames -SkipNativeVideoAnalysis
```

For short smoke:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File .\agent-skills\video-watch\scripts\verify-video-access.ps1 -RunLocalTranscriptionSmoke
```
