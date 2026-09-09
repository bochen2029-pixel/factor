"""check_layout.py -- FACTOR tests, BLUEPRINT_v0.2.md section 5 ledger record.

Models `struct Obligation` from BLUEPRINT_v0.2.md section 5 with ctypes, using
the exact field order and widths written in the design of record, at natural
alignment (the platform C ABI, which is what a memory-mapped record shared
between the kernel binary and any reader must obey).

v0.2 changed the record: `release_ns`, `seq`, `n_wit`, `n_wait`, `tie` and
`unit` were added, the three margins became `int16_t` quantized logits instead
of `float`, and the pad shrank from 14 to 8. This file checks the v0.2 record
and nothing else.

What it asserts
  1. sizeof(Obligation) == 128 and alignof(Obligation) == 8
  2. every field sits at the offset section 5 pins in its own comment
  3. no implicit padding ANYWHERE -- no internal hole, no trailing ABI pad.
     Every one of the 128 bytes is a byte the declaration named. This matters
     because the record is memory-mapped and, per F-REPLAY, digested: implicit
     padding is uninitialised memory and would make that digest depend on what
     the allocator last left there.
  4. the planted lie -- the v0.1 record (float margins, no release_ns/seq/unit,
     _pad[14]) asserted to be 128 bytes -- must FAIL. A layout check that
     cannot tell v0.1 from v0.2 is measuring nothing.
  5. AMENDMENT 3 ITEM 1, AS MADE IMPLEMENTABLE BY AMENDMENT 4 -- the amount
     parse. `amount_fix` is a count of micro-units (Amendment 1 item 2). Item 2
     pinned round-half-even AT the micro-unit and left the parse in front of it
     open; O7 measured three of five tie cases landing on different integers
     when the text went through a binary double. Amendment 3 closed it: an
     amount is parsed from its TEXT as a decimal, by digit arithmetic, and a
     binary floating-point value never touches an amount anywhere. Amendment 4
     supplies the four things an implementer still had to invent:

       item 1  THE GRAMMAR. An amount text is an optional ASCII minus, one or
               more ASCII digits, and optionally an ASCII period followed by one
               or more ASCII digits. Nothing else -- no plus, no exponent, no
               grouping separator, no surrounding space, no bare `.5`, no
               trailing `1.`, no digit outside ASCII. Anything else is refused
               with a typed reason.
       item 2  ROUNDING IS ON THE WHOLE DISCARDED TAIL. "At the seventh decimal
               place" is withdrawn. A tail is a tie only when it is exactly a
               five followed by nothing but zeros. Fixture 13 separates the two
               readings.
       item 4  RANGE. A text whose micro-unit value does not fit int64 is
               refused with a typed reason, NEVER saturated: a saturated amount
               understates a cap breach silently. Saturation is for margins and
               counters only.
       item 6  A SOURCE THAT SUPPLIES A NUMBER. A map over a source column
               stored as a binary float declares that column's `precision`, the
               producer formats the value at that precision into the grammar
               above, the frame carries flag bit 3 `lossy_amount` and the record
               carries flag bit 14 `AMOUNT_LOSSY`. That producer's formatter is
               the ONE place a binary float is allowed near an amount, and its
               output re-enters through the same parser as any other text.

     Amendment 4 item 7 removes the amount from a derived obligation's id, so
     the parse is no longer identity-bearing; it remains law because the
     record's digest, the caps and replay all depend on it. This file carries
     the parser, the fixtures, and two planted lies -- a parser that goes
     through a Python float first, which MUST differ on at least one fixture,
     and a parser that saturates at the int64 bound instead of refusing.

If the v0.2 record does NOT come to exactly 128 with no implicit padding, this
script does not quietly fix it. It prints the measured offsets and the pad
length that would be correct, and exits 1.

Exit 0 : the record as written in section 5 is 128 bytes, correctly offset,
         with no implicit padding, the planted lie was caught, every amount
         fixture parses to its expected micro-unit integer while the double
         path is caught differing, every malformed and out-of-range text is
         refused with the typed error, and the lossy-amount path formats,
         parses and flags as Amendment 4 item 6 states.
Exit 1 : anything else; the table above says which.
"""

import ast
import ctypes
import inspect
import json
import sys
from decimal import Decimal, ROUND_HALF_EVEN, ROUND_HALF_UP

CACHE_LINE = 64
TARGET = 128
MICRO = 1000000        # Amendment 1 item 2: amount_fix counts micro-units

# (C declaration, python name, ctype, count, offset pinned by section 5)
# Exact order and exact pinned offsets from BLUEPRINT_v0.2.md section 5.
SPEC = [
    ("uint64_t id",         "id",         ctypes.c_uint64, 1,   0),
    ("uint64_t party",      "party",      ctypes.c_uint64, 1,   8),
    ("uint64_t opened_ns",  "opened_ns",  ctypes.c_uint64, 1,  16),
    ("uint64_t due_ns",     "due_ns",     ctypes.c_uint64, 1,  24),
    ("uint64_t horizon_ns", "horizon_ns", ctypes.c_uint64, 1,  32),
    ("uint64_t blocked_by", "blocked_by", ctypes.c_uint64, 1,  40),
    ("uint64_t src_rev",    "src_rev",    ctypes.c_uint64, 1,  48),
    ("uint64_t judged_rev", "judged_rev", ctypes.c_uint64, 1,  56),
    ("uint64_t release_ns", "release_ns", ctypes.c_uint64, 1,  64),
    ("int64_t  amount_fix", "amount_fix", ctypes.c_int64,  1,  72),
    ("uint32_t seq",        "seq",        ctypes.c_uint32, 1,  80),
    ("int16_t  m_hand",     "m_hand",     ctypes.c_int16,  1,  84),
    ("int16_t  m_check",    "m_check",    ctypes.c_int16,  1,  86),
    ("int16_t  m_guard",    "m_guard",    ctypes.c_int16,  1,  88),
    ("uint16_t n_wit",      "n_wit",      ctypes.c_uint16, 1,  90),
    ("uint16_t n_wait",     "n_wait",     ctypes.c_uint16, 1,  92),
    ("uint16_t tie",        "tie",        ctypes.c_uint16, 1,  94),
    ("uint32_t cls",        "cls",        ctypes.c_uint32, 1,  96),
    ("uint32_t band",       "band",       ctypes.c_uint32, 1, 100),
    ("uint32_t seat",       "seat",       ctypes.c_uint32, 1, 104),
    ("uint32_t unit",       "unit",       ctypes.c_uint32, 1, 108),
    ("uint16_t flags",      "flags",      ctypes.c_uint16, 1, 112),
    ("uint8_t  state",      "state",      ctypes.c_uint8,  1, 114),
    ("uint8_t  verb",       "verb",       ctypes.c_uint8,  1, 115),
    ("uint8_t  reason",     "reason",     ctypes.c_uint8,  1, 116),
    ("uint8_t  gear",       "gear",       ctypes.c_uint8,  1, 117),
    ("uint8_t  kind",       "kind",       ctypes.c_uint8,  1, 118),
    ("uint8_t  rung",       "rung",       ctypes.c_uint8,  1, 119),
]

