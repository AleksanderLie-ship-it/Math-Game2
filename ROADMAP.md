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
- **v0.7.8** Eighth tutorial pack shipped: div_advanced (Norwegian trappa long division extended into terminating decimals via comma + zero bring-down, 6 slides × 5 examples). Reuses Intermediate's `_short_div_steps` and `_draw_layout` directly. ✅

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
| `mult_advanced`     | TODO    | Build on mult_intermediate. 3-dig × 2-dig and 3-dig × 3-dig with the XX double-placeholder for the hundreds digit. Open with one refresher slide reusing `_mult_steps` + `_draw_layout`. May want more than 7 slides. |
| `div_advanced`      | ✅ done (v0.7.8) | 6 slides × 5 examples, Norwegian trappa method extended into terminating decimals via comma + zero bring-down. Reuses Intermediate's `_short_div_steps` and `_draw_layout` directly. |
| `frac_advanced`     | TODO    | Mixed numbers + improper fractions. Convert to improper → add → convert back. Two-lane layout (original form vs. improper form) throughout. |
| `conv_advanced`     | TODO    | All three directions consolidated. Build on conv_basic + conv_intermediate. Slide 1 = "the three forms are the same number". May want a structurally different shape (two parallel lanes, not linear carousel). |

## v0.7.x follow-up features (after content is in)

- **In-game `(i)` button.** Small icon in the top-right of each game screen that opens the same slideshow in a modal/overlay, pre-seeded with the current question as its example. `base_game.BaseGame.__init__` is the right place to add the button; the overlay should pause the session timer.
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
