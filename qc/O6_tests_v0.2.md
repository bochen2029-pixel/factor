# O6 · THE TEST SCAFFOLD, RE-CUT AGAINST v0.2 — checked by running code

Reviewer O6. Target: `C:\FACTOR\BLUEPRINT_v0.2.md`, sections 4, 5, 12, 21 (and 22
for the gate map). Predecessor: `C:\FACTOR\qc\O3_formats_tests.md`, which built
this scaffold against v0.1 earlier today.

Machine: Windows 11 Pro 26100, Python 3.13.2, MSVC 19.44.35228 (VS 2022
Community, `/std:c++20 /EHsc /W4`), g++ 13.3.0 (WSL Ubuntu-24.04,
`-std=c++20 -Wall -Wextra`).

Neither blueprint was modified. All edits are under `C:\FACTOR\tests\`.

---

## Headline

**§5's record is really 128 bytes now.** O3's one red light is out: the v0.2 record
measures 128 bytes with `alignof == 8`, every field at the offset §5 pins in its
own comment, and **zero implicit padding anywhere** — internal or trailing. Three
independent measurements agree byte for byte: ctypes on Win64, MSVC on Win64, g++
on SysV-x86-64. The `_pad[8]` v0.2 declares is the correct pad, not merely a pad
that reaches 128.

All four checks are green and the four compile targets behave as designed:

| check | exit | headline number |
|---|---:|---|
| `check_layout.py` | 0 | sizeof 128, alignof 8, 29/29 offsets, 0 hole bytes, 0 trailing pad |
| `frame_roundtrip.py` | 0 | STRICT 10000/10000 round trip, **0** splitlines violations |
| `chain_check.py` | 0 | 24 rows / 8 segments verify; 3 planted lies caught |
| `run_falsifiers.py` | 0 | 45 falsifiers, 90/90 functions TODO |
| `cl … layout_check.cpp` | 0 | all static_asserts pass |
| `cl … /DPROVE_SPEC_FAILS` | **2** | C2338, the planted lie refused |
| `g++ … layout_check.cpp` | 0 | same offsets as MSVC and ctypes |
| `g++ … -DPROVE_SPEC_FAILS` | **1** | *the comparison reduces to `(120 == 128)`* |

**§21 has forty-five falsifiers, not forty-six.** The brief for this pass said
forty-six. The table in §21 has 45 rows, and a regex sweep of the whole document
finds 45 distinct `F-*` names and no forty-sixth mentioned anywhere. The scaffold
is built to 45. If a forty-sixth is intended it has not been written down; the
two obvious candidates are the M8 gate (which has three prose conditions and no
falsifier) and a companion for F-SELF.

Below, everything printed by every run, then the files, then where v0.2 is still
short of what an implementer needs.

---

## 1 · §5 · Layout — PASS on three toolchains

`python C:/FACTOR/tests/check_layout.py` → **exit 0**

```
  [1] sizeof == 128          : measured 128   PASS
      alignof == 8           : measured 8   PASS
      128 is two 64-byte cache lines : True
  [2] every pinned offset  : 29 of 29 match   PASS
  [3] no internal hole     : 0 hole byte(s)   PASS
      no trailing ABI pad    : 0 byte(s)   PASS
      named bytes == sizeof  : 128 vs 128   PASS
      fields straddling a cache line: none
  [4] PLANTED LIE -- section 21 F-LAYOUT: 'the v0.1 claim asserted'
      the lie asserts sizeof(v0.1 record) == 128
      measured                              == 120
      VERDICT: CAUGHT
