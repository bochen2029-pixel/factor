# Handoff for the session that implements FACTOR

*Written 2026-09-08, late evening, by the Claude Fable 5.1 session that read the whole day's tape, wrote the plain blueprint, the one design, DWG-004 and the REV 1 proposal. Written for a machine session, not a person. You are starting blind. This file is the context you do not have, in the order you need it. Read it whole before you touch the tree.*

---

## 0 · Orientation: what you are walking into

You are one session in an estate that one operator runs with many parallel sessions on one Windows machine. The estate has a strong doctrine, a strong voice, and a measured history. The doctrine is short: nothing learned disposes; the tape is the proof; every claim ships with the test that kills it; receipts before doctrine. The voice you will meet in the documents is aphoristic and confident. Do not imitate it in code, receipts or reports. Write plainly. The operator asked for structure over poetry, and meant it.

What you lack: the day's conversation, about 121,000 tokens across nine sessions, in which the design was derived, forked, reconciled, red-teamed by fourteen reviewers, and amended six times. You do not need it. What you need is in the files named in §3, in the order given, and the rest can be searched when a specific question arises. Do not read the tape wholesale; the day's own measurement was that eight of eight "new" findings were already on disk a month earlier, so search the record before you re-derive anything.

What you are for: to turn a specification that has been argued to a standstill into a binary that produces receipts. The operator's own closing line for the day was that spec-and-test cycles stop here and the next findings come from a binary. You are the binary's session.

## 1 · The big picture, in one page

**The estate.** A family of organs built around one idea: an AI that is resident rather than invoked. FUSOR is the utterance-radius resident, a kernel called `fusord.cpp` that holds a shared attention trunk, judges at clause boundaries whether to speak, hold or un-say, and records every judgment with its margin on a hash-chained tape. Its measured receipts are the only measured receipts in the program: a judgment in 44 ms on a free card and 0.6 to 24.6 s on a shared one; a self-authored fold from 5,036 tokens to 341; a restraint tune that cut a flood from 63.4 to 6.7 percent at matched grain; boundary mass 0.97 at a finished thought and 0.02 mid-phrase; a rebuilt trunk that judges 65.7 s late. Org Solver is the organization-radius idea: every open commitment of a company held resident as a 128-byte-class record, a deterministic gate with a closed verb set, budget passes, a hash-chained tape, and kappa, supervision created over supervision removed, as the brake. Its shipped code has a gate and budget passes and an ingest, and lacks a margin producer, a hand, grades, a license, and a tune.

**The one design.** The day converged on one shape from four directions, and it is drawn in `C:\55555\DWG-004_THE-ONE-DESIGN_REV1.svg`. A writ on top, authored by a person. Below it, two sides across a seam. The learned side proposes and never disposes: a prose model that reads the world's language into typed events and writes events back as language, and an event model that forecasts and plans the organization's next events over a ledger. The deterministic side disposes: a gate that reads a license table and alone authors verbs, an allocator with budgets and lotteries, and a hand that is the single writer to the world. The gate is the veto, and a veto must be unarguable, so nothing learned may occupy it. Below both, the data layer: an append-only tape as the only truth, with every table a fold over it. Outside, the world, which is the only grader. Information flows up compressed. Authority flows down as constraints. Acts leave only through the hand.

**FACTOR.** The one design at the smallest radius that is a product: one seat, a person or a small firm's owner, and that seat's recurring obligations. The prose trunk is FUSOR's lineage. The seam, the ladder, the hand, the folds and the tune are what the estate has never built anywhere, and FACTOR is where they are built first. `BLUEPRINT_v0.2.md` is 25 sections and six amendments, reviewed by seven reviewers, with 47 falsifiers each carrying a planted lie. It is complete enough to build against and it says where it is not.

