"""File_Watcher — следит за ``File_Memory`` и синхронизирует с SML.

Модуль работает поверх ``watchdog`` и имеет две роли:

1. **Индексатор** (``SyncService``) — сам по себе не зависит от ``watchdog``,
   умеет индексировать файлы ``File_Memory`` в ``Memory_Record`` по маппингу
   из ``design.md §7.4``. Вызывается и из File_Watcher, и из
   ``sml.startup_pack`` при первом запуске.
2. **Наблюдатель** (``FileWatcher``) — запускает ``Observer`` watchdog на
   наборе каталогов, дебаунсит события 500 мс и вызывает индексатор.

Требования:
- Req 8.2 — SLA 60 секунд от ``on_modified`` до видимости в ``sml.read``.
- Req 8.3, Req 8.7 — файл-источник истины: если ``Memory_Record`` расходится
  с файлом, индекс приводится к файлу; в Operation_Log пишется
  ``sync_conflict_file_wins``.
- Req 14.1, Req 14.3 — короткие блокировки, до 3 повторов.
- Req 4.1, Req 8.5 — маппинг файла на тип Memory_Record (см. `FILE_TO_TYPE`).
"""

from __future__ import annotations

import hashlib
import re
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable, List, Optional

from .errors import IOErrorSML
from .ids import new_id
from .models import MemoryRecord
from .operation_log import OperationLog
from .temporal_store import TemporalStore, _record_to_history_snapshot
from .timefmt import now_utc_ms
from .validation import MemoryType

__all__ = [
    "FILE_TO_TYPE",
    "SyncService",
    "FileWatcher",
    "Block",
]


# ---------------------------------------------------------------------------
# Маппинг «файл → тип Memory_Record»
# ---------------------------------------------------------------------------


FILE_TO_TYPE: dict[str, tuple[MemoryType, list[str]]] = {
    "docs/memory/layers/facts.md": (MemoryType.FACT, []),
    "docs/memory/layers/preferences.md": (MemoryType.PREFERENCE, []),
    "docs/memory/layers/constraints.md": (MemoryType.CONSTRAINT, []),
    "docs/memory/layers/timeline.md": (MemoryType.TIMELINE_EVENT, []),
    "docs/decisions.md": (MemoryType.DECISION, []),
    "docs/tasks.md": (MemoryType.TASK, []),
    "docs/current-context.md": (MemoryType.FACT, ["current"]),
}


# ---------------------------------------------------------------------------
# Разбиение файла на блоки
# ---------------------------------------------------------------------------


_HEADING_RE = re.compile(r"^(#{2,3})\s+(.+)$", re.MULTILINE)


@dataclass(frozen=True)
class Block:
    """Блок, на который разбивается файл при индексации."""

    content: str
    start_line: int
    end_line: int


def split_into_blocks(text: str, path_rel: str) -> list[Block]:
    """Разбивает файл на логические блоки.

    Правила (упрощённая реализация §7.4):
    - По умолчанию один блок = один раздел `## Заголовок` уровня 2.
    - Если в файле нет заголовков уровня 2 — весь файл считается одним блоком.
    - ``docs/tasks.md`` разбивается по пунктам чек-листа ``- [ ]`` / ``- [x]``.
    """
    if path_rel.endswith("docs/tasks.md"):
        return _split_tasks_md(text)

    lines = text.splitlines()
    heading_indices: list[int] = []
    for idx, line in enumerate(lines, start=1):
        m = _HEADING_RE.match(line)
        if m and len(m.group(1)) == 2:
            heading_indices.append(idx)

    if not heading_indices:
        return [Block(content=text, start_line=1, end_line=max(len(lines), 1))]

    blocks: list[Block] = []
    for i, start in enumerate(heading_indices):
        end = (heading_indices[i + 1] - 1) if i + 1 < len(heading_indices) else len(lines)
        block_text = "\n".join(lines[start - 1 : end]).strip()
        if block_text:
            blocks.append(Block(content=block_text, start_line=start, end_line=end))
    return blocks


