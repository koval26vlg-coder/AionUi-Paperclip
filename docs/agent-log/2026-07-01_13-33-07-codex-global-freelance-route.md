# Codex agent log: global freelance route

Date: 2026-07-01 13:33 +03:00
Agent: Codex

## User request

Рассмотреть мировые площадки для AI-подработки после отказа от Kwork из-за требования самозанятости.

## Plan

- Сохранить российские биржи отдельно и добавить новый международный маршрут.
- Приоритизировать площадки без российской самозанятости на входе.
- Подготовить очередь действий, английские шаблоны профиля/отклика и скрипты статусов.
- Проверить, что новые PowerShell helpers читают очередь и тексты.

## Done

- Added `docs/global_platforms_route.md`.
- Added `outreach/global_send_queue.csv` with 12 global platform entries.
- Added English profile, gig, project reply, and AI-task application templates under `outreach/global_messages/`.
- Added `tools/copy_global_reply.ps1`.
- Added `tools/update_global_status.ps1`.
- Updated `README.md` with global route commands.

## Verification

- Ran `copy_global_reply.ps1 -Id G001`.
- Ran `copy_global_reply.ps1 -Id G007`.
- Ran `update_global_status.ps1 -Id G006 -Status watch`.
- Imported `outreach/global_send_queue.csv`: 12 rows, 8 ready, 4 watch.

## Risks and limits

- Global platforms usually do not require Russian self-employed status as an account prerequisite, but may require KYC, country availability checks, tax forms, and payment method verification.
- Upwork is kept as watch/reserve because active proposals are tied to Connects.
- No external applications were submitted; all sending/account actions remain manual through the user's own accounts.

## Next check

Start with `G001` Contra profile, `G002-G004` project replies, and `G007/G008/G010` AI-task applications. Do not pay for boosts, subscriptions, verification, or access to jobs before first confirmed revenue.
