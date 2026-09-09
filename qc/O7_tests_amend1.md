# O7 · THE TEST SCAFFOLD, RE-CUT AGAINST AMENDMENT 1 — checked by running code

Source of record: `BLUEPRINT_v0.2.md`, **Amendment 1 · 2026-09-08** at the bottom
of that file, read against §§4, 5, 12, 21 and 22. Previous pass:
`qc/O6_tests_v0.2.md`, whose §6 raised the thirty-one underspecifications the
amendment settles.

Everything below was produced by running the files, on this machine, today.

---

## Headline

**All four harnesses are green against the amended design.**

```
python C:/FACTOR/tests/check_layout.py         exit 0
python C:/FACTOR/tests/frame_roundtrip.py      exit 0
python C:/FACTOR/tests/chain_check.py          exit 0
python C:/FACTOR/tests/run_falsifiers.py       exit 0   94 TODO
```

**The frame is eight fields and the badenc mark finally has a home.** `f` carries
bit 0 `badenc`, bit 1 `truncated`, bit 2 `synthetic_rev`, the hash covers fields
one through seven, and the fifth planted lie — a decoder that accepts `\xNN`
above `0x7F` on a frame whose badenc bit is clear — is caught. All five lies are
caught; `STRICT` still gives zero `splitlines()` violations over 10,000 strings.

**All six personalization strings fit, and all six keys derive.** The
seventeen-byte `"FACTOR dossier v1"` that made `hashlib` refuse a key at boot in
O6 is gone; `FCTR-dossier-v1` is fifteen bytes. The longest of the six is fifteen.

**`verify --chain-only` now verifies something that exists**, and it does it with
a measured zero keyed recomputations. **A compacted span verifies to the same
head it had before compaction**, which is what item 20 was for.

**Two new findings this pass produced that Amendment 1 does not cover**, both
measured rather than argued:

1. **Item 2's rounding rule is not yet deterministic.** It pins round-half-even
   at the micro-unit but not the parse in front of it. Three of five tie cases
   land on *different* micro-unit integers depending on whether the source amount
   was parsed as a decimal or as a binary double — and §5 hashes that integer
   into a derived obligation's id.
2. **Items 19 and 20 collide.** Compacting a span that contains a `fingerprint`
   row leaves the keyed chain clean and the head unchanged, and breaks the
   fingerprint chain anyway. A keyless verifier and the external witness would
   both call a lawfully compacted tape forged.

---

## 1 · §4 · Frame codec — eight fields, 10,000 strings, five planted lies

`python C:/FACTOR/tests/frame_roundtrip.py` → **exit 0**

```
==============================================================================
FACTOR BLUEPRINT_v0.2 section 4 as amended -- frame codec property test
frame: 8 tab-separated fields, the sixth `f` the flags, the eighth the
       chain hash    (Amendment 1, items 8 to 14)
hash : BLAKE2b-256, unkeyed, person='FCTR-spool-v1', over prev_hex || u64le(len) || body
corpus: 10000 strings (seeded, deterministic) incl. 25 adversarial literals
==============================================================================

(0) THE FRAME, AS AMENDED
    fields                 : t_mono_ns venue lane grain rev f text h
    hashed body            : fields 1-7 with their tabs, escaped;
                             excludes the tab before h, h, and the LF
    f, the flag bits       : bit 0 badenc  bit 1 truncated  bit 2 synthetic_rev
    personalization        : 'FCTR-spool-v1' (13 bytes, limit 16)   PASS
    KAT personalized       : f682e7d6d8a4c0b0612903ab2672f9f6
    KAT unpersonalized     : 204d715e71bcc3d901f78d44474ee603
    domain separation      : PASS -- a plain unkeyed BLAKE2b-256 of the same
                             preimage does not verify as a spool line

profile STRICT (MANDATED by section 4)
  round trip, all 8 fields + chain hash : PASS  (10000/10000 passed)
  one line under a byte-level reader     : yes (checked per frame)
  one line under str.splitlines()        : yes (0 violations of 10000)
  chain head after 10000 frames          : 9ee302a46effd13b960f228b2c665738

profile MIN    (NOT legal in v0.2; run as the measurement)
  round trip, all 8 fields + chain hash : PASS  (10000/10000 passed)
  one line under a byte-level reader     : yes (checked per frame)
  one line under str.splitlines()        : NO (4632 violations of 10000)
  chain head after 10000 frames          : b313e9c9fe7dc3a1ef334102fcfc4444
     -> MIN lets these through raw: U+0000 U+000B U+000C U+001C U+001D U+001E
                                    U+0085 U+2028 U+2029
     -> 46.3% of this corpus triggers it.

MANDATORY: every escaped frame is ONE line under str.splitlines()
  STRICT violations : 0   PASS

invalid UTF-8, on a frame whose f sets bit 0, badenc -- items 8 and 9
  b'\xff\xfe'          -> '\\xff\\xfe'          f=5(badenc+synthetic_rev) roundtrip=True
  b'caf\xe9'           -> 'caf\\xe9'            f=5(badenc+synthetic_rev) roundtrip=True
  b'\xc3('             -> '\\xc3('              f=5(badenc+synthetic_rev) roundtrip=True
  b'ok\xed\xa0\x80end' -> 'ok\\xed\\xa0\\x80end' f=5(badenc+synthetic_rev) roundtrip=True
  b'\x80\x81\x82'      -> '\\x80\\x81\\x82'     f=5(badenc+synthetic_rev) roundtrip=True
  invalid-UTF-8 handling: PASS
  U+00E9/U+00FC as CODE POINTS on a frame with badenc clear : PASS -- written
                             as UTF-8, never as \xNN

field caps (amendment item 14, applied to the ENCODED field)
  venue / lane / grain cap : 64 bytes
  text cap                 : the header's frame_cap
  over-cap venue  : refused (venue is 65 encoded bytes, cap is 64)    PASS
  over-cap lane   : refused (lane is 69 encoded bytes, cap is 64)     PASS
  over-cap grain  : refused (grain is 120 encoded bytes, cap is 64)   PASS
  with a header frame_cap of 64, over 2000 corpus strings:
    encoded text fields over the cap : 0   PASS
    capped text decodes to a prefix of the source : 0 bad   PASS
    every truncation sets f bit 1, truncated      : 0 bad   PASS
  a line therefore has a bound: 370 bytes at frame_cap 64
    = 20 t_mono_ns + 3x64 venue/lane/grain + 20 rev + 3 f + 64 text
      + 64 h + 7 tabs

planted lies -- each MUST be caught
------------------------------------------------------------------------------
  LIE 1  encoder drops carriage returns       caught @ idx 7   decoded text differs
  LIE 2  encoder does not escape the backslash caught @ idx 1  decode raised:
                                              trailing backslash: escape truncated
  LIE 3  encoder escapes TAB before backslash  caught @ idx 5  decoded text differs
  LIE 4  decoder passes unknown escapes through caught @ idx 0 the permissive
                                              decoder accepted an unknown escape
  LIE 5  decoder accepts \xNN > 0x7F with badenc clear   caught
       frame text '\\xff\\xfe'  f=0 (badenc CLEAR)
       source bytes b'\xff\xfe'
       the blind decoder accepted it and produced '\ufffd\ufffd' with f=0

why the backslash must be escaped first, concretely:
   text            = '\\t'   (2 chars)
   LIE 2 encodes   = '\t'
   strict decode   = '<TAB>'  <- a TAB appeared out of nowhere
   STRICT encodes  = '\\\\t'
   strict decode   = '\\t'    <- identity

RESULT: ALL CHECKS PASS
```