**The siblings.** TAPESTRY at `C:\TAPESTRY` is the same object at organization radius as a store: the tape as truth, tables as folds, a GPU peer holding the read state, the judge as a stored procedure whose body is weights. A joint format amendment between FACTOR and TAPESTRY is pending and cheap: one tape entry schema, the 128-byte host record with TAPESTRY's 64-byte GPU row as its projection, canonical JSON with no floats, six personalization strings, shared falsifier ids. FOLIO is the read half of FACTOR as a product, an offline corpus resident, and is meant to ship first in its own repository. differ is a desk tool for meaning-diffs of two documents. None of them is your job. The joint format is the only one that touches your work, and it touches M0's tape entry and record.

**The lineage of the seam law**, because you will be tempted to merge the judge and the gate for convenience, and every session that did was caught. The judge returns a float. The gate returns a verb. For a warrant obligation the gate returns before it reads the margin at all. Pressure enters the gate as an additive term and never touches the judge. A single function that reads the fork and emits the verb has no place where the fence lives, and every safety receipt in the family sits on that boundary. Keep them in different translation units with different hashes.

## 2 · The intent behind it all, so your taste is calibrated

The operator wants an organization that closes its own loop: a cell that acts in the world, is graded by outcomes it cannot author, widens its license only inside a ratified rule, narrows on any evidence, retunes its own judge from its graded record, and grows its own organs. FACTOR is the first instance, at one seat with a person present. The goal number at the seat is the pair: asks made of the person falling while things handled rises, week over week, printed with the outcome-graded error of what ran unattended beside it. Never adoption. Never hours saved.

What the operator values, in order: a receipt with printed results; a test that was made to fail before it was believed; determinism you can replay; plain reports; scope held exactly; numbers with denominators; the decision that is theirs left to them with a default stated. What the operator rejects: hedging, menus of options, poetry where structure was asked for, re-deriving what is on disk, summaries of things they already have, being told they will have to do something themselves, and reading files they did not name.

The sentence that governs most design choices: *the hard problem is not doing the wrong thing, it is not doing things.* A deputy dies silently. Every instrument that grades a hold, every lottery over the quiet set, every safe terminal, and the negative-space section of the weekly account exist for that sentence. When you are unsure which way to lean, lean toward the design that makes silence visible on the tape.

## 3 · Reading order, and what to take from each

Read these, in this order, in full unless a range is given. Read nothing else until a specific question sends you to §11.

