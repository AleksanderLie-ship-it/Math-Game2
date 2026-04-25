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

Last shipped: **v0.7.8** (2026-04-25) — eighth tutorial pack: `tutorial_div_advanced`. Norwegian trappa long division extended into terminating decimals. 6 slides × 5 examples (3 exact integer cases matching the game's 75% branch + 2 terminating-decimal cases matching the 25% branch).

Key design decisions Aleks confirmed before writing:
- **Method:** Norwegian trappa / staircase (not English bring-down).
- **Decimal handling:** Append a comma to the quotient and "bring down" an imaginary 0 from the dividend's right edge; new partial = leftover × 10. Repeat until remainder = 0.

Layout reuse: imports `COL_W`, `LINE_H`, `LAYOUT_FONT`, `BAR_COLOR`, `_short_div_steps`, AND `_draw_layout` from `tutorial_div_intermediate`. The new `_long_div(dividend, divisor)` delegates the integer phase to `_short_div_steps`, only adds the decimal-phase loop. Slide 2's refresher renders 36 ÷ 3 = 12 via Intermediate's own `_draw_layout` so the pupil sees the exact same picture from the previous tutorial. Tutorial count now 8.

Slide structure: (1) read the question, (2) refresher with mini Intermediate render, (3) decimal extension on fixed reference 13 ÷ 2 = 6,5, (4) walk the full chain on the cycled example, (5) verify by multiplying back, (6) pitfalls (fixed ref 17 ÷ 4 = 4,25; wrong answers "425" and "4,2").

py_compile clean. Tk-dependent harness deferred (sandbox lacks tkinter; py_compile is the most we can verify here).

Next up (see ROADMAP.md): tutorial packs for mult_advanced, frac_advanced, conv_advanced — then v0.7.x follow-up features (in-game `(i)` button hook), then v0.8.0 main-menu redesign (topic tiles + difficulty picker with bronze/blue/purple/fire item-frame tiers) + shop/cosmetics (dark mode + avatar system).

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
