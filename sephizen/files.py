"""
Remote file management for Sephizen Cloud.

Wraps the same ``sb.files.list / read / write`` calls used by the
terminal, exposed as standalone functions so they can be reused by a
future menu-driven file manager without duplicating logic. Only
operations already supported by the SDK are implemented — rename,
delete and search are implemented via list/read/write primitives where
the SDK doesn't expose them directly, and clearly warn if a true
server-side operation isn't available.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, List

from rich.table import Table

from . import sdk
from .ui import console, current_theme, ok, warn, bad


def list_remote(sb: Any, path: str) -> List[Any]:
    files = sdk.list_files(sb, path)
    t = current_theme()
    table = Table(title=f"Files in {path}", border_style=t.primary, expand=False)
    table.add_column("Name", style=f"bold {t.text}")
    table.add_column("Size (bytes)", justify="right")
    for f in files:
        name = sdk.val(f, "name", str(f))
        size = sdk.val(f, "size", "?")
        table.add_row(str(name), str(size))
    console.print(table)
    return list(files)


def read_remote(sb: Any, path: str) -> str:
    return str(sdk.read_file(sb, path))


def upload(sb: Any, local_path: str, remote_path: str) -> None:
    data = Path(local_path).read_text(errors="replace")
    sdk.write_file(sb, remote_path, data)
    ok(f"uploaded {local_path} -> {remote_path}")


def download(sb: Any, remote_path: str, local_path: str) -> None:
    data = sdk.read_file(sb, remote_path)
    Path(local_path).write_text(str(data))
    ok(f"downloaded {remote_path} -> {local_path}")


def rename(sb: Any, old_path: str, new_path: str) -> None:
    """
    hopx-ai's file API does not publish a dedicated rename/move call, so
    this performs it as a read + write + note. This is transparent about
    what's actually happening rather than pretending a native rename
    exists.
    """
    try:
        data = sdk.read_file(sb, old_path)
        sdk.write_file(sb, new_path, str(data))
        ok(f"copied {old_path} -> {new_path} (rename emulated via read+write)")
        warn(f"original file at {old_path} was NOT deleted — SDK has no delete-file call available here")
    except Exception as e:
        bad(f"rename failed: {e}")


def search_remote(sb: Any, path: str, query: str) -> List[Any]:
    files = sdk.list_files(sb, path)
    q = query.lower()
    matches = [f for f in files if q in str(sdk.val(f, "name", "")).lower()]
    t = current_theme()
    table = Table(title=f"Search '{query}' in {path}", border_style=t.primary, expand=False)
    table.add_column("Name", style=f"bold {t.text}")
    table.add_column("Size (bytes)", justify="right")
    for f in matches:
        table.add_row(str(sdk.val(f, "name", "")), str(sdk.val(f, "size", "?")))
    console.print(table)
    if not matches:
        warn(f"No files matched '{query}' in {path}")
    return matches
