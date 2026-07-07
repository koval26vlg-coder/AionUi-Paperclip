# NOI VPS — runbook восстановления Antigravity-роута

VPS `root@147.90.11.165` поднимали как зарубежный хост для запуска Antigravity CLI (`agy`),
чтобы обходить региональный блокер `User location is not supported`.

## ЗАВЕРШЕНО 2026-07-07 — NOI восстановлен

`check-antigravity-noi.ps1 -Smoke` возвращает `ok`: SSH работает, `agy 1.0.16`, Google OAuth
пройден пользователем, live-вызов модели проходит. NOI готов как резервный Antigravity-роут.
Разделы ниже оставлены как история процесса восстановления.

## Состояние по ходу восстановления (2026-07-07)

- **SSH восстановлен.** `check-antigravity-noi.ps1` показывает `TCP: connected`,
  `SSH banner: SSH-2.0-OpenSSH_8.9p1`, `SSH_OK`. Прежний `banner exchange failed` ушёл —
  сервер загружен, `sshd` слушает порт 22. Console/rescue в панели не понадобился.
- **`agy` установлен** на сервере (обновился до `1.0.16` в ходе авторизации).
- **OAuth завершён.** Первый `-Smoke` падал по таймауту 30с на Google OAuth URL; после входа
  пользователя через `start-antigravity-noi-auth.ps1` повторный `-Smoke` вернул `ok`.

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
