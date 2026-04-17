"""
pdf_export.py
-------------
Parent-facing progress report. 3-page A4 PDF in Norwegian.

Page 1 — Oppsummering
    Title, profile, date. Four summary tiles. 14-day bar chart.
    Auto-generated narrative paragraph. One-line recommendation.

Page 2 — Detaljert oversikt
    Per-tier breakdown (Nybegynner / Mellomnivå / Viderekommen).
    Per-game summary table. Difficulty distribution bar.

Page 3 — Kompetansemål (LK20, 5. trinn)
    Each relevant competence goal with a status dot
    (Mestret / Under utvikling / Ikke startet / Ikke påbegynt i appen)
    and the original Norwegian curriculum text.

Design notes
------------
* Zero runtime dependencies (no reportlab). Ships with a stock Python install
  and PyInstaller bundle.
* Uses Helvetica + Helvetica-Bold with WinAnsiEncoding, which covers all
  Norwegian letters including æ, ø, å.
* Multi-page: add pages via Doc.new_page(). The writer handles xref/offset
  bookkeeping so the structure stays valid regardless of page count.
* Expansion hook: add an optional appendix page (detailed session log) by
  calling doc.new_page() after page 3 and drawing on it. All page helpers
  accept a Page/Doc pair.
"""
# Copyright (c) 2026 Aleksander Lie. All rights reserved.

import datetime

from .achievements import ACHIEVEMENTS_BY_ID, GAME_IDS, GAME_NAMES
from . import curriculum


# ── Page geometry ──────────────────────────────────────────────────────────────

PAGE_W  = 595.0   # A4 width  (210 mm)
PAGE_H  = 842.0   # A4 height (297 mm)
MARGIN  = 42.0    # outer margin


# ── Palette ────────────────────────────────────────────────────────────────────

C_INK    = (0.06, 0.09, 0.16)   # #0f172a
C_MUTED  = (0.39, 0.45, 0.55)   # #64748b
C_DIM    = (0.58, 0.64, 0.72)   # #94a3b8
C_FAINT  = (0.80, 0.84, 0.88)   # #cbd5e1
C_SOFT   = (0.95, 0.96, 0.98)   # #f1f5f9
C_BORDER = (0.89, 0.91, 0.94)   # #e2e8f0
C_GREEN  = (0.08, 0.50, 0.24)   # #15803d
C_AMBER  = (0.96, 0.62, 0.04)   # #f59e0b
C_WHITE  = (1.00, 1.00, 1.00)
C_ACCENT = (0.31, 0.27, 0.90)   # #4f46e5 indigo


# ══════════════════════════════════════════════════════════════════════════════
# Low-level PDF primitives
# ══════════════════════════════════════════════════════════════════════════════

