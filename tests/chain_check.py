"""chain_check.py -- FACTOR tests, BLUEPRINT_v0.2.md sections 4 and 12 as amended.

Implements and exercises, against generated files on disk, the chains v0.2 pins
and Amendment 1 (2026-09-08) settles, then proves each verifier has teeth by
running planted lies past it.

  (a) the TAPE row chain, section 12 -- KEYED
        h       = BLAKE2b-256-keyed( K_tape ; prev_hex || u64le(len(body)) || body )
        K_tape  = BLAKE2b-256( machine_secret, person = "FCTR-tape-v1" )
        prev    = the previous row's h as 64 lowercase hex characters
        genesis = 64 zeros
        body    = the canonical JSON of the row's fields with prev and h removed,
                  and with ms removed (amendment item 16: ms is a key on the row
                  object that the hashed body excludes; it is not a sidecar)

  (a5) the FINGERPRINT chain, amendment item 19 -- UNKEYED, personalized
        At every segment close and every 4,096 rows the kernel writes a
        `fingerprint` row carrying the keyed head, the segment number and the
        row's index on the UNCOMPACTED tape. The fingerprints form their own
        chain: fp_h = BLAKE2b-256( fp_prev || u64le(len(fp_body)) || fp_body ),
        person = "FCTR-fprint-v1", and Amendment 4 item 9 PINS the body:
        fp_body = canon({head, seg, row_orig}). `verify --chain-only` walks that
        chain and its agreement with the witness's copy WITHOUT the tape key,
        and never recomputes a keyed h -- which this file proves with a call
        counter, not with a comment. Amendment 4 item 13 gives the witness's
        copy a form: one canonical-JSON line per fingerprint, carrying the
        console's signature, appended to a store that cannot rewrite.

  (a6) COMPACTION, amendment item 20 -- a signed `tombstone` row replaces the
        removed span, carrying the span's first `prev`, its last `h`, the row
        count and, per Amendment 4 item 12, the heads of the two bracketing
        fingerprints, all under one operator signature. The verifier accepts it
        as the link, so a compacted tape still produces the SAME head, and
        Amendment 4 item 10 has the compactor append a fingerprint AT ONCE,
        before the tape is publishable.

  (a6b) WHICH SPANS MAY BE COMPACTED, Amendment 3 item 2 and Amendment 4 item
        11 -- a tombstone may replace only rows STRICTLY BETWEEN two
        fingerprints, never a fingerprint, and never another tombstone.
        `factor compact` refuses anything else with the typed
        CompactionRefused, before it writes a byte. After a lawful compaction
        BOTH chains verify -- the keyed tape chain reaches the same head, and
        the unkeyed fingerprint chain is untouched, body for body -- so a
        keyless verifier cannot mistake a lawful compaction for a forgery.

  AMENDMENT 4 ITEM 8 -- the VERIFIER holds these rules, not only the writer.
        `compaction_rules` is one function, called by `verify_tape` and by
        `verify_chain_only`, holding the bracket, the fingerprint chain, the
        bracketing heads, the tombstone's signature and item 9's position
        reconstruction. Four of the seven planted lies here are compaction lies
        and every one of them is caught by BOTH verifiers, because the one
        adversary compaction has is a holder of the operator key -- who is the
        person running the keyed verifier.

  (b) the SPOOL self-chain, section 4 -- UNKEYED, personalized "FCTR-spool-v1"
        body    = fields 1 to 7 (t_mono_ns venue lane grain rev f text), escaped,
                  with their tabs -- the frame gained an eighth field, amendment
                  item 8, and `f` is its flags
        genesis = the header line's own h, whose prev is 64 zeros

  (c) the CURSOR, section 4 as amended item 12: (generation, offset, h,
      window_len). The window bounds a backwards re-read that recovers the frame
      at the cursor and its predecessor, so the chain value is recomputed in
      O(window) rather than O(file). A window shorter than two lines is refused.

Exit 0 : every chain verifies, every planted lie is caught, every structural
         rule of section 12 and Amendment 1 holds.
Exit 1 : anything else.
"""

import hashlib
import json
import os
import shutil
import sys
import tempfile

GENESIS = "0" * 64
CHAIN_FIELDS = ("prev", "h")
# Amendment item 16: ms is a key on the row object that the hashed body
# excludes. It is written on the line and excluded from the preimage.
EXCLUDED_FROM_BODY = ("prev", "h", "ms")

MACHINE_SECRET = bytes(range(32))       # a fixture, not a real secret
BLAKE2B_PERSON_MAX = 16                 # hashlib's limit, and BLAKE2b's
JS_SAFE_INT = 2 ** 53 - 1

# Amendment item 15: the personalization strings are at most sixteen bytes and
# PINNED. The v0.2 template that produced a seventeen-byte string is withdrawn.
PERSON = {
    "tape":    b"FCTR-tape-v1",
    "dossier": b"FCTR-dossier-v1",
    "ledger":  b"FCTR-ledger-v1",
    "ckpt":    b"FCTR-ckpt-v1",
    "spool":   b"FCTR-spool-v1",
    "fprint":  b"FCTR-fprint-v1",
}
CHAIN_ORDER = ("tape", "dossier", "ledger", "ckpt", "spool", "fprint")

# Amendment item 19's cadence, and item 22's segment bound.
FPRINT_EVERY = 4096
SEGMENT_BOUND = 64 * 1024 * 1024        # 64 MiB, checked BEFORE the append
FPRINT_RESERVE = 384                    # room kept for the closing fingerprint

# Every keyed recomputation is counted, so `--chain-only` can PROVE it did none.
KEYED_CALLS = [0]


def u64le(n):
    return int(n).to_bytes(8, "little", signed=False)


def chain_key(chain_name, secret=MACHINE_SECRET):
    """K_chain = BLAKE2b-256(machine_secret, person = the pinned string)."""
    return hashlib.blake2b(secret, digest_size=32,
                           person=PERSON[chain_name]).digest()


def keyed_h(key, prev_hex, body):
    KEYED_CALLS[0] += 1
    return hashlib.blake2b(prev_hex.encode("ascii") + u64le(len(body)) + body,
                           digest_size=32, key=key).hexdigest()


def unkeyed_h(prev_hex, body, chain_name):
    """Unkeyed but PERSONALIZED, so a row lifted from one unkeyed chain does not
    verify in another (amendment item 11)."""
    return hashlib.blake2b(prev_hex.encode("ascii") + u64le(len(body)) + body,
                           digest_size=32, person=PERSON[chain_name]).hexdigest()


KEYS = {nm: chain_key(nm) for nm in CHAIN_ORDER}
K_TAPE = KEYS["tape"]

# The operator's key, for the signed tombstone of amendment item 20. A real
# tombstone carries the operator's signature; what this fixture must prove is
# that the signature covers the span's endpoints, the row count and -- Amendment
# 4 item 12 -- the heads of the two bracketing fingerprints, so the operator
# attests that the span was LAWFUL and not merely that it was removed.
K_OPERATOR = hashlib.blake2b(b"operator-key-fixture", digest_size=32).digest()

# The console's key. Amendment 4 item 13: the witness's copy is one line per
# fingerprint -- the fingerprint row's canonical JSON with the console's
# signature over it -- so a witness holds something it can be held to, and a
# store that can append and cannot rewrite is enough to be a witness.
K_CONSOLE = hashlib.blake2b(b"console-key-fixture", digest_size=32).digest()


def op_sign(body):
    return hashlib.blake2b(body, digest_size=32, key=K_OPERATOR).hexdigest()


def console_sign(body):
    return hashlib.blake2b(body, digest_size=32, key=K_CONSOLE).hexdigest()


# ------------------------------------------------------- canonical JSON, sec 12

class NonCanonical(Exception):
    pass


# Amendment item 17: "64-bit fields as strings" is decided by DECLARED WIDTH.
# Every field declared 64-bit -- amount_fix, t_mono_ns, rev, and every id -- is a
# decimal string; int16 margins and small counters are numbers. This table is
# that rule made mechanical: the checker reads the width, not a hand-kept list.
DECLARED_WIDTH = {
    # 64-bit -> decimal string
    "t_mono_ns": "uint64", "rev": "uint64", "src_rev": "uint64",
    "judged_rev": "uint64", "id": "uint64", "party": "uint64",
    "blocked_by": "uint64", "batch": "uint64", "opened_ns": "uint64",
    "due_ns": "uint64", "horizon_ns": "uint64", "release_ns": "uint64",
    "amount_fix": "int64", "offset": "uint64", "generation": "uint64",
    # Amendment 4 item 9 renames the fingerprint's `row` to `row_orig`: the
    # row's index on the UNCOMPACTED tape. Compaction never renumbers.
    "seg": "uint64", "row_orig": "uint64", "count": "uint64",
    # narrower -> JSON number
    "m_hand": "int16", "m_check": "int16", "m_guard": "int16",
    "n_wit": "uint16", "n_wait": "uint16", "tie": "uint16",
    "flags": "uint16", "pos": "uint16", "f": "uint16",
    "cls": "uint32", "band": "uint32", "seat": "uint32", "unit": "uint32",
    "frame_cap": "uint32", "lag_ms": "uint32", "rung": "uint8",
}
WIDE = ("uint64", "int64")
WIDTH_RANGE = {
    "int16": (-32768, 32767), "uint16": (0, 65535),
    "uint32": (0, 4294967295), "uint8": (0, 255),
}

ROW_KEYS = {
    "verb": ("k", "ms", "t_mono_ns", "id", "judged_rev", "verb", "reason",
             "flags", "band", "rung", "m_hand", "m_check", "m_guard",
             "batch", "pos", "prev", "h"),
    "frame": ("k", "ms", "t_mono_ns", "lane", "generation", "offset",
              "frame_h", "prev", "h"),
    # Amendment item 19. `head` is the keyed head this fingerprint attests --
    # the h of the row before it -- so a keyless verifier can compare it with
    # the witness's copy without recomputing anything. Amendment 4 item 9 pins
    # the hashed body as {head, seg, row_orig} and pins what `row_orig` means.
    "fingerprint": ("k", "ms", "head", "seg", "row_orig", "fp_prev", "fp_h",
                    "prev", "h"),
    # Amendment item 20, with Amendment 4 item 12's two bracketing heads. They
    # are ON the row because the signature covers them and a verifier has to be
    # able to recompute the signed body from the row it is handed.
    "tombstone": ("k", "ms", "span_prev", "span_h", "count", "fp_before",
                  "fp_after", "sig", "prev", "h"),
}

# Amendment 4 item 9: "The fingerprint body is pinned: {head, seg, row_orig},
# where row_orig is the row's index on the uncompacted tape." O8's still-open
# item (a) is closed by this line.
FP_BODY_KEYS = ("head", "row_orig", "seg")

# Amendment 4 item 12: "The operator's signature on a tombstone covers the
# span's first prev, its last h, its count, and the heads of the two bracketing
# fingerprints." O8's still-open item (h) is closed by this line -- the operator
# now attests that the span was lawful, not only that it was removed.
TOMB_SIGNED_KEYS = ("count", "fp_after", "fp_before", "span_h", "span_prev")


def _canonical_decimal(s, signed):
    if not isinstance(s, str) or not s:
        return False
    body = s[1:] if (signed and s[0] == "-") else s
    if not body.isdigit():
        return False
    return not (len(body) > 1 and body[0] == "0")


def _check_canonical(obj, path="$"):
    if isinstance(obj, bool):
        return
    if isinstance(obj, float):
        raise NonCanonical(
            "bare float at %s: %r -- section 12 forbids it; margins and amounts "
            "are fixed-point integers" % (path, obj))
    if isinstance(obj, int):
        if abs(obj) > JS_SAFE_INT:
            raise NonCanonical(
                "bare integer at %s exceeds 2**53-1: %d -- section 12 requires "
                "every 64-bit integer as a decimal string" % (path, obj))
        return
    if isinstance(obj, dict):
        for k, v in obj.items():
            if not isinstance(k, str):
                raise NonCanonical("non-string key at %s: %r" % (path, k))
            w = DECLARED_WIDTH.get(k)
            here = path + "." + k
            if w in WIDE:
                if not _canonical_decimal(v, w == "int64"):
                    raise NonCanonical(
                        "%s is declared %s and must be a canonical decimal "
                        "string, got %r" % (here, w, v))
            elif w is not None:
                if not isinstance(v, int) or isinstance(v, bool):
                    raise NonCanonical(
                        "%s is declared %s and must be a JSON number, got %r"
                        % (here, w, v))
                lo, hi = WIDTH_RANGE[w]
                if not lo <= v <= hi:
                    raise NonCanonical("%s is declared %s and %d does not fit"
                                       % (here, w, v))
            _check_canonical(v, here)
    elif isinstance(obj, (list, tuple)):
        for i, v in enumerate(obj):
            _check_canonical(v, "%s[%d]" % (path, i))


def canon(obj):
    """Canonical JSON bytes, section 12."""
    _check_canonical(obj)
    return json.dumps(obj, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False, allow_nan=False).encode("utf-8")


def validate_keys(row):
    """Section 12: unknown keys are fatal, not ignored."""
    kind = row.get("k")
    allowed = ROW_KEYS.get(kind)
    if allowed is None:
        raise NonCanonical("unknown row kind %r" % kind)
    extra = [k for k in row if k not in allowed]
    if extra:
        raise NonCanonical("unknown key(s) %s on a %r row -- fatal"
                           % (", ".join(sorted(extra)), kind))


def row_body(row):
    """The bytes the row's keyed hash covers: the row minus prev, h and ms."""
    return canon({k: v for k, v in row.items() if k not in EXCLUDED_FROM_BODY})


def fp_body(row):
    """The bytes the FINGERPRINT chain covers, pinned by Amendment 4 item 9:
    {head, seg, row_orig}. It excludes ms, prev, h, fp_prev and fp_h, so it is
    computable by a verifier that holds no key at all -- and it holds nothing a
    lawful compaction moves, which is why item 2's promise that both chains
    verify after a compaction is true rather than lucky. A body that covered,
    say, a position on the compacted tape would break under a lawful
    compaction and item 2 would be false."""
    return canon({k: row[k] for k in FP_BODY_KEYS})


def witness_line(row):
    """AMENDMENT 4 ITEM 13. The witness's copy is one line per fingerprint: the
    fingerprint row's canonical JSON, with the console's signature over exactly
    those bytes, separated by a tab. Append-only is the only property the store
    needs -- a transparency log, a second machine, the operator's device.

    The signature is what makes the copy evidence: without it a witness that
    can append can also append a line nobody published, and `--chain-only`'s
    agreement check would be comparing a tape against an unsigned assertion.
    """
    js = canon(row)
    return js + b"\t" + console_sign(js).encode("ascii") + b"\n"


def read_witness(path):
    """Parse the witness's copy. Returns (entries, errors), where an entry is
    the fingerprint row as the console published it. A line whose console
    signature does not cover its bytes is not an entry: it is an error."""
    entries = []
    errors = []
    with open(path, "rb") as f:
        data = f.read()
    for i, line in enumerate(data.split(b"\n")):
        if not line:
            continue
        cut = line.rfind(b"\t")
        if cut < 0:
            errors.append("witness line %d has no signature field" % i)
            continue
        js, sig = line[:cut], line[cut + 1:].decode("ascii", "replace")
        if console_sign(js) != sig:
            errors.append("witness line %d: the console's signature does not "
                          "cover it (sig=%s want=%s) -- the witness holds a "
                          "line the console never published"
                          % (i, sig[:16], console_sign(js)[:16]))
            continue
        try:
            entries.append(json.loads(js.decode("utf-8")))
        except Exception as e:                                   # noqa: BLE001
            errors.append("witness line %d: undecodable JSON (%s)" % (i, e))
    return entries, errors


