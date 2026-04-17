# Next-session prompt — Build the frac_basic tutorial pack (v0.7.2)

> Paste the block between the `---` fences into a fresh Claude session. Everything below it is reference for *you*, Aleks — not the agent.

---

You are continuing work on **Math Practice**, a Windows Tk/PyInstaller game for Norwegian 5th graders (LK20). Current version on disk is **v0.7.1**. Your task this session is to ship the **frac_basic tutorial pack** and bump to **v0.7.2**. Do not start anything else. Do not ask me to confirm between steps — just execute the plan, verify, and report the diffs at the end.

## Preflight — read these before touching anything

1. `/sessions/loving-wonderful-fermat/mnt/.auto-memory/MEMORY.md` (index) and each file it points to. Key behaviours you must respect:
   - Refer to the student as **"the pupil"** — never by name. This is non-negotiable and applies to all slide copy, commentary, and commit-style notes.
   - Credits: bavka (itch.io assets) + Magnus Landaas (creative input). Not relevant this session but don't mis-attribute.
2. `/sessions/loving-wonderful-fermat/mnt/Math Game/games/tutorials/tutorial_div_basic.py` — **this is your template**. Match its shape, tone, and level of visual detail. Do not invent a new format.
3. `/sessions/loving-wonderful-fermat/mnt/Math Game/games/tutorials/slideshow_frame.py` — the renderer. Understand what shapes/primitives Slides can contain before writing any.
4. `/sessions/loving-wonderful-fermat/mnt/Math Game/games/tutorials/__init__.py` — registry you'll update.
5. `/sessions/loving-wonderful-fermat/mnt/Math Game/games/frac_basic.py` — so the tutorial matches how the game actually renders questions (raw `a/d + b/d`, no auto-simplification).
6. `/sessions/loving-wonderful-fermat/mnt/Math Game/VERSION` — changelog style.
7. `/sessions/loving-wonderful-fermat/mnt/Math Game/ROADMAP.md` — current priority stack.
8. `/sessions/loving-wonderful-fermat/mnt/Math Game/game.py` — for the `__version__` constant location.
9. `/sessions/loving-wonderful-fermat/mnt/Math Game/build.bat` — for the `VERSION` build var.

## Deliverable

### 1. Create `games/tutorials/tutorial_frac_basic.py`

Structure (mirror `tutorial_div_basic.py` exactly):

```python
TITLE: str        # "Fractions: Beginner — adding and subtracting with the same denominator"
LEAD: str         # one-liner, e.g. "When the bottoms match, just count the pieces."
SLIDES: list      # ordered Slide objects (whatever dataclass/type tutorial_div_basic uses)
EXAMPLES: list    # curated worked problems ("Next example" toggle in the panel cycles these)
```

Copyright header: `# Copyright (c) 2026 Aleksander Lie. All rights reserved.`

### 2. Pedagogical content — the method

Core pedagogy to convey (this is how the pupil should be taught):

- **Same denominator = same-size pieces.** The denominator *names the piece size*; it's a unit, like "apples" or "fifths". Same unit → you just count.
- **Procedure:** (a) check the denominators match, (b) add/subtract the **numerators only**, (c) **keep the denominator the same**.
- **Analogy to anchor the intuition:** "2 apples + 1 apple = 3 apples" → "2 fifths + 1 fifth = 3 fifths". The denominator is the noun; the numerator is the count.
- **Explicit pitfall:** 2/5 + 1/5 ≠ 3/10. Adding the bottoms would be saying "2 fifths + 1 fifth = 3 tenths" — the piece size magically shrank, which is nonsense. Call this out directly on a slide.
- Show both **addition and subtraction**; subtraction is the same idea (count down instead of up).

### 3. Slide outline (target ~6–8 slides)

Polish the exact copy, but cover these beats:

1. **Setup** — display "2/5 + 1/5 = ?" laid out clearly.
2. **Spot the match** — highlight both denominators (the 5s) and name them the "piece size".
3. **Add the tops** — arrow from 2 and 1 to a new numerator "3".
4. **Keep the bottom** — the 5 stays put. Why: the piece size didn't change.
5. **Answer** — 3/5, double underline.
6. **The "why" in pictures** — if the renderer supports it, draw a bar/pie split into fifths; shade 2, then shade 1 more, land on 3/5. If not feasible, describe it in prose.
7. **Subtraction example** — walk through 4/7 − 1/7 = 3/7 with the same structure but compressed (one slide).
8. **Pitfall** — 2/5 + 1/5 ≠ 3/10 with a one-line explanation.

