# Tutorial pack contract + shape catalog

Read this before writing a new `tutorial_<game_id>.py` module. Two parts:

1. **Mechanical contract** — the plumbing every pack MUST satisfy. Non-negotiable.
2. **Shape catalog** — descriptive pattern the fraction/conversion family converged on. Not a rule. Deviate when the topic calls for it; the triggers are listed below.

---

## 1. Mechanical contract

### Module surface

Every `tutorial_<game_id>.py` exports these four names:

```python
TITLE:    str          # short. ≤ 50 chars ideally, never > TUTORIAL_MIN_W / ~10
LEAD:     str          # one-line method framing under the title
SLIDES:   list[dict]   # [{"title": str, "caption": str, "draw": callable}, ...]
EXAMPLES: list[dict]   # curated problems cycled by "Next example"
```

Each `SLIDES[i]["draw"]` is `(canvas, example, w, h) -> None`. `example` is one entry from `EXAMPLES`; the draw fn reads whatever fields it needs.

Copyright header: `# Copyright (c) 2026 Aleksander Lie. All rights reserved.`

### Registration

Add one line to `games/tutorials/__init__.py::TUTORIAL_REGISTRY`:

```python
"<game_id>": dict(
    title = tutorial_<game_id>.TITLE,
    lead  = tutorial_<game_id>.LEAD,
    slides    = tutorial_<game_id>.SLIDES,
    examples  = tutorial_<game_id>.EXAMPLES,
),
```

`tutorials_panel.py` auto-picks up the registry — no panel edits needed. If the new `game_id` belongs to a new game family, also append it to the right list in `tutorials_panel._CATEGORIES`.

### Canvas + clipping

Canvas is a fixed **720 × 340**. Anything reaching `x > 720` or `y > 340` WILL clip. Use `canvas.bbox` on a hidden probe text to measure strings before drawing pills / strips around them — see the Slide 4 Tip box in `tutorial_div_basic._slide_4` for the measure-then-draw pattern.

### Palette

Import colours from `slideshow_frame.py`:

```python
from .slideshow_frame import (
    INK, MUTED, DIM, FAINT, SOFT,
    ACCENT, ACCENT_DARK, GOOD, WARN,
    BG, CARD_BG, CARD_BORDER,
)
```

Do NOT hardcode hex. The palette mirrors `stats_screen.py` for visual consistency; if you add a new colour, add it to `slideshow_frame.py` first.

### Shared drawing helpers

Available from `slideshow_frame.py` — prefer these over redefining in the tutorial module:

- `draw_centered_expression(canvas, text, y, size=36, color=INK, bold=True, w=CANVAS_W)` — big centered math expression.
- `draw_note(canvas, text, y, ...)` — muted subtitle line.
- `draw_arrow(canvas, x1, y1, x2, y2, color=ACCENT, width=2, dash=None)` — labelled arrow.
- `draw_pill(canvas, cx, cy, text, bg=SOFT, fg=INK, pad=10, size=13, bold=True)` — pill-shaped label with auto-measured width.
- `draw_fraction(canvas, cx, cy, num_text, den_text, num_color=INK, den_color=INK, size=30)` — stacked `num / den` with bar; returns `(num_y, den_y)` for caller layout. **Use this instead of defining `_draw_fraction` locally.**
- `build_slides(slide_fns, titles, captions=None)` — assemble `SLIDES` from parallel arrays. Reduces the repetitive `[dict(title=..., draw=_slide_N), ...]` block to one call.

### Tk 9 widget quirks

`pady=` and `padx=` on widget *constructors* (`tk.Frame`, `tk.Label`, `tk.Button`) must be a single `int` in Tk 9 / Python 3.14. Tuples are only valid on `.pack(pady=…)` and `.grid(pady=…)`. Fix the caller, not the widget.

### Raw ints only

**Do NOT import `fractions.Fraction`** inside a tutorial module. Its auto-reduction on construction silently collapses `75/100` into `3/4` and `8/12` into `2/3`, destroying the rewrite step the slides are teaching. Use it only inside the verification harness if convenient.

### EXAMPLES invariants

Assert every example in a verification harness. Typical invariants, by family:

- **Addition / combination:** `a_num * lcm_mult + b_num * lcm_mult == result_num`, denominators agree after rewrite.
- **Conversion (frac ↔ pct):** `frac_den * mult == 100`, `frac_num * mult == pct`, `gcd(pct, 100) == gcd_reverse`, `pct // gcd_reverse == frac_num`, `100 // gcd_reverse == frac_den`.
- **Conversion (frac ↔ dec):** `frac_den * mult in {10, 100, 1000}`.