**The fifth lie is the one the amendment bought.** Before item 8 the frame had
nowhere to carry `badenc`, so item 9's rule — `\xNN` at or above `0x80` is a raw
byte, legal only on a marked frame — had nothing to hang on and no decoder could
enforce it. LIE 5 builds a real eight-field line whose `text` carries
`\xff\xfe` while `f = 0`, and asserts two things at once: the strict decoder
refuses it, and a decoder that ignores the bit accepts it. If either half fails
the bit is decorative.

**The other half of item 9 is checked too**, and it is the half that is easy to
get wrong: `U+00E9` and `U+00FC` are code points, not raw bytes, and they travel
as UTF-8 on a frame with `badenc` clear. `esc_strict` never emits `\xNN` at or
above `0x80` for any input, which is exactly what makes item 9 consistent — an
escape in that range can only have come from a byte.

**MIN still fails 4632 of 10000**, the same count O6 measured on the seven-field
line, even though the corpus gained two adversarial literals — `"\\x80"`, which
looks like a raw-byte escape and is text, and `"éü"`, which is two code points in
the range item 9 reserves for raw bytes. The measurement that justifies STRICT is
where it was; the eighth field did not move it.

The two chain heads both moved from O6, as they must: the body gained a field and
the hash gained a personalization.

---

## 2 · §12 · Chains — six pinned keys, the fingerprint chain, the tombstone

`python C:/FACTOR/tests/chain_check.py` → **exit 0**

