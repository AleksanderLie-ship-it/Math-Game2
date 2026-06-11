# Math Practice — Roadmap

Copyright (c) 2026 Aleksander Lie. All rights reserved.

Current version: see `VERSION`. Forward-looking only — shipped work lives in `CHANGELOG.md`. Repo map, conventions, and boot context live in `PROJECT_CONTEXT.md`. Post-1.0 curriculum expansion lives in `ROADMAP_POST_1.0.md`.

Target: word-of-mouth sellable at 199 NOK to Norwegian parents / homeschool networks.

---

## Shipped milestones (summary)

- **v0.4.0** User profiles + main menu ✅
- **v0.5.0** Fraction game (basic / intermediate / advanced) ✅
- **v0.6.0** Progress & Stats screen + parent PDF ✅
- **v0.7.0** Tutorial slideshow framework + div_basic pack ✅
- **v0.7.1–0.7.5** Five tutorial packs shipped: div_basic, frac_basic, frac_intermediate, conv_basic, conv_intermediate ✅
- **v0.7.6** Sixth tutorial pack shipped: div_intermediate (short division, Norwegian vertical layout, 7 slides × 5 examples) ✅
- **v0.7.7** Seventh tutorial pack shipped: mult_intermediate (partial products with the X-shift placeholder, originally 7 slides × 5 examples) ✅
- **v0.7.7.1** Patch: render fixes in tutorial_mult_intermediate (slide 2/4 arc-arrow stub bug, slide 3 pill overlap, slide 4 premature sum row). `_draw_layout` gained an explicit `show_sum` parameter. ✅
- **v0.7.7.2** Layout overhaul of tutorial_mult_intermediate: inline `TOP × BOT` row replaces the stacked top/× bot/bar form. Slide 6 "Verify by estimation" dropped (7 → 6 slides). ✅
- **v0.7.8** Eighth tutorial pack shipped: div_advanced (Norwegian trappa long division extended into terminating decimals via comma + zero bring-down, originally 6 slides × 5 examples). Reuses Intermediate's `_short_div_steps` and `_draw_layout` directly. ✅
- **v0.7.8.1** Patch: dropped slide 5 verify (6 → 5 slides). Examples reweighted 4/5 decimals (was 2/5). Slide 1 redundant bottom note removed (caption already covers it). Slide 3 comma callout removed (clashed with title note). ✅
- **v0.7.9** Ninth tutorial pack shipped: frac_advanced (unrelated denominators, two-strategy LCM finding, 7 slides × 5 examples). Reuses Intermediate's `_lcm`, `_rewrite`, `_result_raw`, `_result_reduced`, `_op_word`, `_op_glyph`, `_draw_fraction` directly. ✅
- **v0.7.10** Tenth tutorial pack shipped: mult_advanced (longer factors with the XX double-placeholder, 4 slides × 5 examples). Heavily reuses Intermediate's `_mult_steps` and `_draw_layout` — method unchanged, just XXX×XX / XX×XXX stretches. Pitfalls focus on forgetting one or both X's. ✅
- **v0.7.10.1** Patch: tutorial_conv_basic cleanup. Examples reweighted 3/5 dec→frac (was 1/5). Slides reordered — old slide 7 (full-chain overview) now slide 1; old slide 1 (read the question) dropped (overview already shows the question). Language softened to 5th-grade level: "find the bridge" → "find the missing number"; "raw / clean form" jargon dropped; "greatest common divisor" paired with "shared factor". 8 → 7 slides. ✅
- **v0.7.10.2** conv_advanced finalized as the last v0.7.x piece: (1) `_POOL` extended with /20 and /25 entries (8 + 10 = 18 new pairs, all terminating with integer percentages — pool grows from 13 → 31). (2) `conv_advanced` added to `INTENTIONAL_NO_GUIDE` — no tutorial, by design (method is the union of conv_basic + conv_intermediate). (3) `tutorials_panel._not_needed_card` now selects per-gid copy: conv_advanced reads "All three forms are the same number — Advanced just mixes them." (4) tutorial_conv_basic slide 3/4/5 captions split with `\n` per the directional-branch contract rule. ✅
- **v0.7.11** In-game `(i)` helper button shipped. `BaseGame` mounts an "ⓘ Help" button in the top bar for any game whose id is in `TUTORIAL_REGISTRY`. Click opens the existing `SlideshowFrame` in a Toplevel modal (1280×720, transient + grab) using fixed examples — no dynamic seeding from the live question. Modal pauses the session timer (wall-clock seconds inside the modal subtracted from `session_minutes`); on close the timer resumes. Helper-used sessions: `_helper_used=True` flag short-circuits `record_session` (no points to achievements store), skips every `when="end"` and post-helper `when="live"` achievement, and bypasses the leaderboard prompt. The session is still appended to `sessions_store` with `helper_used=True` so engagement still surfaces in the parent PDF / stats screen. Two new `when="helper"` achievements (Learning category): **Helper Discovered** (10 pts, first use) and **Helper Master** (50 pts, 10 lifetime uses). Lifetime counter `helper_used_total` lives in `achievements_store` stats. Files touched: `games/base_game.py` (helper modal + timer pause + gating), `games/achievements.py` (+2 entries, new `when="helper"` channel), `games/achievements_store.py` (`record_helper_use`, `helper_used_total` default), `games/sessions_store.py` (`helper_used` field on record). ✅
- **v0.7.12** Menu compression + foundation work for v0.8.0 expansions (dark mode, shop, per-difficulty artwork). Main menu collapses from 12 game cards to **4 family tiles** (Multiplication / Division / Fractions: Operations / Fractions: Conversions). Click a family tile → new **difficulty-selection screen** with three cards (Beginner / Intermediate / Advanced) that include a top-of-card asset slot. Tools row widened from 3 → 4 to host a **Shop** placeholder (locked, "Coming v0.8.0", click → messagebox describing planned themes/avatars/frames). Game back-callback now returns to the family's difficulty page rather than the menu, so trying a sibling difficulty is one click. Foundation modules (ready, not yet active): (1) `games/theme.py` — single source-of-truth palette with `_LIGHT` and `_DARK` token dicts and a `theme()` reader that follows `settings.get("theme")`. New menu screens consume it; legacy hardcoded-hex screens migrate as touched. Settings dark-mode toggle stays disabled until rollout completes. (2) `games/assets_loader.py` — optional PNG loader for `assets/games/<family>/<difficulty>.png` with emoji tier-glyph fallback (🌱 / 🔥 / ⚡ for basic / intermediate / advanced). Adding real art later is a zero-code drop-in. `App._tile_images` keeps PhotoImage refs alive (Tk would otherwise GC them mid-render). New game family = one entry in `GAMES` + the three subclasses. Files touched: `game.py` (registry restructure, family/difficulty/tools/shop renderers, _launch signature now `(family, difficulty)`, version bump to 0.7.12), new `games/theme.py`, new `games/assets_loader.py`. ✅
- **v0.7.12.1** Menu polish patch: (1) Default geometry bumped 1080x720 → 1120x800 and minsize 920x560 → 960x600 so the new compressed menu fits without a scrollbar at default size. (2) **Auto-hiding scrollbar.** `show_menu` no longer packs `vsb` up-front; a `_sync_scrollbar` helper compares `canvas.bbox("all")` height against `canvas.winfo_height()` on every inner-frame and canvas `<Configure>` and packs / pack_forgets the scrollbar accordingly. Clean by default, appears only when the user shrinks the window below content height. (3) **Difficulty cards no longer stretch.** `cards.rowconfigure(0, weight=1)` removed and `card.grid(sticky="nsew")` → `sticky="new"` so cards sit at the top of the wrap and only take the height the asset slot + body content require — kills the tall white void below the Play button on a maximised window. (4) Asset slot height 140 → 160 so the tier glyph has more breathing room. ✅
- **v0.7.12.2** Patch over v0.7.12.1: (1) **Mouse-wheel guard.** Wheel scrolled into negative space when content fit (auto-hidden scrollbar but `yview_scroll` still fired). `_install_wheel_handler` now checks `_scroll_target.yview()` first — if `(first, last)` ≈ `(0, 1)` the handler returns immediately. Works uniformly for `Canvas` (menu) and `Text` (Trophy Room). (2) **minsize 960 → 1080.** At 960 px the 4 equal-weight family tiles squish past their labels — "Fractions: Conversions" wraps awkwardly and the rightmost tile starts clipping. Computed floor: 4 × ~235 px tile + 3 × 14 gap + 2 × 48 padding ≈ 1078, rounded up. ✅
- **v0.8.0** Shop & Cosmetics milestone OPEN. Architecture, purchase flow, and the first two cosmetics shipped — the Shop is functional and themed cosmetics are real. (1) **`PurchasesStore`** + `AchievementsStore.spend(points)` + lifetime point bookkeeping (`total_spent` / `get_lifetime_earned`). `profile_manager.load_stores` returns a 5-tuple. (2) Functional Shop modal driven by `SHOP_ITEMS` registry; new items = one entry. Optional `unlock_req` field gates items behind achievements (Matrix requires `sharp_mult_intermediate` so it lines up with the Multiplication: Advanced unlock). (3) **Theme system** — `theme()` reader follows `settings('theme')`; three palettes ship: Light (free, default), Dark (500 pts), Matrix (1000 pts + achievement gate). 30 tokens per palette. New tokens `btn_primary_bg`/`btn_primary_fg`/`card_dim` keep primary buttons legible across themes and let disabled cards recede. Settings → Appearance is a theme picker (Light free / Dark / Matrix); locked rows route to Shop. Theme rollout migrated `game.py`, `base_game.py`, `stats_screen.py`, `practice_missed.py`, `tutorials_panel.py`, all 12 per-game files. `SlideshowFrame` (the slide pages themselves) stays light by design — pedagogical canvas drawings need stable contrast — and v0.8.0 paints `parent.bg = BG` on mount so the dark menu doesn't bleed through padding gaps. (4) Trophy Room header surfaces `lifetime · spent` once the user has spent anything. (5) Stats per-game table fixed: alternating rows now use `card_bg` / `soft` instead of literal "white" so the dark-mode table reads correctly. (6) Settings dialog: 460×400 → 560×600 + resizable height so all 3 themes always fit; toggle button colours themed (the OFF/ON button used to vanish on dark bg). Files touched in this milestone: new `games/purchases_store.py` + `games/theme.py` + `games/assets_loader.py`; `games/profile_manager.py` (5-tuple); `games/achievements_store.py` (spend / lifetime); `game.py` (SHOP_ITEMS registry, themed shop + settings + Trophy Room); `games/base_game.py`; `games/stats_screen.py`; `games/practice_missed.py`; `games/tutorials/tutorials_panel.py` (themed via theme tokens); `games/tutorials/slideshow_frame.py` (parent-bg paint); `games/{mult,div,frac,conv}_*.py`. **Avatar packs + border frames remain** for v0.8.x — assets are already organised under `assets/avatars/` and `assets/borders/`. ✅
- **v0.7.13.2** Achievement-gate on shop items. New optional `unlock_req` field on `SHOP_ITEMS` entries — when present, the item is only purchasable once that achievement is earned, regardless of points balance. **Matrix Mode now requires `sharp_mult_intermediate`** (the same achievement that opens Multiplication: Advanced) — Matrix unlocks naturally as the pupil progresses through the curriculum, not just by grinding points. Shop modal shows a "🔒 Earn '<achievement>' first" hint inside the locked card with the achievement description so the pupil knows what to chase. `_buy()` re-checks the gate at click time as a defensive guard against stale UI. Dark Mode (no `unlock_req`) unchanged: still 500 pts, no progression gate. ✅
- **v0.7.13.1** Dark-mode polish + **Matrix theme**. (1) New tokens `btn_primary_bg` / `btn_primary_fg` / `card_dim` — primary action buttons (Trophy Room, Play, Export PDF) used to render `bg=T["ink"]` which collapses to invisible on dark mode (ink is light grey there); they now read `btn_primary_bg` (dark-slate light / indigo dark / phosphor-green matrix) so they stay legible across themes. `card_dim` collapses to page bg in dark/matrix so disabled cards (e.g. Practice Missed when empty) recede instead of standing out lighter than active cards. (2) **Matrix theme** (1000 pts, second shop item id `matrix_mode`) — green-on-black phosphor palette inspired by the movie. `T["ink"]` = `#00ff41` so digits in question displays glow green automatically; primary buttons are bright green on black; warn=amber, danger=red kept distinct so feedback states still differentiate. (3) Settings → Appearance is now a **theme picker** (Light free / Dark 500 / Matrix 1000) — owned themes show "Use" / "✓ Active"; locked themes show "🔒 Buy in Shop" shortcut. (4) Fixed the `_difficulty_tile` and Practice-Missed Python-level `bg = "white"` assignments that escaped the v0.7.13 kwarg-only regex. (5) `AchievementsStore.spend()` bumps `stats.total_spent`; new `get_total_spent()` and `get_lifetime_earned()` queries. Trophy Room header now shows `lifetime · spent` line below the balance once any spending has happened. ✅
- **v0.7.13** First paid cosmetic — **Dark Mode** (500 pts), purchasable in the Shop. New per-profile `PurchasesStore` (`games/purchases_store.py`) tracks owned cosmetic ids in `<profile_dir>/purchases.json`. `AchievementsStore.spend(points)` deducts from the running total (refuses on insufficient balance). `profile_manager.load_stores` now returns a 5-tuple — purchases store appended. The previously-locked **Shop tile** in the Tools row is now functional: clicking opens a modal listing every entry in `SHOP_ITEMS` (currently just `dark_mode`); each item shows price + Buy/Owned state, balance updates live, double-spend is impossible (`purchases_store.purchase()` is idempotent and `spend()` short-circuits on insufficient points). Settings → Appearance → **Dark mode** toggle replaces the old "Coming soon" placeholder: locked + "Buy in Shop" shortcut when not owned, functional ON/OFF toggle when owned (writes `settings('theme')` as `"light"` / `"dark"` and rebuilds the menu under the modal so the change is visible immediately on close). Theme rollout: `game.py`, `base_game.py`, `stats_screen.py`, `practice_missed.py`, `tutorials_panel.py`, all 12 per-game files, plus `frac_base` migrated to read colors from `theme()` at render time — light-mode visuals identical to v0.7.12.x, dark-mode flips the surface palette without touching brand accents (per-family glyph backgrounds, badge colours, success/danger pills stay literal so they read correctly on both themes). Tutorials' `SlideshowFrame` and the in-game helper modal **stay light intentionally** — pedagogical canvas drawings depend on stable contrast and migrate in a later patch. Files touched: new `games/purchases_store.py`, `games/profile_manager.py` (5-tuple), `games/achievements_store.py` (`spend()`), `game.py` (SHOP_ITEMS registry, functional shop modal, themed toggle, full menu/profile/settings/achievements migration), `games/base_game.py`, `games/stats_screen.py`, `games/practice_missed.py`, `games/tutorials/tutorials_panel.py`, `games/{mult,div,frac,conv}_*.py`. ✅

