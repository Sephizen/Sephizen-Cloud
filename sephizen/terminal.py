"""
Interactive terminal for Sephizen Cloud.

This preserves every command from the original HopX SSH Terminal
(help, exit, clear, info, files, cat, upload, download, py, preview,
delete, and raw shell passthrough) while adding:

  - command history persisted to ~/.sephizen/history
  - Up/Down arrow recall (via prompt_toolkit)
  - Tab completion for built-in commands
  - Auto-suggestion from history
  - Nicer prompts, colors and error messages
"""

from __future__ import annotations

import shlex
import sys
import time
from pathlib import Path
from typing import Any, Tuple

from rich.syntax import Syntax

from . import sdk, config, logs
from .ui import console, current_theme, ok, warn, bad, info, clear
from .help import print_terminal_help

try:
    from prompt_toolkit import PromptSession
    from prompt_toolkit.history import FileHistory
    from prompt_toolkit.completion import WordCompleter
    from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
    _HAS_PROMPT_TOOLKIT = True
except Exception:
    _HAS_PROMPT_TOOLKIT = False

HISTORY_FILE = config.APP_DIR / "history"

BUILTIN_COMMANDS = [
    "help", ":help", "exit", ":exit", "quit", "clear", "info",
    "files", "cat", "upload", "download", "py", "preview", "delete",
    "pwd", "ls", "ls -la", "cd", "python --version", "pip install",
]


def _build_session() -> "PromptSession | None":
    if not _HAS_PROMPT_TOOLKIT:
        return None
    try:
        config.APP_DIR.mkdir(parents=True, exist_ok=True)
        completer = WordCompleter(BUILTIN_COMMANDS, ignore_case=True, sentence=True)
        return PromptSession(
            history=FileHistory(str(HISTORY_FILE)),
            completer=completer,
            auto_suggest=AutoSuggestFromHistory(),
            complete_while_typing=True,
        )
    except Exception:
        return None


def paste_until_eof(language: str) -> str:
    console.print(f"Paste {language} code. End with a single line: [bold]EOF[/bold]")
    lines = []
    while True:
        try:
            line = input()
        except (KeyboardInterrupt, EOFError):
            break
        if line.strip() == "EOF":
            break
        lines.append(line)
    return "\n".join(lines)


def run_command(sb: Any, command: str, cwd: str, timeout: int = 300) -> Tuple[str, str, int, str]:
    """
    Run a shell command in the HopX sandbox and preserve the working
    directory across calls (the SDK itself is stateless per-call).
    """
    marker = "__SEPHIZEN_CWD__"
    safe_cwd = shlex.quote(cwd)

    wrapped = (
        f"cd {safe_cwd} 2>/dev/null || cd /workspace 2>/dev/null || cd /\n"
        f"{command}\n"
        f"__sephizen_code=$?\n"
        f"printf '\\n{marker}:%s\\n' \"$PWD\"\n"
        f"exit $__sephizen_code\n"
    )

    res = sdk.run_raw_command(sb, wrapped, timeout=timeout, working_dir="/")
    stdout = str(getattr(res, "stdout", "") or "")
    stderr = str(getattr(res, "stderr", "") or "")
    code_raw = getattr(res, "exit_code", 0)
    code = int(code_raw if code_raw is not None else 0)
    new_cwd = cwd

    if marker + ":" in stdout:
        before, _, after = stdout.rpartition(marker + ":")
        stdout = before.rstrip("\n") + ("\n" if before.rstrip("\n") else "")
        new_cwd = after.splitlines()[0].strip() or cwd

    return stdout, stderr, code, new_cwd


def preview_url(sb: Any, port: int) -> str:
    return sdk.get_preview_url(sb, port)


def _read_input(session, prompt_str: str) -> str:
    if session is not None:
        return session.prompt(prompt_str)
    return input(prompt_str)