def _split_tasks_md(text: str) -> list[Block]:
    lines = text.splitlines()
    blocks: list[Block] = []
    current_start: Optional[int] = None
    current_lines: list[str] = []
    for idx, line in enumerate(lines, start=1):
        if re.match(r"^\s*-\s*\[[ xX]\]", line):
            if current_start is not None and current_lines:
                content = "\n".join(current_lines).strip()
                if content:
                    blocks.append(
                        Block(content=content, start_line=current_start, end_line=idx - 1)
                    )
            current_start = idx
            current_lines = [line]
        else:
            if current_start is not None:
                current_lines.append(line)
    if current_start is not None and current_lines:
        content = "\n".join(current_lines).strip()
        if content:
            blocks.append(
                Block(
                    content=content,
                    start_line=current_start,
                    end_line=len(lines),
                )
            )
    if not blocks:
        return [Block(content=text, start_line=1, end_line=max(len(lines), 1))]
    return blocks


# ---------------------------------------------------------------------------
# SyncService
# ---------------------------------------------------------------------------


def _content_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


class SyncService:
    """Индексирует ``File_Memory`` в ``Memory_Record`` и поддерживает актуальность."""

    def __init__(
        self,
        *,
        store: TemporalStore,
        op_log: OperationLog,
        root: Path,
        agent_name: str = "file-watcher",
    ) -> None:
        self.store = store
        self.op_log = op_log
        self.root = root
        self.agent_name = agent_name

    # --- Индексация одного файла ---

    def sync_file(self, rel_path: str) -> int:
        """Индексирует/переиндексирует один файл. Возвращает число
        затронутых (вставленных/обновлённых) Memory_Record.

        ``rel_path`` — путь относительно ``root``.
        """
        mapping = FILE_TO_TYPE.get(rel_path)
        if mapping is None:
            return 0
        mem_type, default_tags = mapping

        file_path = self.root / rel_path
        if not file_path.exists():
            return 0

        try:
            text = file_path.read_text(encoding="utf-8")
        except OSError as exc:
            raise IOErrorSML(f"Не удалось прочитать {file_path}: {exc}") from exc

        file_hash = _content_hash(text)
        sync_row = self.store._conn.execute(  # type: ignore[attr-defined]
            "SELECT last_hash FROM sync_state WHERE source_file = ?",
            (rel_path,),
        ).fetchone()
        last_hash = sync_row["last_hash"] if sync_row else None
        if last_hash == file_hash:
            return 0  # уже актуально

        blocks = split_into_blocks(text, rel_path)
        touched = 0
        now = now_utc_ms()

        existing_rows = self.store._conn.execute(  # type: ignore[attr-defined]
            """
            SELECT id, content, source_lines FROM records
             WHERE source_file = ? AND deleted_at IS NULL
            """,
            (rel_path,),
        ).fetchall()
        existing_by_range: dict[str, dict] = {
            row["source_lines"] or "": dict(row) for row in existing_rows
        }

        seen_ranges: set[str] = set()
        for block in blocks:
            rng = f"{block.start_line}-{block.end_line}"
            seen_ranges.add(rng)
            prev = existing_by_range.get(rng)
            if prev is None:
                # Новый блок — insert
                rec_id = new_id()
                record = MemoryRecord.model_validate(
                    {
                        "id": rec_id,
                        "type": mem_type.value,
                        "content": block.content,
                        "author_agent": self.agent_name,
                        "created_at": now,
                        "updated_at": now,
                        "is_current": True,
                        "supersedes_id": None,
                        "superseded_by_id": None,
                        "source_file": rel_path,
                        "source_lines": rng,
                        "tags": list(default_tags),
                    }
                )
                self.store.insert(record)
                self.op_log.log(
                    agent=self.agent_name,
                    op="sync_from_file",
                    result="success",
                    record_id=rec_id,
                )
                touched += 1
            else:
                if prev["content"] != block.content:
                    # Файл — источник истины (Req 8.3): обновляем запись.
                    self.store.update_fields(
                        prev["id"], content=block.content, source_lines=rng
                    )
                    self.op_log.log(
                        agent=self.agent_name,
                        op="sync_conflict_file_wins",
                        result="success",
                        record_id=prev["id"],
                        reason_category="file_wins",
                    )
                    touched += 1

        # Удалённые из файла блоки — помечаем как удалённые (soft-delete)
        for rng, row in existing_by_range.items():
            if rng and rng not in seen_ranges:
                try:
                    self.store.delete(row["id"])
                    self.op_log.log(
                        agent=self.agent_name,
                        op="delete",
                        result="success",
                        record_id=row["id"],
                    )
                    touched += 1
                except Exception:
                    pass

        # Обновляем sync_state
        self.store._conn.execute(  # type: ignore[attr-defined]
            """
            INSERT INTO sync_state (source_file, last_hash, last_indexed_at)
                 VALUES (:source_file, :hash, :at)
            ON CONFLICT(source_file) DO UPDATE
               SET last_hash       = excluded.last_hash,
                   last_indexed_at = excluded.last_indexed_at
            """,
            {"source_file": rel_path, "hash": file_hash, "at": now},
        )
        return touched

    def sync_all(self) -> dict[str, int]:
        """Переиндексирует все известные файлы. Возвращает ``{rel_path: touched}``."""
        result: dict[str, int] = {}
        for rel_path in FILE_TO_TYPE:
            try:
                result[rel_path] = self.sync_file(rel_path)
            except Exception as exc:  # pragma: no cover
                self.op_log.log(
                    agent=self.agent_name,
                    op="sync_from_file",
                    result="error",
                    reason_category="io_error",
                    extra={"source_file": rel_path, "error": str(exc)},
                )
                result[rel_path] = -1
        return result


