# Math Practice — Project Context

> Single boot doc. Read this first. Open ROADMAP.md / CHANGELOG.md only when the decision table below sends you there.

## Identity

- Product: **Math Practice** — Windows Tk/PyInstaller game for elementary-school math drill with dopamine hooks (achievements, shop, leaderboard, avatars).
- Target buyer: Norwegian parents / homeschool networks, LK20 5. trinn.
- Current version: see `VERSION` (single line).
- Price target: 199 NOK (word-of-mouth sellable at v1.0).
- Credits: bavka (itch.io, free avatar + frame assets), Magnus Landaas (creative input / prompt engineering), Aleksander Lie (developer).

## Repo map

Runtime is Windows, Python 3.14 (Tk 9). Ship via `build.bat` (PyInstaller one-file). `dist/` holds the latest builds. Exe VERSION is set manually in `build.bat`; in-app version is `game.py::__version__`; `VERSION` is the single-line current version; `CHANGELOG.md` is the history.

```
game.py                       entry point + App class (menu, nav, wiring)
build.bat                     PyInstaller one-file build (update VERSION= by hand)
VERSION                       current version, one line only
CHANGELOG.md                  full release history
PROJECT_CONTEXT.md            this file
ROADMAP.md                    forward-looking plan (v0.8+ only)
ROADMAP_POST_1.0.md           LK20 coverage + parking lot
README.md                     user-facing intro

games/
  base_game.py                shared BaseGame (question loop, stats plumbing,
                              scratch pad, sessions_store commit, end-of-session
                              name prompt + achievement popups). Every game mode
                              subclasses this.
  achievements.py             GAME_IDS, GAME_NAMES, UNLOCK_REQUIREMENTS,
                              ACHIEVEMENTS list (49), ACHIEVEMENTS_BY_ID
  achievements_store.py       per-profile persistence of earned/progress
  missed_store.py             per-profile missed-question queue
  scores_store.py             per-profile leaderboard
  sessions_store.py           per-profile session log (added v0.6.0)
  settings_manager.py         global settings.json in %APPDATA%
  profile_manager.py          profile CRUD; load_stores() -> (ach, missed,
                              scores, sessions) 4-tuple
  curriculum.py               LK20 5. trinn goal mapping (parent PDF)
  pdf_export.py               3-page Norwegian parent PDF (zero-dep writer)
  stats_screen.py             full-page Progress & Stats screen
  practice_missed.py          Practice Missed review queue screen

  mult_basic / mult_intermediate / mult_advanced
  div_basic  / div_intermediate  / div_advanced
  frac_base.py (shared parser) + frac_basic / frac_intermediate / frac_advanced
  conv_basic / conv_intermediate / conv_advanced

  tutorials/
    __init__.py               TUTORIAL_REGISTRY
    slideshow_frame.py        reusable SlideshowFrame + shared drawing helpers
                              (palette, draw_fraction, build_slides,
                              award_tutorial_achievements + toast)
    TUTORIAL_CONTRACT.md      mechanical contract + shape catalog for new packs
    tutorials_panel.py        grid-of-cards entry screen
    tutorial_div_basic.py     content pack (shipped v0.7.0)
    tutorial_frac_basic.py    content pack (shipped v0.7.2)
    tutorial_frac_intermediate.py  content pack (shipped v0.7.3)
    tutorial_conv_basic.py    content pack (shipped v0.7.4)
    tutorial_conv_intermediate.py  content pack (shipped v0.7.5)
    tutorial_div_intermediate.py   content pack (shipped v0.7.6)
    tutorial_mult_intermediate.py  content pack (shipped v0.7.7)

assets/                       avatar packs + UI frames (used from v0.8.0)
```

