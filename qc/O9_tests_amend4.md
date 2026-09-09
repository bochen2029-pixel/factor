# O9 · AMENDMENT 4 FOLDED INTO THE HARNESSES — checked by running code

Source of record: `BLUEPRINT_v0.2.md`, **Amendment 4 · 2026-09-08 · Amendment 3
made implementable**, at the very end of that file. Previous pass:
`qc/O8_tests_amend3.md`, whose §6 listed thirteen things an implementer would
still have to invent. Amendment 4 settles all thirteen; this pass makes each of
them a check.

Everything below was produced by running the files, on this machine, today.
Nothing outside `C:\FACTOR\tests\` was modified.

> **`BLUEPRINT_v0.2.md` grew during this pass, and not from here.** It was
> 122,129 bytes when Amendment 4 was read at the start of it and 127,629 bytes
> at the end, with a new **Amendment 5 · What TAPESTRY's QC found that FACTOR
> also had** appended after Amendment 4. Amendment 4's own text, lines 874 to
> 897, is byte-identical to the text this pass folded in, so nothing below is
> stale. **Amendment 5 is not addressed here** and is the next harness pass; its
> item 9 in particular ("fold-emitted rows are outputs, re-derivable ... `grade`,
> `license`, `front`, `expect` and `fingerprint` rows ... a replay recomputes
> them and `factor verify` compares") lands directly on `chain_check.py`'s
> fingerprint row and should be read against §2 below.

---

## Headline

**All thirteen items are now checks, and every harness is green.**

```
python C:/FACTOR/tests/check_layout.py                  exit 0
python C:/FACTOR/tests/chain_check.py                   exit 0
python C:/FACTOR/tests/frame_roundtrip.py               exit 0
python C:/FACTOR/tests/run_falsifiers.py                exit 0   94 TODO
python -W error C:/FACTOR/tests/run_falsifiers.py --gate M0
                                                        exit 0   16 TODO
```

`check_layout.py`, `chain_check.py` and `frame_roundtrip.py` are also clean
under `-W error`, which is not required but was checked.

**The amount.** `check_layout.py` now carries item 1's grammar in as many words
and refuses ten forms including the two Amendment 4 names by hand — a leading
plus and a lone minus; item 2's rounding **on the whole discarded tail**, with
the withdrawn phrase "at the seventh decimal place" gone from the code, the
comments and the printed prose, and fixture 13 kept as the case that separates
the two readings; item 4's **range refusal**, four fixtures one micro-unit
inside and one micro-unit outside the `int64` bound on each side of zero, with a
**second planted lie** — a parser that clamps — caught differing on both
out-of-range texts; and item 6's **lossy amount**, a producer that formats a
Python float at a declared precision into item 1's grammar and marks the frame
bit 3 and the record bit 14, over two fixtures. The parser's AST is still walked
and still holds zero floating-point constructs; the same walk over the
**producer's formatter** finds **one**, and the run fails if it finds none —
because a walk that cannot see the float it is looking for is not measuring
anything.

**Compaction.** `chain_check.py`'s bracket check, fingerprint-chain check,
bracketing-head check, tombstone signature and position reconstruction are now
**one function, `compaction_rules`, called by `verify_tape` and by
`verify_chain_only`** — item 8, and the reason the two verifiers cannot drift
apart is that there is only one copy of the rule. Planted lies 4 and 5 are
**caught by both**, where O8 could only assert the keyless half. The fingerprint
body is pinned as `{head, seg, row_orig}` and a lawful compaction is *measured*
to leave every attested body and every `fp_h` byte-identical while four of five
positions move. The scaffold gains **two planted lies**, 6 and 7, and both are
caught by both verifiers.

**One consequence worth stating up front: item 10 is not decidable from a
published tape.** A fingerprint written by the compactor and one written by the
ordinary cadence are the same row, and both attest the same head — a lawful
compaction does not move the head, which is item 20's whole point. So the only
observable a verifier has is *some fingerprint follows this tombstone*, which is
also the "after" half of item 8's bracket. This pass enforces item 10
constructively on the writer (`close_compaction`, checked) and as that
observable on the verifier (planted lie 6, caught twice). §6 item **g** below
records what is left.

---

## 1 · The amount · items 1, 2, 4, 6 and 7

`python C:/FACTOR/tests/check_layout.py` → **exit 0**

Blocks `[1]` to `[4]` — sizeof 128, alignof 8, 29 of 29 pinned offsets, zero
hole bytes, zero trailing ABI pad, and the v0.1 planted lie caught at 120
bytes — print byte-for-byte what O8 printed. The eighteen-fixture table and its
`8 of 18` double-path divergence are unchanged, fixture 13 included. What is
new:

### Item 1 · the grammar, in as many words

```
      AMENDMENT 4 ITEM 1 -- the grammar is exactly
        amount := '-'? DIGIT+ ( '.' DIGIT+ )?   DIGIT := 0..9, ASCII
      forms REFUSED, never coerced:
        '1e-6'         refused: 'e' is not an ASCII digit
        '1.2.3'        refused: more than one decimal point
        ''             refused: empty
        '1,234.00'     refused: ',' is not an ASCII digit
        ' 1.00'        refused: ' ' is not an ASCII digit
        '1.'           refused: a decimal point with no digits after it
        '.5'           refused: no digits before the decimal point
        '+1.00'        refused: '+' is not an ASCII digit
        '-'            refused: a sign with no digits
        '\u0661.\u0665' refused: '\u0661' is not an ASCII digit
      10 of 10 refused with the typed error, reason 'grammar'      PASS
