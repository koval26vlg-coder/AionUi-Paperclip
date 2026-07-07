# L5 Revision Request: car-role mismatch before finalization

## Причина

Перед финализацией пользователь указал, что на dashboard `L3 Codex` все еще выглядит как Nissan GT-R, а `L4 Codex` не считывается как конкретная машина.

Это визуальное несоответствие нельзя закрывать final-report как `approve`, потому что car-role mapping является частью основной идеи продукта: каждый уровень должен быть отдельной машиной с понятной ролью.

## Ожидаемое исправление

Закрепить car policy:

- `L1.0 MiMo AUTO` — tuned kei scout: Autozam AZ-1 / Suzuki Cappuccino.
- `L1.1 Antigravity CLI` — Toyota AE86 Trueno.
- `L2 Antigravity CLI` — Nissan 180SX Type X.
- `L3 Codex` — Toyota Chaser JZX100.
- `L4 Codex` — Nissan Silvia S15 в красно-черной технической стилистике.
- `L5 Claude Code` — Toyota Supra A80.

## Что нельзя искажать

- Не возвращать GT-R как Codex L3.
- Не оставлять L4 как generic `красное техническое купе`.
- Не закрывать workflow finalization, пока dashboard/data/handoff не отражают новую car policy.
