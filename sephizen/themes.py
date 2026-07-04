"""
Theme definitions for Sephizen Cloud.

Each theme maps a small set of semantic roles (primary, accent, success,
warning, error, muted, text) to Rich color names. The active theme is
persisted in the config file and can be changed with ``config set theme``
or the in-app ``theme`` command.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class Theme:
    name: str
    primary: str      # headline / logo gradient start
    secondary: str     # logo gradient end / accents
    success: str
    warning: str
    error: str
    muted: str
    text: str
    prompt: str


THEMES: Dict[str, Theme] = {
    "dark": Theme(
        name="dark",
        primary="bright_cyan",
        secondary="blue",
        success="green3",
        warning="yellow3",
        error="red3",
        muted="grey62",
        text="white",
        prompt="bright_cyan",
    ),
    "cyber": Theme(
        name="cyber",
        primary="magenta",
        secondary="bright_magenta",
        success="spring_green2",
        warning="gold3",
        error="deep_pink2",
        muted="grey50",
        text="bright_white",
        prompt="bright_magenta",
    ),
    "ocean": Theme(
        name="ocean",
        primary="dodger_blue1",
        secondary="cyan",
        success="turquoise2",
        warning="sandy_brown",
        error="orange_red1",
        muted="steel_blue",
        text="white",
        prompt="dodger_blue1",
    ),
    "matrix": Theme(
        name="matrix",
        primary="green3",
        secondary="bright_green",
        success="green1",
        warning="yellow4",
        error="red1",
        muted="grey37",
        text="green3",
        prompt="bright_green",
    ),
    "light": Theme(
        name="light",
        primary="blue3",
        secondary="dodger_blue2",
        success="dark_green",
        warning="dark_orange3",
        error="red3",
        muted="grey42",
        text="black",
        prompt="blue3",
    ),
}

DEFAULT_THEME_NAME = "dark"


def get_theme(name: str) -> Theme:
    return THEMES.get(name, THEMES[DEFAULT_THEME_NAME])


def theme_names() -> list:
    return list(THEMES.keys())
