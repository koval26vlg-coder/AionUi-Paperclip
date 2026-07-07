from __future__ import annotations

import argparse
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from hh_resume_booster_outreach_plan import build_plan


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA_PATH = ROOT / "apps" / "aion-vision" / "data" / "hh-booster-leads.jsonl"
DEFAULT_EXPERIMENT_PATH = ROOT / "apps" / "aion-vision" / "data" / "hh-booster-experiment.json"
DEFAULT_OUT_PATH = ROOT / "apps" / "aion-vision" / "data" / "hh-booster-publish-kit.md"
DEFAULT_OPERATOR_BASE_URL = "http://127.0.0.1:8787"
DEFAULT_REHEARSAL_MINUTES = 15


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def md_escape(value: object) -> str:
    return str(value).replace("|", "\\|")


def normalize_base_url(value: str | None) -> str:
    return (value or "").strip().rstrip("/")


def parse_datetime(value: object, fallback: datetime) -> datetime:
    raw = str(value or "").replace("Z", "+00:00")
    if raw:
        try:
            parsed = datetime.fromisoformat(raw)
            return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)
        except ValueError:
            if "." in raw:
                prefix, rest = raw.split(".", 1)
                digits = []
                suffix_start = len(rest)
                for index, char in enumerate(rest):
                    if not char.isdigit():
                        suffix_start = index
                        break
                    digits.append(char)
                suffix = rest[suffix_start:]
                trimmed = f"{prefix}.{''.join(digits)[:6]}{suffix}"
                try:
                    parsed = datetime.fromisoformat(trimmed)
                    return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)
                except ValueError:
                    pass
    return fallback if fallback.tzinfo else fallback.replace(tzinfo=timezone.utc)


def latest_rehearsal(public_base_url: str | None, *, max_age_minutes: int) -> dict[str, Any] | None:
    normalized_public = normalize_base_url(public_base_url)
    data_dir = DEFAULT_DATA_PATH.parent
    if not normalized_public or not data_dir.exists():
        return None

    now_utc = datetime.now(timezone.utc)
    files = sorted(data_dir.glob("hh-booster-day0-rehearsal-*.json"), key=lambda item: item.stat().st_mtime, reverse=True)
    for path in files:
        try:
            record = json.loads(path.read_text(encoding="utf-8-sig"))
        except (OSError, json.JSONDecodeError):
            continue
        if normalize_base_url(record.get("publicBaseUrl")) != normalized_public:
            continue

        fallback = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
        generated_at = parse_datetime(record.get("generatedAt"), fallback).astimezone(timezone.utc)
        age_minutes = (now_utc - generated_at).total_seconds() / 60
        expires_in = max_age_minutes - age_minutes
        blocking_failures = record.get("blockingFailures") or []
        if not isinstance(blocking_failures, list):
            blocking_failures = [str(blocking_failures)]
        ready = record.get("status") == "ready_for_launch" and not blocking_failures and expires_in >= 0
        return {
            "path": str(path),
            "status": record.get("status") or "unknown",
            "ready": ready,
            "age_minutes": round(age_minutes, 2),
            "expires_in_minutes": round(expires_in, 2),
            "stale_at": generated_at.astimezone().replace(microsecond=0) + timedelta(minutes=max_age_minutes),
            "blocking_failures": blocking_failures,
            "experiment_started_at": record.get("experimentStartedAt"),
            "total_leads": record.get("totalLeads"),
        }
    return None


def find_url(links: list[dict[str, str]], *, offer: str, channel: str) -> str:
    for link in links:
        if link.get("offer") == offer and link.get("channel") == channel:
            return link["url"]
    return ""


def is_ephemeral_tunnel_url(value: str | None) -> bool:
    if not value:
        return False
    parsed = urlparse(value)
    host = (parsed.hostname or "").lower().rstrip(".")
    return (
        host.endswith(".loca.lt")
        or host.endswith(".ngrok-free.app")
        or host.endswith(".trycloudflare.com")
        or host.endswith(".localhost.run")
    )


