"""frame_roundtrip.py -- FACTOR tests, BLUEPRINT_v0.2.md section 4 as amended.

Amendment 1 (2026-09-08) changes the frame. Section 4 now pins one line, EIGHT
tab-separated fields, UTF-8:

    t_mono_ns <TAB> venue <TAB> lane <TAB> grain <TAB> rev <TAB> f <TAB> text <TAB> h

where `f` is a small integer of frame flags -- bit 0 `badenc`, bit 1 `truncated`,
bit 2 `synthetic_rev` -- so the mark finally has a home on the frame itself,
which replay needs (amendment item 8).

`h` is the line's chain hash,

    h = BLAKE2b-256( prev_hex || u64le(len) || fields 1-7 as escaped bytes
                                               with their tabs )

unkeyed so a spool verifies alone, PERSONALIZED with the exact ASCII string
`FCTR-spool-v1` (amendment item 15's pinned list, item 11's domain separation),
so an unkeyed BLAKE2b elsewhere cannot verify as a spool line. `u64le(len)` is
the byte length of the body: fields one through seven with their tabs, escaped,
excluding the tab before `h`, `h` itself, and the terminating newline (item 10).
The genesis `prev` for the first frame is the header line's own `h`; the
header's `prev` is 64 zeros.

Escaping, STRICT, every field, the backslash first, the decoder strict:

    \\  -> \\\\      TAB -> \\t      LF -> \\n      CR -> \\r
    every other C0 control and U+007F  -> \\xNN
    U+0085, U+2028, U+2029             -> \\uNNNN
    a byte sequence that is not valid UTF-8 -> \\xNN per byte, and the frame
                                               sets bit 0 of `f`

Amendment item 9 disambiguates `\\xNN`: NN <= 0x7F names a CODE POINT; NN >= 0x80
names a RAW BYTE and is legal only on a frame whose `badenc` bit is set. A
decoder that accepts \\xNN above 0x7F with the badenc bit clear is PLANTED LIE 5
below, and must be caught.

Amendment item 14 caps every field: `venue`, `lane` and `grain` at 64 encoded
bytes, `text` at the header's frame cap. A line therefore has a bound, printed.

What is checked, per string, on the full eight-field line
  P1  no raw LF or CR survives encoding
  P2  exactly seven TABs, so the split into eight fields is unambiguous
  P3  a byte-level reader sees exactly one line
  P4  str.splitlines() sees exactly one line          <- STRICT must give 0 here
  P5  the round trip returns every field byte-identically
  P6  the eighth field verifies against prev and the body
  P7  the eighth field is 64 lowercase hex characters
  P8  every field is inside its cap

Exit 0 : every property holds under STRICT and all five planted lies were caught.
Exit 1 : anything else.
"""

import hashlib
import random
import sys

FIELDS = ("t_mono_ns", "venue", "lane", "grain", "rev", "f", "text", "h")
NFIELDS = len(FIELDS)          # eight, after amendment item 8
NBODY = NFIELDS - 1            # the seven the hash covers
TAB = "\t"
GENESIS = "0" * 64

# Amendment item 15: the personalization strings are pinned and are at most
# sixteen bytes. The spool chain is unkeyed and personalized with this one.
PERSON_SPOOL = b"FCTR-spool-v1"
BLAKE2B_PERSON_MAX = 16

# Amendment item 8: the frame flags, in `f`.
F_BADENC = 1 << 0
F_TRUNCATED = 1 << 1
F_SYNTHETIC_REV = 1 << 2
F_KNOWN = F_BADENC | F_TRUNCATED | F_SYNTHETIC_REV
F_NAMES = ((F_BADENC, "badenc"), (F_TRUNCATED, "truncated"),
           (F_SYNTHETIC_REV, "synthetic_rev"))

# Amendment item 14: venue, lane and grain are capped at 64 ENCODED bytes; text
# is capped at the header's frame cap.
FIELD_CAP = 64
HEADER_FRAME_CAP = 65536

# Characters that at least one common reader treats as a line terminator, plus
# NUL. MIN does not escape these; STRICT does. This is the set that makes the
# difference measurable.
EXTRA_SPLITTERS = "\x00\x0b\x0c\x1c\x1d\x1e\x85\u2028\u2029"


def H(data):
    """Section 4's spool hash as amended: BLAKE2b-256, unkeyed, personalized."""
    return hashlib.blake2b(data, digest_size=32, person=PERSON_SPOOL).digest()


def H_unpersonalized(data):
    """The same hash WITHOUT the personalization -- shown, never used, so the
    domain separation amendment item 11 asks for is measured rather than assumed."""
    return hashlib.blake2b(data, digest_size=32).digest()


