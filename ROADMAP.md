# Math Practice — Product Roadmap
## Copyright (c) 2026 Aleksander Lie. All rights reserved.

Current version: **v0.6.1**
Target: word-of-mouth sellable at 199 NOK to Norwegian parents/homeschool networks

---

## Priority Order

### v0.4.0 — User Profiles & Main Menu
**Why first:** Every feature after this point (fractions, stats, shop) touches
saved data. Doing profiles now means all future content automatically supports
multiple users. Retrofitting profiles later would mean rewriting every store.

- Main menu screen on launch (before game selection)
  - Create new profile (name entry)
  - Load existing profile (list of saved profiles)
  - Delete profile (with confirmation)
- Each profile gets its own isolated save folder:
  %APPDATA%\MathPractice\profiles\{name}\
  containing achievements.json, scores.json, missed.json
- Refactor all three stores to be path-aware (accept profile directory)
- Active profile shown in game selection header
- Settings placeholder (for future use)

---

### v0.5.0 — Fraction Game
**Why here:** New content before polish. Fractions are the most relevant
gap for 5th grade Norwegian curriculum (LK20). Three difficulty tiers:

- Beginner: same denominator addition/subtraction (1/4 + 2/4 = 3/4)
- Intermediate: different denominators, find common denominator (1/3 + 1/4)
- Advanced: mixed numbers and improper fractions (1½ + 2¾)

Locked behind achievements same as multiplication/division.
New achievements added for fraction milestones.

---

### v0.6.0 — Progress & Stats Screen  ✅ SHIPPED (2026-04-17)
**Why shipped first:** Parents are the buyer. They need visible proof the tool
works. Promoted ahead of the tutorial slideshow because it is pure display
infrastructure on top of already-existing data and a stronger sales hook.

- Accessible from main menu per profile (new card in Review row)
- Summary tiles: total correct, days played, best streak, total practice time
- Questions-per-day bar chart (last 14 days, Canvas-drawn, correct + attempts)
- Accuracy trend per game mode — one sparkline per game with data
- Per-game summary table: sessions, correct, attempts, avg accuracy, best
  streak, last played
- Recent achievements highlight strip
- One-page A4 PDF export for parents (pure-Python, no extra deps)

New infrastructure added to support this:
- `games/sessions_store.py` — per-session log at `<profile>/sessions.json`
- `games/stats_screen.py`   — the full-page StatsScreen
- `games/pdf_export.py`     — dependency-free PDF writer
- `games/curriculum.py`     — LK20 5. trinn goal mapping (added in v0.6.1)
- `profile_manager.load_stores()` now returns a 4-tuple including SessionsStore
- `BaseGame.__init__` accepts an optional `sessions_store` kwarg and records
  every session end (date, game_id, correct, attempts, accuracy, streak,
  minutes)

v0.6.1 patch (2026-04-17) upgraded the PDF export from a one-page English
card into a 3-page Norwegian professional parent report with an LK20
competence-goal page. The report is the primary sales hook for parents —
it turns drill data into a language teachers and parents already trust.

---

### v0.7.0 — Tutorial Slideshow (the (i) button)  [deferred from v0.6]
**Why here:** Makes the product a teaching tool, not just a quiz.
Significant differentiator for the 199 NOK price point.

- Small (i) button in corner of each game screen during play
- Opens a Canvas-based slideshow with a freshly generated example problem
- Step-by-step slides with animated arrows showing exactly which digit
  multiplies which — mirrors the method Aleks uses when teaching Phillip
- Each game mode has its own slide sequence:
  - Mult Basic: single-digit × single-digit with simple grouping visual
  - Mult Intermediate/Advanced: partial products method with arc arrows
  - Div Basic: short division with remainder explanation
  - Div Intermediate/Advanced: long division step-by-step
  - Fractions: denominator alignment, finding LCM, simplification
- Forward/back navigation through slides
- No static image assets — all rendered programmatically on Canvas

---

### v0.8.0 — Shop & Cosmetics (including Avatar System)
**Why here:** Gives achievement points actual spending weight.
Retroactively makes every achievement feel more meaningful.

- Spend points on:
  - Color themes (Dark mode, Warm/amber, Classic light)
  - Avatar/icon shown in profile header and beside game question
  - Avatar border frame (unlockable overlay on the portrait)
  - Bonus XP multiplier (2× points for one session)
- Theme applied globally, persisted per profile in settings.json
- Dark mode is the priority unlock — highest perceived value

**Avatar system design (assets already downloaded and organised):**
- Asset source: AI portrait pack — 100 male portraits, 4 races × 25 professions
- Organised into thematic packs in `assets/avatars/`:
  - **Scholar & Arcane** (24): Wizard, Alchemist, Sorcerer, Illusionist, Enchanter, Artificer
  - **Hero & Honour** (20): Knight, Paladin, Warrior, Samurai, Gladiator
  - **Nature & Spirit** (20): Druid, Ranger, Cleric, Monk, Bard
  - **Shadow & Stealth** (16): Assassin, Ninja, Thief, Pirate
  - **Wild & Fierce** (8): Barbarian, Berserker
  - **Dark Arts** (8): Necromancer, Summoner
  - **Craftsman** (4): Blacksmith (all 4 races)