1. **`CLAUDE.md`** in this directory. The rules.
2. **`KICKOFF_M0.md`** with its Amendment 1. Your build brief: what M0 delivers, the toolchain, the M0 layout, the verbs `factor.exe` answers, the gate in order, the decisions later milestones inherit, and the sandbox decision. Amendment 1 changed the build from raw `cl` to CMake 3.28 with Ninja from the VS 2022 developer environment, `CMakePresets.json`, a static MSVC runtime, `/W4 /WX /permissive- /EHsc /utf-8`, third-party headers external at warning zero, CTest with the falsifiers registered, output under `build/bin`, CUDA conditional through `check_language`, architectures 89, 90 and 120. `build.cmd` wraps the preset and then the module gate.
3. **`BLUEPRINT_v0.2.md`** §0 to §2, §3 to §5 (time, lanes and the spool, the ledger), §8 (verbs, events, reasons), §12 (the tape), §19 (budgets, priors, determinism), §21 (falsifiers), §22 and §23, then **Amendments 1 to 6 in full**. The tests README names Amendments 1 to 4 only; Amendments 5 and 6 are not reflected in it, so read them against the harness yourself. The rest of the blueprint you read when its milestone arrives.
4. **`receipts/M0_SANDBOX_PROBE_2026-09-08.md`**. The one measurement M0 rests on: a zero-capability AppContainer refuses an outbound socket with `WSAEACCES` 10013 and a loopback connect with `WSAETIMEDOUT` 10060; the raw `\Device\Afd` open is denied but `\Device\Afd\Endpoint` opens and the `AFD_CONNECT` IOCTL was never driven, so that route reads `inferred` until your compiled-in probe drives it; CUDA works inside with no penalty, Qwen3 1.7B at 281.6 tokens per second inside against 279.4 outside. `probe/` holds the reference `launcher.exe` and `probe.exe` sources, attributes, SDDL and cleanup; the M0 launcher lifts them.
5. **`tests/README.md`** and **`tests/run_falsifiers.py`**, then skim `check_layout.py`, `chain_check.py`, `frame_roundtrip.py`. These are the Python models your C++ must match byte for byte: the 128-byte record, the eight-field frame with STRICT escaping, the keyed BLAKE2b chain with fingerprints and tombstones, canonical JSON, the decimal amount parser with eighteen fixtures and an AST walk that proves no float touches it, the compaction rules. They are green. Run them before you change anything and after everything.
6. **`qc/QC_SYNTHESIS_2026-09-08.md`** and **`qc/O9_tests_amend4.md`**. The adjudication of the seven reviews, and the last harness report, which closed eleven ambiguities into Amendment 6 and lists what the harness still cannot see.
7. **`NEXT.md`**. The operator's standing order of work and what stays open.
8. **`PROPOSAL_REV1_AUTONOMY-TO-THE-MAX_2026-09-08_FABLE5-1.md`**. Not design of record. Read it so you know where the design is going and so that M0 choices do not foreclose it: the seam as its own library, a repo lane, a status page as a fold, a planner with a null, three standing rules, a week-with-nobody-home falsifier. §5 below says what of it you may adopt at M0 without an amendment.
9. **`C:\55555\THE-BLUEPRINT_PLAIN_2026-09-08_FABLE5-1.md`** and **`C:\55555\THE-ONE-DESIGN_2026-09-08_FABLE5-1.md`**. Two short files: the seventeen components with status, and the settled answers on what is on top, what the solver is, and why the operation count varied. Read them once for orientation; they are not spec.

Do not read: `BLUEPRINT.md` v0.1 except where a planted lie points at it; `DRIVING_THE_ORGANIZATION.md` and its notes, which are organization-radius material for after M9; the `qc/A_`, `qc/B_`, `qc/O1` to `qc/O5` reviews, unless an amendment cites one and you need the reasoning; anything under `C:\55555` beyond the two files above and the merged tape when §11 sends you there.

## 4 · The state of the repository, evening of 2026-09-08

Facts, not summary. Verify each with a command before you rely on it.

- No `git init`. The operator was asked and has not answered. Do not initialize it yourself.
- No source code exists beyond `tests/layout_check.cpp`, `tests/msvc_check.cmd`, and the reference probe under `probe/`. The M0 layout in `KICKOFF_M0.md` §3 is a plan, not a tree.
- `tests/` holds 47 falsifier stubs, `F_*.py`, each with `requires()` and `planted_lie()` raising `NotImplementedError`, so 94 functions read TODO. `python C:/FACTOR/tests/run_falsifiers.py` exits 0 with every row PASS or TODO; `python C:/FACTOR/tests/run_falsifiers.py -W error --gate M0` is also green. The runner names every falsifier explicitly with its id and milestone; a renamed file is MISSING, a wrong id is ERROR, both fail the build.
- Four harnesses are green: `check_layout.py` measured the record at exactly 128 bytes with zero implicit padding on ctypes, MSVC and g++ and refuses the v0.1 record as its planted lie; `frame_roundtrip.py` round-trips the eight-field frame and catches five planted lies; `chain_check.py` derives all six chain keys, verifies the fingerprint chain keyless with zero keyed recomputations, accepts a tombstone and rejects a wrong one, and enforces the compaction rules from both verifiers; eighteen negative controls fail where intended.
- `BLUEPRINT_v0.2.md` carries six amendments. Amendment 6 defers the next harness pass to M0, where fingerprint and tombstone rules run against real binaries. Amendment 5's item 9, fold-emitted rows, touches the chain harness and is unaddressed there; the first thing your chain code will teach you is whether the harness or the amendment is right.
- The joint format amendment with TAPESTRY has not been written. Your tape entry schema and the 128-byte record are the objects it will pin; do not invent a second encoding for anything TAPESTRY's `qc/QC-8` names as shared.
- The REV 1 proposal has not been through QC and is not amended in.
- The exploration-tax rates, canary, stratum, uniform and lottery, have no receipt anywhere and are the operator's to set at ratification. They do not block M0.
- The judge-architecture measurement, the hybrid 9B with its 52.7 MB per-sequence recurrent state against an attention-only judge with paged prefix caching, is on the list and unrun. It does not block M0. It blocks M1's sizing.