def u64le(n):
    return int(n).to_bytes(8, "little", signed=False)


def flag_names(f):
    got = [nm for bit, nm in F_NAMES if f & bit]
    return "+".join(got) if got else "none"


# ------------------------------------------------------- the escaping profiles

_ESC = {"\\": "\\\\", "\t": "\\t", "\n": "\\n", "\r": "\\r"}
_UNESC = {"\\": "\\", "t": "\t", "n": "\n", "r": "\r"}


def esc_min(s):
    """Profile MIN -- NOT a legal profile in v0.2; kept as the measurement."""
    return "".join(_ESC.get(ch, ch) for ch in s)


def esc_strict(s):
    """Profile STRICT -- what section 4 mandates. Backslash first by construction.

    Note that STRICT never emits \\xNN with NN >= 0x80: every code point at or
    above U+0080 that is not U+0085 is written as itself in UTF-8. That is what
    makes amendment item 9's rule consistent -- \\xNN above 0x7F can only have
    come from a raw byte, and therefore only from a badenc frame.
    """
    out = []
    for ch in s:
        if ch in _ESC:
            out.append(_ESC[ch])
            continue
        o = ord(ch)
        if o < 0x20 or o == 0x7F:
            out.append("\\x%02x" % o)
        elif o in (0x85, 0x2028, 0x2029):
            out.append("\\u%04x" % o)
        else:
            out.append(ch)
    return "".join(out)


def esc_bytes(raw):
    """Escape a byte string that is not necessarily valid UTF-8.

    Returns (escaped_text, badenc). Valid UTF-8 runs escape as STRICT text; a
    byte that cannot start or continue a valid sequence escapes as \\xNN and
    sets badenc -- which, since amendment item 8, is bit 0 of the frame's `f`.
    """
    out = []
    badenc = False
    i = 0
    n = len(raw)
    while i < n:
        for width in (4, 3, 2, 1):
            if i + width <= n:
                try:
                    ch = raw[i:i + width].decode("utf-8")
                except UnicodeDecodeError:
                    continue
                if len(ch) == 1:
                    out.append(esc_strict(ch))
                    i += width
                    break
        else:
            out.append("\\x%02x" % raw[i])
            badenc = True
            i += 1
    return "".join(out), badenc


def unesc(s, badenc=False):
    """Strict unescape. Raises ValueError on anything section 4 does not name.

    Amendment item 9: \\xNN with NN <= 0x7F is a code point; NN >= 0x80 is a raw
    byte and is legal ONLY when the frame's badenc bit is set. On a badenc frame
    a raw byte is returned here as the code point chr(NN) -- a lossy view kept
    only so a str-level round trip is expressible. The byte-exact path is
    unesc_to_bytes() below, and it is what the invalid-UTF-8 fixtures use.
    """
    out = []
    i = 0
    n = len(s)
    while i < n:
        ch = s[i]
        if ch == "\\":
            if i + 1 >= n:
                raise ValueError("trailing backslash: escape truncated")
            k = s[i + 1]
            if k in _UNESC:
                out.append(_UNESC[k])
                i += 2
            elif k == "x":
                if len(s[i + 2:i + 4]) != 2:
                    raise ValueError("truncated \\xNN escape")
                nn = int(s[i + 2:i + 4], 16)
                if nn >= 0x80 and not badenc:
                    raise ValueError(
                        "\\x%02x names a raw byte and is legal only on a frame "
                        "whose badenc bit (bit 0 of f) is set" % nn)
                out.append(chr(nn))
                i += 4
            elif k == "u":
                if len(s[i + 2:i + 6]) != 4:
                    raise ValueError("truncated \\uNNNN escape")
                cp = int(s[i + 2:i + 6], 16)
                if 0xD800 <= cp <= 0xDFFF:
                    raise ValueError("escape names a lone surrogate")
                out.append(chr(cp))
                i += 6
            else:
                raise ValueError("unknown escape \\%s -- the decoder is strict, "
                                 "the frame is refused" % k)
        elif ch in "\t\n\r":
            raise ValueError("raw %r inside an encoded field" % ch)
        else:
            out.append(ch)
            i += 1
    return "".join(out)