```

Field offsets, identical under ctypes/Win64, MSVC/Win64 and g++/SysV-x86-64:

| field | off | size | field | off | size |
|---|---:|---:|---|---:|---:|
| `id` | 0 | 8 | `n_wait` | 92 | 2 |
| `party` | 8 | 8 | `tie` | 94 | 2 |
| `opened_ns` | 16 | 8 | `cls` | 96 | 4 |
| `due_ns` | 24 | 8 | `band` | 100 | 4 |
| `horizon_ns` | 32 | 8 | `seat` | 104 | 4 |
| `blocked_by` | 40 | 8 | `unit` | 108 | 4 |
| `src_rev` | 48 | 8 | `flags` | 112 | 2 |
| `judged_rev` | 56 | 8 | `state` | 114 | 1 |
| `release_ns` | 64 | 8 | `verb` | 115 | 1 |
| `amount_fix` | 72 | 8 | `reason` | 116 | 1 |
| `seq` | 80 | 4 | `gear` | 117 | 1 |
| `m_hand` | 84 | 2 | `kind` | 118 | 1 |
| `m_check` | 86 | 2 | `rung` | 119 | 1 |
| `m_guard` | 88 | 2 | `_pad` | 120 | 8 |
| `n_wit` | 90 | 2 | | | |

Last named field `rung` ends at 120; `_pad[8]` carries the record to exactly 128;
`alignof == 8` adds nothing. **The pad-search branch never fired**, because it is
only entered when the declared pad misses 128 or leaves implicit padding. If it
had fired it would have printed every pad length reaching 128 and the single one
of them leaving no implicit padding — the machinery is retained and is what would
report a regression rather than silently correcting it.

`layout_check.cpp` proves the same at compile time, and proves it twice over: it
asserts every offset individually **and** asserts that the sum of the declared
member widths equals `sizeof`. The second form is the one that catches a hole
anywhere in the middle, not merely at the end.

```
cl /std:c++20 /EHsc /W4                     -> CL_CLEAN_EXIT=0
cl /std:c++20 /EHsc /W4 /DPROVE_SPEC_FAILS  -> CL_LIE_EXIT=2, no binary produced
   error C2338: static_assert failed: 'PLANTED LIE: v0.1 claimed 128;
                the compiler says otherwise'
g++ -std=c++20 -Wall -Wextra                -> exit 0
g++ ... -DPROVE_SPEC_FAILS                  -> exit 1, NO_BINARY
   error: static assertion failed: PLANTED LIE: v0.1 claimed 128; ...
   note: the comparison reduces to '(120 == 128)'
```

Runtime print from both binaries:

```
Obligation    (v0.2, _pad[8])  sizeof = 128  alignof = 8
ObligationV01 (v0.1, _pad[14]) sizeof = 120  alignof = 8
named bytes summed = 128   implicit padding = 0
```

The planted lie is now the v0.1 record, which is what §21's F-LAYOUT row asks for
(*"the v0.1 claim asserted"*). It is a better lie than the v0.1 scaffold's,
because it also asserts `sizeof(v0.1) != sizeof(v0.2)`: the two records must not
be byte-compatible, or the ledger header's refusal-not-conversion rule has nothing
to refuse.

Measured, informational, from the same run:

```
  amount_fix: int64 at 1/65536 of `unit`
    range              : -140737488355328.000 to +140737488355328.000 units
    decimal    x 65536            exactly representable
    0.01       655.3600           NO
    0.10       6553.6000          NO
    0.25       16384.0000         yes
    19.99      1310064.6400       NO
    500.00     32768000.0000      yes
```

---

## 2 · §21 · Falsifier scaffold — 45 files, runner green

`python C:/FACTOR/tests/run_falsifiers.py` → **exit 0**

```
  TODO 90

  by section 22 gate
    M0      8   F-CHAIN F-CONSERVE F-DETERMINISM F-EGRESS F-FRAME F-LAYOUT F-PIN F-REPLAY
    M1      8   F-BLIND F-BUDGET F-INERT F-INERT-BYTES F-QUANTA F-RESIDENT F-RIPEN F-SILENCE
    M2      2   F-EXTRACT F-STANDING
    M3      2   F-ORDER F-WINDOW
    M4     10   F-BOTH-SIDES F-CANARY F-COVERED F-DETECT F-EXPIRY F-MONOTONE
                F-PREDICT F-SALT F-TERMINAL F-WITNESS
    M5      3   F-CAP F-FAMILY F-JURY
    M6      5   F-CONTRADICT F-DARK F-DEGRADE F-FRONT F-REDACT
    M7      5   F-COMPILE F-MOLT F-ROLLBACK F-ROLLBACK-MONOTONE F-TICK
    M9      1   F-OBSERVE
    none    1   F-SELF

RESULT: scaffold intact -- 90 of 90 functions are stubs (TODO),
        0 implemented and passing
```

Every one of the 45 reports `TODO` for both `requires()` and `planted_lie()`.
`--verbose` prints, per stub, the one-sentence statement of what it must assert.

The runner no longer merely names files. Each row carries the §21 id **and** the
§22 gate, and the runner refuses a module that disagrees with its row. Verified
by running a copy of the directory with `F_SELF.py` deleted and `F_MOLT.py`'s
gate changed from M7 to M6:

```
  F_SELF                 none  MISSING   MISSING   F-SELF
      file not found: ...\F_SELF.py
  F_MOLT                 M6    ERROR     ERROR     F-MOLT
      MILESTONE is 'M6', section 22 says 'M7'
  ERROR 2   MISSING 2   TODO 86
