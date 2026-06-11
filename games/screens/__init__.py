"""
games.screens
-------------
Modal screens carved out of game.py in v0.9.0 to keep game.py under the
bindfs ~50 KB truncation threshold (see PROJECT_CONTEXT load-bearing
conventions). Each module exports a single `show_*(app)` entry point
that takes the App instance and reads the per-profile stores it needs
(`app._ach_store`, `app._purchases_store`, etc.).
"""
