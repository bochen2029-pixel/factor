# FACTOR · BLUEPRINT v0.1
### A resident deputy: the architecture, the constitution, the record, the build order

**2026-09-08 · greenfield.** This document is the design of record for FACTOR, written on a blank slate. It references ideas that exist elsewhere where they are the right ideas; it fits nothing. Every number that is not a law is a budget and says so. Register: SPEC. Where a later receipt disagrees with this file, the receipt wins and this file is amended by a dated entry, never edited in place.

---

## 0 · What FACTOR is

FACTOR is a resident agent that runs the recurring obligations of one seat, a person or a small firm's owner, end to end, within a license it earns class by class. It does not take turns. It reads the streams the seat already has, derives from them every obligation that exists, owed by the seat and owed to it, and discharges the ones it is licensed to discharge: the reply, the chaser, the booking, the reschedule, the filing, the reconciliation, the staged payment, the standard document, the promise that was made and forgotten. It asks once per kind of work, never per instance. It compiles what it does repeatedly into routines that run without a model. It records everything, holds included, on a hash-chained tape it can be rolled back along. Irreversible acts require two judges trained apart to agree and a cap the machine cannot raise. It prints one line every week: asks made of you against things handled.

A factor, in the mercantile sense, is the commissioned agent who transacts on a principal's behalf within a mandate and is answerable for every transaction. The name is the specification.

### What it refuses

- It is not a chat. A line typed into it is a percept, judged like any other. Nothing waits for it.
- It never acts without a row. A decision made by omission leaves no trace, and that is the failure the whole design exists to prevent.
- It never asks per instance. It asks per class, rarely, with a receipt.
- It never acts irreversibly on one model's word.
- Its judge never leaves the machine. Counsel may be rented. The resident may not.
- It never widens its own license. It may narrow it on evidence, and may widen it only within a rule a person ratified.
- It never runs the whole company. Its scope is one seat's recurring obligations, and it says so.
- It never drops a percept. Judgment may be delayed; the world is never edited.

---

## 1 · The constitution

Twelve laws. Each is a property the system has by construction, checked by a falsifier in §21, not a policy in a document.

1. **Resident.** One process owns the clock and the judgment. It is woken by evidence, never by a prompt, a timer, or a webhook. Sensors may poll; the judge is never clocked.
2. **The obligation is the unit.** Everything FACTOR does is the discharge of an obligation it derived from the record: a thing owed, by whom, to whom, by when, discharged when the record says so.
3. **Every verb is recorded with its margin.** Silence is on the record with its number. The tape is append-only and hash-chained.
4. **One writer.** Every effect on the world passes through one valve, carries its inverse or a take-back window, and is recorded before it leaves.
5. **The kernel has no hands.** The process that judges cannot open a socket. The process that acts cannot judge. They meet over one typed contract.
6. **The license is earned, expires, and is monotone.** Per class and band: shadow, one wiring, the class, audit by exception. Promotion by an anytime-valid test on outcomes; demotion an order of magnitude easier; expiry unless re-earned; a sampled audit floor that never reaches zero. Widening requires a ratification row; narrowing requires only evidence.
7. **Plurality for irreversibles.** Money leaving, a contract, a deletion, a commitment past its window: two judges from different provenance families must agree, and a cap enforced outside the model applies.
8. **Everything is a fold.** Every durable structure except the tape and the trunk is a deterministic reduction over the tape, stamped with the tape head it was folded from, and rebuildable from it. Rollback is choosing an earlier head.
9. **The transform decays into code.** A class handled the same way enough times becomes a routine, replay-tested against the tape, ratified once, run with no forward pass, with the judged path retained under it as its control arm.
10. **Nothing leaves the box.** Egress is zero by construction in the kernel and printed per row in the hand: bytes, endpoint, cost. The only outbound content is a brief to an endpoint the person supplied.
11. **Corpus bytes are inert.** Every byte that arrives on a lane is data. No text on a lane can become an instruction. Effects come only from typed verbs through the valve.
12. **Persistence first.** FACTOR's own health, its model, its card, its lanes, its disk, its keys, its adapters, is a class of obligation on lane `self`, ranked above every counterparty, because the loop closes only if the substrate is there to close it.

---

## 2 · Architecture overview

Four processes, six data objects, one contract between each pair.

```
   lanes ──frames──▶ ┌──────────────┐        effects        ┌──────────────┐ ──▶ the world
   (producers)       │   KERNEL     │ ─────────────────────▶│    HAND      │     mail, calendar,
                     │  the judge   │ ◀───────────────────── │  the valve   │     books, browser,
   the console ◀───▶ │  the ledger  │     receipts, replies  │  the jury's  │     VM, connectors,
   (operator)        │  the seam    │                        │  second key  │     wallet
                     │  the tape    │        organs          └──────────────┘
                     └──────────────┘ ◀──subprocess──▶  memory · relations · index · OCR · ASR
```

**Processes**