RESULT: 4 falsifier function(s) FAILED, ERRORED or are MISSING     EXIT=1
```

So a deleted falsifier, a renamed one, a copy-paste id, and a gate that drifts
from §22 are all build failures. An unwritten falsifier is not.

**Gate assignment.** Two falsifiers are gated twice and are recorded at the
earlier gate, because that is the milestone at which the file must first exist:
F-CONSERVE at M0 (§22: *"without the heard bucket"*) and again at M2 (*"full"*);
F-EGRESS at M0 and again at M3 (*"full"*). F-SELF is recorded as `none` rather
than guessed — see §6 below.

**Zero deletions.** All sixteen v0.1 stub ids survive into v0.2 unchanged in
name, so no stub became orphaned. **Two of the sixteen changed gate:** F-EGRESS
moved M3 → M0 and F-BUDGET moved M4 → M1. All sixteen had their `REQUIRES` and
`PLANTED_LIE` replaced with v0.2's text, which is materially stricter: **28 of
the 45** `requires` cells now carry more than one clause, and **8** of the
planted-lie cells carry more than one lie, so most stubs must assert a
conjunction rather than a single property. The stub messages were written to say
so — F-CONTRADICT's, for instance, spells out the full two-by-two including the
two misses, because "caught by the comparator" alone is half the row.

---

## 3 · §4 · Frame codec — 10,000 strings, STRICT, seven fields

`python C:/FACTOR/tests/frame_roundtrip.py` → **exit 0**

```
corpus: 10000 strings (seeded, deterministic) incl. 23 adversarial literals
frame : 7 tab-separated fields, the seventh the chain hash
hash  : BLAKE2b-256, unkeyed, over prev_hex || u64le(len) || body

profile STRICT (MANDATED by section 4)
  round trip, all 7 fields + chain hash : PASS  (10000/10000 passed)
  one line under a byte-level reader     : yes (checked per frame)
  one line under str.splitlines()        : yes (0 violations of 10000)
  chain head after 10000 frames          : 7d7d634e9a97760c0f258d1d353ec761

profile MIN    (NOT legal in v0.2; run as the measurement)
  round trip, all 7 fields + chain hash : PASS  (10000/10000 passed)
  one line under str.splitlines()        : NO (4632 violations of 10000)
  chain head after 10000 frames          : b7c8f35b8742a09f0e0d4fb3be580e38
     -> MIN lets these through raw: U+0000 U+000B U+000C U+001C U+001D U+001E
                                    U+0085 U+2028 U+2029
     -> 46.3% of this corpus triggers it.

MANDATORY: every escaped frame is ONE line under str.splitlines()
  STRICT violations : 0   PASS

invalid UTF-8 (all five cases badenc=True, roundtrip=True)
  b'\xff\xfe'          -> '\\xff\\xfe'
  b'caf\xe9'           -> 'caf\\xe9'
  b'\xc3('             -> '\\xc3('
  b'ok\xed\xa0\x80end' -> 'ok\\xed\\xa0\\x80end'
  b'\x80\x81\x82'      -> '\\x80\\x81\\x82'
  invalid-UTF-8 handling: PASS

frame cap (64 bytes, applied to the ENCODED field)
  encoded fields over the cap : 0   PASS
  capped field decodes to a prefix of the source : 0 bad   PASS

planted lies -- each MUST be caught
  LIE 1  encoder drops carriage returns          caught @ idx 7  decoded text differs
  LIE 2  encoder does not escape the backslash   caught @ idx 1  decode raised:
                                                 trailing backslash
  LIE 3  encoder escapes TAB before the backslash caught @ idx 5 decoded text differs
  LIE 4  decoder passes unknown escapes through  caught @ idx 0  permissive decoder
                                                 accepted an unknown escape

why the backslash must be escaped first:
   text            = '\\t'   (2 chars)
   LIE 2 encodes   = '\t'
   strict decode   = '<TAB>'  <- a TAB appeared out of nowhere
