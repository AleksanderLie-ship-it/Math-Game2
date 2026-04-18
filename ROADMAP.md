# Math Practice — Product Roadmap
## Copyright (c) 2026 Aleksander Lie. All rights reserved.

Current version: **v0.7.3**
Target: word-of-mouth sellable at 199 NOK to Norwegian parents/homeschool networks

---

## Repo quick map (for future context)

Runtime is Windows, Python 3.14 (Tk 9). The user ships PyInstaller exes from
`build.bat`; `dist/` holds the latest builds. Exe VERSION is set manually in
`build.bat`; in-app version is `game.py::__version__`; plain-text changelog
is the `VERSION` file (single source of truth for release notes).

```
game.py                       entry point + App class (menu, nav, wiring)
build.bat                     PyInstaller one-file build (update VERSION= by hand)
VERSION                       current version on line 1, full CHANGELOG below
ROADMAP.md                    this file
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
                              .daily_counts / .per_game_summary /
                              .accuracy_series / .total_minutes
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

  tutorials/                  added v0.7.0 — see v0.7 section below
    __init__.py               TUTORIAL_REGISTRY
    slideshow_frame.py        reusable SlideshowFrame + drawing helpers +
                              award_tutorial_achievements / toast (v0.7.2)
    tutorials_panel.py        grid-of-cards entry screen
    tutorial_div_basic.py     first content pack
    tutorial_frac_basic.py    Fractions: Beginner pack (v0.7.2)
    tutorial_frac_intermediate.py  Fractions: Intermediate pack (v0.7.3)

assets/                       avatar packs + UI frames (used from v0.8.0)
```

