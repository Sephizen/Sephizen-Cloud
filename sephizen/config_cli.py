"""
`config` command handling: show / set / get / reset.

API keys are always masked when displayed.
"""

from __future__ import annotations

from typing import List

from rich.table import Table

from . import config
from .ui import console, current_theme, ok, warn, bad


def _mask(key: str, value) -> str:
    if key == "api_key" and isinstance(value, str) and value:
        return value[:4] + "…" + value[-4:] if len(value) > 8 else "••••"
    return str(value)


def cmd_show() -> None:
    cfg = config.load_config()
    t = current_theme()
    if not cfg:
        warn("Configuration is empty.")
        return
    table = Table(title=f"Sephizen Cloud Configuration ({config.CONFIG_FILE})", border_style=t.primary, expand=False)
    table.add_column("Key", style=f"bold {t.primary}")
    table.add_column("Value")
    for k, v in cfg.items():
        table.add_row(k, _mask(k, v))
    console.print(table)


def cmd_get(key: str) -> None:
    if not key:
        bad("Usage: config get <key>")
        return
    cfg = config.load_config()
    if key not in cfg:
        warn(f"'{key}' is not set.")
        return
    console.print(_mask(key, cfg[key]))


def cmd_set(key: str, value: str) -> None:
    if not key or value is None:
        bad("Usage: config set <key> <value>")
        return
    config.set_value(key, value)
    ok(f"set {key} = {_mask(key, value)}")


def cmd_reset() -> None:
    from rich.prompt import Confirm
    if Confirm.ask("Reset ALL local configuration? This clears your saved API key too", default=False):
        config.reset_config()
        ok("configuration reset")
    else:
        warn("cancelled")


def handle_config_command(args: List[str]) -> None:
    if not args:
        cmd_show()
        return
    sub = args[0].lower()
    rest = args[1:]
    if sub == "show":
        cmd_show()
    elif sub == "get":
        cmd_get(rest[0] if rest else "")
    elif sub == "set":
        cmd_set(rest[0] if rest else "", " ".join(rest[1:]) if len(rest) > 1 else None)
    elif sub == "reset":
        cmd_reset()
    else:
        bad(f"Unknown config subcommand '{sub}'. Use show, get, set, or reset.")
