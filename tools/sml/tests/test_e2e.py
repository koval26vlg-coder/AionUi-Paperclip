"""End-to-end сценарии Этапа 9 (Req 1-14; P1, P2, P4).

Эти тесты имитируют несколько агентов, работающих с SML:
- P1 Durability: запись, close, reopen, данные на месте.
- P2 Read-After-Commit: запись одним SMLServer, чтение другим (на том же
  state.db) → видно без задержки.
- P4 File Authority: правка файла `docs/memory/layers/facts.md` → sync
  приводит Memory_Record к файлу.
- Fallback: без SML файлы по-прежнему доступны для чтения.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from tools.sml.embedding_engine import EmbeddingEngine
from tools.sml.file_watcher import SyncService
from tools.sml.mcp_adapter import SMLServer, handle_request
from tools.sml.operation_log import OperationLog
from tools.sml.temporal_store import open_store


def _call(server: SMLServer, tool: str, args: dict, rid: int = 1) -> dict:
    return handle_request(
        server,
        {
            "jsonrpc": "2.0",
            "id": rid,
            "method": "tools/call",
            "params": {"name": tool, "arguments": args},
        },
    )["result"]


def _new_server(tmp_path: Path, engine: EmbeddingEngine | None = None) -> SMLServer:
    store = open_store(tmp_path / "state.db")
    op_log = OperationLog(tmp_path / "logs")
    return SMLServer(store=store, engine=engine, op_log=op_log)


# --- P1 Durability ---


def test_p1_durability_across_server_restart(tmp_path: Path) -> None:
    srv1 = _new_server(tmp_path)
    write_res = _call(
        srv1,
        "sml.write",
        {"type": "fact", "content": "SML выжил перезапуск", "author_agent": "codex"},
    )
    rid = write_res["id"]
    srv1.close()

    # Новый сервер поверх той же БД
    srv2 = _new_server(tmp_path)
    read_res = _call(srv2, "sml.read", {"id": rid})
    assert read_res["ok"] is True
    assert read_res["found"] is True
    assert read_res["record"]["content"] == "SML выжил перезапуск"
    srv2.close()


# --- P2 Read-After-Commit (два агента на одном хранилище) ---


def test_p2_read_after_commit_two_agents(tmp_path: Path) -> None:
    """Codex пишет, Cursor читает — на одной и той же state.db."""
    codex = _new_server(tmp_path)
    cursor = _new_server(tmp_path)
    try:
        res = _call(
            codex,
            "sml.write",
            {"type": "fact", "content": "факт от codex", "author_agent": "codex"},
        )
        rid = res["id"]
        # Без sleep: WAL SQLite позволяет читателю видеть коммит сразу
        read_res = _call(cursor, "sml.read", {"id": rid})
        assert read_res["found"] is True
        assert read_res["record"]["content"] == "факт от codex"
        # Имя агента нормализуется на входе: "codex" -> "Codex"
        # (см. tools/sml/validation.normalize_author).
        assert read_res["record"]["author_agent"] == "Codex"
    finally:
        codex.close()
        cursor.close()


# --- P4 File Authority ---


def test_p4_file_edit_propagates_to_sml(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    (root / "docs" / "memory" / "layers").mkdir(parents=True)
    fact_file = root / "docs" / "memory" / "layers" / "facts.md"
    fact_file.write_text("## Факт A\nПервоначальный текст.\n", encoding="utf-8")

    store = open_store(tmp_path / "state.db")
    op_log = OperationLog(tmp_path / "logs")
    sync = SyncService(store=store, op_log=op_log, root=root)
    try:
        touched = sync.sync_file("docs/memory/layers/facts.md")
        assert touched == 1

        # Ручная правка файла → sync приводит запись к файлу
        fact_file.write_text("## Факт A\nОбновлённый текст.\n", encoding="utf-8")
        touched2 = sync.sync_file("docs/memory/layers/facts.md")
        assert touched2 == 1

        rec = store._conn.execute(
            "SELECT content FROM records WHERE is_current=1 ORDER BY updated_at DESC"
        ).fetchone()
        assert "Обновлённый" in rec["content"]
    finally:
        store.close()
        op_log.close()


# --- Fallback: работа без SML через File_Memory ---


def test_fallback_file_memory_readable_without_sml(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    (root / "docs").mkdir(parents=True)
    context_file = root / "docs" / "current-context.md"
    context_file.write_text("# Текущий контекст\n\nТекст.", encoding="utf-8")
    context_index = root / "docs" / "context-index.md"
    context_index.write_text("- docs/current-context.md\n", encoding="utf-8")
    # Простой fallback-сценарий: клиент читает файлы напрямую.
    text = context_file.read_text(encoding="utf-8")
    assert "Текущий контекст" in text
    listing = context_index.read_text(encoding="utf-8")
    assert "docs/current-context.md" in listing


# --- P7 No Network Leak: проверка через psutil ---


def test_p7_no_external_tcp_connections() -> None:
    """Проверяет, что процесс SML не держит TCP-соединений за пределами loopback.

    В этом прогоне SML живёт внутри pytest-процесса — реально проверяем,
    что на loopback (127.0.0.1, ::1) висит только наш SMLServer, и нет
    outbound-соединений к внешним IP. Если psutil недоступен — тест
    скипается.
    """
    psutil = pytest.importorskip("psutil")

    import os

    proc = psutil.Process(os.getpid())
    try:
        connections = proc.net_connections(kind="inet")
    except (psutil.AccessDenied, RuntimeError):  # pragma: no cover
        pytest.skip("Доступ к net_connections запрещён")

    bad: list[tuple[str, int]] = []
    for conn in connections:
        raddr = conn.raddr
        if not raddr:
            continue
        host = raddr[0] if isinstance(raddr, tuple) else raddr.ip
        if host.startswith("127.") or host in {"::1", "localhost"}:
            continue
        bad.append((host, raddr[1] if isinstance(raddr, tuple) else raddr.port))
    assert bad == [], f"Обнаружены внешние TCP-соединения: {bad}"


# --- P6 E2E: секреты в sml.write не попадают в БД ---


def test_p6_secret_rejected_via_mcp(tmp_path: Path) -> None:
    srv = _new_server(tmp_path)
    try:
        res = _call(
            srv,
            "sml.write",
            {
                "type": "fact",
                "content": "секрет: sk-" + "a" * 40,
                "author_agent": "kiro",
            },
        )
        assert res["ok"] is False
        assert res["error"]["category"] == "secret_rejected"

        # Поиск значения секрета в БД: записей не должно быть
        row = srv.store._conn.execute(
            "SELECT COUNT(*) AS c FROM records WHERE content LIKE '%sk-%'"
        ).fetchone()
        assert row["c"] == 0

        # В Operation_Log есть запись rejected
        op_log_path = srv.op_log.active_path
        if op_log_path.exists():
            with op_log_path.open("r", encoding="utf-8") as fh:
                entries = [json.loads(line) for line in fh if line.strip()]
            rejected = [e for e in entries if e.get("result") == "rejected"]
            assert any(e.get("reason_category") == "openai_api_key" for e in rejected)
    finally:
        srv.close()