Profile data on disk: `%APPDATA%\MathPractice\profiles\<name>\` containing
`achievements.json`, `scores.json`, `missed.json`, `sessions.json`. Global
settings at `%APPDATA%\MathPractice\settings.json`.

Sandbox testing: `test_tutorials_mock.py` at `/sessions/loving-wonderful-fermat/`
validates tutorial slide draws against a MockCanvas without needing Tk —
run it after any tutorial change. `test_tutorials.py` needs a DISPLAY and
is only useful on the user's machine.

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

### v0.7.0 — Tutorial Slideshow  ✅ FRAMEWORK SHIPPED (2026-04-17)
**Why here:** Makes the product a teaching tool, not just a quiz.
Significant differentiator for the 199 NOK price point.

**Content added in v0.7.3 (2026-04-18):**
- Third content pack shipped: **tutorial_frac_intermediate** (Fractions:
  Intermediate, 8 slides × 5 examples). LCM → rewrite both fractions →
  same-denom combine → reduce-if-possible → pitfall. The 5 cycled
  examples include one reducer (5/6 − 1/2 = 2/6 → 1/3) so the pupil
  meets the ÷gcd step inside the carousel; slide 7 branches on gcd>1
  per example with a fixed 2/6 → 1/3 mini-demo for the non-reducing
  case so the technique is always visible. Pitfall is a three-column
  layout vs. the two canonical wrongs (3/7 and 3/12) with ≠ glyphs
  between the columns, same cleanup pattern as the frac_basic pitfall
  slide.
- Scholar achievement (Learning, 100 pts — "Read three different
  tutorials") flipped from hidden to visible. Live tutorial count is
  now 3, so the threshold is achievable.

**Content added in v0.7.2 (2026-04-18):**
- Second content pack shipped: **tutorial_frac_basic** (Fractions: Beginner,
  8 slides × 5 examples). Same-piece-size intuition → combine tops → keep
  bottom → answer → bar model → subtraction mirror → pitfall. Examples
  keep results in raw unreduced form to match how the game renders them.
- New "Learning" achievement category wired to a new `when="tutorial"`
  trigger: Bookworm, Full Walkthrough, Curious Mind (visible) + Scholar
  (hidden, 3 different tutorials). Popups fire the moment the pupil earns
  them — not at next session end — via a shared toast helper in
  `slideshow_frame.py`.
- `AchievementsStore` gained `tutorials_viewed`, `tutorials_finished`,
  `tutorial_example_cycled` stats and three idempotent recorder methods.

**Bugs fixed in v0.7.1 (2026-04-18):**
- Conversions: Intermediate — "Convert 38% to fraction" now accepts both
  3/8 and 38/100 (= 19/50). Same fix applies to every rounded pool pair
  (1/3↔33, 2/3↔67, 1/8↔13, 3/8↔38) across both to_pct and to_fraction.
- Conversions: Advanced — "Convert 38% to decimal" now accepts 0.38 in
  addition to 0.375. Only applies when a percentage is source or target
  (frac_to_dec and dec_to_frac stay strict — student has exact data).
- Mechanism: new FractionBase._alternate_expected() hook; conv_intermediate
  and conv_advanced override it to return the literal pct/100 Fraction
  for rounded pairs.

**What shipped in v0.7.0:**
- `games/tutorials/` package with the full architecture
  (see VERSION changelog for module layout and the 4-name content contract
  TITLE / LEAD / SLIDES / EXAMPLES)
- Reusable `SlideshowFrame` widget: pure Canvas (720x340), prev/next +
  keyboard arrows, "Next example" button cycling curated problems
- `TutorialsPanel` full-page browser, grouped by curriculum category,
  lock state mirrored from `UNLOCK_REQUIREMENTS`
- Main-menu "Open Tutorials" card (Review row, next to Practice Missed
  and Progress & Stats)
- First content pack: **tutorial_div_basic** (4 slides x 3 examples,
  method = division as reverse multiplication using the times table)
- Shared drawing helpers exported from `slideshow_frame`:
  `draw_centered_expression`, `draw_note`, `draw_arrow`, `draw_pill`

**What's left in v0.7.x — tutorial content packs.**

Fraction operations games were also revamped in v0.7.1:
- frac_basic now truly shows same-denominator prompts. Previously
  Fraction(2, 6) auto-simplified to 1/3 and questions appeared as
  "1/3 − 1/6", violating the card's "same denominator" promise. Raw
  numerators and the raw denominator are now preserved for display.
- frac_intermediate — left as-is (it was already correct).
- frac_advanced rewritten as proper fractions with unrelated
  denominators (neither divides the other). Pool includes primes
  (7, 11, 13, 17, 19) and composites (10, 12, 14, 15, 16, 18, 20).
  Forces a real LCM step — the pedagogical distinction from
  Intermediate's "one divides the other" pairs. Example: 3/13 + 9/19.
  No mixed numbers on screen.

Each of the following needs a `tutorial_<game_id>.py` module following the
same shape as `tutorial_div_basic.py`, plus one line in
`games/tutorials/__init__.py` to register it. The pedagogical method per
pack MUST match how Aleks actually teaches Phillip — do not invent a
method. Below each game lists the *tentative* slide plan; confirm with
Aleks before writing slides.

Ordering priority: finish the beginner tier across categories first (most
used, easiest wins), then intermediate, then advanced. Fractions packs
are higher-impact than Division Intermediate/Advanced because fractions
are the primary LK20 5. trinn differentiator.

| game_id             | status  | tentative slide plan                                                                                       |
|---------------------|---------|-------------------------------------------------------------------------------------------------------------|
| `mult_basic`        | SKIP    | Pure memorisation; panel renders "No guide needed" placeholder. Intentional, do not add.                    |
| `div_basic`         | ✅ done | Shipped in v0.7.0.                                                                                          |
| `frac_basic`        | ✅ done | Shipped in v0.7.2 (8 slides × 5 examples; same-piece-size intuition + bar model + pitfall).                  |
| `conv_basic`        | TODO    | Fraction ↔ decimal for "clean" denominators (2, 4, 5, 8, 10). Method: rewrite as tenths/hundredths. Place-value grid. |
| `mult_intermediate` | TODO    | 2-digit × 1-digit partial products. Break 24×7 into (20×7)+(4×7). Arc arrows from each digit.              |
| `div_intermediate`  | TODO    | Short division with remainder. Step the dividend digit-by-digit; carry remainder across. Reuse times-table visual from div_basic. |
| `frac_intermediate` | ✅ done | Shipped in v0.7.3 (8 slides × 5 examples; LCM → rewrite both → combine → reduce; three-column pitfall vs. 3/7 and 3/12). |
| `conv_intermediate` | TODO    | Fraction ↔ percentage. Method: "% means out of 100". 3/4 → 75/100 → 75%. Bar model with 100 squares.        |
| `mult_advanced`     | TODO    | 2-digit × 2-digit standard algorithm. Partial products stacked, carry rules. Biggest risk of slide overflow — keep numbers small (use 14×12 style examples). |
| `div_advanced`      | TODO    | Long division. Decide method with Aleks: Norwegian "trappa"/staircase layout vs. English bring-down layout. |
| `frac_advanced`     | TODO    | Mixed numbers + improper fractions. Convert to improper → add → convert back. Two-lane layout (original form vs. improper form) throughout. |
| `conv_advanced`     | TODO    | All three directions consolidated. Build on conv_basic + conv_intermediate. Slide 1 = "the three forms are the same number". |

**v0.7.x follow-up features (after content is in):**
- In-game `(i)` button: small icon in the top-right of each game screen
  during a session that opens the same slideshow in a modal/overlay,
  pre-seeded with the current question as its example.
  `base_game.BaseGame.__init__` is the right place to add the button;
  the overlay should pause the session timer.
- Optional: animated reveals per slide (fade-in of arrows / partial
  products). Framework intentionally ships without animation — only add
  per slide where the step sequence genuinely needs it.
- Optional: one "shared" tutorial entry point for Fractions that mixes
  operations and conversions slides into a single guided tour. Parent
  feedback will tell us if that's needed.
- Needed: More variation in the fraction conversion game, player test reveals too much repetition, at least for advanced mode. 
  Advanced mode should build upon both beginner and 
  intermediate modes.


**Implementation notes for whoever picks this up (future Claude, read these before writing any slide code):**
- Canvas is a fixed 720x340. Anything that might reach x>720 or y>340
  WILL clip. Use `canvas.bbox` on a hidden probe text to measure strings
  before drawing pills/strips around them. See the Slide 4 Tip box in
  `tutorial_div_basic._slide_4` for the measure-then-draw pattern.
- Widget-level `pady=`/`padx=` on `tk.Frame/Label/Button` must be a
  single int in Tk 9 / Python 3.14. Tuples only work on `.pack(pady=…)`
  and `.grid(pady=…)`. This bit us once in v0.7.0 — fix the caller, not
  the widget.
- Colour palette is defined once in `slideshow_frame.py`
  (`INK MUTED DIM FAINT SOFT ACCENT ACCENT_DARK GOOD WARN BG CARD_BG
  CARD_BORDER`). Import from there, don't hardcode hex.
- Every new pack adds one entry to `TUTORIAL_REGISTRY` in
  `games/tutorials/__init__.py`. The panel auto-picks it up — no changes
  needed in `tutorials_panel.py`.
- `tutorials_panel._CATEGORIES` hardcodes the category ordering; add new
  game_ids to the right category list if they introduce a new game family.
- Test harness: `test_tutorials_mock.py` at repo root (sandbox path) runs
  every slide × every example against a MockCanvas without needing Tk.
  Run it after adding a pack to catch silly errors early. Tk-dependent
  interactive test is `test_tutorials.py` — requires a DISPLAY, skipped
  in sandbox.

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
  - **Scholar & Arcane** (4): Wizard, Alchemist, Sorcerer, Illusionist, Enchanter, Artificer
  - **Hero & Honour** (4): Knight, Paladin, Warrior, Samurai, Gladiator
  - **Shadow & Stealth** (4): Assassin, Ninja, Thief, Pirate
  - **Wild & Fierce** (4): Barbarian, Berserker
  - **Dark Arts** (4): Necromancer, Summoner
  - **Craftsman** (4): Blacksmith (all 4 races)
- 11 ornate fantasy border frames in `assets/borders/` (Avatar Kit frames)
- 16 UI-style item frames in `assets/item_frames/` (Item Frame Kit)
- Store unlock tiers: 1 free avatar on profile , located in assets>avatars>starting_avatar, packs unlock by spending points
- Preprocessing: resize from 2048×2048 → 256×256 before bundling (one script, run once)
- Bundled into exe via PyInstaller `--add-data "assets;assets"` flag
- Path resolution via `assets_path()` utility (works in both dev and packaged builds)
- Female avatars available in the source pack — deferred, add in later update if requested

---

### v0.9.0 — Polish & Pre-Release
**Why here:** Visual and UX pass before any public distribution.

- Credits screen (accessible from main menu or about button)
  - Asset credits: bavka (https://itch.io/profile/bavka) -- avatar portraits and UI frames
  - Creative input & prompt engineering: Magnus Landaas
  - Developer: Aleksander Lie
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