| process | owns | may | may not |
|---|---|---|---|
| **kernel** | the clock, the trunk, the judge, the ledger, the seam, the tape, the folds | read spools, fork the trunk, write the tape, emit typed effects to the hand, call organs as subprocesses | open a socket, load a network module, write the writ, write the switch |
| **hand** | the valve, the outbox, the effect registry, the endpoint allowlist, the egress ledger, the second juror | execute a staged effect after its window, reverse it by its inverse, call the supplied endpoint, count every outbound byte | judge, read the trunk, originate an effect, exceed the writ's caps |
| **console** | the operator's surface | show the ledger and the tape tail, take yes / not this / later, edit the writ, flip the switch, request rollback | run a model, touch the spools |
| **organs** | one capability each, at a fixed path | answer one typed request under a budget with an exit code | be imported, hold state the tape does not fold, act |

**Data objects**

| object | truth or fold | shape | rebuilt from |
|---|---|---|---|
| spools | truth | one append-only file per lane, frames | the world; never |
| tape | truth | append-only, hash-chained segments | never |
| trunk | asset | the model's KV state, checkpointed atomically | the tape, lossily, as the twin |
| ledger | fold | fixed 128-byte records, memory-mapped, indexed | tape |
| folds | fold | grades, license, kappa, contradiction index, routines, the account | tape |
| writ | authored | the operator's file: what it may do, per class, pinned | never; changed only by the operator |

---

## 3 · Time

Three clocks, never mixed.

- **The world's clock.** Every frame carries the venue's monotonic stamp and, where the source has one, its own revision, a log sequence number or commit counter, carried as a 64-bit integer and never truncated. Staleness is measured in revisions, never in wall time. This is the deposit clock.
- **The period.** The seam walks every open obligation the last events touched, at sub-second cadence, and every walk is a readout of the ledger, not a decision. The expensive decision, one forward pass, happens only where the walk says.
- **The horizon.** Per class and per verb, the time at which an outcome becomes knowable: the reversal window for an act, the deadline plus breach for a hold, the reply for an ask. Grades are read at the horizon, never before.

Idle time is a percept. A gap longer than the tick threshold enters the trunk as one line, lazily, before the next frame, and a restore inserts one tick for the whole absence.

---

## 4 · Lanes and the spool

A lane is a producer that turns one source into frames. Producers may poll. The kernel never does.

**Frame format**, one line, tab-separated, UTF-8, newline-free fields:

```
t_mono_ns <TAB> venue <TAB> lane <TAB> grain <TAB> rev <TAB> text
```