def seal(row, prev_hex, key=K_TAPE):
    body = row_body(row)
    out = dict(row)
    out["prev"] = prev_hex
    out["h"] = keyed_h(key, prev_hex, body)
    return out


def row_line(row):
    return json.dumps(row, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False).encode("utf-8") + b"\n"


# ------------------------------------------------------------- the plan hash

PLAN_FIELDS = ("id", "judged_rev", "verb", "reason", "flags", "band", "rung",
               "m_hand", "m_check", "m_guard", "batch", "pos")


def plan_hash(rows):
    """Section 12: the plan hash covers, per verb row, (id, judged_rev, verb,
    reason, flags, band, rung, the quantized margins, batch id, position) and
    excludes ms, prev and h."""
    hh = hashlib.blake2b(digest_size=32, person=PERSON["ckpt"])
    for r in rows:
        if r.get("k") != "verb":
            continue
        hh.update(canon({f: r[f] for f in PLAN_FIELDS if f in r}))
    return hh.hexdigest()


# ------------------------------------------------------------ the tape writer

def seg_name(i):
    return "seg-%06d.jsonl" % i


def build_tape(dirpath, n_rows, seg_bytes=1600, ms_base=1000,
               fprint_every=FPRINT_EVERY, witness_path=None):
    """Write n_rows across monotone, zero-padded segments, with a `fingerprint`
    row at every segment close and every `fprint_every` rows.

    Returns (paths, head, rows, fingerprints)."""
    os.makedirs(dirpath, exist_ok=True)
    state = {"prev": GENESIS, "fp_prev": GENESIS, "seg_no": 1,
             "written": 0, "row_index": 0, "since_fp": 0}
    paths = [os.path.join(dirpath, seg_name(1))]
    manifest = []
    fh = open(paths[-1], "wb")
    first_prev = GENESIS
    rows = []
    fps = []
    witness = []

    def append(raw):
        validate_keys(dict(raw, prev="", h=""))
        row = seal(raw, state["prev"])
        line = row_line(row)
        fh.write(line)
        state["written"] += len(line)
        state["prev"] = row["h"]
        state["row_index"] += 1
        state["since_fp"] += 1
        rows.append(row)
        return row

    def append_fingerprint():
        raw = {"k": "fingerprint",
               "ms": ms_base + state["row_index"] * 7 + 3,
               "head": state["prev"],                 # the keyed head attested
               "seg": str(state["seg_no"]),
               # Amendment 4 item 9: the index on the UNCOMPACTED tape. On a
               # tape that has never been compacted this is also the row's
               # position; a compaction moves the position and never the value.
               "row_orig": str(state["row_index"])}
        raw["fp_prev"] = state["fp_prev"]
        raw["fp_h"] = unkeyed_h(state["fp_prev"], fp_body(raw), "fprint")
        state["fp_prev"] = raw["fp_h"]
        row = append(raw)
        state["since_fp"] = 0
        fps.append(row)
        witness.append(row)
        return row

    for i in range(n_rows):
        raw = {
            "k": "verb",
            "ms": ms_base + i * 7,                    # outside the hashed body
            "t_mono_ns": str(1700000000000000000 + i * 1000),
            "id": "%d" % (0xF00D0000 + i),
            "judged_rev": str(100 + i),
            "verb": ["HOLD", "LOOK", "DRAFT"][i % 3],
            "reason": "ok",
            "flags": (i * 3) % 4096,
            "band": i % 7,
            "rung": i % 5,
            "m_hand": (i * 37) % 1000 - 500,          # quantized, never float
            "m_check": (i * 11) % 800 - 400,
            "m_guard": (i * 5) % 600 - 300,
            "batch": str(i // 4),                     # an id -> a decimal string
            "pos": i % 4,
        }
        probe = len(row_line(seal(raw, state["prev"])))
        # Section 12 / amendment item 22: the bound is checked BEFORE the append,
        # with room kept for the fingerprint that closes the segment.
        if (state["written"] + probe + FPRINT_RESERVE > seg_bytes
                and state["written"] > 0):
            append_fingerprint()                      # a fingerprint per close
            fh.close()
            manifest.append({"seg": state["seg_no"], "first_prev": first_prev,
                             "head": state["prev"]})
            state["seg_no"] += 1
            paths.append(os.path.join(dirpath, seg_name(state["seg_no"])))
            fh = open(paths[-1], "wb")
            state["written"] = 0
            first_prev = state["prev"]
        append(raw)
        if state["since_fp"] >= fprint_every:
            append_fingerprint()

    append_fingerprint()                              # the final segment close
    fh.close()
    manifest.append({"seg": state["seg_no"], "first_prev": first_prev,
                     "head": state["prev"]})
    with open(os.path.join(dirpath, "manifest.json"), "w", encoding="utf-8") as m:
        json.dump({"segments": manifest, "head": state["prev"]}, m,
                  sort_keys=True, separators=(",", ":"))
    if witness_path:
        # Amendment 4 item 13: one canonical-JSON line per fingerprint, each
        # carrying the console's signature. Written append-only, which is the
        # only capability item 13 asks a witness for.
        with open(witness_path, "wb") as w:
            for fp_row in witness:
                w.write(witness_line(fp_row))
    return paths, state["prev"], rows, fps


# ---------------------------------------------------------- the tape verifier

def segment_files(dirpath):
    """Section 12: filenames are zero-padded and monotone, and `factor verify`
    walks them in filename order. Returns (names, complaints)."""
    names = sorted(p for p in os.listdir(dirpath)
                   if p.startswith("seg-") and p.endswith(".jsonl"))
    complaints = []
    nums = []
    for nm in names:
        stem = nm[len("seg-"):-len(".jsonl")]
        if not stem.isdigit():
            complaints.append("%s: segment number is not decimal" % nm)
            continue
        if len(stem) != 6:
            complaints.append("%s: segment number is not zero-padded to 6, so "
                              "filename order stops matching numeric order" % nm)
        nums.append(int(stem))
    if nums != sorted(nums):
        complaints.append("filename order %s is not numeric order %s"
                          % (nums, sorted(nums)))
    if nums and nums != list(range(nums[0], nums[0] + len(nums))):
        complaints.append("segment numbers are not contiguous: %s" % nums)
    return names, complaints


def _tail_reasons(raw, no_trailing_lf):
    """Section 12's three torn cases, all tested against the last row.

    Amendment item 18: a valid last row whose hash fails is indistinguishable
    from a forged tail an attacker wants dropped. The verifier accepts the
    earlier head either way, and that is why the head has two witnesses. A
    broken LINK in the last position is a forgery, not a tear, and is fatal.
    """
    reasons = []
    if no_trailing_lf:
        reasons.append("no trailing LF")
    try:
        row = json.loads(raw.decode("utf-8"))
    except Exception as e:                                   # noqa: BLE001
        reasons.append("undecodable JSON (%s, %d bytes)"
                       % (type(e).__name__, len(raw)))
        return reasons
    if "prev" not in row or "h" not in row:
        reasons.append("row missing prev/h")
        return reasons
    try:
        body = row_body(row)
    except NonCanonical as e:
        reasons.append("non-canonical body (%s)" % e)
        return reasons
    if keyed_h(K_TAPE, row["prev"], body) != row["h"]:
        reasons.append("hash of a partially written row")
    return reasons


# -------- Amendment 4 items 8 to 12: the rules BOTH verifiers hold, once
# The verifier-side reasons, as constants, so a test asserts on a value and not
# on a substring of English. They are tagged into the message in brackets.
REASON_UNBRACKETED = "unbracketed"
REASON_UNFINGERPRINTED = "unfingerprinted-tombstone"
REASON_REMOVED_FP = "removed-fingerprint"
REASON_BRACKET_HEAD = "bracket-head-mismatch"
REASON_TOMB_SIG = "tombstone-signature"
REASON_ROW_ORIG = "row-orig-mismatch"


def compaction_rules(fps, tombs):
    """AMENDMENT 4 ITEMS 8 TO 12 -- everything a tape carrying a tombstone must
    satisfy, in ONE function, called by `factor verify` AND by
    `factor verify --chain-only`.

    Item 8: "`factor verify` and `factor verify --chain-only` both refuse a tape
    whose tombstone is not bracketed by a fingerprint on each side, or whose
    span removed a fingerprint. The writer's refusal is hygiene; the verifier's
    refusal is the law, because the one adversary compaction has is a holder of
    the operator key." A rule only the writer holds protects nothing against the
    writer, and O8 left it in `--chain-only` alone. It lives here now, and the
    two verifiers cannot drift apart because there is only one copy of it.

    Nothing here needs the TAPE key. Fingerprint rows, tombstone rows, `count`
    and row order are readable without it, and the operator's and console's
    signatures are checked with keys a keyless verifier already holds -- which
    is why the same function serves both paths, and it is measured, because the
    caller counts keyed recomputations across the call.

    `fps` and `tombs` are lists of (position, segment name, row); position is
    counted over the whole tape in filename order.
    """
    errors = []

    # (1) THE FINGERPRINT CHAIN, item 8's "whose span removed a fingerprint".
    # A span that removes a fingerprint leaves the next fingerprint's `fp_prev`
    # naming an `fp_h` that is no longer on the tape. The tombstone repairs the
    # KEYED chain, so the head does not move and the keyed side sees nothing --
    # unless the keyed side also walks this chain, which is what item 8 says it
    # must.
    fp_prev = GENESIS
    for pos, name, row in fps:
        try:
            want = unkeyed_h(row["fp_prev"], fp_body(row), "fprint")
        except (KeyError, NonCanonical) as e:
            errors.append("%s: unusable fingerprint row at %d: %s"
                          % (name, pos, e))
            continue
        if want != row["fp_h"]:
            errors.append("%s: fingerprint SELF hash mismatch (fp_h=%s want=%s)"
                          % (name, row["fp_h"][:16], want[:16]))
        if row["fp_prev"] != fp_prev:
            errors.append("%s: fingerprint LINK broken [%s] (fp_prev=%s "
                          "expected=%s)" % (name, REASON_REMOVED_FP,
                                            row["fp_prev"][:16], fp_prev[:16]))
        fp_prev = row["fp_h"]

    # (2) EVERY TOMBSTONE: bracketed on each side, its bracketing heads as the
    # operator signed them, and the signature over all five fields.
    for pos, name, row in tombs:
        before = [x for x in fps if x[0] < pos]
        after = [x for x in fps if x[0] > pos]
        if not before:
            # Amendment 3 item 2 / Amendment 4 item 8. The rows removed here
            # were never inside a bracket the witness holds both ends of, so no
            # external observer can bound what was taken.
            errors.append("%s: tombstone at row %d has no fingerprint BEFORE "
                          "it [%s] -- the span it replaces is outside every "
                          "attested bracket" % (name, pos, REASON_UNBRACKETED))
        if not after:
            # Amendment 4 item 10. "A compaction is followed by a fingerprint
            # at once, before the tape is published... A tape is never
            # published with an unfingerprinted tombstone." This is that rule
            # in the form a verifier can hold: a tombstone the tape never
            # fingerprinted.
            errors.append("%s: tombstone at row %d has no fingerprint AFTER it "
                          "[%s] -- the tape was published carrying an "
                          "unfingerprinted tombstone"
                          % (name, pos, REASON_UNFINGERPRINTED))
        if before and after:
            # Amendment 4 item 12. The operator signed two heads; they must be
            # the heads the bracketing fingerprints actually attest, or the
            # operator has attested a bracket that is not the one the span sat
            # in -- a signature over the wrong span, validly signed.
            want_b = before[-1][2].get("head")
            want_a = after[0][2].get("head")
            if row.get("fp_before") != want_b:
                errors.append("%s: tombstone at row %d names fp_before %s but "
                              "the fingerprint bracketing it attests %s [%s]"
                              % (name, pos, str(row.get("fp_before"))[:16],
                                 str(want_b)[:16], REASON_BRACKET_HEAD))
            if row.get("fp_after") != want_a:
                errors.append("%s: tombstone at row %d names fp_after %s but "
                              "the fingerprint bracketing it attests %s [%s]"
                              % (name, pos, str(row.get("fp_after"))[:16],
                                 str(want_a)[:16], REASON_BRACKET_HEAD))
        try:
            signed = canon({k: row[k] for k in TOMB_SIGNED_KEYS})
        except (KeyError, NonCanonical) as e:
            errors.append("%s: tombstone at row %d cannot be checked against "
                          "its signature: %s [%s]"
                          % (name, pos, e, REASON_TOMB_SIG))
        else:
            if op_sign(signed) != row.get("sig"):
                errors.append("%s row %d: tombstone signature does not cover "
                              "(span_prev, span_h, count, fp_before, fp_after) "
                              "-- refused [%s]" % (name, pos, REASON_TOMB_SIG))

    # (3) AMENDMENT 4 ITEM 9's reconstruction. `row_orig` is the index on the
    # UNCOMPACTED tape and compaction never renumbers, so a verifier recovers
    # the position by subtracting the counts of the tombstones before it: each
    # replaces `count` rows with one. A lawful compaction therefore changes
    # nothing a fingerprint attests, and this arithmetic is what makes that
    # checkable rather than merely asserted.
    for pos, name, row in fps:
        removed = 0
        bad = False
        for tp, _tn, trow in tombs:
            if tp >= pos:
                continue
            try:
                removed += int(trow["count"]) - 1
            except (KeyError, TypeError, ValueError):
                bad = True
        if bad:
            continue
        try:
            orig = int(row["row_orig"])
        except (KeyError, TypeError, ValueError):
            errors.append("%s: fingerprint at %d has no usable row_orig"
                          % (name, pos))
            continue
        if orig - removed != pos:
            errors.append("%s: fingerprint at row %d attests row_orig %d and "
                          "%d row(s) were compacted before it, so it should "
                          "sit at %d [%s]"
                          % (name, pos, orig, removed, orig - removed,
                             REASON_ROW_ORIG))
    return errors


def verify_tape(dirpath, link_check=True, use_manifest=False):
    """Walk every segment in filename order. Returns a report; never raises on data.

    Section 12's torn-row rule: exactly one row may be torn, and only the last
    row of the last segment. The head is the h of the last row that verifies
    BOTH ways.

    Amendment item 20: a `tombstone` row is accepted AS THE LINK. Its own prev is
    the compacted span's first prev, and the chain continues from its span_h, so
    a compacted tape reproduces the same head as the tape it was compacted from.

    Amendment 4 item 8: the KEYED verifier holds the compaction rules too, not
    only `--chain-only`. It collects the fingerprints and tombstones as it walks
    and hands them to `compaction_rules`, the same function the keyless verifier
    calls. Before Amendment 4 a tape whose tombstone was unbracketed, or whose
    span removed a fingerprint, passed `factor verify` untouched -- and the
    adversary compaction actually has is the holder of the operator key, who is
    exactly the person `factor verify` is run by.
    """
    segs, complaints = segment_files(dirpath)
    errors = list(complaints)
    warns = []
    prev = GENESIS
    head = GENESIS
    n = 0
    torn = []
    tombs = 0
    pos = -1              # position on the tape, across segments
    fp_rows = []          # (position, segment name, row) for compaction_rules
    tomb_rows = []

    manifest_head = None
    if use_manifest:
        mp = os.path.join(dirpath, "manifest.json")
        if os.path.exists(mp):
            manifest_head = json.load(open(mp, encoding="utf-8")).get("head")

    for si, name in enumerate(segs):
        path = os.path.join(dirpath, name)
        data = open(path, "rb").read()
        if len(data) > SEGMENT_BOUND:
            errors.append("%s: %d bytes exceeds the %d-byte segment bound"
                          % (name, len(data), SEGMENT_BOUND))
        last_seg = (si == len(segs) - 1)
        lines = data.split(b"\n")
        no_trailing_lf = lines[-1] != b""
        if no_trailing_lf and not last_seg:
            errors.append("%s: last row has no trailing LF in a NON-final "
                          "segment -- fatal" % name)
        if lines and lines[-1] == b"":
            lines = lines[:-1]

        for li, raw in enumerate(lines):
            is_tail = last_seg and li == len(lines) - 1
            pos += 1          # counted for every line, torn ones included, so
                              # item 9's reconstruction is over real positions

            def tear(why):
                torn.append("%s row %d: %s" % (name, li, why))

            if is_tail:
                reasons = _tail_reasons(raw, no_trailing_lf)
                if reasons:
                    tear("; ".join(reasons))
                    continue

            try:
                row = json.loads(raw.decode("utf-8"))
            except Exception as e:                            # noqa: BLE001
                errors.append("%s row %d: undecodable mid-chain row: %s"
                              % (name, li, e))
                continue

            if "prev" not in row or "h" not in row:
                errors.append("%s row %d: missing prev/h" % (name, li))
                continue

            try:
                validate_keys(row)
            except NonCanonical as e:
                errors.append("%s row %d: %s" % (name, li, e))
                continue

            try:
                body = row_body(row)
            except NonCanonical as e:
                errors.append("%s row %d: non-canonical body: %s" % (name, li, e))
                continue

            want = keyed_h(K_TAPE, row["prev"], body)
            self_ok = (want == row["h"])
            link_ok = (row["prev"] == prev)

            if not self_ok:
                errors.append("%s row %d: SELF hash mismatch (h=%s want=%s)"
                              % (name, li, row["h"][:16], want[:16]))
            if link_check and not link_ok:
                errors.append("%s row %d: LINK broken (prev=%s expected=%s)"
                              % (name, li, row["prev"][:16], prev[:16]))

            # A fingerprint must attest the head it actually follows, or it is
            # a fingerprint of a tape that does not exist (amendment item 19).
            if row["k"] == "fingerprint":
                fp_rows.append((pos, name, row))
                if row["head"] != row["prev"]:
                    errors.append("%s row %d: fingerprint attests head %s but "
                                  "follows %s" % (name, li, row["head"][:16],
                                                  row["prev"][:16]))

            if row["k"] == "tombstone":
                tombs += 1
                tomb_rows.append((pos, name, row))
                if row["span_prev"] != row["prev"]:
                    errors.append("%s row %d: tombstone's span_prev %s is not its "
                                  "own prev %s" % (name, li,
                                                   row["span_prev"][:16],
                                                   row["prev"][:16]))
                # The tombstone IS the link: the chain continues from span_h.
                prev = row["span_h"]
                n += 1
                if self_ok and (link_ok or not link_check):
                    head = row["span_h"]
                continue

            prev = row["h"]
            n += 1
            if self_ok and (link_ok or not link_check):
                head = row["h"]

    if len(torn) > 1:
        errors.append("%d torn rows; section 12 allows exactly one, and only the "
                      "last row of the last segment: %s" % (len(torn), torn))
    for t in torn:
        warns.append("torn row skipped with a warn -- %s" % t)

    if manifest_head is not None and manifest_head != head:
        errors.append("manifest head %s disagrees with the walked head %s"
                      % (manifest_head[:16], head[:16]))

    # Amendment 4 item 8: the same rules the keyless verifier holds, held here.
    errors.extend(compaction_rules(fp_rows, tomb_rows))

    return {"segments": segs, "rows": n, "head": head, "errors": errors,
            "warns": warns, "torn": torn, "tombstones": tombs,
            "fingerprints": len(fp_rows)}


# ------------------------------------------- (a5) verify --chain-only, item 19

def verify_chain_only(dirpath, witness_path=None):
    """Amendment item 19. Verify the fingerprint chain's internal consistency and
    its agreement with the witness's copy, WITHOUT the tape key.

    Nothing here derives K_tape, and nothing calls keyed_h -- the caller checks
    that with KEYED_CALLS, so 'never recomputes a keyed h' is measured. The
    compaction rules come from `compaction_rules`, shared with `verify_tape`
    (Amendment 4 item 8); they need no tape key either, which is why one
    function can serve both and the counter stays at zero.
    """
    segs, complaints = segment_files(dirpath)
    errors = list(complaints)
    fp_prev = GENESIS
    seen = []
    gaps = []
    last_row = 0
    per_seg = {}
    pos = -1                    # position on the tape, across segments
    fp_rows = []                # (position, segment name, row)
    tomb_rows = []
    # The cadence is counted in the rows BETWEEN fingerprints: a fingerprint row
    # occupies an index of its own and is not one of the 4,096 it closes.
    for name in segs:
        for raw in open(os.path.join(dirpath, name), "rb").read().split(b"\n"):
            if not raw:
                continue
            pos += 1
            try:
                row = json.loads(raw.decode("utf-8"))
            except Exception:                                # noqa: BLE001
                continue                                     # torn tail, skipped
            if row.get("k") == "tombstone":
                # A tombstone is keyless-readable, and Amendment 3 item 2 makes
                # its POSITION checkable without the tape key: it must sit
                # strictly between two fingerprints.
                tomb_rows.append((pos, name, row))
                continue
            if row.get("k") != "fingerprint":
                continue
            fp_rows.append((pos, name, row))
            if "fp_h" not in row or "fp_prev" not in row:
                continue
            fp_prev = row["fp_h"]
            try:
                idx = int(row["row_orig"])
            except (KeyError, TypeError, ValueError):
                continue
            gaps.append(idx - last_row - (1 if seen else 0))
            last_row = idx
            per_seg.setdefault(row["seg"], 0)
            per_seg[row["seg"]] += 1
            seen.append(row)

    # Amendment 4 items 8 to 12, the same code `verify_tape` runs.
    errors.extend(compaction_rules(fp_rows, tomb_rows))

    if witness_path and os.path.exists(witness_path):
        # Amendment 4 item 13. The witness's copy is one canonical-JSON line per
        # fingerprint with the console's signature over it, so the comparison is
        # against published, signed rows rather than against a bare list of
        # digests: a witness that can append could otherwise append anything.
        published, werrors = read_witness(witness_path)
        errors.extend("the witness's copy is not usable: %s" % e
                      for e in werrors)
        mine = [canon(r) for r in seen]
        theirs = [canon(r) for r in published]
        if theirs != mine:
            first = next((i for i, (a, b) in enumerate(zip(theirs, mine))
                          if a != b), min(len(theirs), len(mine)))
            errors.append("the witness's copy disagrees with the tape's "
                          "fingerprints (%d published, %d on the tape, first "
                          "difference at %d)" % (len(theirs), len(mine), first))

    covered = sorted(set(int(s) for s in per_seg))
    missing = [nm for i, nm in enumerate(segs)
               if (i + 1) not in covered and len(segs) == max(covered or [0])]
    if missing:
        errors.append("segments with no fingerprint: %s" % ", ".join(missing))

    return {"fingerprints": len(seen), "head_fp": fp_prev, "errors": errors,
            "max_gap": max(gaps) if gaps else 0, "per_seg": per_seg,
            "attested": [r["head"] for r in seen],
            "tombstones": len(tomb_rows)}


# ---------------------------------------------- (a6) compaction, item 20
# ------------------------------------ and Amendment 3 item 2, which bounds it


class CompactionRefused(Exception):
    """Amendment 3 item 2. `factor compact` refuses a span outright rather than
    writing a tombstone it knows will not verify. The refusal is TYPED and
    carries a machine-readable `reason`, so a caller can tell a refused
    compaction from a crash and from a compaction that merely failed to help.
    """

    def __init__(self, reason, detail):
        super().__init__("%s: %s" % (reason, detail))
        self.reason = reason        # contains-fingerprint | unbracketed | ...
        self.detail = detail


# The refusal reasons, as constants so the tests assert on a value rather than
# on a substring of English. Amendment 3 item 2 names the first two;
# Amendment 4 item 11 names `contains-tombstone`, in those words.
REFUSE_CONTAINS = "contains-fingerprint"
REFUSE_CONTAINS_TOMB = "contains-tombstone"
REFUSE_UNBRACKETED = "unbracketed"
REFUSE_RANGE = "span-out-of-range"


def compaction_refusal(kinds, first, last):
    """Amendment 3 item 2 and Amendment 4 item 11, as a pure decision over the
    tape's row kinds.

    "A tombstone may replace only rows strictly between two fingerprints; the
    fingerprints bounding the span stay on the tape, so the keyed chain and the
    fingerprint chain both verify after a lawful compaction and a keyless
    verifier cannot mistake it for a forgery."

    "Tombstones are protected rows. A span containing a tombstone is refused
    with the reason `contains-tombstone`, exactly as one containing a
    fingerprint is, so a second compaction can never erase the audit of the
    first." (Amendment 4 item 11, which closes O8's still-open item 13.)

    Returns None when the span is lawful, else (reason, detail).

    Three clauses, and all three have teeth:
      * a fingerprint INSIDE the span would be removed, and the next
        fingerprint's `fp_prev` would then name an `fp_h` that is no longer on
        the tape -- the keyed chain stays clean and `--chain-only` breaks. That
        is the collision O7 measured in (a7).
      * a TOMBSTONE inside the span would take with it the `count` and the
        operator's signature over an earlier removal, so the second compaction
        erases the audit of the first and the counts item 9's reconstruction
        depends on stop adding up.
      * a span that is NOT BRACKETED by a fingerprint on both sides removes rows
        no published fingerprint ever attested. The witness holds an attestation
        of the head before the span and after it only when both bound it; a
        compaction outside that bracket is one no external observer ever saw the
        two ends of, and a keyless verifier is right to refuse it. The missing
        side matters downstream: no fingerprint AFTER the span is the shape
        Amendment 4 item 10 forbids by name, a published tape carrying an
        unfingerprinted tombstone.

    A span holding both a fingerprint and a tombstone is reported as
    `contains-fingerprint`: the older rule is checked first, and either reason
    refuses the same span.
    """
    n = len(kinds)
    if not (0 <= first <= last < n):
        return (REFUSE_RANGE,
                "span %d..%d is not inside a tape of %d rows" % (first, last, n))
    inside = [i for i in range(first, last + 1) if kinds[i] == "fingerprint"]
    if inside:
        return (REFUSE_CONTAINS,
                "row(s) %s in the span are fingerprints; compaction never "
                "removes a fingerprint"
                % ", ".join(str(i) for i in inside))
    tombs = [i for i in range(first, last + 1) if kinds[i] == "tombstone"]
    if tombs:
        return (REFUSE_CONTAINS_TOMB,
                "row(s) %s in the span are tombstones; a tombstone is a "
                "protected row, and compacting one away discards the count and "
                "the operator's signature over the earlier removal"
                % ", ".join(str(i) for i in tombs))
    before = any(kinds[i] == "fingerprint" for i in range(0, first))
    after = any(kinds[i] == "fingerprint" for i in range(last + 1, n))
    if not (before and after):
        missing = [w for w, ok in (("before", before), ("after", after)) if not ok]
        return (REFUSE_UNBRACKETED,
                "no fingerprint %s the span; a tombstone may replace only rows "
                "strictly between two fingerprints" % " or ".join(missing))
    return None


def _one_segment(dirpath):
    """(path, rows) for a single-segment fixture tape."""
    segs = sorted(p for p in os.listdir(dirpath) if p.startswith("seg-"))
    assert len(segs) == 1, "this fixture compacts inside one segment"
    path = os.path.join(dirpath, segs[0])
    return path, [json.loads(l) for l in open(path, "rb").read().split(b"\n")[:-1]]


def _bracketing_heads(rows, first, last):
    """AMENDMENT 4 ITEM 12. The heads attested by the fingerprints immediately
    before and immediately after the span -- what the operator's signature has
    to cover, so that the operator attests the span was LAWFUL and not only that
    it was removed. Returns (None, None) when the span is not bracketed, which
    is a span `factor compact` refuses anyway."""
    before = [r for i, r in enumerate(rows)
              if i < first and r.get("k") == "fingerprint"]
    after = [r for i, r in enumerate(rows)
             if i > last and r.get("k") == "fingerprint"]
    return (before[-1]["head"] if before else None,
            after[0]["head"] if after else None)


def compact_span(src_dir, dst_dir, first, last, enforce=True):
    """Replace tape rows [first, last] with one signed tombstone row.

    Returns (span_prev, span_h, count). The tombstone carries the span's first
    `prev`, its last `h`, the row count and -- Amendment 4 item 12 -- the heads
    of the two bracketing fingerprints, so the verifier can step across the hole
    and still reach the same head (item 20), and can tell that the operator
    signed the bracket the span actually sat in.

    Amendment 3 item 2 and Amendment 4 item 11 bound which spans may be replaced
    at all. With `enforce=True` -- what `factor compact` does -- an unlawful span
    raises CompactionRefused and NOTHING IS WRITTEN: dst_dir is not even
    created, so a refused compaction cannot leave a half-compacted tape behind.

    `enforce=False` is the planted lie: the compactor with the refusal skipped.

    The tape this returns is NOT yet publishable. Amendment 4 item 10 requires a
    fingerprint at once, before the tape is published, replicated or read by
    anyone but the compactor: that is `close_compaction`, below.
    """
    _srcpath, srcrows = _one_segment(src_dir)
    refusal = compaction_refusal([r.get("k") for r in srcrows], first, last)
    if refusal is not None and enforce:
        raise CompactionRefused(refusal[0], refusal[1])

    shutil.copytree(src_dir, dst_dir)
    path, rws = _one_segment(dst_dir)
    span = rws[first:last + 1]
    span_prev = span[0]["prev"]
    span_h = span[-1]["h"]
    fp_before, fp_after = _bracketing_heads(rws, first, last)
    raw = {"k": "tombstone", "ms": 4242,
           "span_prev": span_prev, "span_h": span_h, "count": str(len(span)),
           # A missing bracket is a span the enforcing compactor refused; the
           # lie writes 64 zeros there so the row still has the shape the
           # verifier reads, and the verifier's bracket check is what fires.
           "fp_before": fp_before if fp_before is not None else GENESIS,
           "fp_after": fp_after if fp_after is not None else GENESIS}
    raw["sig"] = op_sign(canon({k: raw[k] for k in TOMB_SIGNED_KEYS}))
    tomb = seal(raw, span_prev)
    out = rws[:first] + [tomb] + rws[last + 1:]
    with open(path, "wb") as f:
        for r in out:
            f.write(row_line(r))
    manifest = os.path.join(dst_dir, "manifest.json")
    if os.path.exists(manifest):
        os.remove(manifest)                 # the head it caches is stale now
    return span_prev, span_h, len(span)


def close_compaction(dirpath, witness_path=None, ms=4243):
    """AMENDMENT 4 ITEM 10. "A compaction is followed by a fingerprint at once,
    before the tape is published, replicated or read by anyone but the
    compactor, in addition to the ordinary cadence. A tape is never published
    with an unfingerprinted tombstone."

    So this is not the ordinary cadence and does not wait for it: the compactor
    appends a fingerprint the moment it has written the tombstone, and only then
    is the tape publishable. The new fingerprint's `row_orig` continues the
    UNCOMPACTED numbering (item 9: compaction never renumbers), which is
    recoverable from the file: the rows on it, plus the rows the tombstones say
    they replaced, minus the tombstones themselves.

    If a witness path is given the new line is APPENDED to it, which is the only
    thing item 13 asks a witness to be able to do.

    Returns the new head.
    """
    path, rws = _one_segment(dirpath)
    removed = sum(int(r["count"]) - 1 for r in rws if r.get("k") == "tombstone")
    fps = [r for r in rws if r.get("k") == "fingerprint"]
    raw = {"k": "fingerprint", "ms": ms,
           "head": rws[-1]["h"],                 # the head this attests
           "seg": fps[-1]["seg"] if fps else "1",
           "row_orig": str(len(rws) + removed)}
    raw["fp_prev"] = fps[-1]["fp_h"] if fps else GENESIS
    raw["fp_h"] = unkeyed_h(raw["fp_prev"], fp_body(raw), "fprint")
    row = seal(raw, rws[-1]["h"])
    with open(path, "ab") as f:
        f.write(row_line(row))
    if witness_path:
        with open(witness_path, "ab") as w:
            w.write(witness_line(row))
    return row["h"]


def append_rows(dirpath, n, ms_base=7000):
    """Append n ordinary verb rows to a single-segment tape, continuing the
    keyed chain. Used to build a tape whose tail sits AFTER the last
    fingerprint, which is the only shape in which a compaction can leave a
    tombstone that nothing fingerprints (Amendment 4 item 10)."""
    path, rws = _one_segment(dirpath)
    prev = rws[-1]["h"]
    base = len(rws)
    with open(path, "ab") as f:
        for i in range(n):
            raw = {"k": "verb", "ms": ms_base + i,
                   "t_mono_ns": str(1800000000000000000 + i * 1000),
                   "id": "%d" % (0xBEEF0000 + i), "judged_rev": str(900 + i),
                   "verb": "HOLD", "reason": "ok", "flags": 1, "band": 1,
                   "rung": 1, "m_hand": 1, "m_check": 1, "m_guard": 1,
                   "batch": str(base + i), "pos": 0}
            row = seal(raw, prev)
            f.write(row_line(row))
            prev = row["h"]
    if os.path.exists(os.path.join(dirpath, "manifest.json")):
        os.remove(os.path.join(dirpath, "manifest.json"))
    return prev


def retamper_tombstone(dirpath, new_span_h, resign):
    """Rewrite the tombstone's last h. With resign=False the signature is left
    stale; with resign=True the operator signs the lie and only the LINK can
    catch it."""
    segs = sorted(p for p in os.listdir(dirpath) if p.startswith("seg-"))
    path = os.path.join(dirpath, segs[0])
    rws = [json.loads(l) for l in open(path, "rb").read().split(b"\n")[:-1]]
    for i, r in enumerate(rws):
        if r.get("k") == "tombstone":
            r["span_h"] = new_span_h
            if resign:
                r["sig"] = op_sign(canon({k: r[k] for k in TOMB_SIGNED_KEYS}))
            rws[i] = seal({k: v for k, v in r.items() if k not in CHAIN_FIELDS},
                          r["prev"])
            break
    with open(path, "wb") as f:
        for r in rws:
            f.write(row_line(r))


def retamper_bracket(dirpath, which="fp_after", new_head=None, resign=True):
    """AMENDMENT 4 ITEM 12's planted lie. Move one of the two bracketing heads
    the operator signed, and let the operator RE-SIGN it, so the signature is
    valid over a bracket the span never sat in. Everything else about the tape
    is untouched: the keyed chain, the head, the fingerprint chain and the
    tombstone's own endpoints are all exactly as they were."""
    path, rws = _one_segment(dirpath)
    for i, r in enumerate(rws):
        if r.get("k") == "tombstone":
            r[which] = new_head if new_head is not None else "e" * 64
            if resign:
                r["sig"] = op_sign(canon({k: r[k] for k in TOMB_SIGNED_KEYS}))
            rws[i] = seal({k: v for k, v in r.items() if k not in CHAIN_FIELDS},
                          r["prev"])
            break
    with open(path, "wb") as f:
        for r in rws:
            f.write(row_line(r))


# ------------------------------------------------------------------ the spool

_ESC = {"\\": "\\\\", "\t": "\\t", "\n": "\\n", "\r": "\\r"}

# The frame is EIGHT fields since amendment item 8; seven of them are hashed.
SPOOL_BODY_FIELDS = 7


def esc(s):
    """Profile STRICT, section 4. Shares its rule with frame_roundtrip.py."""
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


def spool_header(lane, generation, frame_cap=65536):
    """Amendment item 13: the header obeys section 12's canonical JSON rules,
    integers as decimal strings included -- so `generation`, declared 64-bit,
    is a string here."""
    return {"contract": "factor.spool/1", "venue": "venue-a", "lane": lane,
            "frame_cap": frame_cap, "hash": "blake2b-256", "esc": "strict",
            "rev_kind": "synthetic", "lag_ms": 250,
            "generation": str(generation)}


def build_spool(path, frames, lane="mail-bo", generation=1, genesis=None):
    """Write a spool: one header line then one line per frame. Returns the head.

    A sealed spool starts its next generation with the old head as its genesis
    prev (section 4, Spool law), which is what `genesis` carries.
    """
    prev = GENESIS
    with open(path, "wb") as f:
        hbody = canon(spool_header(lane, generation))
        hh = unkeyed_h(genesis or prev, hbody, "spool")
        f.write(hbody + b"\t" + hh.encode("ascii") + b"\n")
        prev = hh
        for fr in frames:
            assert len(fr) == SPOOL_BODY_FIELDS
            body = "\t".join(esc(str(x)) for x in fr).encode("utf-8")
            h = unkeyed_h(prev, body, "spool")
            f.write(body + b"\t" + h.encode("ascii") + b"\n")
            prev = h
    return prev


def verify_spool(path, genesis=None):
    """Unkeyed: needs no key, so a spool verifies alone."""
    data = open(path, "rb").read()
    prev = genesis or GENESIS
    errors = []
    n = 0
    lines = data.split(b"\n")
    if lines and lines[-1] == b"":
        lines = lines[:-1]
    else:
        errors.append("spool does not end with LF: torn tail")
    for i, line in enumerate(lines):
        cut = line.rfind(b"\t")
        if cut < 0:
            errors.append("line %d: no hash field" % i)
            continue
        body, hhex = line[:cut], line[cut + 1:].decode("ascii", "replace")
        want = unkeyed_h(prev, body, "spool")
        if want != hhex:
            errors.append("line %d: hash mismatch (have %s want %s)"
                          % (i, hhex[:16], want[:16]))
        if i > 0 and body.count(b"\t") != SPOOL_BODY_FIELDS - 1:
            errors.append("line %d: %d hashed fields, the frame has %d"
                          % (i, body.count(b"\t") + 1, SPOOL_BODY_FIELDS))
        prev = hhex
        n += 1
    return {"lines": n, "head": prev, "errors": errors}


def spool_generation(path):
    """Read the generation out of the spool's header line."""
    with open(path, "rb") as f:
        first = f.readline()
    body = first.rsplit(b"\t", 1)[0]
    return int(json.loads(body.decode("utf-8"))["generation"])


# ------------------------------------------------------------------ the cursor

CURSOR_WINDOW = 4096


def make_cursor(path, off, generation=1, window=CURSOR_WINDOW):
    """Amendment item 12: the cursor is (generation, offset, h, window_len)."""
    start = max(0, off - window)
    with open(path, "rb") as f:
        f.seek(start)
        buf = f.read(off - start)
    line, _prev_line = _split_back(buf)
    if line is None:
        raise ValueError("the cursor offset does not end a line")
    h = line[line.rfind(b"\t") + 1:].decode("ascii", "replace")
    return {"generation": generation, "off": off, "h": h, "window_len": len(buf)}


def _split_back(buf):
    """From a window ending at the cursor, return (last line, the one before it)."""
    if not buf.endswith(b"\n"):
        return None, None
    area = buf[:-1]
    k = area.rfind(b"\n")
    line = area[k + 1:]
    if k < 0:
        return line, None
    j = area.rfind(b"\n", 0, k)
    return line, area[j + 1:k]


def check_cursor(path, cur):
    """Re-check the cursor by reading at most window_len bytes back from off.

    Bounded, not O(n): the point of recording window_len is that the re-check
    reads a fixed amount and still proves the bytes before the cursor are the
    bytes the cursor was taken over.
    """
    size = os.path.getsize(path)
    if size < cur["off"]:
        return False, ("spool is SHORTER than the cursor (%d < %d): truncated or "
                       "replaced" % (size, cur["off"]))
    gen = spool_generation(path)
    if gen != cur["generation"]:
        return False, ("generation %d, the cursor was taken in generation %d -- "
                       "after a spool-seal this cursor points into the wrong file"
                       % (gen, cur["generation"]))
    start = max(0, cur["off"] - cur["window_len"])
    with open(path, "rb") as f:
        f.seek(start)
        buf = f.read(cur["off"] - start)
    if len(buf) != cur["window_len"]:
        return False, ("window is %d bytes, the cursor recorded %d"
                       % (len(buf), cur["window_len"]))
    line, prev_line = _split_back(buf)
    if line is None:
        return False, "the cursor offset no longer ends a line"
    cut = line.rfind(b"\t")
    if cut < 0:
        return False, "the line at the cursor has no hash field"
    have = line[cut + 1:].decode("ascii", "replace")
    if have != cur["h"]:
        return False, ("chain value at the cursor changed: have %s want %s"
                       % (have[:16], cur["h"][:16]))
    if prev_line is None:
        return False, ("window of %d bytes is too short to hold the preceding "
                       "line, so the chain value cannot be recomputed"
                       % cur["window_len"])
    pcut = prev_line.rfind(b"\t")
    prev_h = prev_line[pcut + 1:].decode("ascii", "replace")
    want = unkeyed_h(prev_h, line[:cut], "spool")
    if want != cur["h"]:
        return False, ("the bytes before the cursor no longer hash to its chain "
                       "value (want %s)" % want[:16])
    return True, "ok"


# -------------------------------------------------------------------- helpers

def flip_byte(path, offset):
    with open(path, "r+b") as f:
        f.seek(offset)
        b = f.read(1)
        f.seek(offset)
        f.write(bytes([b[0] ^ 0x01]))


def line_offsets(path):
    data = open(path, "rb").read()
    offs = []
    pos = 0
    for part in data.split(b"\n")[:-1]:
        pos += len(part) + 1
        offs.append(pos)
    return offs


def _parses(line):
    try:
        json.loads(line)
        return True
    except Exception:                                        # noqa: BLE001
        return False


# ----------------------------------------------------------------------- main

def main():
    print("=" * 78)
    print("FACTOR BLUEPRINT_v0.2 sections 4 & 12 as amended -- chain check")
    print("hash: hashlib.blake2b(digest_size=32) -- v0.2 pins BLAKE2b-256, so")
    print("      nothing is substituted and these digests are the real ones")
    print("Amendment 1: pinned personalization, the fingerprint chain, the signed")
    print("      tombstone, the eight-field spool frame, the four-part cursor")
    print("Amendment 4: both verifiers hold the compaction rules, the fingerprint")
    print("      body pinned as {head, seg, row_orig}, the closing fingerprint,")
    print("      protected tombstones, the signed bracket, the witness's form")
    print("=" * 78)

    rc = 0
    root = tempfile.mkdtemp(prefix="factor_chain_")
    try:
        # ------------------------------------------- (0) keys and known answers
        print()
        print("(0) KEYS -- one machine secret, one PINNED personalization per chain")
        print("    %-10s %-18s %-5s %s" % ("chain", "person", "bytes", "K_chain"))
        person_bad = 0
        for nm in CHAIN_ORDER:
            p = PERSON[nm]
            fits = len(p) <= BLAKE2B_PERSON_MAX
            if not fits:
                person_bad += 1
            print("    %-10s %-18s %-5s %s%s"
                  % (nm, repr(p.decode()), len(p), KEYS[nm].hex()[:32],
                     "" if fits else "   OVER THE 16-BYTE LIMIT"))
        print("    all six at most %d bytes : %s"
              % (BLAKE2B_PERSON_MAX, "PASS" if person_bad == 0 else "FAIL"))
        print("    all six keys derived    : %s   (%d distinct of %d)"
              % ("PASS" if len(set(KEYS.values())) == len(CHAIN_ORDER) else "FAIL",
                 len(set(KEYS.values())), len(CHAIN_ORDER)))
        if person_bad or len(set(KEYS.values())) != len(CHAIN_ORDER):
            rc = 1
        kat_body = b"known-answer"
        print("    KAT keyed   H_tape(0*64 || u64le(12) || 'known-answer')")
        print("                = %s" % keyed_h(K_TAPE, GENESIS, kat_body)[:32])
        print("    KAT unkeyed H_spool(same preimage)")
        print("                = %s" % unkeyed_h(GENESIS, kat_body, "spool")[:32])
        print("    KAT unkeyed H_fprint(same preimage)")
        print("                = %s" % unkeyed_h(GENESIS, kat_body, "fprint")[:32])
        print("    (section 12 asks for a known-answer vector asserted at boot;")
        print("     these are it, for this preimage, and should be pinned there)")

        body = canon({"k": "verb", "id": "123"})
        if keyed_h(K_TAPE, GENESIS, body) == keyed_h(KEYS["ledger"], GENESIS, body):
            print("    cross-chain transplant  : FAIL -- two chains share a digest")
            rc = 1
        else:
            print("    cross-chain transplant  : PASS -- a row of the tape chain does")
            print("                              not verify under another chain's key")
        if unkeyed_h(GENESIS, body, "spool") == unkeyed_h(GENESIS, body, "fprint"):
            print("    unkeyed separation      : FAIL")
            rc = 1
        else:
            print("    unkeyed separation      : PASS -- a spool line does not verify")
            print("                              as a fingerprint, and neither verifies")
            print("                              as a plain unkeyed BLAKE2b-256")

        # ---------------------------------------------------- (a) tape chain
        tape = os.path.join(root, "tape")
        witness = os.path.join(root, "witness.txt")
        paths, head, rows, fps = build_tape(tape, 24, seg_bytes=1600,
                                            witness_path=witness)
        rep = verify_tape(tape)
        ok = not rep["errors"] and rep["head"] == head
        print()
        print("(a) TAPE, keyed: h = H_k(prev_hex || u64le(len) || body)")
        print("    rows / segments        : %d rows across %d segments (%d of them"
              % (rep["rows"], len(rep["segments"]), len(fps)))
        print("                             fingerprints)")
        print("    chain crosses segments : %s"
              % ("yes" if len(rep["segments"]) > 1 else "NO -- widen the test"))
        print("    filenames monotone     : %s" % " ".join(rep["segments"]))
        print("    head                   : %s" % rep["head"][:32])
        print("    verify clean tape      : %s (%d errors)"
              % ("PASS" if ok else "FAIL", len(rep["errors"])))
        for e in rep["errors"][:4]:
            print("      %s" % e)
        if not ok:
            rc = 1

        # ------------------------------------- (a1) the manifest is a cache
        no_man = os.path.join(root, "tape_nomanifest")
        shutil.copytree(tape, no_man)
        os.remove(os.path.join(no_man, "manifest.json"))
        rep_nm = verify_tape(no_man)
        with_man = verify_tape(tape, use_manifest=True)
        ok_man = (rep_nm["head"] == head and not rep_nm["errors"]
                  and not with_man["errors"])
        print()
        print("(a1) MANIFEST IS A CACHE, NEVER TRUTH")
        print("     head with manifest.json deleted : %s" % rep_nm["head"][:32])
        print("     head with it present            : %s" % with_man["head"][:32])
        print("     same head both ways             : %s" % (rep_nm["head"] == head))
        print("     VERDICT                         : %s"
              % ("PASS" if ok_man else "FAIL"))
        if not ok_man:
            rc = 1

        lie_man = os.path.join(root, "tape_manifest_lies")
        shutil.copytree(tape, lie_man)
        mp = os.path.join(lie_man, "manifest.json")
        m = json.load(open(mp, encoding="utf-8"))
        m["head"] = "f" * 64
        json.dump(m, open(mp, "w", encoding="utf-8"), sort_keys=True,
                  separators=(",", ":"))
        rep_lm = verify_tape(lie_man, use_manifest=True)
        caught_lm = any("manifest head" in e for e in rep_lm["errors"])
        print("     a manifest claiming a false head: %s"
              % ("CAUGHT by the walk" if caught_lm else "BELIEVED -- FAIL"))
        if not caught_lm:
            rc = 1

        # ------------------------------- (a2) segment filenames must be monotone
        badname = os.path.join(root, "tape_badnames")
        shutil.copytree(tape, badname)
        segs_here = sorted(p for p in os.listdir(badname) if p.startswith("seg-"))
        os.rename(os.path.join(badname, segs_here[-1]),
                  os.path.join(badname, "seg-%d.jsonl" % len(segs_here)))
        _names, complaints = segment_files(badname)
        print()
        print("(a2) SEGMENT FILENAMES -- zero-padded and monotone")
        print("     renamed the last segment to seg-%d.jsonl" % len(segs_here))
        print("     complaints            : %d" % len(complaints))
        for c in complaints[:3]:
            print("       %s" % c)
        print("     VERDICT               : %s"
              % ("PASS -- a name that breaks filename order is refused"
                 if complaints else "FAIL -- the unpadded name went unnoticed"))
        if not complaints:
            rc = 1
        big = max(os.path.getsize(os.path.join(tape, s))
                  for s in rep["segments"])
        print("     largest segment       : %d bytes, bound %d (checked before "
              "the append)" % (big, SEGMENT_BOUND))

        # ---------------------------------- (a3) torn trailing row, head recovery
        minus1 = os.path.join(root, "tape_minus1")
        shutil.copytree(tape, minus1)
        _last = os.path.join(minus1, sorted(
            p for p in os.listdir(minus1) if p.startswith("seg-"))[-1])
        _rows_m = open(_last, "rb").read().split(b"\n")[:-1]
        with open(_last, "wb") as f:
            for r in _rows_m[:-1]:
                f.write(r + b"\n")
        head_minus1 = verify_tape(minus1)["head"]

        for case, blob in (("no trailing LF", None),
                           ("undecodable JSON", b'{"k":"verb","ms":9999,"t_mono'),
                           ("valid JSON, bad hash", None)):
            torn_dir = os.path.join(root, "tape_torn_%s" % case.split()[0])
            shutil.copytree(tape, torn_dir)
            last_seg = os.path.join(torn_dir, sorted(
                p for p in os.listdir(torn_dir) if p.startswith("seg-"))[-1])
            good = open(last_seg, "rb").read()
            good_rows = good.split(b"\n")[:-1]
            if case == "no trailing LF":
                with open(last_seg, "wb") as f:
                    f.write(good[:-1])
                expected = head_minus1
            elif case == "undecodable JSON":
                with open(last_seg, "ab") as f:
                    f.write(blob)
                expected = head
            else:
                r = json.loads(good_rows[-1].decode("utf-8"))
                r["seg"] = "999"                     # h no longer matches body
                with open(last_seg, "wb") as f:
                    f.write(b"\n".join(good_rows[:-1]))
                    if good_rows[:-1]:
                        f.write(b"\n")
                    f.write(row_line(r))
                expected = head_minus1
            r2 = verify_tape(torn_dir)
            ok2 = (len(r2["torn"]) == 1 and not r2["errors"]
                   and r2["head"] == expected and len(r2["warns"]) == 1)
            print()
            print("(a3) TORN TRAILING ROW -- %s" % case)
            print("     torn rows detected    : %d  %s"
                  % (len(r2["torn"]), r2["torn"][0] if r2["torn"] else "NONE"))
            print("     warns                 : %d" % len(r2["warns"]))
            print("     errors                : %d" % len(r2["errors"]))
            for e in r2["errors"][:2]:
                print("       %s" % e)
            print("     head == last row that verifies both ways : %s"
                  % (r2["head"] == expected))
            print("     VERDICT               : %s" % ("PASS" if ok2 else "FAIL"))
            if not ok2:
                rc = 1
        print("     (amendment item 18: case three is indistinguishable from a")
        print("      forged tail an attacker wants dropped. The verifier accepts")
        print("      the earlier head either way; that is why the head has two")
        print("      witnesses, and why this is not a defect the test can close.)")

        # ---- a torn row anywhere but the last row of the last segment is fatal
        early = os.path.join(root, "tape_torn_early")
        shutil.copytree(tape, early)
        first_seg = os.path.join(early, sorted(
            p for p in os.listdir(early) if p.startswith("seg-"))[0])
        raw0 = open(first_seg, "rb").read()
        rl = raw0.split(b"\n")
        rl[1] = b'{"k":"verb","ms":1,"t_mo'          # a torn row mid-segment
        open(first_seg, "wb").write(b"\n".join(rl))
        r3 = verify_tape(early)
        ok3 = len(r3["errors"]) > 0
        print()
        print("(a4) A TORN ROW IN A NON-FINAL POSITION IS FATAL, NOT A WARN")
        print("     errors                : %d" % len(r3["errors"]))
        for e in r3["errors"][:2]:
            print("       %s" % e)
        print("     VERDICT               : %s"
              % ("PASS" if ok3 else "FAIL -- it was tolerated"))
        if not ok3:
            rc = 1

        # ------------------------------ (a5) the fingerprint chain, item 19
        before = KEYED_CALLS[0]
        co = verify_chain_only(tape, witness_path=witness)
        keyed_used = KEYED_CALLS[0] - before
        ok_co = (not co["errors"] and keyed_used == 0
                 and co["fingerprints"] == len(fps))
        print()
        print("(a5) FINGERPRINT CHAIN -- `verify --chain-only`, amendment item 19")
        print("     fingerprints on the tape : %d -- one per segment close, and one"
              % co["fingerprints"])
        print("                                every %d rows" % FPRINT_EVERY)
        print("     fingerprint head         : %s" % co["head_fp"][:32])
        print("     internal consistency     : %s (%d errors)"
              % ("PASS" if not co["errors"] else "FAIL", len(co["errors"])))
        for e in co["errors"][:3]:
            print("       %s" % e)
        print("     agrees with the witness  : %s"
              % ("yes" if not any("witness" in e for e in co["errors"]) else "NO"))
        print("     keyed h recomputations   : %d   %s"
              % (keyed_used,
                 "PASS -- the tape key is never touched"
                 if keyed_used == 0 else "FAIL -- it recomputed a keyed hash"))
        print("     each fingerprint attests the head it follows : %s"
              % ("PASS" if not rep["errors"] else "see (a) above"))
        if not ok_co:
            rc = 1

        # a5b: a fingerprint whose attested head is swapped
        fpl = os.path.join(root, "tape_fp_lie")
        shutil.copytree(tape, fpl)
        seg_fp = os.path.join(fpl, sorted(
            p for p in os.listdir(fpl) if p.startswith("seg-"))[0])
        rws = [json.loads(l) for l in open(seg_fp, "rb").read().split(b"\n")[:-1]]
        for r in rws:
            if r.get("k") == "fingerprint":
                r["head"] = "a" * 64
                break
        with open(seg_fp, "wb") as f:
            for r in rws:
                f.write(row_line(r))
        before = KEYED_CALLS[0]
        co2 = verify_chain_only(fpl, witness_path=witness)
        keyed_used2 = KEYED_CALLS[0] - before
        ok_co2 = len(co2["errors"]) > 0 and keyed_used2 == 0
        print("     a fingerprint with a swapped head, seen WITHOUT the key:")
        print("       errors               : %d -> %s"
              % (len(co2["errors"]), co2["errors"][0][:60] if co2["errors"]
                 else "none"))
        print("       keyed recomputations : %d" % keyed_used2)
        print("       VERDICT              : %s"
              % ("CAUGHT" if ok_co2 else "NOT CAUGHT -- FAIL"))
        if not ok_co2:
            rc = 1

        # a5c: the witness's copy, Amendment 4 item 13 -- and BOTH ways it can
        # disagree. Item 13: "one line per fingerprint, the fingerprint row's
        # canonical JSON with the console's signature over it. Any store that
        # can append and cannot rewrite qualifies as a witness."
        w_entries, w_errs = read_witness(witness)
        w_line0 = open(witness, "rb").read().split(b"\n")[0]
        ok_w = (not w_errs and len(w_entries) == len(fps)
                and all(canon(a) == canon(b)
                        for a, b in zip(w_entries, fps)))
        print("     THE WITNESS'S COPY, Amendment 4 item 13:")
        print("       one line per fingerprint : %d line(s), %d fingerprint(s)"
              % (len(w_entries), len(fps)))
        print("       each line is             : the row's canonical JSON, a")
        print("                                  TAB, the console's signature")
        print("       first line               : %s" % w_line0[:56].decode())
        print("                                  ...  sig %s"
              % w_line0.rsplit(b"\t", 1)[1][:16].decode())
        print("       every signature verifies : %s   %s"
              % (not w_errs, "PASS" if ok_w else "FAIL"))
        if not ok_w:
            rc = 1
            for e in w_errs[:3]:
                print("         %s" % e)

        def rewrite_witness(dst, mutate, resign):
            """Republish the witness with its last fingerprint changed."""
            pairs = []
            for ln in open(witness, "rb").read().split(b"\n"):
                if not ln:
                    continue
                cut = ln.rfind(b"\t")
                pairs.append((ln[:cut], ln[cut + 1:]))
            js, sig = pairs[-1]
            js2 = canon(mutate(json.loads(js.decode("utf-8"))))
            pairs[-1] = (js2, console_sign(js2).encode("ascii") if resign
                         else sig)
            with open(dst, "wb") as f:
                for a, b in pairs:
                    f.write(a + b"\t" + b + b"\n")

        wit_stale = os.path.join(root, "witness_stale.txt")
        rewrite_witness(wit_stale, lambda r: dict(r, head="b" * 64),
                        resign=False)
        co3a = verify_chain_only(tape, witness_path=wit_stale)
        ok_co3a = any("signature does not cover" in e for e in co3a["errors"])
        print("       a witness line the console never signed :")
        print("         %s" % (co3a["errors"][0][:66] if co3a["errors"]
                               else "no error"))
        print("         VERDICT: %s"
              % ("CAUGHT by the console's signature" if ok_co3a
                 else "BELIEVED -- FAIL"))
        if not ok_co3a:
            rc = 1

        wit_lie = os.path.join(root, "witness_lie.txt")
        rewrite_witness(wit_lie, lambda r: dict(r, head="b" * 64), resign=True)
        co3 = verify_chain_only(tape, witness_path=wit_lie)
        ok_co3 = any("witness's copy disagrees" in e for e in co3["errors"])
        print("       a signed witness line that disagrees with the tape :")
        print("         %s" % (next((e for e in co3["errors"]
                                     if "disagrees" in e), "no error")[:66]))
        print("         VERDICT: %s"
              % ("CAUGHT by the comparison" if ok_co3 else "BELIEVED -- FAIL"))
        if not ok_co3:
            rc = 1
        print("       -> the signature and the comparison catch different")
        print("          things: the first is a witness holding a line nobody")
        print("          published, the second is a witness and a tape that")
        print("          were both published and do not agree.")

        # a5d: the 4,096 cadence, measured on a tape long enough to hit it
        big_tape = os.path.join(root, "tape_cadence")
        _p, _h, _r, big_fps = build_tape(big_tape, 9000, seg_bytes=8 * 1024 * 1024)
        co4 = verify_chain_only(big_tape)
        ok_co4 = (not co4["errors"] and co4["max_gap"] <= FPRINT_EVERY
                  and len(big_fps) >= 3)
        print("     cadence on a 9,000-row tape in one segment:")
        print("       fingerprints         : %d at rows %s"
              % (len(big_fps), ", ".join(f["row_orig"] for f in big_fps)))
        print("       largest gap          : %d rows between fingerprints, cadence"
              % co4["max_gap"])
        print("                              %d   %s"
              % (FPRINT_EVERY,
                 "PASS" if co4["max_gap"] <= FPRINT_EVERY else "FAIL"))
        if not ok_co4:
            rc = 1

        # ------------------------------ (a6) compaction and the tombstone
        # The tape is built with a dense fingerprint cadence so that a LAWFUL
        # span exists at all: Amendment 3 item 2 lets a tombstone replace only
        # rows strictly between two fingerprints, so a tape with one fingerprint
        # at its close has no lawful span anywhere.
        one_seg = os.path.join(root, "tape_one")
        one_wit = os.path.join(root, "witness_one.txt")
        _p, head1, rows1, fps1 = build_tape(one_seg, 12, seg_bytes=8 * 1024 * 1024,
                                            fprint_every=3,
                                            witness_path=one_wit)
        _path1, rws1 = _one_segment(one_seg)
        kinds1 = [r["k"] for r in rws1]
        fp_idx1 = [i for i, k in enumerate(kinds1) if k == "fingerprint"]
        LO, HI = 4, 6                       # strictly between fp 3 and fp 7
        comp = os.path.join(root, "tape_compacted")
        span_prev, span_h, n_span = compact_span(one_seg, comp, LO, HI)
        rep_c = verify_tape(comp)
        co_c = verify_chain_only(comp)
        ok_t = (not rep_c["errors"] and rep_c["head"] == head1
                and rep_c["tombstones"] == 1
                and not co_c["errors"]
                and co_c["fingerprints"] == len(fp_idx1))
        print()
        print("(a6) COMPACTION -- a signed tombstone replaces the span, item 20,")
        print("     bounded by Amendment 3 item 2")
        print("     tape                   : %d rows, fingerprints at %s"
              % (len(kinds1), fp_idx1))
        print("     span replaced          : rows %d..%d (%d rows), strictly"
              % (LO, HI, n_span))
        print("                              between the fingerprints at %d and %d"
              % (fp_idx1[0], fp_idx1[1]))
        _cpath, crws = _one_segment(comp)
        tomb_row = next(r for r in crws if r["k"] == "tombstone")
        print("     tombstone carries      : span_prev %s" % span_prev[:16])
        print("                              span_h    %s" % span_h[:16])
        print("                              count     %d" % n_span)
        print("                              fp_before %s"
              % tomb_row["fp_before"][:16])
        print("                              fp_after  %s"
              % tomb_row["fp_after"][:16])
        print("                              operator-signed over ALL FIVE")
        print("                              (Amendment 4 item 12: the operator")
        print("                              attests the span was LAWFUL, not")
        print("                              only that it was removed)")
        print("     head before compaction : %s" % head1[:32])
        print("     head after compaction  : %s" % rep_c["head"][:32])
        print("     same head              : %s   %s"
              % (rep_c["head"] == head1, "PASS" if ok_t else "FAIL"))
        print("     errors                 : %d" % len(rep_c["errors"]))
        for e in rep_c["errors"][:3]:
            print("       %s" % e)
        print("     AFTER A LAWFUL COMPACTION, BOTH CHAINS VERIFY (item 2):")
        print("       keyed tape chain     : %d errors, head unchanged %s"
              % (len(rep_c["errors"]), rep_c["head"] == head1))
        print("       fingerprint chain    : %d errors, %d fingerprints (was %d)"
              % (len(co_c["errors"]), co_c["fingerprints"], len(fp_idx1)))
        print("       verify --chain-only  : %d errors   %s"
              % (len(co_c["errors"]),
                 "PASS" if not co_c["errors"] else "FAIL"))
        for e in co_c["errors"][:3]:
            print("         %s" % e)
        print("       the two fingerprints bounding the span are still on the")
        print("       tape, so the keyless walk sees an unbroken fp chain and a")
        print("       tombstone bracketed on both sides.")
        print("       BOTH verifiers now hold the rule (Amendment 4 item 8):")
        print("         `factor verify`      : %d errors" % len(rep_c["errors"]))
        print("         `verify --chain-only`: %d errors" % len(co_c["errors"]))
        if not ok_t:
            rc = 1

        bad_t = os.path.join(root, "tape_tomb_badh")
        shutil.copytree(comp, bad_t)
        retamper_tombstone(bad_t, "c" * 64, resign=False)
        rep_bt = verify_tape(bad_t)
        ok_bt = any("signature" in e for e in rep_bt["errors"])
        print("     tombstone with a WRONG last h, signature left stale:")
        print("       errors               : %d -> %s"
              % (len(rep_bt["errors"]),
                 next((e for e in rep_bt["errors"] if "signature" in e),
                      "none")[:64]))
        print("       VERDICT              : %s"
              % ("REJECTED by the signature" if ok_bt else "ACCEPTED -- FAIL"))
        if not ok_bt:
            rc = 1

        bad_t2 = os.path.join(root, "tape_tomb_resigned")
        shutil.copytree(comp, bad_t2)
        retamper_tombstone(bad_t2, "c" * 64, resign=True)
        rep_bt2 = verify_tape(bad_t2)
        ok_bt2 = any("LINK broken" in e for e in rep_bt2["errors"])
        print("     tombstone with a WRONG last h, RE-SIGNED by the operator:")
        print("       errors               : %d -> %s"
              % (len(rep_bt2["errors"]),
                 next((e for e in rep_bt2["errors"] if "LINK broken" in e),
                      "none")[:64]))
        print("       VERDICT              : %s"
              % ("REJECTED by the link" if ok_bt2 else "ACCEPTED -- FAIL"))
        print("       head                 : %s -- UNCHANGED. One row's link"
              % rep_bt2["head"][:16])
        print("                              breaks and the walk re-syncs, so the")
        print("                              head alone never reveals it. The")
        print("                              rejection is the error, not the head.")
        if not ok_bt2:
            rc = 1

        # ------- (a6b) AMENDMENT 3 ITEM 2: which spans `factor compact` REFUSES
        # The rule as a pure decision over the tape's row kinds, so both clauses
        # are exercised in both directions without contriving a tape for each.
        # F = a fingerprint row, v = any other row.
        print()
        print("(a6b) `factor compact` REFUSES an unlawful span -- Amendment 3")
        print("      item 2: a tombstone may replace only rows STRICTLY BETWEEN")
        print("      two fingerprints, and never a fingerprint itself;")
        print("      Amendment 4 item 11: and never a TOMBSTONE either")
        print("      F = a fingerprint, T = a tombstone, v = any other row")
        print("      %-14s %-8s %-22s %s"
              % ("tape", "span", "expected", "verdict"))
        REFUSAL_CASES = [
            ("vvvFvvvFvvv", 4, 6,  None),
            ("vvvFvvvFvvv", 4, 4,  None),
            ("vvvFvvvFvvv", 3, 6,  REFUSE_CONTAINS),
            ("vvvFvvvFvvv", 4, 7,  REFUSE_CONTAINS),
            ("vvvFvvvFvvv", 1, 5,  REFUSE_CONTAINS),
            ("vvvFvvvFvvv", 2, 8,  REFUSE_CONTAINS),
            ("vvvFvvvFvvv", 0, 2,  REFUSE_UNBRACKETED),
            ("vvvFvvvFvvv", 8, 10, REFUSE_UNBRACKETED),
            ("vvvvvvv",     2, 4,  REFUSE_UNBRACKETED),
            ("FvvvF",       1, 3,  None),
            ("FF",          0, 1,  REFUSE_CONTAINS),
            ("vvvFvvvFvvv", 9, 11, REFUSE_RANGE),
            # Amendment 4 item 11. The first case is the sharp one: a span that
            # is otherwise perfectly lawful -- strictly between two
            # fingerprints, holding no fingerprint -- and refused solely for
            # the tombstone in it.
            ("vvvFTFvvvFv", 4, 4,  REFUSE_CONTAINS_TOMB),
            ("vvvFvTvFvvv", 4, 6,  REFUSE_CONTAINS_TOMB),
            ("vvvFvTvFvvv", 5, 5,  REFUSE_CONTAINS_TOMB),
            ("vvvFvTvFvvv", 4, 4,  None),
            ("vvvFvTvFvvv", 6, 6,  None),
            # A span holding BOTH: the older rule is reported, and either
            # reason refuses the same span.
            ("vFvTvFvvvFv", 1, 5,  REFUSE_CONTAINS),
            ("TvvFvvvFvvv", 0, 2,  REFUSE_CONTAINS_TOMB),
        ]
        KIND_OF = {"F": "fingerprint", "T": "tombstone"}
        refuse_bad = 0
        for pattern, lo_, hi_, want in REFUSAL_CASES:
            kinds = [KIND_OF.get(c, "verb") for c in pattern]
            got = compaction_refusal(kinds, lo_, hi_)
            reason = None if got is None else got[0]
            ok_r = (reason == want)
            if not ok_r:
                refuse_bad += 1
            print("      %-14s %-8s %-22s %s"
                  % (pattern, "%d..%d" % (lo_, hi_),
                     want if want else "lawful",
                     ("PASS" if ok_r else "FAIL -- got %s" % reason)))
        print("      %d of %d decisions as item 2 states them   %s"
              % (len(REFUSAL_CASES) - refuse_bad, len(REFUSAL_CASES),
                 "PASS" if refuse_bad == 0 else "FAIL"))
        if refuse_bad:
            rc = 1

        # ... and the same refusal end to end, against the tape on disk. A
        # refused compaction must write NOTHING.
        for label, lo_, hi_, want in (
                ("a span holding fingerprint %d" % fp_idx1[0], 3, 5,
                 REFUSE_CONTAINS),
                ("a span before the first fingerprint", 0, 2,
                 REFUSE_UNBRACKETED)):
            dst = os.path.join(root, "tape_refused_%d_%d" % (lo_, hi_))
            try:
                compact_span(one_seg, dst, lo_, hi_)
                print("      rows %d..%d, %s: COMPACTED -- FAIL, it must refuse"
                      % (lo_, hi_, label))
                rc = 1
            except CompactionRefused as e:
                ok_e = (e.reason == want and not os.path.exists(dst))
                print("      rows %d..%d, %s:" % (lo_, hi_, label))
                print("        CompactionRefused(%s)   %s"
                      % (e.reason, "PASS" if e.reason == want
                         else "FAIL -- expected %s" % want))
                print("        %s" % e.detail)
                print("        nothing was written, the destination does not "
                      "exist : %s" % (not os.path.exists(dst)))
                if not ok_e:
                    rc = 1

        # ---- (a6c) AMENDMENT 4 ITEM 9: the pinned body, and what a lawful
        # compaction is not allowed to move.
        fp_before_c = [r for r in rws1 if r["k"] == "fingerprint"]
        fp_after_c = [r for r in crws if r["k"] == "fingerprint"]
        bodies_before = [fp_body(r) for r in fp_before_c]
        bodies_after = [fp_body(r) for r in fp_after_c]
        hs_before = [r["fp_h"] for r in fp_before_c]
        hs_after = [r["fp_h"] for r in fp_after_c]
        same_attest = (bodies_before == bodies_after and hs_before == hs_after)
        print()
        print("(a6c) AMENDMENT 4 ITEM 9 -- the fingerprint body is PINNED as")
        print("      {head, seg, row_orig}, and `row_orig` is the row's index on")
        print("      the UNCOMPACTED tape. Compaction never renumbers.")
        print("      body keys, in canonical order : %s" % (FP_BODY_KEYS,))
        print("      one body, verbatim            : %s"
              % bodies_before[0].decode())
        print("      A LAWFUL COMPACTION CHANGES NO ATTESTED FIELD:")
        print("        %-4s %-10s %-10s %-9s %s"
              % ("fp", "row_orig", "position", "moved by", "body unchanged"))
        pos_after = [i for i, r in enumerate(crws) if r["k"] == "fingerprint"]
        pos_before = [i for i, r in enumerate(rws1) if r["k"] == "fingerprint"]
        recon_bad = 0
        for j, r in enumerate(fp_after_c):
            orig = int(r["row_orig"])
            moved = pos_before[j] - pos_after[j]
            same = bodies_before[j] == bodies_after[j]
            if not same:
                recon_bad += 1
            print("        %-4d %-10d %-10d %-9d %s"
                  % (j, orig, pos_after[j], moved, same))
        print("      %d of %d bodies byte-identical, %d of %d fp_h identical  %s"
              % (sum(1 for a, b in zip(bodies_before, bodies_after) if a == b),
                 len(bodies_before),
                 sum(1 for a, b in zip(hs_before, hs_after) if a == b),
                 len(hs_before), "PASS" if same_attest else "FAIL"))
        print("      the POSITION moved for %d of them and no body did, which is"
              % sum(1 for a, b in zip(pos_before, pos_after) if a != b))
        print("      exactly why item 2's promise -- both chains verify after a")
        print("      lawful compaction -- is true rather than lucky. A body that")
        print("      covered the position would have made it false.")
        print("      a verifier RECONSTRUCTS the position: row_orig minus the")
        print("      counts of the tombstones before it (each replaces `count`")
        print("      rows with one), and `compaction_rules` refuses the tape if")
        print("      the arithmetic does not close.")
        if not same_attest or recon_bad:
            rc = 1
        # ... and the reconstruction, made to fail: a fingerprint whose
        # row_orig is renumbered to its post-compaction position -- which is
        # what an implementer who read item 9 the other way would write.
        renum = os.path.join(root, "tape_renumbered")
        shutil.copytree(comp, renum)
        rpath, rrws = _one_segment(renum)
        for i, r in enumerate(rrws):
            if r["k"] == "fingerprint" and int(r["row_orig"]) != i:
                r["row_orig"] = str(i)
                r["fp_h"] = unkeyed_h(r["fp_prev"], fp_body(r), "fprint")
                rrws[i] = seal({k: v for k, v in r.items()
                                if k not in CHAIN_FIELDS}, r["prev"])
                break
        with open(rpath, "wb") as f:
            for r in rrws:
                f.write(row_line(r))
        rep_re = verify_tape(renum)
        co_re = verify_chain_only(renum)
        ok_re = (any(REASON_ROW_ORIG in e for e in rep_re["errors"])
                 and any(REASON_ROW_ORIG in e for e in co_re["errors"]))
        print("      a compactor that RENUMBERS one fingerprint to its new")
        print("      position instead of leaving row_orig alone:")
        print("        `factor verify`       : %d errors" % len(rep_re["errors"]))
        print("        `verify --chain-only` : %d errors" % len(co_re["errors"]))
        print("        %s" % next((e for e in co_re["errors"]
                                   if REASON_ROW_ORIG in e), "none")[:70])
        print("        VERDICT: %s"
              % ("CAUGHT by both, on the reconstruction" if ok_re
                 else "NOT CAUGHT -- FAIL"))
        if not ok_re:
            rc = 1

        # ---- (a6d) AMENDMENT 4 ITEM 10: the fingerprint that closes a
        # compaction, written at once and before the tape is published.
        closed = os.path.join(root, "tape_closed")
        closed_wit = os.path.join(root, "witness_closed.txt")
        shutil.copytree(comp, closed)
        shutil.copyfile(one_wit, closed_wit)
        # The witness's copy was taken BEFORE the compaction and is not
        # rewritten by it -- item 9 is what makes that possible.
        co_pre = verify_chain_only(closed, witness_path=closed_wit)
        new_head = close_compaction(closed, witness_path=closed_wit)
        rep_cl = verify_tape(closed)
        co_cl = verify_chain_only(closed, witness_path=closed_wit)
        _clpath, clrws = _one_segment(closed)
        last = clrws[-1]
        ok_cl = (not rep_cl["errors"] and not co_cl["errors"]
                 and not co_pre["errors"]
                 and last["k"] == "fingerprint"
                 and rep_cl["head"] == new_head
                 and co_cl["fingerprints"] == len(fp_after_c) + 1)
        print()
        print("(a6d) AMENDMENT 4 ITEM 10 -- a compaction is followed by a")
        print("      fingerprint AT ONCE, before the tape is published,")
        print("      replicated or read by anyone but the compactor")
        print("      witness taken BEFORE the compaction, checked after it:")
        print("        %d errors   %s -- item 9 is why this holds"
              % (len(co_pre["errors"]),
                 "PASS" if not co_pre["errors"] else "FAIL"))
        print("      the compactor then appends the closing fingerprint:")
        print("        row_orig               : %s   (the tape carries %d rows"
              % (last["row_orig"], len(clrws)))
        print("                                 and %d were compacted away, so"
              % (n_span - 1))
        print("                                 the UNCOMPACTED index is %s)"
              % last["row_orig"])
        print("        position               : %d" % (len(clrws) - 1))
        print("        attests head           : %s" % last["head"][:32])
        print("        head after the close   : %s" % new_head[:32])
        print("        (the head MOVES, as it does for any appended row -- item")
        print("         20's 'same head' is the compaction step itself, and the")
        print("         closing fingerprint is an ordinary append after it)")
        print("      published tape verifies both ways:")
        print("        `factor verify`        : %d errors, %d fingerprint(s)"
              % (len(rep_cl["errors"]), rep_cl["fingerprints"]))
        print("        `verify --chain-only`  : %d errors, %d fingerprint(s)"
              % (len(co_cl["errors"]), co_cl["fingerprints"]))
        print("        witness, appended to   : %d line(s)   %s"
              % (len(read_witness(closed_wit)[0]),
                 "PASS" if ok_cl else "FAIL"))
        for e in (rep_cl["errors"] + co_cl["errors"])[:3]:
            print("          %s" % e)
        if not ok_cl:
            rc = 1

        # ---- (a6e) AMENDMENT 4 ITEM 11: a tombstone is a PROTECTED row.
        # The closed tape above now carries one, so a second compaction over it
        # is the case item 11 names, on real bytes.
        second = os.path.join(root, "tape_second_compaction")
        ck = [r["k"] for r in clrws]
        t_at = ck.index("tombstone")
        try:
            compact_span(closed, second, t_at, t_at)
            print()
            print("(a6e) a span containing a TOMBSTONE: COMPACTED -- FAIL")
            rc = 1
        except CompactionRefused as e:
            ok_ct = (e.reason == REFUSE_CONTAINS_TOMB
                     and not os.path.exists(second))
            print()
            print("(a6e) AMENDMENT 4 ITEM 11 -- tombstones are PROTECTED rows")
            print("      row %d of the closed tape, the tombstone itself -- a"
                  % t_at)
            print("      span STRICTLY BETWEEN the fingerprints at %d and %d, so"
                  % (t_at - 1, t_at + 1))
            print("      lawful under item 2 and refused only by item 11:")
            print("        CompactionRefused(%s)   %s"
                  % (e.reason, "PASS" if e.reason == REFUSE_CONTAINS_TOMB
                     else "FAIL -- expected %s" % REFUSE_CONTAINS_TOMB))
            print("        %s" % e.detail)
            print("        nothing was written, the destination does not "
                  "exist : %s" % (not os.path.exists(second)))
            print("      -> a second compaction over the first one's tombstone")
            print("         would discard its `count` and the operator's")
            print("         signature over that removal, so the audit of the")
            print("         first compaction would be erased and item 9's")
            print("         reconstruction would stop closing.")
            if not ok_ct:
                rc = 1

        # -------- (a7) PLANTED LIE 4: a compactor that removes a fingerprint
        # Amendment 3 item 2 exists because of this. With the refusal skipped,
        # the tombstone repairs the KEYED chain and the head does not move --
        # only the keyless walk can see what happened, which is exactly why
        # `verify --chain-only` has to be the one that catches it.
        dense = os.path.join(root, "tape_dense")
        _p, dhead, _r, dfps = build_tape(dense, 15, seg_bytes=8 * 1024 * 1024,
                                         fprint_every=3)
        _dpath, drws = _one_segment(dense)
        dkinds = [r["k"] for r in drws]
        fp_at = [i for i, k in enumerate(dkinds) if k == "fingerprint"]
        base_co = verify_chain_only(dense)
        dcomp = os.path.join(root, "tape_dense_compacted")
        lo, hi = fp_at[1] - 1, fp_at[1] + 1
        _sp, _sh, dn = compact_span(dense, dcomp, lo, hi, enforce=False)
        dkeyed = verify_tape(dcomp)
        dco = verify_chain_only(dcomp)
        # Amendment 4 item 8: BOTH verifiers must catch it, and on the same
        # mechanism -- the fingerprint chain, which the keyed verifier now walks
        # as well. O8 could only assert the keyless half.
        caught_fp_co = any(REASON_REMOVED_FP in e for e in dco["errors"])
        caught_fp_keyed = any(REASON_REMOVED_FP in e for e in dkeyed["errors"])
        caught_fp = caught_fp_co and caught_fp_keyed
        print()
        print("(a7) PLANTED LIE 4 -- a compactor that removes a span CONTAINING")
        print("     a fingerprint (the refusal skipped), Amendment 3 item 2,")
        print("     now caught by BOTH verifiers (Amendment 4 item 8)")
        print("     tape                   : %d rows, fingerprints at %s"
              % (len(dkinds), fp_at))
        print("     compacted              : rows %d..%d (%d rows, one a fingerprint)"
              % (lo, hi, dn))
        # The span this lie uses must be one `factor compact` refuses, or the
        # lie is not a lie -- it is a lawful compaction and proves nothing.
        would = compaction_refusal(dkinds, lo, hi)
        print("     `factor compact` would have refused it : %s"
              % (would[0] if would else
                 "NO -- the predicate calls this span LAWFUL, FAIL"))
        if not would or would[0] != REFUSE_CONTAINS:
            rc = 1
        print("     head unchanged         : %s   <- the keyed CHAIN sees nothing"
              % (dkeyed["head"] == dhead))
        print("     chain-only, before     : %d errors, %d fingerprints"
              % (len(base_co["errors"]), base_co["fingerprints"]))
        print("     chain-only, after      : %d errors, %d fingerprints"
              % (len(dco["errors"]), dco["fingerprints"]))
        for e in dco["errors"][:2]:
            print("       %s" % e)
        print("     `factor verify`, after : %d errors, head %s"
              % (len(dkeyed["errors"]), dkeyed["head"][:16]))
        for e in dkeyed["errors"][:2]:
            print("       %s" % e)
        print("     caught by --chain-only : %s" % caught_fp_co)
        print("     caught by verify       : %s   (Amendment 4 item 8)"
              % caught_fp_keyed)
        print("     VERDICT                : %s"
              % ("CAUGHT by both verifiers" if caught_fp
                 else "NOT CAUGHT -- FAIL"))
        print("     -> the next fingerprint's fp_prev names an fp_h that is no")
        print("        longer on the tape. The keyed CHAIN and its head stay")
        print("        clean -- the tombstone repairs them -- so before")
        print("        Amendment 4 only the keyless walk could tell, and the")
        print("        one adversary compaction has is the holder of the")
        print("        operator key, who is the person running `factor verify`.")
        print("        Item 8 moves the rule into the verifier, both of them.")
        if not caught_fp:
            rc = 1

        # -------- (a8) PLANTED LIE 5: the refusal skipped on an UNBRACKETED span
        # The other half of item 2. This span holds no fingerprint at all, so
        # the fingerprint chain's own links are untouched -- and the compaction
        # is still unlawful, because the rows it removes were never inside any
        # bracket the witness holds an attestation for.
        ucomp = os.path.join(root, "tape_dense_unbracketed")
        ulo, uhi = 0, fp_at[0] - 1
        _sp2, _sh2, un = compact_span(dense, ucomp, ulo, uhi, enforce=False)
        ukeyed = verify_tape(ucomp)
        uco = verify_chain_only(ucomp)
        caught_un_co = any(REASON_UNBRACKETED in e for e in uco["errors"])
        caught_un_keyed = any(REASON_UNBRACKETED in e for e in ukeyed["errors"])
        caught_un = caught_un_co and caught_un_keyed
        print()
        print("(a8) PLANTED LIE 5 -- the refusal skipped on a span that holds NO")
        print("     fingerprint but is not strictly between two, Amendment 3")
        print("     item 2, now caught by BOTH verifiers (Amendment 4 item 8)")
        print("     compacted              : rows %d..%d (%d rows, none a fingerprint)"
              % (ulo, uhi, un))
        would_u = compaction_refusal(dkinds, ulo, uhi)
        print("     `factor compact` would have refused it : %s"
              % (would_u[0] if would_u else
                 "NO -- the predicate calls this span LAWFUL, FAIL"))
        if not would_u or would_u[0] != REFUSE_UNBRACKETED:
            rc = 1
        print("     head unchanged         : %s" % (ukeyed["head"] == dhead))
        print("     fingerprint links      : %d fingerprints, all self-hashes and"
              % uco["fingerprints"])
        print("                              fp_prev links intact")
        print("     chain-only, after      : %d errors" % len(uco["errors"]))
        for e in uco["errors"][:2]:
            print("       %s" % e)
        print("     `factor verify`, after : %d errors" % len(ukeyed["errors"]))
        for e in ukeyed["errors"][:2]:
            print("       %s" % e)
        print("     caught by --chain-only : %s" % caught_un_co)
        print("     caught by verify       : %s   (Amendment 4 item 8)"
              % caught_un_keyed)
        print("     VERDICT                : %s"
              % ("CAUGHT by both, on the missing bracket"
                 if caught_un else "NOT CAUGHT -- FAIL"))
        print("     -> nothing about the fingerprints themselves is wrong here.")
        print("        What is wrong is WHERE the tombstone sits: the rows it")
        print("        removed were never bounded by two published attestations,")
        print("        so the witness cannot say what stood between them.")
        if not caught_un:
            rc = 1

        # -------- (a9) PLANTED LIE 6: a PUBLISHED tape whose tombstone nothing
        # fingerprints -- the other half of the bracket, and the shape
        # Amendment 4 item 10 forbids by name. It needs a tape whose tail sits
        # after the last fingerprint, which is exactly the window item 10
        # closes: without it a compaction near the end of a cadence leaves an
        # unfingerprinted tombstone standing for a whole interval.
        tailed = os.path.join(root, "tape_tailed")
        shutil.copytree(dense, tailed)
        append_rows(tailed, 4)
        _tpath, trws = _one_segment(tailed)
        tkinds = [r["k"] for r in trws]
        tlo, thi = len(trws) - 4, len(trws) - 2
        ncomp = os.path.join(root, "tape_unfingerprinted")
        _sp3, _sh3, tn = compact_span(tailed, ncomp, tlo, thi, enforce=False)
        nkeyed = verify_tape(ncomp)
        nco = verify_chain_only(ncomp)
        caught_nf_co = any(REASON_UNFINGERPRINTED in e for e in nco["errors"])
        caught_nf_keyed = any(REASON_UNFINGERPRINTED in e
                              for e in nkeyed["errors"])
        caught_nf = caught_nf_co and caught_nf_keyed
        print()
        print("(a9) PLANTED LIE 6 -- a tape PUBLISHED carrying an")
        print("     UNFINGERPRINTED tombstone, Amendment 4 item 10")
        print("     tape                   : %d rows, last fingerprint at %d,"
              % (len(trws), max(i for i, k in enumerate(tkinds)
                                if k == "fingerprint")))
        print("                              then %d ordinary rows after it --"
              % (len(trws) - 1 - max(i for i, k in enumerate(tkinds)
                                     if k == "fingerprint")))
        print("                              the window the ordinary 4,096-row")
        print("                              cadence leaves open")
        print("     compacted              : rows %d..%d (%d rows, none a"
              % (tlo, thi, tn))
        print("                              fingerprint or a tombstone)")
        would_n = compaction_refusal(tkinds, tlo, thi)
        print("     `factor compact` would have refused it : %s"
              % (would_n[0] if would_n else
                 "NO -- the predicate calls this span LAWFUL, FAIL"))
        if not would_n or would_n[0] != REFUSE_UNBRACKETED:
            rc = 1
        print("     keyed head unchanged   : %s" % (nkeyed["head"] ==
                                                    trws[-1]["h"]))
        print("     `factor verify`        : %d errors" % len(nkeyed["errors"]))
        for e in nkeyed["errors"][:2]:
            print("       %s" % e)
        print("     `verify --chain-only`  : %d errors" % len(nco["errors"]))
        for e in nco["errors"][:2]:
            print("       %s" % e)
        print("     caught by both         : %s / %s"
              % (caught_nf_keyed, caught_nf_co))
        print("     VERDICT                : %s"
              % ("CAUGHT by both, [%s]" % REASON_UNFINGERPRINTED
                 if caught_nf else "NOT CAUGHT -- FAIL"))
        print("     -> the fingerprints, the keyed chain and the head are all")
        print("        clean; every one of them was written before the")
        print("        compaction and none of them attests it. Item 10 is the")
        print("        writer's side of this -- the compactor writes the closing")
        print("        fingerprint AT ONCE, (a6d) above -- and this is the")
        print("        verifier's side: a tombstone nothing on the tape")
        print("        fingerprints is a tape that was published too early.")
        if not caught_nf:
            rc = 1

        # -------- (a10) PLANTED LIE 7: a bracketing head the operator SIGNED,
        # and it is not the bracket the span sat in. Amendment 4 item 12.
        bh = os.path.join(root, "tape_bracket_head")
        shutil.copytree(closed, bh)
        retamper_bracket(bh, which="fp_after", new_head="e" * 64, resign=True)
        bkeyed = verify_tape(bh)
        bco = verify_chain_only(bh)
        caught_bh_keyed = any(REASON_BRACKET_HEAD in e for e in bkeyed["errors"])
        caught_bh_co = any(REASON_BRACKET_HEAD in e for e in bco["errors"])
        sig_ok = not any(REASON_TOMB_SIG in e for e in bkeyed["errors"])
        caught_bh = caught_bh_keyed and caught_bh_co and sig_ok
        print()
        print("(a10) PLANTED LIE 7 -- a tombstone whose fp_after names a head")
        print("      the bracketing fingerprint does not attest, RE-SIGNED by")
        print("      the operator, Amendment 4 item 12")
        print("      the operator's signature over all five fields : VALID")
        print("        (%s -- so the signature alone cannot catch it)"
              % ("no signature error, as expected" if sig_ok
                 else "signature error -- the lie is not the one intended"))
        print("      keyed head unchanged   : %s" % (bkeyed["head"] == new_head))
        print("      `factor verify`        : %d errors" % len(bkeyed["errors"]))
        for e in bkeyed["errors"][:2]:
            print("        %s" % e)
        print("      `verify --chain-only`  : %d errors" % len(bco["errors"]))
        for e in bco["errors"][:2]:
            print("        %s" % e)
        print("      VERDICT                : %s"
              % ("CAUGHT by both, [%s]" % REASON_BRACKET_HEAD
                 if caught_bh else "NOT CAUGHT -- FAIL"))
        # ... and the other half of item 12: the signature COVERS the two
        # heads. Move one and leave the signature alone, and the signature
        # itself must refuse it -- otherwise `fp_before` and `fp_after` are
        # merely two fields the operator did not sign.
        bh2 = os.path.join(root, "tape_bracket_head_unsigned")
        shutil.copytree(closed, bh2)
        retamper_bracket(bh2, which="fp_before", new_head="d" * 64,
                         resign=False)
        b2 = verify_tape(bh2)
        b2co = verify_chain_only(bh2)
        ok_bh2 = (any(REASON_TOMB_SIG in e for e in b2["errors"])
                  and any(REASON_TOMB_SIG in e for e in b2co["errors"]))
        print("      the same move with the signature LEFT ALONE:")
        print("        %s" % next((e for e in b2["errors"]
                                   if REASON_TOMB_SIG in e), "none")[:68])
        print("        VERDICT: %s"
              % ("REFUSED by the signature -- so the signature really does "
                 "cover the two heads" if ok_bh2
                 else "NOT REFUSED -- the heads are outside the signature, FAIL"))
        if not ok_bh2:
            rc = 1
        print("      -> item 12 is only worth its bytes if the verifier checks")
        print("         the two heads against the tape. A signature over a")
        print("         bracket nobody compares is a signature over a number.")
        print("         With the comparison, the operator can no longer attest")
        print("         that a span sat between two fingerprints it did not.")
        if not caught_bh:
            rc = 1

        # -------------------------------------- LIE 1: one byte mid-chain
        lie1 = os.path.join(root, "tape_lie1")
        shutil.copytree(tape, lie1)
        seg1 = os.path.join(lie1, sorted(
            p for p in os.listdir(lie1) if p.startswith("seg-"))[0])
        raw = open(seg1, "rb").read()
        marks = []
        pos = raw.find(b'"reason":"ok"')
        while pos >= 0:
            marks.append(pos)
            pos = raw.find(b'"reason":"ok"', pos + 1)
        target = marks[len(marks) // 2] + 10
        flip_byte(seg1, target)
        rep3 = verify_tape(lie1)
        still_json = all(_parses(l) for l in
                         open(seg1, "rb").read().split(b"\n")[:-1])
        caught = len(rep3["errors"]) > 0
        print()
        print("(b1) PLANTED LIE 1 -- one byte modified mid-chain (offset %d)" % target)
        print("     forged file still parses as JSON : %s" % still_json)
        print("     errors reported       : %d" % len(rep3["errors"]))
        for e in rep3["errors"][:3]:
            print("       %s" % e)
        print("     VERDICT               : %s" % ("CAUGHT" if caught else "NOT CAUGHT"))
        if not caught:
            rc = 1

        # ------------- LIE 2: mid-chain row rewritten AND its own h recomputed
        lie2 = os.path.join(root, "tape_lie2")
        shutil.copytree(tape, lie2)
        seg0 = os.path.join(lie2, sorted(
            p for p in os.listdir(lie2) if p.startswith("seg-"))[0])
        rws = [json.loads(l) for l in open(seg0, "rb").read().split(b"\n")[:-1]]
        victim = rws[1]
        victim["verb"] = "DO"                        # the forgery
        victim = seal({k: v for k, v in victim.items() if k not in CHAIN_FIELDS},
                      victim["prev"])                # recompute its OWN hash
        rws[1] = victim
        with open(seg0, "wb") as f:
            for r in rws:
                f.write(row_line(r))
        strict = verify_tape(lie2, link_check=True)
        sloppy = verify_tape(lie2, link_check=False)
        ok4 = len(strict["errors"]) > 0 and len(sloppy["errors"]) == 0
        print()
        print("(b2) PLANTED LIE 2 -- a row rewritten with its OWN hash recomputed")
        print("     verifier WITH link check    : %d error(s)  %s"
              % (len(strict["errors"]), "CAUGHT" if strict["errors"] else "MISSED"))
        for e in strict["errors"][:2]:
            print("       %s" % e)
        print("     verifier WITHOUT link check : %d error(s)  %s"
              % (len(sloppy["errors"]),
                 "MISSED -- this is the bug the lie is for" if not sloppy["errors"]
                 else "caught"))
        print("     VERDICT               : %s" % ("PASS" if ok4 else "FAIL"))
        if not ok4:
            rc = 1

        # ------------------------------------------------ the plan hash
        _p2, _h2, rows_b, _f2 = build_tape(os.path.join(root, "tape_b"), 24,
                                           seg_bytes=1600, ms_base=999999)
        ph_a, ph_b = plan_hash(rows), plan_hash(rows_b)
        ms_differ = any(a["ms"] != b["ms"] for a, b in zip(rows, rows_b))
        ok_ph = (ph_a == ph_b and ms_differ)
        print()
        print("(b3) PLAN HASH excludes ms, prev and h (section 12)")
        print("     two runs, every ms different : %s" % ms_differ)
        print("     plan hash run A              : %s" % ph_a[:32])
        print("     plan hash run B              : %s" % ph_b[:32])
        print("     VERDICT                      : %s"
              % ("PASS -- identical, so F-DETERMINISM has something to compare"
                 if ok_ph else "FAIL"))
        if not ok_ph:
            rc = 1

        # ---------------------------------------------------- (c) spool chain
        frames = [(1700000000000000000 + i * 1000, "venue-a", "mail-bo",
                   "commit", i, 4,          # f = bit 2, synthetic_rev
                   "subject %d\twith a tab\nand a newline\x85NEL" % i)
                  for i in range(40)]
        spool = os.path.join(root, "mail-bo.g1.spool")
        shead = build_spool(spool, frames)
        srep = verify_spool(spool)
        okb = not srep["errors"] and srep["head"] == shead
        print()
        print("(c) SPOOL self-chain, UNKEYED and personalized %r"
              % PERSON["spool"].decode())
        print("    frame                  : %d fields, %d of them hashed (amendment"
              % (SPOOL_BODY_FIELDS + 1, SPOOL_BODY_FIELDS))
        print("                             item 8: t_mono_ns venue lane grain rev")
        print("                             f text h)")
        print("    lines                  : %d (1 header + %d frames), %d bytes"
              % (srep["lines"], len(frames), os.path.getsize(spool)))
        print("    header is the genesis  : its own prev is 64 zeros, and it obeys")
        print("                             section 12's canonical JSON (item 13)")
        print("    head                   : %s" % srep["head"][:32])
        print("    verify clean spool     : %s (%d errors)"
              % ("PASS" if okb else "FAIL", len(srep["errors"])))
        if not okb:
            rc = 1
            for e in srep["errors"][:3]:
                print("      %s" % e)

        try:
            canon(dict(spool_header("mail-bo", 1), generation=1))
            print("    header with a BARE integer generation : ACCEPTED -- FAIL")
            rc = 1
        except NonCanonical as e:
            print("    header with a BARE integer generation : refused   PASS")
            print("      %s" % e)

        spool_lie = os.path.join(root, "mail-bo-lie.spool")
        shutil.copyfile(spool, spool_lie)
        mid = os.path.getsize(spool_lie) // 2
        flip_byte(spool_lie, mid)
        srep2 = verify_spool(spool_lie)
        okb2 = len(srep2["errors"]) > 0
        print("    PLANTED LIE 3 -- one byte flipped at offset %d" % mid)
        print("      errors               : %d -> %s"
              % (len(srep2["errors"]),
                 srep2["errors"][0] if srep2["errors"] else "none"))
        print("      VERDICT              : %s" % ("CAUGHT" if okb2 else "NOT CAUGHT"))
        if not okb2:
            rc = 1

        # ------------------------------------------ generation seal carries over
        gen2 = os.path.join(root, "mail-bo.g2.spool")
        g2head = build_spool(gen2, frames, generation=2, genesis=shead)
        g2rep = verify_spool(gen2, genesis=shead)
        g2wrong = verify_spool(gen2)                  # verified as if genesis 0*64
        okg = (not g2rep["errors"] and g2rep["head"] == g2head
               and len(g2wrong["errors"]) > 0)
        print("    generation 2 sealed from generation 1")
        print("      verify with g1 head as genesis : %s (%d errors)"
              % ("PASS" if not g2rep["errors"] else "FAIL", len(g2rep["errors"])))
        print("      verify with 64 zeros instead   : %d errors -- %s"
              % (len(g2wrong["errors"]),
                 "the seal is load-bearing" if g2wrong["errors"] else "FAIL"))
        if not okg:
            rc = 1

        # --------------------------------------------------- (d) the cursor
        offs = line_offsets(spool)
        cur_off = offs[19]                      # ingested through frame 19
        cur = make_cursor(spool, cur_off)
        ok_c, why = check_cursor(spool, cur)
        print()
        print("(d) CURSOR = (generation, offset, h, window_len)  -- item 12")
        print("    generation / off       : %d / %d" % (cur["generation"], cur["off"]))
        print("    h                      : %s" % cur["h"][:32])
        print("    window_len             : %d bytes" % cur["window_len"])
        print("    revalidate unchanged   : %s (%s)" % ("PASS" if ok_c else "FAIL", why))
        if not ok_c:
            rc = 1

        ok_g, why_g = check_cursor(gen2, cur)
        same_size = os.path.getsize(gen2) == os.path.getsize(spool)
        print("    SEALED into generation 2, same byte length (%s): %s"
              % (same_size, "PASS" if not ok_g else "FAIL -- it went unnoticed"))
        print("      %s" % why_g)
        if ok_g or not same_size:
            rc = 1

        rot = os.path.join(root, "replaced.spool")
        build_spool(rot, [(t, v, l, g, r, f, txt.replace("subject", "subjecT"))
                          for (t, v, l, g, r, f, txt) in frames])
        same_len = (os.path.getsize(rot) == os.path.getsize(spool))
        ok_r, why_r = check_cursor(rot, cur)
        print("    REPLACED spool, same byte length (%s): %s (%s)"
              % (same_len, "PASS" if not ok_r else "FAIL -- it went unnoticed",
                 why_r))
        if ok_r or not same_len:
            rc = 1

        trunc = os.path.join(root, "truncated.spool")
        shutil.copyfile(spool, trunc)
        with open(trunc, "r+b") as f:
            f.truncate(cur_off - 10)
        ok_t2, why_t = check_cursor(trunc, cur)
        print("    SHRUNK spool detected  : %s (%s)"
              % ("PASS" if not ok_t2 else "FAIL -- it went unnoticed", why_t))
        if ok_t2:
            rc = 1

        edited = os.path.join(root, "edited.spool")
        shutil.copyfile(spool, edited)
        flip_byte(edited, cur_off - 200)
        ok_e, why_e = check_cursor(edited, cur)
        print("    EDITED bytes before the cursor : %s (%s)"
              % ("PASS" if not ok_e else "FAIL -- it went unnoticed", why_e))
        if ok_e:
            rc = 1

        short = make_cursor(spool, offs[19], window=offs[19] - offs[18])
        ok_s, why_s = check_cursor(spool, short)
        print("    window of exactly one line (%d bytes) : %s"
              % (short["window_len"],
                 "reported" if not ok_s else "NOT reported -- FAIL"))
        print("      %s" % why_s)
        if ok_s:
            rc = 1

        # ------------------------------------------- canonical JSON, section 12
        print()
        print("(e) CANONICAL JSON, section 12, by DECLARED WIDTH (item 17)")
        print("    %d keys declared: %d at 64-bit -> decimal string, %d narrower"
              % (len(DECLARED_WIDTH),
                 sum(1 for w in DECLARED_WIDTH.values() if w in WIDE),
                 sum(1 for w in DECLARED_WIDTH.values() if w not in WIDE)))
        for label, obj, must_fail in (
                ("bare float", {"m_hand": 0.5}, True),
                ("NaN", {"x": float("nan")}, True),
                ("amount_fix as a number", {"amount_fix": 19990000}, True),
                ("amount_fix as a string", {"amount_fix": "19990000"}, False),
                ("t_mono_ns as a number", {"t_mono_ns": 2 ** 63 + 1}, True),
                ("t_mono_ns as a string", {"t_mono_ns": str(2 ** 63 + 1)}, False),
                ("rev as a number", {"rev": 7}, True),
                ("an id as a string", {"id": "12345"}, False),
                ("an id with a leading 0", {"id": "0123"}, True),
                ("m_hand as a number", {"m_hand": -500}, False),
                ("m_hand as a string", {"m_hand": "-500"}, True),
                ("m_hand out of int16", {"m_hand": 40000}, True),
                ("undeclared small int", {"band": 7}, False)):
            try:
                canon(obj)
                got = "accepted"
            except (NonCanonical, ValueError):
                got = "refused"
            good = (got == "refused") == must_fail
            print("    %-28s %-9s %s" % (label, got, "PASS" if good else "FAIL"))
            if not good:
                rc = 1
        try:
            validate_keys({"k": "verb", "surprise": 1})
            print("    %-28s %-9s FAIL" % ("unknown key", "accepted"))
            rc = 1
        except NonCanonical as e:
            print("    %-28s %-9s PASS (%s)" % ("unknown key", "refused", e))
        print("    why: the same double is %s in one runtime and %s in another;"
              % (json.dumps(1e16), "10000000000000000"))
        print("         2**53+1 does not survive a JS reader, so a bare t_mono_ns")
        print("         above it is silently rounded by anything reading the tape")
        print("         in Node or a browser. Two verifiers, two heads, one tape.")

        # ---------------------------------------------------------- findings
        print()
        print("Amendment 1 settled, and this run now encodes")
        print("-" * 78)
        print("  item 15  six pinned personalizations, all <= 16 bytes, all six")
        print("           keys derived. The 17-byte template is gone.")
        print("  item 16  ms is a key on the row that the hashed body excludes.")
        print("  item 17  64-bit-as-string is by DECLARED WIDTH, from a table.")
        print("  item 18  the torn tail is unfalsifiable; the head has two")
        print("           witnesses because of it, and a broken link is fatal.")
        print("  item 19  the fingerprint chain, and --chain-only that walks it")
        print("           with no key and no keyed recomputation.")
        print("  item 20  a signed tombstone is the link across a compacted span,")
        print("           and the head is unchanged by compaction.")
        print("  item 22  the 64 MiB segment bound, checked before the append.")
        print()
        print("Amendment 3 item 2 settled, and this run now encodes")
        print("-" * 78)
        print("  Compaction never removes a fingerprint. A tombstone may replace")
        print("  only rows strictly between two fingerprints, `factor compact`")
        print("  refuses anything else with a typed error and writes nothing,")
        print("  and after a lawful compaction the keyed chain reaches the same")
        print("  head AND the fingerprint chain verifies AND --chain-only reports")
        print("  zero errors. O7's (a7) measurement is planted lie 4, and the")
        print("  other half of the rule -- a span outside every attested bracket")
        print("  -- is planted lie 5.")
        print()
        print("Amendment 4 settled, and this run now encodes")
        print("-" * 78)
        print("  item 8   THE VERIFIER holds the rule, not only the writer. The")
        print("           bracket check and the fingerprint-chain check are one")
        print("           function, `compaction_rules`, called by `factor verify`")
        print("           AND by `verify --chain-only`. Planted lies 4 and 5 are")
        print("           now caught by both, where O8 could only assert the")
        print("           keyless half -- and the adversary compaction has is the")
        print("           holder of the operator key, who is the person running")
        print("           the keyed verifier.")
        print("  item 9   The fingerprint body is PINNED as {head, seg, row_orig},")
        print("           `row_orig` is the index on the uncompacted tape, and a")
        print("           verifier reconstructs the position by subtracting the")
        print("           counts of the tombstones before it. A lawful compaction")
        print("           is measured to change no attested field: every body and")
        print("           every fp_h is byte-identical across it while positions")
        print("           move. A compactor that renumbers is caught by both.")
        print("  item 10  A compaction is followed by a fingerprint AT ONCE:")
        print("           `close_compaction` appends it before the tape is")
        print("           publishable, and a tape published with a tombstone that")
        print("           nothing fingerprints is planted lie 6, refused by both")
        print("           verifiers with [%s]." % REASON_UNFINGERPRINTED)
        print("  item 11  Tombstones are protected rows: a span containing one is")
        print("           refused with reason `%s`, even when it"
              % REFUSE_CONTAINS_TOMB)
        print("           is otherwise strictly between two fingerprints.")
        print("  item 12  The operator's signature covers span_prev, span_h,")
        print("           count AND the two bracketing fingerprint heads, and the")
        print("           verifiers compare those heads with the tape. A")
        print("           bracketing head moved and RE-SIGNED is planted lie 7.")
        print("  item 13  The witness's copy is one canonical-JSON line per")
        print("           fingerprint with the console's signature over it,")
        print("           appended and never rewritten. A line the console never")
        print("           signed and a signed line that disagrees with the tape")
        print("           are caught by different mechanisms, and both are.")
        print()
        print("still open for an implementer")
        print("-" * 78)
        print("  a. CLOSED by Amendment 4 item 9: the fingerprint body is")
        print("     {head, seg, row_orig}. What the amendment still does not say")
        print("     is what a fingerprint row carries OUTSIDE that body --")
        print("     {fp_prev, fp_h, ms, k, prev, h} here -- and an implementation")
        print("     that hashed a different split would still chain differently.")
        print("  b. `seg` and `row_orig` have no declared width. Item 17 decides")
        print("     by width and item 9 names `row_orig` without giving it one;")
        print("     both are decimal strings here because both are unbounded")
        print("     monotone counters, but 'small counters are numbers' reads the")
        print("     other way.")
        print("  c. Item 13 says the header's integers are decimal strings; item 17")
        print("     says decimal strings are for 64-bit fields. `frame_cap` and")
        print("     `lag_ms` are integers and are not 64-bit. They are numbers here.")
        print("  d. The pinned enums -- verb, reason, state, gear, kind -- have a")
        print("     declared width (uint8) but section 12 never says whether the")
        print("     tape writes the number or the name. The plan hash covers verb")
        print("     and reason, so the two spellings are two plan hashes.")
        print("  e. The tombstone's own `h` is verifiable but nothing downstream")
        print("     links to it, since the chain continues from span_h. Whether a")
        print("     verifier must also re-check it is unstated.")
        print("  f. Nothing says whether a fingerprint row counts toward its own")
        print("     4,096 cadence, or whether the counter resets at a segment")
        print("     close. Both are counted here; the gap is the checkable form.")
        print("  g. CLOSED by Amendment 4 item 10 -- the fingerprint is written")
        print("     at the compaction, not at the next ordinary interval. What")
        print("     is still open is that ITEM 10 IS NOT DECIDABLE FROM A")
        print("     PUBLISHED TAPE: a fingerprint written by the compactor and")
        print("     one written by the cadence are the same row, and both attest")
        print("     the same head, so the only observable a verifier has is")
        print("     `some fingerprint follows this tombstone` -- which is also")
        print("     the `after` half of item 8's bracket. This file enforces")
        print("     item 10 constructively on the writer and as that observable")
        print("     on the verifier; a tape whose compactor waited for the")
        print("     cadence but was published after it is indistinguishable from")
        print("     one that did not wait.")
        print("  h. CLOSED by Amendment 4 item 12 -- the signature covers the")
        print("     span's endpoints, its count and both bracketing heads. What")
        print("     item 12 does not say is HOW a verifier gets those two heads:")
        print("     they are fields on the tombstone row here, which puts them")
        print("     inside the row's hashed body and therefore inside the keyed")
        print("     chain as well. An implementation that recomputed them from")
        print("     the tape instead would be signing over fields the row does")
        print("     not carry, and could not check a tombstone in isolation.")
        print("  i. CLOSED by Amendment 4 item 13 -- one canonical-JSON line per")
        print("     fingerprint with the console's signature. What item 13 does")
        print("     not say: which key signs it and how a verifier comes to hold")
        print("     that key, and whether the witness receives TOMBSTONES too. A")
        print("     witness holding only fingerprints can bound a compaction's")
        print("     two ends and still cannot see the `count` between them.")
        print("  j. Item 9's reconstruction is a WHOLE-TAPE computation: the")
        print("     counts of every tombstone before a fingerprint. A verifier")
        print("     handed one segment out of many cannot compute it, and the")
        print("     amendment does not say whether the check is per-tape or")
        print("     per-segment. Every compaction here is inside one segment;")
        print("     one that crossed a segment boundary is untested.")
        print("  k. Item 11 does not say which reason wins when a span holds a")
        print("     fingerprint AND a tombstone. `contains-fingerprint` is")
        print("     reported here, the older rule first; either refuses it.")

    finally:
        shutil.rmtree(root, ignore_errors=True)

    print()
    print("=" * 78)
    print("RESULT: %s" % ("ALL CHECKS PASS" if rc == 0 else "FAILURES ABOVE"))
    return rc


if __name__ == "__main__":
    sys.exit(main())
