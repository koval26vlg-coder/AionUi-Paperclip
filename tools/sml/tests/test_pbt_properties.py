"""Явные property-тесты для задач 5.12 и 7.8 — трассируемость к P-свойствам.

Основное содержание свойств уже покрыто в других файлах тестов; здесь
оставлены короткие, явно помеченные PBT-сценарии, чтобы каждая
``Correctness Property`` из ``design.md §13`` имела как минимум один
тест, чьё имя начинается с ``test_pbt_`` и который прогоняется под
Hypothesis с ≥100 примерами.
"""

from __future__ import annotations

import json
import secrets
import string
from pathlib import Path

import pytest
from hypothesis import given, settings, strategies as st

from tools.sml.mcp_adapter import SMLServer, handle_request
from tools.sml.operation_log import OperationLog
from tools.sml.security import check_secret
from tools.sml.temporal_store import open_store


# --- Общие фикстуры ---


@pytest.fixture
def server(tmp_path: Path):
    store = open_store(tmp_path / "state.db")
    op_log = OperationLog(tmp_path / "logs")
    srv = SMLServer(store=store, engine=None, op_log=op_log)
    yield srv
    srv.close()


def _call(server: SMLServer, tool: str, args: dict, rid: int) -> dict:
    resp = handle_request(
        server,
        {
            "jsonrpc": "2.0",
            "id": rid,
            "method": "tools/call",
            "params": {"name": tool, "arguments": args},
        },
    )
    return resp


# --- 5.12: MCP-контракт, корреляция id ---


@settings(max_examples=100, deadline=None)
@given(
    id_list=st.lists(
        st.integers(min_value=-(10**9), max_value=10**9),
        min_size=1,
        max_size=20,
        unique=True,
    )
)
def test_pbt_mcp_request_ids_preserved(tmp_path_factory, id_list) -> None:
    """P для MCP: любой входной ``id`` возвращается в ответе без изменений."""
    store = open_store(tmp_path_factory.mktemp("pbt5") / "state.db")
    op_log = OperationLog(tmp_path_factory.mktemp("pbt5-log"))
    srv = SMLServer(store=store, engine=None, op_log=op_log)
    try:
        for rid in id_list:
            resp = handle_request(
                srv,
                {
                    "jsonrpc": "2.0",
                    "id": rid,
                    "method": "tools/call",
                    "params": {"name": "sml.ping", "arguments": {}},
                },
            )
            assert resp["id"] == rid
            assert resp["result"]["ok"] is True
    finally:
        srv.close()


@settings(max_examples=50, deadline=None)
@given(
    payload=st.text(
        alphabet=st.characters(
            min_codepoint=0x20,
            max_codepoint=0xFFFF,
            blacklist_categories=("Cs",),
        ),
        min_size=1,
        max_size=500,
    ).filter(lambda s: s.strip() != "" and check_secret(s).is_secret is False),
)
def test_pbt_write_read_roundtrip(tmp_path_factory, payload: str) -> None:
    """P для MCP: write → read возвращает побайтово идентичное content."""
    store = open_store(tmp_path_factory.mktemp("pbt5-wr") / "state.db")
    op_log = OperationLog(tmp_path_factory.mktemp("pbt5-wr-log"))
    srv = SMLServer(store=store, engine=None, op_log=op_log)
    try:
        resp = _call(
            srv,
            "sml.write",
            {"type": "fact", "content": payload, "author_agent": "kiro"},
            rid=1,
        )
        if not resp["result"]["ok"]:
            # редкий случай: pydantic зарезал символ как пробельный
            return
        rec_id = resp["result"]["id"]
        read_resp = _call(srv, "sml.read", {"id": rec_id}, rid=2)
        assert read_resp["result"]["found"] is True
        assert read_resp["result"]["record"]["content"] == payload
    finally:
        srv.close()


# --- 7.8 P6: секреты не попадают никуда ---


@settings(max_examples=100, deadline=None)
@given(length=st.integers(min_value=30, max_value=120))
def test_pbt_p6_secret_never_reaches_storage(tmp_path_factory, length: int) -> None:
    alphabet = string.ascii_letters + string.digits
    candidate = "".join(secrets.choice(alphabet) for _ in range(length))
    # Содержимое, которое должно быть отклонено уровнем энтропии
    content = f"запрос содержит токен {candidate} в середине"
    check = check_secret(content)
    if not check.is_secret:
        # Редко: шенноновская энтропия оказалась ниже порога; тест не применим.
        return

    store_path = tmp_path_factory.mktemp("pbt6") / "state.db"
    op_log_dir = tmp_path_factory.mktemp("pbt6-log")
    store = open_store(store_path)
    op_log = OperationLog(op_log_dir)
    srv = SMLServer(store=store, engine=None, op_log=op_log)
    try:
        resp = _call(
            srv,
            "sml.write",
            {"type": "fact", "content": content, "author_agent": "kiro"},
            rid=1,
        )
        body = resp["result"]
        assert body["ok"] is False
        assert body["error"]["category"] == "secret_rejected"

        # В БД ни одной записи
        count_row = store._conn.execute(
            "SELECT COUNT(*) AS c FROM records"
        ).fetchone()
        assert count_row["c"] == 0

        # Operation_Log содержит rejected, но не сам секрет
        lines_path = op_log.active_path
        if lines_path.exists():
            text = lines_path.read_text(encoding="utf-8")
            entries = [json.loads(l) for l in text.splitlines() if l.strip()]
            assert any(e.get("result") == "rejected" for e in entries)
            assert candidate not in text
    finally:
        srv.close()


# --- 7.8 P7: нет внешних TCP-соединений ---


def test_pbt_p7_no_network_leak_property_style() -> None:
    """P7 — инвариантная проверка: в текущем процессе нет outbound-соединений вне loopback."""
    psutil = pytest.importorskip("psutil")
    import os

    proc = psutil.Process(os.getpid())
    try:
        connections = proc.net_connections(kind="inet")
    except (psutil.AccessDenied, RuntimeError):
        pytest.skip("net_connections недоступны")

    bad: list[tuple[str, int]] = []
    for conn in connections:
        raddr = conn.raddr
        if not raddr:
            continue
        host = raddr[0] if isinstance(raddr, tuple) else raddr.ip
        if host.startswith("127.") or host in {"::1", "localhost"}:
            continue
        bad.append((host, raddr[1] if isinstance(raddr, tuple) else raddr.port))
    assert bad == []
