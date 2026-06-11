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

  screens/                    UI screens carved out of game.py in v0.9.0
                              (two passes) so each module stays well under
                              the 50 KB bindfs truncation threshold. Each
                              module exports show_*(app) entry points that
                              take the App instance and read its profile
                              stores directly (`app._ach_store`, etc.).
                              GAMES / _DIFFICULTY_TIERS / __version__ live
                              in game.py and are lazy-imported (sidesteps
                              the circular-import that an eager top-level
                              `from game import …` would create).
    __init__.py
    settings_dialog.py        show_settings_dialog + _THEME_META + theme picker
    shop_modal.py             show_shop_modal + SHOP_ITEMS registry
                              (game.py imports SHOP_ITEMS from here)
    trophy_room.py            show_trophy_room + tag/insert helpers
    profile_screen.py         show_profile_screen + load_profile +
                              _profile_card; App.show_profiles /
                              App._load_profile delegate here
    main_menu.py              show_menu + show_menu_matrix + _family_tile +
                              _tools_row + _build_tools_tiles + _shop_tile;
                              App.show_menu delegates here
    difficulty_screen.py      show_difficulty + show_difficulty_matrix +
                              _difficulty_tile + _render_lock_hint;
                              App.show_difficulty delegates here

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
tools/                        dev-only verification harnesses
  verify_div_intermediate.py  walks _short_div_steps + EXAMPLES invariants
  verify_mult_intermediate.py walks _mult_steps + EXAMPLES invariants
                              (run from project root: `python tools/verify_*.py`)
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
- **Bindfs truncates large incremental writes.** Files over ~50 KB (currently `game.py`, `stats_screen.py`, `base_game.py`) intermittently get a partial buffer flush — the file ends mid-line / mid-docstring with no error reported. Discipline:
  1. **For files > ~50 KB, prefer atomic full-file `Write` over incremental `Edit`.** Read the file fully into a Python string, do the surgery in memory, then write the whole thing back. Atomic overwrite avoids the merge-into-buffer step that triggers the truncation.
  2. **Verify after every large-file write.** Run `python -m py_compile <path>` and check the file ends with `\n` (not a partial token). Repair on the spot if truncation is detected.
  3. **Avoid edits at the file tail.** The end of long files truncates more often than the middle. When choice exists, edit near the top.
- **Update ritual.** At task end, update `VERSION` (if version bumps), `CHANGELOG.md` (new entry), and the "Current state" block in this file. Be concise.

## Current state

**game.py decomposition shipped (v0.9.0 prep, two passes).** Six UI screens carved out of `game.py` into a new `games/screens/` package. Pass 1 moved the three modals (Settings dialog, Shop modal, Trophy Room) and the `SHOP_ITEMS` registry. Pass 2 moved the page-level screens (profile / main menu / difficulty selection) plus all their internal tile and lock-hint helpers, including the matrix-theme variants. Every public App method that any other code calls (`show_profiles` / `show_menu` / `show_difficulty` / `_show_settings` / `_show_shop` / `_show_achievements` / `_load_profile`) survives as a four-line delegator that lazy-imports the module body — call-sites are intact, no caller code changed. `GAMES` / `_DIFFICULTY_TIERS` / `__version__` stay in `game.py` and the screen modules lazy-import them at render time (eager top-level `from game import …` would deadlock the circular dependency). Final size: `game.py` 2217 → **504 lines, ~20 KB**; new modules 165 / 191 / 204 / 270 / 344 / 736 lines (largest is `main_menu.py` at 31 KB — under the 50 KB bindfs cap with comfortable margin). Pure refactor — no behaviour change, no version bump.

**In-game `(i)` Help button token migration.** The helper modal body (`BaseGame._open_helper_modal`) was already theme-tokened in earlier work; only the helper-trigger button in `_setup_top_bar` had three light-mode hex residues, now migrated to `T["accent"]` / `T["soft"]` / `T["accent_dark"]`. `SlideshowFrame` itself stays light by design — pedagogical canvas drawings need stable contrast — and its on-mount `parent.configure(bg=BG)` still ensures the dark-mode menu doesn't bleed through the modal host's padding gaps.



Last shipped: **v0.8.0** (2026-05-01) — **Shop & Cosmetics milestone open.** Decision to bump straight to a minor version: the breadth of work since v0.7.13 (persistent purchases, full theme architecture, achievement-gated cosmetics, lifetime point bookkeeping, two themed cosmetics shipping) is conceptually a minor bump rather than another patch suffix. Avatar packs + frames remain as v0.8.x work.

