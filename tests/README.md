# C:\FACTOR\tests — the falsifiers and the format checks

Everything here is checked against **`BLUEPRINT_v0.2.md`**, the design of record,
**including Amendments 1, 2, 3 and 4 (2026-09-08)** at the bottom of that file.
`BLUEPRINT.md` (v0.1) is superseded and is referenced only where a planted lie
needs something false to assert.

**Amendment 4** makes Amendment 3 implementable: it settles the thirteen things
`qc/O8_tests_amend3.md` listed as still invented rather than specified. On the
amount side, `check_layout.py` now carries **item 1's grammar** in as many words
— an optional ASCII minus, digits, optionally a period and digits, and nothing
else, so a leading `+` and a lone `-` join the refusals — **item 2's rounding on
the whole discarded tail** (the phrase "at the seventh decimal place" is
withdrawn, and fixture 13 is the case that separates the two readings), **item
4's range refusal**, where a micro-unit value outside `int64` is refused with a
typed reason and *never saturated*, with fixtures one micro-unit inside and one
outside the bound on each side of zero and a clamping parser as the planted lie,
and **item 6's lossy amount**, where a source column stored as a binary float
declares its `precision`, the producer formats at that precision into the
grammar, and the frame carries flag bit 3 with the record carrying flag bit 14.
That formatter is the one place a binary float may touch an amount, and the same
AST walk that finds none in the parser finds it there — which is how the walk is
shown to be measuring rather than agreeing. **Item 7** takes the amount out of a
derived obligation's id, so the parse is no longer identity-bearing; it stays law
because the record's digest, the caps and replay all read the integer, and
`F_EXTRACT.py`'s docstring says so.

On the compaction side, `chain_check.py` gains **item 8**: the bracket check and
the fingerprint-chain check live in one function, `compaction_rules`, called by
`factor verify` *and* by `verify --chain-only`, so planted lies 4 and 5 are now
caught by both — the writer's refusal is hygiene, and the one adversary
compaction has is the holder of the operator key, who is the person running the
keyed verifier. **Item 9** pins the fingerprint body as `{head, seg, row_orig}`
and has a verifier reconstruct position by subtracting the counts of the
tombstones before it; a lawful compaction is *measured* to leave every attested
body and every `fp_h` byte-identical while positions move, and a compactor that
renumbers is caught. **Item 10** has the compactor append a fingerprint at once,
before the tape is publishable, and a tape published carrying an unfingerprinted
tombstone is **planted lie 6**. **Item 11** makes a tombstone a protected row,
refused with reason `contains-tombstone` even when the span is otherwise
strictly between two fingerprints. **Item 12** puts the two bracketing
fingerprint heads under the operator's signature, checked both ways — moved and
re-signed is **planted lie 7**, caught by the comparison; moved and left unsigned
is caught by the signature. **Item 13** gives the witness's copy a form: one
canonical-JSON line per fingerprint with the console's signature over it,
appended and never rewritten, with a line the console never signed and a signed
line that disagrees with the tape caught by different mechanisms.

**Amendment 3** settles the two findings `qc/O7_tests_amend1.md` measured, and
both are now checks rather than notes. **Item 1, the amount parse**, is
`check_layout.py`'s block `[5]`: an amount is parsed from its text as a decimal
by digit arithmetic and rounded half-even on the whole discarded tail (Amendment
4 item 2 withdrew "at the seventh decimal place"), with no floating-point value
anywhere — asserted by walking the parser's own AST, not by
trusting its comments — over eighteen fixtures that carry O7's five tie cases
plus negatives, values with more than seven decimal places, and ties that round
up as well as down; the planted lie is the same rule applied to the double the
text parses to, and it must differ on at least one fixture (it differs on eight)
or the fixtures are proving nothing and the check fails. **Item 2, compaction**,
is `chain_check.py`'s `(a6)`, `(a6b)`, `(a7)` and `(a8)`: `factor compact`
replaces only rows strictly between two fingerprints and refuses anything else
with the typed `CompactionRefused`, writing nothing; after a lawful compaction
the keyed tape chain reaches the same head, the unkeyed fingerprint chain
verifies, and `verify --chain-only` reports zero errors. Its two planted lies
are that refusal skipped in each direction — a span containing a fingerprint,
and a span outside every attested bracket. The keyed chain and its head stay
clean through both, which is why O8 could only catch them keylessly; Amendment 4
item 8 puts the rule in both verifiers and both lies are now caught twice.

