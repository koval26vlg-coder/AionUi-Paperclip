# NOI VPS — runbook восстановления Antigravity-роута

VPS `root@147.90.11.165` поднимали как зарубежный хост для запуска Antigravity CLI (`agy`),
чтобы обходить региональный блокер `User location is not supported`.

## Текущее состояние (проверено 2026-07-07)

- **SSH восстановлен.** `check-antigravity-noi.ps1` показывает `TCP: connected`,
  `SSH banner: SSH-2.0-OpenSSH_8.9p1`, `SSH_OK`. Прежний `banner exchange failed` ушёл —
  сервер загружен, `sshd` слушает порт 22. Console/rescue в панели больше не нужен.
- **`agy 1.0.13` установлен** на сервере.
- **OAuth не завершён.** `check-antigravity-noi.ps1 -Smoke` доходит до Google OAuth URL и
  падает по таймауту 30с: `Error: authentication timed out`. Это единственный оставшийся шаг.

## Что осталось сделать (шаг пользователя)

Авторизацию в Google-аккаунт `koval26vlg@gmail.com` может завершить только пользователь.

1. Запустить видимый OAuth-хелпер:

   ```powershell
   pwsh -File D:\AionUi-Paperclip\tools\start-antigravity-noi-auth.ps1
   ```

2. В открывшемся окне пройти по печатаемому Google OAuth URL, войти как
   `koval26vlg@gmail.com` и подтвердить доступ (scope cloud-platform / userinfo).
3. После успешного входа проверить live-вызов:

   ```powershell
   pwsh -File D:\AionUi-Paperclip\tools\check-antigravity-noi.ps1 -Smoke
   ```

   Успех = smoke возвращает ответ модели без `authentication timed out`.

## Зачем это (и почему не срочно)

NOI — резервный зарубежный маршрут на случай, если региональный блокер вернётся И
локальный Antigravity + fallback `gemini-vertex` одновременно откажут. Сейчас локальный
Antigravity работает (дефолт `grok-antigravity`, L2 = Antigravity), так что NOI — страховка,
а не критичный путь. Поэтому восстановление доведено до «SSH + CLI готовы, ждём OAuth»;
финальный вход можно сделать в удобный момент.

## Хелперы

- `tools/check-antigravity-noi.ps1` — проверка TCP/SSH/agy, с `-Smoke` — live-вызов.
- `tools/start-antigravity-noi-auth.ps1` — видимый OAuth-хелпер.