**v0.7.x tutorial pack milestone CLOSED** — all 8 packs + 2 INTENTIONAL_NO_GUIDE modes covered.

See `CHANGELOG.md` for per-version detail.

---

## v0.7.x remaining — tutorial content packs

Each of the following needs a `tutorial_<game_id>.py` module, plus one line in `games/tutorials/__init__.py` to register it. Read `games/tutorials/TUTORIAL_CONTRACT.md` before starting. The pedagogical method per pack MUST match how Aleks actually teaches the pupil — do not invent a method; confirm with Aleks before writing slides.

Ordering priority: fractions and division packs first (stronger LK20 5. trinn differentiator than mult intermediate/advanced).

| game_id             | status  | tentative slide plan                                                                                       |
|---------------------|---------|-------------------------------------------------------------------------------------------------------------|
| `mult_basic`        | SKIP    | Pure memorisation; panel renders "No guide needed" placeholder. Intentional.                                |
| `mult_intermediate` | ✅ done (v0.7.7.2) | Inline `TOP × BOT` row + partial products with the X-shift placeholder. 6 slides × 5 examples. 4 × 2-dig × 2-dig + 1 × 3-dig × 2-dig stress test (234 × 21 = 4914). |
| `div_intermediate`  | ✅ done (v0.7.6) | 7 slides × 5 exact examples, Norwegian vertical short division, Courier monospace digit columns, dotted "trekker ned" arrow. |
| `mult_advanced`     | ✅ done (v0.7.10) | 4 slides × 5 examples. Same X-shift method as Intermediate, longer factors. Slide 3 fixed reference 23 × 145 = 3335 demonstrates the XX beat. Pitfalls: forgot ONE X (1265) or BOTH X's (1058). |
| `div_advanced`      | ✅ done (v0.7.8.1) | 5 slides × 5 examples (4/5 decimals + 1 integer warmup). Norwegian trappa method extended into terminating decimals via comma + zero bring-down. Reuses Intermediate's `_short_div_steps` and `_draw_layout` directly. |
| `frac_advanced`     | ✅ done (v0.7.9) | 7 slides × 5 examples. Unrelated denominators; two-strategy LCM finding (default multiply, spot shared factor). Always-simplify enforced via slide 6's gcd-divide step. Pitfalls fixed reference 3/13 + 9/19. |
| `conv_advanced`     | ✅ INTENTIONAL_NO_GUIDE (v0.7.10.2) | No tutorial by design — method is the union of conv_basic (frac↔dec) and conv_intermediate (frac↔pct). Per-gid placeholder in tutorials_panel reads "All three forms are the same number — Advanced just mixes them." Pool extended with /20 and /25 entries (13 → 31 pairs). |