```
(0) KEYS -- one machine secret, one PINNED personalization per chain
    chain      person             bytes K_chain
    tape       'FCTR-tape-v1'     12    af2328b5890b125c3a999ce2132a92d7
    dossier    'FCTR-dossier-v1'  15    c5857cff88cfea29dda2aaa9c72237ff
    ledger     'FCTR-ledger-v1'   14    77163b84200b7a6c7549996e658bdcb1
    ckpt       'FCTR-ckpt-v1'     12    c308afa0890b858f5b41edeabc728eb1
    spool      'FCTR-spool-v1'    13    6b568ef89251d46770ca6bdef3b3b05e
    fprint     'FCTR-fprint-v1'   14    75b91e0fd35bf8c4c620dfafbc1cc086
    all six at most 16 bytes : PASS
    all six keys derived    : PASS   (6 distinct of 6)
    KAT keyed   H_tape(0*64 || u64le(12) || 'known-answer')
                = 2b7721c5ef40c2ab519d7890523f502d
    KAT unkeyed H_spool(same preimage)
                = f682e7d6d8a4c0b0612903ab2672f9f6
    KAT unkeyed H_fprint(same preimage)
                = 38306aa3dfd03c1d6f878c350eb879f7
    cross-chain transplant  : PASS -- a row of the tape chain does not verify
                              under another chain's key
    unkeyed separation      : PASS -- a spool line does not verify as a
                              fingerprint, and neither verifies as a plain
                              unkeyed BLAKE2b-256

(a) TAPE, keyed: h = H_k(prev_hex || u64le(len) || body)
    rows / segments        : 32 rows across 8 segments (8 of them fingerprints)
    chain crosses segments : yes
    filenames monotone     : seg-000001.jsonl .. seg-000008.jsonl
    head                   : a111198f708e4f78191092d632e0fb93
    verify clean tape      : PASS (0 errors)

(a1) MANIFEST IS A CACHE, NEVER TRUTH
     head with manifest.json deleted : a111198f708e4f78191092d632e0fb93
     head with it present            : a111198f708e4f78191092d632e0fb93
     same head both ways             : True                 PASS
     a manifest claiming a false head: CAUGHT by the walk

(a2) SEGMENT FILENAMES -- zero-padded and monotone
     renamed the last segment to seg-8.jsonl
     seg-8.jsonl: segment number is not zero-padded to 6, so filename order
                  stops matching numeric order                PASS
     largest segment       : 1502 bytes, bound 67108864 (checked before append)

(a3) TORN TRAILING ROW -- all three of section 12's cases
     no trailing LF        : 1 torn, 1 warn, 0 errors, head steps back  PASS
     undecodable JSON      : 1 torn, 0 errors, head unchanged           PASS
     valid JSON, bad hash  : 1 torn ("hash of a partially written row") PASS

(a4) A TORN ROW IN A NON-FINAL POSITION IS FATAL, NOT A WARN
     errors                : 2                                          PASS

(a5) FINGERPRINT CHAIN -- `verify --chain-only`, amendment item 19
     fingerprints on the tape : 8 -- one per segment close, and one every
                                4096 rows
     fingerprint head         : e6a7d9edacb678b9e59ac6f56fffcb2a
     internal consistency     : PASS (0 errors)
     agrees with the witness  : yes
     keyed h recomputations   : 0   PASS -- the tape key is never touched
     each fingerprint attests the head it follows : PASS
     a fingerprint with a swapped head, seen WITHOUT the key:
       errors               : 1 -> fingerprint SELF hash mismatch
       keyed recomputations : 0
       VERDICT              : CAUGHT
     a witness copy that disagrees : CAUGHT
     cadence on a 9,000-row tape in one segment:
       fingerprints         : 3 at rows 4096, 8193, 9002
       largest gap          : 4096 rows between fingerprints, cadence 4096  PASS

(a6) COMPACTION -- a signed tombstone replaces the span, item 20
     span replaced          : rows 4..8 (5 rows)
     tombstone carries      : span_prev 5ab359602f8129b1
                              span_h    94e0bc2134cce08c
                              count     5, operator-signed
     head before compaction : 25bdae0c052ae779e37dbcedb5070d93
     head after compaction  : 25bdae0c052ae779e37dbcedb5070d93
     same head              : True   PASS
     errors                 : 0
     tombstone with a WRONG last h, signature left stale:
       errors               : 2 -> tombstone signature does not cover
                              (span_prev, span_h, count) -- refused
       VERDICT              : REJECTED by the signature
     tombstone with a WRONG last h, RE-SIGNED by the operator:
       errors               : 1 -> LINK broken (prev=94e0bc2134cce08c ...)
       VERDICT              : REJECTED by the link
       head                 : 25bdae0c052ae779 -- UNCHANGED. One row's link
                              breaks and the walk re-syncs, so the head alone
                              never reveals it. The rejection is the error,
                              not the head.

(a7) A COMPACTED SPAN THAT CONTAINS A FINGERPRINT -- measured
     tape                   : 21 rows, fingerprints at [3, 7, 11, 15, 19, 20]
     compacted              : rows 6..8 (3 rows, one a fingerprint)
     keyed verify           : 0 errors, head 3464b0074f4312d9
     head unchanged         : True
     chain-only, before     : 0 errors, 6 fingerprints
     chain-only, after      : 1 errors, 5 fingerprints
       fingerprint LINK broken (fp_prev=f211e8c47efeabda
                                expected=ddd613f2500077c5)

(b1) PLANTED LIE 1 -- one byte modified mid-chain (offset 656)
     forged file still parses as JSON : True
     seg-000001.jsonl row 1: SELF hash mismatch (h=9bfadc1289790396
                                              want=f3609203555eaba1)   CAUGHT

(b2) PLANTED LIE 2 -- a row rewritten with its OWN hash recomputed
     verifier WITH link check    : 1 error(s)  CAUGHT
     verifier WITHOUT link check : 0 error(s)  MISSED  <- the bug the lie is for

(b3) PLAN HASH excludes ms, prev and h
     two runs, every ms different : True
     plan hash run A / run B      : 86265462925b0026... / 86265462925b0026...  PASS

(c) SPOOL self-chain, UNKEYED and personalized 'FCTR-spool-v1'
    frame                  : 8 fields, 7 of them hashed
    lines                  : 41 (1 header + 40 frames), 6617 bytes
    head                   : dbc34c9583a36ca568ed0cfac2296d6f
    verify clean spool     : PASS (0 errors)
    header with a BARE integer generation : refused   PASS
      $.generation is declared uint64 and must be a canonical decimal string
    PLANTED LIE 3 -- one byte flipped at offset 3308
      line 20: hash mismatch (have 66fba324f8b5ee78 want 2f04b2a7b2beaf65) CAUGHT
    generation 2 sealed from generation 1
      verify with g1 head as genesis : PASS (0 errors)
      verify with 64 zeros instead   : 1 error -- the seal is load-bearing

(d) CURSOR = (generation, offset, h, window_len)  -- item 12
    generation / off       : 1 / 3257
    h                      : 10ec609ed33f4e17c620438b750f78d4
    window_len             : 3257 bytes
    revalidate unchanged   : PASS
    SEALED into generation 2, same byte length (True) : PASS
      generation 2, the cursor was taken in generation 1 -- after a spool-seal
      this cursor points into the wrong file
    REPLACED spool, same byte length (True) : PASS
      chain value at the cursor changed: have 0f40ad44 want 10ec609e
    SHRUNK spool           : PASS (spool is SHORTER than the cursor 3247 < 3257)
    EDITED bytes before the cursor : PASS (no longer hash to its chain value)
    window of exactly one line (160 bytes) : reported -- too short to hold the
      preceding line, so the chain value cannot be recomputed

(e) CANONICAL JSON, by DECLARED WIDTH (item 17)
    34 keys declared: 18 at 64-bit -> decimal string, 16 narrower
    bare float                   refused   PASS
    NaN                          refused   PASS
    amount_fix as a number       refused   PASS
    amount_fix as a string       accepted  PASS
    t_mono_ns as a number        refused   PASS
    t_mono_ns as a string        accepted  PASS
    rev as a number              refused   PASS
    an id as a string            accepted  PASS
    an id with a leading 0       refused   PASS
    m_hand as a number           accepted  PASS
    m_hand as a string           refused   PASS
    m_hand out of int16          refused   PASS
    undeclared small int         accepted  PASS
    unknown key                  refused   PASS

RESULT: ALL CHECKS PASS
```