Three things Amendment 1 changed, and every file here now follows:

* **The frame has an eighth field.** §4's line is
  `t_mono_ns · venue · lane · grain · rev · f · text · h`, where `f` is a small
  integer of frame flags — bit 0 `badenc`, bit 1 `truncated`, bit 2
  `synthetic_rev` — so the badenc mark has a home on the frame itself. `h` covers
  fields 1–7 with their tabs, escaped, excluding the tab before `h`, `h`, and the
  newline. `\xNN` at or below `0x7F` is a code point; at or above `0x80` it is a
  raw byte, legal only when bit 0 of `f` is set.
* **The personalization strings are pinned and are at most sixteen bytes:**
  `FCTR-tape-v1`, `FCTR-dossier-v1`, `FCTR-ledger-v1`, `FCTR-ckpt-v1`,
  `FCTR-spool-v1`, `FCTR-fprint-v1`. The v0.2 template that produced a
  seventeen-byte `"FACTOR dossier v1"` is withdrawn. The spool chain stays
  unkeyed but is personalized `FCTR-spool-v1`, so an unkeyed BLAKE2b elsewhere
  cannot verify as a spool line.
* **`amount_fix` counts micro-units** — one millionth of `unit`, not 1/65536.
  A cent is exactly 10,000; rounding is round-half-even to the micro-unit,
  applied once at ingest. The record layout is unchanged: `int64` at offset 72
  either way.

One thing Amendment 2 measured, and the two sandbox falsifiers now name:

* **The sandbox mechanism in force is `os-enforced`.** A zero-capability
  AppContainer profile, created and applied by the launcher with
  `PROCESS_CREATION_CHILD_PROCESS_RESTRICTED`, refuses the kernel's sockets at
  WFP's ALE layers keyed on the package SID, with no administrator and no
  installer; the card runs inside it at full speed
  (`receipts/M0_SANDBOX_PROBE_2026-09-08.md`). §11's three header-row words are
  `os-enforced`, `wfp-installed` and `lint-only`, and §22's M0 deliverables
  include "the sandbox mechanism on the header row". The three refusal routes
  F-EGRESS names are the ones measured: the socket library, refused with
  `WSAEACCES` (10013); a connect to a live loopback listener, refused with
  `WSAETIMEDOUT` (10060), a timeout and not a fast failure; and the raw device
  control, the `AFD_CONNECT` IOCTL over a handle from `NtCreateFile` on
  `\Device\Afd\Endpoint`, which opens inside the container while the raw
  `\Device\Afd` open is denied with `0xC0000022`. The probe never drove that
  IOCTL, so the third route is inferred and the M0 receipt reads
  `afd: inferred` until F-EGRESS drives it and observes the refusal itself.
  `F_EGRESS.py` and `F_ORGAN_NET.py` say so; nothing here runs inside a
  container yet.

Two kinds of file live here.

**Format checks** run today, against generated data, with no kernel. They pin the
byte-level questions the blueprint leaves open and prove their own tests have
teeth by carrying planted lies of their own.

| file | checks | run |
|---|---|---|
| `check_layout.py` | §5 `struct Obligation`: size, alignment, every pinned offset, no implicit padding, endianness; the micro-unit `amount_fix` block; and the **decimal amount parser** with its 18 fixtures, **item 1's grammar** over 10 refusals, **item 4's int64 range** over 4 boundary fixtures, **item 6's lossy amount** over 2, and **two** planted lies — the double path and the clamping parser (Amendment 3 item 1, Amendment 4 items 1, 2, 4, 6) | `python C:/FACTOR/tests/check_layout.py` |
| `layout_check.cpp` | the same record at compile time: `static_assert` on 128/8, every offset, and the summed field widths | `cl /std:c++20 /EHsc /W4 layout_check.cpp` or `g++ -std=c++20 -Wall -Wextra` |
| `frame_roundtrip.py` | §4 **eight**-field frame with `f`, STRICT escaping, the chain hash as field 8 under `FCTR-spool-v1`, 10 000 randomised strings, the field caps and the line bound, invalid UTF-8 on a frame that carries the mark, **5** planted lies | `python C:/FACTOR/tests/frame_roundtrip.py` |
| `chain_check.py` | §12 keyed tape chain, the **fingerprint chain** with its body pinned as `{head, seg, row_orig}` and `verify --chain-only`, the signed **tombstone** across a compacted span with both bracketing heads under the signature, the **spans compaction refuses** including `contains-tombstone`, the **closing fingerprint** a compaction must be published with, the **witness's canonical-JSON copy**, and the compaction rules held by **both** verifiers (Amendment 3 item 2, Amendment 4 items 8–13), §4 unkeyed spool chain, the four-part cursor, torn rows, segments and the manifest, canonical JSON by declared width, the plan hash, **7** planted lies | `python C:/FACTOR/tests/chain_check.py` |

