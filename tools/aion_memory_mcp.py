import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path


ROOT = Path(os.environ.get("AION_MEMORY_ROOT", Path(__file__).resolve().parents[1])).resolve()
DOCS = ROOT / "docs"
DEBUG_LOG = ROOT / "logs" / "aion-mcp-debug.log"
TRANSPORT_FRAMING = "headers"


def debug(message):
    try:
        DEBUG_LOG.parent.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with DEBUG_LOG.open("a", encoding="utf-8") as handle:
            handle.write(f"{stamp} {message}\n")
    except Exception:
        pass


def read_message():
    global TRANSPORT_FRAMING
    headers = {}

    while True:
        raw_line = sys.stdin.buffer.readline()
        if not raw_line:
            return None

        line = raw_line.decode("utf-8").strip()
        if not line:
            continue

        if line.startswith("{"):
            TRANSPORT_FRAMING = "newline"
            message = json.loads(line)
            debug(f"<- id={message.get('id')} method={message.get('method')} framing=newline")
            return message

        while True:
            if ":" in line:
                key, value = line.split(":", 1)
                headers[key.lower()] = value.strip()

            raw_line = sys.stdin.buffer.readline()
            if not raw_line:
                return None

            line = raw_line.decode("utf-8").strip()
            if line == "":
                break

        break

    length = int(headers.get("content-length", "0"))
    if length <= 0:
        return None
    body = sys.stdin.buffer.read(length)
    TRANSPORT_FRAMING = "headers"
    message = json.loads(body.decode("utf-8"))
    debug(f"<- id={message.get('id')} method={message.get('method')} framing=headers")
    return message