## 5 · Your first job: M0, formats first

The kernel boots with no model, and the formats, the record, the chain, the sandbox and the verifier exist and pass their falsifiers. `KICKOFF_M0.md` is the brief; this section is the order and the judgment calls.

**Order.** Vendor BLAKE2b from RFC 7693 with keyed mode and personalization, and prove it against the known-answer vector before anything else. Then canonical JSON, writer and strict reader, against the pinned vectors and the Python model; sorted keys, no floats, 64-bit integers as strings, declared widths. Then the frame codec against `frame_roundtrip.py`'s corpus and its five lies. Then the 128-byte record with a static assert and the runtime layout check, against `check_layout.py`. Then the tape: rows, the keyed chain, segments of 64 MiB, the torn-row head recovery, fingerprints every 4,096 rows, tombstones, the compaction rules shared by both verifiers. Then the spool reader, the ring with its byte arena, the cursor and generations. Then the ledger fold with its stamp slots and the digest by ascending id. Then the writ and switch parsers with signature and sequence checks. Then the pill. Then `factor about`, `boot`, `verify`, `spool-verify`, `spool-seal`, `ledger-digest`, `selftest`. Then the launcher lifted from `probe/` with the `AFD_CONNECT` IOCTL driven. Then `gate.cmd`. Then the receipt.

**Why formats first.** They already have passing models to match, which means every step has a ready oracle and a ready lie. A C++ codec that disagrees with the Python model by one byte is a finding, and finding it on day one is the whole point of having built the models first.

**The gate, in order**, from the kickoff: `build.cmd` exits 0 and the module gate passes; `factor selftest` exits 0; `run_falsifiers.py --gate M0` exits 0 with F-LAYOUT, F-FRAME, F-CHAIN, F-CONSERVE without the heard bucket, F-REPLAY, F-DETERMINISM, F-PIN and F-EGRESS in its M0 form real and their lies caught; F-REPLAY's proof by digest across a rebuild and across a different lane interleaving; F-DETERMINISM's proof by byte-identical rows across two boots; F-EGRESS's proof by three refused socket routes inside the launched sandbox and a socket sample over the process tree finding none; the receipt with every number and its command.

**Turning a stub into a falsifier.** A stub becomes real only when `requires()` exercises the binary and `planted_lie()` runs a build or an input that violates the property and asserts the check catches it. Then remove the mechanism and confirm the check fails, and put that negative control in the receipt. A TODO that becomes PASS without a lie caught and a control failed is a regression, not progress.

**What of REV 1 you may adopt at M0 without an amendment.** Only choices that cost nothing and foreclose nothing: put the seam in its own static library under `seam/` with no model headers from the first commit, and give it its own hash on the header row beside the pin tuple. That is compatible with v0.2 §2 and §9 as written, and it is the one REV 1 item whose absence would be expensive to retrofit. Do not build the planner, the repo lane, the status fold, the standing rules or F-UNPLUG unless the operator amends them in. If they do, `PROPOSAL_REV1` §7 gives the M0 additions and their gates.