Every example carries a `direction` field when the pack teaches both directions (e.g. `"frac_to_pct"` / `"pct_to_frac"`). Slides that need to branch check this field.

### Achievement hooks

`SlideshowFrame` will call `ach_store.record_tutorial_finished(game_id)` when the pupil reaches the last slide, and `ach_store.mark_tutorial_example_cycled()` when they hit "Next example" once. Toast popups fire automatically. The tutorial module itself does not need to touch achievements.

### Verification harness

`test_tutorials_mock.py` at repo root runs every slide × every example against a `MockCanvas` without needing Tk. Run it after adding a pack. Tk-dependent interactive test is `test_tutorials.py` — requires a DISPLAY, skipped in sandbox.

---

## 2. Shape catalog — descriptive, not prescriptive

The fraction/conversion family (frac_basic, frac_intermediate, conv_basic, conv_intermediate) converged on this 8-beat skeleton through pupil testing. It is an earned pattern for those topics — not a rule for all topics.

### The 8-beat pattern (fraction / conversion family)

| # | Beat                 | Purpose                                                                                    |
|---|----------------------|--------------------------------------------------------------------------------------------|
| 1 | Read the question    | Frame the prompt. Anchor pill naming the method in one line.                               |
| 2 | Place-value anchor   | A visual that grounds the abstraction (10×10 grid, bar model, fraction strip).             |
| 3 | Find the bridge      | Identify the step that converts the problem to a simpler form (LCM, ×mult to 100).         |
| 4 | Apply the rewrite    | Execute the step. Show the ×m / ÷g callouts with arrows.                                   |
| 5 | Read off / confirm   | Extract the answer from the rewritten form. Double underline on final answer.              |
| 6 | Round-trip demo      | Fixed (non-cycling) example showing both directions. Reinforces reversibility.             |
| 7 | Full chain           | Compressed one-line render of the current example with per-stage labels.                   |
| 8 | Pitfall              | Three-column `✓ / ✗ / ✗` layout showing two canonical wrong answers and *why* they're wrong.|

### Direction-dispatch convention

For packs teaching both directions (e.g. frac_to_pct and pct_to_frac), slides 3/4/5/7 branch on `example["direction"]`. Slide 6's round-trip is always a fixed example so the pupil sees both directions regardless of which direction is currently cycled.

### Callout geometry

For ×m / ÷g accent callouts on rewrite slides, endpoints landing inside glyphs was a v0.7.3 regression. The fix:

- Labels at `cy ± 66` (size=30 glyphs) or `cy ± 70` (size=32).
- Arrow tips stop at `cy ± 44` / `cy ± 46` — roughly 10 px clear of glyph edges.
- Reduced-answer underlines sit at `cy + 52` (size=34 glyph), not `cy + 44`.

### Copy rules (5th-grade Norwegian pupil)

- Avoid abbreviations like "gcd" — write "greatest common divisor" in full.
- Split directional branch sentences onto separate lines in Tk caption strings (`\n`) so the Label wraps cleanly.
- One anchor pill per slide, not stacked.
- If a pill and a bottom note are saying the same thing, kill the pill.

### When to deviate

Do NOT force 8 slides if the topic has a different natural shape. Deviate when any of these apply:

- **Fewer genuinely distinct steps.** Partial products (`mult_intermediate`) is read → break digits → two multiplications → add → pitfall = ~5 slides. Forcing 8 pads the method.
- **More distinct steps.** Long division / 2-digit × 2-digit standard algorithm legitimately has more stages (alignment, carry, bring-down). 9–11 slides is fine.
- **Two parallel lanes rather than linear.** `conv_advanced` covers three inter-convertible forms; a two-column layout ("same number shown three ways") may beat a linear carousel.
- **No natural round-trip.** If the method isn't obviously reversible, skip beat 6 rather than fake it.
- **No natural pitfall.** If there's no canonical wrong answer pupils reach for, skip beat 8 rather than invent one.

What MUST stay canon regardless of shape: the mechanical contract (section 1 above), the palette, the helper usage, the 720×340 canvas discipline, the raw-ints rule, and the clipping / callout geometry.

### Pack-to-pack consistency

Pupils recognise the shape from previous packs — for packs in the same family (fraction operations, conversions), stay close to the 8-beat pattern unless a deviation trigger fires. For packs in a new family (mult / div / mixed numbers), optimise for the topic first; cross-family consistency is not load-bearing.
