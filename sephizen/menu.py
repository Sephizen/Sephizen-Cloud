"""
Main menu loop for Sephizen Cloud.
"""

from __future__ import annotations

import time
from typing import Any

from rich.prompt import Prompt

from . import config, sdk, logs
from .ui import console, current_theme, ok, warn, bad, info, clear, pause
from .banner import render_logo_themed
from .dashboard import render_dashboard
from .help import print_menu_help
from .themes import theme_names
from . import vps
from . import terminal as terminal_mod
from . import config_cli

APP_NAME = "Sephizen Cloud"


def show_startup_screen(sandbox_info=None) -> None:
    from .ui import render_system_info
    t = current_theme()
    clear()
    render_logo_themed(console, t)
    console.print()
    render_system_info(sandbox_info)


def print_menu() -> None:
    t = current_theme()
    current = config.get_current()
    console.print(f"[bold]Current VPS:[/bold] {current or '[dim]none selected[/dim]'}")
    console.print()
    console.print("[bold]1)[/bold] create        [bold]2)[/bold] stop         [bold]3)[/bold] start")
    console.print("[bold]4)[/bold] delete        [bold]5)[/bold] terminal     [bold]6)[/bold] exit")
    console.print(f"[{t.muted}]more:[/{t.muted}]")
    console.print("[bold]7)[/bold] list/select   [bold]8)[/bold] dashboard    [bold]9)[/bold] pause")
    console.print("[bold]10)[/bold] resume       [bold]11)[/bold] api key      [bold]12)[/bold] restart")
    console.print("[bold]13)[/bold] search        [bold]14)[/bold] favorite     [bold]15)[/bold] label")
    console.print("[bold]16)[/bold] theme         [bold]17)[/bold] config       [bold]18)[/bold] help")
    console.print()


def run_menu(api_key: str) -> None:
    while True:
        show_startup_screen()
        print_menu()
        choice = Prompt.ask("Choose").strip().lower()
        try:
            if choice in {"1", "create"}:
                vps.create(api_key)
                pause()
            elif choice in {"2", "stop"}:
                vps.action(api_key, "stop")
                pause()
            elif choice in {"3", "start"}:
                vps.action(api_key, "start")
                pause()
            elif choice in {"4", "delete"}:
                vps.action(api_key, "delete")
                pause()
            elif choice in {"5", "terminal"}:
                terminal_mod.terminal(api_key)
                pause()
            elif choice in {"6", "exit", "q", "quit"}:
                ok("bye — your sandboxes keep running")
                return
            elif choice in {"7", "list", "select"}:
                vps.choose_sandbox(api_key)
                pause()
            elif choice in {"8", "dashboard", "info"}:
                try:
                    sb = vps.connect(api_key)
                    render_dashboard(sb)
                except Exception as e:
                    bad(str(e))
                pause()
            elif choice in {"9", "pause"}:
                vps.action(api_key, "pause")
                pause()
            elif choice in {"10", "resume"}:
                vps.action(api_key, "resume")
                pause()
            elif choice in {"11", "apikey", "api key"}:
                config.reset_api_key()
                warn("API key removed. Restart the app to log in again.")
                return
            elif choice in {"12", "restart"}:
                vps.action(api_key, "restart")
                pause()
            elif choice in {"13", "search"}:
                query = Prompt.ask("Search query").strip()
                if query:
                    vps.search_sandboxes(api_key, query)
                pause()
            elif choice in {"14", "favorite"}:
                sid = Prompt.ask("Sandbox ID", default=config.get_current()).strip()
                if sid:
                    vps.toggle_favorite(sid)
                pause()
            elif choice in {"15", "label"}:
                sid = Prompt.ask("Sandbox ID", default=config.get_current()).strip()
                label = Prompt.ask("Label").strip()
                if sid:
                    vps.label_sandbox(sid, label)
                pause()
            elif choice in {"16", "theme"}:
                names = theme_names()
                console.print("Available themes: " + ", ".join(names))
                name = Prompt.ask("Theme", choices=names, default=config.get_theme())
                config.set_theme(name)
                ok(f"theme set to {name}")
                pause()
            elif choice in {"17", "config"}:
                sub = Prompt.ask("config show/get/set/reset", default="show").strip()
                config_cli.handle_config_command(sub.split())
                pause()
            elif choice in {"18", "help"}:
                topic = Prompt.ask("Command (blank for full list)", default="").strip()
                print_menu_help(topic)
                pause()
            else:
                warn("invalid choice")
                time.sleep(0.6)
        except sdk.NotSupportedError as e:
            warn(str(e))
            pause()
        except Exception as e:
            bad(str(e))
            logs.log_error("menu", e)
            pause()
