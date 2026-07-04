# Sephizen Cloud

A professional Cloud / VPS Management CLI built on top of the HopX SDK.

Sephizen Cloud is an upgrade of a previous single-file project (formerly
"HopX SSH Terminal"). It keeps every original feature working while adding
a real dashboard, theming, richer terminal input, structured logging, and
a proper help system — all built with [Rich](https://github.com/Textualize/rich)
and [prompt_toolkit](https://github.com/prompt-toolkit/python-prompt-toolkit).

The terminal is only one feature — the app is meant to feel like a small
cloud platform CLI, not just an SSH shell.

---

## Features

- **Startup screen** — SEPHIZEN ASCII logo (loaded from `ascii-art.txt`,
  never hardcoded) rendered with a blue → cyan gradient, with automatic
  monochrome fallback if your terminal doesn't support color.
- **Dashboard** — active VPS, status, template, region, preview URL,
  public host, timeout, and current directory. Only real values are ever
  shown — nothing is faked.
- **VPS management** — create, connect, list, search, select, favorite,
  label, start, stop, pause, resume, restart (only if the SDK supports
  it), delete.
- **Terminal** — the original shell-passthrough terminal, now with
  command history, Up/Down arrow recall, tab completion, and
  auto-suggestions courtesy of `prompt_toolkit`.
- **File manager** — upload, download, list, read, search (rename is
  emulated via read+write since the SDK has no native rename call).
- **Themes** — dark, cyber, ocean, matrix, light. Your choice is
  remembered.
- **Config system** — `config show / get / set / reset`, all stored in
  `~/.sephizen/config.json`.
- **Logging** — commands, errors, warnings, and execution time are all
  logged locally under `~/.sephizen/logs/`.
- **Help system** — every command documented with description, syntax,
  examples, and related commands.

## What's preserved from the original project

Every original feature still works exactly as before:

- Create / Connect / Start / Stop / Pause / Resume / Delete a VPS
- Interactive terminal (shell passthrough, `py` code execution, `files`,
  `cat`, `upload`, `download`, `preview`, `delete`)
- Preview URL lookup
- API key management (including the `HOPX_API_KEY` environment variable)
- Timeout handling with the same max-timeout fallback ladder
- Working-directory persistence per sandbox
- Local JSON configuration

Old configuration at `~/.hopx_ssh/config.json` is automatically migrated
into `~/.sephizen/config.json` the first time you run the new version, so
you won't lose a saved API key or sandbox selection.

---

## Installation

Requires **Python 3.9+**.

1. Extract this ZIP and enter the project folder:

   ```bash
   cd Sephizen-Cloud
   ```

2. (Recommended) create a virtual environment:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate      # Windows: .venv\Scripts\activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

## Running

```bash
python3 run.py
```

On first run you'll be asked for your HopX API key (or set the
`HOPX_API_KEY` environment variable beforehand to skip the prompt). The
key is saved locally to `~/.sephizen/config.json`.

---

## Project layout

```
Sephizen-Cloud/
├── run.py                  # entry point
├── ascii-art.txt           # SEPHIZEN logo, loaded at startup (edit this to restyle the logo)
├── requirements.txt
├── README.md
├── LICENSE
├── .gitignore
├── config/
│   └── config.example.json # example of the ~/.sephizen/config.json schema
├── logs/                    # placeholder; real logs go to ~/.sephizen/logs/
├── assets/                  # reserved for future static assets
└── sephizen/                # application package
    ├── __init__.py
    ├── banner.py            # loads + renders ascii-art.txt with gradient
    ├── config.py            # ~/.sephizen storage, legacy migration
    ├── config_cli.py        # `config show/get/set/reset`
    ├── dashboard.py         # Rich dashboard for the active VPS
    ├── files.py             # remote file manager helpers
    ├── help.py              # command help system
    ├── logs.py              # command/error/warning logging
    ├── menu.py              # main interactive menu loop
    ├── sdk.py               # thin wrapper around the hopx_ai SDK
    ├── setup.py             # first-run API key onboarding
    ├── terminal.py          # interactive terminal (prompt_toolkit)
    ├── themes.py            # theme definitions
    ├── ui.py                # status messages, panels, system info
    └── vps.py               # VPS lifecycle management
```

---

## Configuration

All configuration lives in `~/.sephizen/config.json`. See
`config/config.example.json` for the schema. You can manage it from
inside the app:

```
config show
config get theme
config set theme ocean
config reset
```

## Themes

```
theme            # lists themes and lets you pick one
theme cyber      # switch directly
```

Available themes: `dark`, `cyber`, `ocean`, `matrix`, `light`.

## Logs

Logs are written to:

```
~/.sephizen/logs/commands.log
~/.sephizen/logs/errors.log
~/.sephizen/logs/warnings.log
```

---

## Important notes

- This is an SSH-*like* terminal, not real OpenSSH — commands run through
  the HopX SDK's command-execution API, not a PTY session.
- Commands that require a true interactive TTY (e.g. `sudo su`) may not
  become an interactive root shell for that reason. Try direct commands
  like `whoami` or `sudo whoami` instead.
- Metrics such as live CPU/RAM/disk/network graphs are **not** included
  because the underlying SDK does not expose them in this project. Faking
  them would be misleading, so they've been deliberately left out.
- `restart` is only available if your installed version of `hopx-ai`
  actually exposes a `restart()` method on the sandbox object; otherwise
  the app tells you clearly instead of pretending it worked.

## License

MIT — see `LICENSE`.
