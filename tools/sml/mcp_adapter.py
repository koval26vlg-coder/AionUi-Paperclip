"""MCP_Adapter — newline-stdio MCP-сервер SML.

Реализован как легковесный JSON-RPC 2.0 поверх stdin/stdout, совместимый
с ``mcpServers`` конфигами Codex/Cursor/Kiro при транспорте ``stdio``.

Публикует набор из 10 MCP-инструментов (см. ``_TOOLS`` ниже). Протокол
минимальный, но покрывает всё, что нужно MCP-клиентам:

- ``initialize`` — базовое рукопожатие.
- ``tools/list`` — манифест всех инструментов.
- ``tools/call`` — вызов конкретного инструмента.
- ``shutdown`` / ``exit`` — штатное завершение.

Любая ошибка (ValidationError, SMLError, неизвестный метод, плохой JSON)
оборачивается в JSON-RPC ``error`` с телом ``{ok: false, error:
{category, message, operation_id}}``. Для ``tools/call`` ответ дополнительно
дублируется в стандартный MCP-блок ``result.content`` как JSON-текст; это
нужно строгим MCP-клиентам вроде Codex, а старые клиенты продолжают читать
верхнеуровневые поля ``ok`` и payload.

Ссылки на требования: Req 1.1, Req 1.2, Req 1.4, Req 1.5, Req 1.6, Req 2.5,
Req 9.3.
"""

from __future__ import annotations

import json
import os
import sys
import time
import traceback
from pathlib import Path
from typing import Any, Callable, Dict, Optional

from . import __version__
from .embedding_engine import (
    DEFAULT_LIMIT,
    MAX_LIMIT,
    MAX_QUERY_LEN,
    EmbeddingEngine,
    build_default_engine,
)
from .errors import (
    ConflictError,
    IOErrorSML,
    NotFoundError,
    SMLError,
    SecretRejectedError,
    UnsupportedError,
    ValidationError,
)
from .ids import new_id, validate_id
from .models import MemoryRecord
from .operation_log import OperationLog
from .response import error_response, ok_response
from .temporal_store import TemporalStore, make_new_record, open_store
from .timefmt import now_utc_ms
from .validation import MEMORY_TYPE_VALUES, validate_source_lines, validate_tags
from .write_guard import guard_secret

__all__ = ["SMLServer", "main"]


# ---------------------------------------------------------------------------
# JSON-RPC error codes
# ---------------------------------------------------------------------------

PARSE_ERROR = -32700
INVALID_REQUEST = -32600
METHOD_NOT_FOUND = -32601
INVALID_PARAMS = -32602
INTERNAL_ERROR = -32603
SMLError_RPC = -32000  # общий код для SML-ошибок внутри tools/call


# ---------------------------------------------------------------------------
# Пути по умолчанию
# ---------------------------------------------------------------------------


def _default_paths() -> tuple[Path, Path, Path]:
    root = Path(os.environ.get("SML_ROOT", "D:/AionUi-Paperclip"))
    return (
        root / "var" / "sml" / "state.db",
        root / "var" / "sml" / "lance",
        root / "logs",
    )


# ---------------------------------------------------------------------------
# SMLServer
# ---------------------------------------------------------------------------


class SMLServer:
    """Stateful-контейнер всех компонентов SML для MCP-адаптера."""

    def __init__(
        self,
        *,
        store: TemporalStore,
        engine: Optional[EmbeddingEngine],
        op_log: OperationLog,
        default_agent: str = "sml",
    ) -> None:
        self.store = store
        self.engine = engine
        self.op_log = op_log
        self.default_agent = default_agent
        self._started_at = time.time()
        self._op_counter = 0

    @classmethod
    def from_defaults(cls) -> "SMLServer":
        state_db, lance_path, logs_dir = _default_paths()
        store = open_store(state_db)
        try:
            engine: Optional[EmbeddingEngine] = build_default_engine(lance_path)
        except IOErrorSML:
            # Если Ollama недоступна, семантика отключена, но остальные инструменты
            # работают. `sml.semantic_query` в таком случае вернёт ошибку.
            engine = None
        op_log = OperationLog(logs_dir)
        return cls(store=store, engine=engine, op_log=op_log)

    def close(self) -> None:
        self.store.close()
        self.op_log.close()

    def next_op_id(self) -> str:
        self._op_counter += 1
        return f"{now_utc_ms()}-sml-{self._op_counter}"

    @property
    def uptime_seconds(self) -> int:
        return int(time.time() - self._started_at)


