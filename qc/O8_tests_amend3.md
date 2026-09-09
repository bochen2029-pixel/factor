# O8 · AMENDMENT 3 FOLDED INTO THE HARNESSES — checked by running code

Source of record: `BLUEPRINT_v0.2.md`, **Amendment 3 · 2026-09-08 · Two findings
from the re-cut tests**, at the very end of that file. Previous pass:
`qc/O7_tests_amend1.md`, whose §3 and §2(a7) measured the two findings and whose
§6 items 1 and 2 are what Amendment 3 settles.

Everything below was produced by running the files, on this machine, today.
Nothing outside `C:\FACTOR\tests\` was modified.

---

## Headline

**Both findings are now checks, and every harness is green.**

```
python C:/FACTOR/tests/check_layout.py                  exit 0
python C:/FACTOR/tests/chain_check.py                   exit 0
python C:/FACTOR/tests/frame_roundtrip.py               exit 0
python C:/FACTOR/tests/run_falsifiers.py                exit 0   94 TODO
python -W error C:/FACTOR/tests/run_falsifiers.py --gate M0
                                                        exit 0   16 TODO
```

**Item 1 is a parser, not a note.** `check_layout.py` grew block `[5]`: an amount
is parsed from its text as a decimal by digit arithmetic, scaled to micro-units
and rounded half-even at the seventh decimal place, with no floating-point value
anywhere — and that last clause is asserted by walking the parser's own AST
rather than by trusting its comments. Eighteen fixtures, O7's five among them,
all parse to their expected integers. The planted lie — the same rule applied to
the double the text parses to — differs on **eight of the eighteen**, and the
check **fails** if it ever differs on none, because a fixture set the double path
agrees with everywhere would be measuring nothing.

**Item 2 is a refusal, not a measurement.** `chain_check.py` gained
`compaction_refusal`, the typed `CompactionRefused`, and a bracket check on the
keyless side. `factor compact` now replaces only rows strictly between two
fingerprints, refuses anything else before it writes a byte, and after a lawful
compaction **the keyed chain reaches the same head, the fingerprint chain
verifies, and `verify --chain-only` reports zero errors**. O7's (a7) measurement
is now planted lie 4; the other half of the rule is planted lie 5. Both are
caught by `--chain-only` alone while the keyed chain and its head stay clean.

**One consequence worth stating up front: Amendment 3 item 2 makes O7's own
(a6) fixture unlawful.** O7 compacted rows 4..8 of a twelve-row tape whose only
fingerprint was the one at its close — no fingerprint before the span, so under
item 2 there is no lawful span on that tape at all. The fixture had to move to a
tape with a dense cadence. Any implementation carrying O7's fixture forward will
find the same thing.

---

## 1 · Amendment 3 item 1 · the amount parse

`python C:/FACTOR/tests/check_layout.py` → **exit 0**

Blocks `[1]` to `[4]` — sizeof 128, alignof 8, 29 of 29 pinned offsets, zero
hole bytes, zero trailing ABI pad, and the v0.1 planted lie caught at 120 bytes —
print byte-for-byte what O7 §3 printed. The record is untouched. What is new:

```
  [5] AMENDMENT 3 ITEM 1 -- the amount is parsed from its TEXT as a
      decimal, by digit arithmetic, rounded half-even at the 7th place
      (section 5 hashes the micro-unit integer into a derived id, so
       the parse is identity-bearing, not cosmetic)

      source text              expected         decimal      via double differ  what it pins
      0.0000005                       0               0               0         O7  tie -> even 0
      0.0000025                       2               2               3 YES     O7  tie -> even 2
      1.0000005                 1000000         1000000         1000001 YES     O7  tie -> even
      19.9900005               19990000        19990000        19990001 YES     O7  tie -> even
      0.1234565                  123456          123456          123456         O7  tie -> even
      0.0000015                       2               2               2         tie UP, q odd
      0.0000035                       4               4               3 YES     tie UP, q odd
      0.0000045                       4               4               5 YES     tie DOWN, q even
      -0.0000025                     -2              -2              -3 YES     negative, tie DOWN
      -0.0000015                     -2              -2              -2         negative, tie UP
      -19.9900005             -19990000       -19990000       -19990001 YES     negative, tie DOWN
      -0.0000005                      0               0               0         negative -> zero
      0.00000250000001                3               3               3         14 places, above tie
      0.00000249999999                2               2               2         14 places, below tie
      1.23456789012345          1234568         1234568         1234568         14 places, 7th is 8
      12345678.9012345   12345678901234  12345678901234  12345678901235 YES     large, tie -> even
      0.01                        10000           10000           10000         a cent, no rounding
      19.99                    19990000        19990000        19990000         the writ's amount
      18 fixtures, 18 parsed to the expected integer      PASS
      digit arithmetic == exact decimal rounding on all 18   PASS
      forms REFUSED, never coerced:
        '1e-6'         refused: 'e' is not an ASCII digit
        '1.2.3'        refused: more than one decimal point
        ''             refused: empty
        '1,234.00'     refused: ',' is not an ASCII digit
        ' 1.00'        refused: ' ' is not an ASCII digit
        '1.'           refused: a decimal point with no digits after it
        '.5'           refused: no digits before the decimal point
        '\u0661.\u0665' refused: '\u0661' is not an ASCII digit
      8 of 8 refused with the typed error                PASS
      no floating point in the parser, by walking its own AST:
        float/complex literals   : 0
        float/complex/Decimal, or a reach for a float's bits : 0
        true division (the one operator that makes one) : 0
        VERDICT: PASS -- the rule is enforced by the code, not by its comments

      PLANTED LIE -- the same rule applied to the double the text
      parses to. Both paths hand a rational to the SAME half-even
      rounder, so the parse is the only difference between them.
        fixtures where the double path differs : 8 of 18
        VERDICT: CAUGHT -- the fixtures exercise Amendment 3 item 1
        why: 0.0000025 as a double is exactly
             0.00000250000000000000020450763478507827386465578456409275531768798828125,
             which is ABOVE the tie, so half-even rounds it up to 3
             while the decimal 2.5 rounds to the even 2. It cuts both
             ways: 0.0000035 as a double is BELOW its tie, so the
             double rounds down to 3 where the decimal rounds up to
             4. Nothing is a tie once it has been through a binary
             float, and which side it lands on is luck.
        these fixtures are F-EXTRACT's: the extractor is where an
        amount text becomes the micro-unit integer section 5 hashes
        into a derived obligation's id.
