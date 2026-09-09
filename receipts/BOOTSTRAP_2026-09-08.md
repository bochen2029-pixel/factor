# BOOTSTRAP · 2026-09-08 · the implementing session's read and the state it verified

This receipt covers the bootstrap step only: the reading order in
`HANDOFF_FOR-THE-IMPLEMENTING-SESSION_2026-09-08_FABLE5-1.md` §3 was executed in
order, and every fact in the handoff's §4 was re-checked with a command before
being relied on. No file in the tree was created, edited or deleted by this step
except this receipt. No code was written. M0 has not been started.

---

## 1 · What was read, in the handoff's order

| # | file | bytes | read |
|---|---|---:|---|
| 1 | `CLAUDE.md` (identical to `AGENTS.md`, verified by `diff`) | 5,128 | full |
| 2 | `KICKOFF_M0.md` with Amendment 1 | 10,372 | full |
| 3 | `BLUEPRINT_v0.2.md` §0–§5, §8, §12, §19, §21, §22, §23, Amendments 1–6 | 131,381 | the named ranges, amendments in full |
| 4 | `receipts/M0_SANDBOX_PROBE_2026-09-08.md` | 12,812 | full |
| 5 | `tests/README.md`, `tests/run_falsifiers.py`; `check_layout.py`, `chain_check.py`, `frame_roundtrip.py` | 24,655 + 4,645 lines | README full, runner header full, three models skimmed and run |
| 6 | `qc/QC_SYNTHESIS_2026-09-08.md`, `qc/O9_tests_amend4.md` | 19,616 + 41,306 | synthesis full; O9 headline, §3, §7 |
| 7 | `NEXT.md` | 4,067 | full |
| 8 | `PROPOSAL_REV1_AUTONOMY-TO-THE-MAX_2026-09-08_FABLE5-1.md` | 29,950 | §0–§1.5, §6–§10 |
| 9 | `C:\55555\THE-ONE-DESIGN_...md`, `C:\55555\THE-BLUEPRINT_PLAIN_...md` | 9,993 + 19,339 | full |

Not read, per the handoff's "do not read" list: `BLUEPRINT.md` v0.1,
`DRIVING_THE_ORGANIZATION.md` and its notes, `qc/A_`, `qc/B_`, `qc/O1`–`qc/O5`,
`qc/O6`–`qc/O8`, the nine-session tape, the rest of `C:\55555`.

---

## 2 · The state of the tree, each claim with its command

**No git.**

```
ls -la C:/FACTOR/.git
ls: cannot access 'C:/FACTOR/.git': No such file or directory
```

**No source beyond the tests and the reference probe.** `C:\FACTOR` holds 12
files and 4 directories at the root, counted by `ls -p | grep -v / | wc -l` and
`ls -p | grep / | wc -l`; `launcher/`, `kernel/`, `seam/`, `hand/`,
`console/`, `lanes/`, `organs/`, `writ/`, `tools/` and `build/` do not exist.
`tests/` holds 47 `F_*.py`, 4 Python models, `layout_check.cpp`,
`msvc_check.cmd`, `README.md`. `probe/` holds 2 sources, 2 exes with their objs,
8 output files, `build.cmd`. `qc/` holds 12 markdown files. `receipts/` held 1
file before this one.

**The gate command is green.**

```
python C:/FACTOR/tests/run_falsifiers.py
  TODO 94
  by section 22 gate
    M0 8  M1 9  M2 2  M3 2  M4 10  M5 3  M6 5  M7 5  M8 2  M9 1
  RESULT: scaffold intact -- 94 of 94 functions are stubs (TODO), 0 implemented and passing
EXIT=0
```

94 of 94 functions are stubs: 47 falsifiers × 2 functions (`requires`,
`planted_lie`). The gate table sums to 47 of 47 falsifiers.

```
python C:/FACTOR/tests/run_falsifiers.py --gate M0
  F_CONSERVE F_REPLAY F_DETERMINISM F_CHAIN F_EGRESS F_PIN F_LAYOUT F_FRAME
  TODO 16
  RESULT: scaffold intact -- 16 of 16 functions are stubs (TODO), 0 implemented and passing
EXIT=0

python -W error C:/FACTOR/tests/run_falsifiers.py --gate M0
EXIT=0
```

16 of 16: 8 M0 falsifiers × 2 functions.

**The three Python models are green.**

```
python C:/FACTOR/tests/check_layout.py
  RESULT: PASS -- section 5's record is 128 bytes, alignof 8, every offset
          as pinned, no implicit padding anywhere, planted lie caught;
          18 amount fixtures parse to their expected micro-unit integers
          by decimal digit arithmetic, and the double path is caught
          differing on 8 of them (Amendment 3 item 1);
          10 malformed texts refused by item 1's grammar, 4 range
          fixtures at the int64 bound with the clamping parser caught,
          and 2 lossy fixtures formatted at a declared precision and
          flagged on frame bit 3 and record bit 14 (Amendment 4).
EXIT=0

python C:/FACTOR/tests/frame_roundtrip.py
  round trip, all 8 fields + chain hash : PASS  (10000/10000 passed)
  RESULT: ALL CHECKS PASS
EXIT=0

python C:/FACTOR/tests/chain_check.py
  RESULT: ALL CHECKS PASS
EXIT=0
```

