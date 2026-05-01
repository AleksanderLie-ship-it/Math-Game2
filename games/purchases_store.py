"""
purchases_store.py
------------------
Per-profile cosmetic-purchase ledger.

Saved to <profile_dir>/purchases.json:

    {
      "owned": ["dark_mode", "avatar_knight", ...]
    }

Why a dedicated store
---------------------
Cosmetic purchases (themes, avatars, frames) are tied to a profile, not
to the global app — siblings sharing the same install should have their
own loadouts and nobody should be able to "earn dark mode for free" by
creating a fresh profile after the first one bought it.

Points are spent through `AchievementsStore.spend(points)` (added v0.7.13);
this store only records *what* is owned, not the points balance.

Item-id contract
----------------
Item ids are stable strings, lowercase with underscores. The shop UI
maps each id to a display name, price, and category. New items are
added by:
  1. Append a SHOP_ITEMS entry in `game.py` (id, name, price, ...).
  2. (Optional) read `purchases_store.has(id)` from any screen that
     needs to gate behaviour on ownership.

`purchase()` is idempotent — calling it on an already-owned id is a
no-op that returns False so callers can detect double-spend attempts.
"""
# Copyright (c) 2026 Aleksander Lie. All rights reserved.

import json
import pathlib


class PurchasesStore:
    def __init__(self, profile_dir: pathlib.Path):
        self._path = pathlib.Path(profile_dir) / "purchases.json"
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._data = self._load()

    # ------------------------------------------------------------------ I/O

    def _load(self) -> dict:
        try:
            if self._path.exists():
                d = json.loads(self._path.read_text(encoding="utf-8"))
                d.setdefault("owned", [])
                return d
        except Exception:
            pass
        return {"owned": []}

    def _save(self):
        try:
            self._path.write_text(
                json.dumps(self._data, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
        except Exception:
            pass

    # ---------------------------------------------------------------- queries

    def has(self, item_id: str) -> bool:
        return item_id in self._data.get("owned", [])

    def all_owned(self) -> list[str]:
        return list(self._data.get("owned", []))

    # --------------------------------------------------------------- writes

    def purchase(self, item_id: str) -> bool:
        """Record an item as owned. Idempotent — returns False if it was
        already owned, True on the first successful record."""
        if self.has(item_id):
            return False
        self._data.setdefault("owned", []).append(item_id)
        self._save()
        return True