What's shippable now:
1. **Shop tile** is functional (replaces v0.7.12's "Coming v0.8.0" placeholder). Click → modal listing every `SHOP_ITEMS` entry with live Buy/Owned state, balance, and achievement-gate hints.
2. **Two cosmetics live:** Dark Mode (500 pts, no gate) and Matrix Mode (1000 pts, gated on `sharp_mult_intermediate` so it lines up with the Multiplication: Advanced curriculum unlock).
3. **Theme picker** in Settings → Appearance. Three palettes selectable when owned: Light (default, free), Dark, Matrix.
4. **Lifetime tracking.** Trophy Room header shows `X lifetime · Y spent` once anything has been spent. `AchievementsStore.spend()` bumps `stats.total_spent`; `get_lifetime_earned() = points + total_spent`.
5. **Theme rollout complete** for the always-on UI: menu, profile screen, settings, achievements popup, BaseGame, stats, practice missed, tutorials grid, all 12 per-game files. `SlideshowFrame` (tutorial slide pages) stays light by design — pedagogical canvas drawings need stable contrast — and on mount it paints `self.parent.configure(bg=BG)` so the active dark/matrix theme doesn't bleed through padding gaps.

Polish items in this build:
- Stats per-game table: alternating row colour was hardcoded `"white"`, fixed to `T["card_bg"]` so dark mode reads correctly.
- Settings dialog: 460×400 → 560×600 + resizable height; all three themes fit without clipping.
- Settings toggle row colours themed (ON/OFF button + label fg) — used to vanish on dark bg.
- Tutorials grid (entry page, before clicking into a slideshow) follows the active theme; the slideshow itself remains light.
- Bindfs note: large game.py rewrites kept truncating mid-write during this build. Recovery pattern is "Python-write the whole tail in one shot" — see the repair scripts in the working transcript. Any future big edit to `game.py` should prefer atomic `Write` over many sequential `Edit` calls.

Adding more cosmetics (next concrete v0.8.x work): drop avatar PNGs in `assets/avatars/<pack>/<id>.png`, append `SHOP_ITEMS` entries with `category="Avatar"` + the asset path, render them as image cards in the shop modal. The asset loader already exists (`games/assets_loader.py`) — current consumer is just the difficulty-tile slot; same machinery serves avatars.

Earlier: **v0.7.13.2** (2026-05-01) — Shop items can now be **achievement-gated** in addition to point-priced. New optional `unlock_req` field on `SHOP_ITEMS` entries names an achievement id; the item refuses purchase until that achievement is earned. **Matrix Mode requires `sharp_mult_intermediate`** — the same achievement that opens Multiplication: Advanced — so Matrix lines up with curriculum progression rather than being pure grind-for-points. Shop modal renders gated items with a yellow "🔒 Earn '<achievement>' first" line inside the card body (using the achievement's existing `desc`), and the Buy button is replaced with a disabled "🔒 Locked". `_buy()` re-checks `unlock_req` at click time as a defensive guard against any stale UI exploit. Dark Mode (no `unlock_req`) is unchanged: 500 pts, no progression gate. Adding new gated items now is a single field on a SHOP_ITEMS entry — keep `unlock_req=None` (or omit) for ungated items.

Earlier: **v0.7.13.1** (2026-05-01) — dark-mode polish + **Matrix theme** (second paid cosmetic, 1000 pts). Three architectural additions on top of v0.7.13:

1. **`btn_primary_bg` / `btn_primary_fg` / `card_dim` tokens** in `theme.py`. Primary action buttons (Trophy Room, Play, Export PDF, etc.) used to read `bg=T["ink"]` which is the *text* color in dark mode — buttons rendered light-grey on light-grey, invisible. The dedicated button-bg tokens give: light = dark slate, dark = indigo accent, matrix = phosphor green. `card_dim` collapses to the page bg in dark/matrix so disabled cards (Practice Missed when empty) recede instead of standing out brighter than active cards (the v0.7.13 bug where soft = #1e293b was *lighter* than card_bg = #0f172a).
2. **Matrix theme** (`_MATRIX` palette + `matrix_mode` shop entry, 1000 pts). Pure black bg, near-black card surfaces, signature `#00ff41` matrix green for `ink` so digits in question displays glow automatically. Warn=amber, danger=red kept distinct so feedback still differentiates.
3. **Theme picker in Settings → Appearance**. Replaces the v0.7.13 single Dark toggle. One row per theme — Light is free, Dark/Matrix gated on `purchases_store.has(<id>_mode)`. Owned rows show "Use" or "✓ Active"; locked rows show "🔒 Buy in Shop" shortcut. Selecting writes `settings('theme')` and rebuilds the menu under the modal.

Lifetime-points bookkeeping: `AchievementsStore.spend()` bumps `stats.total_spent`. New `get_total_spent()` / `get_lifetime_earned()` queries (`= points + total_spent`). Trophy Room header surfaces a `X lifetime · Y spent` line below the balance once anything has been spent.

Files touched in v0.7.13.1: `games/theme.py` (tokens + matrix palette + `theme_name()` / `available_themes()` helpers), `games/achievements_store.py` (`total_spent` default, spend bookkeeping, two new getters), `game.py` (theme picker block in Settings, MATRIX entry in `SHOP_ITEMS`, Trophy Room lifetime/spent block, Python-level `bg = "white"` assignments fixed in `_difficulty_tile` and Practice-Missed disabled state, button-bg swap from `T["ink"]` → `T["btn_primary_bg"]`), `games/base_game.py` (button-bg swap), `games/stats_screen.py` (Export PDF + Trophy header button-bg swap). py_compile clean. Headless smoke import: 3 themes registered (`light`/`dark`/`matrix`), 28 tokens each, 2 shop items, `total_spent` field default-zero on existing profiles.

Earlier: **v0.7.13** (2026-05-01) — **Dark Mode** shipped as the first paid cosmetic (500 pts). The Shop tile is no longer a placeholder — clicking opens a modal that lists every entry in `SHOP_ITEMS` (currently one: `dark_mode`) with live Buy / Owned state, point cost, and balance display. Architecture pieces:

1. **`games/purchases_store.py`** — per-profile JSON ledger at `<profile_dir>/purchases.json` with `has(id)` / `purchase(id)` / `all_owned()`. `purchase()` is idempotent. New profiles start empty.
2. **`AchievementsStore.spend(points)`** — deducts from running total, returns False on insufficient balance. One-way; achievements aren't refunded.
3. **`profile_manager.load_stores`** — returns a **5-tuple now**: `(achievements, missed, scores, sessions, purchases)`. All call-sites that previously bound a 4-tuple were updated.
4. **`SHOP_ITEMS` registry in `game.py`** — list of dicts (id, name, category, icon, desc, price, optional `on_buy` callable). Adding a new item = one entry. `_show_shop` renders one card per item; balance updates in-place after a Buy.
5. **Settings → Appearance** — owns-gated **Dark mode** toggle. When `purchases_store.has("dark_mode")`, writes `settings('theme')` as `"light"`/`"dark"` and rebuilds the menu under the modal so the change paints immediately. When not owned, the row shows a "🔒 Buy in Shop" shortcut that closes Settings and opens the Shop modal.
6. **Theme rollout** — `theme()` reader in `games/theme.py` (already shipped v0.7.12) is now consumed by every menu/game/stats/practice/tutorials-panel render method via a `T = theme()` line at the top. Each file imports `from .theme import theme` and substitutes `bg=T["bg"]`, `fg=T["ink"]` etc. for the previously hardcoded slate-9xx scale. Brand/per-family accents stay literal (per-family glyph backgrounds, success/danger badge palettes, gold star) — they're designed to read on both themes.
7. **Deliberately NOT themed yet** — `games/tutorials/slideshow_frame.py` and the in-game helper modal (`BaseGame._open_helper_modal`). Pedagogical canvas drawings depend on stable ink-on-white contrast; dark-themeing them is a v0.7.13.x follow-up. The user can leave dark mode off if the inconsistency bothers them.

Files touched: new `games/purchases_store.py`; `games/profile_manager.py` (5-tuple + `purchases.json`); `games/achievements_store.py` (`spend()`); `game.py` (SHOP_ITEMS, themed shop modal + tile, themed Settings dark-mode row, full menu/profile/achievements migration); `games/base_game.py`; `games/stats_screen.py`; `games/practice_missed.py`; `games/tutorials/tutorials_panel.py`; all 12 per-game `games/{mult,div,frac,conv}_{basic,intermediate,advanced}.py`. py_compile clean across the board. Headless smoke import: `SHOP_ITEMS` resolves, `theme()` returns 26 tokens, `PurchasesStore` instantiates.

Earlier: **v0.7.12.2** (2026-05-01) — patch over v0.7.12.1: (1) **Mouse-wheel guard.** With the auto-hiding scrollbar, the wheel still fired `yview_scroll` and scrolled the canvas into negative space when content fit. `_install_wheel_handler` now early-returns when `_scroll_target.yview()` reports `(first, last)` ≈ `(0, 1)` — uniform for `Canvas` and `Text`. (2) **minsize 960 → 1080.** Below 1080 px the 4 equal-weight family tiles squish past their labels and the rightmost tile starts clipping. Floor computed from 4 × ~235 px tile + 3 × 14 gap + 2 × 48 section padding ≈ 1078, rounded up. Default geometry 1120x800 retained.

Earlier: **v0.7.12.1** (2026-05-01) — menu polish patch over v0.7.12. Default geometry 1080x720 → 1120x800 and minsize 920x560 → 960x600 so the compressed menu fits at default size without scrolling. The menu's vertical scrollbar is now **auto-hiding** — `show_menu` keeps `vsb` unpacked until a `_sync_scrollbar` helper detects content overflow on inner-frame or canvas `<Configure>`. Difficulty cards no longer stretch on maximised windows: `cards.rowconfigure(0, weight=1)` removed and `card.grid(sticky="nsew")` → `sticky="new"` so each card top-aligns and sizes to its content. Asset slot height bumped 140 → 160. Pure cosmetic patch — no behaviour or persistence changes.

Earlier: **v0.7.12** (2026-05-01) — menu compression + foundation work for v0.8.0. Main menu collapses 12 game cards into **4 family tiles**; clicking a tile opens a new **difficulty-selection screen** with three cards (Beginner / Intermediate / Advanced) and a per-card asset slot. Tools row widened from 3 → 4 to host a **Shop** placeholder (locked, ships in v0.8.0). Game back-callback returns to the difficulty screen for the same family rather than the menu, so trying a sibling difficulty is one click.

Architecture entry points (load-bearing for future expansion):
1. **`game.GAMES`** — one record per family with `id` (e.g. `"mult"`), `label`, `tagline`, `glyph`, `accent`, `difficulties=[…]`. Adding a new family is a single append + three BaseGame subclasses. The previous flat `CATEGORIES` list is gone.
2. **`game._DIFFICULTY_TIERS`** — shared difficulty metadata (basic / intermediate / advanced) keyed by `key`. Order = render order on the difficulty screen.
3. **`games/theme.py`** — single source-of-truth palette. `theme()` reads `settings.get("theme")` and returns a token dict (`bg`, `card_bg`, `ink`, `accent`, `good`, etc.). Both `_LIGHT` and `_DARK` palettes ship; only light is wired into the Settings toggle, because most screens still have hardcoded hex. New screens read from `theme()`; legacy screens migrate token-by-token as we touch them. Once migration completes, flipping the Settings toggle from disabled → enabled is the only remaining step for dark mode.
4. **`games/assets_loader.py`** — `game_tile_image(family_id, difficulty)` looks for `assets/games/<family>/<difficulty>.png` and returns either a `tk.PhotoImage` or `None`. `tier_glyph(difficulty)` returns the emoji fallback (🌱 / 🔥 / ⚡). The difficulty-tile renderer prefers the PNG and falls back to the glyph at 56pt — adding real art later is a zero-code drop-in. **Caller must keep PhotoImage refs alive**; `App._tile_images` is the list that does this for the menu and difficulty screens (Tk would otherwise GC them and the tile renders blank).
5. **Shop tile** lives in the Tools row (`App._shop_tile`). Currently routes to `_show_shop` which fires a messagebox describing planned content (themes, avatars, frames). v0.8.0 replaces that command with a real launcher and flips the locked styling.

Files touched in v0.7.12: `game.py` (registry restructure + family/difficulty/tools/shop renderers + `_launch` signature now `(family, difficulty)` + version bump), new `games/theme.py`, new `games/assets_loader.py`. `BaseGame`, achievements, tutorials, sessions_store untouched. py_compile clean. Smoke import in headless sandbox confirms `GAMES` shape, `_DIFFICULTY_TIERS` shape, `theme()` 26-token dict, and `game_tile_image` graceful-None for missing assets.

Earlier: **v0.7.11** (2026-04-30) — in-game `(i)` helper button. `BaseGame` mounts an "ⓘ Help" button in the top bar for any game whose `GAME_ID` is in `TUTORIAL_REGISTRY`. Click opens `SlideshowFrame` in a 1280×720 Toplevel modal (transient + grab) with the tutorial's fixed examples — no dynamic seeding from the live question.

Reward gating (the carrot/stick that lets the helper exist without becoming the cheat path):
1. `_helper_used=True` flips on first open and is sticky for the rest of the session.
2. `_helper_pause_seconds` accumulates wall-clock seconds inside the modal so `session_minutes` excludes them — The Grind / speed-related stats stay honest.
3. Helper-used sessions skip `achievements_store.record_session()` entirely → zero points to total_correct, zero per-game best updates, no mastery unlocks.
4. `_check_live_achievements` and the end-of-session sweep both early-out when `_helper_used` — anything earned BEFORE the modal opened stays banked, but everything after is reward-free.
5. Leaderboard prompt is suppressed; helper-used sessions never enter the top-10.
6. Session is still appended to `sessions_store` with the new `helper_used` field so the parent PDF / stats screen still see the engagement.
7. Two new `when="helper"` achievements (Learning category) fire from `_check_helper_achievements` on modal close: **Helper Discovered** (10 pts, ≥1 lifetime use) and **Helper Master** (50 pts, ≥10 lifetime uses). Lifetime counter is `stats.helper_used_total`, bumped via `AchievementsStore.record_helper_use()` on every modal open.

The helper path also calls `record_tutorial_viewed` + `award_tutorial_achievements`, so Bookworm / Scholar remain reachable — the pupil really did open a tutorial, just from a different entry point.

Files touched: `games/base_game.py` (button + modal + pause/resume + reward gating), `games/achievements.py` (+ helper_discovered, helper_master on a new `when="helper"` channel), `games/achievements_store.py` (`helper_used_total` default + `record_helper_use`), `games/sessions_store.py` (`helper_used` field on record). py_compile clean. Achievement count: 49 (pre-helper) → it's now 82 because per-game-mastery × 12 games + the four new helper/tutorial entries had already grown the list silently — count comment in this doc was stale; actual ACHIEVEMENTS length is 82 with 2 helper entries verified.

Next up (per ROADMAP): v0.8.0 — main-menu redesign + Shop & Cosmetics (themes, avatars, frames; gives points actual spending weight).

---

Earlier: **v0.7.10.2** (2026-04-25) — final v0.7.x tutorial-pack piece: `conv_advanced` finalised as a no-tutorial mode plus a harder pool, and `tutorial_conv_basic` directional captions split per the contract rule. `_POOL` in `games/conv_advanced.py` grew from 13 → 31 pairs (all `/20` and `/25` entries with integer percentages); `conv_advanced` added to `INTENTIONAL_NO_GUIDE`; `tutorials_panel._not_needed_card` consults a `_NO_GUIDE_REASONS` dict for per-gid copy; `tutorial_conv_basic` slide 3/4/5 captions split with `\n` per the TUTORIAL_CONTRACT directional-branch rule. **v0.7.x tutorial milestone CLOSED.** Tutorial registry: 10 active packs. INTENTIONAL_NO_GUIDE: 2 modes (mult_basic, conv_advanced).

---

Earlier: **v0.7.10.1** (2026-04-25) — patch over `tutorial_conv_basic` after live review with Aleks:
1. **Examples reweighted 3/5 dec→frac** (was 1/5). New mix: 3/4↔0.75 (frac→dec headline), 0.5↔1/2 (dec→frac, ÷5), 3/8↔0.375 (frac→dec, thousandths), 0.4↔2/5 (dec→frac, ÷2), 0.3↔3/10 (dec→frac, gcd=1 → "already lowest" branch).
2. **Slides reordered overview-first.** Old slide 7 (full-chain in one line) is now slide 1; pupils get the shape of the method up front, then the breakdown follows. Old slide 1 (Read the question) dropped — the overview's left side already shows the question. 8 → 7 slides.
3. **Language softened for 5th-grade level.** "Find the bridge" → "Find the missing number". "Raw / clean form" jargon dropped. "Greatest common divisor" paired with "shared factor". Several formal phrasings ("leaves the value unchanged", "the bridge into decimal land", "not a free pass to move digits around the point") rewritten plainer.

`_slide_1` function deleted entirely (was the dropped Read-the-question slide). `_slide_7` and `_slide_8` keep their old function names; only the SLIDES order + numbering change. py_compile clean.

---

Earlier: **v0.7.10** (2026-04-25) — tenth tutorial pack: `tutorial_mult_advanced`. Same Norwegian X-shift method as Intermediate; only new beat is the **XX** double-placeholder when the bottom factor has a hundreds digit. Per Aleks: kept deliberately short — 4 slides × 5 examples.

Method unchanged from Intermediate: the XX is just the natural "k X's per place-shift" rule extended (ones=0, tens=1, hundreds=2, thousands=3). Helper reuse is total: imports `_mult_steps` and `_draw_layout` from `tutorial_mult_intermediate` directly; no new layout code.

Slide structure: (1) refresher + new beat (renders 23 × 15 via Intermediate's `_draw_layout`, beside a "ones→0X / tens→1X / hundreds→XX" key); (2) walk the cycled example; (3) XX beat on fixed reference 23 × 145 = 3335 with row-by-row breakdown highlighting the hundreds-partial; (4) pitfalls (forgot one X → 1265, forgot both → 1058 — both X-related per Aleks's brief).

Examples cover the game's 75 % branch (3-dig × 2-dig: 234×21, 312×23, 145×36) and stretch beyond into 2-dig × 3-dig and 3-dig × 3-dig (23×145, 132×213) so the XX beat shows up in actual cycled examples too. Tutorial count now 10. **All four advanced tutorial packs in scope shipped except `conv_advanced`.**

py_compile clean. Tk-dependent harness deferred (sandbox lacks tkinter).

---

Earlier: **v0.7.9** (2026-04-25) — ninth tutorial pack: `tutorial_frac_advanced`. Adds and subtracts fractions where denominators are **unrelated** (neither divides the other) — e.g. 3/13 + 9/19, 3/8 + 1/12. 7 slides × 5 examples.

**Scope correction note:** the original ROADMAP entry for `frac_advanced` described "Mixed numbers + improper fractions". That was stale — `games/frac_advanced.py` actually teaches LCM-finding for unrelated denoms. ROADMAP table row corrected in this version.

Method (confirmed with Aleks): (1) default = multiply the denominators (always-works); (2) when the bottoms share a factor, spot the smaller LCM (8 and 12 → 24, not 96); (3) always simplify the result via gcd-divide.

Helper reuse: imports `_lcm`, `_rewrite`, `_result_raw`, `_result_reduced`, `_op_word`, `_op_glyph`, `_draw_fraction` from `tutorial_frac_intermediate`. The visual vocabulary (×m callouts, ÷g callouts, two-fraction-side-by-side layout) is pixel-identical across the two packs. Tutorial count now 9.

Slide structure: (1) read the question (with WARN denoms), (2) two-strategy LCM finding — the novel beat (default multiply on cycled, spot-shared-factor on fixed reference 8 & 12), (3) rewrite LEFT (×m), (4) rewrite RIGHT (×n), (5) combine numerators, (6) simplify (real branch when gcd>1; fixed mini-demo 6/8 → 3/4 otherwise), (7) pitfalls (fixed reference 3/13 + 9/19, wrong answers 12/32 and 12/19).

Examples cover: 1/5+1/7 (coprime warmup), 3/8+1/12 (shared factor 4 → LCM 24 vs product 96), 3/14+1/10 (the simplifying case → 22/70 = 11/35), 4/9−1/12 (subtraction, shared factor 3), 3/13+9/19 (the roadmap reference, big numbers).

py_compile clean. Tk-dependent harness deferred (sandbox lacks tkinter).

---

Earlier: **v0.7.8.1** (2026-04-25) — patch over v0.7.8's div_advanced after live screenshot review with Aleks:
1. **Dropped slide 5 (Verify by multiplying back).** Slide count 6 → 5. The Intermediate verify slide was a useful ritual on whole numbers; on decimals the multiplication is non-obvious and gets in the way.
2. **Examples reweighted 4/5 decimals.** Was 3 integer + 2 decimal; now 1 integer warmup + 4 decimal. The novel beat is the comma + zero bring-down — pupil should drill it more than the carry-over from Intermediate.
3. **Slide 1 redundant bottom note removed.** The SlideshowFrame caption below the canvas already paraphrases the same line; doubling crowded the slide.
4. **Slide 3 `comma` callout removed.** The WARN-coloured arrow + label clashed with the title note above the layout; the highlighted decimal step + side-panel walkthrough already make the comma move clear without it.
5. **Cleanup.** Removed the now-unused `show_comma_callout` and `show_bring_down_arrow` parameters from `_draw_layout`; dropped `draw_arrow` from imports.

Original v0.7.8 (2026-04-25): eighth tutorial pack `tutorial_div_advanced`. Norwegian trappa long division extended into terminating decimals.

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