**The MSVC leg of F-LAYOUT is green, and its planted lie is caught.** Run twice,
identical both times.

```
C:/FACTOR/tests/msvc_check.cmd
  CL_CLEAN_EXIT=0
  RUN_EXIT=0
  CL_LIE_EXIT=2
  LIE_REFUSED_C2338
  LIE_NO_BINARY_GOOD
PS_EXIT=0            (39 lines of output; every offset printed matches §5)
```

The clean build compiles and its binary exits 0; the `-DPROVE_SPEC_FAILS` build
of the v0.1 record fails with C2338 and produces no binary. That is 1 planted lie
of 1 caught on this leg.

**The gate after this step.** `python C:/FACTOR/tests/run_falsifiers.py` →
`GATE_EXIT=0`, unchanged from before it.

---

## 3 · The toolchain, verified

| tool | version | path |
|---|---|---|
| Python | 3.13.2 | on PATH |
| CMake, on PATH | 4.3.3 | on PATH |
| CMake, VS 2022 Community | 3.31.6-msvc6 | `.../Common7/IDE/CommonExtensions/Microsoft/CMake/CMake/bin/cmake.exe` |
| Ninja | 1.12.1 | `.../Common7/IDE/CommonExtensions/Microsoft/CMake/Ninja/ninja.exe` |
| MSVC | 19.44 via `vcvars64.bat` | `C:/Program Files/Microsoft Visual Studio/2022/Community/VC/Auxiliary/Build/vcvars64.bat` |

Kickoff Amendment 1 requires CMake 3.28 with Ninja from the VS 2022 developer
environment; both exist at the paths above. The `cmake` on PATH is 4.3.3, a
different program from the one the amendment names.

Present, verified by `ls -d`: `C:\backrooms`, `C:\Booster_Lander_Simulator`,
`C:\connectome\native`, `C:\TAPESTRY`, `C:\llama.cpp`, `C:\peek`, `C:\gym`.

---

## 4 · Findings from the bootstrap

Four measured disagreements. None is fixed here; the handoff §7 says a harness is
a claim about the spec, not the spec, and that both are reported and neither is
changed silently.

**F1 · The two amount harnesses disagree with each other about frame flag bit 3,
and `frame_roundtrip.py` disagrees with the spec.** Amendment 4 item 6 and
Amendment 6 item 6 pin frame `f` bit 3 as `lossy_amount`.
`check_layout.py:174` carries `FRAME_FLAG_LOSSY_AMOUNT = 1 << 3` and its item-6
block sets it on 2 of 2 lossy fixtures. `frame_roundtrip.py:74` has
`F_KNOWN = F_BADENC | F_TRUNCATED | F_SYNTHETIC_REV`, bits 0–2 only, and
`parse_f` refuses anything outside it. Measured, by importing both models:

```
frame_roundtrip.F_KNOWN              = 7 (bits [0, 1, 2])
check_layout.FRAME_FLAG_LOSSY_AMOUNT = 8 (bit 3)
check_layout.RECORD_FLAG_AMOUNT_LOSSY = 16384 (bit 14)
  parse_f('7' ) -> 7   ACCEPTED
  parse_f('8' ) -> REFUSED: f carries unknown flag bit(s) 0x8 -- the decoder is strict, the frame is refused
  parse_f('15') -> REFUSED: f carries unknown flag bit(s) 0x8 -- the decoder is strict, the frame is refused
  parse_f('16') -> REFUSED: f carries unknown flag bit(s) 0x10 -- the decoder is strict, the frame is refused
```

A lawful frame carrying a lossy amount is refused by the spool decoder model as
written. Bit 4 and above being refused is consistent with Amendment 6 item 6
("No bit is free; a new flag is a header version"); bit 3 being refused is not.

**F2 · The amount harness does not carry Amendment 6 items 1, 2 and 3.**
Measured against `check_layout.parse_amount_micro`:

| Amendment 6 item | rule | measured today |
|---|---|---|
| 1 | a leading zero before another digit is refused with reason `grammar` | `'007'` → 7000000 ACCEPTED; `'01.00'` → 1000000 ACCEPTED |
| 2 | a text longer than 40 bytes is refused **before any digit is read** | 41 digits → refused, but by the int64 range check after the digit arithmetic, reason `AmountRange`, not by a length bound |
| 3 | a refused amount mints the obligation with `amount_fix = 0` and flag bit 15 `AMOUNT_ABSENT` | no `AMOUNT_ABSENT` or equivalent constant exists in the file |

`'0'`, `'0.5'` and `'-0'` parse; item 1 names only the leading zero before
another digit, so `'0.5'` is lawful and `'-0'` is unstated (ambiguity A5 below).

