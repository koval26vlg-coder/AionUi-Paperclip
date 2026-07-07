# Codex agent-reach install

Date: 2026-07-06 20:55 +03:00

User request: analyze YouTube Short `https://youtube.com/shorts/A5l_yCqxWMg?si=aFdOkA-ooWvbXfOS`, extract useful tools/platforms, and install required skills/MCP/tools where safe.

What was found:

- The video describes `Panniantong/Agent-Reach`, not "agent rich/reich".
- Transcript and frames were extracted via `video-watch`.
- Artifact: `C:\Users\koval\Documents\Команда\artifacts\video-watch\20260706-202055-youtube.com-shorts-a5l_ycqxwmg-si-afdoka-oowvbxfos`.

Installed and configured:

- `agent-reach` CLI v1.5.0 in `C:\Users\koval\.agent-reach-venv`.
- `agent-reach` skill in `.agents`, `.codex`, `.claude`, and shared `agent-skills`.
- `mcporter` and `opencli` via npm global.
- Portable GitHub CLI `gh` v2.96.0 in `C:\Users\koval\.local\gh-cli\bin\gh.exe`, shim `C:\Users\koval\bat\gh.cmd`.
- Exa MCP in `C:\Users\koval\.mcporter\mcporter.json` and workspace `config\mcporter.json`.
- `yt-dlp` global config includes `--js-runtimes node`.

Verification:

- `agent-reach doctor --json` OK for GitHub, YouTube, Exa search, Web/Jina, RSS, V2EX, Bilibili search.
- `mcporter call 'exa.web_search_exa(query: "Agent Reach GitHub", numResults: 1)'` succeeded.
- `gh repo view Panniantong/Agent-Reach --json ...` succeeded using existing local GitHub token environment. Secret value was not printed intentionally.

Manual remaining:

- Twitter/X, Reddit, Facebook, Instagram, XiaoHongShu are installed/prepared through OpenCLI but require the OpenCLI Chrome extension and logged-in Chrome session. No browser cookies were imported automatically.
- LinkedIn, Xiaoyuzhou, and Xueqiu remain optional/not configured.

Manifests:

- `agent-skills\AGENT_REACH_INSTALL_MANIFEST.md`
- `agent-skills\agent-reach-install-manifest.json`
