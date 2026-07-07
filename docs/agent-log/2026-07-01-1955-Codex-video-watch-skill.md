# 2026-07-01 19:55 +03 - Codex - video-watch skill

## Исходный запрос

Пользователь уточнил, что задача не только в обучении сотрудников и не только в YouTube, а в полноценном качественном распознавании видео/аудио с использованием подходов из видео/PDF и дополнительных сильных способов.

## План

1. Создать универсальный локальный skill `video-watch`.
2. Поддержать гибридный pipeline: `yt-dlp` subtitles, Gemini URL, Newton, локальный OpenAI/Whisper/ffmpeg путь.
3. Добавить рабочие wrapper-скрипты и preflight.
4. Подключить skill через `agent-workflow-router`.
5. Проверить на проблемном YouTube URL.

## Что сделано

- Создан `video-watch` в shared `agent-skills` и синхронизирован в:
  - `C:\Users\koval\.codex\skills\video-watch`
  - `C:\Users\koval\.agents\skills\video-watch`
  - `C:\Users\koval\.claude\skills\video-watch`
- Добавлены:
  - `SKILL.md`
  - `scripts\check-video-stack.ps1`
  - `scripts\watch-video.ps1`
  - `scripts\watch_video.py`
- `agent-workflow-router` обновлен во всех четырех roots: media/video/audio tasks route через `video-watch`.
- Wrapper поддерживает `-Source` и alias `-Input`.
- Python pipeline сохраняет `metadata.json`, `training_pack.md`, subtitles/frames/model outputs при наличии.
- Добавлен fallback поиска исполняемых файлов по известным Windows-путям, чтобы не зависеть только от PATH.
- `yt-dlp` получает explicit JS runtime через Node.js, если Deno отсутствует.
- Newton backend читает `NEWTON_TOKEN` из env или локального `C:\Users\koval\bat\bitrix24-automation\.env` без печати секрета.

## Проверки

- `watch_video.py` проходит `py_compile`.
- PowerShell wrapper парсится.
- `check-video-stack.ps1 -CheckNewtonHealth` видит:
  - Python OK
  - `yt-dlp` OK
  - `ffmpeg` OK at `C:\ffmpeg\bin\ffmpeg.exe`
  - Newton OK
  - Node/npx OK
  - `NEWTON_TOKEN` present
  - Gemini/OpenAI API keys missing in current process
- Dry-run на `https://www.youtube.com/watch?v=So3srrfKiWg`:
  - `yt-dlp-subtitles` blocked by YouTube anti-bot
  - Gemini blocked by missing `GEMINI_API_KEY` / `GOOGLE_API_KEY`
  - Newton blocked because current CLI does not expose `fetch`
  - blocker report saved to `C:\Users\koval\Documents\Команда\artifacts\video-watch\20260701-195257-www.youtube.com-watch-v-so3srrfkiwg\training_pack.md`

## Риски и ограничения

- Без Gemini key, browser cookies, локального файла или восстановленного Newton Fetch текущий конкретный YouTube URL не может быть прочитан.
- Browser cookies не используются автоматически и требуют отдельного явного подтверждения.
- Current Newton CLI health OK, но CLI command list не содержит `fetch`; старые артефакты 2026-06-19 показывают, что такой backend раньше работал через другой/старый CLI path.
- SML watcher heartbeat stale; контекстный пакет был свежий на 2026-07-01, но watcher требует отдельного восстановления.

## Следующий агент

Для реального разбора конкретного YouTube URL выбрать один из путей:

1. Добавить `GEMINI_API_KEY`/`GOOGLE_API_KEY` и использовать Gemini URL backend.
2. Дать явное разрешение на `--cookies-from-browser` для `yt-dlp`.
3. Восстановить/обновить Newton CLI с `fetch`.
4. Передать локальный видео/аудиофайл и использовать local/OpenAI/Newton/ffmpeg route.