```

The frame is now the full seven fields, so the seventh is checked as part of the
round trip: field 7 must be 64 lowercase hex, and it must equal
`BLAKE2b-256(prev_hex ‖ u64le(len(body)) ‖ body)` computed over the *encoded*
first six fields with their tabs. The 10,000 frames are chained end to end, which
is why a chain head is printed — a single wrong byte anywhere in the corpus would
move it.

MIN's **4632 of 10000** is the number that justifies v0.2's decision. It rose from
O3's 4173 because the corpus now runs against the seven-field line; the
conclusion is unchanged and now measured against a mandate rather than a
recommendation.

The v0.1 harness's length-prefixed alternative was **removed**: v0.2 §4 decides
in favour of escaping, so carrying a rejected alternative in a test file is noise.
The reasoning survives in `O3_formats_tests.md` §2.

---

## 4 · §12 · Chains — keyed tape, unkeyed spool, all lies caught

`python C:/FACTOR/tests/chain_check.py` → **exit 0**

The hash is no longer a substitute. v0.2 pins BLAKE2b-256 everywhere and
`hashlib` provides it natively, keyed and personalized, so **every digest printed
below is the digest a real FACTOR tape would carry for the same bytes.**

```
(0) KEYS
    K_tape  = a3f8ac6a059204a0e59a7b0c96a702d6...
    person  = 'FACTOR tape v1' (14 bytes, limit 16)
    KAT keyed   H(0*64 || u64le(12) || 'known-answer') = aef619668f3507819ec2568cab3b727a
    KAT unkeyed H(0*64 || u64le(12) || 'known-answer') = 204d715e71bcc3d901f78d44474ee603
    cross-chain transplant : PASS -- a row of the tape chain does not verify
                             under another chain's key
    personalization LIMIT  : 'FACTOR dossier v1' is 17 bytes
    K_dossier derivable    : NO -- maximum person length is 16 bytes

(a) TAPE, keyed: h = H_k(prev_hex || u64le(len) || body)
    rows / segments        : 24 rows across 8 segments
    chain crosses segments : yes
    filenames monotone     : seg-000001 .. seg-000008.jsonl
    head                   : 23f48a7ad2f429ca9014bd92028bc4ad
    verify clean tape      : PASS (0 errors)

(a1) MANIFEST IS A CACHE, NEVER TRUTH
     head with manifest.json deleted : 23f48a7ad2f429ca9014bd92028bc4ad
     head with it present            : 23f48a7ad2f429ca9014bd92028bc4ad
     same head both ways             : True                 PASS
     a manifest claiming a false head: CAUGHT by the walk

(a2) SEGMENT FILENAMES -- zero-padded and monotone
     renamed the last segment to seg-8.jsonl
     seg-8.jsonl: segment number is not zero-padded to 6, so filename order
                  stops matching numeric order                PASS