```

The two new fixtures are Amendment 4's own words. `+1.00` matters because
`int("+1")` is `1` in Python and in most runtimes' equivalents, so a coercing
parser gives `+1.00` and `1.00` one integer and the claim two spellings. `-` is
the degenerate case of the same clause and is the one a hand-written scanner
reaches after stripping the sign.

The refusals are now checked to carry the *right* reason as well as the right
type: `AmountText.reason` is `grammar`, and a malformed text refused with the
range reason is a FAIL, because the account cannot otherwise tell "the upstream
sent nonsense" from "the upstream sent a number too large to be an amount".

### Item 2 · the tie is the whole discarded tail

The parser already did this; what changed is that the code now says so. The
withdrawn phrase is gone from `parse_amount_micro`'s docstring, from the block
header, and from the informational `amount_fix` block. The comment on the
rounding branch is explicit that `tie` is the leading digit of the discarded
tail and `beyond` is whether anything follows it, and that only a five followed
by nothing but zeros is a tie. Fixture 13 (`0.00000250000001` → **3**, not 2)
stays, and §5's control **CL5** shows it is the fixture that holds the rule: a
parser that reads only the seventh digit fails on it and on nothing else.

### Item 4 · the range, refused and never saturated

```
      AMENDMENT 4 ITEM 4 -- a micro-unit value outside int64 is
      REFUSED with the typed reason, never saturated
        int64 bound : [-9223372036854775808, 9223372036854775807] micro-units
                      = -9223372036854.775808 to 9223372036854.775807 units
        source text              the rule               the clamping lie       what it pins
        9223372036854.775807     9223372036854775807    9223372036854775807    int64 max, just INSIDE
        9223372036854.775808     refused(out-of-range)  9223372036854775807    one micro-unit OVER the max
        -9223372036854.775808    -9223372036854775808   -9223372036854775808   int64 min, just INSIDE
        -9223372036854.775809    refused(out-of-range)  -9223372036854775808   one micro-unit UNDER the min
        4 of 4 as item 4 states them   PASS
        PLANTED LIE -- the same parser CLAMPING at the bound:
          out-of-range texts it saturated instead of refusing : 2 of 2
          VERDICT: CAUGHT -- the rule refuses where the lie returns the bound
```

The refusal is `AmountRange`, a subclass of `AmountText` carrying
`reason = "out-of-range"`, so it is "the typed error" under either reading and
the two refusal kinds are still tellable apart by a value rather than by a
substring of English.

**The bound is not symmetric, and the fixtures are chosen so a parser that
checks `abs()` against `2**63 - 1` fails.** `-9223372036854.775808` is lawful
and its magnitude is one over the maximum; a parser that tested the magnitude
would refuse a lawful amount, and only the negative *inside* fixture catches
that.

The clamping lie is worth its lines because it is the obvious thing to write and
it fails in exactly one direction: the clamped value is *the bound*, so it
compares at-or-under any cap at the bound and the breach is never reported.
That is the asymmetry item 4 states as "saturation is for margins and counters
only" — a saturated margin is still a margin; a saturated amount is a false
negative.

### Item 6 · the lossy amount, and the one lawful float

```
      AMENDMENT 4 ITEM 6 -- a source that supplies a number, not text
        the same AST walk over the producer's formatter: 1 float
          construct(s) -- NOT zero, and that is the point
        frame flag bit 3  `lossy_amount` = 8   PASS
        record flag bit 14 `AMOUNT_LOSSY` = 16384   PASS
        the double the source has prec formatted micro-units  exact text   flags
        0.30000000000000004      2    0.30      300000       0.30 -> 300000 f=8 flags=16384
          the double's noise is cut AT THE DECLARED PRECISION, not carried
        2.675                    2    2.67      2670000      2.675 -> 2675000 f=8 flags=16384
          the loss is REAL: 2.675 as a double is BELOW its tie, so the producer
          emits 2.67 and the half-cent is gone
        2 of 2 lossy fixtures format, parse and flag as item 6 states them  PASS
        compared against caps AS WRITTEN, with no second rounding:
          cap 2670000, lossy amount 2670000 -> breach False
          cap 2670000, the source's true value 2675000 -> breach True
        the account counts lossy amounts PER CLASS: class-0=1, class-1=1
        refuses a str, which should be sent as text PASS
        refuses a precision past the micro-unit    PASS
        refuses no declared precision              PASS
