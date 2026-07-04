"""
Configuration management for Sephizen Cloud.

Everything is stored under ``~/.sephizen/``:

    ~/.sephizen/config.json    -> api key, current sandbox, cwd map, theme, favorites, labels
    ~/.sephizen/logs/          -> command / error / warning logs (see sephizen.logs)

If an old ``~/.hopx_ssh/config.json`` exists from a previous install of
this project, its contents are migrated in automatically so nobody loses
their saved API key or sandbox selection.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional

APP_DIR = Path.home() / ".sephizen"
CONFIG_FILE = APP_DIR / "config.json"
LOG_DIR = APP_DIR / "logs"

# Old branding location. Kept only for a one-time, best-effort migration.
_LEGACY_APP_DIR = Path.home() / ".hopx_ssh"
_LEGACY_CONFIG_FILE = _LEGACY_APP_DIR / "config.json"

DEFAULT_TEMPLATE = "code-interpreter"
DEFAULT_CWD = "/workspace"
DEFAULT_THEME = "dark"


def _read_json(path: Path) -> Dict[str, Any]:
    try:
        return json.loads(path.read_text())
    except Exception:
        return {}


def _migrate_legacy_config() -> None:
    """Copy settings from the old ~/.hopx_ssh/config.json, once."""
    if CONFIG_FILE.exists():
        return
    if not _LEGACY_CONFIG_FILE.exists():
        return
    legacy = _read_json(_LEGACY_CONFIG_FILE)
    if not legacy:
        return
    APP_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps(legacy, indent=2))
    try:
        CONFIG_FILE.chmod(0o600)
    except Exception:
        pass


def load_config() -> Dict[str, Any]:
    _migrate_legacy_config()
    return _read_json(CONFIG_FILE)


def save_config(cfg: Dict[str, Any]) -> None:
    APP_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps(cfg, indent=2))
    try:
        CONFIG_FILE.chmod(0o600)
    except Exception:
        pass


def get(key: str, default: Any = None) -> Any:
    return load_config().get(key, default)


def set_value(key: str, value: Any) -> None:
    cfg = load_config()
    cfg[key] = value
    save_config(cfg)


def unset_value(key: str) -> None:
    cfg = load_config()
    cfg.pop(key, None)
    save_config(cfg)


def reset_config() -> None:
    save_config({})


# ---------------------------------------------------------------- sandbox --
def set_current(sandbox_id: str) -> None:
    cfg = load_config()
    cfg["current_sandbox"] = sandbox_id
    cfg.setdefault("cwd", {})[sandbox_id] = cfg.setdefault("cwd", {}).get(sandbox_id, DEFAULT_CWD)
    save_config(cfg)


def get_current() -> str:
    return str(load_config().get("current_sandbox", ""))


def get_cwd(sandbox_id: str) -> str:
    return str(load_config().get("cwd", {}).get(sandbox_id, DEFAULT_CWD))


def set_cwd(sandbox_id: str, cwd: str) -> None:
    cfg = load_config()
    cfg.setdefault("cwd", {})[sandbox_id] = cwd
    save_config(cfg)


def forget_sandbox(sandbox_id: str) -> None:
    cfg = load_config()
    if cfg.get("current_sandbox") == sandbox_id:
        cfg.pop("current_sandbox", None)
    cfg.get("cwd", {}).pop(sandbox_id, None)
    cfg.get("favorites", {}).pop(sandbox_id, None)
    cfg.get("labels", {}).pop(sandbox_id, None)
    save_config(cfg)


# ---------------------------------------------------------------- api key --
def get_api_key() -> Optional[str]:
    cfg = load_config()
    key = cfg.get("api_key")
    return str(key) if key else None


def set_api_key(key: str) -> None:
    set_value("api_key", key)


def reset_api_key() -> None:
    unset_value("api_key")


# ---------------------------------------------------------------- theme ----
def get_theme() -> str:
    return str(load_config().get("theme", DEFAULT_THEME))


def set_theme(name: str) -> None:
    set_value("theme", name)


# ---------------------------------------------------------- favorites/tags --
def get_favorites() -> Dict[str, bool]:
    return dict(load_config().get("favorites", {}))


def set_favorite(sandbox_id: str, favorite: bool) -> None:
    cfg = load_config()
    favs = cfg.setdefault("favorites", {})
    if favorite:
        favs[sandbox_id] = True
    else:
        favs.pop(sandbox_id, None)
    save_config(cfg)


def is_favorite(sandbox_id: str) -> bool:
    return bool(load_config().get("favorites", {}).get(sandbox_id, False))


def get_labels() -> Dict[str, str]:
    return dict(load_config().get("labels", {}))


def get_label(sandbox_id: str) -> str:
    return str(load_config().get("labels", {}).get(sandbox_id, ""))


def set_label(sandbox_id: str, label: str) -> None:
    cfg = load_config()
    labels = cfg.setdefault("labels", {})
    if label:
        labels[sandbox_id] = label
    else:
        labels.pop(sandbox_id, None)
    save_config(cfg)


# ------------------------------------------------------------- fav ports ---
def get_favorite_ports() -> list:
    return list(load_config().get("favorite_ports", []))


def add_favorite_port(port: int) -> None:
    cfg = load_config()
    ports = cfg.setdefault("favorite_ports", [])
    if port not in ports:
        ports.append(port)
    save_config(cfg)


def remove_favorite_port(port: int) -> None:
    cfg = load_config()
    ports = cfg.setdefault("favorite_ports", [])
    if port in ports:
        ports.remove(port)
    save_config(cfg)
