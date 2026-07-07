# 2026-07-07 — Claude Code — NOI VPS восстановлен (OAuth + smoke ok)

## Итог

Antigravity NOI VPS `root@147.90.11.165` полностью восстановлен как резервный зарубежный
Antigravity-роут.

- SSH работает (`SSH_OK`, banner `SSH-2.0-OpenSSH_8.9p1`), console/rescue не понадобился.
- `agy` на сервере обновился до `1.0.16` в ходе авторизации.
- Пользователь прошёл Google OAuth через `tools/start-antigravity-noi-auth.ps1`.
- Проверка `tools/check-antigravity-noi.ps1 -Smoke` вернула `ok` (live-вызов модели проходит).

## Что обновлено

- `docs/tasks.md`: NOI убран из «В работе», зафиксирован как восстановленный резервный роут
  в разделе инфраструктуры.
- `docs/history/noi-vps-recovery-runbook.md`: добавлен статус «ЗАВЕРШЕНО».

## Роль NOI

Резервный маршрут на случай, если региональный блокер `User location is not supported`
вернётся И локальный Antigravity + fallback `gemini-vertex` одновременно откажут. Сейчас
дефолт — `grok-antigravity` с локальным Antigravity L2; NOI не в активной цепочке, это страховка.

## Следующему агенту

P3 закрыт полностью. Открытых пунктов из аудита хаба не осталось (кроме отдельного
Antigravity L1/L2 runner hardening и отложенного HH Booster).