`layout_check.cpp` compiled with `-DPROVE_SPEC_FAILS` **must fail to compile**.
That is its planted lie, and it is exactly the one §21's F-LAYOUT row names: it
asserts the **v0.1** record (float margins, no `release_ns` / `seq` / `n_wit` /
`n_wait` / `tie` / `unit`, `_pad[14]`) is 128 bytes. It is 120. MSVC exits 2 with
C2338; g++ exits 1 and prints *the comparison reduces to (120 == 128)*.

**Falsifiers** are the **forty-seven** properties of §21 as amended — its
forty-five rows plus the two Amendment 1 item 24 adds for the M8 gate — one file
each, currently stubs. Run them all with:

```
python C:/FACTOR/tests/run_falsifiers.py            # one line per falsifier
python C:/FACTOR/tests/run_falsifiers.py --verbose  # + what each stub must assert
python C:/FACTOR/tests/run_falsifiers.py --gate M0  # just one gate's falsifiers
```

The runner exits 0 while falsifiers are unwritten (`TODO`) and 1 on any `FAIL`,
`ERROR` or `MISSING`. An unwritten falsifier is not a build failure; a broken or
absent one is. Every falsifier is named explicitly in the runner's table with its
§21 id and its §22 gate, so three things fail loudly rather than silently: a file
that is deleted or renamed (`MISSING`), a module whose `ID` does not match its row
(`ERROR`), and a module whose `MILESTONE` does not match §22 (`ERROR`).

## The contract every falsifier obeys

Each `F_<ID>.py` exports four constants and two functions:

```python
ID          = "F-CONSERVE"     # §21's id
MILESTONE   = "M0"             # the §22 gate this falsifier closes
REQUIRES    = "..."            # §21's `requires` column
PLANTED_LIE = "..."            # §21's `the planted lie` column

def requires():
    """Returns None when the property holds.
       Raises AssertionError, carrying the counterexample, when it does not."""

def planted_lie():
    """Builds the sabotaged system this falsifier is aimed at, runs requires()
       against it, and asserts that requires() FAILED.
       A falsifier whose planted lie passes is measuring nothing, and that is
       the failure this function reports."""
```

Both raise `NotImplementedError` until written, with the one-sentence statement
of what they must assert as the message — which is what `--verbose` prints.

A dash in a §21 id becomes an underscore in the filename: `F-BOTH-SIDES` is
`F_BOTH_SIDES.py`, `F-ROLLBACK-MONOTONE` is `F_ROLLBACK_MONOTONE.py`.

## The forty-seven, in §21 table order, the two M8 rows last