def send_message(message):
    debug(f"-> id={message.get('id')} framing={TRANSPORT_FRAMING} keys={','.join(message.keys())}")
    body = json.dumps(message, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    if TRANSPORT_FRAMING == "newline":
        sys.stdout.buffer.write(body + b"\n")
    else:
        sys.stdout.buffer.write(f"Content-Length: {len(body)}\r\n\r\n".encode("ascii"))
        sys.stdout.buffer.write(body)
    sys.stdout.buffer.flush()


def text_result(text, is_error=False):
    return {
        "content": [
            {
                "type": "text",
                "text": text,
            }
        ],
        "isError": is_error,
    }


def safe_slug(value):
    value = value.lower()
    value = re.sub(r"[^a-zа-я0-9]+", "-", value, flags=re.IGNORECASE).strip("-")
    return value or "task"


def rel(path):
    try:
        return str(path.resolve().relative_to(ROOT)).replace("\\", "/")
    except ValueError:
        return str(path)


def read_text(path, limit=None):
    text = path.read_text(encoding="utf-8", errors="replace")
    if limit and len(text) > limit:
        return text[:limit] + "\n\n[Обрезано: файл длиннее лимита.]"
    return text


def markdown_files():
    candidates = [
        ROOT / "AGENTS.md",
        DOCS / "START-HERE.md",
        DOCS / "context-index.md",
        DOCS / "current-context.md",
        DOCS / "tasks.md",
        DOCS / "decisions.md",
        DOCS / "agents.md",
        DOCS / "local-environment.md",
        DOCS / "memory",
        DOCS / "agent-log",
        DOCS / "handoffs",
    ]
    files = []
    for candidate in candidates:
        if candidate.is_file() and candidate.suffix.lower() == ".md":
            files.append(candidate)
        elif candidate.is_dir():
            files.extend(sorted(candidate.rglob("*.md")))
    return files


def build_context_pack(latest_logs=5):
    pack_dir = DOCS / "context-packs"
    pack_dir.mkdir(parents=True, exist_ok=True)
    now = datetime.now()
    latest_path = pack_dir / "context-pack-latest.md"
    archive_path = pack_dir / f"context-pack-{now.strftime('%Y-%m-%d-%H%M%S')}.md"

    core_files = [
        ROOT / "AGENTS.md",
        DOCS / "START-HERE.md",
        DOCS / "context-index.md",
        DOCS / "current-context.md",
        DOCS / "tasks.md",
        DOCS / "decisions.md",
        DOCS / "agents.md",
        DOCS / "local-environment.md",
        DOCS / "memory" / "architecture.md",
        DOCS / "memory" / "layers" / "facts.md",
        DOCS / "memory" / "layers" / "preferences.md",
        DOCS / "memory" / "layers" / "timeline.md",
        DOCS / "memory" / "layers" / "constraints.md",
    ]

    parts = [
        "# Контекстный пакет",
        "",
        f"Дата сборки: {now.strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "Этот файл предназначен для быстрого входа любого агента в общий контекст.",
        "",
    ]

    for path in core_files:
        if path.is_file():
            parts.extend(["---", "", f"## Файл: {rel(path)}", "", read_text(path), ""])

    log_dir = DOCS / "agent-log"
    if log_dir.is_dir():
        logs = [
            item
            for item in sorted(log_dir.glob("*.md"), key=lambda p: p.stat().st_mtime, reverse=True)
            if item.name.lower() != "readme.md"
        ][:latest_logs]
        if logs:
            parts.extend(["---", "", "## Последние записи журнала агентов", ""])
            for log in logs:
                parts.extend([f"### {rel(log)}", "", read_text(log), ""])

    content = "\n".join(parts)
    latest_path.write_text(content, encoding="utf-8")
    archive_path.write_text(content, encoding="utf-8")
    return latest_path


def tool_read_context_pack(args):
    max_chars = int(args.get("maxChars", 60000))
    path = DOCS / "context-packs" / "context-pack-latest.md"
    if not path.exists():
        path = build_context_pack()
    return text_result(read_text(path, max_chars))


def tool_search_memory(args):
    query = str(args.get("query", "")).strip()
    max_results = int(args.get("maxResults", 10))
    if not query:
        return text_result("Нужно передать query.", True)

    terms = [term.lower() for term in re.findall(r"[\wа-яА-ЯёЁ-]+", query) if len(term) > 1]
    if not terms:
        terms = [query.lower()]

    matches = []
    for path in markdown_files():
        text = read_text(path)
        lower = text.lower()
        score = sum(lower.count(term) for term in terms)
        if score <= 0:
            continue

        snippets = []
        lines = text.splitlines()
        for index, line in enumerate(lines):
            lline = line.lower()
            if any(term in lline for term in terms):
                start = max(0, index - 1)
                end = min(len(lines), index + 2)
                snippets.append("\n".join(lines[start:end]))
                if len(snippets) >= 2:
                    break

        matches.append((score, path, snippets))

    matches.sort(key=lambda item: item[0], reverse=True)
    if not matches:
        return text_result(f"По запросу ничего не найдено: {query}")

    output = [f"# Результаты поиска: {query}", ""]
    for score, path, snippets in matches[:max_results]:
        output.append(f"## {rel(path)}")
        output.append(f"Совпадений: {score}")
        output.append("")
        output.extend(snippets)
        output.append("")

    return text_result("\n".join(output))


def tool_add_memory(args):
    category = str(args.get("category", "facts")).strip().lower()
    text = str(args.get("text", "")).strip()
    source_agent = str(args.get("sourceAgent", "unknown")).strip()
    if not text:
        return text_result("Нужно передать text.", True)

    allowed = {
        "facts": DOCS / "memory" / "layers" / "facts.md",
        "preferences": DOCS / "memory" / "layers" / "preferences.md",
        "timeline": DOCS / "memory" / "layers" / "timeline.md",
        "constraints": DOCS / "memory" / "layers" / "constraints.md",
    }
    path = allowed.get(category)
    if not path:
        return text_result(f"Неизвестная категория: {category}. Доступно: {', '.join(allowed)}", True)

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"\n## {now} - {source_agent}\n\n{text}\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(entry)

    build_context_pack()
    return text_result(f"Память добавлена в {rel(path)}")


def tool_add_agent_log(args):
    agent = str(args.get("agent", "unknown")).strip()
    task = str(args.get("task", "task")).strip()
    body = str(args.get("body", "")).strip()
    if not body:
        return text_result("Нужно передать body.", True)

    log_dir = DOCS / "agent-log"
    log_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y-%m-%d-%H%M")
    path = log_dir / f"{stamp}-{safe_slug(agent)}-{safe_slug(task)}.md"
    content = f"# Отчет агента\n\n## Дата и время\n\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n## Агент\n\n{agent}\n\n## Исходная задача\n\n{task}\n\n## Отчет\n\n{body}\n"
    path.write_text(content, encoding="utf-8")
    build_context_pack()
    return text_result(f"Отчет создан: {rel(path)}")


def tool_create_handoff(args):
    from_agent = str(args.get("fromAgent", "unknown")).strip()
    to_agent = str(args.get("toAgent", "next-agent")).strip()
    task = str(args.get("task", "task")).strip()
    summary = str(args.get("summary", "")).strip()
    if not summary:
        return text_result("Нужно передать summary.", True)

    handoff_dir = DOCS / "handoffs"
    handoff_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y-%m-%d-%H%M")
    path = handoff_dir / f"{stamp}-{safe_slug(from_agent)}-to-{safe_slug(to_agent)}-{safe_slug(task)}.md"
    content = f"# Передача задачи другому агенту\n\n## Дата и время\n\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n## От кого\n\n{from_agent}\n\n## Кому\n\n{to_agent}\n\n## Исходная задача\n\n{task}\n\n## Что уже сделано\n\n{summary}\n\n## Где смотреть контекст\n\n- `docs/context-packs/context-pack-latest.md`\n- `docs/agent-log/`\n- `docs/tasks.md`\n- `docs/decisions.md`\n"
    path.write_text(content, encoding="utf-8")
    build_context_pack()
    return text_result(f"Передача создана: {rel(path)}")


def tool_build_context_pack(_args):
    path = build_context_pack()
    return text_result(f"Контекстный пакет обновлен: {rel(path)}")


TOOLS = {
    "read_context_pack": {
        "description": "Прочитать общий контекстный пакет проекта.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "maxChars": {"type": "integer", "description": "Максимум символов в ответе", "default": 60000}
            },
        },
        "handler": tool_read_context_pack,
    },
    "search_memory": {
        "description": "Поиск по общей файловой памяти, решениям, задачам и журналам агентов.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "maxResults": {"type": "integer", "default": 10},
            },
            "required": ["query"],
        },
        "handler": tool_search_memory,
    },
    "add_memory": {
        "description": "Добавить долгосрочную запись в файловую память.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "category": {"type": "string", "enum": ["facts", "preferences", "timeline", "constraints"]},
                "text": {"type": "string"},
                "sourceAgent": {"type": "string"},
            },
            "required": ["category", "text"],
        },
        "handler": tool_add_memory,
    },
    "add_agent_log": {
        "description": "Создать запись журнала работы агента.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "agent": {"type": "string"},
                "task": {"type": "string"},
                "body": {"type": "string"},
            },
            "required": ["agent", "task", "body"],
        },
        "handler": tool_add_agent_log,
    },
    "create_handoff": {
        "description": "Создать передачу задачи другому агенту.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "fromAgent": {"type": "string"},
                "toAgent": {"type": "string"},
                "task": {"type": "string"},
                "summary": {"type": "string"},
            },
            "required": ["fromAgent", "toAgent", "task", "summary"],
        },
        "handler": tool_create_handoff,
    },
    "build_context_pack": {
        "description": "Пересобрать docs/context-packs/context-pack-latest.md.",
        "inputSchema": {"type": "object", "properties": {}},
        "handler": tool_build_context_pack,
    },
}