```

`format_amount_at_precision(value, precision)` is the producer's boundary. It
takes a Python `float` and the precision the **map** declared, formats with
`"%.*f"`, and returns the text, the micro-units that text parses to, and both
flags. The float stops at that line: what crosses is text, and the text
re-enters through the same `parse_amount_micro` as any other amount, which the
run asserts rather than assumes.

The two fixtures pin opposite halves. `0.1 + 0.2` is `0.30000000000000004` and
the producer emits `0.30`, so the double's noise never reaches the amount —
because the precision came from the map and not from the double. `2.675` as a
double is *below* its tie, so the producer emits `2.67` and the half-cent is
gone; the run prints the 2,675,000 micro-units the exact text would have given
beside the 2,670,000 the lossy path gives, shows that a cap of 2,670,000 is
breached by one and not by the other, and states that neither the hand nor the
account may silently prefer the second. The amount is compared **as written**
and the record is **flagged**, which is item 6's "a source that cannot state its
own amounts exactly is a finding about the source" made operational.

**The AST walk is now checked in both directions.** O8 walked
`parse_amount_micro` and `_round_half_even_ratio` and found zero floating-point
constructs. A walk that finds zero everywhere proves nothing, so this pass walks
the producer's formatter with the same function and requires a **non-zero**
count; §5's control **CL8** blinds it and the harness fails.

### Item 7 · the amount leaves the derived id

Item 7 changes §5's identity rule, so three places in `check_layout.py` that
asserted the id covers the amount are corrected: the module docstring, the
comment on the informational `amount_fix` block, and the two printed lines that
said two roundings "mint two obligations for one promise" (now: write two
records for one promise — two digests, and two answers to the same cap). The
`half-up` column's `<- two ids` marker becomes `<- two digests`. The closing
prose now says the fixtures belong to F-EXTRACT **and F-REPLAY**.

`F_EXTRACT.py`'s one docstring sentence is rewritten to match. `ID`,
`MILESTONE`, `REQUIRES`, `PLANTED_LIE`, `requires()` and `planted_lie()` are
byte-identical, so the runner's three loud failures (`MISSING`, mismatched `ID`,
mismatched `MILESTONE`) are untouched and the count stays at forty-seven.

---

## 2 · Compaction · items 8 to 13

`python C:/FACTOR/tests/chain_check.py` → **exit 0**

Every block O8 printed still passes: the six pinned personalizations and six
derived keys, the keyed tape chain, the manifest, the segment filenames, all
three torn cases and the fatal non-final tear, the fingerprint chain with zero
keyed recomputations, the 4,096 cadence on a 9,000-row tape, planted lies 1, 2
and 3, the spool, the four-part cursor and the canonical-JSON table.
`RESULT: ALL CHECKS PASS`.

### Item 8 · one rule, two verifiers

`compaction_rules(fps, tombs)` is the whole of items 8 to 12 in one function.
`verify_tape` collects the fingerprint and tombstone rows with their positions as
it walks and calls it; `verify_chain_only` does the same. Nothing in it needs
the tape key — fingerprint rows, tombstone rows, `count` and row order are all
readable without one, and the operator's and console's signatures use keys a
keyless verifier already holds — which is why one function can serve both, and
it is **measured**: `(a5)`'s `keyed h recomputations : 0` still holds with the
shared checks inside `verify_chain_only`.

The consequence, on planted lie 4:

```
(a7) PLANTED LIE 4 -- a compactor that removes a span CONTAINING
     a fingerprint (the refusal skipped), Amendment 3 item 2,
     now caught by BOTH verifiers (Amendment 4 item 8)
     tape                   : 21 rows, fingerprints at [3, 7, 11, 15, 19, 20]
     compacted              : rows 6..8 (3 rows, one a fingerprint)
     `factor compact` would have refused it : contains-fingerprint
     head unchanged         : True   <- the keyed CHAIN sees nothing
     chain-only, before     : 0 errors, 6 fingerprints
     chain-only, after      : 1 errors, 5 fingerprints
       seg-000001.jsonl: fingerprint LINK broken [removed-fingerprint] (fp_prev=29df541fc6a0200c expected=f8bf55b7439fc8df)
     `factor verify`, after : 1 errors, head 3ea8433c3fa9514e
       seg-000001.jsonl: fingerprint LINK broken [removed-fingerprint] (fp_prev=29df541fc6a0200c expected=f8bf55b7439fc8df)
     caught by --chain-only : True
     caught by verify       : True   (Amendment 4 item 8)
     VERDICT                : CAUGHT by both verifiers
```

and on planted lie 5:

```
(a8) PLANTED LIE 5 -- the refusal skipped on a span that holds NO
     fingerprint but is not strictly between two, Amendment 3
     item 2, now caught by BOTH verifiers (Amendment 4 item 8)
     compacted              : rows 0..2 (3 rows, none a fingerprint)
     `factor compact` would have refused it : unbracketed
     head unchanged         : True
     chain-only, after      : 1 errors
       seg-000001.jsonl: tombstone at row 0 has no fingerprint BEFORE it [unbracketed] -- the span it replaces is outside every attested bracket
     `factor verify`, after : 1 errors
       seg-000001.jsonl: tombstone at row 0 has no fingerprint BEFORE it [unbracketed] -- the span it replaces is outside every attested bracket
     caught by --chain-only : True
     caught by verify       : True   (Amendment 4 item 8)
     VERDICT                : CAUGHT by both, on the missing bracket
