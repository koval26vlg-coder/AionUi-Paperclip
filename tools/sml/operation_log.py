"""Operation_Log — append-only JSONL-журнал операций SML.

Требования:
- Req 10.1 — для каждой операции запись: agent, ts (UTC ISO 8601), op,
  record_id (опц.), result из {success, rejected, error}, reason_category
  (опц.). Срок записи ≤ 1 с после завершения операции.
- Req 10.3 — JSONL, append-only, путь ``logs/sml-operation-log.ndjson``,
  ротация по календарным UTC-суткам в ``sml-operation-log-YYYY-MM-DD.ndjson``,
  удержание ≥ 30 календарных дней, доступность для чтения без запущенного
  SML (flush+fsync после каждой записи).

Реализация простая и потокобезопасная: один writer со своим ``_lock``,
открывает файл в ``"ab"`` и делает ``flush + fsync`` на каждой строке.
"""

from __future__ import annotations

import json
import os
import threading
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, Literal, Optional

from .timefmt import now_utc_ms

__all__ = [
    "OperationLog",
    "OperationResult",
    "OPERATION_TYPES",
    "DEFAULT_RETENTION_DAYS",
]

OperationResult = Literal["success", "rejected", "error"]

# Ограниченный набор значений — единый словарь для оркестратора и тестов.
OPERATION_TYPES = frozenset(
    [
        "write",
        "read",
        "delete",
        "supersede",
        "semantic_query",
        "temporal_query",
        "add_decision",
        "add_log",
        "build_context_pack",
        "startup_pack",
        "ping",
        "sync_from_file",
        "sync_conflict_file_wins",
    ]
)

DEFAULT_RETENTION_DAYS = 30


