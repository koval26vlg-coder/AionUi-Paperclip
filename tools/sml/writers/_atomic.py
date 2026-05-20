"""Утилиты атомарной записи файлов с файловой блокировкой (Req 13.5, Req 14.1).

Алгоритм для новых/заменяемых файлов:
1. Записать контент во временный файл ``<target>.<pid>.<ts>.tmp`` рядом с целевым.
2. ``flush + os.fsync`` во временный файл.
3. ``os.replace`` временный → целевой.

При любой ошибке IO целевой файл остаётся в предыдущем состоянии.

Алгоритм для append (только ``decisions.md``): читаем текущий контент,
добавляем новый блок, пишем atomic replace. Это медленнее, чем ``open("ab")``,
но даёт ровно ту же атомарность, что и для полной замены файла.

Блокировка: ``with_file_lock(path, timeout, retries, delay)`` на Windows
реализована через ``msvcrt.locking`` поверх отдельного ``.lock``-файла
рядом с целевым. На любой ОС корректно освобождает handle.
"""

from __future__ import annotations

import contextlib
import os
import sys
import time
from pathlib import Path
from typing import Iterator, Optional

from ..errors import ConflictError, IOErrorSML

__all__ = [
    "atomic_write_bytes",
    "atomic_write_text",
    "atomic_append_text",
    "with_file_lock",
]


def _tmp_path(target: Path) -> Path:
    return target.with_suffix(
        target.suffix + f".{os.getpid()}.{int(time.time()*1000)}.tmp"
    )


def atomic_write_bytes(target: Path, data: bytes) -> None:
    tmp = _tmp_path(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    try:
        with open(tmp, "wb") as fh:
            fh.write(data)
            fh.flush()
            try:
                os.fsync(fh.fileno())
            except OSError:
                pass
        os.replace(tmp, target)
    except OSError as exc:
        # очищаем временный файл, если он остался
        tmp.unlink(missing_ok=True)
        raise IOErrorSML(f"Ошибка записи {target}: {exc}") from exc


def atomic_write_text(target: Path, text: str, encoding: str = "utf-8") -> None:
    atomic_write_bytes(target, text.encode(encoding))


def atomic_append_text(target: Path, block: str, encoding: str = "utf-8") -> tuple[int, int]:
    """Атомарно дописывает ``block`` в конец ``target``.

    Возвращает пару ``(start_line, end_line)`` — диапазон строк нового блока
    (1-индексация). Если между старым контентом и новым блоком нет
    разделителя-новой-строки, добавляется один ``\\n``.
    """
    target.parent.mkdir(parents=True, exist_ok=True)
    existing = ""
    if target.exists():
        existing = target.read_text(encoding=encoding)
    separator = "" if existing == "" or existing.endswith("\n") else "\n"
    combined = existing + separator + block
    # Считаем строки до/после:
    start_line = existing.count("\n") + (1 if separator else 1)
    # Если existing пустой или оканчивается \n, блок начинается со следующей строки
    if existing == "":
        start_line = 1
    elif existing.endswith("\n"):
        start_line = existing.count("\n") + 1
    end_line = combined.count("\n") + (0 if combined.endswith("\n") else 1)
    atomic_write_text(target, combined, encoding=encoding)
    return start_line, end_line


# ---------------------------------------------------------------------------
# Файловая блокировка
# ---------------------------------------------------------------------------


@contextlib.contextmanager
def with_file_lock(
    target: Path,
    *,
    timeout: float = 5.0,
    retries: int = 3,
    delay: float = 0.25,
) -> Iterator[Path]:
    """Берёт эксклюзивную блокировку через ``.lock``-файл рядом с ``target``.

    На Windows использует ``msvcrt.locking``, на остальных ОС — ``fcntl.flock``.
    При исчерпании ``retries`` попыток (с задержкой ``delay`` между ними)
    бросает ``ConflictError`` (Req 14.1, Req 14.3).
    """
    lock_path = target.with_suffix(target.suffix + ".lock")
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    handle: Optional[int] = None
    last_exc: Optional[BaseException] = None
    for attempt in range(retries + 1):
        try:
            handle = os.open(
                str(lock_path),
                os.O_CREAT | os.O_RDWR,
                0o644,
            )
            if sys.platform == "win32":
                import msvcrt

                msvcrt.locking(handle, msvcrt.LK_NBLCK, 1)
            else:  # pragma: no cover
                import fcntl

                fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
            break
        except OSError as exc:
            last_exc = exc
            if handle is not None:
                try:
                    os.close(handle)
                except OSError:
                    pass
                handle = None
            if attempt < retries:
                time.sleep(delay)
            else:
                raise ConflictError(
                    f"Не удалось получить блокировку файла {target}: {exc}"
                ) from exc
    if handle is None:  # pragma: no cover
        raise ConflictError(f"Не удалось получить блокировку файла {target}")
    try:
        # Ограничиваем удержание не более timeout секунд косвенно: коллер
        # контролирует длительность своих операций под with-блоком.
        _ = timeout
        yield lock_path
    finally:
        try:
            if sys.platform == "win32":
                import msvcrt

                msvcrt.locking(handle, msvcrt.LK_UNLCK, 1)
            else:  # pragma: no cover
                import fcntl

                fcntl.flock(handle, fcntl.LOCK_UN)
        except OSError:
            pass
        try:
            os.close(handle)
        except OSError:
            pass
        try:
            lock_path.unlink(missing_ok=True)
        except OSError:
            pass