def render_matrix(links: list[dict[str, str]]) -> list[str]:
    lines = [
        "| Оффер | Канал | Ссылка |",
        "| --- | --- | --- |",
    ]
    for link in links:
        lines.append(f"| {md_escape(link['label'])} | {md_escape(link['channel'])} | {md_escape(link['url'])} |")
    return lines


def render_rehearsal_section(public_base_url: str, *, max_age_minutes: int) -> list[str]:
    ephemeral = is_ephemeral_tunnel_url(public_base_url)
    rehearsal = latest_rehearsal(public_base_url, max_age_minutes=max_age_minutes)
    lines = ["", "## Fresh Rehearsal", ""]
    if not ephemeral:
        lines.append("Stable public URL: fresh day-0 rehearsal metadata is not required, but prelaunch still must pass before publishing.")
        return lines
    if not rehearsal:
        lines.extend(
            [
                "No matching successful day-0 rehearsal metadata was found for this temporary public URL.",
                "",
                "Run before guarded launch:",
                "",
                "```powershell",
                f'& "{ROOT}\\apps\\aion-vision\\scripts\\start-hh-booster-day0-rehearsal.ps1" -PublicBaseUrl "{public_base_url}" -SkipBuild -WriteSmoke',
                "```",
            ]
        )
        return lines

    state = "fresh" if rehearsal["ready"] else "stale/not ready"
    lines.extend(
        [
            f"- Status: `{state}`",
            f"- Metadata: `{rehearsal['path']}`",
            f"- Age: `{rehearsal['age_minutes']}` min",
            f"- Expires in: `{rehearsal['expires_in_minutes']}` min",
            f"- Stale at: `{rehearsal['stale_at'].strftime('%Y-%m-%d %H:%M:%S')}`",
            f"- Blocking failures: `{len(rehearsal['blocking_failures'])}`",
            f"- Experiment startedAt in rehearsal: `{rehearsal['experiment_started_at'] or 'not started'}`",
            f"- Total leads in rehearsal: `{rehearsal['total_leads']}`",
            "",
            "If this section is stale, rerun day-0 rehearsal before guarded launch.",
        ]
    )
    return lines