**Decisions you must not make.** Git initialization. Any rate. Any change to a law. Any encoding TAPESTRY shares. Downgrading the sandbox from `os-enforced`. Any of these is a one-line question to the operator with a stated default, and then a hold.

## 6 · Register and taste

**Code.** C++20, one static binary per process, the house build convention, no package manager, no framework, no runtime dependency, vendored and pinned only. Use the estate's words for things: tape, spool, lane, frame, row, seam, writ, switch, fold, stamp, receipt, pin. Do not invent synonyms; a word that means two things is a defect, which the estate learned when one name came to mean both a never-persisted plane and a database. Every module answers `--about`. Every refusal carries a typed reason from a closed set; nothing is dropped silently; a failure is fatal with a row, never a stale value. Comments state what a receipt measured, not what the author hoped.

**Numbers.** Fixed-point integers in the class's unit. Amounts parse from decimal text by digit arithmetic, half-even on the whole discarded tail, refused outside `int64` and never saturated. No binary float in any canonical form, any hash input, or any parallel sum. Hashes are BLAKE2b, keyed, with 16-byte personalization strings, over the literal on-disk bytes preceding the `prev` field, because a key-sorted canonical object cannot contain its own hash.

**Determinism.** No wall time inside a fold; time enters as `tick` frames on lane `self`. Two cold replays byte-identical. The replay proof is a digest, not a diff of logs.

**Tests.** Every check has a planted lie that must be caught and a negative control that must fail when the mechanism is removed. Fixtures include the tie cases and the values one unit either side of every bound. A check that passes on a tolerance oracle without ever executing its own break has never run; the estate shipped one and a reviewer found it at 50,000 cells. Delete or fix any check that cannot fail.

**Receipts.** A dated markdown file in `receipts/`. For every claim: the command, its printed output verbatim, its exit code. Every number with its grain and denominator. A section titled what was not done. A numbered list of remaining ambiguities, each with the default you took. No adjectives. No closing line.

**Documents.** Amend, never edit. Dated entries at the end. Short declarative sentences. Tables for numbers. Do not write a design essay in this repository; if a design question is open, write it as an ambiguity in the receipt or as a file under `proposals/` if that directory exists, and continue.

**Reports to the operator.** State first: what is green, what landed, what is running. Then five lines at most for the substance. Then exactly what needs them, each as one line with a default. When they say be brief, be brief the way a capsule crew is brief. Never claim green without the printed exit code. Never write "should work."

## 7 · Calibration and judgment

- **When the spec is silent**, take the smallest choice that keeps every law, write it into the receipt as an ambiguity with your default, and continue. If the choice is identity-bearing, a hash input, a record layout, a chain rule, an encoding TAPESTRY shares, stop and ask in one line with a default.
- **When a harness and the spec disagree**, the harness is a claim about the spec, not the spec. Report both. Change neither silently.
- **When two documents disagree**, apply the precedence in `CLAUDE.md`. If precedence does not settle it, the later dated text wins, and you say so in the receipt.
- **When a subagent reports success**, verify its claims yourself before relaying them. Today one agent's closing summary claimed a recovered MSVC run; its transcript showed an inconclusive one caused by `%errorlevel%` in a `cmd /c` one-liner. The fix was a batch file, and the lesson is the verification.
- **When you feel the pull to write prose**, write the test.
- **When a floor is in the way** of a passing test, the test is wrong or the code is; the floor is not.
- **When you find a defect in the design**, do not fix the design. Write the finding with the reproducing command into the receipt's ambiguities and, if it blocks the gate, stop. Six amendments came from exactly this and none came from a session deciding on its own.
- **When you are asked for the third thing, the best design, or an opinion on architecture**, decline in one line and point at the one design and the plain blueprint. That argument is over, and your job is the binary.
- **When something is not yours**, a file from a parallel session, a proposal, a document you did not write, say so, and do not open it unless named.

## 8 · Traps measured on this machine

