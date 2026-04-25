# Math Practice — Post-1.0 Backlog

Copyright (c) 2026 Aleksander Lie. All rights reserved.

Candidate work after v1.0.0 ships. Nothing here is committed — re-evaluate based on parent feedback and sales.

---

## LK20 Curriculum Coverage — planned game families

These are the goals the parent report currently labels "Ikke påbegynt i appen". Each one becomes a candidate post-1.0 game family. Adding one is cheap: ship the game module + achievement IDs, then flip `covers=[]` to a populated list in `games/curriculum.py` and the report page updates itself.

Goal IDs correspond to entries in `games/curriculum.py`:

- **g5 — Fraction word problems** ("Formulere og løse problemer fra egen hverdag som har med brøk å gjøre.")
  Game design: small set of parameterised Norwegian word problems, single numeric answer, fraction or mixed-number accepted. Fits the existing FractionBase input parser. Priority: high — completes brøk coverage.

- **g6 — Probability and simple combinatorics** ("Diskutere tilfeldighet og sannsynlighet i spill og praktiske situasjoner og knytte det til brøk.")
  Scope includes the classic "2 shirts × 2 pants × 2 socks = 8 combinations" counting question. Good cross-link to brøk goal since the answer is expressible as a fraction. Priority: high — small scope, high curriculum value.

- **g7 — Equations and inequalities** ("Løse ligninger og ulikheter gjennom logiske resonnementer ...")
  Game design: one-variable linear equations of increasing complexity. Tiers could mirror the existing mult/div structure (basic / intermediate / advanced). Priority: medium — larger UX scope, may need a guided-step mode.

- **g9 — Time word problems** ("Formulere og løse problemer fra egen hverdag som har med tid å gjøre.")
  Durations, start/end times, schedules. Priority: medium — separate answer parser needed (HH:MM input).

Explicitly **out of scope** (noted in `curriculum.py`):

- LK20 goal 8 (regneark / personlig økonomi) — spreadsheet skills.
- LK20 goal 10 (programmere algoritmer med variabler, vilkår og løkker) — programming.

Ordering suggestion when we revisit after v1.0:

g6 (probability) → g5 (fraction word problems) → g9 (time) → g7 (equations).

---

## Parking Lot (evaluate based on feedback)

- **Fraction answer scoring: require reduced form + tiered points.** For conversion games asking for a fraction answer, reject unreduced forms (e.g. `80/100` when `4/5` is expected) with feedback "correct value — simplify it." Set `REQUIRE_REDUCED = True` on conversion game classes; add the check in `FractionBase._answers_match` comparing `given.denominator == expected.denominator`. Separately, consider a session "score" system (distinct from correct/accuracy counters) that weights streak, speed, and answer quality — the right architectural home for point bonuses, rather than bolting it onto the current leaderboard schema.
- Addition and subtraction game modes (younger age bracket).
- Natural science quiz mode (Aleks already teaches this to the pupil).
- Classroom / teacher license (up to 30 students, 799–999 NOK).
- Soundtrack (requires pygame dependency — evaluate if worth the exe-size cost).

---

## v1.1.x candidate — "Boss Mode" (math-themed shooter mini-game)

**Concept:** Space Invaders / Typing-of-the-Dead hybrid where the math question is the weapon. Enemies (demons / monsters, DOOM-aesthetic red-and-brown palette) advance toward the pupil; correct answer fires a projectile at the frontmost enemy; wrong answer wastes the turn and enemies step forward but do NOT directly damage HP. HP drops only when an enemy physically reaches the pupil. Clear a wave → next wave with faster / more enemies. HP=0 → game-over + score.

**Hook into mastery system:** unlocked per tier when the pupil hits the v0.8.0 mastery threshold. "You mastered Multiplication Intermediate → the Demon Multiplier appears." One boss per mastered tier, themed on the topic:

- Demon Multiplier (times-table attacks)
- Division Devourer (remainder attacks)
- Fraction Fiend (splits into pieces when hit)
- Conversion Changeling (shifts between frac / dec / pct forms)

Gives mastery a felt payoff, not just a coloured badge. Gives post-1.0 content that keeps the product fresh after shipping.

**Feasibility:** pure Tk Canvas, no new runtime deps. Canvas handles drawing, sprites, game loop via `canvas.after(16, tick)`, keyboard input, bbox collision. 15–30 FPS realistic with 5–10 entities on screen — fine for this scope. Scope estimate: 400–600 lines for a shipping-grade v1 (core loop ~100, enemy movement ~50, HP / game-over ~50, wave progression ~30, polish ~150, BaseGame integration ~50). One-to-two focused sessions for playable v1, another session or two for polish. Canvas-drawn polygon sprites initially (zero asset work); PNG sprite pack upgrade later if wanted.

**Audio decision:** if added with pygame.mixer for laser SFX / menu music, combines with the parking-lot Soundtrack item. Decide together.

**Pedagogical risk — punishment calibration.** If a single wrong answer instantly damages HP the pupil who is trying to learn gets discouraged and drops the mode. If wrong answers do nothing the dopamine deflates. Sweet spot: wrong answer wastes the turn (enemies step forward), HP damage only from enemy-reaches-player contact. Encode as a constant from day one so it is tunable after pupil testing.

**Do NOT commit to this before v1.0 ships.** Parked here intentionally — the pre-1.0 stack (tutorial packs + menu redesign + shop + avatars + polish + installer) is already the right scope for shipping on schedule.
