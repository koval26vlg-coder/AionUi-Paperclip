from __future__ import annotations

import argparse
import os
import re
import shutil
import sqlite3
import subprocess
import sys
import time
from pathlib import Path


BOT_STEP_TYPE = 15
VALID_SHORT_RESPONSES = {"ok", "approve", "revise", "block", "escalate"}
TOOL_MARKERS = {
    "grep_search",
    "read_file",
    "run_command",
    "view_file",
    "write_to_file",
}
INTERNAL_MARKERS = (
    "**acknowledge",
    "**analyz",
    "**clarifying",
    "**confirming",
    "**reviewing",
    "**verifying",
    "i am ",
    "i will ",
    "i need ",
    "i'm ",
    "i've ",
    "okay,",
)
READY_ONLY_MARKERS = (
    "готов к работе",
    "какой вопрос",
    "какую задачу",
    "пожалуйста, сообщите",
    "что вас интересует",
    "please tell",
    "ready to work",
    "what would you like",
    "how can i help",
)
UUID_RE = re.compile(
    r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}",
    re.IGNORECASE,
)


def default_agy_path() -> str:
    found = shutil.which("agy", path=stable_path_value())
    if found:
        return found
    local = Path.home() / "AppData" / "Local" / "agy" / "bin" / "agy.exe"
    return str(local)


def stable_path_entries() -> list[str]:
    home = Path.home()
    system_root = Path(os.environ.get("SystemRoot") or r"C:\Windows")
    preferred = [
        system_root / "system32",
        system_root,
        home / "bat",
        Path(r"C:\Program Files\PowerShell\7"),
        Path(r"C:\Program Files\nodejs"),
        home / "AppData" / "Roaming" / "npm",
        home / "AppData" / "Local" / "agy" / "bin",
    ]
    entries: list[str] = []

    def add(raw: str | os.PathLike[str] | None) -> None:
        if raw is None:
            return
        text = os.path.expandvars(str(raw).strip())
        if not text or text == "${PATH}":
            return
        path = Path(text)
        if not path.exists():
            return
        normalized = str(path)
        if normalized.lower() not in {item.lower() for item in entries}:
            entries.append(normalized)

    for item in preferred:
        add(item)
    for key in ("Path", "PATH"):
        for item in os.environ.get(key, "").split(os.pathsep):
            add(item)
    return entries


def stable_path_value() -> str:
    return os.pathsep.join(stable_path_entries())


def stable_env() -> dict[str, str]:
    env = os.environ.copy()
    path = stable_path_value()
    env["Path"] = path
    env["PATH"] = path
    return env


def default_conversations_dir() -> Path:
    return Path.home() / ".gemini" / "antigravity-cli" / "conversations"


def decode_chunks(blob: bytes | str | None) -> list[str]:
    if blob is None:
        return []
    if isinstance(blob, str):
        text = blob
    else:
        text = blob.decode("utf-8", errors="ignore")
    cleaned = "".join(ch if ch in "\r\n\t" or ord(ch) >= 32 else "\n" for ch in text)
    cleaned = cleaned.replace("\r\n", "\n").replace("\r", "\n")
    chunks = re.split(r"\n{2,}", cleaned)
    return [chunk.strip() for chunk in chunks if chunk.strip()]


def mostly_noise(text: str) -> bool:
    stripped = text.strip()
    if not stripped:
        return True
    if stripped.lower() in VALID_SHORT_RESPONSES:
        return False
    if len(stripped) < 8:
        return True
    meaningful = sum(1 for ch in stripped if ch.isalnum())
    return meaningful / max(len(stripped), 1) < 0.25


def normalize_chunk(text: str) -> str | None:
    stripped = text.strip()
    if "2(bot-" in stripped:
        prefix = stripped.split("2(bot-", 1)[0].strip()
        if prefix and not mostly_noise(prefix):
            return prefix
    if "sessionID" in stripped:
        lines = [line.strip() for line in stripped.splitlines() if line.strip()]
        for index, line in enumerate(lines):
            if line == "sessionID":
                rest = "\n".join(lines[index + 1 :]).strip()
                if rest and not mostly_noise(rest):
                    return rest
        return None
    return stripped


def is_metadata(text: str) -> bool:
    stripped = text.strip()
    if "sessionID" in stripped:
        return True
    if UUID_RE.search(stripped) and len(stripped) < 160:
        return True
    if re.fullmatch(r"[a-z0-9]{8,16}", stripped, re.IGNORECASE):
        return True
    if stripped.startswith('"$') or stripped.startswith("b$") or stripped.startswith("P\n$"):
        return True
    return mostly_noise(stripped)


def is_internal_or_tool(text: str) -> bool:
    lowered = text.lstrip().lower()
    if any(lowered.startswith(marker) for marker in INTERNAL_MARKERS):
        return True
    if any(marker in text for marker in TOOL_MARKERS):
        return True
    if "CommandLine" in text and "WaitMsBeforeAsync" in text:
        return True
    return False


def cleanup_response(text: str) -> str:
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    text = re.sub(r"^2\(bot-[0-9a-f-]+[:B]?\s*", "", text, flags=re.IGNORECASE)
    return text.strip()