def render_publish_kit(plan: dict[str, Any], operator_base_url: str, *, fresh_rehearsal_minutes: int) -> str:
    public_base_url = plan["public_base_url"] or "n/a"
    summary = plan["summary"]
    experiment = summary["experiment"]
    recommended = plan["recommended_today"]
    links = plan["offer_channel_links"]
    telegram_audit = find_url(links, offer="audit", channel="Telegram")
    direct_response = find_url(links, offer="response", channel="Рекомендация")
    vk_avatar = find_url(links, offer="avatar", channel="VK")
    generated_at = now_iso()

    lines = [
        "# HH Resume Booster Publish Kit",
        "",
        f"Generated: `{generated_at}`",
        f"Operator: `{operator_base_url.rstrip('/')}/#hh-booster`",
        f"Public form: `{public_base_url.rstrip('/')}/#hh-booster-public`",
        f"Experiment startedAt: `{experiment['started_at'] or 'not started'}`",
        f"Launch status: `{'started' if experiment['started_at'] else 'ready for guarded start only'}`",
        f"Ephemeral tunnel: `{'yes' if is_ephemeral_tunnel_url(plan['public_base_url']) else 'no'}`",
        "",
        "## Launch Rule",
        "",
        "Do not publish candidate links until prelaunch returns `Status: GO`.",
        "",
        "Required before publishing:",
        "",
        "1. Open operator panel and press `Старт теста`.",
        "2. Save launch manifest with the real public URL.",
        "3. Run prelaunch with public HTTP checks.",
        "4. Publish only links from this kit or from the operator panel with the same public host.",
        "5. If the public host is a temporary tunnel, rerun day-0 rehearsal with write-smoke immediately before launch and be ready to replace links if the tunnel changes.",
        "",
        *render_rehearsal_section(public_base_url, max_age_minutes=fresh_rehearsal_minutes),
        "",
        "## One-command Launch",
        "",
        "Use only when you are ready to start the 14-day clock. The helper checks the public host/API before writing `startedAt`; for temporary tunnels it also requires fresh successful day-0 rehearsal metadata.",
        "",
        "```powershell",
        (
            f'& "{ROOT}\\apps\\aion-vision\\scripts\\prepare-hh-booster-public-launch.ps1" '
            f'-PublicBaseUrl "{public_base_url}" -OperatorBaseUrl "{operator_base_url}" '
            f'-CheckPublicHttp -FreshRehearsalMinutes {fresh_rehearsal_minutes} -StartExperiment'
        ),
        "```",
        "",
        "## Commands After Start",
        "",
        "```powershell",
        (
            f'& "{ROOT}\\apps\\aion-vision\\scripts\\prepare-hh-booster-public-launch.ps1" '
            f'-PublicBaseUrl "{public_base_url}"'
        ),
        (
            f'& "{ROOT}\\.venv-sml\\Scripts\\python.exe" "{ROOT}\\tools\\hh_resume_booster_prelaunch_check.py" '
            f'--operator-base-url "{operator_base_url}" --public-base-url "{public_base_url}" --check-public-http'
        ),
        (
            f'& "{ROOT}\\apps\\aion-vision\\scripts\\watch-hh-booster-test.ps1" '
            f'-OperatorBaseUrl "{operator_base_url}" -PublicBaseUrl "{public_base_url}"'
        ),
        "```",
        "",
        "## Day Target",
        "",
        f"- Leads today: `{recommended['leads']}`",
        f"- Strong paid intent today: `{recommended['paid_intent']}`",
        "- Per-offer coverage today:",
    ]
    for item in recommended["offers"]:
        lines.append(f"  - {item['label']}: `{item['recommended_leads_today']}` lead(s)")

    lines.extend(
        [
            "",
            "## Direct Offer Links",
            "",
            "| Оффер | Ссылка |",
            "| --- | --- |",
        ]
    )
    for link in plan["offer_links"]:
        lines.append(f"| {md_escape(link['label'])} | {md_escape(link['url'])} |")

    lines.extend(["", "## Offer + Channel Matrix", "", *render_matrix(links)])

    lines.extend(
        [
            "",
            "## Ready Texts",
            "",
            "### Career Chat / Telegram",
            "",
            "```text",
            "Тестирую маленький сервис для соискателей на hh.ru: проверка фото, резюме и отклика перед отправкой работодателю.",
            "Нужно 5 минут: выбрать формат 199/399/799 руб. и оставить контакт для ручного разбора.",
            telegram_audit,
            "```",
            "",
            "### Direct Message",
            "",
            "```text",
            "Привет. Я проверяю идею сервиса для hh.ru: фото + резюме + отклик под вакансию.",
            "Можешь выбрать, какой формат был бы реально полезен, и оставить контакт?",
            direct_response,
            "```",
            "",
            "### VK / Public Post",
            "",
            "```text",
            "Проверяю спрос на ручной разбор профиля hh.ru: фото, резюме или отклик под конкретную вакансию.",
            "Без обещаний гарантированных приглашений. Нужна честная готовность платить:",
            vk_avatar,
            "```",
            "",
            "## Outreach Logging",
            "",
            "After sending messages, log only non-personal outreach denominator.",
            "",
            "```powershell",
            (
                f'& "{ROOT}\\.venv-sml\\Scripts\\python.exe" "{ROOT}\\tools\\hh_resume_booster_outreach_log.py" '
                f'--state "{ROOT}\\apps\\aion-vision\\data\\hh-booster-outreach.jsonl" '
                f'--leads "{DEFAULT_DATA_PATH}" add --channel Telegram --type direct_message --offer audit '
                f'--messages-sent 10 --audience-count 10 --note "no personal data"'
            ),
            (
                f'& "{ROOT}\\.venv-sml\\Scripts\\python.exe" "{ROOT}\\tools\\hh_resume_booster_outreach_log.py" '
                f'--state "{ROOT}\\apps\\aion-vision\\data\\hh-booster-outreach.jsonl" '
                f'--leads "{DEFAULT_DATA_PATH}" add --channel Telegram --type direct_message --offer audit '
                f'--messages-sent 10 --audience-count 10 --note "no personal data" --write'
            ),
            "```",
            "",
            "## Daily Control Loop",
            "",
            "```powershell",
            f'& "{ROOT}\\.venv-sml\\Scripts\\python.exe" "{ROOT}\\tools\\hh_resume_booster_data_quality.py" "{DEFAULT_DATA_PATH}" --experiment-state "{DEFAULT_EXPERIMENT_PATH}" --strict',
            f'& "{ROOT}\\.venv-sml\\Scripts\\python.exe" "{ROOT}\\tools\\hh_resume_booster_outreach_plan.py" "{DEFAULT_DATA_PATH}" --experiment-state "{DEFAULT_EXPERIMENT_PATH}" --public-base-url "{public_base_url}"',
            f'& "{ROOT}\\.venv-sml\\Scripts\\python.exe" "{ROOT}\\tools\\hh_resume_booster_concierge_packet.py" "{DEFAULT_DATA_PATH}"',
            f'& "{ROOT}\\.venv-sml\\Scripts\\python.exe" "{ROOT}\\tools\\hh_resume_booster_concierge_packet.py" "{DEFAULT_DATA_PATH}" --show-contact --markdown',
            f'& "{ROOT}\\.venv-sml\\Scripts\\python.exe" "{ROOT}\\tools\\hh_resume_booster_followup_queue.py" "{DEFAULT_DATA_PATH}"',
            f'& "{ROOT}\\.venv-sml\\Scripts\\python.exe" "{ROOT}\\tools\\hh_resume_booster_daily_snapshot.py" "{DEFAULT_DATA_PATH}" --experiment-state "{DEFAULT_EXPERIMENT_PATH}" --public-base-url "{public_base_url}" --default-out --strict-data-quality',
            "```",
            "",
            "## Privacy Rules",
            "",
            "- Do not scrape hh.ru or log into candidate accounts.",
            "- Do not store extra personal data in outreach logs.",
            "- If a candidate asks to delete data, use the data-admin dry-run/write flow before analysis.",
            "- Do not change offer prices or decision gates mid-test without a dated note.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Build HH Resume Booster publish kit without starting the experiment.")
    parser.add_argument("--data", type=Path, default=DEFAULT_DATA_PATH, help="Leads JSONL/JSON/CSV path.")
    parser.add_argument("--experiment-state", type=Path, default=DEFAULT_EXPERIMENT_PATH, help="Experiment state JSON path.")
    parser.add_argument("--public-base-url", required=True, help="Real public base URL for candidate links.")
    parser.add_argument("--operator-base-url", default=DEFAULT_OPERATOR_BASE_URL, help="Operator base URL.")
    parser.add_argument("--fresh-rehearsal-minutes", type=int, default=DEFAULT_REHEARSAL_MINUTES, help="Freshness window for temporary public URL day-0 rehearsal metadata.")
    parser.add_argument("--out", type=Path, help=f"Output markdown path. Defaults to {DEFAULT_OUT_PATH}.")
    parser.add_argument("--write", action="store_true", help="Write markdown to --out. Without this, print to stdout.")
    args = parser.parse_args()

    plan = build_plan(args.data, args.experiment_state, args.public_base_url)
    markdown = render_publish_kit(plan, args.operator_base_url, fresh_rehearsal_minutes=args.fresh_rehearsal_minutes)

    if args.write:
        out = args.out or DEFAULT_OUT_PATH
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(markdown, encoding="utf-8")
        print(str(out))
    else:
        print(markdown, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