### 4. EXAMPLES list

Curate ~5 worked problems that exercise the same method on varied denominators. Suggested mix:

- 2/5 + 1/5 (the headline example)
- 3/8 + 4/8
- 5/9 − 2/9
- 1/6 + 4/6
- 6/11 − 3/11

Each example should include the full step-by-step rendering — do NOT simplify the result (frac_basic preserves raw form and the tutorial should match).
When switching between examples there should be an indicator of what example number you are on.
Should also add achievments relevant to turorial, first time using a tutorial should be one and throw some others in you feel apropriate - think dopamine boost for the pupil

### 5. Register the tutorial

In `games/tutorials/__init__.py`:

- Add `from . import tutorial_frac_basic`
- Add `"frac_basic": tutorial_frac_basic,` to `TUTORIAL_REGISTRY` (in curriculum order — after `div_basic`, before the frac TODOs).
- Remove the `# "frac_basic": tutorial_frac_basic, # to come` comment line.

### 6. Version bump

- `game.py`: `__version__ = "0.7.2"`
- `build.bat`: `set VERSION=0.7.2`

### 7. Changelog — append to `VERSION`

A v0.7.2 entry covering:
- New tutorial pack: Fractions: Beginner (same-denominator add/subtract).
- Registered in `TUTORIAL_REGISTRY`; the Fractions row of the Tutorials panel now shows a live card for Beginner.
- No gameplay or balance changes.

### 8. Roadmap — update `ROADMAP.md`

Tick off the frac_basic tutorial item. If there's a "Tutorial content packs" checklist, mark that row done. Version label to v0.7.2 wherever the file references the current version.

## Verification (non-negotiable, do all of these)

1. **Parse-only syntax check** on every file you edited — use `python3 -c "import ast; ast.parse(open('PATH').read())"`. Do NOT use `py_compile` (it has had cache-race issues in this repo's sandbox).
2. **Smoke-import** the new module: import it in a tiny script and assert `TITLE`, `LEAD`, `SLIDES`, `EXAMPLES` are all present and non-empty, and that `len(SLIDES) >= 6`. You will need a **tkinter stub** if the module transitively imports Tk — use the stub pattern from `/sessions/loving-wonderful-fermat/test_fraction_fixes.py` (function `_install_tk_stub`).
3. **Registry sanity**: after editing `__init__.py`, import `TUTORIAL_REGISTRY` and assert `"frac_basic" in TUTORIAL_REGISTRY` and that `has_tutorial("frac_basic")` returns True.
4. **Copy review**: re-read your own slide text in one pass. Flag any instance where you refer to the student by a name (Phillip, or any other). All copy uses "the pupil" or a generic referent.
5. Show me a concise diff summary at the end — files changed, lines added/removed per file, and the final slide count.

## Gotchas (things that burned prior sessions)

- The Linux sandbox has no tkinter. Never try to launch the Tk frontend. Stub it if the import chain requires it.
- `py_compile` has raced on `__pycache__` write; prefer `ast.parse` for parse-only validation.
- Do NOT use `Fraction` for display storage — it auto-simplifies and breaks unreduced rendering. If you render example numbers as strings, build them from raw ints exactly like `frac_basic.py` does.
- The "Next example" toggle in `slideshow_frame.SlideshowFrame` cycles EXAMPLES — make sure every example is completely self-contained (it should replace the previous one, not depend on state from it).
- English copy only. Norwegian copy is only in the parent-facing PDF (which is a separate pipeline).

## What NOT to do this session

- Do not start the in-game (i) button wiring — that's a separate session.
- Do not start any other tutorial pack (conv_basic, mult_intermediate, etc.).
- Do not touch the frac_basic *game* logic — it is already correct as of v0.7.1.
- Do not introduce dark mode, cosmetics, or v0.8.0 work.
- Do not create any new docs beyond VERSION/ROADMAP edits.

When you're done, end with a 3-bullet summary: (a) files touched, (b) final slide count and example count, (c) any judgment calls you made that I might want to reconsider.

---

## Notes for future-me (Aleks), not the agent

- If you want to swap the "next move" for the in-game (i) button instead, scrap the section above and write a different prompt — but don't mix both in the same session; the scope gets fuzzy and the tutorial's slide polish suffers.
- Current on-disk version when this prompt was written: **v0.7.1**. If you've shipped more since, bump the target accordingly.
- Prompt author's confidence in the plan landing cleanly in one session: **0.85**. Main risk: slide rendering primitives in `slideshow_frame` may not support pie/bar visuals, in which case slide 6 degrades to prose — still fine.
