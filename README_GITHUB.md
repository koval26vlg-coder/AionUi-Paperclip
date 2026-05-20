# Aion SML Core (Shared Memory Layer)

Инфраструктура общей памяти и контекста для автономных AI-агентов. Проект служит «единым источником истины» для Codex, Cursor, Kiro и Gemini CLI, позволяя им работать в едином информационном поле.

## 🚀 Основные возможности

- **Shared Memory Layer (SML)**: MCP-сервер на базе SQLite WAL и LanceDB для хранения фактов, решений и логов работы агентов.
- **Semantic Search**: Встроенный движок семантического поиска (Ollama bge-m3) для автоматического нахождения релевантного контекста перед выполнением задач.
- **Aion Vision**: Футуристичный BOLD UI дашборд (Vite + React + Tailwind), визуализирующий активность агентов и состояние памяти в реальном времени.
- **Cross-Agent Protocol**: Стандартизированный формат журналов и решений, исключающий потерю контекста при смене модели или инструмента.

## 🏗 Архитектура

- **Backend**: Python 3.12+, FastAPI, MCP SDK.
- **Database**: SQLite (для транзакций) + LanceDB (для векторного поиска).
- **Frontend**: React 18, Framer Motion (Industrial/Cyberpunk Aesthetic).

## 🛠 Установка

1. Склонируйте репозиторий.
2. Установите зависимости SML: `pip install -r tools/sml/requirements.txt`.
3. Запустите дашборд: `START-AION-VISION.cmd`.

---
*Проект является частью экосистемы AionUi-Paperclip.*