```

And the closing line of the run:

```
RESULT: PASS -- section 5's record is 128 bytes, alignof 8, every offset
        as pinned, no implicit padding anywhere, planted lie caught;
        18 amount fixtures parse to their expected micro-unit integers
        by decimal digit arithmetic, and the double path is caught
        differing on 8 of them (Amendment 3 item 1).
```

### The fixtures

O7's five are fixtures 1 to 5 and reproduce O7's measured integers exactly,
which matters because they were reached by a different mechanism: O7 used
`Decimal` and `quantize`, this pass uses integer digit slicing cross-checked
against exact-rational rounding. Two independent implementations, the same five
answers. The other thirteen are what item 1 needs exercised and O7 did not carry.

| # | source text | expected micro-units | via double | what it pins |
|---|---|---|---|---|
| 1 | `0.0000005` | 0 | 0 | O7. tie, `q` even, rounds down |
| 2 | `0.0000025` | 2 | **3** | O7. tie down; the double is above the tie |
| 3 | `1.0000005` | 1000000 | **1000001** | O7. tie down; a whole-unit amount |
| 4 | `19.9900005` | 19990000 | **19990001** | O7. tie down; the writ's amount plus a tie |
| 5 | `0.1234565` | 123456 | 123456 | O7. tie down; the double happens to agree |
| 6 | `0.0000015` | 2 | 2 | tie **up**, `q` odd; the double agrees |
| 7 | `0.0000035` | 4 | **3** | tie **up** while the double rounds **down** |
| 8 | `0.0000045` | 4 | **5** | tie **down** while the double rounds **up** |
| 9 | `-0.0000025` | -2 | **-3** | negative; half-even is symmetric about zero |
| 10 | `-0.0000015` | -2 | -2 | negative, tie up |
| 11 | `-19.9900005` | -19990000 | **-19990001** | negative, long, tie down |
| 12 | `-0.0000005` | 0 | 0 | a negative that rounds to zero; the sign vanishes |
| 13 | `0.00000250000001` | 3 | 3 | 14 places; **the digits past the 7th break the tie** |
| 14 | `0.00000249999999` | 2 | 2 | 14 places; below the tie |
| 15 | `1.23456789012345` | 1234568 | 1234568 | 14 places; the 7th digit is 8, no tie |
| 16 | `12345678.9012345` | 12345678901234 | **12345678901235** | large magnitude, tie down |
| 17 | `0.01` | 10000 | 10000 | a cent, nothing to round |
| 18 | `19.99` | 19990000 | 19990000 | the writ's amount as written |

Eight diverge: 2, 3, 4, 7, 8, 9, 11, 16. Fixtures 7 and 8 are the ones worth
keeping: they show the divergence is not one-directional. The double is not
"slightly high"; it is *arbitrary*, and a rule that only ever saw fixture 2 would
leave an implementer believing the double rounds up.

**Fixture 13 catches a second wrong parser the amendment's wording invites.** A
parser that reads "rounded half-even at the seventh decimal place" as *look at
the seventh digit* — sees `5`, calls it a tie, rounds `2` to the even `2` — gets
**2** where the rule gives **3**. Half-even is a property of the whole discarded
tail, not of one digit. Nothing in this harness's decimal path is a float, and
that parser is not a float either; it is simply a different reading of the same
sentence, and only a fixture with digits past the seventh separates them.

### What the parser is

`parse_amount_micro(text)` in `check_layout.py`. Optional `-`, ASCII digits, at
most one `.`, digits on both sides of it. Fewer than seven fraction digits are
zero-padded into the micro-unit integer with nothing to round. More than six are
sliced: the first six join the integer, the seventh is compared against `5`, and
the digits beyond it decide whether a `5` is a tie at all; an exact tie rounds to
the even. The sign is applied last, which is correct because half-even is
symmetric about zero. The result is a Python `int` and every intermediate is one.

`parse_amount_micro_via_double(text)` is the lie. It calls
`float(text).as_integer_ratio()` — the double's *exact* value as a rational — and
hands it to the same `_round_half_even_ratio` the decimal path is cross-checked
against. So the two paths share their rounding and differ only in the parse,
which is precisely the claim Amendment 3 item 1 makes.

The refusals are typed (`AmountText`) and are checked to be typed: a bare
`ValueError` out of a coercion counts as a FAIL, because a refusal a caller
cannot tell from a crash is not a refusal. The Unicode-digit fixture is the
sharp one — `int("\u0661")` is `1` in Python, so an implementer who reaches for
`int()` gives one amount two spellings and one promise two ids.

---

## 2 · Amendment 3 item 2 · compaction never removes a fingerprint

`python C:/FACTOR/tests/chain_check.py` → **exit 0**

Every block O7 printed still passes: the six pinned personalizations and six
derived keys, the keyed tape chain, the manifest, the segment filenames, all
three torn cases and the fatal non-final tear, the fingerprint chain with zero
keyed recomputations, the witness disagreement, the 4,096 cadence on a
9,000-row tape, the three original planted lies, the spool, the four-part cursor
and the canonical-JSON table. `RESULT: ALL CHECKS PASS`. What is new:

### (a6) — a lawful compaction, and BOTH chains after it

```
(a6) COMPACTION -- a signed tombstone replaces the span, item 20,
     bounded by Amendment 3 item 2
     tape                   : 17 rows, fingerprints at [3, 7, 11, 15, 16]
     span replaced          : rows 4..6 (3 rows), strictly
                              between the fingerprints at 3 and 7
     tombstone carries      : span_prev d46f901cbf38afc9
                              span_h    d17c0db71adf5e51
                              count     3, operator-signed
     head before compaction : f6acce2bc11780db3d85f599787cf39c
     head after compaction  : f6acce2bc11780db3d85f599787cf39c
     same head              : True   PASS
     errors                 : 0
     AFTER A LAWFUL COMPACTION, BOTH CHAINS VERIFY (item 2):
       keyed tape chain     : 0 errors, head unchanged True
       fingerprint chain    : 0 errors, 5 fingerprints (was 5)
       verify --chain-only  : 0 errors   PASS
       the two fingerprints bounding the span are still on the
       tape, so the keyless walk sees an unbroken fp chain and a
       tombstone bracketed on both sides.
     tombstone with a WRONG last h, signature left stale:
       errors               : 2 -> seg-000001.jsonl row 4: tombstone signature does not cover (span
       VERDICT              : REJECTED by the signature
     tombstone with a WRONG last h, RE-SIGNED by the operator:
       errors               : 1 -> seg-000001.jsonl row 5: LINK broken (prev=d17c0db71adf5e51 expec
       VERDICT              : REJECTED by the link
       head                 : f6acce2bc11780db -- UNCHANGED. One row's link
                              breaks and the walk re-syncs, so the
                              head alone never reveals it. The
                              rejection is the error, not the head.
```

Both O7 rejection cases are kept and still fail for different reasons — a stale
signature by the signature, a re-signed lie by the link.

### (a6b) — the refusal itself

The rule is factored into `compaction_refusal(kinds, first, last)`, a pure
decision over the tape's row kinds, so both clauses are exercised in both
directions without contriving a tape for each. `F` is a fingerprint row, `v` is
any other.

```
(a6b) `factor compact` REFUSES an unlawful span -- Amendment 3
      item 2: a tombstone may replace only rows STRICTLY BETWEEN
      two fingerprints, and never a fingerprint itself
      tape           span     expected               verdict
      vvvFvvvFvvv    4..6     lawful                 PASS
      vvvFvvvFvvv    4..4     lawful                 PASS
      vvvFvvvFvvv    3..6     contains-fingerprint   PASS
      vvvFvvvFvvv    4..7     contains-fingerprint   PASS
      vvvFvvvFvvv    1..5     contains-fingerprint   PASS
      vvvFvvvFvvv    2..8     contains-fingerprint   PASS
      vvvFvvvFvvv    0..2     unbracketed            PASS
      vvvFvvvFvvv    8..10    unbracketed            PASS
      vvvvvvv        2..4     unbracketed            PASS
      FvvvF          1..3     lawful                 PASS
      FF             0..1     contains-fingerprint   PASS
      vvvFvvvFvvv    9..11    span-out-of-range      PASS
      12 of 12 decisions as item 2 states them   PASS
      rows 3..5, a span holding fingerprint 3:
        CompactionRefused(contains-fingerprint)   PASS
        row(s) 3 in the span are fingerprints; compaction never removes a fingerprint
        nothing was written, the destination does not exist : True
      rows 0..2, a span before the first fingerprint:
        CompactionRefused(unbracketed)   PASS
        no fingerprint before the span; a tombstone may replace only rows strictly between two fingerprints
        nothing was written, the destination does not exist : True
```

The refusal is typed — `CompactionRefused` carries a machine-readable `reason`
(`contains-fingerprint`, `unbracketed`, `span-out-of-range`), so the tests assert
on a value and not on a substring of English — and it fires **before anything is
written**, which the run checks by asserting the destination directory was never
created. A refused compaction that leaves a half-compacted tape behind is worse
than one that never refuses.

### (a7) — planted lie 4, a span containing a fingerprint

```
(a7) PLANTED LIE 4 -- a compactor that removes a span CONTAINING
     a fingerprint (the refusal skipped), Amendment 3 item 2
     tape                   : 21 rows, fingerprints at [3, 7, 11, 15, 19, 20]
     compacted              : rows 6..8 (3 rows, one a fingerprint)
     `factor compact` would have refused it : contains-fingerprint
     keyed verify           : 0 errors, head 3464b0074f4312d9
     head unchanged         : True   <- the keyed side sees nothing
     chain-only, before     : 0 errors, 6 fingerprints
     chain-only, after      : 1 errors, 5 fingerprints
       seg-000001.jsonl: fingerprint LINK broken (fp_prev=f211e8c47efeabda expected=ddd613f2500077c5)
     VERDICT                : CAUGHT by verify --chain-only
```

This is O7 (a7) verbatim in its numbers, promoted from a measurement to a lie
with a verdict: the run now **fails** if `--chain-only` stops catching it.

### (a8) — planted lie 5, the refusal skipped on an unbracketed span

```
(a8) PLANTED LIE 5 -- the refusal skipped on a span that holds NO
     fingerprint but is not strictly between two, Amendment 3 item 2
     compacted              : rows 0..2 (3 rows, none a fingerprint)
     `factor compact` would have refused it : unbracketed
     keyed verify           : 0 errors, head unchanged True
     fingerprint links      : 6 fingerprints, all self-hashes and
                              fp_prev links intact
     chain-only, after      : 1 errors
       seg-000001.jsonl: tombstone at row 0 has no fingerprint before it -- the span it replaces is outside every attested bracket (Amendment 3 item 2)
     VERDICT                : CAUGHT -- a fingerprint-chain error on an unbracketed tombstone
```

The second clause of item 2 needed a mechanism of its own, because nothing about
the fingerprints is wrong in this case — every self-hash and every `fp_prev` link
is intact, and the keyed chain reaches the same head. What is wrong is *where the
tombstone sits*. `verify_chain_only` now records the position of every tombstone
alongside every fingerprint and requires a fingerprint on both sides of each one.
That check is keyless: `count`, `k` and the row order are all readable without
the tape key, so `--chain-only` keeps the property O7 proved with a call counter.

The security content of the clause is what makes it worth enforcing: a span
strictly between two fingerprints is bracketed by two attestations the console
already published to the witness, so the witness holds the head before the span
and the head after it and the compaction cannot change either. Rows outside every
bracket were never attested to anyone, and a compaction there is one no external
observer can bound.

### The prose the run now prints

```
Amendment 3 item 2 settled, and this run now encodes
------------------------------------------------------------------------------
  Compaction never removes a fingerprint. A tombstone may replace
  only rows strictly between two fingerprints, `factor compact`
  refuses anything else with a typed error and writes nothing,
  and after a lawful compaction the keyed chain reaches the same
  head AND the fingerprint chain verifies AND --chain-only reports
  zero errors. O7's (a7) measurement is now planted lie 4, and the
  other half of the rule -- a span outside every attested bracket
  -- is planted lie 5. Both are caught by --chain-only alone,
  while the keyed chain and its head stay clean, which is why the
  keyless verifier is the one that has to hold this rule.
```

O7's still-open item **g** ("items 19 and 20 collide") is rewritten as CLOSED,
carrying forward only what item 2 leaves open. Items a to f, h and i are
unchanged and still print.

---

## 3 · The three harnesses this pass did not touch

```
python C:/FACTOR/tests/frame_roundtrip.py               exit 0   ALL CHECKS PASS
python C:/FACTOR/tests/run_falsifiers.py                exit 0   94 TODO
python -W error C:/FACTOR/tests/run_falsifiers.py --gate M0
                                                        exit 0   16 TODO
```

The falsifier scaffold is unchanged at **forty-seven** files: Amendment 3 adds no
§21 row. Its gate table still reads M0 8, M1 9, M2 2, M3 2, M4 10, M5 3, M6 5,
M7 5, M8 2, M9 1, and every module's `ID` and `MILESTONE` still match its row —
`F_EXTRACT.py`'s docstring gained a sentence and nothing else, so the runner's
three loud failures (`MISSING`, mismatched `ID`, mismatched `MILESTONE`) are
untouched. `--gate M0` under `-W error` is clean, so nothing new emits a warning.
`check_layout.py` and `chain_check.py` are also clean under `-W error`, which is
not required but was checked.

---

## 4 · Files changed

Four files, all under `C:\FACTOR\tests\`. No file was created or deleted.
`BLUEPRINT_v0.2.md`, `BLUEPRINT.md`, `probe/` and `receipts/` were not touched.

| file | change |
|---|---|
| `check_layout.py` | Block `[5]`, the amount parse. New: `parse_amount_micro`, `parse_amount_micro_via_double`, `_round_half_even_ratio`, `_decimal_as_ratio`, `floating_point_constructs`, the `AmountText` exception, `AMOUNT_FIXTURES` (18) and `AMOUNT_REFUSED` (8). The O7 block that printed "the PARSE in front of it is not [pinned]" is replaced by this one, which subsumes it. Blocks `[1]`–`[4]`, `SPEC`, `SPEC_V01` and the micro-unit informational block are untouched. 668 lines. |
| `chain_check.py` | `CompactionRefused` and the three reason constants; `compaction_refusal`, the rule as a pure decision; `_one_segment`; `compact_span` gains `enforce=` and refuses before writing; `verify_chain_only` gains the tombstone bracket check and returns `tombstones`. In `main`: `(a6)` re-cut onto a dense-cadence tape with the chain-only assertion added, `(a6b)` new, `(a7)` promoted from measurement to planted lie 4, `(a8)` new as planted lie 5. Findings prose updated; still-open item `g` rewritten. 1872 lines. |
| `F_EXTRACT.py` | One sentence in the docstring naming `check_layout.py`'s `AMOUNT_FIXTURES` as this falsifier's amount fixtures. `ID`, `MILESTONE`, `REQUIRES`, `PLANTED_LIE` and both functions are byte-identical. |
| `README.md` | The header now says Amendments 1, 2 **and 3**; a paragraph naming both checks and where they live; the `check_layout.py` and `chain_check.py` rows updated (3 planted lies → 5); a pointer to this file. |

**`layout_check.cpp` and `msvc_check.cmd` are untouched.** The record layout is
unchanged by Amendment 3, so the compile-time assertions still hold and
`-DPROVE_SPEC_FAILS` still fails to build.

---

## 5 · The new checks were made to fail before they were believed

Nine negative controls, each disabling exactly one mechanism and requiring the
harness to exit 1. A check that still passes with its mechanism removed is
decorative.

| control | expected | measured |
|---|---|---|
| fixtures reduced to only those the double path agrees with | FAIL | `rc=1`, verdict `NOT CAUGHT` |
| one fixture's expected integer stated wrong | FAIL | `rc=1`, names the fixture and both integers |
| the decimal parser swapped for the double path | FAIL | `rc=1` |
| a parser that calls `float()` fed to the AST walk | non-zero | 1 literal, 1 name |
| a parser using true division fed to the AST walk | non-zero | 1 division |
| `compaction_refusal` always answering "lawful" | FAIL | `rc=1` |
| the bracket check stripped from `--chain-only` | FAIL | `rc=1`, (a8) reports `NOT CAUGHT` |
| the fingerprint LINK check stripped | FAIL | `rc=1`, (a7) reports `NOT CAUGHT` |
| `compact_span` ignoring `enforce=True` | FAIL | `rc=1` |

Two of these found real fragility and were fixed rather than worked around: the
refusal loop crashed on a `ValueError` instead of reporting a FAIL, which is now
an explicit "the refusal must be the typed error" assertion; and the two lie
blocks assumed the predicate would refuse their span, which is now asserted
rather than assumed. The predicate was separately checked on ten further spans,
including inverted and out-of-range ones, with no wrong decisions.

---

## 6 · Where Amendment 3 is still ambiguous for an implementer

Thirteen items. These are what a person sitting down to implement item 1 and
item 2 against the amended file would still have to invent.

### Item 1 · the amount parse

1. **Nothing says what an amount text may look like.** "Parsed from its text as a
   decimal by digit arithmetic" presumes a grammar the amendment never gives.
   This harness accepts `-?digits[.digits]` in ASCII and refuses exponent
   notation, grouping separators, surrounding space, a bare `.5`, a trailing
   `1.`, a leading `+`, and Unicode decimal digits. Every one of those is a form
   some upstream really sends, and each choice is either a different id or an
   obligation that is never minted at all — which is the larger divergence.

2. **`int()` accepts Unicode decimal digits, and that is a live trap.** `"\u0661"`
   is `1` to Python and to several other runtimes' equivalents. An implementer
   who reaches for the obvious conversion gives one amount two spellings. The
   amendment should say ASCII, in those words.

3. **O7's second question is still unanswered: what happens to a source that
   supplies a float?** Item 1 forbids a float *inside* FACTOR; it says nothing
   about a claim that arrives carrying `19.99` as a JSON number, or an upstream
   API that hands the extractor a double. Refuse the claim, refuse the amount, or
   reconstruct the shortest decimal that round-trips — the third is itself a rule
   needing to be pinned, since "shortest round-tripping decimal" is a choice and
   not a fact. The extractor's inputs are other people's formats, so this is the
   largest hole left in item 1.

4. **"Rounded half-even at the seventh decimal place" invites a wrong parser.** A
   parser that inspects only the seventh digit rounds `0.00000250000001` to 2;
   the rule gives 3, because a `5` followed by anything non-zero is not a tie.
   The amendment's other phrase, "rounded half-even on the decimal
   representation", is the correct reading. Both phrases are in the same
   sentence. Fixture 13 exists to separate them.

5. **Whether the parse *is* the "once at ingest" rounding is not said.**
   Amendment 1 item 2 pins rounding applied once at ingest; item 1 pins the
   parse. If the parse is the ingest rounding they are one operation, which is
   the only reading that keeps "once" true — but a map or a later arithmetic step
   that re-rounds would silently make it twice, and nothing forbids that.

6. **No range rule.** `amount_fix` is `int64`: ±9,223,372,036,854.775807 units. A
   text outside that parses to an integer that does not fit the field. Whether
   the parser refuses it, the ledger refuses the record, or the value saturates
   as margins do (Amendment 1 item 6) is unstated. This harness deliberately does
   not answer it — its parser returns an unbounded Python int — because inventing
   an answer here would hide the gap.

7. **The enforcement point for "a binary floating-point value never touches an
   amount" is not given.** This harness enforces it by walking the parser's AST,
   which is available to Python and not to the C++ kernel. And the rule names the
   kernel, the maps and the extractor — not the surfaces, the console or the
   account. An account that formats an amount through a double is presumably
   fine, since printing is not identity-bearing, but the amendment does not draw
   that line.

8. **Item 1 says the tie cases "become the falsifier's fixtures" without naming
   the falsifier.** F-EXTRACT is the only reading that fits — extraction is where
   an amount text becomes the integer §5 hashes — and this pass wrote that into
   `F_EXTRACT.py`'s docstring. A different reading (a new §21 row, or F-DETERMINISM)
   would change the falsifier count, which stays at forty-seven here.

### Item 2 · compaction

9. **Nothing says a VERIFIER must check the bracket.** Item 2 constrains
   `factor compact`. It does not say what a verifier does when handed a tape
   whose tombstone is unbracketed. If only the writer enforces the rule, the rule
   protects nothing against the one adversary compaction actually has — an
   operator with a signing key. This harness makes `--chain-only` refuse an
   unbracketed tombstone, and that is a decision the amendment does not record.

10. **Item 2's guarantee silently depends on an unpinned choice from item 19.**
    "Both chains verify after a lawful compaction" is true here *because* the
    fingerprint body is `{head, row, seg}` and a lawful compaction touches none of
    the three. O7's still-open item (a) recorded that item 19 never pinned the
    fingerprint body; a body that covered, say, a cumulative row count would break
    under a lawful compaction and item 2's promise would be false. Item 2 needs
    item 19's body pinned before it means anything.

11. **A fingerprint's `row` no longer matches its position after a lawful
    compaction.** A fingerprint attests `{head, row, seg}`; compaction removes
    `count` rows and inserts one, so every later fingerprint's `row` exceeds its
    index in the file. Does `row` mean the original index — reconstructible,
    since the tombstone carries `count` — or the position on the compacted tape?
    This harness never rewrites a fingerprint, so `row` keeps its original value
    and a verifier that checked position against `row` would reject a *lawful*
    compaction. The check was deliberately not added for that reason.

12. **"The tombstone itself is fingerprinted at the next interval" is an outcome,
    not an obligation.** By the ordinary 4,096-row and segment-close cadence, or
    by a fingerprint written at the compaction? They differ: compaction *removes*
    rows, so the ordinary cadence puts the next fingerprint further away in wall
    time than it would have been, and a tape can sit published with an
    un-fingerprinted tombstone for a whole interval. If compaction must be
    followed by a fingerprint before the tape is republished, that is a stronger
    rule and it is not the one written.

13. **Nothing says whether a tombstone may itself be compacted away.** A span
    containing a tombstone is neither refused nor blessed; this harness's
    predicate allows it, since a tombstone is not a fingerprint. Compacting one
    away discards the `count` and the operator's signature over the earlier
    removal, so a second compaction erases the audit of the first. Either
    tombstones join fingerprints as rows compaction may not remove, or the
    amendment should say that a nested tombstone's count is folded into the
    outer one.

Two smaller notes carried forward rather than repeated: what the operator's
signature covers is still unstated (O7 §6 item 14 — it covers `(span_prev,
span_h, count)` here, and notably not the bracketing fingerprints, so the
operator does not attest that the span was lawful), and the witness's copy still
has no defined form (O7 §6 item 16).

---

## 7 · What this pass still does not do

* **No kernel.** Both checks run against models in Python — a ctypes record and
  generated JSONL tapes. They pin the byte-level and order-level questions; they
  do not prove any FACTOR binary obeys them.
* **The parser is not the extractor.** `parse_amount_micro` is the rule made
  executable so the fixtures have something to be fixtures *of*. F-EXTRACT is
  still a stub, and wiring these fixtures into it is M2 work.
* **`factor compact` is not a program.** `compact_span` is a model of one, over a
  single-segment fixture tape. A real compaction crossing a segment boundary, or
  one interrupted mid-write, is not exercised.
* **The two rules are not cross-checked against each other.** An amount inside a
  compacted span, and a tombstone whose removed rows carried amounts, are both
  fine by construction here and neither is tested.
* **Forty-seven falsifiers are still stubs.** `94 TODO` is unchanged; Amendment 3
  adds no row and implements none.

---

*O8 · 2026-09-08 · produced by running the files named above, on this machine.*
