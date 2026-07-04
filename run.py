#!/usr/bin/env python3
"""
Sephizen Cloud
==============

A professional Cloud / VPS Management CLI built on the HopX SDK.

This file used to be a single-file script (formerly "HopX SSH Terminal").
It has been upgraded into a small, modular application under the
`sephizen/` package, while keeping every original feature working:
create/connect/list/start/stop/pause/resume/delete a sandbox, an
interactive terminal, file upload/download, preview URLs, API key
management, and working-directory persistence.

Install:
  pip install -r requirements.txt

Run:
  python3 run.py

First run:
  - checks ~/.sephizen/config.json (auto-migrated from the old
    ~/.hopx_ssh/config.json if present)
  - if no API key is found, asks for it and saves it
  - HOPX_API_KEY environment variable is also supported

Notes:
  - "max timeout" is not published as one exact number in the HopX
    quickstart docs. This app tries a very large timeout first, then
    falls back through smaller values until HopX accepts one.
  - This is SSH-like, not real OpenSSH. It runs shell commands through
    the HopX SDK's command-execution API.
  - Commands that require a true interactive TTY, like `sudo su`, may not
    become an interactive root shell through the command API — the HopX
    command execution path is not a full PTY/OpenSSH session.
"""

from __future__ import annotations

import sys

from sephizen import sdk
from sephizen.setup import setup_api_key
from sephizen.menu import run_menu
from sephizen.ui import bad


def main() -> None:
    try:
        sdk.require_sdk()
    except RuntimeError as e:
        bad(str(e))
        sys.exit(2)

    api_key = setup_api_key()
    run_menu(api_key)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print()
        sys.exit(0)
