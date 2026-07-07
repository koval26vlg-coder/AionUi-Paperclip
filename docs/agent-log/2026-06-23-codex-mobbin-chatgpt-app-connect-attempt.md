# 2026-06-23 - Codex - Mobbin ChatGPT/Codex App connector

## Исходный запрос

Пользователь попросил подключить Mobbin для Codex App через ChatGPT app connector.

## План

- Проверить локальные правила и текущий MCP статус.
- Открыть официальную страницу Mobbin app в ChatGPT.
- Не вводить учетные данные пользователя и не обходить OAuth.
- Зафиксировать фактическое состояние.

## Что сделано

- Выполнен `active-run-gate`: `trading_mvp` остается `RUNNING`; работа не затрагивала проект.
- Выполнен Aion memory bootstrap по теме Mobbin ChatGPT connector.
- Открыта страница `https://chatgpt.com/apps/mobbin/asdk_app_69fdb9081018819193707354f21b366e` в управляемом браузере Playwright.
- Управляемый браузер оказался не авторизован в ChatGPT; дальше требуется login пользователя.
- Та же страница открыта в обычном браузере Windows через `Start-Process`, чтобы пользователь мог пройти подключение в своей ChatGPT-сессии.

## Проверки

- `codex mcp list` показывает `mobbin https://api.mobbin.com/mcp enabled OAuth`.
- `claude mcp get mobbin` показывает user-scope HTTP MCP, но статус `Needs authentication`.
- ChatGPT app connector не был подтвержден автоматически, потому что требует интерактивного входа/подтверждения пользователя.

## Следующий шаг

Пользователю нужно в открывшемся браузере нажать `Connect`, затем `Sign in with Mobbin` и подтвердить OAuth. После этого можно вернуться в Codex и попросить проверить состояние.

## Риски и ограничения

- Я не вводил и не запрашивал пароль/2FA.
- Подключение ChatGPT app connector нельзя подтвердить из локального `codex mcp list`; это состояние живет в ChatGPT/Codex App аккаунте.