def unesc_to_bytes(s, badenc=False):
    """Byte-exact unescape: \\xNN >= 0x80 is one raw byte, everything else is
    its UTF-8 encoding. This is the decoder a badenc frame needs, because a
    decoded raw 0xe9 and a decoded U+00E9 are not the same thing on the wire."""
    out = bytearray()
    i = 0
    n = len(s)
    while i < n:
        ch = s[i]
        if ch == "\\":
            if i + 1 >= n:
                raise ValueError("trailing backslash: escape truncated")
            k = s[i + 1]
            if k in _UNESC:
                out += _UNESC[k].encode("utf-8")
                i += 2
            elif k == "x":
                if len(s[i + 2:i + 4]) != 2:
                    raise ValueError("truncated \\xNN escape")
                nn = int(s[i + 2:i + 4], 16)
                if nn >= 0x80:
                    if not badenc:
                        raise ValueError(
                            "\\x%02x names a raw byte and is legal only on a "
                            "frame whose badenc bit is set" % nn)
                    out.append(nn)               # a RAW BYTE, not a code point
                else:
                    out += chr(nn).encode("utf-8")
                i += 4
            elif k == "u":
                if len(s[i + 2:i + 6]) != 4:
                    raise ValueError("truncated \\uNNNN escape")
                cp = int(s[i + 2:i + 6], 16)
                if 0xD800 <= cp <= 0xDFFF:
                    raise ValueError("escape names a lone surrogate")
                out += chr(cp).encode("utf-8")
                i += 6
            else:
                raise ValueError("unknown escape \\%s" % k)
        elif ch in "\t\n\r":
            raise ValueError("raw %r inside an encoded field" % ch)
        else:
            out += ch.encode("utf-8")
            i += 1
    return bytes(out)


# --------------------------------------------------------------- the frame line

def parse_f(raw):
    """`f` is a small integer of flags, written as canonical decimal."""
    if not raw or not raw.isdigit() or (len(raw) > 1 and raw[0] == "0"):
        raise ValueError("f is not a canonical decimal integer: %r" % raw[:16])
    f = int(raw)
    if f & ~F_KNOWN:
        raise ValueError("f carries unknown flag bit(s) 0x%x -- the decoder is "
                         "strict, the frame is refused" % (f & ~F_KNOWN))
    return f


def check_caps(escaped_fields, frame_cap=HEADER_FRAME_CAP):
    """Amendment item 14, applied to the ENCODED field."""
    for i, name in ((1, "venue"), (2, "lane"), (3, "grain")):
        n = len(escaped_fields[i].encode("utf-8"))
        if n > FIELD_CAP:
            raise ValueError("%s is %d encoded bytes, cap is %d"
                             % (name, n, FIELD_CAP))
    n = len(escaped_fields[6].encode("utf-8"))
    if n > frame_cap:
        raise ValueError("text is %d encoded bytes, the header's frame cap is %d"
                         % (n, frame_cap))


def frame_hash(prev_hex, body):
    return H(prev_hex.encode("ascii") + u64le(len(body)) + body).hex()


def encode_pre(escaped_fields, prev_hex, frame_cap=HEADER_FRAME_CAP, caps=True):
    """Build the line from seven ALREADY ESCAPED fields. Returns (line, h)."""
    if len(escaped_fields) != NBODY:
        raise ValueError("expected %d body fields, got %d"
                         % (NBODY, len(escaped_fields)))
    if caps:
        check_caps(escaped_fields, frame_cap)
    body = TAB.join(escaped_fields).encode("utf-8")
    h = frame_hash(prev_hex, body)
    return body.decode("utf-8") + TAB + h, h


def encode_frame(t_mono_ns, venue, lane, grain, rev, f, text, prev_hex,
                 esc=esc_strict, frame_cap=HEADER_FRAME_CAP, caps=True):
    """Return (line_text, h). The line carries no terminating LF."""
    fields = [esc(str(t_mono_ns)), esc(venue), esc(lane), esc(grain),
              esc(str(rev)), str(int(f)), esc(text)]
    return encode_pre(fields, prev_hex, frame_cap=frame_cap, caps=caps)


def decode_frame(line, prev_hex=None, unesc_fn=unesc, frame_cap=HEADER_FRAME_CAP,
                 caps=True):
    """Split, unescape and (when prev_hex is given) verify the eighth field."""
    if "\n" in line or "\r" in line:
        raise ValueError("frame line contains a raw newline")
    parts = line.split(TAB)
    if len(parts) != NFIELDS:
        raise ValueError("expected %d fields, got %d -- an unescaped TAB got through"
                         % (NFIELDS, len(parts)))
    h = parts[NBODY]
    if len(h) != 64 or any(c not in "0123456789abcdef" for c in h):
        raise ValueError("field %d is not 64 lowercase hex characters: %r"
                         % (NFIELDS, h[:20]))
    if prev_hex is not None:
        body = TAB.join(parts[:NBODY]).encode("utf-8")
        want = frame_hash(prev_hex, body)
        if want != h:
            raise ValueError("chain hash mismatch: have %s want %s"
                             % (h[:16], want[:16]))
    if caps:
        check_caps(parts[:NBODY], frame_cap)
    f = parse_f(parts[5])
    badenc = bool(f & F_BADENC)
    vals = [unesc_fn(p, badenc) for p in parts[:NBODY]]
    return {"t_mono_ns": int(vals[0]), "venue": vals[1], "lane": vals[2],
            "grain": vals[3], "rev": int(vals[4]), "f": f, "text": vals[6],
            "h": h, "escaped": parts[:NBODY]}