class _Page:
    """Accumulates PDF content-stream operators for a single page."""

    def __init__(self):
        self._ops: list[str] = []

    # ── text ─────────────────────────────────────────────────────────────

    def text(self, x, y, s, size=10, bold=False, color=C_INK):
        font = "F2" if bold else "F1"
        r, g, b = color
        self._ops.append("BT")
        self._ops.append(f"/{font} {size} Tf")
        self._ops.append(f"{r:.3f} {g:.3f} {b:.3f} rg")
        self._ops.append(f"1 0 0 1 {x:.2f} {y:.2f} Tm")
        self._ops.append(f"({_escape(s)}) Tj")
        self._ops.append("ET")

    def text_wrapped(self, x, y, s, size=10, bold=False, color=C_INK,
                     max_width=400, line_gap=2):
        """Simple greedy word-wrap. Returns the y-coordinate of the line BELOW
        the last rendered line (so the caller can flow subsequent content)."""
        line_h = size + line_gap
        words  = s.split()
        line   = ""
        cur_y  = y
        for w in words:
            trial = (line + " " + w).strip()
            if _text_width(trial, size, bold) <= max_width:
                line = trial
            else:
                if line:
                    self.text(x, cur_y, line, size=size, bold=bold, color=color)
                    cur_y -= line_h
                line = w
        if line:
            self.text(x, cur_y, line, size=size, bold=bold, color=color)
            cur_y -= line_h
        return cur_y

    # ── shapes ───────────────────────────────────────────────────────────

    def rect_fill(self, x, y, w, h, color=C_INK):
        r, g, b = color
        self._ops.append(f"{r:.3f} {g:.3f} {b:.3f} rg")
        self._ops.append(f"{x:.2f} {y:.2f} {w:.2f} {h:.2f} re f")

    def rect_stroke(self, x, y, w, h, color=C_BORDER, width=0.5):
        r, g, b = color
        self._ops.append(f"{r:.3f} {g:.3f} {b:.3f} RG")
        self._ops.append(f"{width} w")
        self._ops.append(f"{x:.2f} {y:.2f} {w:.2f} {h:.2f} re S")

    def line(self, x1, y1, x2, y2, color=C_BORDER, width=0.5):
        r, g, b = color
        self._ops.append(f"{r:.3f} {g:.3f} {b:.3f} RG")
        self._ops.append(f"{width} w")
        self._ops.append(f"{x1:.2f} {y1:.2f} m")
        self._ops.append(f"{x2:.2f} {y2:.2f} l S")

    def circle_fill(self, cx, cy, r, color=C_INK):
        """Filled circle via 4 Bezier segments (magic constant 0.5523)."""
        k  = 0.5523 * r
        rr, g, b = color
        self._ops.append(f"{rr:.3f} {g:.3f} {b:.3f} rg")
        self._ops.append(f"{cx - r:.2f} {cy:.2f} m")
        self._ops.append(f"{cx - r:.2f} {cy + k:.2f} "
                         f"{cx - k:.2f} {cy + r:.2f} "
                         f"{cx:.2f} {cy + r:.2f} c")
        self._ops.append(f"{cx + k:.2f} {cy + r:.2f} "
                         f"{cx + r:.2f} {cy + k:.2f} "
                         f"{cx + r:.2f} {cy:.2f} c")
        self._ops.append(f"{cx + r:.2f} {cy - k:.2f} "
                         f"{cx + k:.2f} {cy - r:.2f} "
                         f"{cx:.2f} {cy - r:.2f} c")
        self._ops.append(f"{cx - k:.2f} {cy - r:.2f} "
                         f"{cx - r:.2f} {cy - k:.2f} "
                         f"{cx - r:.2f} {cy:.2f} c")
        self._ops.append("f")

    def bytes(self) -> bytes:
        return "\n".join(self._ops).encode("latin-1", errors="replace")


class _Doc:
    """Collects pages and emits the final PDF bytes."""

    def __init__(self):
        self.pages: list[_Page] = []

    def new_page(self) -> _Page:
        p = _Page()
        self.pages.append(p)
        return p

    def write(self, path: str):
        _write_pdf(path, self.pages)


# ── Helvetica Type-1 character widths (em units, 1000/em) ─────────────────────
#
# Source: built-in Type-1 Adobe Font Metrics. Used for word-wrap and simple
# right-alignment calculations. We hard-code a small subset — ASCII + Latin-1
# letters used in Norwegian plus a few punctuation marks — enough for our
# needs. Missing characters fall back to an average width.

_HELVETICA_WIDTHS = {
    " ": 278, "!": 278, "\"": 355, "#": 556, "$": 556, "%": 889, "&": 667,
    "'": 191, "(": 333, ")": 333, "*": 389, "+": 584, ",": 278, "-": 333,
    ".": 278, "/": 278, ":": 278, ";": 278, "<": 584, "=": 584, ">": 584,
    "?": 556, "@": 1015,
    "A": 667, "B": 667, "C": 722, "D": 722, "E": 667, "F": 611, "G": 778,
    "H": 722, "I": 278, "J": 500, "K": 667, "L": 556, "M": 833, "N": 722,
    "O": 778, "P": 667, "Q": 778, "R": 722, "S": 667, "T": 611, "U": 722,
    "V": 667, "W": 944, "X": 667, "Y": 667, "Z": 611,
    "[": 278, "\\": 278, "]": 278, "^": 469, "_": 556, "`": 333,
    "a": 556, "b": 556, "c": 500, "d": 556, "e": 556, "f": 278, "g": 556,
    "h": 556, "i": 222, "j": 222, "k": 500, "l": 222, "m": 833, "n": 556,
    "o": 556, "p": 556, "q": 556, "r": 333, "s": 500, "t": 278, "u": 556,
    "v": 500, "w": 722, "x": 500, "y": 500, "z": 500,
    "{": 334, "|": 260, "}": 334, "~": 584,
    # Latin-1 / Norwegian
    "æ": 889, "Æ": 1000, "ø": 611, "Ø": 778, "å": 556, "Å": 667,
    "é": 556, "è": 556, "ê": 556, "ë": 556, "í": 278, "ó": 556, "ú": 556,
    "ñ": 556, "ü": 556, "ö": 556, "ä": 556, "ç": 500,
    "·": 278, "%": 889,
}
_HELVETICA_BOLD_WIDTHS = {
    # Helvetica-Bold is slightly wider for lowercase; use a uniform +8% bump
    c: int(w * 1.06) for c, w in _HELVETICA_WIDTHS.items()
}
_AVG_WIDTH = 500   # fallback


