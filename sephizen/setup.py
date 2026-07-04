"""
First-run setup for Sephizen Cloud: API key onboarding.
"""

from __future__ import annotations

import os
import sys
import time
from getpass import getpass

from . import config
from .ui import console, current_theme, ok, warn, bad
from .banner import render_logo_themed


def setup_api_key() -> str:
    existing = config.get_api_key()
    if existing:
        return existing

    env_key = os.environ.get("HOPX_API_KEY")
    if env_key:
        config.set_api_key(env_key)
        return env_key

    t = current_theme()
    console.clear()
    render_logo_themed(console, t)
    warn(f"No API key found in {config.CONFIG_FILE}")
    console.print("Paste your HopX API key. It will be saved locally.")
    console.print(f"[{t.muted}]Tip: you can also set the HOPX_API_KEY environment variable.[/{t.muted}]\n")
    key = getpass("HopX API key: ").strip()
    if not key:
        bad("API key required")
        sys.exit(1)
    config.set_api_key(key)
    ok("API key saved")
    time.sleep(0.6)
    return key