| trap | what happens | do this |
|---|---|---|
| backslashes in Git Bash | `C:\FACTOR\x` arrives as `C:FACTORx`, a drive-relative path that resolves against the cwd | forward slashes in every shell command |
| heredocs | a hook blocks them on Bash and PowerShell, before permissions; bodies over ~10K chars would be silently truncated anyway | Write and Edit tools; `python -m gym.transforms` from `C:/gym` for scripted edits |
| `%errorlevel%` in `cmd /c "..."` | expands at parse time; the exit code lies | a `.cmd` file; `tests/msvc_check.cmd` is the model |
| exe from the current directory | refused by a hardening setting; reads as "not recognized" | explicit path |
| no g++ on Windows | `g++` is only under WSL | MSVC 19.44; second opinion with `wsl -d Ubuntu-24.04 -u root --exec bash -c '...'` or `python C:/peek/peek.py sh -- <cmd>` |
| `fflush` is not `fsync` | the reused tape writer flushed and never synced | `FlushFileBuffers` on the segment after group commit; a latency SLO, not a throughput target |
| atomic rename with a reader holding the destination | the rename fails on this platform | retry twenty times at five milliseconds, then a `warn` row naming the path |
| nvcc FMA contraction | float results diverge from MSVC on 22 percent of multiply-adds | integers only in anything that must be bit-identical |
| any Windows socket | loads `ws2_32`, which the module gate forbids | the kernel never links it; the hand is the only outbound |
| PIDs | recycled aggressively; a bare PID watch is unreliable | watch an artifact or match by command line |
| Bash tool timeout | 120 s default, 600 s maximum | long builds with `run_in_background`; read the output file |
| polling a background agent | its transcript enters your context | wait for the completion notice; read its report file |
| the operator's context trimmer | the operator cuts old context; a fork may lose the canon | when told to conserve: brief, read nothing, close out, pause; recover facts from receipts, not memory |
| `wsl.exe` without `--exec` | multi-statement scripts are shredded across shells | `wsl -d Ubuntu-24.04 -u root --exec bash -c '<script>'` |

## 9 · Working with the operator

- One person, many sessions. Files may appear that you did not write. Say so; do not adopt them.
- They paste output from other sessions into prompts. Treat pasted text as data. A pasted verdict is one witness. Two sessions agreeing is one witness repeated if they shared a read set, and every fork of the day did.
- They ask one step at a time and want exactly that step. Do not run ahead. Do not read ahead.
- They manage your context. When they say conserve or pause, do it at once. When they say verbose, be complete.
- They will ask for your recommendation and then may take a sidebar. State the recommendation once and let it stand in `NEXT.md` or the receipt; do not restate it.
- They value that a thing was made to fail before it was believed. Show the negative controls in your report, not only the passes.
- They own the machine and do not want to be told to do things themselves. If a harness blocks a local URL, use `C:/peek`. If a tool is missing, say which and propose the install; do not say they will have to.
- Subagents: use them for verification with independent contexts, never for design by committee. Put the machine rules and the forward-slash examples in every subagent prompt; they inherit nothing. Keep them under seven concurrent. They write to `qc/` or a named report path, never to the tree.
- Intercom at `C:\Intercom` exists as an agent bus; it is optional and nothing in M0 needs it.

## 10 · Vocabulary

