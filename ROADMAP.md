# Math Practice — Product Roadmap
## Copyright (c) 2026 Aleksander Lie. All rights reserved.

Current version: **v0.5.0**
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

### v0.6.0 — Tutorial Slideshow (the (i) button)
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

### v0.7.0 — Progress & Stats Screen
**Why here:** Parents are the buyer. They need visible proof the tool works.
All data already exists in JSON — this is purely a display layer.

- Accessible from main menu per profile
- Questions answered per day (bar chart, last 14 days)
- Accuracy trend over time per game mode
- Streak records and achievement highlights
- Simple export to PDF or printable summary (optional)

---

### v0.8.0 — Shop & Cosmetics
**Why here:** Gives achievement points actual spending weight.
Retroactively makes every achievement feel more meaningful.

- Spend points on:
  - Color themes (Dark mode, Warm/amber, Classic light)
  - Avatar/icon shown in profile header
  - Bonus XP multiplier (2× points for one session)
- Theme applied globally, persisted per profile in settings.json
- Dark mode is the priority unlock — highest perceived value

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

| Range     | Meaning                        |
|-----------|-------------------------------|
| 0.1–0.3   | Core game + achievements (done)|
| 0.4–0.5   | Profiles + new content         |
| 0.6–0.7   | Teaching tools + analytics     |
| 0.8–0.9   | Monetisation + polish          |
| 1.0       | Public release                 |
| 1.x       | Post-launch iteration          |