(a3) TORN TRAILING ROW -- all three of section 12's cases
     no trailing LF        : 1 torn, 1 warn, 0 errors, head steps back  PASS
     undecodable JSON      : 1 torn ("no trailing LF; undecodable JSON
                             (JSONDecodeError, 29 bytes)"), 0 errors     PASS
     valid JSON, bad hash  : 1 torn ("hash of a partially written row")  PASS

(a4) A TORN ROW IN A NON-FINAL POSITION IS FATAL, NOT A WARN
     errors                : 2                                          PASS

(b1) PLANTED LIE 1 -- one byte modified mid-chain (offset 664)
     forged file still parses as JSON : True
     seg-000001.jsonl row 1: SELF hash mismatch (h=73223545e02c0520
                                              want=8c74ed34219465ec)   CAUGHT

(b2) PLANTED LIE 2 -- a row rewritten with its OWN hash recomputed
     verifier WITH link check    : 1 error(s)  CAUGHT
     verifier WITHOUT link check : 0 error(s)  MISSED  <- the bug the lie is for

(b3) PLAN HASH excludes ms, prev and h
     two runs, every ms different : True
     plan hash run A / run B      : 9f94375721d50363... / 9f94375721d50363...  PASS

(c) SPOOL self-chain, UNKEYED so it verifies alone
    lines                  : 41 (1 header + 40 frames), 6535 bytes
    head                   : 5cb9154461120b70952f87542ca1628e
    verify clean spool     : PASS (0 errors)
    PLANTED LIE 3 -- one byte flipped at offset 3267
      line 20: hash mismatch (have 7cd13709eb7003ee want 3bcebaac7041879c)  CAUGHT
    generation 2 sealed from generation 1
      verify with g1 head as genesis : PASS (0 errors)
      verify with 64 zeros instead   : 1 error -- the seal is load-bearing

(d) CURSOR: end offset, the frame's chain value h, window length
    off / window_len       : 3217 / 3217 bytes
    revalidate unchanged   : PASS
    REPLACED spool, same byte length (True) : PASS
      chain value at the cursor changed: have 3a8a86c6 want 4396853b
    SHRUNK spool           : PASS (spool is SHORTER than the cursor 3207 < 3217)
    EDITED bytes before the cursor : PASS (no longer hash to its chain value)
    window of exactly one line (158 bytes) : reported -- too short to hold the
      preceding line, so the chain value cannot be recomputed

(e) CANONICAL JSON
    bare float / NaN / bare 64-bit integer   refused    PASS
    64-bit integer as a string / small int   accepted   PASS
    unknown key                              refused    PASS
```

Three things about this run are worth naming.

**The replaced-spool test is now strict.** The v0.1 harness detected a replaced
spool because the replacement happened to have different line lengths, so the
cursor offset no longer landed on a line boundary — a lucky catch, not a proof.
The replacement is now byte-length-identical to the original (`same byte length
(True)`), so every offset still lands correctly and only the chain value can tell
them apart. It does.

**The torn-row rule is implemented literally.** §12 says a torn row is *skipped
with a warn*, and lists "no trailing newline" as one of the three torn cases. So a
row that is complete, canonical and verifies both ways but whose LF never reached
the disk is still torn: it does not advance `prev` and does not become the head.
The head steps back one row. That is the safe direction — the row is re-derived
on restart — but it is a decision, and §12 should say so out loud, because the
opposite reading (accept it, it verifies) is equally available from the text.

**A broken link is deliberately not a torn case.** An intact row that simply does
not follow its predecessor is a forgery, not a tear, so it is fatal even in the
last position. §12 does not say this; the three cases it lists do not include it,
which is the reading taken here.

---

## 5 · Files

Under `C:\FACTOR\tests\` — **51 files** (45 falsifier stubs + 6 harness files)
where there were 22 (16 + 6).

**Created (29)** — one falsifier stub per §21 id that had none:

`F_RESIDENT.py` `F_RIPEN.py` `F_SILENCE.py` `F_QUANTA.py` `F_SALT.py`
`F_CHAIN.py` `F_INERT_BYTES.py` `F_BLIND.py` `F_STANDING.py` `F_ORDER.py`
`F_TERMINAL.py` `F_SELF.py` `F_FAMILY.py` `F_CAP.py` `F_COVERED.py`
`F_WITNESS.py` `F_PREDICT.py` `F_DETECT.py` `F_EXPIRY.py` `F_CANARY.py`
`F_FRONT.py` `F_DARK.py` `F_OBSERVE.py` `F_ROLLBACK_MONOTONE.py` `F_MOLT.py`
`F_DEGRADE.py` `F_REDACT.py` `F_LAYOUT.py` `F_FRAME.py`

**Changed (21)**:

| file | what changed |
|---|---|
| `check_layout.py` | rebuilt for the v0.2 record: 29 pinned offsets asserted individually, no-implicit-padding asserted three ways, planted lie is now the v0.1 record, `amount_fix` scale measured |
| `layout_check.cpp` | v0.2 struct with all 29 offsets; `kNamedBytes == sizeof` proves no hole anywhere; float/IEEE-754 assertions dropped (v0.2 has no float in the record) and replaced with int16 two's-complement bounds; `ObligationV01` added as the `-DPROVE_SPEC_FAILS` lie |
| `frame_roundtrip.py` | seven fields with the chain hash as field 7; STRICT is the mandated profile and MIN is demoted to a measurement; splitlines is now a hard gate; invalid-UTF-8 and frame-cap checks added; length-prefixed alternative removed |
| `chain_check.py` | keyed tape chain with personalization and `u64le(len)`; unkeyed spool; generation seal; three torn cases; segment-filename and manifest-as-cache checks; cursor rewritten to (offset, chain value, window length); canonical-JSON rules of v0.2 enforced; plan hash added |
| `run_falsifiers.py` | 45 named rows carrying id **and** gate; ID/MILESTONE mismatch is an ERROR; `--gate` filter; per-gate summary |
| `README.md` | rewritten for v0.2: 45-row table, gate map, the two §21/§22 mismatches |
| the 16 pre-existing `F_*.py` | `REQUIRES` / `PLANTED_LIE` replaced with v0.2's text; `MILESTONE` re-derived from §22; docstrings re-pointed at `BLUEPRINT_v0.2.md` |

**Deleted: none.** Every falsifier id in the v0.1 scaffold still exists in v0.2's
§21, so no stub became orphaned.

Under `C:\FACTOR\qc\`: this file, `O6_tests_v0.2.md`.

### Re-running everything

```
python C:/FACTOR/tests/check_layout.py         # exit 0
python C:/FACTOR/tests/frame_roundtrip.py      # exit 0
python C:/FACTOR/tests/chain_check.py          # exit 0
python C:/FACTOR/tests/run_falsifiers.py -v    # exit 0, 90 TODO

cl  /std:c++20 /EHsc /W4                        C:/FACTOR/tests/layout_check.cpp  # 0
cl  /std:c++20 /EHsc /W4 /DPROVE_SPEC_FAILS     C:/FACTOR/tests/layout_check.cpp  # 2
g++ -std=c++20 -Wall -Wextra                    layout_check.cpp                  # 0
g++ -std=c++20 -Wall -Wextra -DPROVE_SPEC_FAILS layout_check.cpp                  # 1
```

MSVC needs a VS 2022 developer environment (`vcvars64.bat`); g++ is reached with
`wsl -d Ubuntu-24.04 --exec bash -c "..."` against `/mnt/c/FACTOR/tests/`.

---

## 6 · Where v0.2 is still underspecified

v0.2 closed most of what O3 raised: the record is really 128 bytes, `state` /
`verb` / `gear` / `kind` are numbered in §5 and `reason` 0–26 in §8, the `flags`
bits are assigned, `unit` exists, endianness is pinned, the id-collision rule is
`fatal`, the frame has its seventh field, canonical JSON is defined, the verifier
is two-way, the torn rules and segment rules are written, `ms` is out of the
hashed body, the plan hash is defined, encryption is AEAD over plaintext-hashed
segments, and the spool has a sealing mechanism with generations. What follows is
what a person sitting down to implement §§4, 5, 12, 21 would still have to invent.

### §5 · The ledger

1. **`BLAKE2b-64` is ambiguous, and the two readings differ.** §5 says the id is
   "BLAKE2b-64 of (source, table, key)". BLAKE2b with `digest_size=8` mixes the
   digest length into its parameter block, so it is **not** the first 8 bytes of
   BLAKE2b-256. Measured on the same input `b"source|table|key"`:
   `digest_size=8` → `f8cfc5f9a416434d`; first 8 bytes of `digest_size=32` →
   `0c3b6b8f3fd8b959`. Two builds, two id spaces, one ledger. **Say which, and
   say whether the id is keyed** — an unkeyed id lets anyone who knows the source
   coordinates compute a live id.
2. **`amount_fix`'s scale cannot represent a cent, and no rounding rule is
   given.** 2⁻¹⁶ is a binary fraction: `0.01 × 65536 = 655.36`,
   `19.99 × 65536 = 1310064.64`. Neither is an integer. §5's identity paragraph
   hashes "amount as fixed point" into a **derived obligation's id**, so the
   rounding rule is identity-bearing: two extractors that round `19.99`
   differently mint two obligations for one promise, and §11's caps are compared
   against the same rounded number. Pin the rule (round-half-even at the scale,
   applied once at ingest) or change the scale to 10⁻⁴ or to minor units.
3. **The writ's `unit` and the record's `unit` are different types with no
   mapping.** §11 writes `unit = "USD"`; §5's field is `uint32` ISO-4217
   **numeric** with "an interned code otherwise". Nothing maps `"USD"` → 840, and
   nothing keeps an interned non-money code out of the ISO numeric range — an
   interned code that lands on 840 makes hours look like dollars to the cap.
   Reserve a range: ISO numerics below 1000, interned codes above.
4. **`cls` is interned by the writ's class table and nothing says where that
   table lives.** §5 promises ids stable across runs; `cls` sits in the record and
   in the `(cls, due_ns)` index. If interning is not persisted and stable across a
   writ edit, every historical record is silently renumbered by an edit to the
   writ. Say where the intern table is persisted, that it is append-only, and
   what happens to a class the writ deletes.
5. **The seqlock has no memory-ordering statement and no retry bound.** §5 gives
   the protocol (`seq` odd while writing, reader retries while odd or changed) but
   not the barriers that make it correct on a weakly ordered reader, nor what a
   reader does after N failed retries, nor what `seq` wrapping past 2³² means.
6. **The margins have no saturation rule.** `int16` at 1/1024 logit spans ±32
   logits. A judge that produces ±40 must saturate, not wrap; §5 says only
   "quantized". Same question for `n_wit`, `n_wait` and `tie`, which are `uint16`
   counters with no stated behaviour at 65535.
7. **The hot walk still touches both cache lines.** `due_ns` is at 24 (line 0),
   `cls` at 96 and `state` at 114 (line 1). Not a defect — but §19's 5 ms for
   50,000 obligations assumes it, and the pad is now only 8 bytes, so the escape
   hatch O3 noted (move `cls`/`state`/`band` onto line 0) now costs a field move
   rather than pad.

### §4 · Lanes and the spool

8. **The `badenc` mark has nowhere to live.** §4 mandates that a frame carrying
   invalid UTF-8 "carries a badenc mark", but the frame is exactly seven fields
   and none of them is a mark; `grain` is a closed set of four. A mark that cannot
   be written is a mark no reader can read. Add an eighth field, or a flags field,
   or say the mark is a `refused`/`trunc`-style row on the tape rather than on
   the frame.
9. **`\xNN` is overloaded.** For `NN ≤ 0x1F` and `NN == 0x7F` it names a code
   point; under the badenc rule it names a raw byte. The two readings agree only
   below 0x80. `frame_roundtrip.py` resolves it as *`NN ≥ 0x80` is a raw byte and
   is legal only on a badenc frame*, and round-trips five invalid-UTF-8 fixtures
   under that rule — but §4 does not say it.
10. **`u64le(len)` does not say len of what.** Taken here as the byte length of
    the body: fields 1–6 with their tabs, escaped, excluding the tab before `h`,
    `h` itself and any terminating LF. Without the exclusions spelled out the
    definition is self-referential and two implementations will differ.
11. **The spool chain has no personalization.** §12 gives each keyed chain a
    personalization so a row cannot be lifted between chains. The spool chain is
    unkeyed and has none, so nothing domain-separates a spool line's preimage
    from any other unkeyed BLAKE2b-256 use. The `u64le(len)` prefix helps; a
    personalization would settle it, and costs nothing.
12. **The cursor's window has no defined job.** §4 says the cursor holds the end
    offset, the frame's chain value `h`, and "the byte length of the window
    hashed" — but nothing is hashed over a window in the same sentence, and the
    Spool law separately says the bytes before the cursor must "hash to the
    cursor's chain value", which is a property of the chain, not of a window.
    `chain_check.py` pins it as: the window bounds a **backwards re-read** that
    recovers the frame at the cursor and the one before it, so the chain value can
    be recomputed in O(window) rather than O(file). Under that reading a window
    shorter than two lines is unusable, and the harness reports it (measured: a
    158-byte window over 158-byte frames is refused).
13. **The cursor carries no generation, though every tape reference does.** §4's
    reference tuple is `(lane, generation, offset, h)` but the cursor's own
    sentence names only offset, `h` and window length. After a `spool-seal` a
    cursor with no generation points into the wrong file. Added here; add it to §4.
14. **The header's canonical JSON is not the same canonical JSON.** §4 calls the
    header "a canonical JSON object"; §12 defines canonical JSON with rules
    (64-bit integers as decimal strings, unknown keys fatal) written for the tape.
    `frame_cap`, `lag_ms` and `generation` are integers in the header. Say
    explicitly that §12's rules govern the header too, or the two will drift.
15. **The frame cap bounds one field, not the line.** §4 applies the cap to the
    encoded `text`; `venue`, `lane` and `grain` are uncapped, so the line length
    has no bound. Small, but a lane id from a grown adapter is attacker-shaped.

### §12 · The tape

16. **The personalization template overflows for at least one chain it names.**
    BLAKE2b caps `person` at 16 bytes. `"FACTOR tape v1"` is 14 and works;
    `"FACTOR dossier v1"` is **17** and `hashlib` refuses it with
    *maximum person length is 16 bytes* — and §12 names the dossier as a keyed
    chain in the same paragraph. Shorten the template (`"FACTOR/dossier/1"` is 16)
    or shorten the names. This is a boot-time crash in the current wording.
17. **`ms` is "beside the row" but §12's Rows sentence removes only `prev` and
    `h` from the body.** Two readings: `ms` is a key on the row object that the
    body excludes, or `ms` lives in a sidecar and never touches the JSON line.
    This harness takes the first. Say which; a verifier written to the other
    reading computes a different body and therefore a different head.
18. **"Every 64-bit integer as a decimal string" collides with "margins and
    amounts are fixed-point integers".** `amount_fix` is `int64`. Is it a string
    (declared width) or a number (magnitude below 2⁵³)? Decide by declared width
    or by magnitude and say which — this harness enforces both a declared-key
    list and a 2⁵³ magnitude backstop, which is stricter than either reading
    alone.
19. **The torn tail is unfalsifiable by construction.** Case three — valid JSON
    whose hash does not verify, in the last position — is indistinguishable from
    a forged tail that an attacker wants dropped. The verifier cannot tell them
    apart and must accept the earlier head either way. This is not a fixable
    property of a hash chain; it is why §12's *two witnesses of the head* exists,
    and §12 should say so where the torn rule is stated, so nobody implements the
    tear rule believing the head is self-evident.
20. **A broken link in the last position has no stated disposition.** The three
    torn cases do not include it. Taken here as fatal.
21. **`factor verify --chain-only` verifies something that is not defined.** The
    tape chain is **keyed**, so a verifier without the key can recompute no `h` at
    all. `--chain-only` must therefore verify a different, unkeyed structure — the
    "published fingerprint chain" — and §12 never defines it: what a fingerprint
    covers, how fingerprints are chained, at what cadence, and how one is bound to
    the keyed head it claims to attest.
22. **Compaction and the chain are not reconciled.** §12 permits compaction
    (operator-signed, after a class's expiry window plus one) and simultaneously
    requires that `factor verify` reproduce the head by walking segments. Removing
    a row breaks every subsequent `prev`. Say how a compacted span is replaced —
    a signed tombstone row carrying the removed span's first `prev` and last `h`
    is the usual answer — or compaction silently un-verifies the tape.
23. **§12's kind list is missing eight kinds §8 names.** §12 lists 49 kinds.
    §8's Events paragraph names `expired`, `lapsed`, `graduated`, `demoted`,
    `terminal` and (as `compiled` / `grown`, against §12's `compile` / `grow`)
    two more, plus the `repeat` row §8's Grain paragraph requires. An implementer
    building the kind enum from §12 will not emit them. One list, one place.
24. **The segment size bound is never given a number**, though "the bound is
    checked before the append" is load-bearing for "a row is never split across
    segments".
25. **`machine_secret` is undefined.** §12 derives every chain key from it and
    the Encryption paragraph separately describes a TPM-sealed key bound to the
    boot state and the kernel binary's hash. Are they the same value? If the seal
    is bound to the kernel binary's hash, every kernel upgrade changes the seal —
    say how existing segments and their keys survive an upgrade.

### §21 · Falsifiers

26. **Forty-five rows, and the brief for this pass said forty-six.** Reconcile.
27. **F-SELF is named by no §22 gate**, so nothing in the build order requires it
    to be written. M1 is the natural home — the `health` lane ships with the first
    lanes and F-SELF's requires is about a dead producer. Either gate it or say
    why it is ungated.
28. **M8 has no §21 falsifier.** Its three gate conditions are stated in prose in
    §22 and each would make a serviceable row: an absent organ degrades with code
    6, an organ child that opens a socket is refused, a widening ratify over the
    API is refused. (The last already overlaps F-MONOTONE's second clause.)
29. **F-EGRESS's M0 form is not defined.** §22 gates F-EGRESS at M0 and again at
    M3 "full", but F-EGRESS's `requires` mentions the hand's egress ledger (M3)
    and an organ child (M8). §22 tells us exactly which part of F-CONSERVE M0
    covers ("without the heard bucket") and should do the same here — presumably
    the three OS-refusal routes and the socket sample, without the ledger sum.
30. **Six thresholds are named and nowhere given.** `n0` (F-BOTH-SIDES), `N
    periods` (F-DARK), `self_share` (F-SELF), "the tolerance" (F-EXTRACT), "the
    tie band" (F-TICK, F-QUANTA), and F-DETECT's 500/40 are the only numbers in
    the table. A falsifier cannot be written against a threshold that has no
    value or no named home. Say, per row, that the threshold is declared in the
    writ and printed on the account.
31. **The `law` column mixes two numbering systems** — bare numbers (1, 3, 4, 6,
    7, 8, 9, 10, 11, 12, 13, 14, 19) and section references (§4, §5, §10, §13,
    §24) — with no key. If the bare numbers are §1's constitution clauses, say so
    at the head of the table.

---

## 7 · What this scaffold still does not do

Stated plainly so nobody mistakes green for finished.

* All 45 falsifiers are stubs. The scaffold proves the battery is *complete and
  wired to §21 and §22*, not that any property holds.
* `check_layout.py`, `frame_roundtrip.py` and `chain_check.py` test **models** of
  the record, the codec and the chains, not a kernel. `F_LAYOUT.py`,
  `F_FRAME.py` and `F_CHAIN.py` are the stubs that will wire the same properties
  to the built binary, and their docstrings say so.
* The chain harness generates its own tapes and spools. It does not exercise the
  AEAD, the TPM seal, the external witness, or compaction — items 21, 22 and 25
  above are unimplementable as tests until §12 defines them.