# ---------------------------------------------------------------------------
# Инструменты
# ---------------------------------------------------------------------------


_TOOL_SCHEMAS: dict[str, dict[str, Any]] = {
    "sml.ping": {
        "description": "Проверка доступности SML: версия и uptime.",
        "input_schema": {
            "type": "object",
            "additionalProperties": False,
            "properties": {},
        },
    },
    "sml.write": {
        "description": "Добавить Memory_Record (факт, решение, журнал, задача и т.д.).",
        "input_schema": {
            "type": "object",
            "required": ["type", "content", "author_agent"],
            "additionalProperties": False,
            "properties": {
                "type": {"type": "string", "enum": sorted(MEMORY_TYPE_VALUES)},
                "content": {"type": "string", "minLength": 1, "maxLength": 10000},
                "author_agent": {"type": "string", "minLength": 1, "maxLength": 128},
                "tags": {"type": "array", "items": {"type": "string"}, "maxItems": 20},
                "supersedes_id": {"type": ["string", "null"]},
                "source_file": {"type": ["string", "null"]},
                "source_lines": {"type": ["string", "null"]},
            },
        },
    },
    "sml.read": {
        "description": "Получить Memory_Record по id.",
        "input_schema": {
            "type": "object",
            "required": ["id"],
            "additionalProperties": False,
            "properties": {"id": {"type": "string"}},
        },
    },
    "sml.semantic_query": {
        "description": "Семантический поиск Memory_Record по русскоязычному запросу.",
        "input_schema": {
            "type": "object",
            "required": ["query"],
            "additionalProperties": False,
            "properties": {
                "query": {
                    "type": "string",
                    "minLength": 1,
                    "maxLength": MAX_QUERY_LEN,
                },
                "limit": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": MAX_LIMIT,
                    "default": DEFAULT_LIMIT,
                },
                "include_superseded": {"type": "boolean", "default": False},
                "min_score": {
                    "type": "number",
                    "minimum": 0.0,
                    "maximum": 1.0,
                    "default": 0.5,
                },
            },
        },
    },
    "sml.temporal_query": {
        "description": "Состояние Memory_Record на указанную метку времени.",
        "input_schema": {
            "type": "object",
            "required": ["at"],
            "additionalProperties": False,
            "properties": {
                "at": {"type": "string"},
                "type_filter": {"type": ["string", "null"]},
                "only_current_at": {"type": "boolean", "default": True},
                "limit": {"type": "integer", "minimum": 1, "maximum": 500, "default": 100},
            },
        },
    },
    "sml.supersede": {
        "description": "Атомарно пометить old_ids как устаревшие и связать их с new_id.",
        "input_schema": {
            "type": "object",
            "required": ["new_id", "old_ids"],
            "additionalProperties": False,
            "properties": {
                "new_id": {"type": "string"},
                "old_ids": {
                    "type": "array",
                    "minItems": 1,
                    "maxItems": 50,
                    "items": {"type": "string"},
                },
            },
        },
    },
    "sml.add_decision": {
        "description": "Записать Memory_Record типа decision (writer docs/decisions.md в Этапе 6).",
        "input_schema": {
            "type": "object",
            "required": ["title", "context", "decision", "author_agent"],
            "additionalProperties": False,
            "properties": {
                "title": {"type": "string", "minLength": 1, "maxLength": 200},
                "context": {"type": "string", "minLength": 1, "maxLength": 4000},
                "decision": {"type": "string", "minLength": 1, "maxLength": 4000},
                "author_agent": {"type": "string", "minLength": 1, "maxLength": 128},
                "tags": {"type": "array", "items": {"type": "string"}, "maxItems": 20},
            },
        },
    },
    "sml.add_log": {
        "description": "Записать Memory_Record типа agent_log (writer docs/agent-log/ в Этапе 6).",
        "input_schema": {
            "type": "object",
            "required": ["author_agent", "request", "result"],
            "additionalProperties": False,
            "properties": {
                "date": {"type": "string"},
                "author_agent": {"type": "string", "minLength": 1, "maxLength": 128},
                "request": {"type": "string", "minLength": 1, "maxLength": 4000},
                "plan": {"type": "string", "maxLength": 4000},
                "result": {"type": "string", "minLength": 1, "maxLength": 8000},
                "changed_files": {"type": "array", "items": {"type": "string"}, "maxItems": 200},
                "risks": {"type": "string", "maxLength": 2000},
                "next_steps": {"type": "string", "maxLength": 2000},
            },
        },
    },
    "sml.build_context_pack": {
        "description": "Пересобрать docs/context-packs/context-pack-latest.md (Этап 6).",
        "input_schema": {
            "type": "object",
            "additionalProperties": False,
            "properties": {"reason": {"type": "string", "maxLength": 200}},
        },
    },
    "sml.startup_pack": {
        "description": "Вернуть стартовый контекстный пакет из 6 разделов.",
        "input_schema": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "max_log_entries": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 50,
                    "default": 10,
                }
            },
        },
    },
}