def terminal(api_key: str) -> None:
    from .vps import connect  # local import to avoid circular import

    sb = connect(api_key)
    sid = sdk.sid_of(sb)
    cwd = config.get_cwd(sid)
    t = current_theme()
    session = _build_session()

    clear()
    ok(f"connected terminal: {sid}")
    if not _HAS_PROMPT_TOOLKIT:
        warn("prompt_toolkit not available — falling back to basic input (no history/completion)")
    console.print(f"[{t.muted}]type help for terminal commands[/{t.muted}]\n")

    while True:
        prompt_label = f"{sid[:10]}:{cwd}$ "
        try:
            raw = _read_input(session, prompt_label)
        except (KeyboardInterrupt, EOFError):
            console.print()
            warn("terminal closed; sandbox still running")
            return

        cmd = raw.strip()
        if not cmd:
            continue

        try:
            if cmd in {"exit", ":exit", "quit"}:
                warn("terminal closed; sandbox still running")
                return
            if cmd in {"help", ":help"}:
                print_terminal_help()
                continue
            if cmd == "clear":
                clear()
                continue
            if cmd == "info":
                from .dashboard import render_dashboard
                render_dashboard(sb)
                continue
            if cmd.startswith("files"):
                parts = shlex.split(cmd)
                path = parts[1] if len(parts) > 1 else cwd
                files = sdk.list_files(sb, path)
                for f in files:
                    name = sdk.val(f, "name", str(f))
                    size = sdk.val(f, "size", "?")
                    console.print(f"- {name} ({size} bytes)")
                continue
            if cmd.startswith("cat "):
                path = shlex.split(cmd)[1]
                console.print(sdk.read_file(sb, path))
                continue
            if cmd.startswith("upload "):
                _, local, remote = shlex.split(cmd)
                data = Path(local).read_text(errors="replace")
                sdk.write_file(sb, remote, data)
                ok(f"uploaded {local} -> {remote}")
                continue
            if cmd.startswith("download "):
                _, remote, local = shlex.split(cmd)
                data = sdk.read_file(sb, remote)
                Path(local).write_text(str(data))
                ok(f"downloaded {remote} -> {local}")
                continue
            if cmd == "py":
                code = paste_until_eof("Python")
                res = sdk.run_code(sb, code, working_dir=cwd, timeout=300, language="python")
                out = getattr(res, "stdout", "") or ""
                err = getattr(res, "stderr", "") or ""
                if out:
                    console.print(Syntax(out.rstrip(), "text", background_color="default"))
                if err:
                    console.print(f"[{t.error}]{err.rstrip()}[/{t.error}]")
                continue
            if cmd.startswith("preview"):
                parts = shlex.split(cmd)
                port = int(parts[1]) if len(parts) > 1 else 8000
                url = preview_url(sb, port)
                if url:
                    console.print(f"[{t.success}]{url}[/{t.success}]")
                    config.add_favorite_port(port)
                else:
                    warn("no preview URL available")
                continue
            if cmd == "delete":
                confirm = console.input(f"[{t.error}]Delete sandbox permanently? type DELETE: [/{t.error}]").strip()
                if confirm == "DELETE":
                    sdk.kill(sb)
                    ok("deleted")
                    config.forget_sandbox(sid)
                    return
                warn("cancelled")
                continue

            start = time.time()
            stdout, stderr, code, cwd = run_command(sb, raw, cwd)
            config.set_cwd(sid, cwd)
            took = time.time() - start
            logs.log_command(sid, raw, code, took)

            if stdout:
                console.print(stdout.rstrip("\n"))
            if stderr:
                console.print(f"[{t.error}]{stderr.rstrip(chr(10))}[/{t.error}]", highlight=False)
            if code == 0:
                console.print(f"[{t.muted}]exit 0 · {took:.2f}s[/{t.muted}]")
            else:
                console.print(f"[{t.error}]exit {code} · {took:.2f}s[/{t.error}]")
        except Exception as e:
            bad(str(e))
            logs.log_error("terminal", e)
