"""
Dashboard for Sephizen Cloud.

Shows the state of the currently-selected VPS: status, template, region,
preview URL, public host, timeout and working directory. Only fields that
are actually returned by the SDK are displayed — nothing is fabricated.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from rich.table import Table
from rich.panel import Panel
from rich.align import Align

from . import sdk
from .config import get_cwd, get_current, is_favorite, get_label
from .ui import console, current_theme, bad, dim


def _fetch_info(sb: Any) -> Optional[Dict[str, Any]]:
    try:
        return sdk.get_info(sb)
    except Exception:
        return None


def render_dashboard(sb: Optional[Any]) -> None:
    t = current_theme()
    sid = sdk.sid_of(sb) if sb is not None else get_current()

    table = Table(
        title="Sephizen Cloud — Dashboard",
        title_style=f"bold {t.primary}",
        border_style=t.primary,
        show_lines=False,
        expand=False,
    )
    table.add_column("Field", style=f"bold {t.text}")
    table.add_column("Value", style=t.text)

    if not sid:
        console.print(Panel("No active VPS selected.\nUse [bold]create[/bold] or [bold]select[/bold] to choose one.",
                             title="Dashboard", border_style=t.warning, expand=False))
        return

    label = get_label(sid)
    fav = "★ " if is_favorite(sid) else ""
    table.add_row("Active VPS", f"{fav}{label + ' — ' if label else ''}{sid}")

    info: Optional[Dict[str, Any]] = None
    if sb is not None:
        info = _fetch_info(sb)

    if info:
        status = sdk.val(info, "status", "")
        template = sdk.val(info, "template_name", "")
        region = sdk.val(info, "region", "")
        public_host = sdk.val(info, "public_host", sdk.val(info, "direct_url", ""))
        timeout_seconds = sdk.val(info, "timeout_seconds", "")

        if status:
            table.add_row("Status", str(status))
        if template:
            table.add_row("Template", str(template))
        if region:
            table.add_row("Region", str(region))
        if public_host:
            table.add_row("Public Host", str(public_host))
        if timeout_seconds:
            table.add_row("Timeout", f"{timeout_seconds}s")

        preview = sdk.get_preview_url(sb, port=8000) if sb is not None else ""
        if preview:
            table.add_row("Preview URL", preview)
    else:
        dim("(sandbox details unavailable — showing local data only)")

    table.add_row("Current Directory", get_cwd(sid))

    console.print(Align.center(table))
    console.print()
