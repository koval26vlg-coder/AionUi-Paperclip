"""Тесты MCP_Adapter (задачи 5.1–5.11)."""

from __future__ import annotations

import io
import json
from pathlib import Path

import pytest

from tools.sml.embedding_engine import EmbeddingEngine
from tools.sml.mcp_adapter import SMLServer, handle_request, run_stdio_loop
from tools.sml.operation_log import OperationLog
from tools.sml.temporal_store import open_store


@pytest.fixture
def server(tmp_path: Path) -> SMLServer:
    store = open_store(tmp_path / "state.db")
    op_log = OperationLog(tmp_path / "logs")
    # Embedding_Engine отключаем: тесты, не требующие семантики, не должны
    # зависеть от Ollama. Тесты семантики дергают реальный engine отдельно.
    s = SMLServer(store=store, engine=None, op_log=op_log)
    yield s
    s.close()


# --- Базовые RPC-методы ---


def test_initialize_returns_server_info(server: SMLServer) -> None:
    response = handle_request(
        server, {"jsonrpc": "2.0", "id": 1, "method": "initialize"}
    )
    assert response is not None
    assert response["id"] == 1
    assert response["result"]["serverInfo"]["name"] == "sml"


def test_tools_list_contains_ten_tools(server: SMLServer) -> None:
    response = handle_request(server, {"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
    tools = response["result"]["tools"]
    names = {t["name"] for t in tools}
    expected = {
        "sml.ping",
        "sml.write",
        "sml.read",
        "sml.semantic_query",
        "sml.temporal_query",
        "sml.supersede",
        "sml.add_decision",
        "sml.add_log",
        "sml.build_context_pack",
        "sml.startup_pack",
    }
    assert expected.issubset(names)
    assert len(names) == 10


def test_invalid_rpc_rejected(server: SMLServer) -> None:
    response = handle_request(server, {"foo": "bar"})
    assert "error" in response
    assert response["error"]["code"] == -32600


def test_unknown_method(server: SMLServer) -> None:
    response = handle_request(
        server, {"jsonrpc": "2.0", "id": 99, "method": "tools/nonsense"}
    )
    assert "error" in response
    assert response["error"]["code"] == -32601


def test_initialized_notification_is_ignored(server: SMLServer) -> None:
    response = handle_request(
        server,
        {
            "jsonrpc": "2.0",
            "method": "notifications/initialized",
            "params": {},
        },
    )
    assert response is None


# --- sml.ping ---


def test_ping_happy_path(server: SMLServer) -> None:
    response = handle_request(
        server,
        {
            "jsonrpc": "2.0",
            "id": 5,
            "method": "tools/call",
            "params": {"name": "sml.ping", "arguments": {}},
        },
    )
    body = response["result"]
    assert body["ok"] is True
    assert body["version"].startswith("sml-")
    assert body["uptime_seconds"] >= 0
    assert body["records_total"] == 0
    assert body["degraded"] is False


# --- sml.write + sml.read ---


def _call(server: SMLServer, tool: str, args: dict, request_id: int = 1) -> dict:
    response = handle_request(
        server,
        {
            "jsonrpc": "2.0",
            "id": request_id,
            "method": "tools/call",
            "params": {"name": tool, "arguments": args},
        },
    )
    return response["result"]


def test_write_then_read_roundtrip(server: SMLServer) -> None:
    write_res = _call(
        server,
        "sml.write",
        {
            "type": "fact",
            "content": "русский факт о SML",
            "author_agent": "kiro",
        },
    )
    assert write_res["ok"] is True
    rid = write_res["id"]
    read_res = _call(server, "sml.read", {"id": rid})
    assert read_res["ok"] is True
    assert read_res["found"] is True
    assert read_res["record"]["content"] == "русский факт о SML"


def test_read_missing_returns_not_found(server: SMLServer) -> None:
    bogus = "00000000-0000-7000-8000-000000000000"
    res = _call(server, "sml.read", {"id": bogus})
    assert res["ok"] is True
    assert res["found"] is False


def test_read_invalid_id(server: SMLServer) -> None:
    res = _call(server, "sml.read", {"id": "not-a-uuid"})
    assert res["ok"] is False
    assert res["error"]["category"] == "validation"


def test_write_rejects_secret(server: SMLServer) -> None:
    res = _call(
        server,
        "sml.write",
        {
            "type": "fact",
            "content": "токен: sk-" + "a" * 40,
            "author_agent": "kiro",
        },
    )
    assert res["ok"] is False
    assert res["error"]["category"] == "secret_rejected"


def test_write_rejects_unknown_type(server: SMLServer) -> None:
    res = _call(
        server,
        "sml.write",
        {"type": "unknown", "content": "x", "author_agent": "kiro"},
    )
    assert res["ok"] is False
    # SML выбрасывает либо validation (pydantic), либо unsupported — оба
    # корректные варианты семантики. Проверим, что это не success.
    assert res["error"]["category"] in {"validation", "unsupported"}


def test_supersede_via_rpc(server: SMLServer) -> None:
    a = _call(server, "sml.write", {"type": "decision", "content": "v1", "author_agent": "kiro"})
    b = _call(server, "sml.write", {"type": "decision", "content": "v2", "author_agent": "kiro"})
    sup = _call(
        server,
        "sml.supersede",
        {"new_id": b["id"], "old_ids": [a["id"]]},
    )
    assert sup["ok"] is True
    assert sup["updated_ids"] == [a["id"]]
    a_read = _call(server, "sml.read", {"id": a["id"]})
    assert a_read["record"]["is_current"] is False
    assert a_read["record"]["superseded_by_id"] == b["id"]


def test_temporal_query_future_rejected(server: SMLServer) -> None:
    _call(server, "sml.write", {"type": "fact", "content": "x", "author_agent": "kiro"})
    res = _call(server, "sml.temporal_query", {"at": "2099-01-01T00:00:00.000Z"})
    assert res["ok"] is False
    assert res["error"]["category"] == "validation"


def test_startup_pack_empty_sections(server: SMLServer) -> None:
    res = _call(server, "sml.startup_pack", {})
    assert res["ok"] is True
    assert res["complete"] is False
    assert "project_nature" in res["empty_sections"]


def test_startup_pack_with_content(server: SMLServer) -> None:
    _call(
        server,
        "sml.write",
        {"type": "fact", "content": "Проект — общая память агентов.", "author_agent": "kiro"},
    )
    _call(
        server,
        "sml.write",
        {"type": "preference", "content": "Работать на русском.", "author_agent": "kiro"},
    )
    res = _call(server, "sml.startup_pack", {})
    assert res["ok"] is True
    assert len(res["sections"]["project_nature"]) == 1
    assert len(res["sections"]["preferences"]) == 1
    assert "project_nature" not in res["empty_sections"]


# --- Correlation id: несколько запросов подряд сохраняют id ---


def test_request_ids_preserved(server: SMLServer) -> None:
    ids = [42, 101, 7]
    for rid in ids:
        resp = handle_request(
            server,
            {
                "jsonrpc": "2.0",
                "id": rid,
                "method": "tools/call",
                "params": {"name": "sml.ping", "arguments": {}},
            },
        )
        assert resp["id"] == rid


# --- stdio loop ---


def test_stdio_loop_processes_multiple_requests(server: SMLServer) -> None:
    requests_in = "\n".join(
        [
            json.dumps({"jsonrpc": "2.0", "id": 1, "method": "tools/list"}),
            json.dumps(
                {
                    "jsonrpc": "2.0",
                    "id": 2,
                    "method": "tools/call",
                    "params": {"name": "sml.ping", "arguments": {}},
                }
            ),
            json.dumps({"jsonrpc": "2.0", "id": 3, "method": "exit"}),
        ]
    )
    stdin = io.StringIO(requests_in + "\n")
    stdout = io.StringIO()
    code = run_stdio_loop(server, stdin=stdin, stdout=stdout)
    assert code == 0
    out_lines = [line for line in stdout.getvalue().splitlines() if line.strip()]
    # ожидаем ответы на 2 запроса (на exit ответ не пишется)
    assert len(out_lines) == 2
    parsed = [json.loads(l) for l in out_lines]
    assert parsed[0]["id"] == 1
    assert "tools" in parsed[0]["result"]
    assert parsed[1]["id"] == 2
    assert parsed[1]["result"]["ok"] is True


def _framed_message(payload: dict) -> bytes:
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    return f"Content-Length: {len(body)}\r\n\r\n".encode("ascii") + body


def _parse_framed_messages(raw: bytes) -> list[dict]:
    messages: list[dict] = []
    pos = 0
    while pos < len(raw):
        header_end = raw.index(b"\r\n\r\n", pos)
        header = raw[pos:header_end].decode("ascii")
        content_length = int(header.split(":", 1)[1].strip())
        body_start = header_end + 4
        body_end = body_start + content_length
        messages.append(json.loads(raw[body_start:body_end].decode("utf-8")))
        pos = body_end
    return messages


def test_stdio_loop_supports_content_length_framing(server: SMLServer) -> None:
    requests_in = b"".join(
        [
            _framed_message(
                {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "initialize",
                    "params": {"protocolVersion": "2025-06-18"},
                }
            ),
            _framed_message(
                {
                    "jsonrpc": "2.0",
                    "method": "notifications/initialized",
                    "params": {},
                }
            ),
            _framed_message({"jsonrpc": "2.0", "id": 2, "method": "tools/list"}),
            _framed_message({"jsonrpc": "2.0", "id": 3, "method": "exit"}),
        ]
    )
    stdin = io.BytesIO(requests_in)
    stdout = io.BytesIO()

    code = run_stdio_loop(server, stdin=stdin, stdout=stdout)

    assert code == 0
    parsed = _parse_framed_messages(stdout.getvalue())
    assert len(parsed) == 2
    assert parsed[0]["id"] == 1
    assert parsed[0]["result"]["protocolVersion"] == "2025-06-18"
    assert parsed[1]["id"] == 2
    assert "tools" in parsed[1]["result"]


def test_stdio_loop_bad_json(server: SMLServer) -> None:
    stdin = io.StringIO("{not valid json\n")
    stdout = io.StringIO()
    run_stdio_loop(server, stdin=stdin, stdout=stdout)
    parsed = json.loads(stdout.getvalue().strip())
    assert parsed["error"]["code"] == -32700
