"""
profile_manager.py
------------------
Profile CRUD and directory logic.

Profiles are stored under:
  %APPDATA%\MathPractice\profiles\<profile_name>\
    achievements.json
    scores.json
    missed.json
    sessions.json

A profile registry at:
  %APPDATA%\MathPractice\profiles.json
  -> { "profiles": ["Phillip", "Anna", ...], "last": "Phillip" }
"""
# Copyright (c) 2026 Aleksander Lie. All rights reserved.

import json
import os
import pathlib
import shutil

from .achievements_store import AchievementsStore
from .missed_store       import MissedStore
from .scores_store       import ScoresStore
from .sessions_store     import SessionsStore


# ── Base path ─────────────────────────────────────────────────────────────────

def _base() -> pathlib.Path:
    appdata = os.getenv("APPDATA")
    root = pathlib.Path(appdata) if appdata else pathlib.Path.home() / ".MathPractice"
    return root / "MathPractice"

def _registry_path() -> pathlib.Path:
    return _base() / "profiles.json"

def _profile_dir(name: str) -> pathlib.Path:
    return _base() / "profiles" / _safe_name(name)

def _safe_name(name: str) -> str:
    """Sanitise a profile name for use as a directory name."""
    keep = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-. ")
    cleaned = "".join(c for c in name if c in keep).strip()
    return cleaned or "Profile"


# ── Registry I/O ──────────────────────────────────────────────────────────────

def _load_registry() -> dict:
    try:
        p = _registry_path()
        if p.exists():
            return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        pass
    return {"profiles": [], "last": None}

def _save_registry(reg: dict):
    p = _registry_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(reg, indent=2, ensure_ascii=False), encoding="utf-8")


# ── Public API ────────────────────────────────────────────────────────────────

def list_profiles() -> list[str]:
    """Return list of profile names in creation order."""
    return _load_registry().get("profiles", [])

def last_profile() -> str | None:
    """Return the name of the most recently used profile, or None."""
    return _load_registry().get("last")

def profile_exists(name: str) -> bool:
    return name in list_profiles()

def create_profile(name: str) -> bool:
    """Create a new profile. Returns False if name already exists."""
    name = name.strip()
    if not name or profile_exists(name):
        return False
    reg = _load_registry()
    reg["profiles"].append(name)
    reg["last"] = name
    _save_registry(reg)
    # Initialise the directory (stores create their files on first save)
    _profile_dir(name).mkdir(parents=True, exist_ok=True)
    return True

def delete_profile(name: str) -> bool:
    """Delete a profile and all its data. Returns False if not found."""
    reg = _load_registry()
    if name not in reg["profiles"]:
        return False
    reg["profiles"].remove(name)
    if reg.get("last") == name:
        reg["last"] = reg["profiles"][-1] if reg["profiles"] else None
    _save_registry(reg)
    try:
        shutil.rmtree(_profile_dir(name), ignore_errors=True)
    except Exception:
        pass
    return True

def set_last_profile(name: str):
    """Record which profile was used most recently."""
    reg = _load_registry()
    reg["last"] = name
    _save_registry(reg)


# ── Store factory ─────────────────────────────────────────────────────────────

def load_stores(name: str) -> tuple[AchievementsStore, MissedStore, ScoresStore, SessionsStore]:
    """Instantiate all four stores for the given profile."""
    d = _profile_dir(name)
    d.mkdir(parents=True, exist_ok=True)
    set_last_profile(name)
    return (
        AchievementsStore(d),
        MissedStore(d),
        ScoresStore(d),
        SessionsStore(d),
    )