# ---------------------------------------------------------------------------
# Реализация инструментов
# ---------------------------------------------------------------------------


def _tool_ping(server: SMLServer, params: dict[str, Any], op_id: str) -> dict[str, Any]:
    records_total = server.store.count()
    degraded = records_total > 10_000
    server.op_log.log(
        agent=server.default_agent, op="ping", result="success", operation_id=op_id
    )
    return ok_response(
        {
            "version": f"sml-{__version__}",
            "uptime_seconds": server.uptime_seconds,
            "records_total": records_total,
            "degraded": degraded,
        }
    )


def _tool_write(server: SMLServer, params: dict[str, Any], op_id: str) -> dict[str, Any]:
    author = params.get("author_agent", server.default_agent)
    content = params["content"]
    guard_secret(
        agent=author,
        op="write",
        text=content,
        op_log=server.op_log,
        operation_id=op_id,
    )
    record = make_new_record(
        type=params["type"],
        content=content,
        author_agent=author,
        tags=params.get("tags") or [],
        source_file=params.get("source_file"),
        source_lines=params.get("source_lines"),
    )
    server.store.insert(record)
    supersedes_id = params.get("supersedes_id")
    if supersedes_id:
        server.store.supersede(record.id, [supersedes_id])

    if server.engine is not None:
        try:
            server.engine.upsert(record.id, record.content)
        except IOErrorSML:
            # Embedding-сбой не откатывает SQLite — переиндексация в Этапе 6
            pass

    server.op_log.log(
        agent=author,
        op="write",
        result="success",
        record_id=record.id,
        operation_id=op_id,
    )
    return ok_response(
        {
            "id": record.id,
            "created_at": record.created_at,
            "updated_at": record.updated_at,
            "is_current": True,
            "supersedes_id": supersedes_id,
        }
    )


def _tool_read(server: SMLServer, params: dict[str, Any], op_id: str) -> dict[str, Any]:
    record_id = params["id"]
    validate_id(record_id)
    record = server.store.read_by_id(record_id)
    server.op_log.log(
        agent=server.default_agent,
        op="read",
        result="success",
        record_id=record_id,
        operation_id=op_id,
    )
    if record is None:
        return ok_response({"found": False})
    return ok_response({"found": True, "record": record.as_public_dict()})