```

The head is unchanged in both, which is the point item 8 makes: the tombstone
repairs the keyed chain, so the keyed *chain* never sees a compaction lie. Only
the rule does — and until Amendment 4 the keyed verifier did not hold it, while
the adversary compaction actually has is the holder of the operator key, who is
the person running `factor verify`.

Every verifier-side error now carries a bracketed machine-readable reason, so
the tests assert on `[unbracketed]`, `[unfingerprinted-tombstone]`,
`[removed-fingerprint]`, `[bracket-head-mismatch]`, `[tombstone-signature]` and
`[row-orig-mismatch]` rather than on English.

### Item 9 · the pinned body, and what a lawful compaction may not move

```
(a6c) AMENDMENT 4 ITEM 9 -- the fingerprint body is PINNED as
      {head, seg, row_orig}, and `row_orig` is the row's index on
      the UNCOMPACTED tape. Compaction never renumbers.
      body keys, in canonical order : ('head', 'row_orig', 'seg')
      one body, verbatim            : {"head":"abd60f692c353e2c54d158ad6f1cff27eaf289a28d275c78fd486bcd767abde2","row_orig":"3","seg":"1"}
      A LAWFUL COMPACTION CHANGES NO ATTESTED FIELD:
        fp   row_orig   position   moved by  body unchanged
        0    3          3          0         True
        1    7          5          2         True
        2    11         9          2         True
        3    15         13         2         True
        4    16         14         2         True
      5 of 5 bodies byte-identical, 5 of 5 fp_h identical  PASS
      the POSITION moved for 4 of them and no body did
      a compactor that RENUMBERS one fingerprint to its new
      position instead of leaving row_orig alone:
        `factor verify`       : 3 errors
        `verify --chain-only` : 2 errors
        seg-000001.jsonl: fingerprint at row 5 attests row_orig 5 and 2 row(s)
        VERDICT: CAUGHT by both, on the reconstruction
```

The field is renamed `row` → `row_orig` on the fingerprint row, in
`FP_BODY_KEYS`, in `ROW_KEYS`, and in §12's `DECLARED_WIDTH` table. The
reconstruction is `row_orig − Σ(count − 1)` over the tombstones before it — each
tombstone replaces `count` rows with one — and `compaction_rules` refuses the
tape when the arithmetic does not close.

This closes O8's still-open item **10** the right way round: item 2's promise
that both chains verify after a lawful compaction is now *true because the body
holds nothing a compaction moves*, and the table above measures it rather than
asserting it. It also closes O8's item **11** — `row_orig` means the original
index, a verifier that compared it against the file position would reject a
lawful compaction, and the correct check is the subtraction, which is now
present and has teeth (control **CC9**).

### Item 10 · the closing fingerprint, and planted lie 6

```
(a6d) AMENDMENT 4 ITEM 10 -- a compaction is followed by a
      fingerprint AT ONCE, before the tape is published,
      replicated or read by anyone but the compactor
      witness taken BEFORE the compaction, checked after it:
        0 errors   PASS -- item 9 is why this holds
      the compactor then appends the closing fingerprint:
        row_orig               : 17   (the tape carries 16 rows
                                 and 2 were compacted away, so
                                 the UNCOMPACTED index is 17)
        position               : 15
        attests head           : 4f9d8bd259f912e605d536b4dcb0ccb9
        head after the close   : 1e36a451c2fd622bc7fbf541dd55554f
      published tape verifies both ways:
        `factor verify`        : 0 errors, 6 fingerprint(s)
        `verify --chain-only`  : 0 errors, 6 fingerprint(s)
        witness, appended to   : 6 line(s)   PASS
```

`compact_span` now returns a tape that is **not yet publishable** and
`close_compaction` is the step item 10 requires. Splitting them keeps item 20's
property exactly where it belongs: the *compaction step* reaches the same head
(`(a6)`'s `same head : True`, unchanged from O8), and the closing fingerprint is
an ordinary append after it, which moves the head as any appended row does. The
new fingerprint's `row_orig` continues the uncompacted numbering, recovered from
the file as rows-on-it plus rows-the-tombstones-replaced, and the reconstruction
closes at position 15.

The verifier's side is planted lie 6:

```
(a9) PLANTED LIE 6 -- a tape PUBLISHED carrying an
     UNFINGERPRINTED tombstone, Amendment 4 item 10
     tape                   : 25 rows, last fingerprint at 20,
                              then 4 ordinary rows after it --
                              the window the ordinary 4,096-row
                              cadence leaves open
     compacted              : rows 21..23 (3 rows, none a
                              fingerprint or a tombstone)
     `factor compact` would have refused it : unbracketed
     keyed head unchanged   : True
     `factor verify`        : 1 errors
       seg-000001.jsonl: tombstone at row 21 has no fingerprint AFTER it [unfingerprinted-tombstone] -- the tape was published carrying an unfingerprinted tombstone
     `verify --chain-only`  : 1 errors
       seg-000001.jsonl: tombstone at row 21 has no fingerprint AFTER it [unfingerprinted-tombstone] -- the tape was published carrying an unfingerprinted tombstone
     caught by both         : True / True
     VERDICT                : CAUGHT by both, [unfingerprinted-tombstone]
