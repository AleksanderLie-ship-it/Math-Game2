# Changelog

All notable changes to Math Practice.
Current version lives in `VERSION` (single line).

v0.7.7  (2026-04-24)
--------------------
- New tutorial pack: Multiplication: Intermediate — multi-digit
  vertical multiplication via partial products with the Norwegian
  "X-shift" placeholder. Each digit of the bottom number multiplies
  the whole top; the tens partial is written with an "X" in the ones
  column so the place-value shift is made visible rather than left
  invisible.
  games/tutorials/tutorial_mult_intermediate.py — 7 slides × 5
  curated examples. Slide beats:
    1  Read the question (skeleton pill "top × bottom, one partial per
       bottom-digit" + faint mini-layout with dashed partial/sum slots)
    2  The big idea (arc-arrow swoop from the ones digit of the bottom
       to every digit of the top — the "each bottom-digit hits the
       whole top" move; pill naming both partials for the cycled
       example plus the X-shift reminder)
    3  First partial: ones × top (LEFT: column-by-column carry trace
       "ones: 4×5 = 20 — write 0, carry 2 / tens: 2×5 + 2 = 12 — write
       12", one line per top-digit; RIGHT: live layout through partial
       0, GOOD pill "first partial = P")
    4  Second partial: tens × top + X shift (live layout through
       partial 1, ACCENT highlight, arc arrows from the tens digit; pill
       "{top} × {d_tens} = P, then append X — the X holds the ones slot
       open"; bottom note: "tens count ten times" in plain language)
    5  Add the partials (complete layout; GOOD pill "answer: {top} ×
       {bot} = {answer}"; bottom note spells the add-column meaning,
       e.g. "115 + 230 = 345")
    6  Verify by estimation (round each factor to the nearest 10, draw
       the rounded product under an ACCENT arrow; pill "exact A ·
       estimate B · same ballpark"; no percent-tolerance policing
       because rounding BOTH factors can widen the gap (12×14 → 10×10
       = 100 vs exact 168) — what estimation actually catches is 10×
       or 100× errors from a missing X or a dropped carry, not small
       arithmetic slips)
    7  Pitfalls (fixed reference 23 × 15 = 345, three-column ✓/✗/✗
       with ≠ glyphs: Wrong A "23 × 15 = 138" forgot the X shift
       → added 115 + 23 without shift; Wrong B "23 × 15 = 335"
       carry error in the ones row → wrote 105 instead of 115; WARN
       anchor "one X per place-shift, and carry every time the column
       product is ten or more"; bottom note flags the XX placeholder
       for 3-digit multipliers as the mult_advanced pack)
  Examples cycle 12×14=168 (small warm-up, light carries), 23×15=345
  (both partials carry), 48×27=1296 (heavier arithmetic in both
  rows), 17×36=612 (top < bottom — the method does not depend on
  order), 234×21=4914 (3-digit × 2-digit stress test — mirrors the
  handwritten reference picture; sits outside the game's 99×99 range
  on purpose so mult_advanced can open with a single refresher slide
  and extend into 3×2 / 3×3 territory without re-teaching the
  scaffold).
  Pedagogy: "multiply the ones first, write the last digit, remember
  the rest as a carry; then multiply the tens the same way and mark
  the shift with an X." Raw ints throughout. No fractions.Fraction.

- Rendering: dedicated `_mult_steps(top, bot)` returns one dict per
  digit of the bottom (ordered ones → tens → hundreds …) with
  digit_val / digit_pos / product / padded_str / carries. `padded_str`
  = str(product) + "X" × digit_pos, so the X placeholders appear as
  literal chars in the rendered row and render in DIM while real
  digits render in INK (or ACCENT when highlighted). `_draw_layout(
  canvas, cx, oy, ex, highlight_partial, show_through_partial,
  show_arc_arrows, underline_answer)` renders the full vertical block
  in Courier 16 bold monospace (COL_W=18, LINE_H=26), right-anchored
  at the ones column, with a first bar under `× bot` and a second bar
  above the double-underlined sum. Arc arrows are drawn after the
  partial loop so slide 2 (show_through_partial=-1) can display just
  the top / × bot / bar + arcs without any partial rows.

- Registered in TUTORIAL_REGISTRY (games/tutorials/__init__.py) in
  curriculum order, between the SKIP-commented mult_basic and
  div_basic. The Multiplication — Intermediate row of the Tutorials
  panel now shows a live "Open guide" card; mult_advanced stays on
  the "Guide coming soon" placeholder.

- Tutorial count bumped from 6 to 7.

- Scope expansion: the game's `mult_intermediate.py` randomly
  generates 2-dig × 1-dig, 1-dig × 2-dig, AND 2-dig × 2-dig, with
  2×2 being the method-showcase case. Per decision this pack
  prioritises 2×2 throughout — the 2×1 case collapses to "one partial
  row, no X shift" and is handled implicitly. Practical fallout: the
  `mult_advanced` ROADMAP row now needs a wider scope than the
  original "2-digit × 2-digit standard algorithm" plan — probably
  3-digit × 2-digit and the XX double-placeholder for a hundreds
  digit. Capture in ROADMAP.

- Deviation trigger: 7 slides instead of the 8-beat canon, justified
  by the TUTORIAL_CONTRACT's "more distinct steps" + "no natural
  round-trip" clauses. Multiplication has one method (stack, build
  one partial per bottom-digit with X-shift, add), no inverse
  operation, so the canon's slide 6 round-trip beat collapses into
  the slide 6 verify-by-estimation beat.

- VERSION bumped 0.7.6 → 0.7.7.
  game.py::__version__ bumped to "0.7.7".
  build.bat VERSION=0.7.7.

- Verification harness: verify_mult_intermediate.py at repo root.
  Checks per example (top × bot == answer; step count == digits of
  bot; per-step digit_val / digit_pos / product / padded_str; sum
  invariant sum(product × 10^pos) == answer) and per slide (every
  slide draws on a MockCanvas across every example without raising,
  per-slide draw counts printed for regression-diff). CONTRACT
  sanity checks TITLE length, TUTORIAL_REGISTRY length (must be 7
  after this pack), and that every slide is a callable with the
  {title, caption, draw} keys. Harness not actually executed this
  session — the workspace sandbox returned "Workspace unavailable"
  on every retry. Harness logic and every _mult_steps invariant
  traced by hand against all five examples. Run the harness on the
  next workspace-up session before cutting the exe.

- Bundled polish (same ship):
    * div_intermediate slide 5 pill overlap fix. For the 3-step
      example (738 ÷ 2 → 10 rows) the final '0' sat directly under
      the green answer pill. Layout raised to oy=52 (was 68) and top
      note shifted to y=24 (was 30) — gives ~34px clearance between
      the '0' and the pill top for the worst-case example.

- No gameplay / balance / question-pool changes. mult_intermediate.py
  game logic (MultiplicationIntermediate, PROBLEM_TYPES, pool
  generation, SRS, scoring) is untouched. Tutorials-panel "Open
  guide" card is the only entry point for now; in-game (i) button
  wiring is tracked in ROADMAP v0.7.x follow-up.

v0.7.6  (2026-04-24)
--------------------
- New tutorial pack: Division: Intermediate — short division in
  Norwegian vertical layout (dividend : divisor = quotient, subtractions
  stair-stepped underneath, quotient double-underlined).
  games/tutorials/tutorial_div_intermediate.py — 7 slides × 5 curated
  examples. Slide beats:
    1  Read the question (skeleton pill "set up the skeleton: dividend :
       divisor = quotient" + faint mini-layout showing dividend, ':',
       divisor, '=' and a dashed answer placeholder; bottom note anchors
       to notebook ritual, no longer references "Norwegian" by name)
    2  The big idea (concrete first-partial question bound to the
       cycled example — "What times {divisor} gives closest to
       {first_partial} WITHOUT going over?" + 6-row times-table strip
       of the divisor so the pupil sees the Beginner anchor)
    3  First step (left: times-table column of the divisor with the
       matching row in GOOD, over-rows in WARN, ≤/> side-labels; right:
       live _draw_layout through step 0 with the first answer digit
       highlighted; pill "first answer digit = q" — "quotient" swapped
       for "answer digit" in pupil-facing copy so the word isn't a
       new vocabulary block on top of a new method)
    4  Subtract, then drop down (full layout through step 1 with ACCENT
       highlight; dotted ACCENT "trekker-ned" arrow from the just-used
       dividend digit down into the newly-formed partial row; pill names
       the new partial and its answer digit)
    5  Finish the chain (complete layout, no highlight; GOOD pill
       "answer: {dividend} ÷ {divisor} = {quotient} (remainder 0)"; bottom
       note explains the final 0 as the exact-division tell)
    6  Verify by multiplying back (large `{q} × {d} = ?` above a GOOD
       `{q} × {d} = {dividend} ✓` with ACCENT down-arrow between them;
       pill "if the product lands back on the dividend, the quotient is
       correct"; tightened bottom note no longer repeats the caption)
    7  Pitfalls (fixed reference 252 ÷ 9 = 28, three-column ✓/✗/✗
       layout with ≠ glyphs: Wrong A = "252 ÷ 9 = 2" stopped-early,
       Wrong B = "252 ÷ 9 = 38" went-over; WARN anchor "walk every
       dividend digit, pick the largest product that doesn't go over";
       bottom note flags decimal-remainder continuation as the
       div_advanced pack)
  Examples cycle 36÷3=12 (warm-up, mirrors the handwritten picture
  that anchors the Norwegian style), 252÷9=28 (1-digit divisor with
  mid-chain carry — same numbers as slide 7 so the pitfall column
  reads as reinforcement, not a new scene), 738÷2=369 (3-digit
  quotient — intentionally outside the game's Type-A quotient range
  [11..30] as a stress-test of the method, and so div_advanced can
  open with a single refresher slide instead of re-explaining the
  whole scaffold), 156÷13=12 (first 2-digit divisor, tight estimation),
  192÷16=12 (2-digit divisor, even tighter first-digit estimation).
  All five are exact (remainder 0) to match div_intermediate.py's
  generator — the brief originally asked for a non-exact example but
  a mismatch between the tutorial and the live game would have been
  worse pedagogy than deferring remainders to div_advanced.
  Pedagogy: "short division is the Beginner times-table trick
  applied one digit at a time" — every step is the same estimate /
  subtract / drop-down ritual. Raw ints throughout, no
  fractions.Fraction (not relevant here; kept consistent with the
  rest of the pack conventions).

- Rendering: dedicated `_short_div_steps(dividend, divisor)` computes
  the (partial, quotient_digit, product, remainder, start_col, end_col)
  chain once per example. Leading dividend digits that can't
  accommodate the divisor (e.g. the "2" in 252÷9) are absorbed into
  step 0 rather than emitted as a 0-quotient no-op, matching the
  handwritten convention. `_draw_layout(canvas, ox, oy, ex,
  highlight_step, show_through_step, show_bring_down_arrow)` renders
  the full vertical block in Courier 16 bold monospace (COL_W=15,
  LINE_H=22) so digits line up column-for-column across every row.
  Tuned layout constants keep the 3-step example (738÷2, 10 rows)
  clear of slide 5's bottom pill inside the fixed 720×340 canvas.

- Registered in TUTORIAL_REGISTRY (games/tutorials/__init__.py) in
  curriculum order, between div_basic and frac_basic. The
  Division — Short Division row of the Tutorials panel now shows a
  live "Open guide" card for Intermediate; div_advanced stays on
  the "Guide coming soon" placeholder.

- Tutorial count bumped from 5 to 6. Scholar achievement threshold
  unchanged (reachable since v0.7.3).

- Deviation trigger: 7 slides instead of the 8-beat canon, justified by
  the TUTORIAL_CONTRACT's "more distinct steps" and "no natural
  round-trip" clauses — short division has one method (estimate-subtract-
  drop), no inverse operation to demo as a round-trip, so the canon's
  slide 6 "round-trip demo" beat collapses into the slide 6 verify
  beat instead.

- v0.7.6 post-ship polish (same day, pupil-review feedback from
  rendered slides):
    * Slide 1: pill reworded "write it as a Norwegian vertical: …"
      → "set up the skeleton: dividend : divisor = quotient"; bottom
      note no longer duplicates the Beginner-trick line from slide 2's
      copy; caption no longer repeats "Norwegian vertical" or the
      dividend-divisor-quotient triple now in the pill.
    * Slide 2: the big centered question template was `"What times
      {divisor} gives closest to ? WITHOUT going over?"` — the bare
      "?" looked untethered from the cycled example. Bound it to
      `_short_div_steps(...)[0]["partial"]` so the pupil reads a
      concrete first-partial (e.g. "25" when cycling 252÷9), and the
      top note now names which example the question targets.
    * Slide 3: pill and bottom note renamed "quotient digit" →
      "answer digit" for the 5th-grade reading level; internal
      identifiers (step["quotient_digit"]) deliberately unchanged —
      the jargon-swap is user-facing only.
    * Slide 6: bottom note shortened to "If it lands off, the step
      where the numbers first drift is where the bad times-table row
      lives." — removes the repetition of the caption's
      "Multiply … If not, re-check the times-table row" wording.

- VERSION bumped 0.7.5 → 0.7.6.
  game.py::__version__ bumped to "0.7.6".
  build.bat VERSION=0.7.6.

- Verification harness: verify_div_intermediate.py at repo root.
  Checks per example (dividend == divisor × quotient; step chain
  consistency: product = q×divisor, remainder = partial - product,
  assembled digits == declared quotient, col spans in range, final
  remainder == 0) and per slide (every slide draws on a MockCanvas
  across every example without raising; per-slide draw counts
  printed so a future slim-the-slides pass shows up as a divergent
  total). CONTRACT sanity checks TITLE length, TUTORIAL_REGISTRY
  length (must be 6 after this pack), and that every slide is a
  callable with the {title, caption, draw} keys. Harness not
  actually executed this session — the workspace sandbox that
  normally runs `python verify_div_intermediate.py` returned
  "Workspace unavailable" across every retry. Harness logic was
  traced by hand against all five examples. Run the harness on the
  next workspace-up session before cutting the exe.

- No gameplay / balance / question-pool changes. div_intermediate.py
  game logic (DivisionIntermediate, pool generation, SRS, scoring) is
  untouched — the tutorials panel "Open guide" card is the only
  entry point for now. In-game (i) button wiring is tracked in
  ROADMAP v0.7.x follow-up.

Doc infra  (2026-04-23)
-----------------------
- Boot-cost refactor, no gameplay / game-code behavior change.
- `VERSION` cut from 731 lines to 1 line. Historical changelog moved here.
- `NEXT_SESSION_PROMPT.md` removed (was stale, targeted already-shipped v0.7.5).
- `PROJECT_CONTEXT.md` added as the single boot doc. Holds repo map,
  conventions, current state, and a "when to read what" decision table.
- `ROADMAP.md` slimmed: repo map moved to PROJECT_CONTEXT; per-version
  "Content added in v0.7.X" prose dropped (lives in this file); post-1.0
  LK20 + parking lot extracted to `ROADMAP_POST_1.0.md`. ~460 → ~130 lines.
- `games/tutorials/TUTORIAL_CONTRACT.md` added: mechanical contract +
  shape catalog with explicit deviation triggers. Protects against
  8-slide canon-pressure on packs where the method has fewer / more
  distinct steps (mult_intermediate, div_intermediate, mult_advanced,
  div_advanced, conv_advanced).
- `slideshow_frame.py` gained two shared helpers — `draw_fraction(...)` and
  `build_slides(slide_fns, titles, captions=None)`. Existing tutorial files
  unchanged; new packs should import from slideshow_frame rather than
  duplicate locally.
- `.gitignore` added. `__pycache__` purged.
- Auto-memory `feedback_pupil_framing.md` removed — now owned by
  PROJECT_CONTEXT.md conventions section.
- `game.py::__version__` and `build.bat` VERSION unchanged at 0.7.5.

v0.7.5  (2026-04-20)
--------------------
- New tutorial pack: Conversions: Intermediate (fraction ↔ percentage,
  integer % only — the "rewrite with 100 on the bottom" method).
  games/tutorials/tutorial_conv_intermediate.py — 8 slides × 5 curated
  examples. Slide beats:
    1  Read the question (prompt + single anchor pill: "% means /100,
       that's the whole trick")
    2  Place-value anchor (10×10 hundredths grid with pct cells shaded
       for the current example; "{pct} shaded → {pct}/100 = {pct}%"
       label; one GOOD pill "% literally reads as 'out of 100'")
    3  Find the bridge — direction-dispatched. frac_to_pct: "what ×
       {frac_den} = 100?" with ×mult dashed call-out; den=10 edge-case
       note "already tens — one jump to 100". pct_to_frac: "drop the %
       → pct/100", then names the greatest common divisor of pct and
       100 in full prose (gcd abbreviation avoided in slide copy per
       v0.7.3 pupil-test rule)
    4  Apply the rewrite — direction-dispatched. frac_to_pct: {num}/
       {den} × {mult}/{mult} = {pct}/100 with ×m labels at cy±66 /
       tips cy±44 on size=30 glyphs. pct_to_frac: {pct}/100 ÷ {g}/{g}
       = {frac_num}/{frac_den} with ÷g callouts, same geometry
    5  Read off or confirm — direction-dispatched. frac_to_pct: big
       green "{pct}%" with double underline; "any fraction over 100 —
       just read the top with a % sign" pill. pct_to_frac: green check
       next to the clean-pool fraction; "lowest terms — matches the
       clean pool" pill
    6  Round-trip demo (fixed 3/4 ↔ 75%, always visible regardless of
       cycled example — two columns showing ×25 forward and ÷25
       reverse. Anchor pill: "go up with ×m to land on 100 ↔ come
       back with ÷gcd to reach the fraction")
    7  Full chain (one-line compressed render of the current example
       with per-stage labels)
    8  Pitfalls (three-column ≠ layout: ✓ 1/4 = 25% | ✗ 1/4 ≠ 14%
       "dropped the denominator" | ✗ 3/4 ≠ 34% "ignored the bottom")
  Examples cycle 3/4→75% (×25), 1/2→50% (×50), 2/5→40% (×20), 25%→1/4
  (÷25 reverse direction), 3/20→15% (×5). Four frac_to_pct examples +
  one pct_to_frac so the pupil meets the reverse direction inside the
  carousel without diluting the core method. Clean-integer tier only —
  rounded pool entries (1/3, 2/3, 1/8, 3/8) deliberately excluded
  because teaching method with a rounded pair masks the arithmetic.
  Multiplier set spans {25, 50, 20, 25, 5} — four distinct values so
  the bridge is demonstrably not always the same integer.
  Pedagogy: "a percentage is just a fraction whose bottom is always
  100 — so to convert, multiply up to 100, then read off the top."
  Raw ints throughout — fractions.Fraction deliberately not imported
  because its auto-reduction would silently collapse "75/100" into
  "3/4" and destroy the rewrite step.

- Registered in TUTORIAL_REGISTRY (games/tutorials/__init__.py) in
  curriculum order, after conv_basic. The Conversions — Fractions ↔
  Percentages row of the Tutorials panel now shows live "Open guide"
  cards for both Beginner and Intermediate; conv_advanced stays on
  the "Guide coming soon" placeholder.

- Tutorial count bumped from 4 to 5. Scholar achievement (read three
  different tutorials, 100 pts) threshold is unchanged — already
  reachable since v0.7.3, now has a fifth path.

- No gameplay / balance / question-pool changes. conv_intermediate
  game logic (ConvIntermediate, _PAIRS, _alternate_expected,
  FractionBase) is untouched — the tutorials panel's "Open guide"
  card is the only entry for now. The in-game (i) entry point will be
  wired in a later version when the tutorial-from-game flow is added.

- build.bat VERSION line is pinned to 0.7.3 on disk (read-only mount
  blocked the edit again this session, as in v0.7.4). Update manually
  to 0.7.5 before running a build, or the exe filename will still say
  v0.7.3.

- Polish pass (same day, post-ship pupil-review):
    * Rebalanced examples 4/1 → 3/2 (frac_to_pct / pct_to_frac). The 4/1
      skew left the pupil meeting the reverse direction only once;
      3/2 keeps the core method dominant without making pct_to_frac
      feel token. New cycle: 3/4→75%, 1/2→50%, 2/5→40%, 1/4↔25%,
      3/20→15%.
    * Slide 1 in-canvas bottom note shortened — the previous wording
      duplicated the Tk-caption line above the canvas.
    * Slide 2 redrawn — grid shrunk 200→170 px and moved up (grid_y
      70→60) so the green pill no longer collides with the bottom
      muted note. Pill reworded to "% names how many of the 100
      squares are shaded"; bottom note to "The % sign is just shorthand
      for 'out of 100'." — both plainer for a Norwegian 5th grader.
    * Slides 3 / 4 / 5 captions — the two "Going to a …" sentences are
      now split onto separate lines (\n inside the caption string) so
      the Tk Label wraps the directional branches cleanly instead of
      running them together.
    * Slide 6 anchor pill simplified: "go up with ×m to land on 100 ↔
      come back with ÷gcd to reach the fraction" → "multiply up to 100
      · divide back to the fraction". Removes the ×m / ÷gcd jargon and
      matches the level of a 5th grader.
    * verify_conv_intermediate.py direction-balance assertion relaxed
      from strict 4/1 to "≥2 of each direction" to match the new mix.
      All 51 checks still green; per-slide draw totals now
      56/545/72/110/68/105/95/150 = 1201.
    * Second slide-2 pass (same day, screenshot review): removed the
      top draw_note "A percentage counts pieces out of 100." at y=36.
      Its baseline was brushing the grid label at y=46 ("hundredths
      grid — 100 equal squares") and it duplicated the slide caption.
      Layout is otherwise unchanged; per-slide total for slide 2
      drops from 545 → 540 draws.

v0.7.4  (2026-04-19)
--------------------
- New tutorial pack: Conversions: Beginner (fraction ↔ decimal for clean
  denominators 2, 4, 5, 8, 10 — the "rewrite as tenths / hundredths /
  thousandths" method).
  games/tutorials/tutorial_conv_basic.py — 8 slides × 5 curated examples.
  Slide beats:
    1  Read the question (prompt pill: "a decimal is a fraction with 10,
       100, or 1000 on the bottom — that's the whole trick")
    2  Place-value anchor (tenths bar with 1/10 shaded + hundredths 10×10
       grid with 7/100 shaded; spell-out pedagogy "1 digit = tenths,
       2 digits = hundredths, 3 digits = thousandths")
    3  Find the bridge — direction-dispatched. frac_to_dec: "what × den
       lands on 10 / 100 / 1000?" with ×mult dashed call-out. dec_to_frac:
       "count the digits after the point → that picks the denominator".
       Special-case: when mult=1 (the 3/10 example) the slide says
       "already tenths, skip the bridge"
    4  Apply the rewrite — direction-dispatched. frac_to_dec: equation
       num/den × mult/mult = target_num/target_den with ×m labels at
       cy±66 / tips cy±44 on size=30 glyphs. dec_to_frac: dec_str →
       target_num/target_den with labels at cy±72 / tips cy±48 on
       size=34 glyph
    5  Read / simplify — direction-dispatched. frac_to_dec: double
       underline under the result decimal. dec_to_frac: ÷g / ÷g callouts
       reducing target to frac_num/frac_den at cy±70 / cy±46 (size=32),
       with gcd=1 fallback branch kept for future-proofing
    6  Round-trip demo (fixed 3/4 ↔ 0.75, always visible regardless of
       cycled example — two columns showing ×25 forward and ÷25 reverse.
       Anchor pill: "multiply up to a power of ten ↔ divide by the
       greatest common divisor")
    7  Full chain (one-line compressed render of the current example
       with per-stage labels)
    8  Pitfalls (three-column ≠ layout: ✓ 3/8=0.375 | ✗ 3/8≠0.38 "can't
       just copy the digits" | ✗ 1/4≠0.4 "4 is the piece count, not the
       decimal place")
  Examples cycle 3/4↔0.75 (×25), 1/2→0.5 (×5), 3/8→0.375 (×125), 0.4→2/5
  (÷2 reverse direction), 3/10→0.3 (mult=1 edge case). Four frac_to_dec
  examples + one dec_to_frac so the pupil meets the reverse direction
  inside the carousel without diluting the core method.
  Pedagogy: "a decimal is just a fraction whose bottom is already 10,
  100, or 1000 — so to convert, multiply top and bottom up to one of
  those denominators, then read off the digits."
  Raw ints throughout — fractions.Fraction deliberately not imported
  because its auto-reduction would hide the rewrite step.

- Registered in TUTORIAL_REGISTRY (games/tutorials/__init__.py) in
  curriculum order, after frac_intermediate. The Conversions —
  Fractions ↔ Decimals row of the Tutorials panel now shows a live
  "Open guide" card for Beginner; conv_intermediate and conv_advanced
  stay on the "Guide coming soon" placeholder.

- Tutorial count bumped from 3 to 4. Scholar achievement (read three
  different tutorials, 100 pts) remains reachable — threshold was
  already achievable in v0.7.3 and now has an extra path.

- No gameplay / balance / question-pool changes. conv_basic game logic
  (ConvBasic class, _PAIRS pool, FractionBase) is untouched — the
  tutorials panel's "Open guide" card is the only entry for now; the
  in-game (i) entry point will be wired in a later version when the
  tutorial-from-game flow is added.

- build.bat VERSION line is pinned to 0.7.3 on disk (read-only mount
  blocked the edit this session). Update manually to 0.7.4 before
  running a build, or the exe filename will still say v0.7.3.

v0.7.3  (2026-04-18)
--------------------
- New tutorial pack: Fractions: Intermediate (add/subtract with different
  denominators — the LCM / common-denominator case).
  games/tutorials/tutorial_frac_intermediate.py — 8 slides × 5 curated
  examples. Slide beats:
    1  Read the question (highlight the mismatched bottoms with a ≠)
    2  Pieces don't match (two same-length bars cut into a_den vs b_den)
    3  Find the LCM (walk multiples of each bottom; ring the first hit)
    4  Rewrite the LEFT fraction (×m top AND bottom, accent callouts)
    5  Rewrite the RIGHT fraction (×n top AND bottom, same trick)
    6  Now it's Beginner (same-denom add/subtract, numerator arrows down)
    7  Reduce if possible (conditional per example: show ÷gcd step when
       the result reduces, otherwise "gcd=1, already lowest" with a
       fixed 2/6 → 1/3 mini demo so the technique is still visible)
    8  Pitfall (fixed 2/3 + 1/4: ≠ 3/7 added bottoms, ≠ 3/12 forgot to
       rewrite the tops — three-column ≠ layout)
  Examples cycle 2/3+1/4, 1/2+1/3, 3/4−1/3, 2/5+1/2, 5/6−1/2 (the last
  is the reducer: 2/6 → 1/3, so the pupil meets the ÷gcd step inside
  the carousel). Raw ints throughout — fractions.Fraction was
  deliberately avoided because its auto-reduction on construction
  would turn "8/12" into "2/3" and hide the whole rewrite step.
  Method pedagogy: "you can't count thirds and quarters together —
  cut both into the same piece size (LCM) first; that reduces the
  problem to the Beginner case."

- Registered in TUTORIAL_REGISTRY (games/tutorials/__init__.py) in
  curriculum order, after frac_basic. The Fractions — Operations row
  of the Tutorials panel now shows live "Open guide" cards for both
  Beginner and Intermediate; frac_advanced stays on the "Guide coming
  soon" placeholder.

- Scholar achievement un-hidden (games/achievements.py). The hidden
  "Read three different tutorials" threshold (100 pts) was
  unreachable with only div_basic and frac_basic shipped. v0.7.3
  brings the live tutorial count to 3, so the threshold is now
  achievable and the achievement becomes visible in the Trophy Room.

- No gameplay / balance / question-pool changes. frac_intermediate
  game logic, DENOM_PAIRS, FractionBase, and the in-game (i) entry
  point are all untouched — the tutorials panel's "Open guide" card
  is the only entry for now.

- Polish pass from first-run pupil test:
    Slide 1 (frac_intermediate): dropped the redundant below-fraction
    denominator labels and stray ≠ that duplicated the already
    WARN-coloured denominators in the equation. Replaced with a single
    amber pill "the bottoms: a ≠ b" under the equation so the mismatch
    is named once, cleanly.
    Slides 4, 5, 7 (×m and ÷g callouts): the top/bottom accent labels
    with inward-pointing arrows had arrow endpoints (cy±18 / cy±20)
    that landed *inside* the numerator / denominator glyphs — the
    arrowhead visibly pierced through the digits. Fix: pushed labels
    out to cy±66 (slides 4/5, size=30 glyphs) and cy±70 (slide 7,
    size=32 glyphs), with arrow tips stopping at cy±44 / cy±46 — 10 px
    clear of the glyph edges in every case. Reduced-answer underline
    on slide 7 also nudged down (cy+52 instead of cy+44) so it sits
    below the size=34 glyph bottom rather than cutting through it.
    Slide 7 copy: "gcd(x, y) = k" → "greatest common divisor = k" in
    the pill (both branches). Pedagogical readability for 5th graders
    who haven't met the abbreviation.
    slideshow_frame.TUTORIAL_MIN_W bumped 1200 → 1280. The first-cut
    intermediate title ("Fractions: Intermediate — adding and
    subtracting with different denominators", 76 chars at 26-pt bold)
    ran ~1140 px and clipped on both ends at the previous 1200 floor.
    Fixed at source by shortening the title to "Fractions:
    Intermediate — unlike denominators" (45 chars, shorter than
    frac_basic's); the minsize bump leaves room for one slightly
    fatter future title without another re-ship. Only edit to
    slideshow_frame.py this release; draw helpers untouched.

- Note: update build.bat manually — change set VERSION=0.7.2 to
  set VERSION=0.7.3

v0.7.2  (2026-04-18)
--------------------
- New tutorial pack: Fractions: Beginner (same-denominator add/subtract).
  games/tutorials/tutorial_frac_basic.py — 8 slides × 5 curated examples.
  Slide beats:
    1  Read the question (numerator / denominator labelled)
    2  Same piece size (highlight denominators; "both are fifths")
    3  Combine the tops (arrows from the two numerators; only the
       numerators combine, operator-agnostic)
    4  Keep the bottom (curved arrow showing the denominator stays)
    5  Answer (result double-underlined)
    6  See it in pieces (bar model of d segments; shade / cross off)
    7  Subtraction mirror (fixed 4/7 − 1/7 = 3/7 — method is identical)
    8  The pitfall (fixed 2/5 + 1/5 ≠ 3/10 with one-line explanation)
  Examples cycle 2/5+1/5, 3/8+4/8, 5/9−2/9, 1/6+4/6, 6/11−3/11; results
  stay in raw unreduced form to match how frac_basic.py renders them.
  Method pedagogy: denominator is the piece size (unit), numerator is
  the count — "2 fifths + 1 fifth = 3 fifths", like counting apples.
- Registered in TUTORIAL_REGISTRY (games/tutorials/__init__.py) in
  curriculum order, after div_basic and before the frac_intermediate /
  frac_advanced TODOs. The Fractions — Operations row of the Tutorials
  panel now shows a live "Open guide" card for Beginner; the other two
  stay on the "Guide coming soon" placeholder.

- New "Learning" achievement category (4 entries, new when="tutorial"
  trigger — fires immediately from the tutorials panel / slideshow
  rather than from session end, so the pupil gets the popup the moment
  they earn it):
    Bookworm           📖 +25   Open your first tutorial guide.
    Full Walkthrough   🎓 +50   Read a tutorial all the way to the last slide.
    Curious Mind       🔍 +20   Use the "Next example" button inside a tutorial.
    Scholar            🧠 +100  Read three different tutorials. (Hidden)
  CATEGORY_ORDER updated to slot "Learning" between "Practice" and
  "Exploration".

- New achievement stats in AchievementsStore:
    tutorials_viewed        : list[str]  — unique game_ids opened
    tutorials_finished      : list[str]  — unique game_ids read to last slide
    tutorial_example_cycled : bool       — "Next example" has been used once
  Store API extended with three idempotent recorders:
    record_tutorial_viewed(game_id)
    record_tutorial_finished(game_id)
    mark_tutorial_example_cycled()

- Slideshow wiring:
    games/tutorials/slideshow_frame.py now accepts optional ach_store
    and game_id kwargs. When supplied it reports completion-of-last-slide
    and first-example-cycle back into the store, then fires
    award_tutorial_achievements() to popup any newly earned ones.
    Module-level award_tutorial_achievements(parent, ach_store) and
    _show_achievement_popup(parent, ach, slot) are a local copy of the
    toast helper in base_game — kept self-contained so the tutorial
    code path never has to reach into BaseGame.
    games/tutorials/tutorials_panel.py passes ach_store + game_id
    through on _launch_tutorial and records the "opened" event with
    an immediate achievement check.

- No gameplay / balance / question-pool changes. frac_basic game
  logic and frac_base parser untouched.

- Polish pass from first-run pupil test:
    Tutorial window now enforces a 1200x720 minsize while mounted —
    below that the 26-pt bold TITLE (e.g. "Fractions: Beginner —
    adding and subtracting with the same denominator") clipped out
    of the header. SlideshowFrame captures the prior minsize on
    mount and restores it on back, so the main menu can shrink
    again after the pupil exits. New constants TUTORIAL_MIN_W /
    TUTORIAL_MIN_H at the top of slideshow_frame.py control the
    floor; if div_basic or a future pack needs more room, bump
    them in one place.
    Slide 1 (frac_basic): removed the redundant bottom in-canvas
    note. On narrow windows it competed with the Tk caption
    underneath and visibly misaligned (centered vs. left-anchored
    rendering). Arrow-labelled "numerator / denominator" callouts
    on the left fraction carry the teaching now; caption carries
    the summary.
    Slide 2 (frac_basic): re-centered the denominator highlight
    rings on the digit itself. The oval had been floating ~8 px
    below the glyph; new y-range cy+4 to cy+40 wraps the digit
    cleanly. Pill "both pieces are N-ths" unchanged in position.
    Slide 6 (frac_basic): added an explicit 22-pt bold
    "a/d op b/d = res/d" expression below the bar — connects the
    coloured segments in the bar model to the fraction arithmetic
    the pupil has to perform in the game. Story-text caption moved
    down to keep the same overall slide footprint.

- Polish pass 2 from second-run pupil test (arrow aim + pitfall
  clutter):
    Slide 3 (frac_basic): the working line used to be a single
    centred "{a}  {op}  {b}  =  {res}" string, and the arrows from
    the two numerators were aimed at sum_x ± 34 — an estimate that
    missed because a 5-token centred string puts `b` at sum_x and
    `a` roughly at sum_x-68 (not ± 34). Arrows visibly landed on
    the "+" and the "=" glyphs instead of on the digits. Fix: split
    the line into 5 individually-placed text items at known x
    positions (x_a, x_op, x_b, x_eq, x_res) spaced by tok_gap=34,
    then aim draw_arrow at x_a and x_b directly. Endpoint y moved
    from sum_y-4 (inside the glyph) to sum_y-14 (just above the
    top of the 22-pt cap height) so the arrowhead touches the
    digit rather than overlapping it. Verified across all 5
    cycled examples (headline 2/5+1/5 and the subtraction case
    6/11-3/11 both clean).
    Slide 8 (frac_basic): the pitfall slide had three stacked text
    blocks saying the same thing — a verbose in-canvas body box
    ("Adding the bottoms would turn fifths into tenths..."), a
    warn line ("Keep the denominator. Always."), and the Tk
    caption underneath carrying a third phrasing. Removed the
    body box and its supporting rectangle + bbox-probe machinery;
    the Tk caption already carries the longer reasoning. Added a
    40-pt bold ≠ between the Correct and Wrong columns so the
    contrast is carried *visually* rather than requiring two
    paragraphs of prose. Pulled the two columns slightly further
    apart (left_cx = w/2-170, right_cx = w/2+170; gap 48) to give
    the ≠ room to breathe, and re-spaced the five items within
    each column symmetrically around its centre. Replaced the
    redundant warn line with a single amber take-home pill:
    "The piece size never changes — so the bottom never changes."
    Final warn "Keep the denominator. Always." kept at the very
    bottom as the one-sentence mnemonic.

- Note: update build.bat manually — change set VERSION=0.7.1 to
  set VERSION=0.7.2

v0.7.1  (2026-04-18)
--------------------
- Bugfix: Conversions: Intermediate wrongly rejected literal readings of
  rounded-percent prompts. "Convert 38% to fraction" accepted only 3/8
  and rejected 38/100 (= 19/50); "Convert 33% to fraction" accepted 1/3
  only. Same class of bug affected every rounded pair in the pool
  (1/3↔33, 2/3↔67, 1/8↔13, 3/8↔38) and both directions (to_pct and
  to_fraction). Root cause: _answers_match only compared against the
  exact Fraction stored in the pool, so the literal reading of the
  *displayed* (rounded) percentage failed the equality check.
- Bugfix: Conversions: Advanced same issue in the "pct_to_dec" direction
  — "Convert 38% to decimal" rejected 0.38 because expected was 3/8 =
  0.375 (diff 0.005, outside 0.0011 tolerance). 0.375 is still accepted;
  0.38 now passes too.
- frac_base.py: new _alternate_expected() hook — subclasses return an
  iterable of Fractions that are also acceptable answers. Tested
  against the active ANSWER_FORMAT like the primary expected. Default
  returns (), so games without rounded pairs (frac_*, conv_basic) are
  unchanged.
- conv_intermediate.py: overrides _alternate_expected to return the
  literal pct/100 Fraction when the pool pair is a rounded one. Active
  for both to_pct and to_fraction directions (both involve the
  percentage side).
- conv_advanced.py: overrides _alternate_expected only when the
  direction string contains "pct" (source or target is a percentage).
  frac_to_dec and dec_to_frac stay strict — the student has exact data
  on those directions and must give an exact answer.

- frac_basic (Fractions: Beginner) same-denominator display bug fixed.
  The card promised "same denominator" but the game regularly rendered
  questions like "1/3 − 1/6" because Fraction(2, 6) auto-simplifies to
  Fraction(1, 3) and the old _fmt_frac printed the simplified form.
  Raw ints are now stored (self._a_num, self._b_num, self._denom) and
  used for display; the Fraction type is still used for computation
  and for the answer check. Visible effect: questions now always read
  "a/d ± b/d = ?" with a common denominator on both sides.

- Fractions: Advanced rewrite. Aleks's note: "numbers not only between
  1 and 10 — i was thinking 3/13 + 9/19, fractions like this". The
  previous revamp (bigger mixed numbers) was the wrong direction;
  Advanced is now:
    Proper fractions only. No mixed numbers, no improper display.
    DENOMS pool [5, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
    — mix of primes (7, 11, 13, 17, 19) and composites.
    Pair rule inverted from Intermediate: neither denominator may
    divide the other. Forces a real LCM step (multiply denominators
    or find a non-trivial LCM like 18 for 6+9), not just scaling one
    operand to match the other. This is the pedagogical distinction
    from Intermediate (which uses multiple-of pairs).
    Numerators sample 1..denom-1 so on denom 13 a student can hit
    12/13 — numerators naturally break past 10.
    Raw numerator/denominator preserved on display (4/12 stays "4/12",
    not Fraction-simplified to "1/3") so the LCD task stays visible.
    Results allowed to exceed 1 (answer accepted in improper, mixed, or
    reduced form — FractionBase parser handles all three).
    Subtitle: "Add and subtract fractions with unrelated denominators."
    Hint: "find a common denominator first — any equivalent answer
    works."
    Menu card: "Like 3/13 + 9/19 = 174/247."

- Menu card descriptions brought back in line with the rewrite:
    Fractions: Beginner — "Like 2/5 + 1/5 = 3/5." (previously 1/3+1/3,
      unrepresentative of the expanded denominator pool)
    Fractions: Advanced — "Unrelated denominators. Like 3/13 + 9/19 =
      174/247." (previously 1 1/2 + 2 1/4, the wrong pedagogical
      target entirely)
- Bugfix: Tutorials panel mis-labelled genuine TODOs as "No guide
  needed · This mode is about recall speed, so there's nothing to
  walk through." That copy was written for mult_basic only but
  fired for every game missing from TUTORIAL_REGISTRY — including
  Division: Intermediate (short division) and Division: Advanced
  (long division), which emphatically ARE concepts worth walking
  through. Fix: split the placeholder into two distinct states:
    INTENTIONAL_NO_GUIDE (new set in games/tutorials/__init__.py):
      currently just {"mult_basic"}. Renders the existing
      "No guide needed · recall speed" card.
    Everything else missing from TUTORIAL_REGISTRY:
      renders a new amber "Guide coming soon" card with copy
      "A step-by-step walkthrough for this mode is in the works.
      Play the game in the meantime."
  tutorials_panel._render_categories now routes each gid to
  _tutorial_card / _not_needed_card / _coming_soon_card based on
  this three-way classification. Existing test_tutorials_mock.py
  still passes; div_basic tutorial behaviour unchanged.

- No DB / persistence schema changes. No new files. Tutorial system
  slideshow framework (v0.7.0) untouched.

- Verified by test_fraction_fixes.py (sandbox unit test at
  /sessions/loving-wonderful-fermat/). Covers all three bug cases for
  conv games, confirms strict directions stay strict, exercises 400
  frac_basic questions for same-denom display invariant, and exercises
  600 frac_advanced questions confirming numerators/denoms push past 10
  and both improper/mixed forms appear. 15/15 passed.

- Note: update build.bat manually — change set VERSION=0.7.0 to
  set VERSION=0.7.1

v0.7.0  (2026-04-17)
--------------------
- Tutorial Slideshow system (the "(i) button" feature, per roadmap) — shipped
  as framework + first tutorial pack. Accessed via a new "Tutorials" card on
  the main menu (third card in the Review row, sibling of Progress & Stats
  and Practice Missed). The in-game (i) launcher on each game screen is
  deferred to a later 0.7.x — this release ships the browser entry only.

- New package games/tutorials/ with:
    __init__.py
        TUTORIAL_REGISTRY: dict[str, module] — game_id -> content module.
        Adding a new tutorial is one line here + one new content file.
        Helpers: get_tutorial(gid), has_tutorial(gid).
    slideshow_frame.py
        Reusable SlideshowFrame widget. Pure tkinter Canvas (720x340) with
        prev/next nav, keyboard arrows, and "Next example" cycling through
        curated worked problems. Palette mirrors stats_screen.py.
        Exports drawing helpers that content modules build on:
            draw_centered_expression(canvas, text, y, size, color, bold, w)
            draw_note(canvas, text, y, w, color, size)
            draw_arrow(canvas, x1, y1, x2, y2, color, width, dash)
            draw_pill(canvas, cx, cy, text, bg, fg, pad, size, bold)
    tutorials_panel.py
        Full-page grid of tutorial cards, grouped by curriculum category
        (Multiplication / Division / Fractions — Operations / Fractions —
        Conversions). Cards render as Guide / Locked / "No guide needed"
        based on TUTORIAL_REGISTRY membership and UNLOCK_REQUIREMENTS.
    tutorial_div_basic.py
        First content pack. 4 slides x 3 examples:
            1 — The big idea (division undoes multiplication)
            2 — Flip the question (rewrite a/b as "? x b = a")
            3 — Use the times table (walk divisor's row until match)
            4 — Verify (multiply back to confirm)

- Content-module contract (for future tutorial packs):
    Each tutorial_<game_id>.py must export four names:
        TITLE    : str           shown in slideshow header (English)
        LEAD     : str           one-liner subtitle
        SLIDES   : list[dict]    each dict {title, caption, draw}
                                  draw(canvas, example, w, h) -> None
        EXAMPLES : list[dict]    tutorial-defined shape. The "Next example"
                                  button cycles through these and re-runs
                                  the current slide's draw with the new
                                  example. Arithmetic packs use
                                  {"a": int, "b": int, "ans": int}.
    All copy is English (in-game UI language). Norwegian lives only in
    the parent PDF report.

- Design rules baked in:
    mult_basic intentionally has NO tutorial (rote memorisation — nothing
    to walk through). The panel renders a "No guide needed" placeholder
    so the grid stays even.
    Tutorial lock state mirrors UNLOCK_REQUIREMENTS from achievements.py —
    never show a guide for content the pupil can't yet play.
    Canvas size is fixed at 720x340 (CANVAS_W, CANVAS_H in slideshow_frame).
    Anything past x=720 clips. Measure-then-draw for any pill or strip
    that holds variable-length text (see Slide 4 tip box for the pattern).

- Main menu wiring:
    game.py line 32: `from games.tutorials.tutorials_panel import TutorialsPanel`
    game.py line 33: `from games.tutorials import TUTORIAL_REGISTRY`
    "Open Tutorials" card sits at row=0, column=2 in the Review row, next
    to Practice Missed (col 0) and Progress & Stats (col 1).
    Entry point: App._launch_tutorials — mounts TutorialsPanel in a fresh
    Frame under root, back_callback=self.show_menu.

- Bugfix: Tk 9 / Python 3.14 compatibility. Widget-level pady= must be a
  single integer; passing a tuple now raises TclError "bad screen distance".
  Fixed in slideshow_frame.py line 117 by moving the asymmetric padding
  from the Frame constructor onto the subsequent .pack() call (pack/grid
  DO accept tuples). Hardened SlideshowFrame.__init__ to pre-declare widget
  attrs as None and _render_current to no-op when they are — so a partial
  build fails loudly in the right place rather than surfacing a misleading
  AttributeError from a later button click.

- Bugfix: Slide 3 content overflow. The "match — answer is X" label sat at
  x=660 on a 720px canvas; "match —" showed, rest clipped. Shortened to
  just "match!" at x=col_x[2]+155 with a shorter arrow. The green-highlighted
  row already carries the pedagogy.

- Bugfix: Slide 4 Tip box lopsided. The 600px fixed-width pill had ~180px
  of empty space on the right. Replaced with a measure-then-draw approach
  (canvas.bbox on hidden probe text), so the pill now wraps tightly around
  "Tip + body" and centres on the canvas. Reusable pattern for future packs.

- Bugfix: latent v0.6.0 regression surfaced. The frac_* and conv_* game
  classes override __init__ and did not accept/forward sessions_store, so
  launching any of the six crashed with TypeError: unexpected keyword
  argument 'sessions_store'. (mult_* and div_* don't override __init__, so
  they inherit BaseGame's signature and were unaffected — that's why only
  Fractions / Conversions were broken.) Added `sessions_store=None` to each
  of the six subclass __init__ signatures and forwarded it in the super()
  call. v0.6.0 only exercised mult/div in QA, so nobody hit this until
  the latest Fractions session was opened post-v0.7.0 build.

- Note: update build.bat manually — change set VERSION=0.6.1 to set VERSION=0.7.0

v0.6.1  (2026-04-17)
--------------------
- Bugfix: mousewheel scrolling on the main menu stopped working after
  returning from a subscreen (Practice Missed, Progress & Stats). Root
  cause: subscreens called canvas.bind_all("<MouseWheel>", ...), which is
  application-wide and replaced the menu's own handler with one whose
  captured canvas was destroyed on return. Fix: App._install_wheel_handler
  centralises the root wheel binding, and show_menu re-installs it each
  time the menu is rendered. Mousewheel now works anywhere over the menu
  body again, not just directly over the scrollbar.
- PDF parent report reworked into a 3-page professional report in Norwegian:
    Page 1 (Oppsummering):
        Header, 4 summary tiles, 14-day bar chart,
        auto-generated narrative paragraph ("Vurdering"),
        next-focus recommendation strip
    Page 2 (Detaljert oversikt):
        Per-tier breakdown (Nybegynner / Mellomnivå / Viderekommen)
        Difficulty distribution bar (share of attempts per tier, stacked)
        Per-game summary table: økter, riktige, forsøk, snitt, best rekke, sist
    Page 3 (Kompetansemål, LK20 5. trinn):
        Each relevant LK20 competence goal with a colored status dot
        (Mestret / Under utvikling / Ikke startet / Ikke påbegynt i appen)
        Verbatim Norwegian goal text from Udir, Norwegian note per goal
        One-line summary footnote
- New module games/curriculum.py:
    GOALS_5_TRINN list (8 relevant LK20 goals; spreadsheet + programming
    goals intentionally out of scope for this math-drill product)
    Each goal declares its covering game_ids and threshold tier;
    adding a new game family later = editing one list
    goal_status(), summary_counts(), strongest/weakest helpers
- pdf_export.py rewrite:
    Multi-page _Doc / _Page writer with proper xref bookkeeping
    cp1252 / WinAnsiEncoding — native æ, ø, å rendering
    Typographic Unicode normalisation (em-dash, curly quotes) on write
    Helvetica character-width table for word-wrap + right-alignment
    Expansion-ready: appendix pages can be added via doc.new_page()
- Page-footer contract: "Side X av 3" kept as a constant so future appendix
  pages don't invalidate the displayed total on the three main pages
- Report filename unchanged (progress_<profile>_<YYYY-MM-DD>.pdf)
- Note: update build.bat manually — change set VERSION=0.6.0 to set VERSION=0.6.1

v0.6.0  (2026-04-17)
--------------------
- Added Progress & Stats screen — accessible from the main menu per profile:
    Summary tiles: total correct, days played, best streak, total practice time
    14-day questions-per-day bar chart (Canvas-drawn, attempts + correct stacked)
    Per-game accuracy trend sparklines (one per game mode with data)
    Per-game summary table: sessions, correct, attempts, avg accuracy, best streak, last played
    Recent achievements highlight strip
- New sessions.json per-profile log — every completed session is recorded:
    Fields: date, ts, game_id, correct, attempts, accuracy, streak, minutes
    Committed at end of every session via base_game._commit_and_check
- New games/sessions_store.py (SessionsStore class) with aggregation helpers:
    daily_counts(days), per_game_summary(), accuracy_series(game_id, limit),
    total_minutes(), first_session_date()
- PDF export — one-page A4 parent-friendly progress report:
    Zero-dependency pure-Python PDF writer (games/pdf_export.py)
    Title + profile + date, summary tiles, bar chart, per-game table, recent achievements
    File → Save-As dialog, default filename: progress_<profile>_<YYYY-MM-DD>.pdf
- New "Progress & Stats" card on the main menu, next to Practice Missed
- profile_manager.load_stores now returns a 4-tuple including the SessionsStore
- base_game.BaseGame.__init__ accepts an optional sessions_store kwarg
- Roadmap updated: v0.7 (Stats) promoted to v0.6.0, v0.6 (Tutorial) deferred to v0.7.0
- Note: update build.bat manually — change set VERSION=0.5.2 to set VERSION=0.6.0

v0.5.2  (2026-04-16)
--------------------
- Layout refactor: question area now expands to fill available vertical space
    Question box (q_area) takes all remaining height above the controls
    Controls (entry, buttons, feedback, scratch pad) stay compact at the bottom
    Eliminates dead space between buttons and scratch pad
- Scratch pad is now fixed height (5 lines) in the compact controls zone
- Right stats panel widened from 290px to 310px — reduces label crowding
- Avatar assets organised into thematic category folders under assets/avatars/:
    Scholar_Arcane (24), Hero_Honour (20), Nature_Spirit (20),
    Shadow_Stealth (16), Wild_Fierce (8), Dark_Arts (8), Craftsman (4)
    Borders (11 ornate frames), Item_Frames (16 UI frames)
    Female avatars removed from working set (retained in source pack for later)
- Roadmap v0.8.0 updated with full avatar system design and asset inventory

v0.5.1  (2026-04-16)
--------------------
- Added scratch pad to all game screens
    Text area below the answer buttons for partial calculations and working notes
    Monospace font (Courier 12) on off-white background for a paper-like feel
    "Clear" button to wipe it between questions
    Persists within a session but is not saved — purely a working surface
    Lives in base_game.py so all game modes inherit it automatically

v0.5.0  (2026-04-16)
--------------------
- Added Fractions — Operations category (3 tiers):
    Beginner:      same-denominator addition/subtraction (denominators 2–10)
    Intermediate:  different denominators (one a multiple of the other)
    Advanced:      mixed numbers addition/subtraction
- Added Fractions — Conversions category (3 tiers):
    Beginner:      fraction ↔ decimal (clean denominators: 2, 4, 5, 8, 10)
    Intermediate:  fraction ↔ percentage (integer %)
    Advanced:      all three directions (fraction/decimal/percentage)
- New frac_base.py: FractionBase class with fraction-aware input parsing
    Accepts "3/4", "1 3/4" (mixed number), "0.75", "75" in single text entry
    Uses Python fractions.Fraction for exact equivalence checking
    ANSWER_FORMAT instance variable controls expected answer type per question
- 6 new game IDs added to achievements.py with full Sharp/Precise/Flawless suite
- 3 new cross-game achievements: Fraction Fan, Common Ground, Converter
- Unlock requirements: each Intermediate/Advanced tier locked behind Sharp in previous
- Note: update build.bat manually — change set VERSION=0.4.1 to set VERSION=0.5.0

v0.4.1  (2026-04-13)
--------------------
- Added Settings screen (⚙ button on profile screen and in game menu)
- Working settings:
    Auto-login — skip profile screen, load last profile automatically on startup
    Start maximized — open window fullscreen every time
- Coming-soon placeholders visible but disabled: Dark mode, Sound effects, Language
- Settings persisted globally to %APPDATA%\MathPractice\settings.json (not per-profile)
- Note: update build.bat manually — change set VERSION=0.3.1 to set VERSION=0.4.1

v0.4.0  (2026-04-13)
--------------------
- Added user profile system — multiple players on one install
- New profile selection screen on launch (create, load, delete profiles)
- Each profile has isolated save data in %APPDATA%\MathPractice\profiles\{name}\
  (achievements, leaderboard scores, missed questions all separate per profile)
- Active profile shown in game menu header with one-click profile switching
- Refactored all three stores (AchievementsStore, MissedStore, ScoresStore)
  to be path-aware — no more hardcoded global paths
- Added profile_manager.py for profile CRUD and store instantiation
- Copyright footer also shown on the profile selection screen

v0.3.1  (2026-04-13)
--------------------
- Copyright notice added to all source files
- Copyright footer added to main menu (version + © Aleksander Lie)

v0.3.0  (2026-04-13)
--------------------
- Added full achievement system with 49 achievements across 6 categories
- Achievement points displayed in menu header (star icon)
- Trophy Room panel — scrollable list of all achievements, earned/locked state
- Intermediate and Advanced games locked behind achievement prerequisites
  (Multiplication: Beginner's "Sharp" unlocks Intermediate, etc.)
- Locked game cards show which achievement is required to unlock them
- Toast popup notifications when achievements are earned mid-session or on exit
- Staggered popup queue so multiple achievements don't overlap
- Achievement data persisted to %APPDATA%\MathPractice\achievements.json
- Fixed: menu mousewheel scroll now works anywhere on the menu, not just the scrollbar
- Fixed: locked card popup triggers on the full card including the gray unlock box
- Fixed: locked card message now shows full game context ("Sharp in Multiplication: Beginner")
- Fixed: Practice Missed "All Cleared" state now shows a message and auto-returns to menu

v0.2.0  (2026-04-13)
--------------------
- Added Division: Beginner, Intermediate, Advanced game modes
- Added Practice Missed — review queue for all previously wrong answers
- Missed questions persisted to %APPDATA%\MathPractice\missed.json
- Leaderboard per game, persisted to %APPDATA%\MathPractice\scores.json
- Score entry prompt with name input after each session
- Base game architecture (BaseGame) shared across all game modes
- Progress bar, streak counter, accuracy display during play

v0.1.0  (2026-04-13)
--------------------
- Initial build
- Multiplication: Beginner, Intermediate, Advanced game modes
- Timed question sessions with configurable length
- Correct / incorrect feedback per answer
- Basic leaderboard (in-memory)
- Main menu with game selection cards