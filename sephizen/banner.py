"""
Startup banner rendering for Sephizen Cloud.

The SEPHIZEN logo is never hardcoded in Python. It is loaded from
``ascii-art.txt`` (shipped alongside ``run.py``) every time the banner is
shown, so editing that text file is enough to change the logo. If the
file is missing, or the terminal does not support color, the app falls
back to plain monochrome text rather than crashing.
"""

from __future__ import annotations

import os
import shutil
from pathlib import Path
from typing import List, Optional

from rich.console import Console
from rich.text import Text

from .themes import Theme

# ascii-art.txt lives next to run.py (the project root), not inside the
# sephizen/ package directory.
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
ASCII_ART_PATH = _PROJECT_ROOT / "ascii-art.txt"


def _supports_color(console: Console) -> bool:
    if os.environ.get("NO_COLOR"):
        return False
    return bool(console.is_terminal and console.color_system)


def load_ascii_logo() -> Optional[List[str]]:
    """Read the ASCII logo from ascii-art.txt. Returns None if unavailable."""
    try:
        raw = ASCII_ART_PATH.read_text(encoding="utf-8")
    except Exception:
        return None
    lines = raw.splitlines()
    # Trim fully-blank leading/trailing lines so vertical centering looks right,
    # but keep internal blank lines that are part of the artwork.
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
    return lines if lines else None


def _lerp_color(c1: tuple, c2: tuple, t: float) -> str:
    r = round(c1[0] + (c2[0] - c1[0]) * t)
    g = round(c1[1] + (c2[1] - c1[1]) * t)
    b = round(c1[2] + (c2[2] - c1[2]) * t)
    return f"#{r:02x}{g:02x}{b:02x}"


# Blue -> cyan gradient endpoints (used regardless of active theme so the
# logo always reads as "premium blue/cyan" per spec).
_GRADIENT_START = (0x1E, 0x3A, 0xF2)   # deep blue
_GRADIENT_END = (0x22, 0xE5, 0xE5)     # bright cyan


def render_logo(console: Console, center: bool = True) -> bool:
    """
    Print the SEPHIZEN ASCII logo with a blue -> cyan gradient.

    Returns True if the logo was rendered from ascii-art.txt, False if it
    fell back to a plain-text title (file missing or color unsupported).
    """
    lines = load_ascii_logo()
    term_width = shutil.get_terminal_size(fallback=(100, 24)).columns

    if not lines:
        # Fallback: no ascii-art.txt found.
        fallback = Text("SEPHIZEN CLOUD", style="bold cyan")
        if center:
            console.print(fallback, justify="center")
        else:
            console.print(fallback)
        return False

    use_color = _supports_color(console)
    height = max(len(lines) - 1, 1)

    art_width = max((len(line) for line in lines), default=0)
    pad = max((term_width - art_width) // 2, 0) if center else 0
    left_pad = " " * pad

    for i, line in enumerate(lines):
        if not use_color:
            console.print(left_pad + line)
            continue
        t = i / height
        hex_color = _lerp_color(_GRADIENT_START, _GRADIENT_END, t)
        text = Text(line)
        text.stylize(hex_color)
        console.print(left_pad, text, sep="")

    return True


def render_logo_themed(console: Console, theme: Theme, center: bool = True) -> bool:
    """Same as render_logo, but exposed separately in case callers want to
    tint the fallback title using the active theme's primary color."""
    lines = load_ascii_logo()
    if lines:
        return render_logo(console, center=center)

    fallback = Text("SEPHIZEN CLOUD", style=f"bold {theme.primary}")
    if center:
        console.print(fallback, justify="center")
    else:
        console.print(fallback)
    return False