def _tool_semantic_query(
    server: SMLServer, params: dict[str, Any], op_id: str
) -> dict[str, Any]:
    if server.engine is None:
        raise IOErrorSML(
            "Embedding_Engine не инициализирован (проверьте Ollama на 127.0.0.1:11434)"
        )
    query = params["query"]
    limit = int(params.get("limit", DEFAULT_LIMIT))
    include_superseded = bool(params.get("include_superseded", False))
    min_score = float(params.get("min_score", 0.5))
    hits = server.engine.search(
        query, limit=limit, min_score=min_score
    )
    results: list[dict[str, Any]] = []
    for hit in hits:
        record = server.store.read_by_id(hit.record_id)
        if record is None:
            continue
        if not include_superseded and not record.is_current:
            continue
        payload = record.as_public_dict()
        # поле relevance_score выдаётся рядом, не внутри record
        results.append({"record": payload, "relevance_score": hit.relevance_score})
    degraded = server.store.count() > 10_000
    server.op_log.log(
        agent=server.default_agent,
        op="semantic_query",
        result="success",
        operation_id=op_id,
    )
    return ok_response({"results": results, "degraded": degraded})


def _tool_temporal_query(
    server: SMLServer, params: dict[str, Any], op_id: str
) -> dict[str, Any]:
    records = server.store.query_at(
        params["at"],
        type_filter=params.get("type_filter"),
        only_current_at=bool(params.get("only_current_at", True)),
        limit=int(params.get("limit", 100)),
    )
    server.op_log.log(
        agent=server.default_agent,
        op="temporal_query",
        result="success",
        operation_id=op_id,
    )
    return ok_response(
        {"at": params["at"], "records": [r.as_public_dict() for r in records]}
    )


def _tool_supersede(
    server: SMLServer, params: dict[str, Any], op_id: str
) -> dict[str, Any]:
    new_id_ = params["new_id"]
    old_ids = params["old_ids"]
    if not isinstance(old_ids, list) or not old_ids:
        raise ValidationError.for_field("old_ids", "должен быть непустым списком")
    updated = server.store.supersede(new_id_, old_ids)
    server.op_log.log(
        agent=server.default_agent,
        op="supersede",
        result="success",
        record_id=new_id_,
        operation_id=op_id,
    )
    return ok_response({"updated_ids": updated, "updated_at": now_utc_ms()})


def _tool_add_decision(
    server: SMLServer, params: dict[str, Any], op_id: str
) -> dict[str, Any]:
    """Пишет Memory_Record типа decision и атомарно append'ит блок в
    ``docs/decisions.md`` (Req 13.3, Req 13.5)."""
    from .writers.decisions import append_decision

    author = params["author_agent"]
    title = params["title"]
    context_text = params["context"]
    decision_text = params["decision"]
    # detect секрета по конкатенированному контенту, чтобы гарантированно
    # проверить все три поля разом.
    all_text = f"{title}\n\n{context_text}\n\n{decision_text}"
    guard_secret(
        agent=author,
        op="add_decision",
        text=all_text,
        op_log=server.op_log,
        operation_id=op_id,
    )

    decisions_path = _default_paths()[0].parent.parent.parent / "docs" / "decisions.md"
    # Сначала создаём Memory_Record — с пустым source_file, чтобы при
    # ошибке IO файл не создавался.
    record = make_new_record(
        type="decision",
        content=all_text,
        author_agent=author,
        tags=params.get("tags") or [],
    )
    server.store.insert(record)

    try:
        start, end = append_decision(
            decisions_path,
            title=title,
            context=context_text,
            decision=decision_text,
            author_agent=author,
            date_utc=now_utc_ms()[:10],
            tags=params.get("tags") or [],
        )
        server.store.update_fields(
            record.id,
            source_file="docs/decisions.md",
            source_lines=f"{start}-{end}",
        )
    except (IOErrorSML, ConflictError) as exc:
        # IO-сбой — помечаем запись и репортим клиенту ошибку.
        server.op_log.log(
            agent=author,
            op="add_decision",
            result="error",
            record_id=record.id,
            reason_category=exc.category,
            operation_id=op_id,
        )
        raise

    if server.engine is not None:
        try:
            server.engine.upsert(record.id, all_text)
        except IOErrorSML:
            pass

    server.op_log.log(
        agent=author,
        op="add_decision",
        result="success",
        record_id=record.id,
        operation_id=op_id,
    )
    return ok_response(
        {
            "id": record.id,
            "source_file": "docs/decisions.md",
            "source_lines": f"{start}-{end}",
        }
    )