## v0.7.x follow-up features (after content is in)

- ~~**In-game `(i)` button.**~~ Shipped in v0.7.11. Final design: fixed examples (no dynamic seeding from the live question) — keeps the helper deterministic and easy to QA, and the trade-off (zero points + zero mastery achievements for the session) is the carrot/stick that disincentivises the obvious abuse vector. Discovered/Master are the only achievements the helper path unlocks.
- **Optional: animated reveals per slide** (fade-in of arrows / partial products). Framework ships without animation; add per-slide only when the step sequence genuinely needs it.
- **Optional: shared Fractions tour.** One entry point that mixes operations and conversions slides into a single guided tour. Parent feedback will tell us if it is needed.
- **Needed: more variation in the fraction conversion game.** Pupil-test reveals too much repetition, at least in advanced mode. Advanced should build upon beginner and intermediate modes.

---

## v0.8.x — Shop & Cosmetics (Avatar System remaining)

**Status:** v0.8.0 shipped — Shop infrastructure + theme cosmetics (Dark, Matrix) are live. The remaining v0.8.x work is the avatar / frame pack: turning the already-organised `assets/avatars/` and `assets/borders/` art into purchasable items in the same `SHOP_ITEMS` registry. Each avatar entry just needs an id, price, optional `unlock_req`, and the existing `assets_loader` machinery handles the rest.

