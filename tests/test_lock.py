from pathlib import Path
import pytest
from core.lock import ProjectLocked, SessionLock

def test_lock_acquire_release(tmp_path: Path) -> None:
    lock = SessionLock(tmp_path / ".lock")
    lock.acquire()
    lock.release()

def test_double_lock_in_same_process(tmp_path: Path) -> None:
    first = SessionLock(tmp_path / ".lock")
    second = SessionLock(tmp_path / ".lock")
    first.acquire()
    try:
        with pytest.raises(ProjectLocked):
            second.acquire()
    finally:
        first.release()

def test_lock_after_release(tmp_path: Path) -> None:
    first = SessionLock(tmp_path / ".lock")
    first.acquire()
    first.release()
    second = SessionLock(tmp_path / ".lock")
    second.acquire()
    second.release()

def test_context_manager(tmp_path: Path) -> None:
    with SessionLock(tmp_path / ".lock"):
        pass
    with SessionLock(tmp_path / ".lock"):
        pass
