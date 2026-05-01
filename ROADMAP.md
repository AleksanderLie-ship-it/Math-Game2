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

## v0.8.0 — Shop & Cosmetics (including Avatar System)

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