def _tool_add_log(
    server: SMLServer, params: dict[str, Any], op_id: str
) -> dict[str, Any]:
    """Пишет Memory_Record типа agent_log и создаёт файл в
    ``docs/agent-log/`` (Req 13.2, Req 13.5)."""
    from .writers.agent_log import create_log_file

    author = params["author_agent"]
    date_iso = params.get("date") or now_utc_ms()
    request_text = params["request"]
    result_text = params["result"]
    plan = params.get("plan")
    risks = params.get("risks")
    next_steps = params.get("next_steps")
    changed_files = params.get("changed_files") or []

    parts = [f"# Запрос\n{request_text}", f"# Результат\n{result_text}"]
    if plan:
        parts.append(f"# План\n{plan}")
    if risks:
        parts.append(f"# Риски\n{risks}")
    if next_steps:
        parts.append(f"# Следующему\n{next_steps}")
    content = "\n\n".join(parts)
    guard_secret(
        agent=author, op="add_log", text=content, op_log=server.op_log, operation_id=op_id
    )

    agent_log_dir = _default_paths()[0].parent.parent.parent / "docs" / "agent-log"
    record = make_new_record(
        type="agent_log", content=content, author_agent=author, tags=[]
    )
    server.store.insert(record)
    try:
        created_path = create_log_file(
            agent_log_dir,
            date_iso_ms=date_iso,
            author_agent=author,
            request=request_text,
            result=result_text,
            plan=plan,
            changed_files=changed_files,
            risks=risks,
            next_steps=next_steps,
        )
    except (IOErrorSML, ConflictError) as exc:
        server.op_log.log(
            agent=author,
            op="add_log",
            result="error",
            record_id=record.id,
            reason_category=exc.category,
            operation_id=op_id,
        )
        raise

    rel = created_path.relative_to(agent_log_dir.parent.parent)
    rel_posix = rel.as_posix()
    # source_lines = 1-N (весь файл)
    lines_total = created_path.read_text(encoding="utf-8").count("\n") + 1
    server.store.update_fields(
        record.id,
        source_file=rel_posix,
        source_lines=f"1-{lines_total}",
    )
    if server.engine is not None:
        try:
            server.engine.upsert(record.id, content)
        except IOErrorSML:
            pass
    server.op_log.log(
        agent=author,
        op="add_log",
        result="success",
        record_id=record.id,
        operation_id=op_id,
    )
    return ok_response({"id": record.id, "source_file": rel_posix})


def _tool_build_context_pack(
    server: SMLServer, params: dict[str, Any], op_id: str
) -> dict[str, Any]:
    """Собирает ``docs/context-packs/context-pack-latest.md`` из 6 разделов.

    Для каждого раздела берёт актуальный контент из файлов ``docs/`` —
    пока writer просто копирует содержимое основных источников истины.
    """
    from .writers.context_pack import build_and_write

    root = _default_paths()[0].parent.parent.parent
    pack_path = root / "docs" / "context-packs" / "context-pack-latest.md"
    source_files = [
        "AGENTS.md",
        "docs/current-context.md",
        "docs/tasks.md",
        "docs/decisions.md",
        "docs/memory/layers/facts.md",
        "docs/memory/layers/preferences.md",
        "docs/memory/layers/constraints.md",
        "docs/memory/layers/timeline.md",
    ]
    sections: list[tuple[str, str]] = []
    for rel in source_files:
        file_path = root / rel
        if not file_path.exists():
            continue
        try:
            content = file_path.read_text(encoding="utf-8")
        except OSError:
            continue
        sections.append((rel.replace("\\", "/"), content))

    build_and_write(pack_path, sections=sections, built_at=now_utc_ms())
    server.op_log.log(
        agent=server.default_agent,
        op="build_context_pack",
        result="success",
        operation_id=op_id,
    )
    return ok_response(
        {
            "source_file": "docs/context-packs/context-pack-latest.md",
            "updated_at": now_utc_ms(),
            "sections_written": len(sections),
        }
    )