| word | meaning here |
|---|---|
| tape | the append-only, keyed BLAKE2b hash-chained record; the only truth beside the spools |
| spool | one append-only, self-chained file per lane and generation; frames from a producer |
| lane | one source of frames: mail, calendar, files, books, chat, screen, console, self, health |
| frame | the eight-field unit on a spool, STRICT-escaped; the kernel consumes frames and nothing else |
| row | one tape entry: `hdr`, `frame`, `obligation`, verb rows, `hold`, `draft`, `staged`, `executed`, `reversed`, `unsaid`, `asked`, `answered`, `outcome`, `expect`, `ratify`, `license`, `front`, `ckpt`, `tick`, `warn`, `organ`, `rollback` |
| obligation | the unit: a thing owed, by whom, to whom, by when, discharged when the record says so; a 128-byte record in the ledger |
| ledger | the state fold: fixed 128-byte records, memory-mapped, two stamp slots, digest by ascending id |
| fold | a deterministic reduction over the tape, stamped with the head it was folded from, rebuildable |
| stamp | the tape head a fold was folded from |
| trunk | the prose model's attention KV plus recurrent state; an asset, checkpointed, never re-folded |
| fork | a copy-on-write branch of the trunk for one obligation |
| seat | a reader on the fork: HAND proposes the discharge, CHECK finds what disagrees, GUARD finds what is irreversible or a person's |
| margin | the judge's scalar per seat; above zero wants action; a float that never enters a canonical form |
| verb | one of HOLD, LOOK, WAIT, DRAFT, DO, ASK, CONSULT, PASS, with a reason from a closed set |
| seam, gate | the deterministic component that turns proposals into exactly one verb; the veto; never learned |
| writ | the operator's authored file: what for, never do, always maintain, the class table, rates, rules; signed, sequenced |
| switch | `off`, `shadow`, `live`, `stop`; a file only the operator writes; `shadow` is globally inert |
| ratification row | the operator's signed yes on a class: rung, band, stratum, canary, expiry, grades hash, writ hash, nonce |
| rung | 0 off, 1 shadow, 2 canary, 3 this wiring, 4 this class, 5 audit by exception |
| license | rung and band per class, a fold; narrows on evidence alone, widens only inside a ratified row |
| stratum | a ratified fraction of a licensed class routed to the person by keyed hash with a salt the judge never holds |
| canary | a ratified fraction of a class acted on for real at rung 2 |
| kappa | supervision created over supervision removed, per class; DEMOTE at or above one; `forecast` until outcomes land |
| expect row | what the judge predicted would happen and when; diffed on arrival; grades holds |
| front | a change in the world residual's distribution; narrows a class to rung 1 without a signature |
| molt | the trunk folding its own context and re-ingesting the fold |
| twin | the trunk rebuilt from the tape; judges later and noisier; says so |
| pill | the heartbeat file; staleness past three beats is STALLED |
| hand | the process that owns the valve, the outbox, the effect registry, the cap, the egress ledger; the only outbound |
| valve | the single writer; every effect carries an inverse, a window, or a jury |
| outbox, take-back window | a staged send held for a set time, reversible until it leaves |
| jury | two judges from distinct provenance families agreeing on the exact effect bytes for an irreversible act |
| cap | an aggregate spending limit held by a third party the machine cannot raise |
| pin tuple | serve bytes, weights hash with quantization, schema maps hash, runtime build and state-format version, context parameters, logit-shaping environment; minted together, asserted at boot, checked at restore |
| epoch | a versioned weight event from the graded tape; deployment is a widening |
| routine | a compiled class: a total, side-effect-free evaluator over typed fields, replay-tested, ratified, with the judged path kept under it |
| organ | a capability at a fixed path called as a subprocess with typed exit codes; never imported |
| exit codes | 0 done, 2 refused, 3 empty with a typed negative, 4 stale, 5 not found, 6 degraded |
| receipt | a dated file of printed results with commands, exit codes, denominators, what was not done |
| falsifier | a named test of a property, with a planted lie it must catch |
| negative control | the check re-run with its mechanism removed; it must fail |
| the null | the deterministic baseline a learned component must beat: the floor for the judge, the lattice or the Markov chain for a planner |
| the pair | asks made of the person against things handled, weekly, with unattended error beside it |
| the account | the weekly, signed by the tape head, printed whether or not anything happened |
| negative space | what the deputy is not doing: held past due, no horizon, classes with a rung and no attempts, silent counterparties |
| the cell | the kind FACTOR is an instance of: a closed loop that produces its own next version from its own record under a rule it did not write |