- 11 ornate fantasy border frames in `assets/borders/` (Avatar Kit frames)
- 16 UI-style item frames in `assets/item_frames/` (Item Frame Kit)
- Store unlock tiers: 1 free avatar on profile creation, packs unlock by spending points
- Preprocessing: resize from 2048×2048 → 256×256 before bundling (one script, run once)
- Bundled into exe via PyInstaller `--add-data "assets;assets"` flag
- Path resolution via `assets_path()` utility (works in both dev and packaged builds)
- Female avatars available in the source pack — deferred, add in later update if requested

---

### v0.9.0 — Polish & Pre-Release
**Why here:** Visual and UX pass before any public distribution.

- Custom app icon (.ico file, shown in taskbar and exe)
- Better typography — consistent font sizing across all screens
- Inno Setup installer wrapping the PyInstaller exe
  - Creates desktop shortcut
  - Appears in Add/Remove Programs
  - Proper install/uninstall flow
- Windows SmartScreen workaround documented for buyers
- Gumroad product page:
  - Screenshots, short screen recording demo
  - Price: 199 NOK
  - Clear description tied to Norwegian 5th grade curriculum (LK20)

---

### v1.0.0 — First Public Release
**Milestone:** Sellable word-of-mouth product.

- All of the above stable and tested
- Copyright and version displayed in-app
- Clean installer, no raw exe sharing
- Gumroad page live
- Distribution: Norwegian parent Facebook groups, homeschool networks,
  private school communities

---

## LK20 Curriculum Coverage — planned game families

These are the goals the parent report currently labels "Ikke påbegynt i
appen". Each one becomes a candidate post-1.0 game family. Adding one is
cheap: ship the game module + achievement IDs, then flip `covers=[]` to a
populated list in `games/curriculum.py` and the report page updates itself.

Goal IDs correspond to entries in `games/curriculum.py`:

- **g5 — Fraction word problems** ("Formulere og løse problemer fra egen
  hverdag som har med brøk å gjøre.")
  Game design: small set of parameterised Norwegian word problems, single
  numeric answer, fraction or mixed-number accepted. Fits the existing
  FractionBase input parser. Priority: high — completes brøk coverage.

- **g6 — Probability and simple combinatorics** ("Diskutere tilfeldighet
  og sannsynlighet i spill og praktiske situasjoner og knytte det til
  brøk.") Scope includes the classic "2 shirts × 2 pants × 2 socks = 8
  combinations" counting question. Good cross-link to brøk goal since the
  answer is expressible as a fraction. Priority: high — small scope,
  high curriculum value.

- **g7 — Equations and inequalities** ("Løse ligninger og ulikheter
  gjennom logiske resonnementer ...") Game design: one-variable linear
  equations of increasing complexity. Tiers could mirror the existing
  mult/div structure (basic / intermediate / advanced). Priority:
  medium — larger UX scope, may need a guided-step mode.

- **g9 — Time word problems** ("Formulere og løse problemer fra egen
  hverdag som har med tid å gjøre.") Durations, start/end times, and
  schedules. Priority: medium — separate answer parser needed
  (HH:MM input).

Explicitly **out of scope** for this product (noted in `curriculum.py`):
- LK20 goal 8 (regneark / personlig økonomi) — spreadsheet skills
- LK20 goal 10 (programmere algoritmer med variabler, vilkår og løkker) —
  programming

Ordering suggestion when we revisit after v1.0:
g6 (probability) → g5 (fraction word problems) → g9 (time) → g7 (equations).

---

## Parking Lot (post-1.0, evaluate based on feedback)

- **Fraction answer scoring: require reduced form + tiered points**
  For conversion games asking for a fraction answer, reject unreduced forms
  (e.g. 80/100 when 4/5 is expected) with feedback "correct value — simplify it."
  Set `REQUIRE_REDUCED = True` on conversion game classes; add the check in
  `FractionBase._answers_match` comparing `given.denominator == expected.denominator`.
  Separately, consider a session "score" system (distinct from the correct/accuracy
  counters) that weights streak, speed, and answer quality — this is the right
  architectural home for point bonuses, rather than bolting it onto the current
  leaderboard schema.

- Addition and subtraction game modes (younger age bracket)
- Natural science quiz mode (Aleks already teaches this to Phillip)
- Classroom/teacher license (up to 30 students, 799-999 NOK)
- Soundtrack (requires pygame dependency — evaluate if worth the exe size cost)
- Web version / cross-platform rebuild (larger effort, different audience)
- Code signing certificate (~$300 USD/year) for cleaner SmartScreen experience
- GDPR compliance + student data handling (required for school contracts)

---

## Version Key

| Range     | Meaning                            |
|-----------|-----------------------------------|
| 0.1–0.3   | Core game + achievements (done)    |
| 0.4–0.5   | Profiles + new content (done)      |
| 0.6       | Analytics — Progress & Stats (done)|
| 0.6.1     | Parent report (Norwegian, LK20)    |
| 0.7       | Teaching tools — Tutorial (i)      |
| 0.8–0.9   | Monetisation + polish              |
| 1.0       | Public release                     |
| 1.x       | Post-launch iteration              |