def line_bound(frame_cap=HEADER_FRAME_CAP):
    """Amendment item 14: 'A line therefore has a bound.' Here it is."""
    return (20                     # t_mono_ns, u64 as decimal
            + 3 * FIELD_CAP        # venue, lane, grain
            + 20                   # rev, u64 as decimal
            + 3                    # f, a small integer of flags
            + frame_cap            # text
            + 64                   # h
            + (NFIELDS - 1))       # the seven tabs


# ------------------------------------------------------------------- frame cap

def cap_encoded(text, cap, esc=esc_strict):
    """Section 4: the cap is a byte count applied to the ENCODED field, and
    truncation cuts the SOURCE on a code-point boundary before escaping, so an
    escape is never split. Returns (encoded, dropped_code_points)."""
    enc = esc(text).encode("utf-8")
    if len(enc) <= cap:
        return enc.decode("utf-8"), 0
    lo, hi = 0, len(text)
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if len(esc(text[:mid]).encode("utf-8")) <= cap:
            lo = mid
        else:
            hi = mid - 1
    return esc(text[:lo]), len(text) - lo


# ------------------------------------------------------------------- the corpus

ALPHABET = (
    "abcXYZ019 .,;:'\"" * 3          # ordinary text, weighted
    + "\t\t\n\n\r\\\\"                # the four that MUST be escaped
    + EXTRA_SPLITTERS                 # the ones MIN leaves alive
    + "\x01\x1b\x7f"                  # other controls
    + "\u00e9\u00fc\u4e2d\u6587\u0416\u05d0\u0627"   # non-ASCII BMP
    + "\U0001f600\U0001f4a9\U00010000"               # astral
    + "e\u0301a\u0308"                                # combining marks
    + "\u200b\ufeff"                                  # zero-width, BOM
)

ADVERSARIAL = [
    "",
    "\\",
    "\\\\",
    "\\t",              # a literal backslash then a t -- must NOT decode to TAB
    "\\n\\r\\\\",
    "\t",
    "\n",
    "\r",
    "\r\n",
    "\n\r",
    "a\tb\nc\rd\\e",
    "trailing backslash \\",
    "\\x41",            # looks like an escape, is text
    "\\x80",            # looks like a RAW BYTE escape, is text -- item 9's edge
    "\\u0041",
    "\x00",
    "\x85",
    "\u2028",
    "\u2029",
    "\x0b\x0c\x1c\x1d\x1e",
    "\U0001f600\t\U0001f4a9\n",
    "quote\"and'apostrophe",
    "\u00e9\u00fc",     # code points 0x80..0xff, which are NOT raw bytes
    " " * 100,
    "\\" * 64,
]

BAD_BYTES = [
    b"\xff\xfe",                     # never valid UTF-8
    b"caf\xe9",                      # latin-1 e-acute inside ASCII
    b"\xc3\x28",                     # a truncated two-byte sequence
    b"ok\xed\xa0\x80end",            # a surrogate encoded as UTF-8
    b"\x80\x81\x82",                 # bare continuation bytes
]


def make_corpus(n, seed=20260908):
    rng = random.Random(seed)
    corpus = list(ADVERSARIAL)
    while len(corpus) < n:
        ln = rng.choice((0, 1, 2, 3, 5, 8, 13, 40, 200))
        corpus.append("".join(rng.choice(ALPHABET) for _ in range(ln)))
    return corpus[:n]


# ------------------------------------------------------------------ the checks