SPEC_PAD = 8          # uint8_t _pad[8];   as written in v0.2 section 5
SPEC_PAD_OFFSET = 120  # ... at offset 120, per its own comment

# ---------------------------------------------------------------- planted lie
# v0.1's record, verbatim from BLUEPRINT.md section 5. Section 21's F-LAYOUT
# row names "the v0.1 claim asserted" as this check's planted lie.
SPEC_V01 = [
    ("uint64_t id",         "id",         ctypes.c_uint64, 1),
    ("uint64_t party",      "party",      ctypes.c_uint64, 1),
    ("uint64_t opened_ns",  "opened_ns",  ctypes.c_uint64, 1),
    ("uint64_t due_ns",     "due_ns",     ctypes.c_uint64, 1),
    ("uint64_t horizon_ns", "horizon_ns", ctypes.c_uint64, 1),
    ("uint64_t blocked_by", "blocked_by", ctypes.c_uint64, 1),
    ("uint64_t src_rev",    "src_rev",    ctypes.c_uint64, 1),
    ("uint64_t judged_rev", "judged_rev", ctypes.c_uint64, 1),
    ("int64_t  amount_fix", "amount_fix", ctypes.c_int64,  1),
    ("float    m_hand",     "m_hand",     ctypes.c_float,  1),
    ("float    m_check",    "m_check",    ctypes.c_float,  1),
    ("float    m_guard",    "m_guard",    ctypes.c_float,  1),
    ("uint32_t cls",        "cls",        ctypes.c_uint32, 1),
    ("uint32_t band",       "band",       ctypes.c_uint32, 1),
    ("uint32_t seat",       "seat",       ctypes.c_uint32, 1),
    ("uint16_t flags",      "flags",      ctypes.c_uint16, 1),
    ("uint8_t  state",      "state",      ctypes.c_uint8,  1),
    ("uint8_t  verb",       "verb",       ctypes.c_uint8,  1),
    ("uint8_t  reason",     "reason",     ctypes.c_uint8,  1),
    ("uint8_t  gear",       "gear",       ctypes.c_uint8,  1),
    ("uint8_t  kind",       "kind",       ctypes.c_uint8,  1),
    ("uint8_t  rung",       "rung",       ctypes.c_uint8,  1),
    ("uint8_t  _pad[14]",   "_pad",       ctypes.c_uint8, 14),
]


# ------------------------------------ Amendment 3 item 1: the amount parse
# "An amount is parsed from its text as a decimal by digit arithmetic, scaled to
# micro-units, and rounded half-even on the decimal representation; a binary
# floating-point value never touches an amount anywhere in the kernel, the maps
# or the extractor."  The two parsers below differ in ONE thing: the rational
# they hand to the rounder. Item 2 pinned the rounder; item 1 of this amendment
# pins what is handed to it. Amendment 4 items 1, 2, 4 and 6 pin the grammar,
# the tie, the range and the one lawful float.

MICRO_PLACES = 6                     # amount_fix counts 10^-6 of `unit`
ASCII_DIGITS = frozenset("0123456789")

# Amendment 4 item 4. `amount_fix` is int64 (section 5, offset 72), so the
# micro-unit integer has a hard bound. A text outside it is REFUSED. It is not
# saturated: the whole point of a cap is that it is compared in micro-units, and
# a saturated amount sits just under a cap it actually breached.
INT64_MIN = -(2 ** 63)
INT64_MAX = 2 ** 63 - 1

# Amendment 4 item 6. A source column stored as a binary float declares its
# `precision`; the producer formats the value at that precision and the loss is
# DECLARED on both the frame and the record rather than hidden in the digits.
FRAME_FLAG_LOSSY_AMOUNT = 1 << 3     # frame flag bit 3, `lossy_amount`
RECORD_FLAG_AMOUNT_LOSSY = 1 << 14   # record flag bit 14, `AMOUNT_LOSSY`


class AmountText(Exception):
    """An amount text this parser refuses. Identity-bearing input is refused,
    never coerced: a coerced amount mints a second obligation for one promise.

    `reason` is machine-readable so a caller asserts on a value and not on a
    substring of English, and so the account can count refusals by kind."""

    reason = "grammar"


class AmountRange(AmountText):
    """Amendment 4 item 4: a well-formed amount text whose micro-unit value does
    not fit int64. It is a refusal and not a clamp, and it is a DIFFERENT
    refusal from a malformed text, because the two mean opposite things about
    the upstream: one sent nonsense, the other sent a number too large to be an
    amount at all."""

    reason = "out-of-range"


def _round_half_even_ratio(num, den):
    """Round the exact rational num over den to an integer, half to even, in
    integer arithmetic only.

    The sign is handled by magnitude, which is what half-even means -- it is
    symmetric about zero, so -2.5 rounds to -2 exactly as 2.5 rounds to 2.
    """
    neg = num < 0
    n = -num if neg else num
    q, r = divmod(n, den)
    twice = 2 * r
    if twice > den or (twice == den and (q & 1)):
        q += 1
    return -q if neg else q