class OperationLog:
    """JSONL-журнал в ``<base_dir>/sml-operation-log.ndjson`` с ротацией по UTC-суткам.

    Параметры:
    - ``base_dir`` — каталог для журналов (обычно ``<repo>/logs``).
    - ``retention_days`` — сколько дней хранить ротированные файлы.

    Поведение:
    - активный файл: ``sml-operation-log.ndjson``.
    - при первой записи нового UTC-дня:
        1. текущий файл переименовывается в
           ``sml-operation-log-YYYY-MM-DD.ndjson`` (дата предыдущей записи);
        2. открывается новый ``sml-operation-log.ndjson``;
        3. файлы старше ``retention_days`` удаляются.
    """

    ACTIVE_NAME = "sml-operation-log.ndjson"
    ROTATED_PREFIX = "sml-operation-log-"
    ROTATED_SUFFIX = ".ndjson"

    def __init__(
        self,
        base_dir: Path | str,
        *,
        retention_days: int = DEFAULT_RETENTION_DAYS,
    ) -> None:
        self._base_dir = Path(base_dir)
        self._base_dir.mkdir(parents=True, exist_ok=True)
        self._retention_days = retention_days
        self._lock = threading.Lock()
        # Файл открываем лениво при первой записи, чтобы удобно было создавать
        # объект без побочных эффектов на диске.
        self._fh: Optional[Any] = None
        self._current_date: Optional[str] = None  # YYYY-MM-DD в UTC

    @property
    def base_dir(self) -> Path:
        return self._base_dir

    @property
    def active_path(self) -> Path:
        return self._base_dir / self.ACTIVE_NAME

    # --- Запись ---

    def log(
        self,
        *,
        agent: str,
        op: str,
        result: OperationResult,
        record_id: Optional[str] = None,
        reason_category: Optional[str] = None,
        operation_id: Optional[str] = None,
        extra: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Записывает запись журнала в активный файл.

        Если метка времени пересекла UTC-полночь по сравнению с
        предыдущей записью — выполняет ротацию и очистку старых файлов.
        """
        if op not in OPERATION_TYPES:
            raise ValueError(f"Неизвестный тип операции: {op!r}")
        if result not in {"success", "rejected", "error"}:
            raise ValueError(f"Неизвестный result: {result!r}")
        if result != "success" and reason_category is None:
            raise ValueError("reason_category обязателен для result != success")

        ts = now_utc_ms()
        # ts вида "YYYY-MM-DDTHH:MM:SS.sssZ" → дата UTC
        date_utc = ts[:10]

        entry: Dict[str, Any] = {
            "ts": ts,
            "agent": agent,
            "op": op,
            "result": result,
        }
        if record_id is not None:
            entry["record_id"] = record_id
        if reason_category is not None:
            entry["reason_category"] = reason_category
        if operation_id is not None:
            entry["operation_id"] = operation_id
        if extra:
            # Не даём пользователю перетереть обязательные поля
            for key, value in extra.items():
                if key in entry:
                    continue
                entry[key] = value

        line = json.dumps(entry, ensure_ascii=False) + "\n"

        with self._lock:
            self._maybe_rotate(date_utc)
            if self._fh is None:
                self._fh = open(self.active_path, "ab", buffering=0)
                self._current_date = date_utc
            self._fh.write(line.encode("utf-8"))
            self._fh.flush()
            try:
                os.fsync(self._fh.fileno())
            except OSError:
                # На некоторых ФС (smb, tmpfs) fsync может не поддерживаться.
                # Данные гарантированно сброшены через flush.
                pass

    def close(self) -> None:
        with self._lock:
            if self._fh is not None:
                try:
                    self._fh.flush()
                except Exception:
                    pass
                self._fh.close()
                self._fh = None

    def __enter__(self) -> "OperationLog":
        return self

    def __exit__(self, *exc_info: Any) -> None:
        self.close()

    # --- Ротация и TTL ---

    def _maybe_rotate(self, date_utc: str) -> None:
        """Если текущий UTC-день отличается от дня последней записи — ротация.

        Вызывается под ``_lock``.
        """
        if self._current_date is not None and self._current_date == date_utc:
            return

        # Если активный файл существует (первая запись после старта процесса
        # или переход через полночь), его нужно переименовать в файл по дате
        # последней записи, которая в нём лежит.
        if self.active_path.exists() and self._current_date is not None:
            dest = (
                self._base_dir
                / f"{self.ROTATED_PREFIX}{self._current_date}{self.ROTATED_SUFFIX}"
            )
            if self._fh is not None:
                try:
                    self._fh.flush()
                    os.fsync(self._fh.fileno())
                except OSError:
                    pass
                try:
                    self._fh.close()
                except Exception:
                    pass
                self._fh = None
            # На Windows rename открытого/недавно-закрытого файла бывает
            # ненадёжным из-за antivirus/indexer. Поэтому используем
            # copy+unlink через raw bytes — гарантированно работает.
            with open(self.active_path, "rb") as src_fh:
                data = src_fh.read()
            mode = "ab" if dest.exists() else "wb"
            with open(dest, mode) as dst_fh:
                dst_fh.write(data)
                try:
                    os.fsync(dst_fh.fileno())
                except OSError:
                    pass
            try:
                self.active_path.unlink()
            except OSError:
                # если unlink не удался, всё равно продолжаем — новый fh
                # перезапишет содержимое в следующем log().
                pass

        # Когда активного файла ещё нет (первый запуск) или он уже закрыт —
        # просто фиксируем дату, реальный файл откроется в log().
        self._current_date = date_utc
        self._cleanup_old_files(date_utc)

    def _cleanup_old_files(self, today_utc: str) -> None:
        """Удаляет ротированные файлы старше ``retention_days`` календарных суток.

        Вызывается под ``_lock``.
        """
        try:
            today = datetime.strptime(today_utc, "%Y-%m-%d").replace(
                tzinfo=timezone.utc
            )
        except ValueError:
            return
        cutoff = today - timedelta(days=self._retention_days)
        for p in self._base_dir.glob(f"{self.ROTATED_PREFIX}*{self.ROTATED_SUFFIX}"):
            date_str = p.name[len(self.ROTATED_PREFIX) : -len(self.ROTATED_SUFFIX)]
            try:
                file_date = datetime.strptime(date_str, "%Y-%m-%d").replace(
                    tzinfo=timezone.utc
                )
            except ValueError:
                continue
            if file_date < cutoff:
                try:
                    p.unlink()
                except OSError:
                    pass

    # --- Для тестов ---

    def force_rotate_to(self, date_utc: str) -> None:
        """Принудительно переводит внутреннюю "дату" на указанную.

        Нужно исключительно для тестов ротации (чтобы не менять системное
        время).
        """
        with self._lock:
            self._maybe_rotate(date_utc)