def _text_width(s: str, size: float, bold: bool = False) -> float:
    """Rough text width in points."""
    table = _HELVETICA_BOLD_WIDTHS if bold else _HELVETICA_WIDTHS
    em = sum(table.get(c, _AVG_WIDTH) for c in s)
    return em * size / 1000.0


def _escape(s: str) -> str:
    """Escape a string for the PDF (...) literal.
    Normalises typographic Unicode to ASCII, then encodes to cp1252 (WinAnsi).
    """
    replacements = {
        "\u2014": "-",   # em-dash  —
        "\u2013": "-",   # en-dash  –
        "\u2212": "-",   # minus    −
        "\u2018": "'",   # left single quote
        "\u2019": "'",   # right single quote
        "\u201C": '"',
        "\u201D": '"',
        "\u2026": "...",
        "\u00A0": " ",
    }
    s = "".join(replacements.get(c, c) for c in s)
    out = []
    for ch in s:
        if ch in ("(", ")", "\\"):
            out.append("\\" + ch)
            continue
        try:
            b = ch.encode("cp1252")[0]
        except (UnicodeEncodeError, UnicodeDecodeError):
            out.append("?")
            continue
        if 32 <= b < 127:
            out.append(ch)
        elif b >= 128:
            out.append(f"\\{b:03o}")
        else:
            out.append("?")
    return "".join(out)


# ── Writer ─────────────────────────────────────────────────────────────────────