def tool_list():
    return [
        {
            "name": name,
            "description": spec["description"],
            "inputSchema": spec["inputSchema"],
        }
        for name, spec in TOOLS.items()
    ]


def handle_request(message):
    method = message.get("method")
    msg_id = message.get("id")

    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "aion-file-memory", "version": "0.1.0"},
            },
        }

    if method == "ping":
        return {"jsonrpc": "2.0", "id": msg_id, "result": {}}

    if method == "tools/list":
        return {"jsonrpc": "2.0", "id": msg_id, "result": {"tools": tool_list()}}

    if method == "tools/call":
        params = message.get("params") or {}
        name = params.get("name")
        args = params.get("arguments") or {}
        spec = TOOLS.get(name)
        if not spec:
            result = text_result(f"Неизвестный инструмент: {name}", True)
        else:
            try:
                result = spec["handler"](args)
            except Exception as exc:
                result = text_result(f"Ошибка инструмента {name}: {exc}", True)
        return {"jsonrpc": "2.0", "id": msg_id, "result": result}

    if method and method.startswith("notifications/"):
        return None

    return {
        "jsonrpc": "2.0",
        "id": msg_id,
        "error": {"code": -32601, "message": f"Method not found: {method}"},
    }


def main():
    debug("server started")
    while True:
        try:
            message = read_message()
            if message is None:
                debug("stdin closed")
                break
            response = handle_request(message)
            if response is not None and "id" in message:
                send_message(response)
        except Exception as exc:
            debug(f"fatal error: {exc}")
            break


if __name__ == "__main__":
    main()