Five things about this run are worth naming.

**The dossier key exists now.** O6's run printed `K_dossier derivable : NO --
maximum person length is 16 bytes`, which was a boot-time crash in the published
wording. Item 15's six strings are 12, 15, 14, 12, 13 and 14 bytes. All six keys
derive and all six are distinct.

**`--chain-only` is proved keyless, not asserted keyless.** Every call to
`keyed_h` increments a counter. The chain-only walk is bracketed by reads of that
counter and reports `keyed h recomputations : 0`. The same counter reads 0 while
catching a fingerprint whose attested head was swapped — so the keyless verifier
has teeth without the key, which is the entire point of item 19.

**The fingerprint is bound to the keyed head two ways.** `head` is inside the
fingerprint's hashed body, so tampering with it breaks the unkeyed chain a
keyless verifier can walk; and the keyed verifier separately refuses a
fingerprint whose `head` is not the `prev` it actually follows. Item 19 asks how
a fingerprint is "bound to the keyed head it claims to attest" and this is the
cheapest answer that works from both sides.

**Compaction preserves the head, which is the whole assertion.** §12 requires
`factor verify` to reproduce the head by walking segments, and removing rows
breaks every subsequent `prev`. The tombstone carries both endpoints; the walk
enters at `span_prev`, leaves at `span_h`, and the final head is byte-identical
to the head of the tape the span was cut from. Both rejection cases are tested,
and they are caught by *different* mechanisms — a stale signature by the
signature, a re-signed lie by the link — which is why both are worth having.

**A re-signed tombstone does not move the head.** Only one row's link breaks and
the walk re-syncs on the next row, so a verifier that compares heads and ignores
errors would see nothing. That is a general property of link-checking and it is
worth saying out loud: the head is not a substitute for the error list.

---

## 3 · §5 · Layout — unchanged, and the micro-unit block

`python C:/FACTOR/tests/check_layout.py` → **exit 0**

The record is untouched by Amendment 1, and the run confirms it: item 2 changes
the *scale* `amount_fix` counts, not its width or its offset.

```
  [1] sizeof == 128          : measured 128   PASS
      alignof == 8           : measured 8     PASS
      128 is two 64-byte cache lines : True
  [2] every pinned offset  : 29 of 29 match   PASS
  [3] no internal hole     : 0 hole byte(s)   PASS
      no trailing ABI pad    : 0 byte(s)      PASS
      named bytes == sizeof  : 128 vs 128     PASS
      fields straddling a cache line: none

  [4] PLANTED LIE -- section 21 F-LAYOUT: 'the v0.1 claim asserted'
      the lie asserts sizeof(v0.1 record) == 128
      measured                              == 120
      VERDICT: CAUGHT

  offsets(json) = {"id": 0, "party": 8, "opened_ns": 16, "due_ns": 24,
    "horizon_ns": 32, "blocked_by": 40, "src_rev": 48, "judged_rev": 56,
    "release_ns": 64, "amount_fix": 72, "seq": 80, "m_hand": 84, "m_check": 86,
    "m_guard": 88, "n_wit": 90, "n_wait": 92, "tie": 94, "cls": 96, "band": 100,
    "seat": 104, "unit": 108, "flags": 112, "state": 114, "verb": 115,
    "reason": 116, "gear": 117, "kind": 118, "rung": 119, "_pad": 120}
