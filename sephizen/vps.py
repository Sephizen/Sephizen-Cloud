"""
VPS (sandbox) management for Sephizen Cloud.

Covers: create, connect, list, search, select, favorite, label,
start, stop, pause, resume, restart (only if the SDK supports it),
and delete. Favorites and labels are stored locally in the config file;
everything else is a direct pass-through to the HopX SDK.
"""

from __future__ import annotations

import time
from typing import Any, List, Optional

from rich.table import Table
from rich.prompt import Prompt, Confirm

from . import sdk, config, logs
from .ui import console, current_theme, ok, warn, bad, info, dim
from .dashboard import render_dashboard


def connect(api_key: str, sandbox_id: Optional[str] = None) -> Any:
    sdk.require_sdk()
    sid = sandbox_id or config.get_current()
    if not sid:
        sid = Prompt.ask("Sandbox ID").strip()
    if not sid:
        raise RuntimeError("No sandbox selected")
    sb = sdk.connect_sandbox(api_key, sid)
    config.set_current(sdk.sid_of(sb))
    return sb


def parse_timeout_choice(raw: str) -> List[int]:
    raw = raw.strip().lower()
    if raw in {"", "max", "m", "maximum"}:
        return sdk.MAX_TIMEOUT_TRIES[:]
    try:
        seconds = int(raw)
        return [seconds]
    except Exception:
        warn("Invalid timeout, using max fallback list")
        return sdk.MAX_TIMEOUT_TRIES[:]


def create(api_key: str) -> Any:
    sdk.require_sdk()
    template = Prompt.ask("Template", default=sdk.DEFAULT_TEMPLATE).strip() or sdk.DEFAULT_TEMPLATE
    timeout_raw = Prompt.ask("Timeout seconds", default="max").strip()
    timeout_tries = parse_timeout_choice(timeout_raw)

    last_error: Optional[Exception] = None
    for timeout in timeout_tries:
        try:
            info(f"creating sandbox template={template}, timeout={timeout}s ...")
            sb = sdk.create_sandbox(api_key, template=template, timeout_seconds=timeout)
            config.set_current(sdk.sid_of(sb))
            ok(f"created {sdk.sid_of(sb)}")
            ok(f"accepted timeout: {timeout}s")
            show_info(sb)
            return sb
        except Exception as e:
            last_error = e
            warn(f"timeout {timeout}s rejected/failed: {e}")
            logs.log_warning("create", f"timeout {timeout}s rejected: {e}")
            time.sleep(0.2)

    err = RuntimeError(f"Could not create sandbox with any timeout. Last error: {last_error}")
    logs.log_error("create", err)
    raise err


def list_sandboxes(api_key: str) -> List[Any]:
    sdk.require_sdk()
    info("fetching sandboxes...")
    boxes = sdk.list_sandboxes(api_key, limit=100)
    if not boxes:
        warn("No sandboxes found")
        return []

    t = current_theme()
    table = Table(border_style=t.primary, expand=False)
    table.add_column("#", justify="right")
    table.add_column("★", justify="center")
    table.add_column("Sandbox ID", style=f"bold {t.text}")
    table.add_column("Label")
    table.add_column("Status")
    table.add_column("Template")

    current = config.get_current()
    for i, sb in enumerate(boxes, 1):
        try:
            inf = sdk.get_info(sb)
        except Exception:
            inf = {}
        sid = sdk.sid_of(sb)
        status = str(sdk.val(inf, "status", "?"))
        template = str(sdk.val(inf, "template_name", ""))
        star = "★" if config.is_favorite(sid) else ""
        label = config.get_label(sid)
        marker_style = f"bold {t.success}" if sid == current else t.text
        table.add_row(str(i), star, f"[{marker_style}]{sid}[/{marker_style}]", label, status, template)

    console.print(table)
    console.print()
    return boxes


def search_sandboxes(api_key: str, query: str) -> List[Any]:
    """Filter sandboxes locally by ID, label, template or status substring."""
    boxes = sdk.list_sandboxes(api_key, limit=100)
    if not boxes:
        warn("No sandboxes found")
        return []
    q = query.strip().lower()
    matches = []
    for sb in boxes:
        sid = sdk.sid_of(sb)
        label = config.get_label(sid).lower()
        try:
            inf = sdk.get_info(sb)
            template = str(sdk.val(inf, "template_name", "")).lower()
            status = str(sdk.val(inf, "status", "")).lower()
        except Exception:
            template = status = ""
        if q in sid.lower() or q in label or q in template or q in status:
            matches.append(sb)

    if not matches:
        warn(f"No sandboxes matched '{query}'")
        return []

    t = current_theme()
    table = Table(title=f"Search results for '{query}'", border_style=t.primary, expand=False)
    table.add_column("Sandbox ID", style=f"bold {t.text}")
    table.add_column("Label")
    for sb in matches:
        sid = sdk.sid_of(sb)
        table.add_row(sid, config.get_label(sid))
    console.print(table)
    return matches


def choose_sandbox(api_key: str) -> Optional[str]:
    boxes = list_sandboxes(api_key)
    if not boxes:
        return None
    choice = Prompt.ask("Choose # or paste sandbox id").strip()
    if not choice:
        return None
    if choice.isdigit():
        idx = int(choice) - 1
        if 0 <= idx < len(boxes):
            sid = sdk.sid_of(boxes[idx])
            config.set_current(sid)
            ok(f"selected {sid}")
            return sid
    config.set_current(choice)
    ok(f"selected {choice}")
    return choice


def toggle_favorite(sandbox_id: str) -> None:
    new_state = not config.is_favorite(sandbox_id)
    config.set_favorite(sandbox_id, new_state)
    if new_state:
        ok(f"marked {sandbox_id} as favorite")
    else:
        info(f"removed {sandbox_id} from favorites")


def label_sandbox(sandbox_id: str, label: str) -> None:
    config.set_label(sandbox_id, label)
    ok(f"labeled {sandbox_id} as '{label}'" if label else f"cleared label for {sandbox_id}")


def show_info(sb: Any) -> None:
    try:
        inf = sdk.get_info(sb)
    except Exception as e:
        bad(f"could not get info: {e}")
        logs.log_error("show_info", e)
        return
    render_dashboard(sb)


def action(api_key: str, name: str) -> None:
    sb = connect(api_key)
    sid = sdk.sid_of(sb)
    start_time = time.time()
    try:
        if name == "start":
            info(f"starting {sid}...")
            sdk.start(sb)
            ok("started")
        elif name == "stop":
            info(f"stopping {sid}...")
            sdk.stop(sb)
            ok("stopped")
        elif name == "pause":
            sdk.pause(sb)
            ok("paused")
        elif name == "resume":
            sdk.resume(sb)
            ok("resumed")
        elif name == "restart":
            sdk.restart(sb)
            ok("restarted")
        elif name == "delete":
            confirm = Prompt.ask(f"[bold red]Delete {sid} permanently? type DELETE[/bold red]").strip()
            if confirm != "DELETE":
                warn("cancelled")
                return
            sdk.kill(sb)
            ok("deleted")
            config.forget_sandbox(sid)
        logs.log_command(sid, f"vps:{name}", 0, time.time() - start_time)
    except sdk.NotSupportedError as e:
        warn(str(e))
        logs.log_warning(f"vps:{name}", str(e))
    except Exception as e:
        bad(str(e))
        logs.log_error(f"vps:{name}", e)
        raise