def _write_pdf(path: str, pages: list[_Page]):
    """Write a multi-page PDF from a list of _Page objects."""
    # We know the object layout up front:
    #   1   Catalog
    #   2   Pages (parent)
    #   3   Font F1   (Helvetica)
    #   4   Font F2   (Helvetica-Bold)
    #   5,6 Page1 object + Content1 stream
    #   7,8 Page2 object + Content2 stream
    #   ... etc.
    font1_id  = 3
    font2_id  = 4

    # Build object bodies
    objects: list[bytes] = []

    catalog_obj = b"<< /Type /Catalog /Pages 2 0 R >>"
    objects.append(catalog_obj)

    # Placeholder — filled in after we know page object ids
    objects.append(b"")   # will replace at index 1 (Pages)

    objects.append(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica "
                   b"/Encoding /WinAnsiEncoding >>")
    objects.append(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold "
                   b"/Encoding /WinAnsiEncoding >>")

    page_obj_ids: list[int] = []
    for page in pages:
        content_bytes = page.bytes()
        content_obj = (f"<< /Length {len(content_bytes)} >>\nstream\n"
                       .encode("latin-1")
                       + content_bytes
                       + b"\nendstream")
        # Reserve content first, then page object that references it
        content_id = len(objects) + 1
        objects.append(content_obj)

        page_id = len(objects) + 1
        page_obj = (
            f"<< /Type /Page /Parent 2 0 R "
            f"/MediaBox [0 0 {PAGE_W:.0f} {PAGE_H:.0f}] "
            f"/Resources << /Font << /F1 {font1_id} 0 R /F2 {font2_id} 0 R >> >> "
            f"/Contents {content_id} 0 R >>"
        ).encode("latin-1")
        objects.append(page_obj)
        page_obj_ids.append(page_id)

    # Fill in the Pages parent object now that we know its Kids
    kids = " ".join(f"{i} 0 R" for i in page_obj_ids)
    pages_obj = (f"<< /Type /Pages /Count {len(page_obj_ids)} "
                 f"/Kids [{kids}] >>").encode("latin-1")
    objects[1] = pages_obj

    # Write to disk
    with open(path, "wb") as f:
        f.write(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")

        offsets = [0]   # obj 0 free
        for i, obj in enumerate(objects, start=1):
            offsets.append(f.tell())
            f.write(f"{i} 0 obj\n".encode("latin-1"))
            f.write(obj)
            f.write(b"\nendobj\n")

        xref_pos = f.tell()
        f.write(f"xref\n0 {len(objects) + 1}\n".encode("latin-1"))
        f.write(b"0000000000 65535 f \n")
        for off in offsets[1:]:
            f.write(f"{off:010d} 00000 n \n".encode("latin-1"))

        f.write(b"trailer\n")
        f.write(f"<< /Size {len(objects) + 1} /Root 1 0 R >>\n"
                .encode("latin-1"))
        f.write(f"startxref\n{xref_pos}\n%%EOF\n".encode("latin-1"))


# ══════════════════════════════════════════════════════════════════════════════
# Report builder
# ══════════════════════════════════════════════════════════════════════════════

# Tier grouping used on page 2
TIER_ORDER    = ["basic", "intermediate", "advanced"]
TIER_LABEL_NO = {
    "basic":        "Nybegynner",
    "intermediate": "Mellomnivå",
    "advanced":     "Viderekommen",
}

# Human-readable Norwegian game names for the parent-facing report
GAME_NAMES_NO = {
    "mult_basic":        "Multiplikasjon — nybegynner",
    "mult_intermediate": "Multiplikasjon — mellomnivå",
    "mult_advanced":     "Multiplikasjon — viderekommen",
    "div_basic":         "Divisjon — nybegynner",
    "div_intermediate":  "Divisjon — mellomnivå",
    "div_advanced":      "Divisjon — viderekommen",
    "frac_basic":        "Brøk — nybegynner",
    "frac_intermediate": "Brøk — mellomnivå",
    "frac_advanced":     "Brøk — viderekommen",
    "conv_basic":        "Omgjøring — nybegynner",
    "conv_intermediate": "Omgjøring — mellomnivå",
    "conv_advanced":     "Omgjøring — viderekommen",
}

# Short Norwegian name used in narrative
GAME_SHORT_NO = {
    "mult_basic":        "multiplikasjon (nybegynner)",
    "mult_intermediate": "multiplikasjon (mellomnivå)",
    "mult_advanced":     "multiplikasjon (viderekommen)",
    "div_basic":         "divisjon (nybegynner)",
    "div_intermediate":  "divisjon (mellomnivå)",
    "div_advanced":      "divisjon (viderekommen)",
    "frac_basic":        "brøkregning (nybegynner)",
    "frac_intermediate": "brøkregning (mellomnivå)",
    "frac_advanced":     "brøkregning (viderekommen)",
    "conv_basic":        "omgjøring mellom brøk og desimaltall",
    "conv_intermediate": "omgjøring mellom brøk og prosent",
    "conv_advanced":     "omgjøring mellom brøk, desimaltall og prosent",
}


def _game_tier(gid: str) -> str:
    for tier in TIER_ORDER:
        if gid.endswith("_" + tier):
            return tier
    return "basic"


# ── Public entry point ────────────────────────────────────────────────────────

def export_progress_report(path: str, profile_name: str,
                           ach_store, sessions_store):
    """Render and write the 3-page Norwegian progress report to `path`."""
    doc = _Doc()

    total_pages = 3   # page numbering in footers — kept as a constant so
                      # future appendix pages can be added without breaking
                      # the displayed total on pages 1-3

    _draw_page_1_summary(doc.new_page(), profile_name, ach_store, sessions_store,
                         page_num=1, total_pages=total_pages)
    _draw_page_2_details(doc.new_page(), profile_name, ach_store, sessions_store,
                         page_num=2, total_pages=total_pages)
    _draw_page_3_curriculum(doc.new_page(), profile_name, ach_store, sessions_store,
                            page_num=3, total_pages=total_pages)

    doc.write(path)


# ── Page 1: Oppsummering ──────────────────────────────────────────────────────

def _draw_page_1_summary(page, profile_name, ach_store, sessions_store,
                         page_num, total_pages):
    left  = MARGIN
    right = PAGE_W - MARGIN
    y     = PAGE_H - MARGIN

    # ── Header ───────────────────────────────────────────────────────────
    page.text(left, y - 6, "Math Practice  —  Fremgangsrapport",
              size=20, bold=True, color=C_INK)
    y -= 28
    page.text(left, y,
              f"Profil: {profile_name}     Generert: {datetime.date.today().isoformat()}",
              size=10, color=C_MUTED)
    y -= 10
    page.line(left, y, right, y, color=C_BORDER, width=0.6)
    y -= 22

    # ── Summary tiles ────────────────────────────────────────────────────
    stats         = ach_store.get_stats()
    total_correct = stats.get("total_correct", 0)
    days_played   = len(stats.get("days_played", []))
    best_streak   = stats.get("best_streak_ever", 0)
    total_min     = sessions_store.total_minutes() if sessions_store else 0.0

    tiles = [
        ("Riktige totalt",  f"{total_correct:,}".replace(",", " ")),
        ("Dager \u00f8vd",  f"{days_played}"),
        ("Beste rekke",     f"{best_streak}"),
        ("\u00d8vingstid",  _fmt_minutes_no(total_min)),
    ]
    tile_h   = 64
    tile_gap = 10
    tile_w   = (right - left - tile_gap * 3) / 4
    for i, (label, value) in enumerate(tiles):
        x = left + i * (tile_w + tile_gap)
        page.rect_stroke(x, y - tile_h, tile_w, tile_h,
                         color=C_BORDER, width=0.6)
        page.text(x + 10, y - 16, label, size=8, color=C_MUTED)
        page.text(x + 10, y - tile_h + 12, value,
                  size=20, bold=True, color=C_INK)
    y -= tile_h + 24

    # ── 14-day bar chart ─────────────────────────────────────────────────
    page.text(left, y, "Oppgaver per dag — siste 14 dager",
              size=12, bold=True, color=C_INK)
    y -= 12
    page.text(left, y, "Grønn = riktige svar.  Grå = totalt antall forsøk.",
              size=9, color=C_MUTED)
    y -= 10

    chart_h    = 130
    plot_left  = left + 26
    plot_right = right - 8
    plot_w     = plot_right - plot_left
    chart_top  = y - 8
    chart_base = chart_top - chart_h

    daily = sessions_store.daily_counts(14) if sessions_store else []
    _draw_bar_chart(page, daily, plot_left, chart_base, plot_w, chart_h)
    y = chart_base - 24

    # ── Narrative paragraph ──────────────────────────────────────────────
    page.text(left, y, "Vurdering", size=12, bold=True, color=C_INK)
    y -= 14
    narrative = _build_narrative(profile_name, ach_store, sessions_store)
    y = page.text_wrapped(left, y, narrative,
                          size=10, color=C_INK,
                          max_width=right - left, line_gap=3)
    y -= 10

    # ── Recommendation strip ─────────────────────────────────────────────
    rec_title, rec_body = _build_recommendation(profile_name, sessions_store)
    if rec_title:
        strip_h = 46
        page.rect_fill(left, y - strip_h, right - left, strip_h, color=C_SOFT)
        page.rect_stroke(left, y - strip_h, right - left, strip_h,
                         color=C_BORDER, width=0.4)
        page.text(left + 12, y - 16, rec_title,
                  size=10, bold=True, color=C_INK)
        page.text_wrapped(left + 12, y - 30, rec_body,
                          size=9, color=C_MUTED,
                          max_width=right - left - 24, line_gap=2)

    _draw_footer(page, page_num, total_pages)


# ── Page 2: Detaljert oversikt ────────────────────────────────────────────────

def _draw_page_2_details(page, profile_name, ach_store, sessions_store,
                         page_num, total_pages):
    left  = MARGIN
    right = PAGE_W - MARGIN
    y     = PAGE_H - MARGIN

    page.text(left, y - 6, "Detaljert oversikt",
              size=20, bold=True, color=C_INK)
    y -= 28
    page.text(left, y,
              "Fordeling etter vanskelighetsgrad og spill.",
              size=10, color=C_MUTED)
    y -= 10
    page.line(left, y, right, y, color=C_BORDER, width=0.6)
    y -= 22

    # ── Per-tier breakdown (Nybegynner / Mellomnivå / Viderekommen) ──────
    page.text(left, y, "Fordeling etter vanskelighetsgrad",
              size=12, bold=True, color=C_INK)
    y -= 16

    summary = sessions_store.per_game_summary() if sessions_store else {}
    tier_totals = {t: {"correct": 0, "attempts": 0, "sessions": 0}
                   for t in TIER_ORDER}
    for gid, row in summary.items():
        tier = _game_tier(gid)
        tier_totals[tier]["correct"]  += row["total_correct"]
        tier_totals[tier]["attempts"] += row["total_attempts"]
        tier_totals[tier]["sessions"] += row["sessions"]

    # Summary pills
    for i, tier in enumerate(TIER_ORDER):
        t = tier_totals[tier]
        col_w = (right - left) / 3 - 6
        x = left + i * ((right - left) / 3)
        box_h = 50
        page.rect_stroke(x, y - box_h, col_w, box_h, color=C_BORDER, width=0.4)
        page.text(x + 10, y - 14, TIER_LABEL_NO[tier],
                  size=9, bold=True, color=C_MUTED)
        acc = round(t["correct"] / t["attempts"] * 100) if t["attempts"] else 0
        page.text(x + 10, y - 34,
                  f"{t['correct']} riktige  /  {t['attempts']} forsøk",
                  size=10, bold=True, color=C_INK)
        page.text(x + 10, y - 46,
                  f"{t['sessions']} økt{'er' if t['sessions'] != 1 else ''}  ·  {acc}% snitt",
                  size=8, color=C_MUTED)
    y -= 66

    # ── Difficulty distribution bar ──────────────────────────────────────
    page.text(left, y, "Andel forsøk per vanskelighetsgrad",
              size=10, bold=True, color=C_INK)
    y -= 10
    total_attempts_all = sum(t["attempts"] for t in tier_totals.values())
    bar_h = 14
    if total_attempts_all > 0:
        cursor = left
        bar_y = y - bar_h
        tier_colors = {"basic": C_GREEN, "intermediate": C_AMBER, "advanced": C_ACCENT}
        for tier in TIER_ORDER:
            w = (right - left) * tier_totals[tier]["attempts"] / total_attempts_all
            if w > 0:
                page.rect_fill(cursor, bar_y, w, bar_h,
                               color=tier_colors[tier])
                pct = round(tier_totals[tier]["attempts"] / total_attempts_all * 100)
                if w > 30:
                    page.text(cursor + 4, bar_y + 4,
                              f"{TIER_LABEL_NO[tier]}  {pct}%",
                              size=8, bold=True, color=C_WHITE)
            cursor += w
    else:
        page.text(left, y - 10, "Ingen økter registrert ennå.",
                  size=9, color=C_DIM)
    y -= bar_h + 18

    # ── Per-game summary table ───────────────────────────────────────────
    page.text(left, y, "Spillsammendrag", size=12, bold=True, color=C_INK)
    y -= 14

    # Table header
    col_x = [left, left + 220, left + 266, left + 314, left + 360, left + 412, left + 468]
    headers = ["Spill", "\u00d8kter", "Riktige", "Fors\u00f8k",
               "Snitt", "Best rekke", "Sist"]
    for i, h in enumerate(headers):
        page.text(col_x[i], y, h, size=8, bold=True, color=C_MUTED)
    page.line(left, y - 3, right, y - 3, color=C_BORDER, width=0.4)
    y -= 14

    if not summary:
        page.text(left, y, "Ingen økter registrert ennå.",
                  size=9, color=C_DIM)
        y -= 14
    else:
        # Walk GAME_IDS in curriculum order to keep rows grouped by subject
        shown = 0
        for gid in GAME_IDS:
            row = summary.get(gid)
            if not row:
                continue
            shown += 1
            if shown % 2 == 0:
                page.rect_fill(left, y - 2, right - left, 12, color=C_SOFT)
            values = [
                GAME_NAMES_NO.get(gid, GAME_NAMES.get(gid, gid)),
                str(row["sessions"]),
                str(row["total_correct"]),
                str(row["total_attempts"]),
                f"{row['avg_accuracy']}%",
                str(row["best_streak"]),
                row["last_date"] or "—",
            ]
            for i, v in enumerate(values):
                page.text(col_x[i], y, v, size=8, color=C_INK)
            y -= 12

    _draw_footer(page, page_num, total_pages)


# ── Page 3: Kompetansemål ─────────────────────────────────────────────────────

def _draw_page_3_curriculum(page, profile_name, ach_store, sessions_store,
                            page_num, total_pages):
    left  = MARGIN
    right = PAGE_W - MARGIN
    y     = PAGE_H - MARGIN

    page.text(left, y - 6,
              "LK20 — Kompetansemål etter 5. trinn",
              size=20, bold=True, color=C_INK)
    y -= 28
    page.text(left, y,
              "Relevante kompetansemål fra læreplanen i matematikk (Udir).",
              size=10, color=C_MUTED)
    y -= 10
    page.line(left, y, right, y, color=C_BORDER, width=0.6)
    y -= 20

    # ── Legend ───────────────────────────────────────────────────────────
    legend_items = [
        ("mestret",         "Mestret"),
        ("under_utvikling", "Under utvikling"),
        ("ikke_startet",    "Ikke startet"),
        ("ikke_i_appen",    "Ikke p\u00e5begynt i appen"),
    ]
    lx = left
    for key, label in legend_items:
        page.circle_fill(lx + 4, y - 3, 4,
                         color=curriculum.STATUS_COLOR_RGB[key])
        page.text(lx + 14, y - 6, label, size=9, color=C_MUTED)
        lx += 130
    y -= 20

    # ── Goals list ───────────────────────────────────────────────────────
    counts = curriculum.summary_counts(ach_store, sessions_store)

    for goal in curriculum.GOALS_5_TRINN:
        st = curriculum.goal_status(goal, ach_store, sessions_store)
        status = st["status"]
        detail = st["detail"]
        mastered, total = st["progress"]

        # Dot
        dot_color = curriculum.STATUS_COLOR_RGB[status]
        page.circle_fill(left + 4, y - 5, 4.5, color=dot_color)

        # Goal text (wrapped)
        goal_x = left + 18
        wrap_w = right - goal_x
        end_y = page.text_wrapped(goal_x, y - 6, goal["text"],
                                  size=10, bold=True, color=C_INK,
                                  max_width=wrap_w, line_gap=2)

        # Status + progress
        status_line = curriculum.STATUS_LABEL_NO[status]
        if total > 0 and status != "ikke_i_appen":
            status_line += f"   ({mastered} av {total} spillmodus mestret)"
        page.text(goal_x, end_y - 2, status_line,
                  size=9, color=C_MUTED)

        # Optional note
        if detail:
            page.text_wrapped(goal_x, end_y - 14, detail,
                              size=8, color=C_DIM,
                              max_width=wrap_w, line_gap=2)
            y = end_y - 34
        else:
            y = end_y - 18

        # Guard against overflow (very conservative — normal content fits easily)
        if y < 110:
            break

    # ── Footnote summary ─────────────────────────────────────────────────
    # Make sure there is space for the footnote; if not, skip it.
    if y > 90:
        y -= 4
        page.line(left, y, right, y, color=C_BORDER, width=0.4)
        y -= 12
        page.text(left, y,
                  f"Oppsummering:  {counts['mestret']} mestret, "
                  f"{counts['under_utvikling']} under utvikling, "
                  f"{counts['ikke_startet']} ikke startet, "
                  f"{counts['ikke_i_appen']} ikke p\u00e5begynt i appen. "
                  f"Totalt {counts['total']} relevante kompetansem\u00e5l.",
                  size=8, color=C_MUTED)

    _draw_footer(page, page_num, total_pages)


# ── Shared drawing helpers ────────────────────────────────────────────────────

def _draw_bar_chart(page, daily, x, y_base, w, h):
    """Draw the 14-day questions-per-day chart on `page`.

    daily: list[(date_iso, correct, attempts)]
    (x, y_base) is the bottom-left corner of the plotting area.
    """
    page.line(x, y_base, x + w, y_base, color=C_FAINT, width=0.6)

    if not daily or all(a == 0 for _, _, a in daily):
        page.text(x + 4, y_base + h / 2 - 4,
                  "Ingen aktivitet registrert ennå.",
                  size=10, color=C_DIM)
        return

    max_val = max((a for _, _, a in daily), default=1)
    def _nice_max(v):
        if v <= 5:   return 5
        if v <= 10:  return 10
        if v <= 25:  return 25
        if v <= 50:  return 50
        if v <= 100: return 100
        return int(((v + 49) // 50) * 50)
    y_max = _nice_max(max_val)

    # Gridlines + y-axis labels
    for k in range(5):
        gy = y_base + h * k / 4
        page.line(x, gy, x + w, gy, color=C_SOFT, width=0.3)
        label = str(int(y_max * k / 4))
        tw = _text_width(label, 7)
        page.text(x - tw - 4, gy - 3, label, size=7, color=C_DIM)

    n       = len(daily)
    gap     = 3
    bar_w   = (w - gap * (n - 1)) / n
    today   = datetime.date.today().isoformat()
    for i, (date_iso, correct, attempts) in enumerate(daily):
        x0 = x + i * (bar_w + gap)
        if attempts > 0:
            th = attempts / y_max * h
            ch = correct  / y_max * h
            page.rect_fill(x0, y_base, bar_w, th, color=C_FAINT)
            page.rect_fill(x0, y_base, bar_w, ch, color=C_GREEN)
            # value label on top
            lbl = str(attempts)
            tw = _text_width(lbl, 6, bold=True)
            page.text(x0 + (bar_w - tw) / 2, y_base + th + 3,
                      lbl, size=6, bold=True, color=C_INK)
        # date tick
        try:
            d = datetime.date.fromisoformat(date_iso)
            label = f"{d.day}" if d.day != 1 and i != 0 else d.strftime("%d %b")
        except Exception:
            label = date_iso[-2:]
        tw = _text_width(label, 6)
        bold = (date_iso == today)
        page.text(x0 + (bar_w - tw) / 2, y_base - 10,
                  label, size=6, bold=bold,
                  color=C_INK if bold else C_MUTED)


def _draw_footer(page, page_num, total_pages):
    left  = MARGIN
    right = PAGE_W - MARGIN
    page.line(left, 50, right, 50, color=C_BORDER, width=0.4)
    page.text(left, 36,
              f"Math Practice  ·  Fremgangsrapport  ·  {datetime.date.today().isoformat()}",
              size=8, color=C_DIM)
    mid = f"Side {page_num} av {total_pages}"
    mw  = _text_width(mid, 8)
    page.text((PAGE_W - mw) / 2, 36, mid, size=8, color=C_DIM)
    tail = "(c) 2026 Aleksander Lie"
    tw   = _text_width(tail, 8)
    page.text(right - tw, 36, tail, size=8, color=C_DIM)


# ── Narrative + recommendation generators ─────────────────────────────────────

def _build_narrative(profile_name, ach_store, sessions_store) -> str:
    """Auto-generate a short Norwegian paragraph describing the progress.
    Always falls back gracefully when data is thin."""
    sessions = sessions_store.all_sessions() if sessions_store else []
    if not sessions:
        return (f"{profile_name} har ikke registrert øvingsdata ennå. "
                f"Etter noen økter vil rapporten vise fremgang, "
                f"nøyaktighet og anbefalinger.")

    # Aggregates for narrative
    stats       = ach_store.get_stats()
    days_total  = len(stats.get("days_played", []))
    best_streak = stats.get("best_streak_ever", 0)

    # Accuracy over last 14 days
    recent = sessions[-30:]   # rough "last while"
    total_correct  = sum(int(s.get("correct",  0)) for s in recent)
    total_attempts = sum(int(s.get("attempts", 0)) for s in recent)
    acc = round(total_correct / total_attempts * 100) if total_attempts else 0

    strongest = curriculum.strongest_game_ids(sessions_store, limit=1)
    weakest   = curriculum.weakest_game_ids(sessions_store, limit=1)

    parts = []
    parts.append(
        f"{profile_name} har øvd i {len(sessions)} økt"
        f"{'er' if len(sessions) != 1 else ''} fordelt på {days_total} dag"
        f"{'er' if days_total != 1 else ''}."
    )
    if total_attempts > 0:
        parts.append(
            f"Gjennomsnittlig nøyaktighet de siste øktene er {acc} %, "
            f"og beste rekke riktige svar på rad er {best_streak}."
        )
    if strongest:
        parts.append(
            f"Sterkest på {GAME_SHORT_NO.get(strongest[0], strongest[0])}."
        )
    if weakest and (not strongest or weakest[0] != strongest[0]):
        parts.append(
            f"Bør øve mer på {GAME_SHORT_NO.get(weakest[0], weakest[0])}."
        )
    return " ".join(parts)


def _build_recommendation(profile_name, sessions_store) -> tuple[str, str]:
    """Produce a short 'next focus' recommendation box (title, body)."""
    if not sessions_store or sessions_store.count() == 0:
        return (
            "Forslag til første økt",
            "Start med Multiplikasjon — nybegynner for å bygge grunnferdighet, "
            "og prøv deretter Brøk — nybegynner for å bli kjent med grunnleggende brøkregning."
        )
    weak = curriculum.weakest_game_ids(sessions_store, limit=1)
    if weak:
        gid = weak[0]
        return (
            "Foreslått fokus fremover",
            f"Anbefalt neste fokusområde er {GAME_SHORT_NO.get(gid, gid)}. "
            f"Korte, daglige økter (10–15 minutter) gir bedre resultater "
            f"enn lange økter én gang i uken."
        )
    return (
        "Foreslått fokus fremover",
        "Fortsett den jevne øvingsrutinen, og prøv å låse opp neste "
        "vanskelighetsnivå i spillene hvor grunnivået er mestret."
    )


# ── utility ───────────────────────────────────────────────────────────────────

def _fmt_minutes_no(m: float) -> str:
    if m < 60:
        return f"{int(round(m))} min"
    hours = m / 60
    if hours < 10:
        return f"{hours:.1f} t"
    return f"{int(round(hours))} t"