def parse_amount_micro(text):
    """THE RULE. Parse an amount from its text as a decimal, by digit
    arithmetic, and return the integer count of micro-units, rounded half-even
    on the whole discarded tail.

    THE GRAMMAR, Amendment 4 item 1, and nothing else:

        amount := "-"? DIGIT+ ( "." DIGIT+ )?        DIGIT := "0".."9", ASCII

    so: no leading plus, no exponent, no grouping separator, no surrounding
    space, no bare `.5`, no trailing `1.`, no lone `-`, and no digit outside
    ASCII -- because a runtime that accepts Unicode digits gives one amount two
    spellings, and `int("\\u0661")` is 1 in Python and in several other runtimes'
    equivalents. Every refusal is the typed AmountText, so a caller can tell a
    refused amount from a crash.

    THE TIE, Amendment 4 item 2. "Rounded half-even at the seventh decimal
    place" is WITHDRAWN, because it invites a parser that looks at the seventh
    digit alone. The discarded tail is a tie only when it is exactly a five
    followed by nothing but zeros; a tie rounds to the even micro-unit; anything
    else rounds by its value. That is what `beyond` decides below, and fixture
    13 (`0.00000250000001` -> 3, not 2) is the case that separates the two
    readings. Both readings are float-free, so no float check can catch the
    wrong one -- only a fixture with digits past the seventh can.

    THE RANGE, Amendment 4 item 4. The micro-unit value must fit int64. It is
    refused with AmountRange when it does not, never clamped.

    Nothing here builds a binary value. The digits are sliced as characters, the
    micro-unit integer is assembled from those characters, and the decision on
    the tail is made by comparing digits -- so the result depends on the TEXT
    and on nothing else. Amendment 4 item 7 took the amount out of a derived
    obligation's id; the parse is still law, because the record's digest, the
    hand's cap comparison and replay all read this integer.
    """
    if not isinstance(text, str):
        raise AmountText("an amount arrives as text, not as %s"
                         % type(text).__name__)
    if text == "":
        raise AmountText("empty")
    s = text[1:] if text.startswith("-") else text
    neg = text.startswith("-")
    if s == "":
        raise AmountText("a sign with no digits")
    if s.count(".") > 1:
        raise AmountText("more than one decimal point")
    whole, point, frac = s.partition(".")
    if whole == "":
        raise AmountText("no digits before the decimal point")
    if point and frac == "":
        raise AmountText("a decimal point with no digits after it")
    for ch in whole + frac:
        if ch not in ASCII_DIGITS:
            raise AmountText("%s is not an ASCII digit" % ascii(ch))

    if len(frac) <= MICRO_PLACES:
        # Nothing to round: every digit the text carries fits in a micro-unit.
        micro = int(whole + frac.ljust(MICRO_PLACES, "0"))
    else:
        micro = int(whole + frac[:MICRO_PLACES])
        # The DISCARDED TAIL is every digit past the sixth, not just the
        # seventh: `tie` is its leading digit and `beyond` says whether anything
        # follows it. A five with anything non-zero after it is ABOVE the half
        # and rounds up by value; only a five followed by nothing but zeros is a
        # tie, and a tie goes to the even micro-unit (Amendment 4 item 2).
        tie = int(frac[MICRO_PLACES])
        beyond = any(c != "0" for c in frac[MICRO_PLACES + 1:])
        if tie > 5 or (tie == 5 and beyond):
            micro += 1
        elif tie == 5 and not beyond and (micro & 1):
            micro += 1                                 # half to EVEN
    micro = -micro if neg else micro
    if micro < INT64_MIN or micro > INT64_MAX:
        # Amendment 4 item 4. NOT clamped: a saturated amount would sit at the
        # bound and compare under a cap it actually breached, and the breach
        # would never be reported. Saturation is for margins and counters.
        raise AmountRange("%s is %d micro-units, outside int64 [%d, %d]; an "
                          "amount is refused at the bound, never saturated"
                          % (text, micro, INT64_MIN, INT64_MAX))
    return micro


def parse_amount_micro_via_double(text):
    """THE PLANTED LIE. The same rule -- scale to micro-units, round half-even
    -- applied to the binary double the text parses to, instead of to the text.

    `float(text).as_integer_ratio()` is the double's EXACT value as a rational,
    and it is handed to the same rounder the decimal path uses, so this function
    isolates the parse and nothing else. Where the two disagree, the rounding
    mode is not the culprit; the binary parse is. Nothing is a tie once it has
    been through a binary float, and which side it lands on is luck.
    """
    num, den = float(text).as_integer_ratio()
    return _round_half_even_ratio(num * (10 ** MICRO_PLACES), den)


def parse_amount_micro_saturating(text):
    """THE SECOND PLANTED LIE, Amendment 4 item 4. The same decimal parse, but
    an out-of-range amount is CLAMPED to the int64 bound instead of refused --
    the obvious thing to write, and the reason item 4 had to be written down.

    A clamped amount is not merely wrong by a little. It is wrong in the one
    direction that matters: it lands just inside the bound, so the hand's cap
    comparison sees an amount UNDER any cap at or above the bound and reports no
    breach, and nothing downstream can tell a clamped amount from a real one.
    """
    try:
        return parse_amount_micro(text)
    except AmountRange:
        return INT64_MIN if text.startswith("-") else INT64_MAX


def format_amount_at_precision(value, precision):
    """AMENDMENT 4 ITEM 6 -- the producer's boundary, and the ONE place in this
    file a binary float is allowed anywhere near an amount.

    "A producer's JSON reader carries the number's lexeme as text and never
    converts it; the lexeme is the amount text. A map over a source column
    stored as a binary float declares that column's `precision`, the producer
    formats the value at that precision, the frame carries flag bit 3,
    `lossy_amount`, and the record carries flag bit 14, `AMOUNT_LOSSY`."

    So a float never crosses this line: the producer formats it at the
    precision the MAP declared -- not at whatever precision the double happens
    to carry -- and what crosses is text, which re-enters through
    `parse_amount_micro` exactly like any other amount text. The flag is a
    finding about the SOURCE, not about this value: it is set even when the
    formatted text happens to be exact, because the next row from that column
    will not be.

    Returns the producer's record of what it did, so a test can assert on every
    part of it.
    """
    if not isinstance(value, float):
        raise AmountText("this helper exists to format a binary float; %s is "
                         "not one, and a source that has the text should send "
                         "the text" % type(value).__name__)
    if not isinstance(precision, int) or isinstance(precision, bool):
        raise AmountText("the map must DECLARE the column's precision")
    if precision < 0 or precision > MICRO_PLACES:
        raise AmountText("a declared precision of %r is outside 0..%d places; "
                         "past the micro-unit there is nothing left to declare"
                         % (precision, MICRO_PLACES))
    text = "%.*f" % (precision, value)     # <- the float stops here
    return {"text": text,
            "micro": parse_amount_micro(text),
            "precision": precision,
            "frame_f": FRAME_FLAG_LOSSY_AMOUNT,
            "record_flags": RECORD_FLAG_AMOUNT_LOSSY,
            "lossy": True}


def _decimal_as_ratio(text):
    """The same decimal text as an exact rational, for cross-checking the digit
    arithmetic above against the rounder the double path uses. If these two ever
    disagree, the digit slicing is wrong and the fixtures would not show it."""
    s = text[1:] if text.startswith("-") else text
    whole, _point, frac = s.partition(".")
    mant = int(whole + frac)
    if text.startswith("-"):
        mant = -mant
    return mant * (10 ** MICRO_PLACES), 10 ** len(frac)


# The fixtures. The five O7 measured are 1 to 5; the rest are what the amendment
# needs exercised and O7 did not carry -- negatives, more than seven decimal
# places, and ties that round UP as well as ties that round DOWN.
#   (source text, expected micro-units, what the case pins)
AMOUNT_FIXTURES = [
    ("0.0000005",        0,               "O7  tie -> even 0"),
    ("0.0000025",        2,               "O7  tie -> even 2"),
    ("1.0000005",        1000000,         "O7  tie -> even"),
    ("19.9900005",       19990000,        "O7  tie -> even"),
    ("0.1234565",        123456,          "O7  tie -> even"),
    ("0.0000015",        2,               "tie UP, q odd"),
    ("0.0000035",        4,               "tie UP, q odd"),
    ("0.0000045",        4,               "tie DOWN, q even"),
    ("-0.0000025",       -2,              "negative, tie DOWN"),
    ("-0.0000015",       -2,              "negative, tie UP"),
    ("-19.9900005",      -19990000,       "negative, tie DOWN"),
    ("-0.0000005",       0,               "negative -> zero"),
    ("0.00000250000001", 3,               "14 places, above tie"),
    ("0.00000249999999", 2,               "14 places, below tie"),
    ("1.23456789012345", 1234568,         "14 places, 7th is 8"),
    ("12345678.9012345", 12345678901234,  "large, tie -> even"),
    ("0.01",             10000,           "a cent, no rounding"),
    ("19.99",            19990000,        "the writ's amount"),
]

