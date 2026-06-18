"""Тесты полнотекстового фоллбэка (FTS5), когда семантика недоступна.

Покрывает:
- ``TemporalStore.text_search`` — прямой FTS5-поиск по содержимому;
- ``sml.semantic_query`` через адаптер с ``engine=None`` — деградация на
  текстовый поиск (``mode="text"``) вместо падения;
- безопасную обработку пустых/мусорных запросов.
"""

from __future__ import annotations

from pathlib import Path

from tools.sml.mcp_adapter import SMLServer, handle_request
from tools.sml.operation_log import OperationLog
from tools.sml.temporal_store import make_new_record, open_store


def _call(server: SMLServer, tool: str, args: dict) -> dict:
    return handle_request(
        server,
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {"name": tool, "arguments": args},
        },
    )["result"]


def _server_no_engine(tmp_path: Path) -> SMLServer:
    store = open_store(tmp_path / "state.db")
    op_log = OperationLog(tmp_path / "logs")
    return SMLServer(store=store, engine=None, op_log=op_log)


def _seed(server: SMLServer) -> None:
    for content in [
        "Конверсия за неделю по категориям и менеджерам в Bitrix24",
        "Ежедневный бэкап базы памяти SML с ротацией копий",
        "Нормализация имён агентов в общей памяти",
    ]:
        server.store.insert(
            make_new_record(type="fact", content=content, author_agent="codex")
        )


def test_text_search_finds_by_word(tmp_path: Path) -> None:
    server = _server_no_engine(tmp_path)
    try:
        _seed(server)
        pairs = server.store.text_search("конверсия", limit=5)
        assert pairs, "ожидался хотя бы один результат"
        top_record, top_score = pairs[0]
        assert "Конверси" in top_record.content
        assert 0.0 < top_score <= 1.0
    finally:
        server.close()


def test_text_search_prefix_match(tmp_path: Path) -> None:
    server = _server_no_engine(tmp_path)
    try:
        _seed(server)
        # префиксный матч: "бэкап" найдёт запись про бэкапы
        pairs = server.store.text_search("бэкап ротация", limit=5)
        assert any("бэкап" in r.content.lower() for r, _ in pairs)
    finally:
        server.close()


def test_text_search_empty_query_returns_empty(tmp_path: Path) -> None:
    server = _server_no_engine(tmp_path)
    try:
        _seed(server)
        assert server.store.text_search("", limit=5) == []
        assert server.store.text_search("   ", limit=5) == []
        # одиночные короткие токены отбрасываются
        assert server.store.text_search("я", limit=5) == []
    finally:
        server.close()


def test_text_search_special_chars_do_not_crash(tmp_path: Path) -> None:
    server = _server_no_engine(tmp_path)
    try:
        _seed(server)
        # спецсимволы синтаксиса FTS5 не должны вызывать ошибку
        for q in ['конверсия"', "memory AND (", "* OR *", 'a "b" c*']:
            server.store.text_search(q, limit=5)  # не падает
    finally:
        server.close()


def test_semantic_query_falls_back_to_text(tmp_path: Path) -> None:
    server = _server_no_engine(tmp_path)
    try:
        _seed(server)
        res = _call(server, "sml.semantic_query", {"query": "нормализация агентов"})
        assert res["ok"] is True
        assert res["mode"] == "text"
        assert res["degraded"] is True
        assert len(res["results"]) >= 1
        assert "relevance_score" in res["results"][0]
    finally:
        server.close()


def test_semantic_query_fallback_excludes_superseded(tmp_path: Path) -> None:
    server = _server_no_engine(tmp_path)
    try:
        rec = make_new_record(
            type="fact", content="устаревший факт про конверсию", author_agent="codex"
        )
        server.store.insert(rec)
        # помечаем запись неактуальной напрямую через update
        server.store.update_fields(rec.id, is_current=False)
        res = _call(server, "sml.semantic_query", {"query": "конверсию"})
        ids = [r["record"]["id"] for r in res["results"]]
        assert rec.id not in ids
    finally:
        server.close()
