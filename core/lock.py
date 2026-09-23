"""Single-writer project session lock."""
from __future__ import annotations
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from .errors import MyProError

class ProjectLocked(MyProError):
    def __init__(self, path: Path, holder_pid: int | None = None) -> None:
        message = f"project is locked: {path}"
        if holder_pid is not None:
            message += f" (held by pid {holder_pid})"
        super().__init__(message)
        self.path = path
        self.holder_pid = holder_pid

@dataclass
class SessionLock:
    path: Path
    _fd: int | None = None

    def acquire(self) -> None:
        if self._fd is not None:
            return
        self.path.parent.mkdir(parents=True, exist_ok=True)
        fd = os.open(self.path, os.O_CREAT | os.O_RDWR, 0o644)
        try:
            self._lock_fd(fd)
        except OSError as exc:
            os.close(fd)
            raise ProjectLocked(self.path, self._read_holder_pid()) from exc
        self._fd = fd
        self._write_holder()

    def release(self) -> None:
        if self._fd is None:
            return
        fd = self._fd
        self._fd = None
        try:
            self._unlock_fd(fd)
        finally:
            os.close(fd)

    def __enter__(self) -> "SessionLock":
        self.acquire()
        return self

    def __exit__(self, *_exc: object) -> None:
        self.release()

    @staticmethod
    def _lock_fd(fd: int) -> None:
        if sys.platform == "win32":
            import msvcrt
            os.lseek(fd, 0, os.SEEK_SET)
            msvcrt.locking(fd, msvcrt.LK_NBLCK, 1)
        else:
            import fcntl
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)

    @staticmethod
    def _unlock_fd(fd: int) -> None:
        if sys.platform == "win32":
            import msvcrt
            try:
                os.lseek(fd, 0, os.SEEK_SET)
                msvcrt.locking(fd, msvcrt.LK_UNLCK, 1)
            except OSError:
                pass
        else:
            import fcntl
            try:
                fcntl.flock(fd, fcntl.LOCK_UN)
            except OSError:
                pass

    def _write_holder(self) -> None:
        if self._fd is None:
            return
        os.lseek(self._fd, 0, os.SEEK_SET)
        os.ftruncate(self._fd, 0)
        os.write(self._fd, str(os.getpid()).encode("ascii"))
        os.fsync(self._fd)

    def _read_holder_pid(self) -> int | None:
        try:
            text = self.path.read_text(encoding="ascii").strip()
            return int(text) if text else None
        except (OSError, ValueError):
            return None