```

The 29-row field table is byte-for-byte what `O6_tests_v0.2.md` §1 printed; the
only block that changed is this one:

```
  amount_fix: int64, an integer count of MICRO-UNITS, 10^-6 of `unit`
              (Amendment 1 item 2; the layout above is unchanged by it)
    range              : -9223372036854.775808 to 9223372036854.775807 units
                         about +-9.2 trillion units, either way
    a cent             : exactly 10000 micro-units
    decimal    micro-units      exactly representable
    0.01       10000            yes
    0.10       100000           yes
    19.99      19990000         yes
    500.00     500000000        yes
    all four exactly representable : PASS
    rounding: round-half-even to the micro-unit, applied once at ingest
    units        x 10^6       half-even    half-up (NOT the rule)
    0.0000005    0.5000000    0            1   <- two ids
    0.0000015    1.5000000    2            2
    0.0000025    2.5000000    2            3   <- two ids
    0.0000011    1.1000000    1            1
    -> where the two columns differ, two extractors that picked different
       rounding mint two obligations for one promise. That is why item 2 pins
       the rule and pins it AT INGEST, once.

  the rounding rule is pinned; the PARSE in front of it is not
    source text    decimal      via double   differ
    0.0000005      0            0
    0.0000025      2            3            YES
    1.0000005      1000000      1000001      YES
    19.9900005     19990000     19990001     YES
    0.1234565      123456       123456
    3 of 5 tie cases land on different micro-unit integers
    -> 0.0000025 as a double is exactly
       0.00000250000000000000020450763478507827386465578456409275531768798828125,
       which is ABOVE the tie, so half-even rounds it up to 3 while the decimal
       2.5 rounds to the even 2. Nothing is a tie once it has been through a
       binary float, and which side it lands is luck.
       Section 5 hashes the micro-unit integer into a derived id, so item 2 must
       also say the amount is parsed as a DECIMAL, once, before it is rounded.
       Otherwise the rule is not deterministic.
```

O6's version of this block reported that a cent *cannot be represented* at
1/65536 and that no rounding rule existed. Both are fixed. What replaced them is
a smaller but real gap, measured above and carried into §6 below.

---

## 4 · §21 · Falsifier scaffold — 47 files, runner green

`python C:/FACTOR/tests/run_falsifiers.py` → **exit 0**

```
  TODO 94

  by section 22 gate
    M0     8   F-CHAIN F-CONSERVE F-DETERMINISM F-EGRESS F-FRAME F-LAYOUT
               F-PIN F-REPLAY
    M1     9   F-BLIND F-BUDGET F-INERT F-INERT-BYTES F-QUANTA F-RESIDENT
               F-RIPEN F-SELF F-SILENCE
    M2     2   F-EXTRACT F-STANDING
    M3     2   F-ORDER F-WINDOW
    M4    10   F-BOTH-SIDES F-CANARY F-COVERED F-DETECT F-EXPIRY F-MONOTONE
               F-PREDICT F-SALT F-TERMINAL F-WITNESS
    M5     3   F-CAP F-FAMILY F-JURY
    M6     5   F-CONTRADICT F-DARK F-DEGRADE F-FRONT F-REDACT
    M7     5   F-COMPILE F-MOLT F-ROLLBACK F-ROLLBACK-MONOTONE F-TICK
    M8     2   F-ORGAN-DEGRADE F-ORGAN-NET
    M9     1   F-OBSERVE

RESULT: scaffold intact -- 94 of 94 functions are stubs (TODO),
        0 implemented and passing
