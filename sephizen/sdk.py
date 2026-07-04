"""
HopX SDK access layer for Sephizen Cloud.

This module is a thin, typed wrapper around the ``hopx_ai`` package. Every
call site here matches the original project's usage of the SDK exactly
(``Sandbox.create``, ``Sandbox.connect``, ``Sandbox.list``, ``sb.start()``,
``sb.stop()``, ``sb.pause()``, ``sb.resume()``, ``sb.kill()``,
``sb.get_info()``, ``sb.commands.run(...)``, ``sb.run_code(...)``,
``sb.files.list/read/write``, ``sb.get_preview_url(...)``).

Nothing here invents SDK capabilities. If the installed SDK version does
not support a given attribute (e.g. ``restart``), the corresponding
function raises ``NotSupportedError`` instead of silently pretending it
worked.
"""

from __future__ import annotations

import sys
from typing import Any, Dict, List, Optional, Tuple

try:
    from hopx_ai import Sandbox
except Exception:
    Sandbox = None  # type: ignore

try:
    from hopx_ai.exceptions import APIError, ResourceLimitError
except Exception:
    APIError = ResourceLimitError = Exception  # type: ignore


class NotSupportedError(Exception):
    """Raised when the installed SDK does not expose a requested feature."""


# Max-timeout fallback ladder. HopX's quickstart docs do not publish one
# exact maximum, so "max" tries these from largest to smallest until the
# API accepts one.
MAX_TIMEOUT_TRIES: List[int] = [
    2_147_483_647,  # int32 max seconds, ~68 years; likely rejected, tried first
    315_360_000,    # 10 years
    31_536_000,     # 1 year
    2_592_000,      # 30 days
    604_800,        # 7 days
    172_800,        # 48 hours
    86_400,         # 24 hours
    43_200,         # 12 hours
    21_600,         # 6 hours
    7_200,          # 2 hours
    3_600,          # 1 hour
]

DEFAULT_TEMPLATE = "code-interpreter"
DEFAULT_CWD = "/workspace"


def sdk_available() -> bool:
    return Sandbox is not None


def require_sdk() -> None:
    if Sandbox is not None:
        return
    raise RuntimeError(
        "hopx-ai SDK is not installed.\nInstall it with:\n  pip install hopx-ai"
    )


def sid_of(sb: Any) -> str:
    return str(getattr(sb, "sandbox_id", None) or getattr(sb, "id", None) or "unknown")


def val(obj: Any, key: str, default: Any = "") -> Any:
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)


def create_sandbox(api_key: str, template: str, timeout_seconds: int) -> Any:
    require_sdk()
    return Sandbox.create(template=template, timeout_seconds=timeout_seconds, api_key=api_key)


def connect_sandbox(api_key: str, sandbox_id: str) -> Any:
    require_sdk()
    return Sandbox.connect(sandbox_id, api_key=api_key)


def list_sandboxes(api_key: str, limit: int = 100) -> List[Any]:
    require_sdk()
    return list(Sandbox.list(api_key=api_key, limit=limit))


def get_info(sb: Any) -> Dict[str, Any]:
    return sb.get_info()


def start(sb: Any) -> None:
    sb.start()


def stop(sb: Any) -> None:
    sb.stop()


def pause(sb: Any) -> None:
    sb.pause()


def resume(sb: Any) -> None:
    sb.resume()


def restart(sb: Any) -> None:
    """Only calls sb.restart() if the SDK actually exposes it."""
    if not hasattr(sb, "restart"):
        raise NotSupportedError("This version of the HopX SDK does not support restart().")
    sb.restart()


def kill(sb: Any) -> None:
    sb.kill()


def list_files(sb: Any, path: str) -> Any:
    return sb.files.list(path)


def read_file(sb: Any, path: str) -> Any:
    return sb.files.read(path)


def write_file(sb: Any, path: str, data: str) -> None:
    sb.files.write(path, data)


def run_code(sb: Any, code: str, working_dir: str, timeout: int = 300, language: str = "python") -> Any:
    return sb.run_code(code, language=language, working_dir=working_dir, timeout=timeout)


def run_raw_command(sb: Any, command: str, timeout: int, working_dir: str = "/") -> Any:
    return sb.commands.run(command, timeout=timeout, working_dir=working_dir)


def get_preview_url(sb: Any, port: int) -> str:
    if hasattr(sb, "get_preview_url"):
        try:
            return str(sb.get_preview_url(port=port))
        except Exception:
            pass
    try:
        inf = sb.get_info()
        host = str(val(inf, "public_host", val(inf, "direct_url", ""))).rstrip("/")
        if not host:
            return ""
        if "://" in host:
            scheme, rest = host.split("://", 1)
        else:
            scheme, rest = "https", host
        return f"{scheme}://{port}-{rest}"
    except Exception:
        return ""
