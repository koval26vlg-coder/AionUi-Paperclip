# Aion Vision

Aion Vision - локальный веб-дашборд для общей памяти агентов SML.

Интерфейс читает живые данные из `D:\AionUi-Paperclip\var\sml\state.db` через dev endpoint `/api/sml-dashboard`. Для статического preview также создается snapshot `public/aion-data.json`.

## Запуск

Из корня workspace:

```powershell
.\START-AION-VISION.cmd
```

Или напрямую:

```powershell
cd D:\AionUi-Paperclip\apps\aion-vision
npm run export:data
npm install
npm run dev
```

## Проверки

```powershell
npm run lint
npm run build
```

## Текущие ограничения

- dev endpoint работает только при запуске через Vite;
- `public/aion-data.json` является snapshot и обновляется при запуске `START-AION-VISION.cmd` или `npm run export:data`;
- production build дает предупреждение о размере чанка из-за общего bundle с `recharts` и `framer-motion`.