# ---------------------------------------------------------------------------
# FileWatcher (runtime)
# ---------------------------------------------------------------------------


class FileWatcher:
    """Фоновый наблюдатель через watchdog + дебаунс 500 мс."""

    DEBOUNCE_SECONDS = 0.5

    def __init__(
        self,
        sync_service: SyncService,
    ) -> None:
        self._sync = sync_service
        self._pending: dict[str, float] = {}
        self._lock = threading.Lock()
        self._stop = threading.Event()
        self._worker: Optional[threading.Thread] = None
        self._observer = None  # watchdog Observer, type: Optional[Any]

    def _schedule(self, rel_path: str) -> None:
        with self._lock:
            self._pending[rel_path] = time.time() + self.DEBOUNCE_SECONDS

    def _worker_loop(self) -> None:  # pragma: no cover - фоновый поток
        while not self._stop.is_set():
            now = time.time()
            ready: list[str] = []
            with self._lock:
                for rel, deadline in list(self._pending.items()):
                    if deadline <= now:
                        ready.append(rel)
                        del self._pending[rel]
            for rel in ready:
                try:
                    self._sync.sync_file(rel)
                except Exception:
                    pass
            time.sleep(0.1)

    def start(self) -> None:  # pragma: no cover - требует watchdog
        from watchdog.events import FileSystemEventHandler
        from watchdog.observers import Observer

        root = self._sync.root
        handler = self

        class _Handler(FileSystemEventHandler):
            def on_modified(self, event):  # type: ignore[override]
                if event.is_directory:
                    return
                try:
                    rel = str(Path(event.src_path).resolve().relative_to(root)).replace(
                        "\\", "/"
                    )
                except ValueError:
                    return
                if rel in FILE_TO_TYPE:
                    handler._schedule(rel)

            def on_created(self, event):  # type: ignore[override]
                self.on_modified(event)

        self._observer = Observer()
        for rel in FILE_TO_TYPE:
            dir_path = (root / rel).parent
            dir_path.mkdir(parents=True, exist_ok=True)
            self._observer.schedule(_Handler(), str(dir_path), recursive=False)
        self._observer.start()
        self._worker = threading.Thread(target=self._worker_loop, daemon=True)
        self._worker.start()

    def stop(self) -> None:  # pragma: no cover
        self._stop.set()
        if self._observer is not None:
            self._observer.stop()
            self._observer.join(timeout=2)
        if self._worker is not None:
            self._worker.join(timeout=2)
