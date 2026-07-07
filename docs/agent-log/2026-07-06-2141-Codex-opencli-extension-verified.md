# Codex OpenCLI extension verified

Date: 2026-07-06 21:41 +03:00

User reported that the OpenCLI Chrome extension was installed.

Verification:

- `opencli doctor` passed:
  - daemon running on port `19825`, version `1.8.6`
  - extension connected, version `1.0.22`
  - profile `23yp8u5h` connected
- `agent-reach doctor --json` now reports OK for:
  - GitHub via `gh CLI`
  - YouTube via `yt-dlp`
  - Twitter/X via OpenCLI
  - Reddit via OpenCLI
  - Facebook via OpenCLI
  - Instagram via OpenCLI
  - Bilibili via OpenCLI
  - XiaoHongShu via OpenCLI
  - Exa search via `mcporter`
  - Web/Jina, RSS, V2EX

Remaining:

- LinkedIn MCP is not configured.
- Xiaoyuzhou podcast transcription route is not configured.
- Xueqiu still needs logged-in cookie import/configuration.

Updated:

- `agent-skills\AGENT_REACH_INSTALL_MANIFEST.md`
- `agent-skills\agent-reach-install-manifest.json`