**Why here:** gives achievement points actual spending weight. Retroactively makes every achievement feel more meaningful.

- Spend points on:
  - Color themes (Dark mode, Warm/amber, Classic light)
  - Avatar/icon shown in profile header and beside game question
  - Avatar border frame (unlockable overlay on the portrait)
- Theme applied globally, persisted per profile in settings.json.
- Dark mode is the priority unlock — highest perceived value.

Avatar system design (assets already downloaded and organised):

- Asset source: AI portrait pack — 100 male portraits, 4 races × 25 professions.
- Organised into thematic packs in `assets/avatars/`:
  - **Scholar & Arcane** (4): Wizard, Alchemist, Sorcerer, Illusionist, Enchanter, Artificer
  - **Hero & Honour** (4): Knight, Paladin, Warrior, Samurai, Gladiator
  - **Shadow & Stealth** (4): Assassin, Ninja, Thief, Pirate
  - **Wild & Fierce** (4): Barbarian, Berserker
  - **Dark Arts** (4): Necromancer, Summoner
  - **Craftsman** (4): Blacksmith (all 4 races)
- 11 ornate fantasy border frames in `assets/borders/` (Avatar Kit frames).
- 16 UI-style item frames in `assets/item_frames/` (Item Frame Kit).
- Store unlock tiers: 1 free avatar per profile (`assets/avatars/starting_avatar`), packs unlock by spending points.
- Preprocessing: resize 2048×2048 → 256×256 before bundling (one script, run once).
- Bundled into exe via PyInstaller `--add-data "assets;assets"`.
- Path resolution via `assets_path()` utility (works in both dev and packaged builds).
- Female avatars available in source pack — deferred, add later if requested.