```

The tape is the dense fixture with four ordinary rows appended after its last
fingerprint — the window the 4,096-row cadence leaves open, and the one item 10
closes. The fingerprints, the keyed chain and the head are all clean; every one
of them was written *before* the compaction and none attests it.

### Item 11 · tombstones are protected rows

The predicate gains `contains-tombstone` and the table grows from twelve
decisions to nineteen:

```
      vvvFTFvvvFv    4..4     contains-tombstone     PASS
      vvvFvTvFvvv    4..6     contains-tombstone     PASS
      vvvFvTvFvvv    5..5     contains-tombstone     PASS
      vvvFvTvFvvv    4..4     lawful                 PASS
      vvvFvTvFvvv    6..6     lawful                 PASS
      vFvTvFvvvFv    1..5     contains-fingerprint   PASS
      TvvFvvvFvvv    0..2     contains-tombstone     PASS
      19 of 19 decisions as item 2 states them   PASS
```

The last two pin the ordering: a span holding both a fingerprint and a tombstone
reports `contains-fingerprint` (the older rule first) and a span holding a
tombstone *and* outside every bracket reports `contains-tombstone`. Either
reason refuses the same span, and §6 item **k** records that the amendment does
not choose.

End to end, on the compacted-and-closed tape from `(a6d)`, which now really
carries a tombstone:

```
(a6e) AMENDMENT 4 ITEM 11 -- tombstones are PROTECTED rows
      row 4 of the closed tape, the tombstone itself -- a
      span STRICTLY BETWEEN the fingerprints at 3 and 5, so
      lawful under item 2 and refused only by item 11:
        CompactionRefused(contains-tombstone)   PASS
        row(s) 4 in the span are tombstones; a tombstone is a protected row, and compacting one away discards the count and the operator's signature over the earlier removal
        nothing was written, the destination does not exist : True
```

That span is the sharpest form of the rule: it is strictly between two
fingerprints and holds no fingerprint, so item 2 permits it and only item 11
refuses it.

### Item 12 · the signature covers the bracket

The tombstone row gains `fp_before` and `fp_after`, the heads attested by the
fingerprints immediately before and after the span, and
`TOMB_SIGNED_KEYS` becomes `(count, fp_after, fp_before, span_h, span_prev)`:

```
     tombstone carries      : span_prev 5b3310550235358d
                              span_h    0cfee6a865cbeab7
                              count     3
                              fp_before abd60f692c353e2c
                              fp_after  0cfee6a865cbeab7
                              operator-signed over ALL FIVE