def check_profile(corpus, esc, name):
    """Round-trip every string through the full eight-field line.

    Returns (failures, splitline_violations, head)."""
    fails = []
    split_bad = []
    prev = GENESIS                       # stands in for the header's h
    # The fixture lane's rev is the lane's own synthetic counter, so every frame
    # in this corpus carries bit 2. `f` is therefore non-zero throughout and the
    # round trip has something to carry.
    f = F_SYNTHETIC_REV
    for idx, s in enumerate(corpus):
        line, h = encode_frame(1700000000000000000 + idx, "venue-a", "mail-bo",
                               "commit", idx, f, s, prev, esc=esc)
        # P1: no raw newline survived encoding.
        if "\n" in line or "\r" in line:
            fails.append((idx, "P1 raw newline survived encoding"))
            prev = h
            continue
        # P2: exactly seven TABs, so the eight-way split is unambiguous.
        if line.count(TAB) != NFIELDS - 1:
            fails.append((idx, "P2 tab count %d" % line.count(TAB)))
            prev = h
            continue
        # P3: a byte-level reader sees exactly one line.
        if len((line.encode("utf-8") + b"\n").split(b"\n")) != 2:
            fails.append((idx, "P3 byte-level split saw more than one line"))
            prev = h
            continue
        # P4: str.splitlines() sees exactly one line. STRICT must give zero
        # violations; MIN's count is the measurement that justifies STRICT.
        if len(line.splitlines()) > 1:
            split_bad.append(idx)
        # P5/P6/P7/P8: round trip, chain hash, hex shape, caps.
        try:
            got = decode_frame(line, prev_hex=prev)
        except ValueError as e:
            fails.append((idx, "P5 decode raised: %s" % e))
            prev = h
            continue
        if got["text"] != s:
            fails.append((idx, "P5 text differs"))
        elif got["t_mono_ns"] != 1700000000000000000 + idx or got["rev"] != idx:
            fails.append((idx, "P5 scalar field differs"))
        elif got["f"] != f:
            fails.append((idx, "P5 flags differ: %d" % got["f"]))
        elif got["h"] != h:
            fails.append((idx, "P6 chain hash differs"))
        prev = h
    return fails, split_bad, prev


# ----------------------------------------------------------------- planted lies

def esc_drop_cr(s):
    """LIE 1 (section 21 F-FRAME's own): an encoder that drops carriage returns."""
    return esc_strict(s.replace("\r", ""))


def esc_no_backslash(s):
    """LIE 2: escapes TAB/LF/CR and the controls but not the backslash itself.

    Ambiguous: the two-character text  \\t  encodes to  \\t  and decodes to a TAB.
    """
    out = []
    for ch in s:
        if ch in ("\t", "\n", "\r"):
            out.append(_ESC[ch])
            continue
        o = ord(ch)
        if o < 0x20 or o == 0x7F:
            out.append("\\x%02x" % o)
        elif o in (0x85, 0x2028, 0x2029):
            out.append("\\u%04x" % o)
        else:
            out.append(ch)
    return "".join(out)


def esc_wrong_order(s):
    """LIE 3: the right set, the wrong order -- TAB escaped before the backslash."""
    t = (s.replace("\t", "\\t").replace("\n", "\\n").replace("\r", "\\r"))
    t = t.replace("\\", "\\\\")          # <- too late; it doubles its own output
    return t


def unesc_permissive(s, badenc=False):
    """LIE 4: a decoder that passes an unknown escape through instead of raising."""
    out = []
    i = 0
    while i < len(s):
        if s[i] == "\\" and i + 1 < len(s):
            k = s[i + 1]
            if k in _UNESC:
                out.append(_UNESC[k])
            else:
                out.append("\\" + k)      # <- the lie
            i += 2
        else:
            out.append(s[i])
            i += 1
    return "".join(out)


def unesc_badenc_blind(s, badenc=False):
    """LIE 5 (amendment item 9): a decoder that accepts \\xNN above 0x7F whatever
    the frame's badenc bit says. It decodes a raw byte out of a frame that never
    declared one, so a lane can smuggle bytes past every reader that trusts the
    mark -- which is the whole reason item 8 gave the mark a home."""
    return unesc(s, badenc=True)          # <- the lie: the flag is ignored


def catch_encoder_lie(corpus, esc):
    """Return the first corpus index at which this encoder fails to round-trip."""
    prev = GENESIS
    for idx, s in enumerate(corpus):
        try:
            line, h = encode_frame(1, "v", "l", "commit", 0, 0, s, prev, esc=esc)
            if "\n" in line or "\r" in line:
                return idx, s, "raw newline in output"
            if line.count(TAB) != NFIELDS - 1:
                return idx, s, "tab count %d" % line.count(TAB)
            if decode_frame(line, prev_hex=prev)["text"] != s:
                return idx, s, "decoded text differs from input"
            prev = h
        except ValueError as e:
            return idx, s, "decode raised: %s" % e
    return None


def catch_decoder_lie(corpus):
    """The permissive decoder: find an input it silently accepts."""
    for idx, s in enumerate(corpus):
        bad = esc_strict(s) + "\\q"       # an escape section 4 does not name
        try:
            unesc(bad)
            return idx, s, "the STRICT decoder failed to raise"
        except ValueError:
            pass
        try:
            unesc_permissive(bad)         # the lie accepts it
            return idx, s, "the permissive decoder accepted an unknown escape"
        except ValueError:
            continue
    return None