# Forms the parser refuses, one per clause of Amendment 4 item 1's grammar.
# Each is a way one promise gets two micro-unit integers, or one integer gets
# two spellings, if it is coerced instead.
AMOUNT_REFUSED = [
    ("1e-6",        "exponent notation is a float's spelling, not a decimal"),
    ("1.2.3",       "two decimal points"),
    ("",            "empty"),
    ("1,234.00",    "a grouping separator"),
    (" 1.00",       "leading space"),
    ("1.",          "a point with no digits after it"),
    (".5",          "no digits before the point"),
    # Amendment 4 item 1, in as many words: "no plus". A leading plus is the
    # form an upstream that formats with a sign really sends, and `int("+1")`
    # is 1, so a coercing parser gives `+1.00` and `1.00` one integer and two
    # spellings of the claim text they came from.
    ("+1.00",       "a leading plus; item 1's grammar has one sign, the minus"),
    # The sign with nothing after it: the degenerate case of the same clause,
    # and the one a hand-written scanner reaches after stripping the sign.
    ("-",           "a minus and no digits at all"),
    # Arabic-Indic one and five. `int()` accepts these, so one amount would have
    # two spellings and one promise two ids. Built with chr() and printed with
    # ascii() so this file, and its output, stay pure ASCII on any console.
    (chr(0x0661) + "." + chr(0x0665),
     "Unicode decimal digits int() would accept"),
]

# Amendment 4 item 4, the range. `amount_fix` is int64, so the micro-unit value
# has a hard bound at +-2**63. The four fixtures are the two texts just INSIDE
# it and the two just OUTSIDE it, on each side of zero -- the bound is not
# symmetric, so a parser that checks abs() against 2**63-1 refuses a lawful
# amount and this table catches it.
#   (source text, expected micro-units or None when it must be refused, note)
AMOUNT_RANGE = [
    ("9223372036854.775807",   INT64_MAX,      "int64 max, just INSIDE"),
    ("9223372036854.775808",   None,           "one micro-unit OVER the max"),
    ("-9223372036854.775808",  INT64_MIN,      "int64 min, just INSIDE"),
    ("-9223372036854.775809",  None,           "one micro-unit UNDER the min"),
]

# Amendment 4 item 6, the lossy amount. A source column stored as a binary float
# declares its `precision`; the producer formats at that precision and the frame
# and record carry the flags. Two fixtures, and they pin opposite halves:
#   (the float the source holds, the map's declared precision, the text the
#    producer must emit, its micro-units, the text an exact source would have
#    sent, what the case pins)
LOSSY_FIXTURES = [
    (0.1 + 0.2, 2, "0.30", 300000, "0.30",
     "the double's noise is cut AT THE DECLARED PRECISION, not carried"),
    (2.675, 2, "2.67", 2670000, "2.675",
     "the loss is REAL: 2.675 as a double is BELOW its tie, so the "
     "producer emits 2.67 and the half-cent is gone"),
]


def floating_point_constructs(fn):
    """Walk a function's own AST and count everything that could put a binary
    floating-point value in its hands: a float or complex literal, a name that
    resolves to float/complex/Decimal, a reach for a float's bits, or a true
    division. A comment saying "no floats here" is not evidence; this is."""
    tree = ast.parse(inspect.getsource(fn))
    lits = names = divs = 0
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, (float, complex)):
            lits += 1
        elif isinstance(node, ast.Div):
            divs += 1
        elif isinstance(node, ast.Name) and node.id in ("float", "complex",
                                                        "Decimal"):
            names += 1
        elif isinstance(node, ast.Attribute) and node.attr in (
                "as_integer_ratio", "fromhex", "hex", "is_integer"):
            names += 1
    return lits, names, divs


def build(pad_len, spec=None, tag="v02"):
    """Build the Obligation structure with a trailing uint8_t _pad[pad_len]."""
    spec = SPEC if spec is None else spec
    fields = [(name, ct if n == 1 else ct * n) for (_, name, ct, n, *_r) in spec]
    if pad_len is not None and pad_len > 0:
        fields.append(("_pad", ctypes.c_uint8 * pad_len))
    return type("Obligation_%s_pad%s" % (tag, pad_len), (ctypes.Structure,),
                {"_fields_": fields})


def field_rows(struct_t, spec=None):
    """Yield (decl, name, offset, size, gap_before) for every field."""
    spec = SPEC if spec is None else spec
    rows = []
    cursor = 0
    decls = {n: d for (d, n, _, _, *_r) in spec}
    for fname, ftype in struct_t._fields_:
        off = getattr(struct_t, fname).offset
        size = ctypes.sizeof(ftype)
        rows.append((decls.get(fname, "uint8_t  %s[%d]" % (fname, size)),
                     fname, off, size, off - cursor))
        cursor = off + size
    return rows, cursor


def dump(struct_t, title, spec=None):
    rows, last_end = field_rows(struct_t, spec)
    size = ctypes.sizeof(struct_t)
    align = ctypes.alignment(struct_t)
    print("  %s" % title)
    print("  %-22s %8s %6s %6s %6s %s"
          % ("field", "offset", "size", "end", "hole", "cache line"))
    print("  " + "-" * 74)
    holes = 0
    straddles = []
    for decl, fname, off, fsize, gap in rows:
        if gap:
            holes += gap
        first, last = off // CACHE_LINE, (off + fsize - 1) // CACHE_LINE
        lines = "L%d" % first
        if first != last:
            lines = "L%d/L%d STRADDLES" % (first, last)
            straddles.append(fname)
        print("  %-22s %8d %6d %6d %6d %s"
              % (decl, off, fsize, off + fsize, gap, lines))
    tail = size - last_end
    print("  " + "-" * 74)
    print("  last field ends at %d; trailing ABI padding = %d; internal holes = %d"
          % (last_end, tail, holes))
    print("  sizeof = %d   alignof = %d" % (size, align))
    return {"size": size, "align": align, "last_end": last_end,
            "holes": holes, "tail": tail, "straddles": straddles}


