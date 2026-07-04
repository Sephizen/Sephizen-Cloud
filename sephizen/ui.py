"""
Rich-powered UI helpers for Sephizen Cloud: status messages, panels,
tables, and the system info block shown under the startup banner.
"""

from __future__ import annotations

import os
import platform
import sys
import time
from pathlib import Path
from typing import Any, Dict, Optional

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.align import Align

from . import __version__
from .config import get_current, get_theme as get_theme_name
from .themes import get_theme, Theme

console = Console()


def current_theme() -> Theme:
    return get_theme(get_theme_name())


# --------------------------------------------------------------- messages --
def ok(msg: str) -> None:
    t = current_theme()
    console.print(f"[{t.success}]✓[/{t.success}] {msg}")


def warn(msg: str) -> None:
    t = current_theme()
    console.print(f"[{t.warning}]![/{t.warning}] {msg}")


def bad(msg: str) -> None:
    t = current_theme()
    console.print(f"[{t.error}]✗[/{t.error}] {msg}")


def info(msg: str) -> None:
    t = current_theme()
    console.print(f"[{t.primary}]›[/{t.primary}] {msg}")


def dim(msg: str) -> None:
    t = current_theme()
    console.print(f"[{t.muted}]{msg}[/{t.muted}]")


def clear() -> None:
    os.system("cls" if os.name == "nt" else "clear")


def pause() -> None:
    t = current_theme()
    console.input(f"\n[{t.muted}]press enter...[/{t.muted}]")


def rule(title: str = "") -> None:
    t = current_theme()
    console.rule(title, style=t.primary)


# ------------------------------------------------------------- info block --
def system_info_lines(sandbox_info: Optional[Dict[str, Any]] = None) -> Dict[str, str]:
    """
    Build the label -> value map shown under the startup banner. Only
    values that actually exist are included (never fake data).
    """
    from . import sdk as sdk_mod  # local import to avoid cycles

    data: Dict[str, str] = {}
    data["Version"] = __version__

    sid = get_current()
    if sid:
        data["Current VPS"] = sid

    if sandbox_info:
        status = sdk_mod.val(sandbox_info, "status", "")
        template = sdk_mod.val(sandbox_info, "template_name", "")
        region = sdk_mod.val(sandbox_info, "region", "")
        if status:
            data["Status"] = str(status)
        if template:
            data["Template"] = str(template)
        if region:
            data["Region"] = str(region)

    data["Current Directory"] = os.getcwd()
    data["Python Version"] = platform.python_version()
    data["Platform"] = f"{platform.system()} {platform.release()}"
    data["Current Time"] = time.strftime("%Y-%m-%d %H:%M:%S")
    return data


def render_system_info(sandbox_info: Optional[Dict[str, Any]] = None) -> None:
    t = current_theme()
    data = system_info_lines(sandbox_info)
    table = Table.grid(padding=(0, 2))
    table.add_column(justify="right", style=f"bold {t.primary}")
    table.add_column(justify="left", style=t.text)
    for label, value in data.items():
        table.add_row(f"{label}:", value)
    console.print(Align.center(table))
    console.print()


# ---------------------------------------------------------------- panels --
def panel(content: str, title: str = "", style: Optional[str] = None) -> None:
    t = current_theme()
    console.print(Panel(content, title=title or None, border_style=style or t.primary, expand=False))


def error_panel(title: str, message: str) -> None:
    t = current_theme()
    console.print(Panel(message, title=title, border_style=t.error, expand=False))
