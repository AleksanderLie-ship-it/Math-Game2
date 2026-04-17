"""
frac_base.py
------------
Shared base class for all fraction-based games (operations & conversions).

Overrides _validate_input / _parse_answer / _answers_match so subclasses
can work with fraction strings ("3/4", "1 3/4"), decimals ("0.75"), and
percentages typed as plain numbers ("75" meaning 75%).

ANSWER_FORMAT controls which mode is active:
    "fraction"    — parse as Fraction, compare exactly
    "decimal"     — parse as float, compare within 0.001
    "percentage"  — parse as float (user types "75"), compare given/100 to expected Fraction

Subclasses should set ANSWER_FORMAT as a class variable (operations) or
update self.ANSWER_FORMAT per question in new_question() (conversion games).

get_question_dict() returns None — fraction games do not feed the missed queue yet.
"""
# Copyright (c) 2026 Aleksander Lie. All rights reserved.

from fractions import Fraction
from .base_game import BaseGame


# ──────────────────────────────────────────── utility functions ────────────────

def _parse_frac_input(raw: str) -> Fraction:
    """
    Parse a user-typed string into a Fraction.
    Accepts:
        "3/4"       proper fraction
        "1 3/4"     mixed number
        "0.75"      decimal
        "75"        integer (whole number)
        "1.5"       decimal
    Raises ValueError if the string cannot be parsed.
    """
    raw = raw.strip().replace(",", ".")
    if not raw:
        raise ValueError("empty input")

    # Mixed number: "1 3/4"
    parts = raw.split()
    if len(parts) == 2:
        return Fraction(int(parts[0])) + Fraction(parts[1])

    # Proper fraction: "3/4"
    if "/" in raw:
        return Fraction(raw)

    # Decimal or integer: "0.75" or "75"
    return Fraction(raw).limit_denominator(10000)


def _fmt_frac(f: Fraction) -> str:
    """Format as 'n/d', or plain 'n' if f is a whole number."""
    if f.denominator == 1:
        return str(f.numerator)
    return f"{f.numerator}/{f.denominator}"


def _fmt_mixed(f: Fraction) -> str:
    """
    Format as mixed number.
    Examples:  7/4 → '1 3/4',  3/4 → '3/4',  4/4 → '1',  -7/4 → '-1 3/4'
    """
    negative = f < 0
    f = abs(f)
    if f.denominator == 1:
        result = str(f.numerator)
    elif f.numerator >= f.denominator:
        whole = f.numerator // f.denominator
        rem   = f - whole
        result = f"{whole} {rem.numerator}/{rem.denominator}"
    else:
        result = f"{f.numerator}/{f.denominator}"
    return f"-{result}" if negative else result


# ──────────────────────────────────────────────────── base class ───────────────

class FractionBase(BaseGame):
    """
    Extends BaseGame with fraction-aware input, parsing and answer matching.
    Expected answer from get_expected() must always be a Fraction.
    """
    ALLOW_DECIMAL = True          # allows "." in the entry widget
    ANSWER_FORMAT = "fraction"    # class-level default; override per question for conv games

    # ────────────────────────────────────────────── input validation ───────────

    def _validate_input(self, *_):
        v   = self.answer_var.get()
        fmt = getattr(self, "ANSWER_FORMAT", "fraction")

        if fmt in ("decimal", "percentage"):
            # Only digits + one decimal separator
            filtered = ""
            dot_seen = False
            for c in v:
                if c.isdigit():
                    filtered += c
                elif c in (".", ",") and not dot_seen:
                    dot_seen = True
                    filtered += "."
        else:
            # Fraction / mixed-number: digits, one "/", one ".", one " " (before "/")
            filtered    = ""
            dot_seen    = False
            slash_seen  = False
            space_seen  = False
            for c in v:
                if c.isdigit():
                    filtered += c
                elif c == "/" and not slash_seen and not dot_seen:
                    slash_seen = True
                    filtered  += c
                elif c in (".", ",") and not dot_seen and not slash_seen:
                    dot_seen  = True
                    filtered  += "."
                elif (c == " " and not space_seen and not slash_seen
                      and filtered and filtered[-1].isdigit()):
                    space_seen = True
                    filtered  += c

        if v != filtered:
            self.answer_var.set(filtered)

    # ────────────────────────────────────────────────────── parsing ────────────

    def _parse_answer(self, raw: str):
        """Return float for decimal/percentage format, Fraction otherwise."""
        fmt = getattr(self, "ANSWER_FORMAT", "fraction")
        raw = raw.strip().replace(",", ".")
        if fmt in ("decimal", "percentage"):
            return float(raw)
        return _parse_frac_input(raw)

    def _answers_match(self, given, expected) -> bool:
        """
        given    — output of _parse_answer (float or Fraction)
        expected — a Fraction from get_expected()

        Subclasses may return additional acceptable answers via
        _alternate_expected() — each is tested against the same format rules.
        This is how conversion games accept both the exact fraction and
        the literal reading of a rounded percentage (e.g. 38% may be
        answered as either 3/8 or 19/50).
        """
        fmt = getattr(self, "ANSWER_FORMAT", "fraction")
        candidates = [expected]
        extras = self._alternate_expected()
        if extras:
            candidates.extend(extras)

        for cand in candidates:
            try:
                if fmt == "decimal":
                    if abs(float(given) - float(cand)) < 0.0011:
                        return True
                elif fmt == "percentage":
                    if abs(float(given) / 100.0 - float(cand)) < 0.0011:
                        return True
                else:
                    if Fraction(given) == Fraction(cand):
                        return True
            except Exception:
                continue
        return False

    def _alternate_expected(self):
        """
        Override to list additional acceptable Fraction answers for the
        current question. Returns an iterable of Fractions (or empty).
        """
        return ()

    # ─────────────────────────────────────────────────── missed store ──────────

    def get_question_dict(self):
        """Fraction questions not yet tracked in the missed store."""
        return None