**F3 · The chain harness does not carry Amendment 6 items 7, 10 and 11's second
half, and its own "still open" list names three of them as open.** Amendment 6
item 10 requires a per-segment header carrying the cumulative tombstone count
and the `row_orig` of the segment's first row, and refuses a span crossing a
segment boundary with reason `crosses-segment`; item 11 requires the witness to
receive tombstone rows as well as fingerprints; item 7 gives item 10 a checkable
form on the published tape. `grep` over `chain_check.py` finds
`unbracketed` and no `crosses-segment`, no cumulative tombstone count, no
per-segment `row_orig`. The file's printed items (g), (i), (j) are exactly these
three, and item (k) is settled by Amendment 6 item 11's precedence rule, which
the file's behaviour already matches but does not assert. Item (h) is settled by
Amendment 6 item 8 in the harness's favour: the bracketing heads are fields on
the tombstone row, inside its hashed body.

**F4 · Amendment 5 item 9 is not in the chain harness, and it may contradict
Amendment 1 item 19.** Item 19 says the *kernel* writes a `fingerprint` row at
every segment close and every 4,096 rows. Item 9 lists `fingerprint` among
fold-emitted rows, which are "written by folds onto the tape, stamped with the
head they were computed from", recomputed on replay and compared by
`factor verify`. `grep` finds no `stamp` and no fold-emitted-row handling in
`chain_check.py`. The handoff §4 flagged this as unaddressed; it is, and the two
amendment texts assign the writer differently.

`tests/README.md` states its scope as "Amendments 1, 2, 3 and 4". F1 to F4 are
the measured extent of what Amendments 5 and 6 add beyond that scope.

---

## 5 · What was not done

1. No code was written. `launcher/`, `kernel/`, `seam/`, `build.cmd`,
   `gate.cmd`, `CMakePresets.json` do not exist and were not started.
2. No harness was changed. F1 to F4 are reported, not fixed.
3. No falsifier stub was turned into a falsifier. 94 of 94 functions remain TODO.
4. The g++ second opinion on `layout_check.cpp` under WSL was not run; only the
   MSVC leg was re-verified this session.
5. `probe/launcher.exe` and `probe/probe.exe` were not run. The sandbox receipt
   was read, not reproduced.
6. `qc/O6`, `qc/O7`, `qc/O8`, `qc/A_`, `qc/B_`, `qc/O1`–`qc/O5` were not opened.
7. `tests/__pycache__/check_layout.cpython-313.pyc`, dated 2026-09-08 14:58 and
   not written by this session, is still in the tree. It was left alone.
8. The joint format amendment with TAPESTRY was not read or written; nothing
   under `C:\TAPESTRY` was opened.

---

## 6 · Ambiguities, with the default taken

Each is carried into M0. A1 to A4 are identity-bearing or hash-bearing and are
the handoff §7's "stop and ask in one line with a default" class; they are asked
in the report and defaulted here so the work is not blocked.

1. **A1 · Frame flag bit 3 (F1).** Default: the spec wins. The M0 spool decoder
   accepts `f` bit 3 as `lossy_amount` and refuses bit 4 and above, and
   `frame_roundtrip.py`'s `F_KNOWN` is a harness defect to be reported with the
   M0 receipt, not silently widened.
2. **A2 · The tape's spelling of the pinned enums.** §12 never says whether a
   row writes `verb` as the number or the name; the plan hash covers `verb` and
   `reason`, so two spellings are two plan hashes. Default: the pinned number,
   as the record holds it, with the name nowhere on the tape.
3. **A3 · The declared width of `seg` and `row_orig`.** Amendment 1 item 17
   decides string-versus-number by declared width; Amendment 4 item 9 names
   `row_orig` without giving it one. Default: both are 64-bit and therefore
   decimal strings, which is what `chain_check.py` does today.
4. **A4 · What a `fingerprint` row carries outside its pinned body.**
   Amendment 4 item 9 pins the body as `{head, seg, row_orig}` and says nothing
   about the rest of the row. Default: `{fp_prev, fp_h, ms, k, prev, h}` outside
   the body, as `chain_check.py` writes it.
5. **A5 · `-0` as an amount text.** Amendment 6 item 1 gives the amount one
   spelling by refusing a leading zero before another digit, and does not name
   the sign. Default: `-0` parses to 0, as today, and the canonical form written
   back is `0`.
6. **A6 · Who writes the `fingerprint` row (F4).** Default: the kernel, per
   Amendment 1 item 19, which is the later-specific rule for this row kind, and
   the M0 receipt records the conflict with Amendment 5 item 9 rather than
   resolving it in code.
7. **A7 · `truncated`, frame `f` bit 1, against the `trunc` row's dropped
   count.** Nothing says which is authoritative.
   Default: the `trunc` row's count is authoritative and the bit is its mark;
   both are written, and a frame with the bit and no row is a defect.
8. **A8 · Which `cmake` M0 uses.** Default: the VS 2022 Community CMake
   3.31.6-msvc6 named by Kickoff Amendment 1, invoked from the developer
   environment, not the 4.3.3 on PATH.
9. **A9 · The order of work.** `NEXT.md`, dated 2026-09-08 19:33, puts FOLIO
   first and the judge-architecture measurement second, with M0 third. The
   handoff, dated the same day at 23:42, assigns M0 to this session. Default:
   the handoff, as the later dated text written for this session, and the
   question is put to the operator.