---

## v0.9.0 — Polish & Pre-Release

- Credits screen (main menu or about button): bavka (itch.io, avatar portraits + UI frames); creative input / prompt engineering: Magnus Landaas; developer: Aleksander Lie.
- Custom app icon (.ico, shown in taskbar and exe).
- Consistent font sizing across all screens.
- Inno Setup installer wrapping the PyInstaller exe — desktop shortcut, Add/Remove Programs entry, install/uninstall flow.
- Windows SmartScreen workaround documented for buyers.
- Gumroad product page: screenshots, short screen-recording demo, 199 NOK, LK20 5. trinn description.
- ~~**`game.py` decomposition.**~~ ✅ Six modal/page screens carved into `games/screens/` across two passes:
  - **First pass (modals):** `settings_dialog.py` (204 lines, `show_settings_dialog` + `_THEME_META` + theme picker), `shop_modal.py` (270 lines, `show_shop_modal` + `_render_item` + `_buy` + `SHOP_ITEMS` registry), `trophy_room.py` (165 lines, `show_trophy_room` + tag/insertion helpers).
  - **Second pass (pages):** `profile_screen.py` (191 lines, `show_profile_screen` + `load_profile` + `_profile_card`), `main_menu.py` (736 lines, `show_menu` + `show_menu_matrix` + `_family_tile` + `_tools_row` + `_build_tools_tiles` + `_shop_tile`), `difficulty_screen.py` (344 lines, `show_difficulty` + `show_difficulty_matrix` + `_difficulty_tile` + `_render_lock_hint`).
  Every new module is under 50 KB (largest: `main_menu.py` at 31 KB, well under the bindfs truncation cap). All public App methods (`show_profiles` / `show_menu` / `show_difficulty` / `_show_settings` / `_show_shop` / `_show_achievements` / `_load_profile`) survive as four-line delegators so every existing call-site keeps working. `game.py` collapsed from ~98 KB / 2217 lines → **~20 KB / 504 lines** — App-controller core only (`__init__`, `_apply_styles`, wrappers, `_launch*`, `_clear`, `_install_wheel_handler`, `main`) plus the `GAMES` and `_DIFFICULTY_TIERS` registries the screen modules lazy-import. Pure refactor — no behaviour change, no version bump.
- ~~**Token migration for in-game `(i)` Help button.**~~ ✅ The `_open_helper_modal` body itself was already theme-tokened (uses `T["bg"]` for the Toplevel + host frame); the helper-trigger button in `BaseGame._setup_top_bar` had three light-mode hex residues (`fg="#4f46e5"`, `activebackground="#f8fafc"`, `activeforeground="#4338ca"`) — migrated to `T["accent"]` / `T["soft"]` / `T["accent_dark"]`. SlideshowFrame stays light-mode by design (pedagogical canvas drawings need stable contrast); its on-mount `parent.configure(bg=BG)` still paints the helper-modal host so the dark-mode menu doesn't bleed through.

---

## v1.0.0 — First Public Release

Milestone: sellable word-of-mouth product.

- All of the above stable and tested.
- Copyright and version displayed in-app.
- Clean installer, no raw-exe sharing.
- Gumroad page live.
- Distribution: Norwegian parent Facebook groups, homeschool networks, private school communities.

---

## Post-1.0 backlog

LK20 coverage (fraction word problems, probability, equations, time) + parking lot features (addition/subtraction modes, natural-science quiz, classroom license, soundtrack, etc.): see `ROADMAP_POST_1.0.md`.