Profile data on disk: `%APPDATA%\MathPractice\profiles\<name>\` containing `achievements.json`, `scores.json`, `missed.json`, `sessions.json`. Global settings at `%APPDATA%\MathPractice\settings.json`.

## Load-bearing conventions

Rules that, if violated, break the product or break pupil trust. Do not re-derive — these are earned, not guessed.

- **Pupil framing.** Refer to the student as "the pupil" — never by name. Product is positioned for many parents, not one child. Applies to all slide copy and in-app text.
- **UI text is English.** All user-facing strings remain in English regardless of target market. (Parent PDF is Norwegian; that is the only exception.)
- **Caveman mode in chat.** Zero filler, zero meta-commentary, direct execution only. No "I'll now…" preambles. Project instructions say so.
- **Raw ints in tutorial modules.** Do NOT import `fractions.Fraction` inside `games/tutorials/tutorial_*.py`. Its auto-reduction on construction silently collapses `75/100` into `3/4` and destroys the whole rewrite step the slides are teaching. Use it only in verification harnesses if convenient.
- **Palette lives in `games/tutorials/slideshow_frame.py`** (`INK MUTED DIM FAINT SOFT ACCENT ACCENT_DARK GOOD WARN BG CARD_BG CARD_BORDER`). Import from there — do not hardcode hex.
- **Tk 9 widget `pady=` / `padx=` must be int** on widget constructors (`tk.Frame`, `tk.Label`, `tk.Button`). Tuples are only valid on `.pack(pady=…)` / `.grid(pady=…)`. This bit us in v0.7.0 — fix the caller, not the widget.
- **Canvas is a fixed 720×340** inside every tutorial slide. Anything reaching `x>720` or `y>340` WILL clip. Use `canvas.bbox` on a hidden probe text to measure strings before drawing pills/strips — see the Slide 4 Tip box in `tutorial_div_basic._slide_4` for the measure-then-draw pattern.
- **Bindfs mount may refuse writes / deletes.** If a write to `build.bat` (or any file clean in git HEAD) returns "Operation not permitted", do not fight the FS — document a manual follow-up in CHANGELOG and move on. For deletes, call `mcp__cowork__allow_cowork_file_delete` once per session; that unlocks the folder.
- **Update ritual.** At task end, update `VERSION` (if version bumps), `CHANGELOG.md` (new entry), and the "Current state" block in this file. Be concise.

## Current state

Last shipped: **v0.7.7.2** (2026-04-25) — pedagogy + layout overhaul of tutorial_mult_intermediate after live review with Aleks:
1. **Inline-expression layout.** Replaced the stacked Norwegian form (top number, × bot row, bar) with a single inline `TOP × BOT` row at the top, partials right-aligned beneath the TOP factor only (the bot factor lives only in the inline expression). Matches Aleks's handwritten reference picture exactly. `_draw_layout` rewrite anchors columns to `col_anchor_x` (TOP's ones-digit x); `bot_lsb_x` is its inline-positioned counterpart for arc-arrow sourcing. New `_inline_anchors(cx, ex)` helper, new `skeleton=True` mode used by slide 1, new `show_inline=False` for slide 2's second-pass arc overlay.
2. **Slide count 7 → 6.** Slide 6 "Verify by estimation" dropped at Aleks's request. Slide 7 (Pitfalls) renumbered to 6. `draw_arrow` import removed (no longer used).
3. **Slide 1 pill shortened** to "one partial row per right-number digit, right-aligned beneath the LEFT factor" so it fits the canvas width.
4. **Slide 2 arc arrows** anchored closer to the digit baselines (src/dst y = oy − 4 instead of oy − 12) so the tails read as lifting off the bot-digit and landing on the top-digit, not floating in space.

py_compile clean. Harnesses verify_div_intermediate.py + verify_mult_intermediate.py remain pending execution before the next exe build. Scope-shift unchanged: mult_intermediate covers 2-dig × 2-dig prominently + a 3-dig × 2-dig stress test (234 × 21), so mult_advanced widens to 3-dig × 2-dig / 3-dig × 3-dig (see ROADMAP).

Next up (see ROADMAP.md for detail): tutorial packs for mult_advanced, div_advanced, frac_advanced, conv_advanced — then v0.7.x follow-up features (in-game `(i)` button hook), then v0.8.0 main-menu redesign (topic tiles + difficulty picker with bronze/blue/purple/fire item-frame tiers) + shop/cosmetics (dark mode + avatar system).

## When to read what

| Task                              | Read first                                                                 |
|-----------------------------------|----------------------------------------------------------------------------|
| Add / edit a tutorial pack        | `games/tutorials/TUTORIAL_CONTRACT.md`, `slideshow_frame.py`, nearest-family sibling tutorial file |
| Add a new game mode               | `games/base_game.py`, the nearest-sibling game file, `achievements.py` for IDs |
| Touch achievements                | `games/achievements.py` (+ `achievements_store.py` if adding a new stat)   |
| Touch the parent PDF              | `games/pdf_export.py` + `curriculum.py`                                    |
| Debug release history             | `CHANGELOG.md`                                                             |
| Plan next milestone               | `ROADMAP.md`                                                               |
| Post-v1.0 curriculum expansion    | `ROADMAP_POST_1.0.md`                                                      |

**Before writing a new tutorial pack:** ask whether the topic genuinely wants 8 slides. If the method has fewer distinct steps (e.g. partial products ≈ 5), write fewer. See `TUTORIAL_CONTRACT.md` "shape catalog" for deviation triggers.