| # | file | id | gate | requires | the planted lie |
|---|---|---|---|---|---|
| 1 | `F_RESIDENT.py` | F-RESIDENT | M1 | a run with no frames writes no verb row; every verb row's wake names a frame | a verb from a timer callback |
| 2 | `F_TICK.py` | F-TICK | M7 | a restored trunk receives one tick for its absence; the first frame's margins match a no-restart control within the tie band | resume with no tick |
| 3 | `F_RIPEN.py` | F-RIPEN | M1 | a deadline crossing with no inbound frame still produces a verb row | walk only the event-touched set |
| 4 | `F_EXTRACT.py` | F-EXTRACT | M2 | planted promises recovered at the tolerance; retractions close; a forwarded quote is one witness | offsets emitted by the model; a quote counted twice |
| 5 | `F_SILENCE.py` | F-SILENCE | M1 | a judgment without a row is fatal; no open obligation lacks a standing verb | a hold with no row |
| 6 | `F_CONSERVE.py` | F-CONSERVE | M0, M2 full | every frame lands in exactly one of eight dispositions | drop one frame silently; count a replayed batch twice |
| 7 | `F_REPLAY.py` | F-REPLAY | M0 | a full replay of the spools reproduces the ledger digest bit-identically without re-running the model | a float accumulator; a re-run extractor |
| 8 | `F_DETERMINISM.py` | F-DETERMINISM | M0 | two runs, two insertion orders, byte-identical plan hashes | walk in hash-map order |
| 9 | `F_QUANTA.py` | F-QUANTA | M1 | replay under a perturbed batch composition reproduces every verb row; rows that differ carry `tie` | compare raw logits and call the difference a pass |
| 10 | `F_SALT.py` | F-SALT | M4 | every lottery assignment is reproducible from the writ and unpredictable from the trunk | a system random generator |
| 11 | `F_CHAIN.py` | F-CHAIN | M0 | one flipped byte in a segment fails `verify`; a row rewritten with its hash recomputed fails the link check | a row-local verifier |
| 12 | `F_INERT.py` | F-INERT | M1 | with the switch `off`, every venue is byte-identical to FACTOR absent; with `shadow`, the hand receives no effect | an effect under `shadow` |
| 13 | `F_INERT_BYTES.py` | F-INERT-BYTES | M1 | a planted frame carrying an effect message, a verb name, a writ stanza and an organ answer produces a frame row and a verb row and nothing else | the seam parses a verb name out of frame text |
| 14 | `F_BLIND.py` | F-BLIND | M1 | with the counterparty's frames removed, the check and guard margins never fall below the full read's | use the full read alone |
| 15 | `F_STANDING.py` | F-STANDING | M2 | an obligation witnessed only by a party without standing never reaches DO at any rung | standing inferred from politeness |
| 16 | `F_EGRESS.py` | F-EGRESS | M0, M3 full | a probe opens a socket by three routes, the socket library (`WSAEACCES` 10013), a live loopback connect (`WSAETIMEDOUT` 10060) and the `AFD_CONNECT` IOCTL over a `\Device\Afd\Endpoint` handle, and all three are refused by the OS, the third driven and observed, never inferred; the egress ledger equals the sum of its rows; no process in the tree holds a socket | a module-list check standing in for the OS refusal; an organ child that opens a socket |
| 17 | `F_WINDOW.py` | F-WINDOW | M3 | a windowed effect reversed inside its window leaves no trace in the world and a `reversed` row, against the provider actually wired | release before the window |
| 18 | `F_ORDER.py` | F-ORDER | M3 | every `executed` row is preceded by its `staged` and `verb` rows; a failed effect leaves a `verb` row and a `warn` | execute then record |
| 19 | `F_BUDGET.py` | F-BUDGET | M1 | two thousand asks, room for ten, the rest hold on budget and nothing acts; the stratum is funded first | act because nobody was available |
| 20 | `F_TERMINAL.py` | F-TERMINAL | M4 | an obligation past due with no license and no budget takes its safe terminal; `expired` never precedes an `asked` or a `hold(budget)` | hold silently |
| 21 | `F_SELF.py` | F-SELF | M1 | a dead producer opens a `health` obligation within one tick; health never reaches DO, never autostarts, never exceeds `self_share` | health at DO; an autostart |
| 22 | `F_JURY.py` | F-JURY | M5 | one dissenting family and the irreversible effect holds; a quorum of one family counted twice is refused; an approval bound to different effect bytes is refused | two judges of one lineage as two families |
| 23 | `F_FAMILY.py` | F-FAMILY | M5 | two judges of the same lineage agreeing wrongly do not clear a two-family quorum | lineage ignored |
| 24 | `F_CAP.py` | F-CAP | M5 | an effect above the per-act, per-day or per-party cap never leaves; raising the cap fails at the provider; a first-time payee always asks | a full-permission key |
| 25 | `F_MONOTONE.py` | F-MONOTONE | M4 | the license fold cannot widen a band without a covering signed ratification row; a ratify row over the API is refused; a seen nonce is refused | widen on grades alone |
| 26 | `F_COVERED.py` | F-COVERED | M4 | every `executed` row at rung 3+ has an unexpired covering ratify row; no `executed` row in a class whose kappa read at or above one | an executed row one revision after expiry |
| 27 | `F_BOTH_SIDES.py` | F-BOTH-SIDES | M4 | a band is not calibrated until both sides clear `n0`; an outcome forged from the hand's own receipt does not calibrate | license on act evidence only |
| 28 | `F_WITNESS.py` | F-WITNESS | M4 | a planted self-written close never licenses; an outcome from the lane the effect wrote to is a receipt | grade a calendar confirm from the calendar it wrote |
| 29 | `F_PREDICT.py` | F-PREDICT | M4 | every bet precedes its grade in horizon order; a re-fold reproduces every e-value bit-identically | a bet computed from the grade it reads |
| 30 | `F_DETECT.py` | F-DETECT | M4 | a class good for 500 grades then degraded for 40 is demoted; a fixed-start process on the same tape is not | demotion by a fixed-start process |
| 31 | `F_EXPIRY.py` | F-EXPIRY | M4 | a rung past its ratification's window drops one; classes ratified together do not expire in one cohort | permanent once approved |
| 32 | `F_CANARY.py` | F-CANARY | M4 | under `live`, a rung-2 class acts on the lottery's fraction and no other instance; every canary effect reverses cleanly | a canary on an irreversible effect; a canary with no covering row |
| 33 | `F_FRONT.py` | F-FRONT | M6 | a planted distribution shift suspends the class before its expiry; a stationary stream does not | fronts read at the fold's cadence |
| 34 | `F_DARK.py` | F-DARK | M6 | an obligation with no recency, ripeness or expectation is judged within N periods | rank only what moved |
| 35 | `F_OBSERVE.py` | F-OBSERVE | M9 | a staggered arm measures whether being shadowed changes the person's behaviour | assume it does not |
| 36 | `F_ROLLBACK.py` | F-ROLLBACK | M7 | folds re-derived to an earlier head match the folds stamped at that head; the rollback row is honoured as a fold instruction | a fold that reads past its head; a fold that re-applies a shadowed row |
| 37 | `F_ROLLBACK_MONOTONE.py` | F-ROLLBACK-MONOTONE | M7 | a rollback never re-widens a band | restore yesterday's license |
| 38 | `F_MOLT.py` | F-MOLT | M7 | a planted fact in the oldest band survives the fold at the family's ratio or the account prints `lossy` | silent truncation at the watermark |
| 39 | `F_CONTRADICT.py` | F-CONTRADICT | M6 | a typed disagreement is caught by the comparator, a prose one by the inference head, neither by the other; a contested pair is never resolved | one head for both |
| 40 | `F_DEGRADE.py` | F-DEGRADE | M6 | an obligation whose check evidence depended on an organ answering 3, 4, 5 or 6 never reaches DO | a missing organ as a clean check |
| 41 | `F_REDACT.py` | F-REDACT | M6 | a brief is assembled by code from declared fields through the redactor; its bytes are on the tape | a brief assembled by the model |
| 42 | `F_COMPILE.py` | F-COMPILE | M7 | a ratified routine replays bit-identically; an out-of-domain instance falls back; a diverging routine suspends in real time | a routine that passes on a sample; a routine that extrapolates |
| 43 | `F_PIN.py` | F-PIN | M0 | a drifted serve byte, weight, quantization, schema map, runtime version, context parameter or environment variable refuses to boot | a supplied identity trusted unchecked |
| 44 | `F_LAYOUT.py` | F-LAYOUT | M0 | `sizeof(Obligation) == 128`, every offset as pinned, no implicit padding | the v0.1 claim asserted |
| 45 | `F_FRAME.py` | F-FRAME | M0 | 10,000 random strings round-trip; each is one line to every reader | an encoder that drops carriage returns |
| 46 | `F_ORGAN_DEGRADE.py` | F-ORGAN-DEGRADE | M8 | an absent organ degrades with code 6 and the account names it | a crash |
| 47 | `F_ORGAN_NET.py` | F-ORGAN-NET | M8 | an organ child that opens a socket is refused by the sandbox | a declaration trusted without confinement |

