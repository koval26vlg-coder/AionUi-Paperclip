# 2026-07-03 12:24 +03 - Codex - video-watch access verifier and repair helper

## Исходный запрос
Продолжить цель по расшифровке YouTube и доступам через `OPENAI_API_KEY`, `GEMINI_API_KEY`, `GOOGLE_API_KEY`, `NEWTON_TOKEN`, с приоритетом прямого доступа к YouTube.

## Краткий план
- Не считать цель закрытой из-за внешних блокеров.
- Добавить явный verifier/repair слой, чтобы после обновления ключей можно было быстро доказать, какой backend работает.
- Проверить verifier на реальном YouTube smoke.
- Синхронизировать skill roots.

## Что сделано
- `agent-skills/video-watch/scripts/set-video-api-keys.ps1` расширен:
  - новый флаг `-NewtonOnly`;
  - скрытый ввод `NEWTON_TOKEN`;
  - сохранение в Windows User env и Process env;
  - выводит только present/length/format_ok, без значения токена.
- Добавлен `agent-skills/video-watch/scripts/verify-video-access.ps1`:
  - проверяет direct YouTube tools (`yt-dlp`, `ffmpeg`, `deno`);
  - проверяет impersonation fallback (`curl_cffi`, `brotli`);
  - проверяет OpenAI `/v1/models`;
  - проверяет Gemini API key `generateContent`;
  - проверяет Vertex Gemini через ADC;
  - проверяет Newton health;
  - опционально проверяет Newton YouTube fetch через `-CheckNewtonFetch`;
  - опционально запускает direct subtitle smoke через `-RunDirectYouTubeSmoke`;
  - опционально запускает full auto smoke через `-RunFullAutoSmoke`;
  - поддерживает `-Json`.
- `SKILL.md` обновлен командами verifier и hidden token setter.
- Все изменения синхронизированы в:
  - `C:\Users\koval\.codex\skills\video-watch`
  - `C:\Users\koval\.agents\skills\video-watch`
  - `C:\Users\koval\.claude\skills\video-watch`

## Проверки
- `verify-video-access.ps1 -CheckNewtonFetch -RunDirectYouTubeSmoke`:
  - direct YouTube tools OK.
  - youtube impersonation OK.
  - OpenAI models endpoint OK.
  - Gemini API key generate blocked 429 quota/prepay.
  - Vertex Gemini OK.
  - Newton health OK.
  - Newton fetch failed 401 `Invalid token`.
  - direct YouTube subtitles smoke OK, artifact `C:\Users\koval\Documents\Команда\artifacts\video-watch\20260703-121913-www.youtube.com-watch-v-so3srrfkiwg\training_pack.md`.
- `verify-video-access.ps1 -RunFullAutoSmoke`:
  - full-auto-youtube OK.
  - artifact `C:\Users\koval\Documents\Команда\artifacts\video-watch\20260703-121948-www.youtube.com-watch-v-so3srrfkiwg\training_pack.md`.
  - attempts: `yt-dlp-subtitles=True`, `gemini-api-key-url=False`, `vertex-gemini-url=True`.

## Текущий статус
- Direct YouTube path: working.
- Vertex Gemini native video analysis: working.
- Local Whisper fallback: working.
- OpenAI key: valid, but transcription still needs billing/quota.
- Gemini API key route: present, but generation still blocked by quota/prepay.
- Newton: CLI/health working, current token invalid for fetch.

## Следующий агент
If the user provides a refreshed Newton token, run:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File .\agent-skills\video-watch\scripts\set-video-api-keys.ps1 -NewtonOnly
pwsh -NoProfile -ExecutionPolicy Bypass -File .\agent-skills\video-watch\scripts\verify-video-access.ps1 -CheckNewtonFetch -RunDirectYouTubeSmoke
```

If OpenAI billing/quota is fixed, run the verifier and optionally force:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File .\agent-skills\video-watch\scripts\watch-video.ps1 -Source "<youtube-url>" -Backend openai -NoFrames -SkipNativeVideoAnalysis
```