def prompt_for_print_arg(prompt: str) -> str:
    normalized = prompt.replace("\r\n", "\n").replace("\r", "\n")
    if "\n" not in normalized:
        return normalized
    escaped = normalized.replace("\\", "\\\\").replace("\n", "\\n")
    return (
        "The next prompt is encoded as a single command-line argument. "
        "Interpret every literal \\n sequence as a real line break before "
        "answering, and do not mention this transport encoding. "
        f"{escaped}"
    )


def stdout_looks_recoverable_failure(text: str) -> bool:
    stripped = cleanup_response(text)
    if not stripped:
        return True
    lowered = stripped.lower()
    if any(marker in lowered for marker in READY_ONLY_MARKERS):
        return True
    if is_metadata(stripped) or mostly_noise(stripped):
        return True
    return False


def extract_response_from_blob(blob: bytes | str | None) -> str | None:
    chunks = decode_chunks(blob)
    response_chunks: list[str] = []
    started = False
    for chunk in chunks:
        chunk = normalize_chunk(chunk) or ""
        if is_metadata(chunk):
            continue
        if is_internal_or_tool(chunk):
            if started:
                break
            continue
        if chunk.startswith("2(bot-") and started:
            break
        response_chunks.append(chunk)
        started = True
        if chunk.lower() in VALID_SHORT_RESPONSES:
            break
        if sum(len(item) for item in response_chunks) > 12000:
            break
    if not response_chunks:
        return None
    return cleanup_response("\n\n".join(response_chunks)) or None


def extract_latest_response_from_db(db_path: Path) -> str | None:
    try:
        con = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    except sqlite3.Error:
        return None
    try:
        rows = con.execute(
            "select step_payload from steps where step_type=? order by idx desc",
            (BOT_STEP_TYPE,),
        )
        for (payload,) in rows:
            response = extract_response_from_blob(payload)
            if response and not stdout_looks_recoverable_failure(response):
                return response
    except sqlite3.Error:
        return None
    finally:
        con.close()
    return None


def recent_conversation_dbs(conversations_dir: Path, started_at: float) -> list[Path]:
    if not conversations_dir.exists():
        return []
    dbs = [path for path in conversations_dir.glob("*.db") if path.is_file()]
    recent = [path for path in dbs if path.stat().st_mtime >= started_at - 5]
    candidates = recent or dbs
    return sorted(candidates, key=lambda path: path.stat().st_mtime, reverse=True)[:10]


def recover_from_conversations(conversations_dir: Path, started_at: float) -> tuple[str | None, Path | None]:
    for db_path in recent_conversation_dbs(conversations_dir, started_at):
        response = extract_latest_response_from_db(db_path)
        if response and not stdout_looks_recoverable_failure(response):
            return response, db_path
    return None, None


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run agy --print and recover empty stdout from Antigravity conversation DB."
    )
    parser.add_argument("prompt")
    parser.add_argument("--agy", default=os.environ.get("AGY_EXE") or default_agy_path())
    parser.add_argument("--model")
    parser.add_argument("--sandbox", action="store_true")
    parser.add_argument("--print-timeout", default="5m0s")
    parser.add_argument("--process-timeout-seconds", type=int, default=390)
    parser.add_argument("--cwd", default=str(Path.cwd()))
    parser.add_argument("--conversations-dir", type=Path, default=default_conversations_dir())
    parser.add_argument("--no-db-fallback", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    command = [args.agy]
    if args.sandbox:
        command.append("--sandbox")
    if args.model:
        command.extend(["--model", args.model])
    command.extend(["--print-timeout", args.print_timeout, "--print", prompt_for_print_arg(args.prompt)])

    started_at = time.time()
    try:
        result = subprocess.run(
            command,
            text=True,
            capture_output=True,
            cwd=args.cwd,
            timeout=args.process_timeout_seconds,
            check=False,
            env=stable_env(),
        )
    except FileNotFoundError:
        print(f"agy executable not found: {args.agy}", file=sys.stderr)
        return 127
    except subprocess.TimeoutExpired:
        print("agy --print timed out", file=sys.stderr)
        return 124

    stdout = result.stdout.strip()
    if stdout and not stdout_looks_recoverable_failure(stdout):
        print(result.stdout.rstrip())
        if result.stderr.strip():
            print(result.stderr.rstrip(), file=sys.stderr)
        return result.returncode

    if result.returncode != 0:
        if result.stderr.strip():
            print(result.stderr.rstrip(), file=sys.stderr)
        return result.returncode

    if not args.no_db_fallback:
        response, db_path = recover_from_conversations(args.conversations_dir, started_at)
        if response:
            print(response)
            if stdout:
                print("Ignored unusable Antigravity stdout and recovered DB response", file=sys.stderr)
            print(f"Recovered Antigravity response from {db_path}", file=sys.stderr)
            return 0

    if result.stderr.strip():
        print(result.stderr.rstrip(), file=sys.stderr)
    if stdout:
        print(stdout)
        print("agy --print returned unusable stdout and no DB response was recovered", file=sys.stderr)
        return 3
    print("agy --print returned empty stdout and no DB response was recovered", file=sys.stderr)
    return 3


if __name__ == "__main__":
    raise SystemExit(main())