def main():
    print("=" * 78)
    print("FACTOR BLUEPRINT_v0.2 section 5 -- struct Obligation layout check")
    print("platform: %s  python: %s  ctypes natural alignment (no _pack_)"
          % (sys.platform, sys.version.split()[0]))
    print("=" * 78)

    fails = []

    spec_t = build(SPEC_PAD)
    print()
    m = dump(spec_t, "AS WRITTEN IN BLUEPRINT_v0.2 SECTION 5  (uint8_t _pad[%d])"
             % SPEC_PAD)

    payload_end = m["last_end"] - SPEC_PAD   # end of `rung`, the last named field

    # -- 1. size and alignment ------------------------------------------------
    print()
    print("  [1] sizeof == %d          : measured %d   %s"
          % (TARGET, m["size"], "PASS" if m["size"] == TARGET else "FAIL"))
    if m["size"] != TARGET:
        fails.append("sizeof is %d, not %d" % (m["size"], TARGET))
    print("      alignof == 8           : measured %d   %s"
          % (m["align"], "PASS" if m["align"] == 8 else "FAIL"))
    if m["align"] != 8:
        fails.append("alignof is %d, not 8" % m["align"])
    print("      128 is two %d-byte cache lines : %s"
          % (CACHE_LINE, TARGET % CACHE_LINE == 0))

    # -- 2. every offset as section 5 pins it ---------------------------------
    off_bad = []
    for (decl, name, ct, n, pinned) in SPEC:
        got = getattr(spec_t, name).offset
        if got != pinned:
            off_bad.append((name, pinned, got))
    pad_off = getattr(spec_t, "_pad").offset
    if pad_off != SPEC_PAD_OFFSET:
        off_bad.append(("_pad", SPEC_PAD_OFFSET, pad_off))
    print("  [2] every pinned offset  : %d of %d match   %s"
          % (len(SPEC) + 1 - len(off_bad), len(SPEC) + 1,
             "PASS" if not off_bad else "FAIL"))
    for name, want, got in off_bad:
        print("        %-12s section 5 says %d, the ABI puts it at %d"
              % (name, want, got))
        fails.append("%s at %d, section 5 pins %d" % (name, got, want))

    # -- 3. no implicit padding anywhere --------------------------------------
    named_bytes = sum(ctypes.sizeof(ct) * n for (_, _, ct, n, _p) in SPEC) + SPEC_PAD
    print("  [3] no internal hole     : %d hole byte(s)   %s"
          % (m["holes"], "PASS" if m["holes"] == 0 else "FAIL"))
    if m["holes"]:
        fails.append("%d byte(s) of internal alignment hole" % m["holes"])
    print("      no trailing ABI pad    : %d byte(s)   %s"
          % (m["tail"], "PASS" if m["tail"] == 0 else "FAIL"))
    if m["tail"]:
        fails.append("%d byte(s) of implicit trailing padding" % m["tail"])
    print("      named bytes == sizeof  : %d vs %d   %s"
          % (named_bytes, m["size"],
             "PASS" if named_bytes == m["size"] else "FAIL"))
    if named_bytes != m["size"]:
        fails.append("declared fields name %d bytes but sizeof is %d"
                     % (named_bytes, m["size"]))
    print("      -> every one of the %d bytes is a byte the declaration named,"
          % m["size"])
    print("         so the F-REPLAY digest over the raw record is deterministic.")
    print("      fields straddling a cache line: %s"
          % (", ".join(m["straddles"]) if m["straddles"] else "none"))

    # -- the pad that would be correct, if the declared one is not ------------
    if m["size"] != TARGET or m["tail"] != 0:
        candidates = [n for n in range(0, 129)
                      if ctypes.sizeof(build(n)) == TARGET]
        exact = [n for n in candidates if payload_end + n == TARGET]
        print()
        print("  NOT SILENTLY FIXED. The last named field `rung` ends at byte %d."
              % payload_end)
        print("  Declared pad: _pad[%d] -> sizeof %d." % (SPEC_PAD, m["size"]))
        print("  Pad lengths that compile to %d: %s" % (TARGET, candidates))
        if exact:
            print("  Of those, only _pad[%d] leaves NO implicit trailing padding."
                  % exact[0])
            print("  CORRECTION for section 5: uint8_t _pad[%d];  (%d payload + %d pad = %d)"
                  % (exact[0], payload_end, exact[0], TARGET))
            print()
            dump(build(exact[0]), "WHAT _pad[%d] WOULD LOOK LIKE" % exact[0])
        else:
            print("  No trailing pad length reaches %d bytes; the field order itself"
                  % TARGET)
            print("  must change. Measured offsets are in the table above.")

    # -- 4. the planted lie: the v0.1 record asserted to be 128 ---------------
    print()
    print("  [4] PLANTED LIE -- section 21 F-LAYOUT: 'the v0.1 claim asserted'")
    v01_t = build(None, spec=SPEC_V01, tag="v01")
    v01 = dump(v01_t, "      v0.1 RECORD (float margins, no release_ns/seq/unit, _pad[14])",
               spec=SPEC_V01)
    lie_holds = (v01["size"] == TARGET)
    print("      the lie asserts sizeof(v0.1 record) == %d" % TARGET)
    print("      measured                              == %d" % v01["size"])
    print("      VERDICT: %s"
          % ("CAUGHT -- the v0.1 record is not 128 bytes and this check says so"
             if not lie_holds else
             "NOT CAUGHT -- the check cannot tell v0.1 from v0.2, it is blind"))
    if lie_holds:
        fails.append("planted lie NOT caught: the v0.1 record measured 128 bytes")
    print("      (the same lie is a compile-time static_assert in layout_check.cpp,")
    print("       which must FAIL to build under -DPROVE_SPEC_FAILS)")

    # -- machine-readable offsets, for cross-checking layout_check.cpp --------
    offsets = {n: getattr(spec_t, n).offset for (_, n, _, _, _p) in SPEC}
    offsets["_pad"] = pad_off
    print()
    print("  offsets(json) = " + json.dumps(offsets, sort_keys=False))

    # -- amount_fix: the scale Amendment 1 pins, measured ---------------------
    # Amendment 1 item 2 withdraws 1/65536. `amount_fix` is an integer count of
    # MICRO-UNITS, one millionth of `unit`. A cent is exactly 10,000. Rounding is
    # round-half-even to the micro-unit, applied ONCE at ingest (Amendment 4
    # item 3: the parse IS that rounding, and no map, fold, cap comparison or
    # serialization re-rounds it). Amendment 4 item 7 took the amount OUT of a
    # derived obligation's id, so what the integer decides is the record's
    # digest, section 11's caps -- compared in micro-units -- and replay. THE
    # LAYOUT DOES NOT CHANGE: amount_fix is int64 at offset 72 under either
    # scale, which is why this block is informational and the table above is
    # untouched.
    print()
    print("  amount_fix: int64, an integer count of MICRO-UNITS, 10^-6 of `unit`")
    print("              (Amendment 1 item 2; the layout above is unchanged by it)")
    lo = Decimal(-(2 ** 63)) / MICRO
    hi = Decimal(2 ** 63 - 1) / MICRO
    print("    range              : %s to %s units" % (lo, hi))
    print("                         about +-9.2 trillion units, either way")
    print("    a cent             : exactly %d micro-units" % (MICRO // 100))
    print("    %-10s %-16s %s" % ("decimal", "micro-units", "exactly representable"))
    exact_bad = 0
    for d in ("0.01", "0.10", "19.99", "500.00"):
        scaled = Decimal(d) * MICRO
        ok = (scaled == scaled.to_integral_value())
        if not ok:
            exact_bad += 1
        print("    %-10s %-16s %s"
              % (d, int(scaled) if ok else scaled, "yes" if ok else "NO"))
    print("    all four exactly representable : %s"
          % ("PASS" if exact_bad == 0 else "FAIL"))
    if exact_bad:
        fails.append("%d of the four sample amounts is not a whole number of "
                     "micro-units" % exact_bad)
    print("    rounding: round-half-even to the micro-unit, applied once at")
    print("              ingest -- and the PARSE is that one application")
    print("              (Amendment 4 item 3); nothing downstream re-rounds")
    print("    %-12s %-12s %-12s %s"
          % ("units", "x 10^6", "half-even", "half-up (NOT the rule)"))
    for d in ("0.0000005", "0.0000015", "0.0000025", "0.0000011"):
        raw = Decimal(d) * MICRO
        even = raw.quantize(Decimal(1), rounding=ROUND_HALF_EVEN)
        up = raw.quantize(Decimal(1), rounding=ROUND_HALF_UP)
        print("    %-12s %-12s %-12s %s%s"
              % (d, raw, even, up, "   <- two digests" if even != up else ""))
    print("    -> where the two columns differ, two extractors that picked")
    print("       different rounding write two different records for one")
    print("       promise: two digests, and two answers to the same cap.")
    print("       That is why item 2 pins the rule and pins it AT INGEST, once.")

    # -- 5. AMENDMENT 3 ITEM 1: the amount is parsed as DECIMAL TEXT -----------
    # Item 2 pinned the rounding MODE but not the parse in front of it, and
    # half-even is only well defined once you know what is being rounded. O7
    # measured three of five tie cases landing on different micro-unit integers
    # depending on whether the text passed through a binary double first.
    # Amendment 3 item 1 closes it: the parse is by digit arithmetic on the
    # decimal text, and no binary floating-point value touches an amount. The
    # tie cases O7 measured are now the fixtures, and the planted lie is a
    # parser that goes through a double.
    print()
    print("  [5] AMENDMENT 3 ITEM 1, AS AMENDMENT 4 MAKES IT IMPLEMENTABLE --")
    print("      the amount is parsed from its TEXT as a decimal, by digit")
    print("      arithmetic, rounded half-even ON THE WHOLE DISCARDED TAIL")
    print("      (Amendment 4 item 2 withdraws 'at the seventh decimal place':")
    print("       a tail is a tie only when it is exactly a five followed by")
    print("       nothing but zeros. Item 7 took the amount out of a derived")
    print("       id, so the parse is no longer identity-bearing -- it is still")
    print("       law, because the record's digest, the caps and replay read it)")
    print()
    print("      %-17s %15s %15s %15s %-7s %s"
          % ("source text", "expected", "decimal", "via double", "differ",
             "what it pins"))
    parse_bad = 0
    ratio_bad = 0
    differ = 0
    for text, want, note in AMOUNT_FIXTURES:
        try:
            got = parse_amount_micro(text)
        except AmountText as e:
            parse_bad += 1
            fails.append("amount %s was REFUSED by the parser (%s); it is a "
                         "well-formed decimal and must parse" % (text, e))
            print("      %-17s %15d %15s %15s %-7s %s"
                  % (text, want, "REFUSED", "-", "", note))
            continue
        dbl = parse_amount_micro_via_double(text)
        num, den = _decimal_as_ratio(text)
        exact = _round_half_even_ratio(num, den)
        if got != want:
            parse_bad += 1
            fails.append("amount %s parsed to %d micro-units, expected %d"
                         % (text, got, want))
        if got != exact:
            ratio_bad += 1
            fails.append("amount %s: digit arithmetic gave %d, exact decimal "
                         "rounding gave %d" % (text, got, exact))
        if got != dbl:
            differ += 1
        print("      %-17s %15d %15d %15d %-7s %s%s"
              % (text, want, got, dbl, "YES" if got != dbl else "", note,
                 "" if got == want else "   <- WRONG, expected above"))
    n_fix = len(AMOUNT_FIXTURES)
    print("      %d fixtures, %d parsed to the expected integer      %s"
          % (n_fix, n_fix - parse_bad, "PASS" if parse_bad == 0 else "FAIL"))
    print("      digit arithmetic == exact decimal rounding on all %d   %s"
          % (n_fix, "PASS" if ratio_bad == 0 else "FAIL"))

    # -- AMENDMENT 4 ITEM 1: the grammar, clause by clause -------------------
    # A parse that decides a record's digest refuses what it cannot spell one
    # way, rather than coercing it into a second digest for the same promise.
    refuse_bad = 0
    print()
    print("      AMENDMENT 4 ITEM 1 -- the grammar is exactly")
    print("        amount := '-'? DIGIT+ ( '.' DIGIT+ )?   DIGIT := 0..9, ASCII")
    print("      forms REFUSED, never coerced:")
    for text, why in AMOUNT_REFUSED:
        try:
            v = parse_amount_micro(text)
            refuse_bad += 1
            print("        %-14s ACCEPTED as %d -- FAIL (%s)"
                  % (ascii(text), v, why))
            fails.append("the parser accepted %s, which it must refuse (%s)"
                         % (ascii(text), why))
        except AmountRange as e:
            # A grammar refusal must not arrive wearing the range reason, or
            # the account cannot tell "the upstream sent nonsense" from "the
            # upstream sent a number too large to be an amount".
            refuse_bad += 1
            print("        %-14s refused as OUT-OF-RANGE -- FAIL: %s"
                  % (ascii(text), e))
            fails.append("the parser refused %s with reason %r; a malformed "
                         "text is a grammar refusal" % (ascii(text), e.reason))
        except AmountText as e:
            print("        %-14s refused: %s" % (ascii(text), e))
        except Exception as e:                                   # noqa: BLE001
            # A typed refusal, or it is not a refusal a caller can act on: a
            # bare ValueError out of a coercion is exactly what an amount parser
            # must not do, because it cannot be told from a crash.
            refuse_bad += 1
            print("        %-14s refused with %s, not AmountText -- FAIL: %s"
                  % (ascii(text), type(e).__name__, e))
            fails.append("the parser refused %s with %s; the refusal must be "
                         "the typed AmountText" % (ascii(text), type(e).__name__))
    print("      %d of %d refused with the typed error, reason %r      %s"
          % (len(AMOUNT_REFUSED) - refuse_bad, len(AMOUNT_REFUSED),
             AmountText.reason, "PASS" if refuse_bad == 0 else "FAIL"))

    # -- AMENDMENT 4 ITEM 4: the range, refused and never saturated ----------
    # `amount_fix` is int64 at offset 72, so the micro-unit value has a hard
    # bound. Item 4: a text outside it is refused with a typed reason, "never
    # saturated, because a saturated amount would understate a cap breach
    # silently". The planted lie is the parser that clamps.
    print()
    print("      AMENDMENT 4 ITEM 4 -- a micro-unit value outside int64 is")
    print("      REFUSED with the typed reason, never saturated")
    print("        int64 bound : [%d, %d] micro-units" % (INT64_MIN, INT64_MAX))
    print("                      = %s to %s units"
          % (Decimal(INT64_MIN).scaleb(-6), Decimal(INT64_MAX).scaleb(-6)))
    print("        %-24s %-22s %-22s %s"
          % ("source text", "the rule", "the clamping lie", "what it pins"))
    range_bad = 0
    range_caught = 0
    for text, want, note in AMOUNT_RANGE:
        try:
            got = parse_amount_micro(text)
            shown = "%d" % got
            if want is None:
                range_bad += 1
                fails.append("amount %s is outside int64 and was ACCEPTED as "
                             "%d; item 4 refuses it" % (text, got))
                shown += "  <- MUST REFUSE"
            elif got != want:
                range_bad += 1
                fails.append("amount %s parsed to %d micro-units, expected %d"
                             % (text, got, want))
                shown += "  <- WRONG"
        except AmountRange as e:
            shown = "refused(%s)" % e.reason
            if want is not None:
                range_bad += 1
                fails.append("amount %s is inside int64 and must parse to %d, "
                             "but was refused: %s" % (text, want, e))
                shown += "  <- MUST PARSE"
        except AmountText as e:
            shown = "refused(%s)" % e.reason
            range_bad += 1
            fails.append("amount %s: item 4's refusal must carry the range "
                         "reason, got %r (%s)" % (text, e.reason, e))
            shown += "  <- WRONG REASON"
        sat = parse_amount_micro_saturating(text)
        if want is None and sat in (INT64_MIN, INT64_MAX):
            range_caught += 1
        print("        %-24s %-22s %-22s %s"
              % (text, shown, "%d" % sat, note))
    print("        %d of %d as item 4 states them   %s"
          % (len(AMOUNT_RANGE) - range_bad, len(AMOUNT_RANGE),
             "PASS" if range_bad == 0 else "FAIL"))
    print("        PLANTED LIE -- the same parser CLAMPING at the bound:")
    print("          out-of-range texts it saturated instead of refusing : %d of %d"
          % (range_caught, sum(1 for _t, w, _n in AMOUNT_RANGE if w is None)))
    print("          VERDICT: %s"
          % ("CAUGHT -- the rule refuses where the lie returns the bound"
             if range_caught else
             "NOT CAUGHT -- the clamping parser agreed everywhere, so these "
             "fixtures prove nothing"))
    if range_caught == 0:
        fails.append("planted lie NOT caught: the saturating parser never "
                     "differed from the rule, so the range fixtures are not "
                     "exercising item 4")
    print("          why it matters: a cap of %d micro-units is compared"
          % INT64_MAX)
    print("            against the amount as parsed. The clamped value is")
    print("            EXACTLY the bound, so it compares <= any cap at the")
    print("            bound and the breach is never reported. Item 4's")
    print("            'saturation is for margins and counters only' is that")
    print("            asymmetry: a saturated margin is still a margin, a")
    print("            saturated amount is a false negative.")

    # No binary float anywhere in the parser -- checked by walking its own AST.
    lits = names = divs = 0
    for fn in (parse_amount_micro, _round_half_even_ratio):
        a, b, c = floating_point_constructs(fn)
        lits += a
        names += b
        divs += c
    float_free = (lits == 0 and names == 0 and divs == 0)
    print("      no floating point in the parser, by walking its own AST:")
    print("        float/complex literals   : %d" % lits)
    print("        float/complex/Decimal, or a reach for a float's bits : %d"
          % names)
    print("        true division (the one operator that makes one) : %d" % divs)
    print("        VERDICT: %s"
          % ("PASS -- the rule is enforced by the code, not by its comments"
             if float_free else "FAIL -- the parser can build a binary value"))
    if not float_free:
        fails.append("the decimal parser holds %d floating-point construct(s)"
                     % (lits + names + divs))

    # -- AMENDMENT 4 ITEM 6: the one lawful float, and the two flags ---------
    # "A map over a source column stored as a binary float declares that
    # column's `precision`, the producer formats the value at that precision,
    # the frame carries flag bit 3, `lossy_amount`, and the record carries flag
    # bit 14, `AMOUNT_LOSSY`. A lossy amount is compared against caps as written
    # and the account counts lossy amounts per class."
    print()
    print("      AMENDMENT 4 ITEM 6 -- a source that supplies a number, not text")
    print("      the producer formats it at the map's DECLARED precision, into")
    print("      item 1's grammar, and the loss is declared on both the frame")
    print("      and the record instead of hiding in the digits")
    lf_lits, lf_names, lf_divs = floating_point_constructs(
        format_amount_at_precision)
    print("        the same AST walk over the producer's formatter: %d float"
          % (lf_lits + lf_names + lf_divs))
    print("          construct(s) -- NOT zero, and that is the point: the one")
    print("          place a binary float may touch an amount is the producer's")
    print("          boundary, and the walk that finds none in the parser finds")
    print("          this one, so it is measuring and not merely agreeing")
    if lf_lits + lf_names + lf_divs == 0:
        fails.append("the AST walk sees no float in format_amount_at_precision, "
                     "so it is blind and its zero on the parser proves nothing")
    print("        frame flag bit 3  `lossy_amount` = %d   %s"
          % (FRAME_FLAG_LOSSY_AMOUNT,
             "PASS" if FRAME_FLAG_LOSSY_AMOUNT == 8 else "FAIL"))
    print("        record flag bit 14 `AMOUNT_LOSSY` = %d   %s"
          % (RECORD_FLAG_AMOUNT_LOSSY,
             "PASS" if RECORD_FLAG_AMOUNT_LOSSY == 16384 else "FAIL"))
    if FRAME_FLAG_LOSSY_AMOUNT != 8 or RECORD_FLAG_AMOUNT_LOSSY != 16384:
        fails.append("item 6 pins frame bit 3 and record bit 14; this file has "
                     "%d and %d" % (FRAME_FLAG_LOSSY_AMOUNT,
                                    RECORD_FLAG_AMOUNT_LOSSY))
    print("        %-24s %-4s %-9s %-12s %-12s %s"
          % ("the double the source has", "prec", "formatted", "micro-units",
             "exact text", "flags"))
    lossy_bad = 0
    per_class = {}
    for i, (val, prec, want_text, want_micro, exact_text, note) in \
            enumerate(LOSSY_FIXTURES):
        rec = format_amount_at_precision(val, prec)
        cls = "class-%d" % i
        per_class[cls] = per_class.get(cls, 0) + (1 if rec["lossy"] else 0)
        exact_micro = parse_amount_micro(exact_text)
        flags = "f=%d flags=%d" % (rec["frame_f"], rec["record_flags"])
        bad = []
        if rec["text"] != want_text:
            bad.append("formatted %r, expected %r" % (rec["text"], want_text))
        if rec["micro"] != want_micro:
            bad.append("parsed to %d, expected %d" % (rec["micro"], want_micro))
        if not (rec["frame_f"] & FRAME_FLAG_LOSSY_AMOUNT):
            bad.append("the frame does not carry bit 3")
        if not (rec["record_flags"] & RECORD_FLAG_AMOUNT_LOSSY):
            bad.append("the record does not carry bit 14")
        # The formatted text must itself be a lawful amount text: the producer
        # emits into item 1's grammar and the parser is not given a special
        # case for it.
        try:
            parse_amount_micro(rec["text"])
        except AmountText as e:                                  # noqa: PERF203
            bad.append("the producer emitted %r, which item 1 refuses (%s)"
                       % (rec["text"], e))
        if bad:
            lossy_bad += 1
            for b in bad:
                fails.append("lossy fixture %s: %s" % (ascii(str(val)), b))
        print("        %-24s %-4d %-9s %-12d %-12s %s%s"
              % (repr(val)[:24], prec, rec["text"], rec["micro"],
                 "%s -> %d" % (exact_text, exact_micro), flags,
                 "" if not bad else "   <- FAIL"))
        print("          %s" % note)
        if exact_micro != rec["micro"]:
            print("          the source's own value would have been %d "
                  "micro-units;" % exact_micro)
            print("          the %d-place column cannot say so, which is why the"
                  % prec)
            print("          record says AMOUNT_LOSSY rather than guessing.")
    print("        %d of %d lossy fixtures format, parse and flag as item 6"
          % (len(LOSSY_FIXTURES) - lossy_bad, len(LOSSY_FIXTURES)))
    print("          states them   %s" % ("PASS" if lossy_bad == 0 else "FAIL"))
    # "compared against caps as written": the cap comparison reads the parsed
    # integer, with no second rounding and no reach back to the double.
    cap_micro = parse_amount_micro("2.67")
    lossy_micro = format_amount_at_precision(2.675, 2)["micro"]
    true_micro = parse_amount_micro("2.675")
    print("        compared against caps AS WRITTEN, with no second rounding:")
    print("          cap %d, lossy amount %d -> breach %s"
          % (cap_micro, lossy_micro, lossy_micro > cap_micro))
    print("          cap %d, the source's true value %d -> breach %s"
          % (cap_micro, true_micro, true_micro > cap_micro))
    print("          the two disagree, and neither the hand nor the account may")
    print("          silently pick the second: the amount is compared as")
    print("          written and the record is FLAGGED, because a source that")
    print("          cannot state its own amounts exactly is a finding about")
    print("          the source.")
    if lossy_micro > cap_micro or not (true_micro > cap_micro):
        fails.append("the lossy cap comparison no longer shows the divergence "
                     "item 6 is about")
    print("        the account counts lossy amounts PER CLASS: %s"
          % ", ".join("%s=%d" % kv for kv in sorted(per_class.items())))
    if sum(per_class.values()) != len(LOSSY_FIXTURES):
        fails.append("the per-class lossy tally counted %d of %d"
                     % (sum(per_class.values()), len(LOSSY_FIXTURES)))
    # A float is not an amount text, and the helper says so rather than
    # formatting at a precision nobody declared.
    for bad_call, why in ((("19.99", 2), "a str, which should be sent as text"),
                          ((1.0, 7), "a precision past the micro-unit"),
                          ((1.0, None), "no declared precision")):
        try:
            format_amount_at_precision(*bad_call)
            print("        refuses %-28s ACCEPTED -- FAIL" % why)
            fails.append("format_amount_at_precision accepted %r (%s)"
                         % (bad_call, why))
        except AmountText:
            print("        refuses %-34s PASS" % why)

    # -- the planted lie: the double path must DIFFER somewhere ---------------
    print()
    print("      PLANTED LIE -- the same rule applied to the double the text")
    print("      parses to. Both paths hand a rational to the SAME half-even")
    print("      rounder, so the parse is the only difference between them.")
    print("        fixtures where the double path differs : %d of %d"
          % (differ, n_fix))
    print("        VERDICT: %s"
          % ("CAUGHT -- the fixtures exercise Amendment 3 item 1"
             if differ else
             "NOT CAUGHT -- the double agreed everywhere, so these fixtures "
             "prove nothing"))
    if differ == 0:
        fails.append("planted lie NOT caught: the double path agreed with the "
                     "decimal path on all %d fixtures, so the fixtures are not "
                     "exercising the parse rule" % n_fix)
    print("        why: 0.0000025 as a double is exactly")
    print("             %s," % Decimal(float("0.0000025")))
    print("             which is ABOVE the tie, so half-even rounds it up to 3")
    print("             while the decimal 2.5 rounds to the even 2. It cuts both")
    print("             ways: 0.0000035 as a double is BELOW its tie, so the")
    print("             double rounds down to 3 where the decimal rounds up to")
    print("             4. Nothing is a tie once it has been through a binary")
    print("             float, and which side it lands on is luck.")
    print("        these fixtures are F-EXTRACT's and F-REPLAY's: the")
    print("        extractor is where an amount text becomes the micro-unit")
    print("        integer, and Amendment 4 item 7 moved what depends on that")
    print("        integer from the derived id to the record's digest, the")
    print("        hand's cap comparison and replay.")

    # -- endianness ------------------------------------------------------------
    probe = ctypes.c_uint64(0x0102030405060708)
    print("  byte order on this machine: %s (uint64 0x0102030405060708 -> %s)"
          % (sys.byteorder, bytes(probe).hex()))
    print("  section 5 pins little-endian and an explicit pad, and the ledger header")
    print("  pins byte order, record size and every enum; a ledger whose header")
    print("  disagrees with the running build is refused, never converted.")

    print()
    print("=" * 78)
    if fails:
        print("RESULT: FAIL")
        for f in fails:
            print("  - %s" % f)
        return 1
    print("RESULT: PASS -- section 5's record is %d bytes, alignof %d, every offset"
          % (TARGET, m["align"]))
    print("        as pinned, no implicit padding anywhere, planted lie caught;")
    print("        %d amount fixtures parse to their expected micro-unit integers"
          % len(AMOUNT_FIXTURES))
    print("        by decimal digit arithmetic, and the double path is caught")
    print("        differing on %d of them (Amendment 3 item 1);" % differ)
    print("        %d malformed texts refused by item 1's grammar, %d range"
          % (len(AMOUNT_REFUSED), len(AMOUNT_RANGE)))
    print("        fixtures at the int64 bound with the clamping parser caught,")
    print("        and %d lossy fixtures formatted at a declared precision and"
          % len(LOSSY_FIXTURES))
    print("        flagged on frame bit 3 and record bit 14 (Amendment 4).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
