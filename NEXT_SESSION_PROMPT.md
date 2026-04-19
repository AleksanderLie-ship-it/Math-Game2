# Next-session prompt — Build the conv_basic tutorial pack (v0.7.4)

> Paste the block between the `---` fences into a fresh Claude session. Everything below it is reference for *you*, Aleks — not the agent.

---

You are continuing work on **Math Practice**, a Windows Tk/PyInstaller game for Norwegian 5th graders (LK20). Current version on disk is **v0.7.3**. Your task this session is to ship the **conv_basic tutorial pack** (Conversions: Beginner — fraction ↔ decimal for clean denominators) and bump to **v0.7.4**. Caveman mode: zero filler, zero meta-commentary, direct execution only. Do not ask me to confirm between steps — execute the plan, verify, and report the diffs at the end.

## Preflight — read these before touching anything

1. `/sessions/<session>/mnt/.auto-memory/MEMORY.md` (index) + each file it points to. Non-negotiable behaviours:
   - Refer to the student as **"the pupil"** — never by name. Applies to all slide copy and commentary.
   - Credits stay bavka + Magnus Landaas (not relevant this session but don't mis-attribute).
2. `/sessions/<session>/mnt/Math Game/games/tutorials/tutorial_frac_intermediate.py` — **this is your structural template** (most recent, most polished pack; use its slide shape, alignment rules, pitfall pattern). `tutorial_frac_basic.py` and `tutorial_div_basic.py` are secondary references.
3. `/sessions/<session>/mnt/Math Game/games/tutorials/slideshow_frame.py` — renderer + drawing helpers (`draw_centered_expression`, `draw_note`, `draw_arrow`, `draw_pill`) + `TUTORIAL_MIN_W`/`TUTORIAL_MIN_H` constants + colour palette (`INK MUTED DIM FAINT SOFT ACCENT ACCENT_DARK GOOD WARN BG CARD_BG CARD_BORDER`). Import colours from here; do not hardcode hex. Do NOT modify draw helpers unless absolutely necessary — the frac_intermediate polish pass already set good floor defaults.
4. `/sessions/<session>/mnt/Math Game/games/tutorials/__init__.py` — registry you'll update.
5. `/sessions/<session>/mnt/Math Game/games/conv_basic.py` — so tutorial answers match how the game renders them (decimals as strings like "0.75"; fractions as raw `a/b` from the `_PAIRS` pool; never auto-simplified in display). Note the pool: denominators 2, 4, 5, 8, 10; plus the 2/4 entry that tests simplification.
6. `/sessions/<session>/mnt/Math Game/games/frac_base.py::_fmt_frac` — how fractions are printed.
7. `/sessions/<session>/mnt/Math Game/games/achievements.py` — Scholar is already visible (tutorial count = 3, will be 4 after this). No achievement flips needed this ship, but re-confirm counts.
8. `/sessions/<session>/mnt/Math Game/VERSION` — changelog style. The v0.7.3 block is your formatting reference.
9. `/sessions/<session>/mnt/Math Game/ROADMAP.md` — priority stack + the `conv_basic` TODO row you're flipping to ✅.
10. `/sessions/<session>/mnt/Math Game/game.py` — for `__version__`.
11. `/sessions/<session>/mnt/Math Game/build.bat` — for `set VERSION=`.

## Deliverable

### 1. Create `games/tutorials/tutorial_conv_basic.py`

Structure mirrors `tutorial_frac_intermediate.py`:

```python
TITLE: str        # KEEP SHORT — ≤ 50 chars. E.g. "Conversions: Beginner — fraction ↔ decimal"
LEAD: str         # one-liner that frames the method
SLIDES: list      # ordered slide dicts with "title" + "draw" callable
EXAMPLES: list    # curated worked problems cycled by the "Next example" button
```

Copyright header: `# Copyright (c) 2026 Aleksander Lie. All rights reserved.`

### 2. Pedagogical content — the method

Core pedagogy to convey (this is how the pupil is taught):

- **A decimal IS a fraction with a power-of-ten denominator.** 0.7 = 7/10. 0.23 = 23/100. "Decimal places" name the denominator: 1 digit after the point → tenths, 2 digits → hundredths, 3 digits → thousandths.
- **Conversion = rewriting as tenths/hundredths.** For denominators 2, 4, 5, 8, 10, the goal is to find a multiplier `m` such that `den × m` lands on 10, 100, or 1000. Then multiply the top by the same `m`. Read the resulting `N/10` (or `/100`, `/1000`) straight off as a decimal.
  - 1/2 → ×5 → 5/10 → 0.5
  - 3/4 → ×25 → 75/100 → 0.75
  - 1/5 → ×2 → 2/10 → 0.2
  - 3/8 → ×125 → 375/1000 → 0.375
  - 7/10 → already tenths → 0.7
- **Reverse direction (decimal → fraction).** Count the digits after the point, that's your denominator (10 / 100 / 1000). Put the digits on top. Simplify if asked — but in this game, the game expects the *unreduced* pool form, so we show both forms and explain that `0.75 = 75/100 = 3/4`.
- **Place-value grid intuition.** A 10-square bar for tenths; a 10×10 = 100-square grid for hundredths. Shading N squares visualises `N/100`. Use this as the "why" anchor in at least one slide — it's the single best intuition for "decimal = shaded fraction of the whole".
- **Pitfall:** `1/4 ≠ 0.4` (don't just drop the denominator beside the point) and `3/8 ≠ 0.38` (the fraction bar is division, not decimal-place substitution). Show both wrongs side-by-side with the correct path.

### 3. Slide outline (target 7–8 slides)

Polish the exact copy and visuals, but cover these beats. Use `tutorial_frac_intermediate.SLIDES` as the layout template; reuse helpers from `slideshow_frame.py`.

1. **Setup** — "Convert 3/4 to a decimal" displayed cleanly, with the LEAD line underneath. Amber pill: "a decimal is a fraction with 10 / 100 / 1000 on the bottom".
2. **Place-value anchor** — draw a 10-square row (tenths) and a 10×10 grid (hundredths). Label "0.1 = 1/10" and "0.01 = 1/100". No algebra; just the picture.
3. **Find the multiplier** — for 3/4, ask: "what times 4 lands on 100?" → 25. Arc-arrow from 4 to 100 labelled ×25.
4. **Multiply the top by the same number** — ×25 on the numerator too. 3 → 75. Arc-arrow from 3 to 75 labelled ×25. Both arrows visible simultaneously. Use the same arrow-tip-10px-clear-of-glyph rule from v0.7.3 (see Gotchas).
5. **Read it off** — 75/100 → "0.75". Double underline the answer. Pill: "75 hundredths = 0.75".
6. **Reverse example** — 0.2 → ?/?. Count the digits after the point (one → tenths), put 2 on top: 2/10. Then the simplify step: ÷2 on both → 1/5. Spell out "greatest common divisor" (not gcd) — same rule as v0.7.3 frac_intermediate slide 7.
7. **Cycle the examples** — one slide that just renders the current example's full chain (fraction → multiplier → tenths/hundredths → decimal, or decimal → count digits → raw form → reduced form).
8. **Pitfall** — three-column layout (same pattern as frac_intermediate slide 8): "Correct" (3/8 = 0.375 via ×125 → 375/1000), "Wrong A" (3/8 ≠ 0.38 — "you can't copy the digits"), "Wrong B" (1/4 ≠ 0.4 — "4 is the piece count, not the decimal place"). ≠ glyphs between columns.

### 4. EXAMPLES list (5 curated)

Every example must be renderable end-to-end (multiplier path OR decimal-digit-count path). All drawn from the `conv_basic._PAIRS` pool so the tutorial matches the live game:

- `3/4 ↔ 0.75` (headline — ×25 path, hundredths)
- `1/2 ↔ 0.5` (tenths, ×5 — easy confidence win)
- `3/8 ↔ 0.375` (thousandths, ×125 — stretches the method)
- `2/5 ↔ 0.4` (tenths, ×2 — reverse-direction anchor)
- `3/10 ↔ 0.3` (already tenths — demonstrates "no multiplier needed")

For each example pre-compute: source numerator, source denominator, target power-of-ten denominator (10/100/1000), multiplier, final digits, decimal string. Store as a dict per `tutorial_frac_intermediate.EXAMPLES`.

The pack should handle BOTH directions per cycle. Pick one canonical direction per example (follow the arrow in the table above), but the slides should reference the reverse on the reverse-example slide.

### 5. Register the tutorial

In `games/tutorials/__init__.py`:

- Add `from . import tutorial_conv_basic`
- Add `"conv_basic": tutorial_conv_basic,` to `TUTORIAL_REGISTRY` in curriculum order (after `frac_intermediate`, before any remaining TODOs for conv).

### 6. Version bump

- `game.py`: `__version__ = "0.7.4"`
- `build.bat`: `set VERSION=0.7.4`

### 7. Changelog — append v0.7.4 block to `VERSION`

Cover:
- New tutorial pack: Conversions: Beginner (fraction ↔ decimal, clean denominators 2/4/5/8/10).
- Slide beats summary (the 7–8 above, compressed).
- Examples list.
- Registered in `TUTORIAL_REGISTRY`; Conversions row of the Tutorials panel now shows a live Beginner card.
- No gameplay or balance changes.
- Note: tutorial count is now 4, so Scholar remains achievable (already visible since v0.7.3).

### 8. Roadmap — update `ROADMAP.md`

- Current version → **v0.7.4**.
- `conv_basic` row in the tutorial table → ✅ done.
- Add a "Content added in v0.7.4" summary block above the v0.7.3 block in the v0.7.0 Tutorial Slideshow section. Mirror the v0.7.3 block's tone and length.
- Add `tutorial_conv_basic.py` to the repo quick map listing.

## Verification (non-negotiable)

1. **`ast.parse`** on every edited file. Do NOT use `py_compile` (known `__pycache__` race in this sandbox).
2. **MockCanvas smoke test** — copy the pattern from `/sessions/<previous-session>/verify_frac_intermediate.py`:
   - stub tkinter + tkinter.ttk
   - load `games` + `games.tutorials` via `importlib.util.spec_from_file_location`
   - resolve via `TUTORIAL_REGISTRY["conv_basic"]`
   - assert `len(SLIDES) >= 7`, `len(EXAMPLES) == 5`
   - for each example, assert your multiplier math: `source_num * mult / source_den * mult == decimal_value` (use a tolerance or convert via Fraction ONLY inside verification, never inside the tutorial rendering code)
   - render every slide × every example against a MockCanvas with the id-aware `delete()` (only clears on `"all"`; filters by id otherwise — the v0.7.3 harness had this fix)
   - assert no exceptions and `n_items > 0` per draw
3. **Registry sanity**: `has_tutorial("conv_basic")` returns True; `TUTORIAL_REGISTRY["conv_basic"]` resolves.
4. **Copy review**: re-read your own slide text once. Flag any instance where you refer to the student by name. All copy must say "the pupil" or a generic referent.
5. Report a concise diff: files touched, lines added/removed per file, final slide count, final example count.

## Gotchas (lessons burned into v0.7.2 and v0.7.3)

- **Arrow tips must sit 10px clear of glyph edges.** For size-30 fraction glyphs, numerator sits at cy−20 and den at cy+20, each ~14px tall (size × 0.65 ≈ 19.5, half is ~10, plus cap-height margin → 34 total span from cy). Arrow labels go to cy±66, arrow tips to cy±44. For size-32 glyphs: labels cy±70, tips cy±46. For size-34 glyphs (answer slides): underline at cy+52. If you use a different glyph size, scale these numbers — do NOT eyeball from prior packs; measure.
- **Spell out abbreviations in slide copy.** No "gcd", no "lcm" without context. Say "greatest common divisor" and "lowest common multiple" on any pill the pupil sees. The teacher voice is the one speaking.
- **`TUTORIAL_MIN_W` floor is 1280** as of v0.7.3. Do NOT bump it further — if a title clips at 1280, **shorten the title**. 26pt bold ≈ 15px/char, so keep TITLE ≤ 50 chars to be safe (~750px measured, plenty of margin). LEAD can be longer since it's 13pt.
- **No `Fraction` for display storage**. `Fraction(75, 100)` auto-reduces to `Fraction(3, 4)` and breaks every `75/100` slide. Use raw ints throughout; Fraction is allowed ONLY inside verification code.
- **No new `.md` docs.** VERSION + ROADMAP.md are the only narrative files you touch. Project instructions mention a `PROJECT_CONTEXT.md` — it doesn't exist in the repo. Don't create it.
- **English copy only.** Norwegian stays in the parent PDF pipeline.
- **Linux sandbox has no tkinter.** Don't try to launch the Tk frontend. Stub it for verification.
- **Widget `pady=`/`padx=` must be int, not tuple**, in Tk 9 / Python 3.14. Tuples only work on `.pack()`/`.grid()`.
- **Canvas is 720x340.** Anything reaching x>720 or y>340 clips. Use `canvas.bbox` on a hidden probe text to measure strings before drawing pills around them. Pattern: see `tutorial_frac_intermediate` slides 3/4/5.
- **MockCanvas `delete()` must be id-aware.** The v0.7.3 harness learned this the hard way — `draw_pill` calls `canvas.delete(tmp)` on a measurement probe and a naive mock wipes every item. Copy the fixed `delete()` from `verify_frac_intermediate.py`.
- **Every example is self-contained.** "Next example" cycles EXAMPLES; the slide for example N must not depend on state from example N−1.

## What NOT to do this session

- Do not start the in-game `(i)` button wiring — separate session.
- Do not start any other tutorial pack (mult_intermediate, div_intermediate, conv_intermediate, etc.).
- Do not touch `conv_basic.py` game logic — it's already correct.
- Do not modify `slideshow_frame.py` draw helpers or colour palette.
- Do not introduce animations, dark mode, or v0.8.0 work.
- Do not create any new `.md` files.

When done, end with a 3-bullet summary: (a) files touched with lines added/removed, (b) final slide count + example count + MockCanvas draw/item totals from verification, (c) any judgement calls Aleks might want to reconsider.

---

## Notes for future-me (Aleks), not the agent

- After conv_basic, the beginner tier is complete across categories (div_basic ✅ / frac_basic ✅ / conv_basic ✅; mult_basic intentional SKIP). Natural v0.7.5 targets: `mult_intermediate` or `div_intermediate`. Fractions Advanced (`frac_advanced`) also open; it's higher pedagogical value than Division Intermediate per your own priority note.
- The in-game `(i)` button is sitting in the roadmap v0.7.x follow-up section. Once all three beginner tutorials are out, that's the next natural step — it's pure wiring, not new content, and it's the feature that makes the tutorials actually discoverable mid-session.
- Screenshot test plan on Windows box after the ship: launch the Tutorials panel, open Conversions → Beginner, click Next for each example once, verify no glyph clipping, no arrow-piercing, title renders fully at min-size window. The three burns from v0.7.3 (arrow pierce, gcd abbreviation, title clip) are what to watch for.
- Current on-disk version when this prompt was written: **v0.7.3**. If you've shipped more since, update the "current version" references in the fenced block before pasting.