- `t_mono_ns`: the venue's monotonic clock, one stamping authority per venue.
- `venue`: which machine or service stamped it.
- `lane`: a typed id: `mail-<acct>`, `cal-<acct>`, `books-<org>`, `files-<root>`, `chat-<ws>`, `screen`, `shell`, `browser`, `self`, `counsel`, `console`.
- `grain`: `commit` (a completed thing), `forming` (a partial, never committed to the trunk), `tool` (a machine's output), `world` (a sensor).
- `rev`: the source's own revision, or 0.
- `text`: flattened; tabs and newlines escaped; capped by the header's declared frame cap, with the dropped count on a `trunc` row rather than a silent cut.

**Spool law.** Each lane's spool is append-only. The header line declares the contract version, the venue, the frame cap, and the spool's own chain: every frame line carries a running BLAKE3 of the previous frame's hash and its own bytes, so a spool verifies alone. The kernel's tape references frames by `(lane, offset, hash)`; a full replay re-reads spools by the tape's references and must reproduce the ledger byte-identically.

**The ring.** One single-producer single-consumer ring per lane, fixed power-of-two capacity, heap-allocated. A full ring blocks the producer; the spool on disk is the backlog. Drops are impossible by construction; stalls are counted and printed.

**The cursor.** Per lane: the end offset of the last frame the kernel ingested onto the trunk, never the offset read or pushed, with a prefix hash of the preceding bytes so a rotated or truncated spool is detected and the tail restarts loudly at zero. A crash with a full ring replays the ring on restart, visible as `replay` rows, never skipped.

**The mark.** The spool size at process start is recorded before the model loads, and the tail begins from the mark, so nothing that lands during load is skipped.

**Producers shipped with v0.** Mailbox over IMAP or Graph, read only. Calendar over CalDAV, Graph, or ICS. A watched folder tree. Books over the QuickBooks or Xero API or a dropped export. The console box. The screen, one text line per accessibility-tree change in a watched window, never a pixel, password fields having no collector at all. Lane `self`: the kernel's own committed speech and its own health.

---

## 5 · The ledger

One record per obligation, resident, memory-mapped, two cache lines. No strings in the hot record; text lives in the dossier and on the tape.

```c
struct Obligation {                   // 128 bytes, fixed, versioned by the header
  uint64_t id;            // BLAKE3-64 of (source, table, key) for structured;
                          // of the canonical claim for projected; stable across runs
  uint64_t party;         // counterparty id, stable hash; 0 = self
  uint64_t opened_ns;     // when it came into being, world clock
  uint64_t due_ns;        // 0 = no deadline
  uint64_t horizon_ns;    // when the outcome is expected to be knowable
  uint64_t blocked_by;    // id that must close first; 0 = none
  uint64_t src_rev;       // deposit clock of the last row that touched it, 64-bit
  uint64_t judged_rev;    // deposit clock at which the last margins were computed
  int64_t  amount_fix;    // fixed point, 1/65536 of the class's unit; never float
  float    m_hand, m_check, m_guard;   // the last three seat margins
  uint32_t cls;           // decision class, from the writ
  uint32_t band;          // margin band at last judgment
  uint32_t seat;          // who holds it: a worker pool, a human seat, 0 unassigned
  uint16_t flags;         // see below
  uint8_t  state;         // OPEN HELD WAITING DRAFTED STAGED DONE ASKED PASSED CLOSED
  uint8_t  verb;          // last verb
  uint8_t  reason;        // last reason
  uint8_t  gear;          // 0 code · 1 reflex · 2 fast · 3 deep · 4 human
  uint8_t  kind;          // 0 structured · 1 projected · 2 self
  uint8_t  rung;          // license rung this obligation was judged under
  uint8_t  _pad[14];
};
// flags: OWED_BY_ME OWED_TO_ME IRREVERSIBLE EXOGENOUS BLOCKED NEEDS_WORDS
//        SHADOW CANARY PINNED COMPILED JURIED DIRTY
```

**Identity.** Structured obligations hash their source coordinates. Projected obligations hash a canonical form of the claim: party, kind, the normalized statement, and the source frame's hash. Two extractions of the same promise from the same thread converge on one id; a retelling of the promise in a later thread links to it as a witness rather than opening a second obligation.

**Revision.** A row whose revision equals the record's is an idempotent replay. A lower revision is refused and counted, never merged. A full replay leaves the ledger bit-identical, proven by an order-independent digest.

**Indexes.** Primary by id. Secondary by `(cls, due_ns)` for the ripeness walk, by `party` for the counterparty view, by `state` for the open set. All rebuilt from the records on open; none persisted as truth.

**The dossier.** Per id, an append-only side store: the obligation's statement, its source frames by reference, the quotes that witnessed it, the drafts, the briefs, the jury's reasons. Keyed by id, chained into the tape by hash.

**Contribution.** An obligation contributes to the field and to the walk while OPEN, HELD, WAITING, DRAFTED, STAGED, or ASKED. CLOSED leaves at compaction. DONE is a transient between STAGED and CLOSED that lasts until the outcome horizon.

---

## 6 · The extractor

Two paths into the ledger.

**Structured.** A schema map per source, authored once, small: table, key, the predicate under which the obligation exists, the predicate under which it is discharged, the columns for deadline, amount, party, and the flags declared rather than inferred. Enrichment is a left join across side tables that works in either arrival order, and it re-fills the record when a side row arrives late. One-to-many side tables reduce by a declared rule, sum or latest, never by accident.

**Projected.** Prose becomes obligations through the model. The extractor reads each committed frame on a text lane and emits candidate obligations as typed rows: kind, party, statement, due if stated, amount if stated, and the verbatim span that witnesses it. The span is located in the frame by deterministic code; a candidate whose span does not locate is refused. Confidence is not a number the model reports; it is the count of independent witnesses, frames that project to the same id. A projected obligation with one witness is real but thin, and thinness is a reason the seam can name.

**The extraction falsifier.** A planted battery of threads with known promises, requests, and quotes must be recovered within tolerance; a shuffled battery must not; a thread with a retracted promise must close the obligation, not open a second one.

---

## 7 · The trunk and the judge

**The trunk.** One KV-resident context per seat, on the card, never re-read. The root holds the writ's summary, the seat's specifics, and the running record. Forks branch from the root per obligation when it is attended to; a fork reads the obligation's dossier and its neighbourhood, judges, and is released, or lives on while a counterparty conversation is open. Fork cost is the divergent suffix only. On a recurrent-hybrid model a fork's state cannot be rewound, so a delayed judgment is a judgment about now and the row says so.

**The judge.** One forward pass per instant, on a fork, producing three margins from three seats that share the trunk and differ only in mandate:

| seat | mandate | its margin means |
|---|---|---|
| **HAND** | do the discharge: draft, fill, compute, send | above zero, the discharge is ready |
| **CHECK** | find what on file disagrees with this | above zero, something on file contradicts it |
| **GUARD** | find what is irreversible, risky, or a person's to decide | above zero, a person or a jury should see it |

Each margin is the difference of two logits on a verbatim probe frame, read on a fork of the trunk as it stands now. The probe frame, the seat names, and the mandates are the serve bytes; their hash is pinned and asserted before the model loads, and a drifted byte refuses to boot.

**The frontier copy.** The trunk's last logits are copied at every trunk decode, and prediction error on the next frame is read from the copy, never from a fork's logits. The error is logged as the residual and gates nothing directly; it is one of the four signals the walk ranks by.

**Gears.** Reflex: the resident judge, a model in the ten to thirty billion class tuned for restraint, on the card, billing nothing. Fast: a larger local model for drafting and extraction. Deep: the supplied endpoint, for the hardest drafts, for code generation, and as the second juror. Every row prints its gear.

---

## 8 · The verbs and the reasons

One verb per open obligation per walk. Never silence.

| verb | what it does | leaves the box | needs a license |
|---|---|---|---|
| **HOLD** | nothing, written down with its margin and reason | no | no |
| **LOOK** | one priced fetch of more context, filed after the line it illuminates | no | no |
| **WAIT** | a hold with a horizon; two lines that disagree, shown; re-judged at the horizon or on change | no | no |
| **DRAFT** | produce the discharge and stage it where a person can see it; nothing sent | no | no |
| **DO** | execute the discharge through the valve | yes, through the hand | yes, per class and band |
| **ASK** | a brief to a named person, under the human budget | to the console | no |
| **CONSULT** | a brief to the supplied endpoint, cost printed, the stream never crosses | a brief only | no, under the deep budget |
| **PASS** | hand the obligation to another seat the writ names | no | no |

Events, not verbs: **UNSAID** (a forming DRAFT or DO killed at the seam because a landing frame overturned it, the aired prefix and the killed remainder both on the tape), **EXPIRED**, **GRADUATED**, **DEMOTED**, **COMPILED**, **GROWN**, **REVERSED**, **ROLLED-BACK**.

Reasons, closed set: `ok · margin · blocked · thin-evidence · uncalibrated · contradicted · irreversible · budget-human · budget-deep · capacity · jury-dissent · window-open · expired · demoted · shadow · canary`.

---

## 9 · The seam and the writ

The pass proposes; the seam disposes. Nothing learned may dispose.

**The writ** is a file only the operator writes. The kernel reads it every beat, pins its hash on the tape, and never writes it. It has a global stanza and one stanza per class:

```
[factor]
seat            = "bo"
switch          = "shadow"            # off | shadow | live, per class below may narrow, never widen
human_minutes   = 60                  # per day, the adjudication budget
deep_usd        = 2.00                # per day, the counsel budget
tick_s          = 30
takeback_min    = 10                  # default outbox window
audit_floor     = "sqrt(3/F)"         # sampled review fraction at volume F, never below 1/64
endpoints       = ["api.example.ai"]  # the only hosts the hand may reach

[class.booking-confirm]
scope           = ["mail.send"]       # effects this class may take
rung            = 2                   # 0 off · 1 shadow · 2 wiring · 3 class · 4 exception
band            = [1.0, 99]           # margin band licensed at this rung
stratum         = 0.10                # fraction still routed to the person, never 0 while rung >= 3
canary          = 0.02                # fraction acted at rung 1, reversible only
jury            = 0                   # judges required: 0 for reversible classes
expiry_days     = 30
cap_amount      = 0
horizon_days    = { do = 7, hold = 14, ask = 3 }

[class.pay-bill]
scope           = ["books.pay"]
rung            = 1
jury            = 2                   # two provenance families must agree
cap_amount      = 500.00
irreversible    = true                # a person signs unless jury_may_sign = true
```

**The gate**, per obligation, in this order, and the order is the fence:

1. `IRREVERSIBLE` and the class has no jury delegation: **ASK**. A person signs. Always.
2. `m_guard > 0`: **ASK** if the class rung is below 3; at rung 3 or above and the effect reversible, the jury decides; jury dissent: **ASK**.
3. `m_check > 0`: **WAIT**, with the two lines. Re-judged when the record changes or at the horizon.
4. `BLOCKED`: **HOLD** (blocked).
5. License for `(cls, band)` not calibrated, or thin evidence: **DRAFT** if `m_hand` clears the act threshold, else **HOLD** (uncalibrated). Drafting never needs a license because nothing leaves.
6. `m_hand ≥ θ_do`: **DO** if the rung permits it for this band, else **DRAFT** plus a shadow row stating the DO it would have taken.
7. `m_hand ≥ θ_look`: **LOOK**. Else **HOLD** (margin).
8. Budget passes over the whole set: ASKs ranked by the value of the look under the human budget, overflow **HOLD** (budget-human); CONSULTs under the deep budget, overflow **HOLD** (budget-deep); DOs under worker capacity, overflow **HOLD** (capacity). Running out of people degrades to holding, never to acting.
9. Every row written. Every wire row carries the tape row's hash.

The thresholds are in the writ, pinned. Pressure from the ledger's ripeness enters the ranking of the walk, never the gate's threshold: a loaded queue changes what is looked at first, not how much evidence an act needs.

---

## 10 · The ladder and the license

Per class and margin band. Four rungs.

| rung | it may | you see |
|---|---|---|
| 1 · shadow | nothing; it writes what it would have done | the would-have column of the account |
| 2 · this wiring | act on exactly the case approved | a row per act, each reversible |
| 3 · this class | act on cases of the same shape | a row per act and a weekly count |
| 4 · audit by exception | act without a row unless something looks wrong | a sampled fraction, never zero |

**The test.** Each `(cls, band, verb)` keeps an anytime-valid sequential test on outcome-graded correctness, an e-process, so the license can be read at any time without a multiple-comparison lie. Promotion when the evidence for correctness at or above the person's baseline crosses the ratified bar. Demotion when the evidence against crosses a bar an order of magnitude closer. Both sides of the act threshold must clear the sample floor before a band is calibrated, so a license is never granted on act-side evidence alone while hold-side error is invisible.

**Expiry.** A rung must be re-earned within its window or it drops one. Nothing is permanent because it was once approved.

**The audit floor.** At rung 4 the sampled fraction reviewed by a person falls with volume and never below the floor. The review gets cheaper, never absent.

**The monotone law**, the property that makes this a ladder and not a slope: the license reducer may narrow on evidence alone. It may widen only to a rung and band a ratification row on the tape covers, and it may never author the rule. The ratification row is the console's image of the operator's yes: class, rung, band, stratum, canary, expiry, hashed.

**The stratum.** A ratified fraction of every licensed class is still routed to the person. It keeps the calibration alive after the humans have left the class, keeps the person practiced for the residual, and is the only instrument that grades holds on the act horizon once the class is live. The kernel may raise it on evidence and may never lower it.

**The canary.** At rung 1, a ratified fraction of reversible instances is acted on inside the take-back window, so the region where the deputy disagrees with the person gets outcomes. Shadow alone grades the deputy only where it agrees with the person; the canary is how the disagreement region earns a grade.

---

## 11 · The valve and the hand

**Two processes, one contract.** The kernel emits typed effects over a local pipe. The hand executes them. The kernel's binary links no network module and refuses to start if one is present in its process; the hand is the only process with a socket, and it cannot originate an effect. The law that hazards are unreachable by construction is thereby physical: the kernel cannot send an email even if its model wanted to.

**The effect registry.** Every effect type declares one of three reversibility classes, and the valve enforces it:

| class | mechanism | examples |
|---|---|---|
| inverse-carrying | the inverse is recorded with the effect and can be applied | file move, calendar tentative, ledger row, draft |
| windowed | held in the outbox for the take-back window, reversible until it leaves | mail send, calendar confirm, message post |
| irreversible | requires the jury and the cap, or a person's signature | payment, contract, deletion, external form submit |

**The outbox.** Every windowed effect is staged with a release time. Until release it is reversible from the console, from an UNSAID at the seam, or from a jury dissent. At release the hand executes it, records the receipt, and the obligation moves to DONE until its horizon.

**The jury.** Judges are registered by provenance family: the local model's family, the supplied endpoint's family, a second local model's family. An irreversible effect requires agreement from the number of distinct families the writ names, each judge reading the same brief, the obligation, the proposed effect, the record excerpts, and returning a margin and a reason. Any dissent is an ASK. The judges' rows are on the tape with their families and hashes.

**The cap.** A per-class amount cap in the writ, and where a third-party wallet with a spending cap exists, the hand uses it as the second key: a limit the model cannot raise, enforced outside the box.

**Egress.** The hand counts every outbound byte per endpoint per row and refuses any host not in the writ's allowlist. The kernel's egress is zero, printed on the header row from the module gate.

**Idempotency.** Every effect carries the obligation id and the deposit revision it was judged at. The hand refuses an effect whose revision is older than the obligation's current revision: a stale decision cannot leave.

---

## 12 · The tape

Append-only, hash-chained, segmented, the ground of everything.

**Rows.** JSON lines. Every row: `k` (kind), `ms` (steady clock since boot), `t_mono_ns`, the row's fields, `prev`, `h`. `h = BLAKE3-256(prev ‖ body)`. Segments rotate at a size bound; a manifest lists segment heads; the chain crosses segments. The head is recovered on open from the last complete row of the last segment, walking back over a torn trailing row and warning about it. A sidecar head file is never truth.

**Kinds.** `hdr · frame · obligation · b · verb · draft · staged · executed · reversed · unsaid · asked · answered · consulted · jury · outcome · grade · license · ratify · compile · grow · ckpt · rollback · vram · tick · replay · trunc · warn · fatal · account · end`.

**References, not copies.** A `frame` row references its spool by `(lane, offset, hash)`. A replay re-reads the spools. The tape holds the deputy's judgments, its acts, and their receipts; the spools hold the world.

**Encryption at rest.** Segments encrypted with a key held on the machine; a daily fingerprint of the head published in the account so the chain can be checked from outside the box without reading it.

**The verifier.** `factor verify` walks every segment, recomputes every hash, checks every frame reference against its spool, and needs no model. It is the receipt behind every claim in the account.

---

## 13 · The folds

Each fold is a deterministic reduction over the tape, stamped with the head it was folded from, and incremental: a fold at head H plus the rows from H to H' equals the fold at H'.

| fold | reduces | produces |
|---|---|---|
| **state** | obligation, verb, staged, executed, reversed, outcome rows | the ledger and its indexes |
| **grades** | verb rows joined to outcome rows by id and revision, at per-verb horizons | correctness per `(cls, band, verb)`, both sides of the threshold |
| **license** | grades, ratify rows, expiry, the monotone law | rung and band per class; the stratum and canary rates |
| **kappa** | verb rows with their costs; the person's baseline minutes per class measured from the shadow period | supervision created per supervision removed, per class; DEMOTE above one |
| **contradiction** | obligations and their neighbourhoods | pairs that disagree, with the head that found them: a typed comparator for amounts, dates, accounts, names; an inference head for prose against prose; both orderings scored |
| **routines** | verb and executed rows per class | candidate routines where a deterministic function explains the class's discharges |
| **account** | everything since the last account | the weekly, signed by the head |

**The residual and the walk.** The walk over open obligations is ranked by four free signals: recency, where the world just changed; ripeness, where a deadline is near; residual, where the frontier copy's prediction error is high; thinness, where the license is uncalibrated and a look buys more than a verb. The ranking carries a uniform component and inverse-density weighting, pinned in the writ, so the classes watched hardest do not look most predictable for having been watched, and a no-guide stratum runs permanently so the ranking's value is measured against not ranking.

---

## 14 · The compiler and the grower

**The compiler.** When the routines fold finds a class whose discharges over the last N instances are explained by a deterministic function of the obligation's fields, template fills, arithmetic, lookups, the kernel asks the deep gear to write the function, replays it against every instance on the tape, and requires bit-identical output on the deterministic part. It then proposes the routine as a ratification with the receipt. Ratified, the routine runs in the fast path with no forward pass, and the judged path continues on the stratum as its control arm. A routine whose stratum disagrees with it is demoted the same day.

**The grower.** When a lane fails, an export format changes, or the want-ledger names a source with no adapter, the kernel treats the gap as an obligation on lane `self`, asks the deep gear to write the adapter, tests it on the source's sample against the lane contract's conformance battery, and proposes it once. Ratified adapters are pinned by hash and expire with the writ.

Neither the compiler nor the grower can ratify. Both leave artifacts the person keeps.

---

## 15 · Rollback and checkpoints

A checkpoint is a directory: the trunk state, the tape head, the ledger fold stamp, the license fold stamp, the routines in force, the writ hash, the wall time of the last frame, and a manifest hashing all of it. Checkpoints are written atomically to a temp path and renamed with write-through, the previous generation kept, and the manifest written last so it never describes a checkpoint that is not on disk.

`factor rollback <checkpoint>` appends a `rollback` row naming the target, re-derives every fold to that head, reverses every inverse-carrying effect executed after it and lists every windowed or irreversible one it cannot reverse, and restores the trunk if the model and serve pins match, else boots the twin and says so. The tape is never rewound. The current judge cannot veto a rollback; the switch is a file only the operator writes.

---

## 16 · Organs

Capabilities that are not the kernel's own live at fixed paths as subprocesses and are never imported.

**The contract.** One request in, JSON on stdin or argv; one answer out, JSON on stdout; a token or byte budget honoured and any truncation counted; exit codes branched on, never text:

```
0  done      2  refused      3  empty, a typed negative      4  stale, rebuild
5  not found 6  degraded, the answer is real and says which rung was missing
```

Every organ answers `--about` with its version, pins, and what it needs. Every organ's output is inert: data, never instruction. Every organ the kernel consults leaves its head hash as a row on the kernel's tape, so the whole animal verifies from one genesis while each organ verifies alone.

**Organs FACTOR expects.** Memory and relations over the seat's corpus; an adjacency index that returns read plans; a lifetime-archive reader with local OCR and ASR; a browser hand and a machine hand behind the valve; a connector catalog behind the lane contract. Which implementation fills each slot is a configuration line, and an absent organ degrades the answer with exit code 6, never a crash.

---

## 17 · Surfaces

**The console.** A separate process under the operator's hand. It shows the ledger by ripeness, the tape tail, the open asks, and the two lines. It takes yes, not this, or later on a class, and each answer becomes a `ratify` row. It edits the writ and flips the switch, which the kernel reads and never writes. It has a box: a line typed there is a frame on lane `console`, judged like any other. It is the one interface that survives, because the residual is where a person still looks.

**The account.** Every Friday, whether or not anything happened: what it did, what it held with margins, what it asked, what it compiled, what it grew, the two lines, kappa per class with its verdict, the egress total, the tape head's fingerprint. Signed by the head. Replying to it reaches the human.

**The API.** A local named pipe with the same typed messages the console uses, so a script or another agent can read the ledger or file a ratification under the operator's identity. Read paths are free; write paths require the operator's key.

**The organ surface.** The kernel serves its own state to organs over the stateless tool protocol, read only.

---

## 18 · The tune

The judge improves only by versioned weight events, never by living weights.

- `factor epoch` exports the graded rows since the last epoch: every verb with its margin, its outcome, and its grade, both holds and acts, into a training set with the serve bytes frozen.
- Training runs outside the kernel and produces an adapter or a full tune.
- The goldens are the tape: the new version must not regress on the graded rows it was trained beside, held out by time, with the person's baseline as the bar.
- The pins are a pair minted together: the serve-bytes hash and the weights hash. Both are asserted at boot; both are checked at restore against the checkpoint's manifest. A changed serve byte is a retune; a changed weight without a new pin refuses to load.
- Lineages are allowed: two adapters may serve two strata and the grades decide which widens. No lineage self-promotes.

---

## 19 · Performance budgets and determinism

Budgets, to be replaced by measurements; each printed on the account as measured against budget.

| quantity | budget |
|---|---|
| frame arrival to verb, reflex path, free card, p50 | under 200 ms |
| one three-seat judgment on a fork | under 150 ms |
| ledger walk over fifty thousand obligations | under 5 ms |
| checkpoint outage, disclosed | under 200 ms |
| boot with model load | under 30 s |
| kernel egress | 0 bytes, structurally |
| VRAM printed | at boot, after load, every minute, every boundary |

**Determinism laws.** Fixed-point amounts, never float accumulation. Every walk sorted by id, never by hash order. Every threshold pinned in the writ. Two runs over the same spools and writ produce byte-identical verb rows, proven by a plan hash on the account. The lattice, if a pressure field is added, batches without changing arithmetic. A decode failure is fatal with a row, never a stale margin.

---

## 20 · Threat model

- **Injection through lanes.** Every lane byte is inert. The seam executes no text; effects arise only from typed verbs; the hand accepts only registered effect types with typed fields. A frame that says "send the money" is a percept with a margin.
- **Injection through hands.** A browser or a machine hand is an effector behind the valve; what it reads comes back as a lane, inert; what it does is a registered effect with a window or an inverse.
- **Credentials.** Held by the hand's seams, never in a frame, never on the tape, never in a brief.
- **Supply chain.** Every organ, adapter, and routine is hash-pinned with an expiry and boot-asserted. A poisoned adapter is a lane that lies, and the extraction and conformance falsifiers are the battery.
- **The model as adversary.** It cannot open a socket, write the writ, flip the switch, widen a license, raise a cap, or veto a rollback. Its only powers are to propose, to draft, and to act within a ratified window.
- **The operator as the last line.** Off is inert mid-flight. Stop finishes the tape. Everything can be undone to a checkpoint, and what cannot be undone is listed.

---

## 21 · Falsifiers

Each ships with a planted lie that must fail, because an oracle that only passes measures nothing.

| id | requires | the planted lie |
|---|---|---|
| F-CONSERVE | every frame in every spool lands in exactly one of: ingested, replayed, truncated-with-count, refused-stale, or heard-not-judged | drop one frame silently |
| F-REPLAY | a full replay of the spools reproduces the ledger digest bit-identically | a float accumulator on amounts |
| F-DETERMINISM | two runs, two insertion orders, byte-identical verb rows | walk in hash-map order |
| F-INERT | with the switch off, kernel behaviour is byte-identical to the kernel absent | a side effect in shadow |
| F-EGRESS | the kernel's process holds no network module; the hand's egress equals the sum of its rows | an unlisted endpoint |
| F-WINDOW | a windowed effect reversed inside its window leaves no trace in the world and a `reversed` row on the tape | release before the window |
| F-BUDGET | two thousand asks, room for ten, the rest hold on budget and nothing acts | act because nobody was available |
| F-JURY | one dissenting family and the irreversible effect holds | a quorum of one family counted twice |
| F-MONOTONE | the license fold cannot widen a band without a covering ratification row | widen on grades alone |
| F-BOTH-SIDES | a band is not calibrated until both sides of the threshold clear the floor | license on act-side evidence only |
| F-ROLLBACK | folds re-derived to an earlier head match the folds recorded at that head | a fold that reads the future |
| F-EXTRACT | planted promises recovered; retractions close rather than duplicate | offsets emitted by the model |
| F-CONTRADICT | a planted typed disagreement caught by the comparator; a planted prose disagreement caught by the inference head; neither by the other | one head for both |
| F-COMPILE | a ratified routine replays bit-identically against the tape it was compiled from | a routine that passes on a sample |
| F-TICK | a restored trunk receives one tick for its absence; margins on the first frame match a no-restart control within noise | resume with no tick |
| F-PIN | a drifted serve byte or weight refuses to boot | a supplied identity trusted unchecked |

---

## 22 · Milestones and gates

Each milestone ends in a dated receipt and a gate that exits zero, or the milestone is not done.

- **M0 · The kernel boots.** Pins, module gate, spools, rings, cursors, the tape, the ledger, `verify`, `about`. No model. Gate: F-CONSERVE, F-REPLAY, F-DETERMINISM, F-PIN.
- **M1 · The judge.** The model loads, forks, probes; the three seats; the seam and the writ; shadow verbs on a planted spool; the switch. Gate: the planted battery; F-INERT.
- **M2 · The extractor and the first lane.** The mailbox lane; structured maps for calendar and books; projected obligations with witnesses. Gate: F-EXTRACT.
- **M3 · The hand.** Two processes; the effect registry; the outbox and the window; the egress ledger. Gate: F-WINDOW, F-EGRESS.
- **M4 · The ladder.** Grades at per-verb horizons; the sequential test; the license fold with the monotone law; the stratum and the canary; the console's ratify rows. Gate: F-MONOTONE, F-BOTH-SIDES, F-BUDGET.
- **M5 · The jury and the cap.** Provenance families; quorum; the wallet as second key. Gate: F-JURY.
- **M6 · The folds.** The contradiction index with both heads; kappa on measured baselines; the account. Gate: F-CONTRADICT.
- **M7 · The compiler, the grower, rollback.** Gate: F-COMPILE, F-ROLLBACK, F-TICK.
- **M8 · Organs and surfaces.** The organ contract; the console; the API; the organ surface. Gate: an absent organ degrades with exit code 6 and the account says which.
- **M9 · The tune.** `epoch`; goldens from the tape; the pin pair; lineages. Gate: a regressing version refuses to load.

---

## 23 · Layout

**The repository**

```
C:\FACTOR\
  BLUEPRINT.md            this file, amended by dated entries below §24
  kernel\                 the judge, the ledger, the seam, the tape, the folds; one static binary
  hand\                   the valve, the outbox, the effect registry, the jury's second key; one binary
  console\                the operator's surface; one binary
  lanes\                  producers: mail, calendar, files, books, chat, screen, shell, browser
  organs\                 adapters to organs at fixed paths; the contract and its conformance battery
  writ\                   the writ schema, examples, the validator
  tests\                  the falsifiers, each with its planted lie
  tools\                  verify, epoch, rollback, doctor, the twin
  receipts\               dated receipts per milestone
```

**A FACTOR home**

```
<home>\
  writ.toml               the operator's; hashed on every header row
  switch                  off | shadow | live; a file only the operator writes
  spools\<lane>.spool     one per lane, append-only, self-chained
  spools\<lane>.cursor    the ingested offset and its prefix hash
  tape\seg-000001.jsonl   the record, chained across segments
  tape\manifest.json      segment heads
  ledger\                 the state fold, memory-mapped, stamped
  folds\                  grades, license, kappa, contradictions, routines, stamped
  dossier\                per-obligation side store, chained
  trunk\                  checkpoints, each a directory with a manifest
  outbox\                 staged windowed effects awaiting release
  accounts\               the weekly, signed
  heartbeat.json          the pill; staleness past three beats is STALLED, fail loud
```

---

## 24 · Bets and open questions

- **[BET] The disposition transfers.** A restraint-tuned judge from another distribution will judge obligations at parity or better after the first epoch. Kill: shadow agreement in no band predicts outcome accuracy after ninety days.
- **[BET] Projected obligations are stable enough to license.** Kill: the extraction falsifier's recovery is below tolerance on real mail after the extractor's first two versions.
- **[BET] The person is a usable prior.** Kill: outcome-scored accuracy in a band does not correlate with shadow agreement in that band.
- **[BET] Compilation covers most of the mass.** Kill: fewer than half of licensed discharges in the first three wires are explained by a deterministic function after two hundred instances.
- **[OPEN] Seat count.** Three seats are proven at the utterance radius; obligations may want a fourth, a CLERK for bookkeeping discharges. Decide from the shadow tape, not in advance.
- **[OPEN] The pressure field.** A relaxation over class and time can rank the walk; it is not in v0.1 because the four free signals may suffice at one seat's scale. Add it only when the walk is measured to miss ripeness.
- **[OPEN] The hand's second juror.** Whether the endpoint juror sees the same brief as the local juror or a redacted one is a privacy decision the writ should make per class.

---

*Amendments are dated entries appended below this line. The file above is never edited in place.*

---

## Amendment 2026-09-08 · Superseded by v0.2 after the first QC

Seven reviewers read this file on the day it was written: internal consistency, canon and parallel-fork cross-reference, mathematics and systems feasibility verified against primary sources, ecosystem assumptions verified against vendor documentation, data formats checked by running code, cross-session chatter over the concordance and the bus, and an adversarial pass. Their reports are in `qc/`, the adjudication ledger is `qc/QC_SYNTHESIS_2026-09-08.md`, and the corrected design of record is `BLUEPRINT_v0.2.md`. This file stands as written so the corrections stay printed beside the claims they bought.

The load-bearing corrections, in one paragraph each. The record was 120 bytes, not 128, and margins were floats inside a digest; v0.2 pins the layout, quantizes margins, and adds the fields the seam needed. The canary was unreachable and contradicted the shadow rung and F-INERT; v0.2 gives it rung 2 and makes `shadow` globally inert. The gate licensed action on the absence of objection, asked irreversible obligations before they were ready and again every walk, never reached LOOK on thin evidence, let a blocked obligation spend human minutes, and had no terminus for escalation; v0.2 rewrites it with standing, readiness, affirmative clearance, degraded evidence, budget partitions and a safe terminal. "The kernel has no hands" was a module-list lint while the kernel spawned socketed organs; v0.2 enforces it at the process-tree boundary with a zero-capability sandbox and moves effector organs under the hand. "A file only the operator writes" was a filesystem path; v0.2 makes authority a signature with a sequence and fail-closed reads. The license test was underspecified to the point of being wrong if coded naively; v0.2 carries the one-sided betting process, the change detector for demotion, the frozen or paired baseline, horizon-ordered total grading, and the both-sides minimum. Outcomes could be the hand's own writes reflected; v0.2 requires exogenous witnesses and adds the expectation row so holds are graded without a person. Rollback re-derived the license and erased demotions; v0.2 makes narrowings survive rollback. The jury was undefined on families, could vote on what it drafted, and bound to nothing; v0.2 defines families, separates roles, binds approvals to effect bytes, and never requires the endpoint. Caps were per instance with no first-payee rule; v0.2 aggregates them and treats a new payee as irreversible. `self` merged own speech with health and could act in its own interest; v0.2 splits the lanes and forbids health from ever doing. Byte-identical logits were promised from a backend that cannot give them; v0.2 makes the decision deterministic by quantization and a tie band. The ecosystem did not behave as assumed: push is minute-grain and needs a public endpoint the kernel cannot have, most sources have no revision counter, the named wallet does not exist yet, the connector catalog has no triggers, and the deep model is an endpoint and never local; v0.2 states each as it is. Twenty-nine falsifiers were added, and a law each for allocation and identity.

What every reviewer said to keep is listed in the synthesis §4 and is unchanged in v0.2.