```

and the planted lie:

```
(a10) PLANTED LIE 7 -- a tombstone whose fp_after names a head
      the bracketing fingerprint does not attest, RE-SIGNED by
      the operator, Amendment 4 item 12
      the operator's signature over all five fields : VALID
        (no signature error, as expected -- so the signature alone cannot catch it)
      keyed head unchanged   : True
      `factor verify`        : 1 errors
        seg-000001.jsonl: tombstone at row 4 names fp_after eeeeeeeeeeeeeeee but the fingerprint bracketing it attests 0cfee6a865cbeab7 [bracket-head-mismatch]
      `verify --chain-only`  : 1 errors
        seg-000001.jsonl: tombstone at row 4 names fp_after eeeeeeeeeeeeeeee but the fingerprint bracketing it attests 0cfee6a865cbeab7 [bracket-head-mismatch]
      VERDICT                : CAUGHT by both, [bracket-head-mismatch]
      the same move with the signature LEFT ALONE:
        seg-000001.jsonl row 4: tombstone signature does not cover (span_pre
        VERDICT: REFUSED by the signature -- so the signature really does cover the two heads
```

Both halves are needed and they catch different things. The **comparison**
against the tape is what stops an operator signing a bracket the span never sat
in; the **signature** is what stops anyone else moving a head the operator did
sign. A harness with only the comparison would pass with the heads outside the
signature — control **CC6** is exactly that, and it fails on the second case.

O8's two rejection cases are kept and still fail for different reasons: a stale
signature by the signature, a re-signed lie by the link.

### Item 13 · the witness's copy has a form

```
     THE WITNESS'S COPY, Amendment 4 item 13:
       one line per fingerprint : 8 line(s), 8 fingerprint(s)
       each line is             : the row's canonical JSON, a
                                  TAB, the console's signature
       first line               : {"fp_h":"f8bf55b7439fc8dfe41f9215cc3e9f72f3173c539352279
                                  ...  sig c039dec783a8741b
       every signature verifies : True   PASS
       a witness line the console never signed :
         the witness's copy is not usable: witness line 7: the console's si
         VERDICT: CAUGHT by the console's signature
       a signed witness line that disagrees with the tape :
         the witness's copy disagrees with the tape's fingerprints (8 publi
         VERDICT: CAUGHT by the comparison
```

The witness was a list of bare `fp_h` digests; it is now the fingerprint row's
canonical JSON with `K_CONSOLE`'s signature over exactly those bytes, one line
each, written and appended only — `close_compaction` **appends** the closing
fingerprint's line to the same file, which is the only capability item 13 asks a
witness for.

The two disagreement cases are different mechanisms and the run says so: a line
the console never signed is a witness holding something nobody published; a
signed line that disagrees is a witness and a tape that were both published and
do not agree. Only the second was checkable before, because a bare digest list
carries no attestation of its own.

The witness for the compaction fixture is taken **before** the compaction and
checked after it — `0 errors` — which is item 9 doing its work: a lawful
compaction leaves every published fingerprint byte-identical, so the witness's
copy needs no rewriting and the store never has to.

---

## 3 · The three harnesses this pass did not change

```
python C:/FACTOR/tests/frame_roundtrip.py               exit 0   ALL CHECKS PASS
python C:/FACTOR/tests/run_falsifiers.py                exit 0   94 TODO
python -W error C:/FACTOR/tests/run_falsifiers.py --gate M0
                                                        exit 0   16 TODO
```

The falsifier scaffold is unchanged at **forty-seven** files: Amendment 4 adds no
§21 row. Its gate table still reads M0 8, M1 9, M2 2, M3 2, M4 10, M5 3, M6 5,
M7 5, M8 2, M9 1, and every module's `ID` and `MILESTONE` still matches its row.
`F_EXTRACT.py`'s docstring is the only falsifier change, and it touches no
constant.

`layout_check.cpp` and `msvc_check.cmd` are untouched. The record layout is
unchanged by Amendment 4 — item 6's two flags are bits inside the existing
`uint16_t flags` and the existing frame `f`, and item 7 changes what goes into a
derived id and not what the record holds — so the compile-time assertions still
hold and `-DPROVE_SPEC_FAILS` still fails to build.

---

## 4 · Files changed

Four files, all under `C:\FACTOR\tests\`. No file was created or deleted.
`BLUEPRINT_v0.2.md`, `BLUEPRINT.md`, `probe/` and `receipts/` were not touched.

| file | change |
|---|---|
| `check_layout.py` | New: `AmountRange` (a subclass of `AmountText` carrying `reason`), `parse_amount_micro_saturating` (item 4's planted lie), `format_amount_at_precision` (item 6's producer boundary), `INT64_MIN`/`INT64_MAX`, `FRAME_FLAG_LOSSY_AMOUNT`, `RECORD_FLAG_AMOUNT_LOSSY`, `AMOUNT_RANGE` (4 fixtures) and `LOSSY_FIXTURES` (2). `AMOUNT_REFUSED` grows from 8 to 10 with `+1.00` and `-`. `parse_amount_micro` gains the range refusal, the grammar in its docstring and the whole-tail comment; `TIE_PLACE` is deleted with the phrase it named. Block `[5]` gains three sub-blocks. The docstring, the `amount_fix` informational block and four printed lines are corrected for item 7. `AMOUNT_FIXTURES` and blocks `[1]`–`[4]` are unchanged. 1,060 lines. |
| `chain_check.py` | New: `compaction_rules` (items 8–12 in one function, called by both verifiers), six `REASON_*` constants, `K_CONSOLE`/`console_sign`, `witness_line`/`read_witness`, `_bracketing_heads`, `close_compaction`, `append_rows`, `retamper_bracket`, `REFUSE_CONTAINS_TOMB`. Changed: `FP_BODY_KEYS` to `{head, row_orig, seg}`, `TOMB_SIGNED_KEYS` to five fields, `ROW_KEYS` for both row kinds, `DECLARED_WIDTH` `row`→`row_orig`, `build_tape`'s fingerprint and witness, `compact_span` (bracketing heads, no longer publishes), `verify_tape` (position counting, row collection, shared rules), `verify_chain_only` (shared rules, new witness format). In `main`: `(a5c)` re-cut as two witness cases, `(a6)` gains the bracketing heads and the both-verifier line, `(a6b)` grows to 19 decisions, `(a6c)`/`(a6d)`/`(a6e)` new, `(a7)`/`(a8)` assert both verifiers, `(a9)`/`(a10)` new as planted lies 6 and 7. Findings prose and still-open items rewritten. 2,705 lines. |
| `F_EXTRACT.py` | One docstring paragraph: the amount fixtures pin the record's digest, the caps and replay rather than the derived id (item 7). `ID`, `MILESTONE`, `REQUIRES`, `PLANTED_LIE` and both functions are byte-identical. 47 lines. |
| `README.md` | The header now says Amendments 1, 2, 3 **and 4**; a new Amendment 4 section covering all thirteen items; the `check_layout.py` and `chain_check.py` rows updated (2 planted lies on the layout side, 5 → **7** on the chain side); the Amendment 3 paragraph corrected where item 2 withdrew its wording; a pointer to this file. 292 lines. |

---

## 5 · The new checks were made to fail before they were believed

Eighteen negative controls, each disabling exactly one mechanism in a **copy** of
the harness and requiring it to exit 1. A check that still passes with its
mechanism removed is decorative. All eighteen fail, each on the check it was
aimed at.

| # | control | measured |
|---|---|---|
| CL1 | item 4's range refusal removed | `rc=1`, both out-of-range fixtures marked `MUST REFUSE` |
| CL2 | the parser saturates at the bound instead of refusing | `rc=1`, both clamp to the bound and are marked `MUST REFUSE` |
| CL3 | a leading `+` admitted into the grammar | `rc=1`, `'+1.00' ACCEPTED as 1000000`, 9 of 10 refused |
| CL4 | a grammar refusal wearing the range reason | `rc=1`, `'' refused as OUT-OF-RANGE`, 9 of 10 |
| CL5 | the tie decided by the seventh digit alone (item 2's wrong reading) | `rc=1`, `18 fixtures, 17 parsed to the expected integer` — **fixture 13 alone** |
| CL6 | the record's `AMOUNT_LOSSY` flag dropped | `rc=1`, both lossy fixtures print `flags=0 <- FAIL` |
| CL7 | the producer ignores the map's declared precision | `rc=1`, emits `0.300000` and `2.675000` |
| CL8 | the AST walk blinded (no float construct in the formatter) | `rc=1`, "the AST walk sees no float ... so it is blind and its zero on the parser proves nothing" |
| CC1 | item 8's "no fingerprint BEFORE" check stripped | `rc=1`, `(a8)` reports `NOT CAUGHT` |
| CC2 | item 10's "no fingerprint AFTER" check stripped | `rc=1`, `(a9)` reports `NOT CAUGHT` |
| CC3 | the fingerprint LINK check stripped | `rc=1`, `(a7)` reports `NOT CAUGHT` |
| CC4 | `factor verify` no longer runs the shared rules | `rc=1`, `NOT CAUGHT` **and** the tombstone signature `ACCEPTED` |
| CC5 | item 12's `fp_after` comparison stripped | `rc=1`, `(a10)` reports `NOT CAUGHT` |
| CC6 | the two heads dropped from what the operator signs | `rc=1`, `NOT REFUSED -- the heads are outside the signature` |
| CC7 | `close_compaction` writes no closing fingerprint | `rc=1`, `(a6d)` fails on the head and the witness |
| CC8 | `contains-tombstone` removed from the refusal | `rc=1`, `(a6e)` COMPACTED, `15 of 19 decisions` |
| CC9 | item 9's position reconstruction stripped | `rc=1`, the renumbering case reports `NOT CAUGHT` |
| CC10 | the console's signature on a witness line not checked | `rc=1`, the stale-signature case reports `BELIEVED` |

Two of these are checks that exist *because* a control was written first. **CL8**
is the reason the AST walk is now run over the producer's formatter and required
to find a float: without it, the walk's zero on the parser could have been the
walk seeing nothing at all. **CC6** is the reason `(a10)` carries a second case
with the signature left alone: with only the head comparison, dropping the two
heads out of the signature changed no result, and item 12's actual claim — that
the signature *covers* them — was untested.

---

## 6 · Where Amendment 4 is still ambiguous for an implementer

Eleven items. Amendment 4 closed all thirteen of O8's; these are what folding it
in surfaced.

### The amount

1. **Item 1's grammar accepts leading zeros, and §12's does not.**
   `parse_amount_micro("01.00")` and `parse_amount_micro("1.00")` both give
   1,000,000, and `"0000000001.5"` gives 1,500,000 — the grammar is
   `-?DIGIT+(.DIGIT+)?` and says nothing about a canonical spelling. §12's
   `_canonical_decimal` refuses a leading zero on every declared 64-bit field,
   for exactly the reason item 1 was written. Under item 7 this no longer forks
   an id, and the micro-unit integer is the same either way, so nothing breaks —
   but the *claim text* has two spellings, and any digest over the source text
   (as opposed to over the record) forks. This harness implements item 1 as
   written and does not refuse them.

2. **There is no length bound on an amount text.** A text of ten million digits
   is lawful under item 1 and this parser will build the integer before the
   range check refuses it, which is a denial-of-service shape at the extractor's
   boundary — the one place the input is other people's bytes. A bound on the
   text, checked before the arithmetic, is the obvious fix and is not written.

3. **Item 4 does not say what a refused amount does to the claim.** The typed
   reason goes on a `refused` row (item 1), but whether the obligation is not
   minted, minted without an amount, or minted and immediately closed is
   unstated, and the three differ in what the account can later count.

4. **Item 6 does not define "class" for "the account counts lossy amounts per
   class".** The record's `cls`, the map's column, or the source? This harness
   tallies per fixture as a placeholder and prints it as one.

5. **Item 6's declared precision has no stated interaction with items 2 and 4.**
   A precision of 6 makes the producer's rounding the *only* rounding, so item
   2's tie rule never runs; a precision below 6 means the producer rounds and
   then the parser does not, so "rounded once at ingest" (item 3) happens in the
   producer, not in the kernel. And a float large enough that formatting it at
   the declared precision leaves the int64 range is refused by item 4 *after*
   the producer has already committed to a text. This file bounds precision to
   0..6 and refuses anything else, which is a choice, not a rule.

6. **Item 6 pins record flag bit 14 and frame flag bit 3 with no published flag
   map to check them against.** §5's `flags` is `uint16` and the blueprint names
   no other bit, so `AMOUNT_LOSSY = 1 << 14` is asserted here and cross-checked
   against nothing. The first collision will be found by an implementer, not by
   a test.

### Compaction

7. **Item 10 is not decidable from a published tape.** A fingerprint written by
   the compactor and one written by the ordinary cadence are the same row shape,
   carry the same body keys, and attest the same head — because a lawful
   compaction does not move the head. The only observable a verifier has is that
   *some* fingerprint follows the tombstone, which is the "after" half of item
   8's bracket. So this pass enforces item 10 constructively on the writer
   (`close_compaction`) and as that observable on the verifier (planted lie 6).
   A tape whose compactor waited for the ordinary cadence and was published
   afterwards is indistinguishable from one that did not wait. A checkable form
   of the stronger rule — for instance, requiring the last fingerprint's
   `row_orig` to post-date every tombstone's original span — is available and is
   not what item 10 says.

8. **Item 12 does not say how a verifier obtains the two bracketing heads.**
   They are fields on the tombstone row here, which puts them inside the row's
   hashed body and therefore inside the keyed chain as well as the signature. An
   implementation that instead recomputed them from the tape at verify time
   would be signing over fields the row does not carry, and could not check a
   tombstone in isolation. The choice is load-bearing and unwritten.

9. **`fp_after` and `span_h` coincide whenever the span ends immediately before
   its bracketing fingerprint**, which is the common case and is the case in
   `(a6)`: both are `0cfee6a865cbeab7`. They diverge only when ordinary rows
   stand between the span's end and the next fingerprint. An implementer who
   only ever tested the adjacent case would not notice that they are two
   different things.

10. **Item 9's reconstruction is a whole-tape computation.** It needs the counts
    of every tombstone before the fingerprint, so a verifier handed one segment
    out of many cannot perform it. Whether the check is per-tape or per-segment
    is unstated, and a per-segment verifier would need each segment to carry the
    tombstone count that precedes it. Related: every compaction in this harness
    is inside a single segment; one that crossed a segment boundary is untested,
    and `row_orig` numbering across a boundary is not exercised.

11. **Item 11 does not say which reason wins when a span holds both a
    fingerprint and a tombstone**, and item 13 does not say which key signs a
    witness line, how a verifier comes to hold that key, or whether the witness
    receives **tombstones** as well as fingerprints. A witness holding only
    fingerprints can bound a compaction's two ends and still cannot see the
    `count` between them, so it can tell that *something* was removed and not
    how much.

---

## 7 · What this pass still does not do

* **No kernel.** Both checks run against models in Python — a ctypes record and
  generated JSONL tapes. They pin the byte-level and order-level questions; they
  do not prove any FACTOR binary obeys them. Item 5's "in the kernel the amount
  is a distinct integer type with no conversion to or from a floating-point
  type, so a float touching an amount fails to compile" is a C++ claim and is
  **not** checked here — `layout_check.cpp` has no amount type, and the AST walk
  is a Python instrument.
* **The parser is not the extractor.** `parse_amount_micro` is the rule made
  executable so the fixtures have something to be fixtures *of*. F-EXTRACT is
  still a stub, and wiring these fixtures into it is M2 work. Item 3's "no map,
  fold, cap comparison or serialization re-rounds an amount" is asserted in
  prose and enforced by F-REPLAY, which is also a stub.
* **`factor compact` is not a program.** `compact_span` and `close_compaction`
  are models of one, over single-segment fixture tapes. A real compaction
  crossing a segment boundary, or one interrupted between the tombstone and its
  closing fingerprint — the exact window item 10 is about — is not exercised.
* **The witness is a file.** Item 13's "any store that can append and cannot
  rewrite" is modelled by an append-only local file with a fixture console key.
  Nothing here proves a transparency log, a second machine or the operator's
  device behaves that way, and nothing distributes the console's key.
* **Forty-seven falsifiers are still stubs.** `94 TODO` is unchanged; Amendment 4
  adds no row and implements none.

---

*O9 · 2026-09-08 · produced by running the files named above, on this machine.*
