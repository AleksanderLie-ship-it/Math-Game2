"""
settings_manager.py
-------------------
Global app settings (not per-profile).
Saved to %APPDATA%\MathPractice\settings.json
"""
# Copyright (c) 2026 Aleksander Lie. All rights reserved.

import json
import os
import pathlib


def _path() -> pathlib.Path:
    appdata = os.getenv("APPDATA")
    base = pathlib.Path(appdata) if appdata else pathlib.Path.home() / ".MathPractice"
    return base / "MathPractice" / "settings.json"


_DEFAULTS = {
    "auto_login":       False,   # skip profile screen, load last profile automatically
    "start_maximized":  False,   # start window maximized
    # Future settings (not yet active):
    # "theme":          "light",
    # "sound":          False,
    # "language":       "en",
}


class SettingsManager:
    def __init__(self):
        self._path = _path()
        self._data = self._load()

    def _load(self) -> dict:
        try:
            if self._path.exists():
                d = json.loads(self._path.read_text(encoding="utf-8"))
                for k, v in _DEFAULTS.items():
                    d.setdefault(k, v)
                return d
        except Exception:
            pass
        return dict(_DEFAULTS)

    def _save(self):
        try:
            self._path.parent.mkdir(parents=True, exist_ok=True)
            self._path.write_text(
                json.dumps(self._data, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
        except Exception:
            pass

    def get(self, key: str):
        return self._data.get(key, _DEFAULTS.get(key))

    def set(self, key: str, value):
        self._data[key] = value
        self._save()


# Module-level singleton — settings are global, not per-profile
settings = SettingsManager()
