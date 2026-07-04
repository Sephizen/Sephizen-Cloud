"""
Professional help system for Sephizen Cloud.

Every command is documented with a description, syntax, examples, and
related commands, rendered as Rich panels.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from rich.panel import Panel
from rich.table import Table

from .ui import console, current_theme


@dataclass(frozen=True)
class CommandHelp:
    name: str
    description: str
    syntax: str
    examples: List[str] = field(default_factory=list)
    related: List[str] = field(default_factory=list)


MENU_COMMANDS: List[CommandHelp] = [
    CommandHelp(
        "create", "Create a new VPS sandbox.", "create",
        ["create  (then follow the template/timeout prompts)"],
        ["connect", "list", "delete"],
    ),
    CommandHelp(
        "connect", "Connect to an existing VPS by ID (or the current one).", "connect [sandbox_id]",
        ["connect", "connect abc123"],
        ["terminal", "select"],
    ),
    CommandHelp(
        "list", "List all VPS sandboxes on your account.", "list",
        ["list"],
        ["search", "select"],
    ),
    CommandHelp(
        "search", "Search sandboxes by id, label, template or status.", "search <query>",
        ["search web", "search running"],
        ["list", "select"],
    ),
    CommandHelp(
        "select", "Choose which VPS is 'current' for other commands.", "select",
        ["select"],
        ["favorite", "label", "terminal"],
    ),
    CommandHelp(
        "favorite", "Toggle favorite status for a sandbox (stored locally).", "favorite <sandbox_id>",
        ["favorite abc123"],
        ["label", "list"],
    ),
    CommandHelp(
        "label", "Attach a local nickname to a sandbox.", "label <sandbox_id> <text>",
        ["label abc123 'staging box'"],
        ["favorite", "list"],
    ),
    CommandHelp(
        "start", "Start the current VPS.", "start", ["start"], ["stop", "pause", "resume"],
    ),
    CommandHelp(
        "stop", "Stop the current VPS.", "stop", ["stop"], ["start", "delete"],
    ),
    CommandHelp(
        "pause", "Pause the current VPS.", "pause", ["pause"], ["resume"],
    ),
    CommandHelp(
        "resume", "Resume a paused VPS.", "resume", ["resume"], ["pause"],
    ),
    CommandHelp(
        "restart", "Restart the current VPS (only if the SDK supports it).", "restart",
        ["restart"], ["start", "stop"],
    ),
    CommandHelp(
        "delete", "Permanently delete the current VPS. Requires typing DELETE to confirm.", "delete",
        ["delete"], ["stop"],
    ),
    CommandHelp(
        "terminal", "Open an interactive terminal session on the current VPS.", "terminal",
        ["terminal"], ["dashboard", "files"],
    ),
    CommandHelp(
        "dashboard", "Show the live dashboard for the current VPS.", "dashboard",
        ["dashboard"], ["info"],
    ),
    CommandHelp(
        "theme", "Switch the color theme (dark, cyber, ocean, matrix, light).", "theme [name]",
        ["theme", "theme cyber"], ["config"],
    ),
    CommandHelp(
        "config", "View or edit local configuration.", "config <show|get|set|reset> [key] [value]",
        ["config show", "config get theme", "config set theme ocean", "config reset"],
        ["theme"],
    ),
    CommandHelp(
        "apikey", "Change or reset the stored HopX API key.", "apikey",
        ["apikey"], ["config"],
    ),
]

TERMINAL_COMMANDS: List[CommandHelp] = [
    CommandHelp("help", "Show terminal command help.", "help / :help"),
    CommandHelp("exit", "Exit the terminal (sandbox keeps running).", "exit / :exit / quit"),
    CommandHelp("clear", "Clear the screen.", "clear"),
    CommandHelp("info", "Show sandbox info / dashboard.", "info"),
    CommandHelp("files", "List remote files.", "files [path]", ["files /workspace"]),
    CommandHelp("cat", "Read a remote file.", "cat <file>", ["cat app.py"]),
    CommandHelp("upload", "Upload a local text file to the sandbox.", "upload <local> <remote>",
                ["upload ./app.py /workspace/app.py"]),
    CommandHelp("download", "Download a remote text file locally.", "download <remote> <local>",
                ["download /workspace/app.py ./app.py"]),
    CommandHelp("py", "Paste Python code and run it (end with EOF).", "py"),
    CommandHelp("preview", "Show the public preview URL for a port.", "preview [port]", ["preview 8000"]),
    CommandHelp("delete", "Delete the sandbox and exit the terminal.", "delete"),
]


def _render_command(cmd: CommandHelp) -> None:
    t = current_theme()
    body = f"[bold]{cmd.description}[/bold]\n\n[dim]Syntax:[/dim] {cmd.syntax}"
    if cmd.examples:
        body += "\n\n[dim]Examples:[/dim]\n" + "\n".join(f"  {e}" for e in cmd.examples)
    if cmd.related:
        body += f"\n\n[dim]Related:[/dim] {', '.join(cmd.related)}"
    console.print(Panel(body, title=cmd.name, border_style=t.primary, expand=False))


def print_menu_help(command: str = "") -> None:
    if command:
        for cmd in MENU_COMMANDS:
            if cmd.name == command.lower():
                _render_command(cmd)
                return
        console.print(f"No help found for '{command}'.")
        return

    t = current_theme()
    table = Table(title="Sephizen Cloud — Commands", border_style=t.primary, expand=False)
    table.add_column("Command", style=f"bold {t.primary}")
    table.add_column("Description")
    for cmd in MENU_COMMANDS:
        table.add_row(cmd.name, cmd.description)
    console.print(table)
    console.print(f"[dim]Tip: type 'help <command>' for full details.[/dim]")


def print_terminal_help() -> None:
    t = current_theme()
    table = Table(title="Terminal Commands", border_style=t.primary, expand=False)
    table.add_column("Command", style=f"bold {t.primary}")
    table.add_column("Description")
    for cmd in TERMINAL_COMMANDS:
        table.add_row(cmd.syntax, cmd.description)
    console.print(table)
    console.print(
        "\n[dim]Anything else runs as a shell command in the sandbox, e.g.[/dim] "
        "pwd, ls -la, cd /workspace, pip install requests, python --version"
    )
    console.print(
        "[dim]Note: 'sudo su' may not become a true interactive root shell — "
        "HopX command execution is not a full PTY/OpenSSH session. Try 'whoami' "
        "or 'sudo whoami' instead.[/dim]"
    )