def catch_badenc_lie():
    """LIE 5: build a real eight-field frame whose text carries \\xNN above 0x7F
    while `f` leaves the badenc bit CLEAR. The strict decoder must refuse it; the
    blind decoder must accept it. Anything else and the badenc bit is decorative.
    """
    for raw in BAD_BYTES:
        enc, badenc = esc_bytes(raw)
        if not badenc:
            continue
        fields = [esc_strict("1"), esc_strict("venue-a"), esc_strict("mail-bo"),
                  esc_strict("commit"), esc_strict("0"), "0", enc]   # f = 0
        line, _h = encode_pre(fields, GENESIS)
        try:
            decode_frame(line, prev_hex=GENESIS)
            return raw, enc, "the STRICT decoder failed to refuse it"
        except ValueError:
            pass
        try:
            got = decode_frame(line, prev_hex=GENESIS, unesc_fn=unesc_badenc_blind)
        except ValueError:
            continue
        return (raw, enc,
                "the blind decoder accepted it and produced %r with f=%d (badenc "
                "clear)" % (got["text"][:20], got["f"]))
    return None


def main():
    n = 10000
    corpus = make_corpus(n)
    print("=" * 78)
    print("FACTOR BLUEPRINT_v0.2 section 4 as amended -- frame codec property test")
    print("frame: %d tab-separated fields, the sixth `f` the flags, the eighth the"
          % NFIELDS)
    print("       chain hash    (Amendment 1, items 8 to 14)")
    print("hash : BLAKE2b-256, unkeyed, person=%r, over prev_hex || u64le(len) || body"
          % PERSON_SPOOL.decode())
    print("corpus: %d strings (seeded, deterministic) incl. %d adversarial literals"
          % (len(corpus), len(ADVERSARIAL)))
    print("=" * 78)

    rc = 0

    # -- the eighth field, and the personalization ---------------------------
    print()
    print("(0) THE FRAME, AS AMENDED")
    print("    fields                 : %s" % " ".join(FIELDS))
    print("    hashed body            : fields 1-%d with their tabs, escaped;" % NBODY)
    print("                             excludes the tab before h, h, and the LF")
    print("    f, the flag bits       : %s"
          % "  ".join("bit %d %s" % (i, nm)
                      for i, (_b, nm) in enumerate(F_NAMES)))
    print("    personalization        : %r (%d bytes, limit %d)   %s"
          % (PERSON_SPOOL.decode(), len(PERSON_SPOOL), BLAKE2B_PERSON_MAX,
             "PASS" if len(PERSON_SPOOL) <= BLAKE2B_PERSON_MAX else "FAIL"))
    if len(PERSON_SPOOL) > BLAKE2B_PERSON_MAX:
        rc = 1
    kat_body = b"known-answer"
    kat_pre = GENESIS.encode("ascii") + u64le(len(kat_body)) + kat_body
    with_p = H(kat_pre).hex()
    without_p = H_unpersonalized(kat_pre).hex()
    print("    KAT personalized       : %s" % with_p[:32])
    print("    KAT unpersonalized     : %s" % without_p[:32])
    print("    domain separation      : %s"
          % ("PASS -- a plain unkeyed BLAKE2b-256 of the same preimage does not "
             "verify as a spool line" if with_p != without_p else "FAIL"))
    if with_p == without_p:
        rc = 1

    # -- the mandated profile, and the one it replaced ----------------------
    results = {}
    for esc, name, mandated in ((esc_strict, "STRICT", True),
                                (esc_min, "MIN", False)):
        fails, split_bad, head = check_profile(corpus, esc, name)
        results[name] = (fails, split_bad, head)
        ok = not fails
        print()
        print("profile %-6s %s" % (name, "(MANDATED by section 4)" if mandated
                                   else "(NOT legal in v0.2; run as the measurement)"))
        print("  round trip, all %d fields + chain hash : %s  (%d/%d passed)"
              % (NFIELDS, "PASS" if ok else "FAIL",
                 len(corpus) - len(fails), len(corpus)))
        if fails:
            for f in fails[:5]:
                print("     idx %d: %s" % f)
            if mandated:
                rc = 1
        print("  one line under a byte-level reader     : yes (checked per frame)")
        print("  one line under str.splitlines()        : %s (%d violations of %d)"
              % ("yes" if not split_bad else "NO", len(split_bad), len(corpus)))
        print("  chain head after %d frames          : %s" % (len(corpus), head[:32]))
        if split_bad and not mandated:
            bad_chars = sorted({c for i in split_bad for c in corpus[i]
                                if c in EXTRA_SPLITTERS})
            print("     -> MIN lets these through raw: %s"
                  % " ".join("U+%04X" % ord(c) for c in bad_chars))
            print("     -> a byte-level reader sees 1 frame, str.splitlines() sees 2.")
            print("        %.1f%% of this corpus triggers it. That measurement is why"
                  % (100.0 * len(split_bad) / len(corpus)))
            print("        v0.2 section 4 mandates STRICT.")
        if split_bad and mandated:
            rc = 1
            print("     -> STRICT was supposed to close this and did not")

    # -- the splitlines check as a hard gate on STRICT -----------------------
    s_fails, s_split, _ = results["STRICT"]
    print()
    print("MANDATORY: every escaped frame is ONE line under str.splitlines()")
    print("  STRICT violations : %d   %s"
          % (len(s_split), "PASS" if not s_split else "FAIL"))
    if s_split:
        rc = 1
        for i in s_split[:5]:
            print("     idx %d: %r" % (i, corpus[i][:40]))

    # -- invalid UTF-8, now on a frame that CARRIES the mark -----------------
    print()
    print("invalid UTF-8: escaped per byte as \\xNN, never replaced (section 0 forbids")
    print("               editing the world, and U+FFFD is an edit), on a frame whose")
    print("               f sets bit 0, badenc -- amendment items 8 and 9")
    bad_ok = True
    prev = GENESIS
    for raw in BAD_BYTES:
        enc, badenc = esc_bytes(raw)
        if not badenc:
            print("  %-24s NOT MARKED badenc -- FAIL" % repr(raw))
            bad_ok = False
            rc = 1
            continue
        fields = ["1700000000000000000", "venue-a", "mail-bo", "world",
                  "0", str(F_BADENC | F_SYNTHETIC_REV), enc]
        line, h = encode_pre(fields, prev)
        try:
            got = decode_frame(line, prev_hex=prev)
            back = unesc_to_bytes(got["escaped"][6], badenc=bool(got["f"] & F_BADENC))
            trip = (back == raw)
        except ValueError as e:
            got, trip = {"f": -1}, False
            print("      decode raised: %s" % e)
        print("  %-24s -> %-34s f=%d(%s) roundtrip=%s"
              % (repr(raw), repr(enc), got["f"], flag_names(got["f"]), trip))
        if not trip:
            bad_ok = False
            rc = 1
        prev = h
    print("  invalid-UTF-8 handling: %s" % ("PASS" if bad_ok else "FAIL"))

    # A code point in 0x80..0xff is NOT a raw byte, and must survive with the
    # badenc bit CLEAR. This is the other half of item 9.
    line, _h = encode_frame(1, "venue-a", "mail-bo", "commit", 0, 0,
                            "caf\u00e9 \u00fcber", GENESIS)
    got = decode_frame(line, prev_hex=GENESIS)
    ok_cp = (got["text"] == "caf\u00e9 \u00fcber" and got["f"] == 0)
    print("  U+00E9/U+00FC as CODE POINTS on a frame with badenc clear : %s"
          % ("PASS -- written as UTF-8, never as \\xNN" if ok_cp else "FAIL"))
    if not ok_cp:
        rc = 1

    # -- the caps, amendment item 14 -----------------------------------------
    print()
    print("field caps (amendment item 14, applied to the ENCODED field)")
    print("  venue / lane / grain cap : %d bytes" % FIELD_CAP)
    print("  text cap                 : the header's frame_cap")
    cap_fails = 0
    for name, idx, val in (("venue", 1, "v" * (FIELD_CAP + 1)),
                           ("lane", 2, "mail-" + "x" * FIELD_CAP),
                           ("grain", 3, "commit" * 20)):
        fields = ["1", "venue-a", "mail-bo", "commit", "0", "0", "text"]
        fields[idx] = val
        try:
            encode_pre(fields, GENESIS)
            print("  over-cap %-6s : ACCEPTED -- FAIL" % name)
            cap_fails += 1
        except ValueError as e:
            print("  over-cap %-6s : refused (%s)   PASS" % (name, e))
    if cap_fails:
        rc = 1

    small_cap = 64
    over = 0
    boundary_bad = 0
    trunc_bit_bad = 0
    for s in corpus[:2000]:
        enc, dropped = cap_encoded(s, small_cap)
        f = F_TRUNCATED if dropped else 0
        if len(enc.encode("utf-8")) > small_cap:
            over += 1
        if (dropped > 0) != bool(f & F_TRUNCATED):
            trunc_bit_bad += 1
        try:
            if not s.startswith(unesc(enc)):
                boundary_bad += 1
        except ValueError:
            boundary_bad += 1
    print("  with a header frame_cap of %d, over 2000 corpus strings:" % small_cap)
    print("    encoded text fields over the cap : %d   %s"
          % (over, "PASS" if over == 0 else "FAIL"))
    print("    capped text decodes to a prefix of the source : %d bad   %s"
          % (boundary_bad, "PASS" if boundary_bad == 0 else "FAIL"))
    print("    every truncation sets f bit 1, truncated      : %d bad   %s"
          % (trunc_bit_bad, "PASS" if trunc_bit_bad == 0 else "FAIL"))
    if over or boundary_bad or trunc_bit_bad:
        rc = 1
    print("  a line therefore has a bound: %d bytes at frame_cap %d"
          % (line_bound(small_cap), small_cap))
    print("    = 20 t_mono_ns + 3x%d venue/lane/grain + 20 rev + 3 f + %d text"
          % (FIELD_CAP, small_cap))
    print("      + 64 h + %d tabs" % (NFIELDS - 1))

    # -- the planted lies must be caught ------------------------------------
    print()
    print("planted lies -- each MUST be caught")
    print("-" * 78)
    lies = [
        (esc_drop_cr, "LIE 1  encoder drops carriage returns"),
        (esc_no_backslash, "LIE 2  encoder does not escape the backslash"),
        (esc_wrong_order, "LIE 3  encoder escapes TAB before the backslash"),
    ]
    for esc, label in lies:
        hit = catch_encoder_lie(corpus, esc)
        if hit is None:
            print("  %-52s NOT CAUGHT  <-- the test is blind" % label)
            rc = 1
        else:
            idx, s, why = hit
            print("  %-52s caught @ idx %-5d %s" % (label, idx, why))
            print("       input %r" % (s[:40],))

    hit = catch_decoder_lie(corpus)
    label = "LIE 4  decoder passes unknown escapes through"
    if hit is None:
        print("  %-52s NOT CAUGHT  <-- the test is blind" % label)
        rc = 1
    else:
        idx, s, why = hit
        print("  %-52s caught @ idx %-5d %s" % (label, idx, why))

    hit5 = catch_badenc_lie()
    label = "LIE 5  decoder accepts \\xNN > 0x7F with badenc clear"
    if hit5 is None:
        print("  %-52s NOT CAUGHT  <-- the test is blind" % label)
        rc = 1
    else:
        raw, enc, why = hit5
        print("  %-52s caught" % label)
        print("       frame text %r  f=0 (badenc CLEAR)" % (enc[:32],))
        print("       source bytes %r" % (raw,))
        print("       %s" % why)

    # A concrete demonstration of LIE 2's ambiguity, spelled out.
    print()
    print("why the backslash must be escaped first, concretely:")
    src = "\\t"                       # two characters: backslash, t
    print("   text            = %r   (%d chars)" % (src, len(src)))
    print("   LIE 2 encodes   = %r" % esc_no_backslash(src))
    print("   strict decode   = %r   <- a TAB appeared out of nowhere"
          % unesc(esc_no_backslash(src)))
    print("   STRICT encodes  = %r" % esc_strict(src))
    print("   strict decode   = %r   <- identity" % unesc(esc_strict(src)))

    # -- what Amendment 1 settled, and what it did not -----------------------
    print()
    print("Amendment 1 settled, and this run now encodes")
    print("-" * 78)
    print("  item 8   the badenc mark has a home: `f`, bit 0, on the frame itself.")
    print("  item 9   \\xNN <= 0x7F is a code point; >= 0x80 is a raw byte and is")
    print("           legal only when bit 0 of f is set. LIE 5 is that rule's test.")
    print("  item 10  u64le(len) is the body: fields 1-7 with their tabs, escaped,")
    print("           excluding the tab before h, h itself, and the LF.")
    print("  item 11  the spool chain is personalized %r." % PERSON_SPOOL.decode())
    print("  item 14  venue/lane/grain at %d encoded bytes, text at the header cap,"
          % FIELD_CAP)
    print("           so the line is bounded.")
    print()
    print("still open for an implementer")
    print("-" * 78)
    print("  a. `f`'s wire form is not pinned. This decoder demands canonical")
    print("     decimal with no sign and no leading zero; \"007\" and \"+7\" are")
    print("     refused. Two encoders could disagree and change the hash.")
    print("  b. Unknown bits of `f` have no stated disposition. Bits 3+ are")
    print("     refused here, by analogy with an unknown grain being a refused")
    print("     frame -- but reserved-and-ignored is equally readable, and the two")
    print("     differ the day a lane emits a bit this build has never seen.")
    print("  c. Who sets `truncated`? The trunc row already carries the dropped")
    print("     count (section 4); bit 1 now duplicates its existence. Nothing")
    print("     says the two must agree, or which is authoritative.")

    print()
    print("=" * 78)
    print("RESULT: %s" % ("ALL CHECKS PASS" if rc == 0 else "FAILURES ABOVE"))
    return rc


if __name__ == "__main__":
    sys.exit(main())