def _tool_startup_pack(
    server: SMLServer, params: dict[str, Any], op_id: str
) -> dict[str, Any]:
    max_log_entries = int(params.get("max_log_entries", 10))
    section_limits = {
        "project_nature": 20,
        "decisions": 20,
        "active_tasks": 50,
        "preferences": 20,
        "constraints": 20,
        "recent_logs": max_log_entries,
    }
    type_for_section = {
        "project_nature": "fact",
        "decisions": "decision",
        "active_tasks": "task",
        "preferences": "preference",
        "constraints": "constraint",
        "recent_logs": "agent_log",
    }
    sections: dict[str, list[dict[str, Any]]] = {name: [] for name in section_limits}
    empty_sections: list[str] = []
    for name, tpe in type_for_section.items():
        limit = section_limits[name]
        rows = server.store._conn.execute(  # type: ignore[attr-defined]
            """
            SELECT id, type, content, author_agent, created_at, updated_at,
                   is_current, supersedes_id, superseded_by_id,
                   source_file, source_lines, tags_json
              FROM records
             WHERE type = :type AND deleted_at IS NULL AND is_current = 1
             ORDER BY updated_at DESC
             LIMIT :limit
            """,
            {"type": tpe, "limit": limit},
        ).fetchall()
        if not rows:
            empty_sections.append(name)
            continue
        import json as _json
        for row in rows:
            sections[name].append(
                {
                    "id": row["id"],
                    "type": row["type"],
                    "content": row["content"],
                    "author_agent": row["author_agent"],
                    "created_at": row["created_at"],
                    "updated_at": row["updated_at"],
                    "is_current": bool(row["is_current"]),
                    "tags": _json.loads(row["tags_json"] or "[]"),
                }
            )
    server.op_log.log(
        agent=server.default_agent,
        op="startup_pack",
        result="success",
        operation_id=op_id,
    )
    return ok_response(
        {
            "complete": len(empty_sections) == 0,
            "empty_sections": empty_sections,
            "sections": sections,
        }
    )


TOOL_IMPL: Dict[str, Callable[[SMLServer, dict[str, Any], str], dict[str, Any]]] = {
    "sml.ping": _tool_ping,
    "sml.write": _tool_write,
    "sml.read": _tool_read,
    "sml.semantic_query": _tool_semantic_query,
    "sml.temporal_query": _tool_temporal_query,
    "sml.supersede": _tool_supersede,
    "sml.add_decision": _tool_add_decision,
    "sml.add_log": _tool_add_log,
    "sml.build_context_pack": _tool_build_context_pack,
    "sml.startup_pack": _tool_startup_pack,
}


# ---------------------------------------------------------------------------
# JSON-RPC маршрутизация
# ---------------------------------------------------------------------------


def _rpc_error(code: int, message: str, id_: Any = None) -> dict[str, Any]:
    return {
        "jsonrpc": "2.0",
        "id": id_,
        "error": {"code": code, "message": message},
    }


def _rpc_result(result: Any, id_: Any) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": id_, "result": result}


def _mcp_tool_result(payload: dict[str, Any]) -> dict[str, Any]:
    """Возвращает результат tools/call в MCP-совместимой форме.

    Ранние клиенты Cursor/Kiro нормально принимали «плоский» JSON в result,
    но Codex MCP-мост ожидает стандартный ``content``. Чтобы не ломать уже
    работающие сценарии и тесты, оставляем исходные поля payload наверху и
    добавляем MCP-представление рядом.
    """
    result = dict(payload)
    result["content"] = [
        {
            "type": "text",
            "text": json.dumps(payload, ensure_ascii=False),
        }
    ]
    if payload.get("ok") is False:
        result["isError"] = True
    return result


