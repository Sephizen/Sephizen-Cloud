"""
Local logging for Sephizen Cloud.

Writes rotating-by-day log files under ``~/.sephizen/logs/``:

    commands.log   -> every terminal / SDK command that was executed
    errors.log     -> exceptions and failures
    warnings.log   -> non-fatal warnings shown to the user

Logging never raises: if the log directory can't be written to (read-only
filesystem, permissions, etc.) calls silently no-op so logging can never
crash the app.
"""

from __future__ import annotations

import datetime as _dt
from pathlib import Path

from .config import LOG_DIR

COMMANDS_LOG = LOG_DIR / "commands.log"
ERRORS_LOG = LOG_DIR / "errors.log"
WARNINGS_LOG = LOG_DIR / "warnings.log"


def _timestamp() -> str:
    return _dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _append(path: Path, line: str) -> None:
    try:
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as fh:
            fh.write(line.rstrip("\n") + "\n")
    except Exception:
        pass  # logging must never crash the app


def log_command(sandbox_id: str, command: str, exit_code: int, duration_seconds: float) -> None:
    _append(
        COMMANDS_LOG,
        f"[{_timestamp()}] sandbox={sandbox_id or '-'} exit={exit_code} "
        f"time={duration_seconds:.3f}s cmd={command!r}",
    )


def log_error(context: str, error: Exception) -> None:
    _append(ERRORS_LOG, f"[{_timestamp()}] {context}: {error}")


def log_warning(context: str, message: str) -> None:
    _append(WARNINGS_LOG, f"[{_timestamp()}] {context}: {message}")


def tail(path: Path, n: int = 50) -> list:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
        return lines[-n:]
    except Exception:
        return []
