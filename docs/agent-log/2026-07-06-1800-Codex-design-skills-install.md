# Codex design skills install

Date: 2026-07-06 18:00 +03:00

Workspace: `C:\Users\koval\Documents\Codex\2026-05-18\npx-skills-add-anthropics-claude-code`

Installed design/code-agent skills from the YouTube Short workflow:

- `impeccable` from `https://github.com/pbakaus/impeccable`
- `design-taste-frontend` from `https://github.com/Leonxlnx/taste-skill`
- `animation-vocabulary` from `https://github.com/emilkowalski/skill`
- `emil-design-eng` from `https://github.com/emilkowalski/skill`
- `review-animations` from `https://github.com/emilkowalski/skill`

Install method:

- `npx skills add pbakaus/impeccable --skill impeccable --agent "*" --global --copy -y --full-depth`
- `npx skills add Leonxlnx/taste-skill --skill design-taste-frontend --agent "*" --global --copy -y --full-depth`
- `npx skills add emilkowalski/skill --skill animation-vocabulary emil-design-eng review-animations --agent "*" --global --copy -y --full-depth`
- Synced installed folders from `C:\Users\koval\.agents\skills` into Codex, Claude, and shared workspace roots.

Verified target roots:

- `C:\Users\koval\.agents\skills`
- `C:\Users\koval\.codex\skills`
- `C:\Users\koval\.claude\skills`
- `C:\Users\koval\Documents\Codex\2026-05-18\npx-skills-add-anthropics-claude-code\agent-skills`

Validation result:

- All five expected skill folders exist in all four roots.
- All five `SKILL.md` files are present and non-empty in all four roots.
- Human-readable manifest: `agent-skills\DESIGN_SKILLS_INSTALL_MANIFEST.md`
- JSON manifest: `agent-skills\design-skills-install-manifest.json`

Claude skill folders that existed after CLI install were backed up before sync with suffix `.backup.20260706-165448`.

Next step for agents: restart long-running Codex / Claude Code / Cursor / Antigravity terminals if they do not discover the new skills immediately.