def handle_request(server: SMLServer, request: dict[str, Any]) -> Optional[dict[str, Any]]:
    """Обрабатывает один JSON-RPC запрос. Возвращает ответ (dict) или None
    для уведомлений (без id).
    """
    if not isinstance(request, dict):
        return _rpc_error(INVALID_REQUEST, "Ожидается JSON-RPC 2.0")
    if request.get("jsonrpc") != "2.0":
        return _rpc_error(INVALID_REQUEST, "Ожидается JSON-RPC 2.0", request.get("id"))
    method = request.get("method")
    params = request.get("params") or {}
    id_ = request.get("id")

    if id_ is None and isinstance(method, str) and method.startswith("notifications/"):
        return None

    if method == "initialize":
        requested_protocol = params.get("protocolVersion")
        protocol_version = (
            requested_protocol if isinstance(requested_protocol, str) else "2025-06-18"
        )
        return _rpc_result(
            {
                "protocolVersion": protocol_version,
                "serverInfo": {"name": "sml", "version": __version__},
                "capabilities": {"tools": {}},
            },
            id_,
        )
    if method == "tools/list":
        tools_manifest = [
            {
                "name": name,
                "description": schema["description"],
                "inputSchema": schema["input_schema"],
            }
            for name, schema in _TOOL_SCHEMAS.items()
        ]
        return _rpc_result({"tools": tools_manifest}, id_)
    if method == "tools/call":
        tool_name = params.get("name")
        tool_args = params.get("arguments") or {}
        if tool_name not in TOOL_IMPL:
            op_id = server.next_op_id()
            return _rpc_result(
                _mcp_tool_result(
                    error_response(
                        UnsupportedError(f"Неизвестный инструмент: {tool_name!r}"),
                        operation_id=op_id,
                    )
                ),
                id_,
            )
        op_id = server.next_op_id()
        try:
            result_payload = TOOL_IMPL[tool_name](server, tool_args, op_id)
        except SMLError as exc:
            return _rpc_result(_mcp_tool_result(error_response(exc, op_id)), id_)
        except (ValueError, TypeError) as exc:
            # pydantic ValidationError и ручные ValueError из валидаторов
            # мапим в категорию validation (Req 2.5, Req 4.3).
            server.op_log.log(
                agent=server.default_agent,
                op="write" if tool_name in {"sml.write", "sml.add_decision", "sml.add_log"} else "read",
                result="rejected",
                reason_category="validation",
                operation_id=op_id,
            )
            return _rpc_result(
                _mcp_tool_result(error_response(ValidationError(str(exc)), op_id)), id_
            )
        except Exception as exc:  # pragma: no cover - внутренний сбой
            server.op_log.log(
                agent=server.default_agent,
                op="ping",  # неизвестная операция — используем обобщённый тег
                result="error",
                reason_category="io_error",
                operation_id=op_id,
            )
            return _rpc_result(
                _mcp_tool_result(
                    error_response(
                        IOErrorSML(f"{type(exc).__name__}: {exc}"),
                        operation_id=op_id,
                    )
                ),
                id_,
            )
        return _rpc_result(_mcp_tool_result(result_payload), id_)
    if method == "shutdown":
        return _rpc_result(None, id_)
    if method == "exit":
        return None
    return _rpc_error(METHOD_NOT_FOUND, f"Неизвестный метод: {method!r}", id_)


# ---------------------------------------------------------------------------
# Цикл stdio
# ---------------------------------------------------------------------------


def _as_text(raw: Any) -> str:
    if isinstance(raw, bytes):
        return raw.decode("utf-8")
    return str(raw)


def _is_eof(raw: Any) -> bool:
    return raw == b"" or raw == ""


def _read_nonempty_line(stdin: Any) -> Any:
    while True:
        line = stdin.readline()
        if _is_eof(line):
            return line
        if _as_text(line).strip():
            return line


def _write_bytes(stdout: Any, payload: bytes) -> None:
    try:
        stdout.write(payload)
    except TypeError:
        stdout.write(payload.decode("utf-8"))
    stdout.flush()