Rows 46 and 47 are Amendment 1 item 24's. §21's table in `BLUEPRINT_v0.2.md`
still shows forty-five rows; the amendment is what makes it forty-seven, and it
is also what gates F-SELF at M1. Item 24 gives the two new rows a `requires` and
a planted lie but **no `law` column** — the stubs record `§16` for
F-ORGAN-DEGRADE and `5, §16` for F-ORGAN-NET as a reading, not as the text.
F-ORGAN-NET's stub names the same three routes as F-EGRESS, with the same three
observations, because a `net: none` organ is spawned by the launcher into the
same container under the kernel's package SID.

## By milestone gate (§22)

| gate | count | falsifiers |
|---|---:|---|
| M0 · the kernel boots | 8 | F-LAYOUT, F-FRAME, F-CHAIN, F-CONSERVE (without the heard bucket), F-REPLAY, F-DETERMINISM, F-PIN, F-EGRESS |
| M1 · the judge | 9 | F-INERT, F-INERT-BYTES, F-BLIND, F-QUANTA, F-BUDGET, F-SILENCE, F-RESIDENT, F-RIPEN, F-SELF |
| M2 · the extractor and the first lane | 2 | F-EXTRACT, F-STANDING (+ F-CONSERVE full) |
| M3 · the hand | 2 | F-WINDOW, F-ORDER (+ F-EGRESS full) |
| M4 · the ladder | 10 | F-MONOTONE, F-BOTH-SIDES, F-WITNESS, F-PREDICT, F-DETECT, F-EXPIRY, F-CANARY, F-COVERED, F-SALT, F-TERMINAL |
| M5 · the jury and the cap | 3 | F-JURY, F-FAMILY, F-CAP |
| M6 · the folds | 5 | F-FRONT, F-CONTRADICT, F-DEGRADE, F-DARK, F-REDACT |
| M7 · compiler, grower, rollback, molt | 5 | F-COMPILE, F-ROLLBACK, F-ROLLBACK-MONOTONE, F-MOLT, F-TICK |
| M8 · organs and surfaces | 2 | F-ORGAN-DEGRADE, F-ORGAN-NET |
| M9 · the tune | 1 | F-OBSERVE |