```

**The `none` row is gone and M8 is no longer empty.** Amendment 1 item 24 gates
F-SELF at M1 and adds the two M8 rows, so every one of the forty-seven now sits
behind a milestone and the runner's gate column matches §22 plus the amendment
for all forty-seven. The runner still refuses a module whose `ID` or `MILESTONE`
disagrees with its row, so F-SELF's move from `none` to `M1` had to be made in
both places or the run would have exited 1.

The two new stubs carry item 24's `requires` and planted lie verbatim and the
same two-function contract as the other forty-five.

---

## 5 · Files

Under `C:\FACTOR\tests\` — **54 files** where there were 52 (O6 counted 51;
`msvc_check.cmd` was added after that pass and is untouched here).

**Created (2)**

| file | id | gate |
|---|---|---|
| `F_ORGAN_DEGRADE.py` | F-ORGAN-DEGRADE | M8 |
| `F_ORGAN_NET.py` | F-ORGAN-NET | M8 |

**Rewritten (2)**

* `frame_roundtrip.py` — eight fields; `f` and its three flag bits; the hash over
  fields 1–7 personalized `FCTR-spool-v1`; item 9's `\xNN` rule in both the
  str-level and a new byte-exact decoder; per-field caps and the printed line
  bound; the invalid-UTF-8 fixtures now travel on frames that carry the mark; a
  fifth planted lie. The 10,000-string corpus, the `splitlines()` gate, the MIN
  measurement and the first four lies are kept.
* `chain_check.py` — the six pinned personalizations and all six keys; the
  fingerprint chain, `verify_chain_only` and the keyed-call counter that proves
  it keyless; the witness file and its disagreement case; the signed tombstone,
  compaction, and both rejection cases; the (a7) measurement; the cursor as
  `(generation, offset, h, window_len)` with a generation check; canonical JSON
  by a declared-width table; the spool rebuilt on the eight-field frame. The
  three planted lies, the torn cases, the manifest and segment rules and the plan
  hash are kept.

**Changed (48)**

* `check_layout.py` — the informational `amount_fix` block only. The `SPEC`
  table, the assertions and the planted lie are untouched.
* `run_falsifiers.py` — forty-seven rows; F-SELF `none` → `M1`; the two M8 rows
  appended; the gate notes rewritten against item 24.
* `README.md` — the three Amendment 1 changes up front; the harness table; the
  falsifier table at forty-seven with the two new rows; the gate table with M1 at
  9, M8 at 2 and the `none` row removed; the two §21/§22 mismatches recorded as
  closed; `94 TODO`.
* `F_SELF.py` — `MILESTONE` `"none"` → `"M1"`, and the docstring's gate note
  rewritten.
* 44 falsifier stubs — the one stale line *"Contract, identical for all
  forty-five falsifiers"* → *forty-seven*. No other change; no `ID`, `MILESTONE`,
  `REQUIRES` or `PLANTED_LIE` was touched.

**Deleted: none.** **`layout_check.cpp` and `msvc_check.cmd` are untouched** —
the record layout is unchanged, so the compile-time assertions still hold and
`-DPROVE_SPEC_FAILS` still fails to build.

### Re-running everything

```
python C:/FACTOR/tests/check_layout.py         # exit 0
python C:/FACTOR/tests/frame_roundtrip.py      # exit 0
python C:/FACTOR/tests/chain_check.py          # exit 0
python C:/FACTOR/tests/run_falsifiers.py -v    # exit 0, 94 TODO
```

---

## 6 · Where Amendment 1 is still ambiguous for an implementer

Twenty-two items. The amendment closed thirty-one gaps; these are what a person
sitting down to implement §§4, 5, 12, 21 against the amended file would still
have to invent. The first two are the ones that change bytes.

### The two that change bytes

1. **Item 2 pins the rounding mode but not the parse in front of it.**
   Round-half-even is only defined once you know what is being rounded. An
   extractor that parses `"0.0000025"` into a binary double and then rounds
   half-even gets **3**; one that parses it as a decimal gets **2**. Measured:
   **three of five tie cases diverge** (§3 above). Because §5 hashes the
   micro-unit integer into a derived obligation's id, the two extractors mint two
   obligations for one promise — which is the exact failure item 2 was written to
   prevent. **Say that the amount is parsed as a decimal, once, before it is
   rounded**, and say what happens to a source that supplies a float.

2. **Items 19 and 20 collide over compaction.** Item 20 makes the tombstone the
   link for the keyed chain. It says nothing about the unkeyed fingerprint chain,
   and nothing exempts a `fingerprint` row from a compacted span. Measured in
   (a7): compacting a span containing one fingerprint leaves the keyed verify at
   **0 errors with the head unchanged**, and leaves `--chain-only` reporting a
   **broken fingerprint link**. A keyless verifier, and the external witness whose
   copy `--chain-only` must agree with, would both call a lawfully compacted tape
   forged. Either compaction never removes a fingerprint, or the tombstone
   carries the fingerprint chain across too — and whichever it is, the tombstone
   needs a place to say so.

### §4 · the frame

3. **`f`'s wire form is not pinned.** This harness demands canonical decimal, no
   sign, no leading zero, so `"007"` and `"+7"` are refused. The field is inside
   the hashed body, so two encoders that spell the same flags differently produce
   two chain hashes for one frame.

4. **Unknown bits of `f` have no stated disposition.** Bits 3 and above are
   refused here, by analogy with §4's "an unknown grain … is a refused frame".
   Reserved-and-ignored is equally readable from item 8, and the two differ the
   first day a grown lane emits a bit this build has never seen.

5. **Nothing says who sets `truncated`, or how it relates to the `trunc` row.**
   §4 already requires a `trunc` row carrying the dropped count. Bit 1 now
   duplicates that row's existence without duplicating its count. Nothing says
   the two must agree or which is authoritative when they do not.

6. **Does item 9's badenc gate cover every field or only `text`?** Item 9 is
   written frame-wide ("legal only on a frame with `badenc` set") and is applied
   to all seven body fields here. A `venue` or `lane` carrying a raw byte is the
   attacker-shaped case, so frame-wide is the safe reading — but §4's escaping
   paragraph reaches invalid UTF-8 only through `text`.

7. **Item 14 caps three fields and refuses; it does not say to truncate.** An
   over-cap `venue`, `lane` or `grain` is a refused frame here, matching §4's
   treatment of a lane id outside the declared pattern, while an over-cap `text`
   is truncated with a count. That asymmetry is a decision the amendment does not
   record.

8. **The line bound depends on unstated field widths.** Item 14 says "a line
   therefore has a bound", and it does — 370 bytes at a 64-byte frame cap — but
   only once you assume `t_mono_ns` and `rev` are decimal u64 (20 bytes) and `f`
   is at most three digits. None of the three is capped by the amendment.

### §12 · the tape

9. **The fingerprint row's shape is not given.** Item 19 says a fingerprint
   "carr[ies] the keyed head, the segment number and the row index" and that
   fingerprints "form their own unkeyed chain", but not which fields the
   fingerprint hash covers. This file hashes `{head, row, seg}` and carries
   `fp_prev`/`fp_h` beside them. Any other split is a different fingerprint chain
   over the same tape, and the witness cannot tell the two apart.

10. **`seg` and `row` have no declared width**, and item 17 decides by declared
    width. Both are unbounded monotone counters, so they are decimal strings
    here; "small counters are numbers" reads the other way.

11. **Item 13 and item 17 pull against each other on the header.** Item 13 says
    the header obeys §12 "integers as decimal strings included"; item 17 says
    decimal strings are for 64-bit fields. `frame_cap` and `lag_ms` are integers
    and are not 64-bit. They are numbers here and `generation` is a string.

12. **The pinned enums have a declared width but no declared spelling.** `verb`,
    `reason`, `state`, `gear` and `kind` are `uint8` in §5, and §12 never says
    whether a tape row writes the number or the name. The plan hash covers `verb`
    and `reason`, so the two spellings are two plan hashes — and F-DETERMINISM
    compares plan hashes.

13. **Is `batch` an id?** Item 17 says "every id" is a decimal string; §12 calls
    the plan hash's field a "batch id". It is a decimal string here, which
    changes the plan-hash preimage. Say whether "id" means the `uint64` identity
    fields of §5 or anything the prose calls an id.

14. **Item 20 does not say what the operator's signature covers.** It covers
    `(span_prev, span_h, count)` here. A signature over fewer fields lets one
    endpoint be moved under a valid signature, which is exactly the case (a6)'s
    second rejection tests.

15. **The tombstone's own `h` has no stated job.** The chain continues from
    `span_h`, so nothing downstream links to the tombstone's own hash. It is
    verified here as a self-integrity value; whether a verifier must is unstated.

16. **The witness's copy has no defined form.** `--chain-only` must verify "its
    agreement with the witness's copy", so the console publishes *something* — a
    list of `fp_h` here — but item 19 does not say what, nor what a disagreement
    is (a `warn`, a `fatal`, or a refusal to verify).

17. **The 4,096 cadence is not defined precisely enough to check.** Does a
    fingerprint row count toward its own cadence? Does the counter reset at a
    segment close? Both are counted here, and the checkable form is the gap
    between fingerprints, which the run reports as 4096.

### §21 and the amendment itself

18. **Item 24 gives the two new rows no `law` column**, though every other row in
    §21 has one and item 27 has just declared what the column means. The stubs
    record `§16` for F-ORGAN-DEGRADE and `5, §16` for F-ORGAN-NET as a reading.

19. **§22's third M8 gate condition still has no falsifier.** Item 24 adds rows
    for two of M8's three prose gates; "a widening ratify over the API is
    refused" is covered only by F-MONOTONE's second clause, which is gated at M4.
    O6 item 28 noted the overlap; the amendment neither adds the row nor says the
    overlap suffices.

20. **The preamble says thirty-one, and twenty-seven numbered items follow.**
    They do reconcile — O6's 12 and 13 merge into item 12, its 19 and 20 into
    item 18, its 26, 27 and 28 into item 24 — but nothing in the amendment says
    so, so a reader auditing coverage cannot tell which O6 item was settled where,
    or whether four were dropped.

21. **"Files changed by this amendment: none in place" leaves the body of the
    blueprint contradicting its own amendment in at least five places.** §4 still
    shows a seven-field frame and no `f`; §5's C listing still comments
    `amount_fix` as `1/65536 of unit`; §12 still writes the withdrawn
    `"FACTOR <chain> v1"` template; §12's kind list still lacks the nine kinds
    item 21 adds; §21's table still has forty-five rows, and §22's M1 gate still
    does not name F-SELF while its M8 gate still names three prose conditions
    rather than the two falsifiers item 24 created for them.
    An implementer reading top to bottom meets the wrong text first, and the
    amendment is 800 lines below it. This is the largest practical hazard in the
    file and it is a documentation decision, not a design one.

22. **Item 26 names where the thresholds live but not what they are called.**
    "Declared in the writ's `[test]`, `[walk]` and class stanzas" fixes the home;
    a falsifier still cannot read `n0`, `self_share`, the dark-quota period, the
    extraction tolerance or the tie band without the key names. The falsifiers
    that need them stay unwritable until the writ schema is pinned.

---

## 7 · What this scaffold still does not do

Stated plainly so nobody mistakes green for finished.

* **All forty-seven falsifiers are stubs.** The scaffold proves the battery is
  complete and wired to §21, §22 and Amendment 1 item 24, not that any property
  holds.
* `check_layout.py`, `frame_roundtrip.py` and `chain_check.py` test **models** of
  the record, the codec and the chains, not a kernel. `F_LAYOUT.py`, `F_FRAME.py`
  and `F_CHAIN.py` are the stubs that will wire the same properties to the built
  binary.
* **Item 1's id hash is not exercised anywhere.** `BLAKE2b-64` with
  `digest_size = 8`, unkeyed, over `(source, table, key)` is now unambiguous, and
  no harness computes one. It belongs with the extractor at M2.
* **Items 3, 4, 5, 6 and 7 are untested**: the ISO-4217 mapping and the
  sub-1000 reservation, the append-only class table, the seqlock's ordering and
  its 64-retry bound, margin saturation at ±32767 with flag bit 13, and the 5 ms
  hot-walk budget. All five need a kernel or a concurrent reader; none is a
  format question this scaffold can reach.
* **Item 23's TPM seal and `factor reseal` are untested.** The chain harness
  generates its own tapes and spools with a fixture secret; it does not exercise
  the AEAD, the seal, or a kernel upgrade.
* The external witness is modelled as a file. `--chain-only` checks agreement
  with it, which is item 19's requirement, but nothing here proves the witness is
  append-only or that the box cannot rewrite it.
* The tombstone's signature is a keyed BLAKE2b under a fixture key, not the
  operator's real signature scheme, which §12 does not name.

---

## 8 · A note on what the file said while this ran

`BLUEPRINT_v0.2.md` grew during this pass. It was 112,816 bytes when this pass
started and 115,320 when it finished: **Amendment 2 · The sandbox law, measured**
was appended by another hand at 13:54, from
`receipts/M0_SANDBOX_PROBE_2026-09-08.md`.

**Amendment 1 is byte-identical across that change** — items 1 to 27 and the
closing paragraph are exactly the text this pass was cut against — so nothing
above is stale.

**This pass does not cover Amendment 2**, which is about §11's sandbox mechanism,
§7's card measurement and the pipe descriptor, none of which these three
harnesses model. One line in it does reach §21 and should be folded into the
stubs by whoever takes the next pass:

> Amendment 2's fifth bullet carries a residual into **F-EGRESS**: the raw
> `\Device\Afd` open is denied but `\Device\Afd\Endpoint` opens inside the
> container, and the probe did not drive the `AFD_CONNECT` IOCTL, so that route
> is established by inference. The kernel's compiled-in F-EGRESS probe must drive
> the IOCTL and observe the refusal, and until it does the M0 receipt reads
> `afd: inferred`.

`F_EGRESS.py`'s stub message names three OS-refusal routes without naming the
IOCTL, and `F_ORGAN_NET.py`'s names "a raw device control". Neither is wrong;
both would be sharper for saying which device control, and F-EGRESS's should
carry the `afd: inferred` condition explicitly. Left alone here because this pass
was scoped to Amendment 1.

**Follow-up, later on 2026-09-08 — folded in.** The note above is closed, under
`C:\FACTOR\tests\` only; neither BLUEPRINT file was touched.

* `F_EGRESS.py` — `requires()` and `planted_lie()` now name the three routes as
  Amendment 2 measured them: the socket library, refused with `WSAEACCES`
  (10013); a connect to a live loopback listener, refused with `WSAETIMEDOUT`
  (10060), a timeout and not a fast refusal; and the raw device control, the
  `AFD_CONNECT` IOCTL driven over a handle from `NtCreateFile` on
  `\Device\Afd\Endpoint`, which opens inside the container while the raw
  `\Device\Afd` open is denied with `0xC0000022`. Both messages state that the
  falsifier must drive the IOCTL itself and observe the refusal as the status
  the filter returns, never infer it from the open; that the M0 receipt reads
  `afd: inferred` until it does; and that inferring the third route from the
  open is the second shape of the planted lie. The status the IOCTL will return
  is deliberately not pinned, because nothing has observed it yet. The
  docstring records the mechanism in force — `os-enforced`, a zero-capability
  AppContainer with `PROCESS_CREATION_CHILD_PROCESS_RESTRICTED` — and, as this
  file's reading of §22's M0 deliverable "the sandbox mechanism on the header
  row", `requires()` now also reads the header row's word against the refusals
  it observed: `lint-only` standing in for `os-enforced` is the module-list lie
  in §21's own words. `ID`, `MILESTONE`, `REQUIRES` and `PLANTED_LIE` are
  untouched, because §21's row did not change.
* `F_ORGAN_NET.py` — "a raw device control" is now the same `AFD_CONNECT` IOCTL
  over a `\Device\Afd\Endpoint` handle, with the same two error codes on the
  other two routes, because a `net: none` organ is spawned by the launcher into
  the same container under the kernel's package SID; the kernel itself cannot
  spawn it, by the launch attribute. The organ probe drives the IOCTL again from
  the organ rather than taking F-EGRESS's M0 observation on trust. Constants
  untouched.
* `README.md` — an Amendment 2 paragraph up front recording the mechanism in
  force and the `afd: inferred` residual; row 16 of the falsifier table names
  the three routes; a note under the gate table on the M0 header-row
  deliverable; a pointer to this note.
* Nothing else needed the mechanism recorded: a grep over `tests/` for
  sandbox, os-enforced, header row, mechanism, Afd and WSAE hits only the two
  stubs and the README. `chain_check.py` models the spool's header line, not
  the boot header row that carries the word. `run_falsifiers.py` is untouched.
* Both docstrings became raw strings and the messages double their backslashes:
  on Python 3.13 a bare `\D` in an ordinary string is a SyntaxWarning, and
  `python -W error run_falsifiers.py --gate M0` would have turned it into an
  `ERROR` and an exit 1. That strict run exits 0.

```
python C:/FACTOR/tests/run_falsifiers.py       exit 0   94 TODO
```

The file has grown again since this section was written: 116,928 bytes at
13:57, carrying **Amendment 3 · Two findings from the re-cut tests**, sourced
from §6 items 1 and 2 above. This follow-up does not fold Amendment 3 into
`check_layout.py` or `chain_check.py` — the decimal parse becomes a falsifier
fixture with a through-a-double parser as its lie, and `factor compact` must
refuse a span containing a fingerprint row — because it was scoped to Amendment
2. That is the next pass, and the README says so.