def _write_response(stdout: Any, response: dict[str, Any], *, framed: bool) -> None:
    body = json.dumps(response, ensure_ascii=False).encode("utf-8")
    if framed:
        header = f"Content-Length: {len(body)}\r\n\r\n".encode("ascii")
        _write_bytes(stdout, header + body)
        return
    _write_bytes(stdout, body + b"\n")


def _read_framed_body(stdin: Any, first_header_line: Any) -> Optional[str]:
    content_length: Optional[int] = None
    line = first_header_line
    while not _is_eof(line):
        text = _as_text(line).strip()
        if not text:
            break
        name, sep, value = text.partition(":")
        if sep and name.lower() == "content-length":
            try:
                content_length = int(value.strip())
            except ValueError:
                return None
        line = stdin.readline()

    if content_length is None:
        return None
    body = stdin.read(content_length)
    if _is_eof(body):
        return None
    return _as_text(body)


def _handle_message_text(
    server: SMLServer, message_text: str
) -> tuple[Optional[dict[str, Any]], bool]:
    try:
        request = json.loads(message_text)
    except json.JSONDecodeError as exc:
        return _rpc_error(PARSE_ERROR, f"Неверный JSON: {exc}"), False

    response = handle_request(server, request)
    exit_requested = isinstance(request, dict) and request.get("method") == "exit"
    return response, exit_requested


def _run_line_loop(server: SMLServer, stdin: Any, stdout: Any, first_line: Any) -> int:
    raw_line = first_line
    while not _is_eof(raw_line):
        line = _as_text(raw_line).strip()
        if line:
            response, exit_requested = _handle_message_text(server, line)
            if exit_requested:
                break
            if response is not None:
                _write_response(stdout, response, framed=False)
        raw_line = stdin.readline()
    return 0


def _run_framed_loop(server: SMLServer, stdin: Any, stdout: Any, first_line: Any) -> int:
    header_line = first_line
    while not _is_eof(header_line):
        body_text = _read_framed_body(stdin, header_line)
        if body_text is None:
            response = _rpc_error(PARSE_ERROR, "Неверное framed stdio сообщение")
            _write_response(stdout, response, framed=True)
            return 1
        response, exit_requested = _handle_message_text(server, body_text)
        if exit_requested:
            break
        if response is not None:
            _write_response(stdout, response, framed=True)
        header_line = _read_nonempty_line(stdin)
    return 0


def run_stdio_loop(server: SMLServer, stdin=None, stdout=None) -> int:
    """Читает JSON-RPC из stdin, пишет ответы в stdout.

    Поддерживает оба варианта stdio, которые встречаются у MCP-клиентов:
    newline-delimited JSON и framed сообщения с ``Content-Length``.
    """
    stdin = stdin or sys.stdin
    stdout = stdout or sys.stdout
    first_line = _read_nonempty_line(stdin)
    if _is_eof(first_line):
        return 0
    if _as_text(first_line).lower().startswith("content-length:"):
        return _run_framed_loop(server, stdin, stdout, first_line)
    return _run_line_loop(server, stdin, stdout, first_line)


def main(argv: list[str] | None = None) -> int:
    argv = list(argv or sys.argv[1:])
    if "--selfcheck" in argv:
        # Реальная проверка: пакет импортируется, Temporal_Store открывается,
        # OpenAI/Ollama доступен (опционально — если Ollama упала, всё равно
        # считаем selfcheck успешным, эмбеддер может быть недоступен).
        try:
            server = SMLServer.from_defaults()
            server.close()
        except Exception as exc:
            print(f"sml-selfcheck-fail: {exc}", file=sys.stderr)
            return 1
        print("sml-selfcheck-ok")
        return 0

    server = SMLServer.from_defaults()
    try:
        return run_stdio_loop(server, stdin=sys.stdin.buffer, stdout=sys.stdout.buffer)
    finally:
        server.close()


if __name__ == "__main__":
    sys.exit(main())