M0's deliverables in §22 also include "the sandbox mechanism on the header row".
Amendment 2 measured it as `os-enforced` on this machine, and F-EGRESS is the
falsifier that reads the header row's word against the refusals it observes — a
reading of §22 recorded in `F_EGRESS.py`, since §21's row does not name the
header row.

The two mismatches between §21 and §22 that the previous pass carried are both
**closed by Amendment 1 item 24**, and the runner's table now says so rather than
carrying them:

* **F-SELF was named by no §22 gate**, so nothing in the build order forced it to
  be written. It is now gated at **M1**, where the `health` lane ships.
* **M8 had no §21 falsifier.** It now has two, from §22's own prose gates.
  §22's third M8 condition — a widening ratify over the API is refused — is still
  covered only by F-MONOTONE's second clause, which is gated at M4; Amendment 1
  added rows for the first two and not for that one.

## Running everything

```
python C:/FACTOR/tests/check_layout.py         # exit 0
python C:/FACTOR/tests/frame_roundtrip.py      # exit 0
python C:/FACTOR/tests/chain_check.py          # exit 0
python C:/FACTOR/tests/run_falsifiers.py -v    # exit 0, 94 TODO

cl  /std:c++20 /EHsc /W4                  C:/FACTOR/tests/layout_check.cpp  # 0
cl  /std:c++20 /EHsc /W4 /DPROVE_SPEC_FAILS ...                             # 2
g++ -std=c++20 -Wall -Wextra              layout_check.cpp                  # 0
g++ -std=c++20 -Wall -Wextra -DPROVE_SPEC_FAILS ...                         # 1
```

All four Python checks are green against v0.2 as amended. The two
`PROVE_SPEC_FAILS` builds are green by failing.

The run against v0.2 as published is `C:\FACTOR\qc\O6_tests_v0.2.md`; the run
after Amendment 1, with every printed number and what the amendment still leaves
ambiguous, is `C:\FACTOR\qc\O7_tests_amend1.md`. The Amendment 2 follow-up that
sharpened `F_EGRESS.py` and `F_ORGAN_NET.py` is noted at the end of that file's
§8. The Amendment 3 pass — the amount fixtures, the compaction refusal, and what
item 1 and item 2 still leave for an implementer to invent — is
`C:\FACTOR\qc\O8_tests_amend3.md`. The Amendment 4 pass, which folds all
thirteen of that file's open items into the harnesses and lists what is left
after them, is `C:\FACTOR\qc\O9_tests_amend4.md`.