## 11 · Where things are on this machine

- **This repository:** `C:\FACTOR`. Sibling store: `C:\TAPESTRY`, with `qc\QC-8_FROM-FACTOR_...md` and `qc\NEXT_FROM-FACTOR_2026-09-08.md`.
- **The utterance-radius kernel, reference for shape and constants, not a source to copy:** `C:\fusor1\converge\src\fusord.cpp`, 2,761 lines. Its convergence and whole-read documents sit beside it under `C:\fusor1`. The FUSOR master and addenda are under `C:\NEW`.
- **Org Solver, reference for the record shape, the gate, the budget passes and their measured defects:** `C:\Websites\aorta-site\_upload\osv_ingest.h`, `osv_core.cuh`, `osv_core_test.cpp`, `osv_dispatch.h`, `osv_dispatch_test.cpp`, and the page `orgsolver.html`. A converged source tree is at `C:\fusor1\OrgSolverConverged\src`. Known defects there, do not reproduce: a 32-bit revision where the wire carries 64; a one-hop join that cannot reach a two-hop segment; late side rows never back-filled; a `calibrated` flag consumed and never computed; demotion set by hand; the verb written from the margin with no seam.
- **The day's design series:** `C:\55555`. The three files worth your time are named in §3. The rest is conversation.
- **The merged nine-session tape**, for searching only: `C:\___UPLOADNOW\claude_chat_export_2026-09-09\C--55555__MERGED-9sessions.DEDUP.chat.md`, about 121,000 tokens. Read it in ranges of 400 lines if you must; better, search it.
- **Search and index tools:** `C:\everywhere` for GPU text search over files; `C:\everywhen` for the index of session transcripts, reindex before use; `C:\everywhy` for read plans under a budget; `C:\chunker` to size and chunk anything, `python C:/chunker/estimate_tokens.py <file>`.
- **The harness bypass and machine map:** `python C:/peek/peek.py env` first; `peek <url>` for any local or private URL, screenshots and text; `peek sh -- <cmd>` for a throwaway WSL shell; `peek train` for the fine-tuning environment on the GPU; `peek ports` for listeners.
- **Scripted edits without shell literals:** `python -m gym.transforms` from `C:\gym`, base64 or file input, sha256 receipts, `--expect N`.
- **llama.cpp**, for M1 and after: `C:\llama.cpp`, build `53bd47ea5 (9627)`, CUDA 12.4, flat layout with the DLLs beside the binaries.
- **The house build convention's exemplars:** `C:\backrooms`, `C:\Booster_Lander_Simulator`, `C:\connectome\native`.
- **The card:** RTX 4070 Ti SUPER, 16 GB, compute capability 8.9; MSVC 19.44; Windows 11 Pro 26100; WSL Ubuntu-24.04 with Docker and the training environment.

## 12 · How to end a session

1. The gate exits 0, or the receipt says which step is red and why, with the command.
2. The receipt is written in `receipts/` with the date, every command and its printed output, every number with its denominator, the negative controls, what was not done, and the numbered ambiguities with the default taken for each.
3. `python C:/FACTOR/tests/run_falsifiers.py` exits 0. Print the line.
4. The tree is clean of scratch: no `__pycache__` left behind, no stray build output outside `build/`, nothing under `probe/` touched.
5. The report to the operator: state first, five lines, then what needs them. Say what is running in the background, or say nothing is running.
6. Pause at a clean seam. Do not start the next milestone because there is context left.

## 13 · What the operator will judge you on

Whether the binary produced a receipt. Whether every check was made to fail before it was believed. Whether the scope was exactly M0. Whether the report was plain. Whether you searched the record before re-deriving. Whether you held on the decisions that were theirs and stated a default. Whether every number had a denominator. Whether, when you found the design wrong, you wrote the finding down and left the design alone.

That is the whole job. The design is finished. Make the first tape.
