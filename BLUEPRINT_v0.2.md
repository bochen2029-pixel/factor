# FACTOR · BLUEPRINT v0.2
### A resident deputy: the architecture, the constitution, the record, the build order — after the first QC

**2026-09-08 · design of record.** Supersedes v0.1 (`BLUEPRINT.md`), which stands unedited beside it with a dated amendment. Every change from v0.1 was made in response to a named finding in `qc/QC_SYNTHESIS_2026-09-08.md` and the seven reviewer files beside it. Every number that is not a law is a budget and says so, and where a measured prior exists on this machine it is printed beside the budget with its source. Register: SPEC. Where a later receipt disagrees with this file, the receipt wins and this file is amended by a dated entry, never edited in place.

---

## 0 · What FACTOR is

FACTOR is a resident agent that runs the recurring obligations of one seat, a person or a small firm's owner, end to end, within a license it earns class by class. It does not take turns. It reads the streams the seat already has, derives from them every obligation that exists, owed by the seat and owed to it, and discharges the ones it is licensed to discharge: the reply, the chaser, the booking, the reschedule, the filing, the reconciliation, the staged payment, the standard document, the promise that was made and forgotten. It asks per class for licenses and per instance only where a signature is the law. It compiles what it does repeatedly into routines that run without a model. It records everything, holds included, on a hash-chained tape it can be rolled back along without ever regaining authority it lost. Irreversible acts require two judges trained apart to agree and a cap the machine cannot raise. It prints one line every week: asks made of you against things handled.

A factor, in the mercantile sense, is the commissioned agent who transacts on a principal's behalf within a mandate and is answerable for every transaction. The name is the specification.

### What it refuses

- It is not a chat. A line typed into it is a percept, judged like any other. Nothing waits for it.
- It never acts without a row. A decision made by omission leaves no trace, and that is the failure the design exists to prevent.
- **The hard problem is not doing the wrong thing. It is not doing things.** A deputy's death is silent: missed actions, breached deadlines, opportunities never opened. Every instrument in this document that grades a hold, every lottery over the quiet set, and every safe terminal exists for that sentence.
- It never asks per instance where a class would do. It asks per class, rarely, with a receipt.
- It never acts irreversibly on one model's word, and never for a payee it has not paid before.
- Its judge never leaves the machine. Counsel may be rented. The resident may not.
- It never widens its own license. The world narrows it on evidence. Only a ratified rule widens it, and only inside that rule's own criterion.
- It never treats a byte as an instruction, and it never treats a stranger's prose as evidence that licenses an act.
- It never acts on its own behalf. Its own health opens obligations that may hold, look, draft, or ask, and may never do.
- It never runs the whole company. Its scope is one seat's recurring obligations, and it says so.
- It never drops a percept. Judgment may be delayed; the world is never edited.

### Scope is a writ decision, not an architecture decision

The same eight operations run a deputy with a person present and a headquarters with no person at all. Three parameters change owner between those two: the schema map, the ratification, and the actor on the stratum. At one seat the operator owns all three. Nothing in the architecture changes if an owner changes, and nothing below should be read as assuming otherwise.

---

## 1 · The constitution

Fourteen laws. Each is a property the system has by construction, checked by at least one falsifier in §21, not a policy in a document.

1. **Resident.** One process owns the clock and the judgment. The judge consumes frames and nothing else. Time enters as frames on lane `self`: a `tick` frame at the tick threshold, a `horizon` frame when a standing verb's horizon passes, a `health` frame from the pill. The walk is clocked; the judge is not. Sensors may poll.
2. **The obligation is the unit.** Everything FACTOR does is the discharge of an obligation it derived from the record: a thing owed, by whom, to whom, by when, discharged when the record says so.
3. **Every judgment is recorded with its margin.** One verb row per judgment; a standing verb with its margin on every open obligation at every instant; never silence. The tape is append-only and hash-chained.
4. **One writer.** Every effect passes through one valve, carries its inverse or a take-back window or a jury, and is recorded before it leaves. A failed effect leaves a row.
5. **The kernel has no hands, and neither does anything it spawns.** The process that judges cannot open a socket, enforced by the operating system at the boundary of its process tree, not by a module list. The process that acts cannot originate an effect. They meet over one typed pipe.
6. **The license is earned, expires, and is monotone.** Per class and band: shadow, canary, one wiring, the class, audit by exception. Promotion by an anytime-valid test on exogenous outcomes; demotion by a change detector at a bar an order of magnitude closer; expiry unless re-earned; an audit floor that never reaches zero. The world narrows on evidence with no signature. Only a signed ratification widens, and a ratification is a rule with an outcome criterion: widening inside the rule is written by outcomes, and only the rule needs a signature.
7. **Plurality for irreversibles.** Money leaving, a contract, a deletion, a commitment past its window, a first-time payee: two judges from different provenance families must agree on the exact effect bytes, and a cap the machine cannot raise applies in aggregate.
8. **Everything is a fold.** Every durable structure except the tape, the spools, and the trunk is a deterministic reduction over the tape, stamped with the head it was folded from, and rebuildable from it. Rollback restores state and never restores authority.
9. **The transform decays into code.** A class handled the same way enough times becomes a routine: an organ in a total, side-effect-free evaluator, replay-tested against the tape, ratified once, entering at the canary rung, with the judged path retained under it as its control arm. Compiling a class removes the forward pass, never the fence.
10. **Nothing leaves the box unmetered.** The kernel's egress is zero by construction. The hand's egress is two kinds, a licensed effect to an allowlisted host and a redacted brief to the counsel endpoint, each printed per row with bytes, host and cost. Every producer's outbound bytes are metered. Bytes that leave on a rented machine are declared unmetered on the row.
11. **Bytes are inert as code and never trusted as evidence.** No text on a lane can become an instruction. An obligation whose only witnesses are a party without standing may never take DO. Untrusted text may raise a caution margin and may never lower one.
12. **Persistence first, fenced.** FACTOR's own health is a class of obligation on lane `health`, walked first. Those obligations may hold, look, draft and ask, never do. Every effect on FACTOR's own substrate requires an operator signature. FACTOR may not acquire, provision, copy itself, create an account, obtain a credential, restart itself, resist a stop, or write anything that causes it to be run later. Priority orders the walk and never buys budget.
13. **Allocation.** Scarcity degrades to holding, never to acting. The human stratum is funded before any ask is ranked. Budgets are partitioned by class and reason so one counterparty cannot starve the rest. Escalation terminates: an obligation past due with no license and no budget takes its class's declared safe terminal rather than holding silently.
14. **Identity.** The serve bytes, the weights and their quantization, the schema maps, the runtime's build and state-format version, the context parameters, and the environment that shapes the logits are pinned as one set minted together, asserted at boot, checked at restore. A changed member is a retune.

---

## 2 · Architecture overview

```
   producers ──frames──▶ ┌──────────────┐   typed effects   ┌──────────────┐ ──▶ the world
   (pull, metered)       │   KERNEL     │ ─────────────────▶│    HAND      │     allowlisted hosts,
                         │  the judge   │ ◀───────────────── │  the valve   │     the counsel endpoint,
   console ◀──signed───▶ │  the ledger  │  receipts, heads   │  the cap     │     effector organs
   (operator key)        │  the seam    │                    └──────────────┘     (browser, machine,
                         │  the tape    │  read organs, net: none                  connector actions)
                         └──────────────┘  in the same sandbox
                                ▲
                         launcher (re-executes the kernel into the sandbox; spawns organs)
```

**Processes**

| process | owns | may | may not | network |
|---|---|---|---|---|
| **launcher** | the AppContainer profile, the process tree | re-execute the kernel into the sandbox, spawn read organs into it, spawn the hand | judge, effect | none |
| **kernel** | the clock, the trunk, the judge, the ledger, the seam, the folds, the tape's key | read spools, fork the trunk, write the tape, emit typed effects to the hand, ask read organs | open a socket, spawn a process, write the writ, write the switch | denied by the OS |
| **hand** | the valve, the outbox, the effect registry, the endpoint allowlist, the egress ledger, the cap credential, effector organs, the head counter-signature key | execute a staged effect after its window, reverse by inverse, reach allowlisted hosts and the counsel endpoint, count every outbound byte | judge, originate an effect, read the trunk, hold a full-permission cap key | the only outbound |
| **console** | the operator's surface and the operator key's use | show the ledger and the tape tail, take answers and ratifications, edit the writ, flip the switch, request rollback, sign console frames | run a model, read a spool, write any spool but `console` | none |
| **producers** | one lane each | pull from a source, append frames, hold broker-issued credentials | judge, effect, append to any other lane | outbound, metered |
| **organs** | one capability each at a fixed path | answer one typed request under a budget with an exit code | be imported, act, hold state the tape does not fold, ask for a forward pass | read organs none; effector organs via the hand |
| **tools** | verify, epoch, rollback, doctor, twin, spool-seal | read everything, write receipts | effect | none except epoch's training export |

**Data objects**

| object | truth or fold | shape | rebuilt from |
|---|---|---|---|
| spools | truth | one append-only, self-chained file per lane and generation | the world; never |
| tape | truth | append-only, keyed hash chain, segmented | never |
| trunk | asset | attention KV plus recurrent state, checkpointed atomically | the tape, lossily, as the twin |
| ledger | fold | fixed 128-byte records, memory-mapped, stamped | tape |
| folds | fold | grades, license, kappa, fronts, contradictions, routines, wants, the account | tape |
| writ, switch | authored, signed | the operator's files with detached signatures and a sequence | never; changed only by the operator |

---

## 3 · Time

Four clocks, never mixed, and every field says which one it carries.

| clock | carried by | epoch | comparable across venues | survives a venue reboot |
|---|---|---|---|---|
| the deposit clock | `rev` on a frame; `src_rev`, `judged_rev` on a record | the source's own counter, or a synthetic monotone counter minted per lane at append | no, and never compared across lanes | yes, by construction |
| the venue's monotonic clock | `t_mono_ns` on a frame | per venue boot | no | no; a header row records the boot |
| wall time | `opened_ns`, `due_ns`, `horizon_ns`, `release_ns`; `t_wall_ns` on `tick` and `hdr` rows | Unix epoch | yes | yes |
| the period | the walk | none | n/a | n/a |

The seam's `now` is the last wall stamp on the tape, never the system clock, so a replay has the same `now` the run had. Wall time enters only as a percept. Staleness of a record is measured in revisions. A source with no revision counter gets a synthetic one at the lane; the refuse-lower rule applies only to a source's own counter and never to an opaque token.

**Lag is a lane property with a number.** Every lane's header declares its world-to-frame lag as measured, and the account prints it. Every latency budget in §19 starts at frame arrival because the other half is the lane's, not the kernel's.

The horizon per class and verb is when an outcome becomes knowable: the reversal window for DO, the deadline plus breach detection for HOLD, the answer for ASK, the counterparty's reply for a chaser. Grades are read at the horizon, never before.

Idle time is a percept: one `tick` frame per gap above the tick threshold, lazily, before the next frame; one tick for the whole absence on restore.

---

## 4 · Lanes and the spool

A lane is a producer that turns one source into frames. Producers pull. The kernel never does.

**Frame format**, one line, seven tab-separated fields, UTF-8:

```
t_mono_ns <TAB> venue <TAB> lane <TAB> grain <TAB> rev <TAB> text <TAB> h
```

- `rev`: the source's own counter, or the lane's synthetic counter. A frame that carries a synthetic counter says so in the header.
- `grain`: `commit`, `forming`, `tool`, `world`. An unknown grain, or a lane id outside the declared pattern, is a refused frame with a row, never a default.
- `text`: escaped as below and capped at the header's frame cap, the cap applied to the encoded field; truncation cuts the source on a code-point boundary and the `trunc` row carries the dropped count.
- `h`: the line's chain hash, `BLAKE2b-256(prev_hex ‖ u64le(len) ‖ fields 1–6 as escaped bytes with their tabs)`, unkeyed so a spool verifies alone, with the genesis `prev` the header line's `h`.

**Escaping**, every field, the backslash first, the decoder strict:

```
\  -> \\      TAB -> \t      LF -> \n      CR -> \r
every other C0 control and U+007F  -> \xNN
U+0085, U+2028, U+2029             -> \uNNNN
a byte sequence that is not valid UTF-8 -> \xNN per byte, and the frame carries a badenc mark
```

A backslash before anything but `t n r \ x u` is a refused frame. Invalid UTF-8 is escaped, never replaced, because replacement is an edit of the world.

**The header line** is a canonical JSON object `{contract, venue, lane, frame_cap, hash, esc, rev_kind, lag_ms, generation}` followed by a tab and its own chain hash over a genesis `prev` of 64 zeros. It is the chain's genesis and it counts in every offset. A header outside the chain is a header an adapter can rewrite silently.

**Spool law.** A spool never rotates on its own and never shrinks. A spool that shrinks, or whose bytes before the cursor no longer hash to the cursor's chain value, is `fatal` for that lane: the tail stops, the lane opens a `health` obligation, and the operator restores it. A spool is sealed into a new generation only by `factor spool-seal`, operator-signed, which records the old head in the lane's manifest and starts the next generation with that head as its genesis `prev`. Every tape reference to a frame is `(lane, generation, offset, h)`.

**The ring.** One single-producer single-consumer ring of frames per lane, fixed power-of-two slot count with a separate byte arena, heap-allocated. A full ring blocks the tailer; the spool is the backlog; drops are impossible. A crash replays the spool from the cursor, visible as `replay` rows.

**The cursor.** Per lane: the end offset of the last frame the kernel ingested onto the trunk, the chain value `h` of that frame, and the byte length of the window hashed, so a rotated or truncated spool is detected by reading one line. Never the offset read or pushed.

**The mark.** The spool size at process start is recorded before the model loads, and the tail begins from the mark.

**Producer laws**, the lane contract's four verbatim: file-only or socket-only, never both; never blocks the venue; never appends to any session or any other lane; inert when the switch reads `off`. Plus two of FACTOR's: credentials are issued by the seam broker, scoped and short-lived, never embedded in producer code; every producer's outbound bytes are counted on the egress ledger.

**The conformance battery**, the lane contract's five verbatim: monotonic clocks, torn-last-line tolerance, inert-off, replay determinism with two cold tails byte-identical, header handshake. A lane without a green run streams with its receipts quarantined and its obligations at rung 1.

**Producers shipped with v0, as the sources actually behave:**

| lane | mechanism | lag, declared | revision |
|---|---|---|---|
| `mail-<acct>`, the person's mailbox, read only | IMAP IDLE with CONDSTORE required, one connection per folder, re-issued every 25 minutes; Gmail through a Pub/Sub pull subscription with `history.list` as the truth; Graph through Azure Event Hubs with delta queries as the truth | seconds for IDLE, up to three minutes for Graph, push as an accelerator only | `MODSEQ` or `historyId`; synthetic for Graph |
| `mail-factor`, FACTOR's own address | an agent inbox provisioned as an object, so a chaser's reply lands as a frame | provider's | synthetic |
| `cal-<acct>` | CalDAV sync-token poll at 30 to 60 s; Google `events.list` with `syncToken`; Graph through Event Hubs | poll floor | synthetic |
| `books-<org>` | QuickBooks Change Data Capture sweep at 60 s with webhooks as a hint; Xero webhooks for the six event categories and 60 s polling for payments and bank transactions | 60 s | synthetic |
| `files-<root>` | a watched folder tree | seconds | synthetic |
| `chat-<ws>` | the workspace's read API | provider's | provider's cursor |
| `screen` | one text line per accessibility-tree change in a watched window; a collector that would emit a credential emits `<redacted:field>` and a count | sub-second | synthetic |
| `console` | the operator's box; every frame signed with the operator key over its bytes and the preceding chain hash; an unsigned frame lands on `console-unsigned` with no standing | none | synthetic |
| `self` | the kernel's own committed lines re-entering: heard, never judged | none | synthetic |
| `health` | the pill's telemetry: card, disk, keys, adapters, lanes, subscriptions, credential expiry | none | synthetic |

Credential and subscription lifetimes are `health` obligations with hard dates: Gmail watches at seven days, Graph subscriptions at seven days or one with resource data, Google refresh tokens under a Testing consent screen at seven days, Xero webhook disablement after twenty-four hours of failed delivery, the SMTP basic-auth removal in 2026. The Google app is registered as Internal to the seat's Workspace so verification and the seven-day clock do not apply.

---

## 5 · The ledger

One record per obligation, resident, memory-mapped, 128 bytes exactly, little-endian, explicit pad, every enum pinned.

```c
struct Obligation {                       // 128 bytes; asserted at compile time; no implicit padding
  uint64_t id;            //   0  BLAKE2b-64 of (source, table, key) for structured;
                          //      of the canonical claim for derived; stable across runs
  uint64_t party;         //   8  counterparty id, stable hash; 0 = self
  uint64_t opened_ns;     //  16  wall
  uint64_t due_ns;        //  24  wall; 0 = no deadline
  uint64_t horizon_ns;    //  32  wall; the horizon of the standing verb
  uint64_t blocked_by;    //  40  id that must close first; 0 = none; binding only from a structured source
  uint64_t src_rev;       //  48  deposit clock of the last row that touched it, 64-bit
  uint64_t judged_rev;    //  56  deposit clock at which the standing margins were computed
  uint64_t release_ns;    //  64  wall; outbox release or ask deadline of the standing verb
  int64_t  amount_fix;    //  72  1/65536 of `unit`; never float
  uint32_t seq;           //  80  seqlock: odd while being written
  int16_t  m_hand;        //  84  1/1024 logit, quantized; the readiness margin
  int16_t  m_check;       //  86  the contradiction margin
  int16_t  m_guard;       //  88  the hazard margin
  uint16_t n_wit;         //  90  independent witnesses, per provenance root
  uint16_t n_wait;        //  92  consecutive WAITs at one revision
  uint16_t tie;           //  94  times a margin landed inside the tie band
  uint32_t cls;           //  96  decision class, interned by the writ's class table
  uint32_t band;          // 100  margin band index at the standing judgment
  uint32_t seat;          // 104  who holds it: a worker pool, a human seat, 0 unassigned
  uint32_t unit;          // 108  ISO 4217 numeric for money; an interned code otherwise
  uint16_t flags;         // 112
  uint8_t  state;         // 114
  uint8_t  verb;          // 115
  uint8_t  reason;        // 116
  uint8_t  gear;          // 117
  uint8_t  kind;          // 118
  uint8_t  rung;          // 119  the rung the standing judgment ran under
  uint8_t  _pad[8];       // 120  zeroed on every write
};
static_assert(sizeof(Obligation) == 128 && alignof(Obligation) == 8);
```

**Pinned encodings.** `state`: 0 OPEN · 1 HELD · 2 WAITING · 3 DRAFTED · 4 STAGED · 5 DONE · 6 ASKED · 7 PASSED · 8 CLOSED. `verb`: 0 HOLD · 1 LOOK · 2 FETCH · 3 WAIT · 4 DRAFT · 5 DO · 6 ASK · 7 CONSULT · 8 PASS. `gear`: 0 code · 1 reflex · 2 fast · 3 deep · 4 human. `kind`: 0 structured · 1 derived · 2 health. `reason`: numbered in §8. `flags` bits: 0 OWED_BY_ME · 1 OWED_TO_ME · 2 IRREVERSIBLE · 3 EXOGENOUS · 4 BLOCKED · 5 NEEDS_WORDS · 6 SHADOW · 7 CANARY · 8 PINNED · 9 COMPILED · 10 JURIED · 11 UNTRUSTED_ORIGIN · 12 DEGRADED · 13–15 reserved and zero. Their meanings: IRREVERSIBLE is derived from the class's scope against the effect registry, never authored; EXOGENOUS means waiting on a counterparty nobody here controls, so the obligation is never driven forward by expectation and its ripeness uses `due_ns` alone; PINNED means ingest is authoritative and the solver may not move its fields; NEEDS_WORDS means the discharge requires prose and DRAFT precedes DO; UNTRUSTED_ORIGIN is set by the extractor when no witness has standing; DEGRADED is set by the seam when an organ the judgment depended on answered anything but zero.

The ledger header pins the byte order, the record size, and every encoding above; a ledger whose header disagrees with the running build is refused, never converted. Margins are written canonically: no NaN, and a NaN from the judge is `fatal`.

**Identity.** Structured obligations hash their source coordinates. Derived obligations hash the canonical claim only: party, kind, due and amount as fixed point, and the statement normalized by pinned deterministic code; the witnessing frame's reference goes to the dossier as a witness and never into the id, so a retelling adds a witness rather than a second obligation. Where a statement cannot be canonicalized deterministically, the extractor emits typed fields only and the statement is stored, not hashed. Id 0 is reserved. A second distinct preimage hashing to a live id is a `fatal` row, never a merge; at a million obligations the birthday probability is about three in a hundred million, and it must be loud rather than invisible.

**Revision.** Compared only between rows of the same source and table. A row whose revision equals the record's is an idempotent replay; a lower revision is refused and counted. Side tables carry their own counters and are applied whenever newer than the last side row of the same table in the dossier. A full replay leaves the ledger bit-identical, proven by the chain hash of every record taken in ascending id order.

**Indexes.** Primary by id; by `(cls, due_ns)` for ripeness; by `party`; by `state`. Rebuilt on open; none persisted as truth.

**The dossier.** Per id, an append-only side store: the statement, the source frames by reference, the witnesses and their provenance roots, the drafts, the briefs as sent, the jury's reasons, the expectation. Each entry encrypted under a per-party, per-period subkey; retention declared per lane and party in the writ; erasure destroys the subkey and writes an `erasure` row, and the chain, computed over ciphertext for the dossier, continues to verify.

**Contribution and the state machine.** OPEN, HELD, WAITING, DRAFTED, STAGED, ASKED and PASSED contribute to the walk. Transitions: STAGED on release becomes DONE; STAGED on reversal, un-say or jury dissent returns to OPEN; DONE at its horizon becomes CLOSED on a good outcome or returns to OPEN on a reversal or a false discharge; ASKED on `sign` becomes STAGED or DONE, on `decline` becomes HELD, on `later` becomes WAITING with the answer's horizon, on its ask horizon returns to OPEN with reason `expired`; PASSED contributes until the receiving seat's first row and returns to OPEN at its due; CLOSED reopens if the discharge predicate is false again at a higher revision. A rung loss re-stamps no record; a STAGED effect from a rung now below its band is un-said by the seam at the next walk.

**The record and its readers.** The console reads the map while the kernel writes it. The writer makes `seq` odd, mutates, makes it even; a reader retries while it is odd or changed. Nothing on the map is 128-byte atomic and the design does not pretend otherwise.

**Durability without a journal.** The tape is the write-ahead log. The ledger file is a 4096-byte header holding two checksummed stamp slots, then the record array. A stamp is a monotone generation, the tape head the map was folded from, the record count, and a checksum. A commit writes the records, calls `FlushViewOfFile` and then `FlushFileBuffers`, because the first alone is not a barrier, then writes the stamp into the older slot and flushes again. On open the higher checksummed stamp is the truth; if neither checksums or the stamped head is behind the tape, the ledger re-folds forward from the stamped head and writes a `replay` row. That is the normal path after an unclean exit, and it holds without assuming sector writes are atomic. Growth is a map and unmap cycle with the stamp's count as the authority; nothing keys off the file's modification time.

---

## 6 · The extractor

Two paths into the ledger.

**Structured.** A schema map per source, authored once, pinned by hash, small: table, key, the predicate under which the obligation exists, the predicate under which it is discharged, the columns for deadline, amount, unit and party, the flags declared rather than inferred, and the enrichment side tables with their keys and their one-to-many rule, sum or latest, declared. Enrichment is a left join that works in either arrival order and re-fills the record when a side row arrives late. Every unmapped table, unrecognized column and unlocated span is counted and named on the account; an ingest that is quiet about what it did not understand stops covering half the business without telling anyone. The 64-bit revision, the back-fill on late side rows and the declared one-to-many rule are deliberate corrections to measured defects in the shipped Org Solver ingest and must not be simplified away.

**Derived.** Prose becomes obligations through the model, on a compiled lane in Addendum Q's sense: text to typed rows, inheriting the prediction channel. The extractor reads each committed frame on a text lane and emits candidates as typed rows: kind, party, statement, due if stated, amount and unit if stated, and the verbatim span that witnesses it. The span is located in the frame by deterministic code; a candidate whose span does not locate is refused. The model never emits an offset.

**Witnesses and standing.** Confidence is the count of independent witnesses, and independence is per provenance root: all frames authored by one party, in one thread, on one lane, or derived from one another by quotation or forwarding count as one witness forever. A derived obligation reaches two witnesses only through a second root: a structured lane, a different authenticated party, or an operator confirmation. A party has standing when it appears on a structured lane, when the seat has previously written to it, or when an operator row names it. An obligation whose every witness lacks standing carries UNTRUSTED_ORIGIN and its licensed verbs are HOLD, LOOK, DRAFT and ASK at every rung. A percept from a party without standing may add evidence and may never retire a contradiction or a WAIT.

**Blocking.** A derived obligation may assert a dependency and it is advisory: it ranks the walk and never gates a verb. Only a structured source or an operator row creates a binding block.

**The transport rule.** The model never reads a value in order to retype it. Amounts, dates, accounts and identifiers move through code and typed fields; only judgment moves through the model, and judgment is compiled into code the moment it is stable.

**The extraction falsifier.** A planted battery of threads with known promises, requests and quotes must be recovered at recall at least 0.9 and precision at least 0.95; a shuffled battery must not; a retracted promise must close the obligation, not open a second; a forwarded quote of the same message must not count as a second witness. The measured prior from the family: 87.2 percent of verbatim quotes locate; a version below it prints `below prior`.

---

## 7 · The trunk and the judge

**The trunk.** One resident context per seat, on the card, never re-read: the model's held state, attention KV plus recurrent state on a hybrid model, checkpointed atomically. The root holds the writ's summary, the seat's specifics, and the running record. Forks branch from the root per obligation when it is attended to; a fork reads the obligation's dossier, its precedents, and the contradiction fold's candidate pairs, judges, and is released, or lives on while a counterparty conversation is open.

A fork is a sequence copy, and its cost is the divergent suffix only because the context runs with `kv_unified = true`, asserted at boot; a cross-stream copy is a full buffer copy and is refused. On a recurrent model a fork aliases the state until it decodes, so a fork judged and released without a decode costs nothing and the VRAM cost is deferred, not absent.

**Rewind is bounded, not absent.** A partial sequence removal on a recurrent or hybrid model succeeds only within the snapshot depth `n_rs_seq` the writ pays for and only when no rewind is pending; otherwise it returns false with nothing mutated. A delayed judgment beyond the depth is a judgment about now, and the row says so with `at`, the revision the instant closed at, `now`, the revision judged at, `late`, and `covers`, the instants folded into one judgment. The design rule follows: defer as little as possible.

**The molt.** The root's running record is bounded by a watermark of `n_ctx − 2048`. At the watermark the scribe seat, at its pinned temperature, authors a fold of the oldest band; the fold is a `molt` row carrying the hash and token count of the span it replaces; forks in flight are released first; the span is evicted regionally and the fold re-ingested. Nothing is re-read from a spool. A trunk rebuilt from the tape is the twin and is labelled so. F-MOLT plants a fact in the oldest band that must survive the fold at the family's measured ratio or the account prints `lossy`.

**The placement law.** Own lines commit to the trunk only after the world line open when they formed has closed. A LOOK's result files after the line it illuminates. A splice is `fatal`.

**The flush law on text lanes.** An instant closes at the segmenter set, `.` `!` `?` newline and end-of-generation, at 24 tokens, or at 1500 ms since the first unjudged token, whichever first; under backlog the caps coarsen by a pinned factor and the row says `coarsened`. The segmenter set and caps are serve bytes. A settle pass returns to the main loop after at most eight folded windows so the switch, the pill, the cursor and the checkpoint gate run.

**The un-say.** A forming DRAFT or DO killed at the seam writes an `unsaid` row with `aired`, `killed`, the cause among `margin_flipped`, `settled_by_world`, `window_closed`, `jury_dissent`, and the margin before and after. When anything was aired, the trunk commit is the prefix followed by the interruption marker, never the bare prefix, because the family measured a bare prefix priming the next seat to adopt the line. The marker carries its kill condition as a bet.

**The judge.** Three seats on one trunk. In M1 they are v11's SPEAKER, SKEPTIC and SENTINEL, byte-identical, with the probe frame, the cue frame and the pin unchanged, mapped to three roles outside the serve bytes:

| role | seat in v11 | its margin means |
|---|---|---|
| **hand** | SPEAKER | above zero, the discharge is ready |
| **check** | SKEPTIC | above zero, something on file contradicts it |
| **guard** | SENTINEL | above zero, a person or a jury should see it |

HAND · CHECK · GUARD as mandates in their own words enter only with the first epoch's tune and its new pin. Each margin is the difference of two logits on a verbatim probe frame, read on a fork of the trunk as it stands now, the three probe frames batched in one pass of fixed shape pinned beside the serve bytes. The margin is quantized to `int16` in 1/1024 logit before it touches the gate, and only the quantized value is written.

**The monotone-percept law.** The check and guard seats are read twice when the full read is at or below zero and the counterparty authored any frame in the dossier: once on the dossier as it stands and once with every frame authored by the obligation's counterparty removed. The gate uses the maximum of the two. Untrusted text may raise a caution margin and may never lower one.

**Precedent.** The class's recent graded rows re-enter the fork's context as lane `precedent`, so the judge conditions on what was decided and how it turned out between tunes. Precedent is context, not license.

**The frontier copy.** The trunk's last logits are copied at every trunk decode; prediction error on the next frame is read from the copy and logged as the frame residual. It gates nothing and ranks nothing.

**Two permanent nulls.** The floor: a deterministic judge over the typed fields, due, blocked, amount, party, age, emitting the same verbs with margin ±1, graded by the same outcome rows and printed beside the model per class, band and verb; a class is licensed to the model only where the model beats the floor on both sides, else the class is compiled to the floor. The twin: the same weights and serve bytes asked only at the walk's poll points, paired judgment by judgment; the account prints the paired difference. Both run in shadow on every class forever.

**Gears and the card.** Reflex: the resident judge, on a 16 GB card an 8 to 14B model at four bits, billing nothing. Fast: the same weights at a different sampling budget on a small card, a larger local model only where VRAM allows. Deep: the supplied endpoint, for the hardest drafts, for code generation, and as an optional juror; Kimi K3 at 2.8T parameters is an endpoint and never a local tier. A VRAM budget in the writ covers weights plus the trunk's KV at its watermark plus fork headroom, and a boot whose free VRAM after load is below it refuses rather than prints. Every row prints its gear.

---

## 8 · The verbs, the events, the reasons

Nine verbs. One verb row per judgment, and a standing verb with its margin on every open obligation at every instant.

| verb | what it does | leaves the box | needs a license |
|---|---|---|---|
| **HOLD** | nothing, written with its margin and reason | no | no |
| **LOOK** | one read of local corpus or a read organ under a token budget, filed after the line it illuminates; the `look` row carries the plan hash, the stop rule, the dropped count | no | no |
| **FETCH** | one network read through the hand: licensed per class, allowlisted, counted, recorded with the full URL and byte count; a target is a typed field or a ratified domain, never a URL from counterparty prose | yes | yes |
| **WAIT** | a hold with a horizon; two lines that disagree, shown; re-judged on change or at the horizon; `n_wait` counted | no | no |
| **DRAFT** | produce the discharge and stage it where the person can see it; nothing sent | no | no |
| **DO** | execute the discharge through the valve | yes | yes, per class and band |
| **ASK** | a brief to a named person, under the human budget | to the console | no |
| **CONSULT** | a redacted brief to the supplied endpoint, a disclosing effect, cost and bytes printed | a brief only | under the deep and disclosure budgets |
| **PASS** | hand the obligation to a seat the writ names; a pass to a human seat costs that seat's minutes | no | no |

"Leaves the box" means reaches a counterparty or a host the seat does not own. A draft in the seat's own drafts folder is an inverse-carrying effect through the hand and does not leave.

**Grain.** A verb row is written per judgment: a forward pass, a routine run, or a budget pass that changes the verb. The walk writes nothing. An obligation is re-judged only when a world row touches it, its blocker closes, its horizon arrives, a ratify or front row covers its class, or a lottery selects it. A second judgment at the same revision and horizon is a `repeat` row with no forward pass. A DRAFT is regenerated only when the revision advances and supersedes the previous draft. An ASK is issued once per obligation and question hash until answered or expired. Never-silence means no open obligation has `src_rev` newer than `judged_rev` for longer than the tick threshold without a `hold(capacity)` row.

**The expectation.** Every verb row for a class with an expectable outcome carries `expect: {what, by_ns}`. The `expect` fold diffs arrivals against it; a miss raises the obligation's world residual and grades the hold at the miss. It is the hold-side grade that needs no person.

**Events**, row kinds, not verbs: `unsaid`, `expired`, `lapsed`, `graduated`, `demoted`, `compiled`, `grown`, `reversed`, `rollback`, `front`, `terminal`.

**Reasons**, closed and numbered: 0 `ok` · 1 `margin` · 2 `blocked` · 3 `thin-evidence` · 4 `uncalibrated` · 5 `contradicted` · 6 `irreversible` · 7 `budget-human` · 8 `budget-deep` · 9 `budget-self` · 10 `capacity` · 11 `jury-dissent` · 12 `window-open` · 13 `expired` · 14 `demoted` · 15 `shadow` · 16 `canary` · 17 `degraded` · 18 `out-of-domain` · 19 `unstanding` · 20 `jury-stale` · 21 `presence` · 22 `tie` · 23 `repeat` · 24 `terminal` · 25 `front` · 26 `cap`. The Org Solver strings are kept where they overlap so its falsifier scripts port.

---

## 9 · The seam and the writ

The pass proposes; the seam disposes. Nothing learned may dispose.

**The writ** is signed, sequenced, and never written by the kernel. It contains no expressions; every schedule is chosen from a closed set by name. A writ missing any pinned key refuses to load. Class names are interned into a table inside the writ, so a `cls` value is stable across edits.

```
[factor]
seat              = "bo"
switch_default    = "off"
human_minutes     = { total = 60, irreversible = 15, priority = 15, unstanding = 5 }   # per day, partitioned
deep_usd          = 2.00               # per day
disclose_bytes    = 200000             # per day, every disclosing effect
fixed_costs       = [ { name = "agent-inbox", usd_month = 10 } ]
takeback_min      = 10                 # the floor of every windowed effect
burst_release     = 5                  # effects per minute after a presence gap
audit_floor       = "sqrt3"            # the named schedule: max(sqrt(3/F), 1/64)
endpoints         = ["api.example.ai"] # the only hosts the hand may reach
counsel           = { family = "k3-endpoint", redact = "standard" }
account_to        = "bo@seat.example"  # changing this is a writ edit
tick_s            = 30
self_share        = 0.10               # health's cap on every budget
vram_budget_mib   = 9000

[walk]
uniform           = 0.05               # every walk draws this fraction uniformly over open obligations
lottery           = 0.02               # the dark-matter quota over obligations with no signal
no_guide          = 0.05               # the control stratum where ranking is not used
salt              = "<32 hex>"         # the lottery salt; read by the kernel, never in the trunk
inv_density       = true

[thresholds]
do = 1.0   look = 0.2   consult = 0.5   tie = 0.002

[test]
alpha_up = 0.01   alpha_dn = 0.10   n0 = 30   delta = 0.05   c_trunc = 0.5

[class.booking-confirm]
scope           = ["mail.send"]
bands           = [-inf, 0.0, 1.0, 3.0, inf]      # on m_hand, quantized
rung            = { b2 = 3, b3 = 4 }              # rung per band; unlisted bands are rung 1
stratum         = 0.10                            # a floor; the fold may raise it, never lower it
canary          = 0.02                            # rung 2 only, reversible effects only
guard_jury      = 0                               # 0 means no delegation, never a jury of none
jury            = 0
jury_may_sign   = false
cap             = { amount = 0, period_day = 0, party_day = 0, unit = "USD" }
expiry_days     = 30
horizon_days    = { do = 7, hold = 14, ask = 3, wait = 2 }
wit_floor       = 2
pass_to         = ""
safe_terminal   = "ack-and-defer"                 # the declared terminal at due with no license and no budget
brief_fields    = ["party", "due", "amount", "statement_spans"]
sensitive       = false
presence_gated  = false

[class.pay-bill]
scope           = ["books.pay"]
bands           = [-inf, 0.0, 2.0, inf]
rung            = { b2 = 1 }
jury            = 2                               # two provenance families; the endpoint never required
jury_may_sign   = false                           # a person signs
cap             = { amount = 500.00, period_day = 1500.00, party_day = 500.00, unit = "USD" }
irreversible    = true
presence_gated  = true
```

**The signature.** `writ.toml` and `switch` carry detached signatures from an operator key held in a user-presence-gated keystore; each carries a monotonic `seq`; the kernel refuses any writ or switch below the highest sequence pinned on the tape. Fail-closed: an unverifiable writ reads as rung 0 in every class; an unverifiable switch reads as `off`. Narrowing works unsigned; widening never does. The console is the only process that requests a signature, per edit, showing the diff.

**The gate**, per obligation the walk selected, in this order, and the order is the fence:

0. **Standing.** UNTRUSTED_ORIGIN: the licensed verbs are HOLD, LOOK, DRAFT, ASK; reason `unstanding` where a DO would have followed.
1. **Readiness and re-entry.** An obligation whose standing verb is ASKED, WAITING, or STAGED with an open window is not re-gated until its revision advances past `judged_rev` or the standing verb's horizon passes. A second ASK at one revision is refused and counted. Steps 3 and 4 route a proposed discharge and fire only when `m_hand ≥ θ_do`; steps 2, 5 and 6 may fire at any margin.
2. **Blocked.** BLOCKED by a binding edge: HOLD (blocked), margins recorded, re-judged when the blocker closes.
3. **Irreversible.** IRREVERSIBLE, or a first-time payee: ASK, a person signs; or, when the class sets `jury_may_sign` and names `jury ≥ 2` families satisfiable locally, the jury, with any dissent an ASK. Under budget overflow, HOLD (budget-human); never any other verb.
4. **Guard.** `m_guard > ε`: ASK, unless the class rung is 4 or above, every effect in scope is reversible, and the writ names `guard_jury ≥ 2`, in which case the jury decides and dissent is ASK.
5. **Check.** `m_check > ε`: WAIT with the two lines, reason `contradicted`, `n_wait` incremented; a WAIT re-judged at its horizon with the revision unchanged becomes ASK under the human budget, overflow HOLD (contradicted).
6. **Degraded evidence.** DEGRADED: at most DRAFT, reason `degraded`. An organ's silence is never a clean check.
7. **Affirmative clearance.** A DO requires `m_guard < −ε` and `m_check < −ε` with `ε` the pinned tie band; a margin inside `[−ε, +ε]` is treated as positive and the row says `tie`. The deputy acts on a judge's assertion that nothing is wrong, never on its silence.
8. **Evidence and license.** Thin evidence, `n_wit` below the class's `wit_floor`: LOOK if `m_hand ≥ θ_look`, else HOLD (thin-evidence). Then the license fold alone, never the grades fold: the rung for `(cls, band)`. `m_hand ≥ θ_do` and the rung permits DO for this band: DO. Rung 2 and the salted lottery selects `(id, judged_rev)` and every effect in scope is windowed or inverse-carrying and the switch is `live`: DO with flag CANARY. Otherwise DRAFT plus a shadow row stating the DO it would have taken. Class assignment is itself a judged decision with its own margin; where an instance plausibly matches more than one class it takes the most restrictive rung and cap.
9. **Look, consult, pass.** `m_hand < θ_do` and the class names `pass_to`: PASS. `m_hand ≥ θ_look`: LOOK, or CONSULT when the look's value clears `θ_consult` and the deep and disclosure budgets have room. Else HOLD (margin).
10. **Budget passes over the whole set.** The stratum draws of every licensed class are funded from the human budget first; if the stratum alone exceeds it, every class at rung 4 or above drops to DRAFT for the period and the account says so. ASKs are then ranked within their partitions by the value of the look, amount times urgency, doubled past due, times precedent leverage, times one plus thinness, ties by id; overflow HOLD (budget-human). CONSULTs under the deep budget, overflow HOLD (budget-deep). DOs under worker capacity, overflow HOLD (capacity). Health obligations under `self_share` of each, overflow HOLD (budget-self).
11. **The terminal.** An obligation past `due_ns` whose class has no license for it and whose ask could not be funded takes the class's declared safe terminal, itself a windowed effect: an acknowledgement, a defer with notice, a decline. An `expired` row is never the first the person hears of an obligation; every obligation reaches ASK at `due − horizon.ask` at the latest.
12. **Rows, then wire.** Every judgment writes its rows; every wire row carries its tape row's hash; the wire is the lane contract's verdict row with `tape_h`.

Pressure from the ledger's ripeness enters the ranking of the walk and never the gate's threshold. A loaded queue changes what is looked at first, not how much evidence an act needs. The thresholds `θ_do` and `θ_look` are not dials on the judge; they are the lower edges of the bands a ratification licenses, per class, pinned. The gate reads competence live from the license fold on every judgment, so demotion is a conjunction and never a flag.

---

## 10 · The ladder and the license

Per class and band, six rungs.

| rung | it may | you see |
|---|---|---|
| 0 · off | nothing; not judged | nothing |
| 1 · shadow | nothing that reaches anyone; it writes what it would have done | the would-have column of the account |
| 2 · canary | act on a ratified fraction of instances whose every effect is reversible, inside the take-back window, under `live` | a row per canary act, each reversible |
| 3 · this wiring | act on exactly the case approved | a row per act |
| 4 · this class | act on cases of the same shape | a row per act and a weekly count |
| 5 · audit by exception | act, with a row the person is not shown unless something looks wrong; a sampled fraction of rows, never zero, is shown | the sample |

The global switch's `shadow` position is globally inert: no effect of any class leaves, canary included. Shadow means shadow.

**The test.** Each `(cls, band, verb)` keeps two one-sided processes on outcome-graded correctness. With grades `X_i ∈ {0,1}`, a pinned baseline `p0`, a ratified margin `δ`, and a predictable bet `λ_i` estimated from prior grades only and truncated at `C`:

```
E⁺_t = ∏ (1 + λ⁺_i (X_i − p0)),     λ⁺ ∈ [0, C/p0]               evidence for
M⁻_t = (1 + M⁻_{t−1}) · (1 + λ⁻_t (X_t − p0)),  λ⁻ ∈ [−C/(1−p0), 0]   evidence against
λ*(p) = (p − p0) / (p0 (1 − p0))
```

`E⁺` is an e-process for the null "no better than baseline"; the non-negative sign of its bet is what makes that hold for the whole composite null, and it is a law. `M⁻` is a Shiryaev–Roberts e-detector, because degradation is a change in a good process and a fixed-start process would be diluted by the good history before it. Promotion when `min(E⁺_act, E⁺_hold) ≥ 1/α_up` with both sides above the sample floor `n0`; demotion when `max(M⁻_act, M⁻_hold) ≥ 2/α_dn` with `α_dn = 10·α_up`. Promotion inherits Ville's inequality; demotion inherits the detector's run-length bound. A Beta-mixture e-process runs beside the betting process as a check, and disagreement by more than an order of magnitude is a bug.

**The baseline.** `p0` is never estimated from the stream the test consumes. Preferred, wherever a stratum exists: the test is paired against the person on the stratum, `Z_i = (1{deputy right} − 1{person right} + 1)/2` against `m = 1/2 + δ/2`, which needs no external baseline and does not drift with the case mix. Otherwise `p0` is the lower end of a one-sided 95 percent Clopper–Pearson interval on the person's correctness measured once in shadow and pinned by a ratification row.

**Horizons.** Grades enter each process in ascending `(horizon_ns, id)`, never in decision order. The grading function is total: unknown at the horizon grades zero on the promotion side. An outcome landing after its horizon writes a `regrade` row that feeds the epoch and may trigger a demotion review, and never re-enters a process that has passed that horizon. The bet is written on the tape before its grade is read. The license is read at the class's longest finite verb horizon; grades are reported per verb at their own. Obligations with no deadline are excluded from licensing evidence and graded only through the stratum and the expectation.

**Calibration** of a band requires both sides of the threshold to clear `n0`: the acts, from acts, shadow and canary, and the holds, from shadow disagreement, the stratum, and expectation misses.

**Expiry.** A ratification row carries its own expiry. When it passes, the class drops one rung and the row is spent; re-widening requires a new ratification. Before expiry, a rung that loses its evidence drops one rung on grades alone and may re-earn it while the row stands. Re-earning resets both processes; after `k` epochs the lifetime error bound is `k·α_up` and the account prints it. Expiry is jittered deterministically from the class id so classes ratified together do not expire in a cohort; the console shows a seven-day horizon.

**The audit floor.** At rung 5 the sampled fraction is `max(sqrt(3/F), 1/64)` at volume `F`, the class's judged instances in the trailing seven days. The square-root branch is a fixed point of the rule of three: reviewing `sqrt(3F)` items and finding nothing certifies a defect ceiling of `sqrt(3/F)`, the sampling fraction itself. The `1/64` floor binds above 12,288 per period.

**The monotone law.** The license reducer may narrow on evidence alone: grades, kappa, fronts, expiry, and the floor's parity check. It may widen only to a rung and band a signed ratification row covers, one rung at a time, and it may never author the rule.

**The ratification row** carries class, rung, band, stratum, canary, expiry, the hash of the grades fold at the head it was minted from, the sample count on each side, kappa, the writ hash, the console build hash, a nonce, and the operator's signature over all of it. The license fold refuses a row whose grades hash is not on the tape, whose writ hash is not the writ in force, whose nonce was seen, or that widens by more than one rung. A widening takes effect at the first beat after `ratify_delay_min`, cancellable from the console throughout.

**The stratum.** A ratified fraction of every class at rung 2 or above is routed to the person, floored by the writ's value and by the audit floor. The kernel may raise it on evidence and may never lower it; lowering below the fold's value requires a `stratum_override` with a reason and an expiry, printed on the account every week it stands. The draw is `BLAKE2b(id ‖ judged_rev ‖ salt) mod 2^32 < rate · 2^32`, the salt in the writ and never in the trunk, so the assignment is reproducible from the writ and unpredictable from inside the judge. The stratum is drawn toward what the class fails on, over-representing the band nearest the act threshold and the region where the check seat fired. When the human budget is exhausted, the stratum's draws are judged in shadow by the floor and the base arm, marked `arm = null`; they grade holds and never license. No single counterparty may contribute more than a ratified fraction of a class's evidence, default one fifth, and a party new to a class is judged one rung below it for its first instances.

**Fronts.** A `front` fold on the ingest clock runs CUSUM on the per-class world residual and on the structured columns' distributions; a front in a class writes a `front` row and narrows the class to rung 1 until re-earned, with no ratification needed. Expiry and fronts are the first line; kappa bites late.

---

## 11 · The valve and the hand

**The sandbox.** At startup the launcher creates an AppContainer profile with zero capabilities, derives its package SID, and re-executes the kernel into it with child-process creation restricted. Windows Filtering Platform then denies every socket the kernel or any read organ in the container attempts, outbound, inbound and loopback, at the ALE layers, with no administrator and no installer. The module gate is retained as a lint. The header row prints which mechanism is in force: `os-enforced`, `wfp-installed` when the container could not host the card and an administrator-installed filter keyed to the image path stands instead, or `lint-only`. The account prints the same word every week. Whether the resident model runs on the card inside the container is measured at M0 on the target machine before anything is built on top of it.

**The pipe.** The hand creates it with `FILE_FLAG_FIRST_PIPE_INSTANCE` so a squatter is a loud startup failure, with `PIPE_REJECT_REMOTE_CLIENTS`, and with an explicit descriptor naming the kernel's package SID and denying network and anonymous logons. Both ends identify each other after connect by process id and image; the kernel opens its end with identification-level impersonation so a hostile server cannot impersonate it.

**The effect registry.** Five reversibility classes, and the registry is the truth for reversibility; a class is IRREVERSIBLE when any effect in its scope is registry-irreversible.

| class | mechanism | examples |
|---|---|---|
| inverse-carrying | the inverse recorded with the effect and applicable | file move, calendar tentative, draft, ledger row |
| windowed | held in the outbox for the take-back window, reversible until release | mail send, calendar confirm, message post |
| irreversible | the jury and the cap, or a person's signature | payment, contract, deletion, external form submit, a first-time payee |
| disclosing | no inverse, no window; the harm is that bytes left; counted against the disclosure budget; a sensitive class requires an ASK | CONSULT, FETCH, every brief to an endpoint |
| reflexive | a change to FACTOR's own definition: a routine, an adapter, a map, the lane set; a ratification plus goldens plus an expiry, never a window alone; the inverse is the previous version | compile, grow |

The three-state invariant: an irreversible effect without a signature or a jury holds; a reversible effect without a license may act only as a canary inside its window; a licensed effect acts. No fourth path exists in the hand.

**The outbox** is the hand's private state, never an interface; the hand accepts staged effects only over the pipe and ignores any file it did not write. Release is a round trip: at release the hand asks the kernel for the obligation's current revision and the effect digest and sends only on an exact match; with no answer within the bound, or a wedged kernel, nothing leaves. `takeback_min` is a floor: for any class marked `presence_gated`, every irreversible, every disclosing, every first-contact party, the effective window is the larger of the floor and the time to the next operator presence signal, presence being recorded as a `presence` row; after a presence gap, release is rate-limited to `burst_release` per minute and the remainder hold with reason `window-open`. `factor outbox --hold-all` cancels without the kernel. A provider's own scheduled send may be used as a second, outer window and is never the authoritative one, because F-WINDOW must be provable from the tape without a network call.

**The jury.** A provenance family is `(base weights hash, pretraining corpus id, tuner, vendor)`, declared and pinned; two judges collide if any component matches and a colliding pair never counts as two. A family holds at most one role per obligation: a judge may not vote on an effect its family drafted, compiled, consulted on, or supplied evidence for. An endpoint family is never a required family for an irreversible effect; irreversible quorum must be satisfiable by local families alone. Jurors are kernel-side organs in the sandbox, or reached through the hand for an endpoint family; the hand holds the cap and never a judge. Each juror reads the same brief, the local juror the full one and the endpoint juror the redacted one, and returns a margin and a reason. The brief and the jury row cover `(obligation id, src_rev, effect type, every typed effect field including amount and payee, the cap in force, tape head, nonce)`; the valve recomputes the digest at release and refuses on any difference; an approval older than `jury_ttl` is void. The account prints inter-family agreement per class, and a jury whose agreement exceeds the ratified ceiling is a jury of one: `jury_may_sign` is withdrawn for that class automatically. The jury never sits on a card's authorization webhook, where a timeout would convert a dissent into an approval.

**The cap.** Caps are rolling aggregates, per class per day, per counterparty per day, and per act, enforced by the hand and, where a provider exists, by the provider outside the box. A set of effects to one party inside a window is capped as one effect. A first-time payee is irreversible regardless of amount. The cap provider is an interface: a `cap-provider` organ whose `--about` declares who holds the key; the reference implementation is a card-issuing provider with per-authorization, daily and monthly limits enforced at authorization time, and the hand holds a restricted key that cannot write those limits. F-CAP tries to raise the cap with the hand's own credential and the provider must refuse.

**Egress.** The hand counts every outbound byte per endpoint per row and refuses any host not in the allowlist. Every producer's outbound bytes are counted on the same ledger. An effect executed on a rented machine records the vendor as the endpoint and marks the machine's own page bytes unmetered by construction, declared on the row. Every brief's exact bytes are hashed to the tape and retained in the dossier.

**Idempotency.** Every effect carries the obligation id and the revision it was judged at; the hand refuses a duplicate pair and refuses at release a pair whose revision the kernel reports as superseded.

**Hands.** A free local headless browser with a throwaway profile is the first hand; a cloud browser with a live view and a downloadable replay is the second; a full agent computer is the third. Never the person's own browser, which is a lane. A rented machine's screenshot chain and replay are downloaded, hashed and written to the dossier; the vendor URL is metadata. A vendor's managed credentials are refused; credentials come from the seam broker. A persistent logged-in profile on a rented machine is a standing credential and must be licensed by the writ.

**Two addresses.** The person's mailbox is a lane, read only. FACTOR's own address is an agent inbox provisioned as an object, so a chaser's reply lands as a frame; every outbound effect names which address it leaves from and the egress ledger prints it.

---

## 12 · The tape

Append-only, keyed hash chain, segmented, the ground of everything.

**Rows.** JSON lines. Every row is `body` plus `prev` plus `h`, where `body` is the canonical JSON of the row's fields with `prev` and `h` removed, and:

```
h = BLAKE2b-256-keyed( K_tape ; prev_hex ‖ u64le(len(body)) ‖ body )
K_chain = BLAKE2b-256( machine_secret, personalization = "FACTOR <chain> v1" )
```

`prev` is the previous row's `h` as 64 lowercase hex characters; the genesis `prev` is 64 zeros. The tape and the dossier are keyed, with the key sealed to the kernel's process; the spool chains are unkeyed so a spool verifies alone. Personalization strings give each chain an independent key from one secret, so a row lifted from one chain cannot verify in another. The known-answer vector for the hash is asserted at boot beside the serve bytes.

**Two witnesses of the head.** The hand records the tape head with every `staged` and `executed` receipt under its own key, so a compromised kernel cannot rewrite a judgment that preceded an effect without the hand's copy disagreeing. The console appends the head fingerprint to an external witness the box can write and cannot rewrite at least daily; the account prints the last externally witnessed head, its time, and the rows accrued since, and a gap is a `warn`.

**Canonical JSON.** UTF-8; keys sorted by code point; separators `,` and `:` with no spaces; no ASCII escaping of non-ASCII; no NaN, no Infinity, no bare floats; every 64-bit integer written as a decimal string; unknown keys are `fatal`. Margins and amounts are fixed-point integers. Measured on this machine, the same double serializes as `1e+16` in one language and `10000000000000000` in another; two verifiers would compute two heads for one tape.

**Clocks on rows.** `ms`, the steady clock since boot, lives beside the row and outside the hashed body. `t_mono_ns` on a `frame` row is the frame's; on a `verb` row it is the triggering frame's, so a replay reproduces it. The plan hash on the account covers, per verb row, `(id, judged_rev, verb, reason, flags, band, rung, the quantized margins, batch id, position)` and excludes `ms`, `prev` and `h`.

**Verification is two-way.** `h == H(prev ‖ len ‖ body)` proves the row is intact; `prev == previous row's h` proves it is in its place. A verifier that checks only the first accepts a rewritten row whose hash was recomputed; the planted lie in `tests/chain_check.py` is exactly that row.

**Torn rows.** Exactly one row may be torn, and only the last row of the last segment: no trailing newline, undecodable JSON, or a hash that does not verify. Any of the three earlier, or in a non-final segment, is `fatal`. The head is the `h` of the last row that verifies both ways, and a torn row is skipped with a `warn`.

**Segments.** A row is never split across segments; the bound is checked before the append. Filenames are zero-padded and monotone; the first row of segment N+1 carries `prev` equal to the last verified `h` of segment N; `manifest.json` is a cache and `factor verify` must produce the same head with it deleted. No row counted by a live e-process may be compacted before its class's expiry window plus one; compaction is operator-signed and recorded.

**Encryption.** The chain is computed over plaintext; each segment is sealed under an AEAD whose associated data is the segment's first `prev`, with keys wrapped by a TPM-sealed key bound to the boot state and the kernel binary's hash, unsealed into the kernel's process only. `factor verify` needs the key; `factor verify --chain-only` verifies the published fingerprint chain without it. Spools and the dossier are encrypted the same way.

**Kinds.** `hdr · frame · heard · echo · forming-skipped · refused · trunc · replay · obligation · boundary · verb · look · fetch · draft · staged · executed · reversed · unsaid · asked · answered · consulted · discard · jury · outcome · receipt · grade · regrade · license · ratify · stratum_override · expect · want · front · compile · grow · organ · ckpt · rollback · molt · vram · tick · presence · switch · warn · fatal · erasure · account · stop · end`. Every kind folds or verifies; `boundary` is the frontier copy's residual on a committed frame.

**References, not copies.** A `frame` row references its spool by `(lane, generation, offset, h)`, where `h` is the spool line's chain hash. A replay re-reads the spools; the tape holds judgments and receipts.

---

## 13 · The folds

Each fold is a deterministic reduction over the tape, stamped with the head it was folded from, incremental, and named with its clock and its input's trust.

| fold | clock | reduces | produces | input trust |
|---|---|---|---|---|
| **state** | incremental on write | obligation, verb, draft, staged, executed, reversed, unsaid, asked, answered, outcome, expired, rollback rows | the ledger and its indexes | deterministic |
| **grades** | each verb's horizon | verb rows joined to exogenous outcome rows by id and revision; the person's own discharges as verb rows with `seat = human`; shadow disagreement | correctness per `(cls, band, verb)` for the deputy and the person, both sides of the threshold, the direction of disagreement | exogenous |
| **expect** | on arrival | `expect` fields diffed against what arrived | misses, which grade holds and raise the world residual | exogenous |
| **license** | periodic and on `ratify` | grades, ratify rows, fronts, expiry, the floor's parity, the monotone law | rung and band per class; the stratum rate; the canary rate | chosen thresholds, guarded |
| **kappa** | periodic; daily on the console, weekly on the account | verb rows with their costs; the person's baseline minutes per class | supervision created per supervision removed, per class; DEMOTE at or above one; `forecast` until the outcomes for the period have reached their horizon, then `measured` | chosen thresholds |
| **fronts** | the ingest clock | CUSUM on the per-class world residual and on structured column distributions | `front` rows that narrow a class immediately | deterministic |
| **contradiction** | on arrival, incremental; exhaustive once | a new obligation against its topical neighbours; a typed comparator for amounts, dates, accounts and names; an inference head for prose against prose; both orderings | pairs that disagree with the head that found them; contested pairs stand and are never resolved | deterministic and model, each row says which |
| **routines** | periodic | verb and executed rows per class | classes whose discharges a deterministic function explains | deterministic |
| **wants** | weekly | `want` rows, a judgment that would have differed given a named unreachable source | proposals clustered by frequency times decision impact, capped per account | deterministic |
| **negative space** | idle cycles | obligations held past due, held with no horizon, classes with a rung and no attempts, counterparties silent past their baseline | the `not doing` section of the account | deterministic |
| **account** | weekly | everything since the last account | the weekly, signed by the head | n/a |

**Outcomes.** An `outcome` row is admissible to the grades fold only if its witnessing frame arrived on a lane or venue the graded effect did not write to, or carries a counterparty revision the hand did not author. A frame that is the hand's own effect reflected is a `receipt` row, joined to `executed` for reconciliation and never to a verb for grading. A class whose outcomes are predominantly self-attested may never exceed rung 3. Every outcome row names its `evidence_source`. Outcome semantics per verb: for DO, not reversed and the discharge predicate true at the horizon; for HOLD, the discharge predicate true by due without a person's act, else breach; for ASK, the answer; for a shadow verb, the person's action on the same id, graded immediately as agreement or disagreement, plus the outcome of the person's act.

**Kappa's fraction.** Numerator: person-minutes created per week by asks, stratum reviews, audit samples, reversals and probes in the class, at minutes per event measured from the console's decision latency. Denominator: person-minutes removed, the class's instances handled by the deputy times the baseline minutes per instance, measured in shadow from the screen lane's active-window time on the instance's thread. A class with no baseline has kappa undefined and cannot be promoted. The account never prints a handled count without the outcome-graded error rate of what ran unattended beside it, at both grains.

**The walk.** Covers the whole open set every period, ranked and budgeted, so a deadline ripening with no inbound frame is still judged. The ranking signals: `health` first, sorted by id; recency, where the world just changed; ripeness, re-projected against `now` on every walk; the world residual, an obligation's deviation from its expectation and its class baseline; thinness, where the license is uncalibrated; the dark-matter lottery over obligations with no signal at the writ's rate; a uniform component; inverse-density weighting; and a no-guide stratum where the ranking is not used, so its value is measured against not ranking. The frame residual, the model's prediction error on the next frame, is logged and ranks nothing, because prediction error on a person's writing is novelty, noise or capture, and aiming by it densifies the flakiest seats. The kernel may raise the uniform and lottery rates and never lower them.

**The contradiction budget.** The incremental scan runs before the verb on the card against a few thousand candidate pairs with a pinned p50 and cap; a scan past the cap writes WAIT with reason `degraded` rather than stalling. The exhaustive sweep over an archive runs once, rented, and its one-time question is how much cheap retrieval would have missed.

---

## 14 · The compiler and the grower

**Routines are organs, not code in the kernel.** When the routines fold finds a class whose discharges over the last N instances are explained by a deterministic function of the obligation's typed fields, the kernel asks the deep gear through the hand to write the function, and the function is written in a total, side-effect-free evaluator over the typed fields: no I/O, no imports, no clock, no randomness, fixed-point arithmetic, a bounded step count, statically verified against the grammar before ratification; where native speed is required, WebAssembly with no host imports beyond a pure field-accessor interface, hash-pinned. A routine declares its input domain; an instance outside it falls back to the judged path with reason `out-of-domain`, never extrapolation. It is replay-tested against every instance on the tape and must reproduce the deterministic part bit-identically, then proposed as a reflexive effect with the receipt. Ratified, it enters at rung 2 for its class and climbs on its own grades; it emits a proposed effect that passes the same gate, caps and valve as a judged discharge; its first M live instances are compared to the judged path in real time and divergence above the ratified rate suspends it immediately; drift in the input distribution suspends it likewise; the judged path continues under it at the stratum rate as its control arm.

**Adapters run in the sandbox.** When a lane fails, an export format changes, or the wants fold names a source with no producer, the gap is a `health` obligation. A grown adapter is written through the deep gear, runs in the network-denied sandbox with a per-adapter host allowlist enforced by the sandbox rather than by its own code, receives scoped, short-lived credentials from the seam broker, passes the conformance battery on a recorded sample, runs in shadow against that sample, then read-only diffed against its predecessor for its first live period, and is pinned with its own expiry that no unrelated writ edit resets.

**Growth floors.** Graft, mounting an existing catalog action or producer, before grow, authoring one; authorship only while idle; at most N proposals per account; every grown artifact is something the person keeps.

Neither the compiler nor the grower can ratify.

---

## 15 · Rollback and checkpoints

**A checkpoint** is a directory: the trunk state saved with attention and recurrent caches together, the tape head, the ledger stamp, the license stamp, the routines in force, the writ hash and sequence, the wall time of the last frame, the verbatim tail, `npast`, and a manifest hashing all of it against the pin tuple. Written to a temp path, renamed with write-through, the previous generation kept, the manifest written last. Periodic checkpoints run only when idle, no line open, two seconds since the last frame and backlog zero, and always at molt and at stop; the `ckpt` row carries `outage_ms` and the frames queued during it. Restore requires the manifest, the pin tuple, and `npast` to agree, tries the previous generation on a mismatch, clears any pending rewind, and boots the twin and says so when both fail. A checkpoint of an aliased fork cannot be restored; the root is checkpointed, never an alias. Every atomic rename retries twenty times at five milliseconds and then writes a `warn` naming the path, because a reader holding the destination open makes the rename fail on this platform.

**Rollback restores state and never restores authority.** A `rollback` row at tape position P naming checkpoint head H is a fold instruction: every fold reads the tape in order, discards its state at P, resumes from its own stamp at H, and continues with the rows after P; rows between H and P stay on the tape, verify, and are shadowed for state and grades; the account counts them. A `license` row recording a demotion or an evidence-driven narrowing applies at every head at or after it and survives rollback; re-widening after a rollback requires a fresh ratification. A rollback target is operator-signed; a rollback that would re-widen any license is refused unless it names each widening; the reversal set is presented before it runs, and reversal of effects older than the ratified age requires a signature. Effects executed after H are reversed by inverse where possible and listed where not.

---

## 16 · Organs

Capabilities that are not the kernel's own live at fixed paths as subprocesses and are never imported.

**The contract.** One typed request in; one JSON answer out; a token or byte budget honoured and any truncation counted, never silent; the stop rule stated first; a `plan_hash` where the answer is a plan; corpus excerpts wrapped as INERT blocks the seam executes nothing inside. Exit codes, with the family's semantics: `0` done · `2` refused, never retried with a reworded argument · `3` empty, a typed negative carried in the body · `4` stale, rebuild · `5` not found · `6` degraded, the body names the missing rung. Every organ answers `--about` with its version, pins, its network declaration and the subset of codes it uses. Every organ's paid lanes are refused when called by the kernel; an organ that needs a paid lane is reached only through the hand as a CONSULT.

**Network declaration.** An organ declares `net: none` or `net: via-hand`. The launcher spawns only `net: none` organs into the kernel's sandbox; every `via-hand` organ is a child of the hand. An organ that lies about its declaration is caught by the sandbox, not by the declaration.

**The tape of tapes.** Every organ the kernel consults leaves an `organ` row carrying its name, version, pins, exit code, and its own tape head, so the whole animal verifies from one genesis while each organ verifies alone.

**The organ surface.** The kernel serves its own state to organs over stdio only, using the dated tool protocol revision of 2026-07-28, which is stateless and has deprecated sampling, so an organ can never ask the kernel for a forward pass. Exit codes map to a declared `_meta` key. A re-issued call after a dropped stream lands as a `replay` row, never a second `consulted`.

**Named organs.** Memory and relations over the seat's corpus, whose `place` verdict is the residual signal on file lanes, RETELLING adding a witness and never opening an obligation; an adjacency index that returns read plans under a budget, whose exit 3 writes `hold(thin-evidence)`; a shared notebook of what was understood, whose `contradicts` links are where contested pairs stand; a lifetime-archive reader with local OCR and ASR. Which implementation fills each slot is a configuration line; an absent organ degrades with exit code 6 and the account says which.

---

## 17 · Surfaces

**The console.** A separate process under the operator's hand and key. It shows the ledger by ripeness, the tape tail, the open asks with their two lines, and the seven-day expiry horizon. It never writes into a line the person is touching; forming text is never saved. An answer to an instance ask, sign, decline or later, is an `answered` row keyed by `(id, judged_rev)` and changes no license. An answer on a class, yes, not this, or later, is a signed `ratify` row naming class, rung, band, stratum, canary, expiry; the console labels which it is asking. It records decision latency and whether the two lines were opened; a class whose median ask latency is below the floor with a yes-rate above the ceiling has its stratum raised and its promotion frozen until the operator ratifies a `reviewed` row. A ratified fraction of asks are probes carrying a planted error the operator should catch; an approved probe freezes the class and is named on the account. `not this` answers fold per class; past a pinned count in one direction the account carries the divergence as a finding, and the person edits the writ.

**The account.** Every Friday, whether or not anything happened, and kappa daily on the console: what it did, what it held with margins, what it asked, what it compiled, what it grew, what it is not doing, the pair, asks made of you against things handled, kappa per class with its verdict and its `forecast` or `measured` mark, the outcome-graded error rate of what ran unattended, the tie count per class, inter-family jury agreement, egress and disclosure totals by host, the fixed costs, tenancy of the card and the latency percentiles for free and shared, the last externally witnessed head, and the tape head's fingerprint. Every number carries its grain, per judgment, per obligation or per class, its denominator, and the hash of the fold that produced it; a number lacking any of the three is not printed. Never adoption. Never hours saved. The account's destination is a field of the signed writ; a reply to it is an untrusted mail frame with no operator standing.

**The API.** A local named pipe with the console's typed messages. Read paths are free. Write paths are narrowing only: `not this`, `later`, `stop`, `rollback`, `answered`. A `ratify` row that widens is minted only by the console from an interactive act.

**The watchdog** is an operator-installed service that may report and may stop, never start with different arguments. Restarts are rate-limited, land as `restart` rows, and a crash loop degrades to `off` until a person flips the switch.

---

## 18 · The tune

The judge improves only by versioned weight events, never by living weights.

- `factor epoch` exports the graded rows since the last epoch, every verb with its margin, outcome and grade, holds and acts alike, excluding jury rows and every row whose outcome was produced under jury approval, so the local juror is never trained to agree with the remote one.
- Training runs outside the kernel and produces an adapter or a full tune.
- The goldens are the tape: the new version must not regress on the graded rows it was trained beside, held out by time, with the person's baseline as the bar.
- Deploying a new version is a widening and needs a ratification.
- The pin is a tuple minted together and asserted at boot and at restore: the serve bytes, the weights file hash with its quantization type and imatrix, the hash over every schema map in force, the runtime's build identity and state-format version, a hash of the context parameters that shape the state layout, and every environment variable that shapes the logits. A changed member is a retune. A requantization is a different judge.
- Lineages are allowed: two adapters may serve two strata and the grades decide which widens. No lineage self-promotes.
- The transfer bet names its bar: at the utterance radius the best fixed threshold caught 36 of 39 planted moments and was deaf where it mattered, dial zero fired 921 times an hour, and the tune moved the flood from 63.4 to 6.7 percent at matched grain. The obligation-radius tune must reproduce a cut of that order on the shadow tape or the bet dies.
- The captured-corpus kill: a disposition pretrained on decisions harvested from organizations that were themselves captured is expert in exactly the situations dysfunction produces. The goldens are the exposed surface; the staggered-rollout arm and the floor's parity check are the instruments.

---

## 19 · Budgets, priors, and determinism

Every budget below carries the measured prior that exists on this machine, with its source, or says `no prior`. Each is printed on the account beside its measurement.

| quantity | budget | measured prior | source |
|---|---|---|---|
| one three-seat judgment on a fork, free card | under 150 ms | 44 ms per single probe on a free card; 106 to 135 ms p50 for three seats in the kernel's smoke runs | family bench; kernel convergence §7 |
| the same, card shared with a workstation | printed, never budgeted | 600 ms to 24.6 s | Addendum B |
| frame arrival to verb, reflex path, free card, p50 | under 300 ms | 733 ms p50 live, 1421 ms mean shadow, on a loaded card | kernel convergence §7 |
| ledger readout over fifty thousand obligations | under 5 ms | no prior | |
| probe sweep over fifty thousand obligations | printed as its own line | about 37 minutes at 44 ms each | a parallel session's arithmetic |
| incremental contradiction scan per new obligation | p50 under 2 s, cap 10 s | no prior | |
| trunk KV per token | printed | about 17 KB | family bench |
| trunk depth without degradation | 160,000 tokens | 160,000 and more, no knee | operator's live test |
| checkpoint outage | under 200 ms | 56 to 92 ms at 512 tokens; about 1.2 GB at 65,536 | kernel convergence §7.3 |
| boot with model load and trunk restore | under 60 s | no prior; the restore dominates | |
| asks funded per day at `human_minutes = 60` | printed | five, at the shipped twelve minutes per brief | Org Solver `VerbCost` |
| outcomes per class per term against `n0` per side | printed | no prior; at one seat most classes will sit at rungs 1 and 2 until this is measured | |
| flood rate at dial zero and after the tune | printed | 921 per hour; 63.4 to 6.7 percent | the operator's recorded workday |
| kernel egress | 0 bytes, OS-enforced | | |
| VRAM after load against `vram_budget_mib` | a boot refusal | 10.8 GB free of 16 GB on this box, co-tenanted | `vramtop`, 2026-09-08 |

**Determinism laws.** Fixed-point amounts, never float accumulation. Every walk sorted by id. Every threshold pinned in the writ. A decode failure is fatal with a row, never a stale margin. Every lottery draws from a keyed hash of `(id, judged_rev, salt)`, never a system generator.

**What is deterministic is the decision, not the logit, and the difference is a law rather than an apology.** Logits from the CUDA backend are not batch-invariant: the same tokens give different last bits depending on how many others shared the pass, and they move with the ubatch split, the KV layout, the device's SM count, the driver and cuBLAS version, and the backend's environment. As of 2026-09-08 the runtime offers no deterministic mode, and the pull request proposing one has been an unmerged draft for a year. So FACTOR makes the decision insensitive to the card: margins are quantized to `int16` in 1/1024 logit before the gate; a margin within the tie band of any threshold takes the conservative branch and writes `tie` with a counter; the verb row records the batch it was judged in and its position, so a replay reconstructs the same batch rather than deriving one from a clock it no longer has; and the boot pin covers the runtime, driver, device and environment. The law restated: two runs over the same spools, writ and pins produce byte-identical verb rows, proven by the plan hash; two runs across different pins may differ only where a margin crossed a quantum, and every such row already says `tie`. A class whose tie rate climbs has badly placed thresholds, and that is a finding.

---

## 20 · Threat model

**What is enforced, and by what.** The kernel cannot reach the network: the operating system, at the boundary of its process tree, with the header row saying which mechanism stands. The kernel cannot spawn a process: the launch attribute. The writ and the switch cannot be forged: a signature from a key the console alone uses, with user presence. A stale decision cannot leave: the release round trip. A license cannot widen without a person: the monotone law, the signed ratify row, and F-MONOTONE. Money cannot leave on one model's word or above the cap: the jury, the aggregate caps, the restricted key, and F-CAP.

**What is not enforced, and said plainly.** A local administrator or SYSTEM lifts the filter, injects, reads the trunk, edits the writ; AppContainer is not a defence against the machine's owner. Covert channels, timing, file names, the content of a permitted brief, are unbounded. The hand's allowlist and byte ledger are the perimeter; the kernel's inability to open a socket is depth behind it.

**Injection through lanes.** Inertness of bytes is not inertness of evidence. A crafted message that projects to a real obligation is the attack that matters, and it is met by standing, by witnesses counted per provenance root, by the monotone-percept law, and by FETCH targets that are never a URL from prose.

**Injection through hands and organs.** What a hand reads returns as a lane and is inert; what it does is a registered effect. An organ's silence is degraded evidence, never a clean check. An organ that opens a socket is caught by the sandbox.

**Credentials.** Issued by the seam broker, scoped and short-lived, never in a frame, a brief, the tape, or generated code.

**Supply chain.** Every organ, adapter and routine is hash-pinned with an expiry and boot-asserted; adapters run shadowed and read-only before live.

**The model as adversary.** It cannot open a socket, spawn, write the writ, flip the switch, widen a license, raise a cap, lower a stratum, delete evidence, or veto a rollback. Its own health cannot act. Its powers are to propose, to draft, and to act within a ratified window.

**The operator as the last line.** Off is inert. Stop finishes the tape. Everything can be undone to a checkpoint, what cannot is listed, and nothing undone returns authority.

---

## 21 · Falsifiers

Each ships with a planted lie that must fail. Grouped by the law it tests.

| id | law | requires | the planted lie |
|---|---|---|---|
| F-RESIDENT | 1 | a run with no frames writes no verb row; every verb row's wake names a frame | a verb from a timer callback |
| F-TICK | 1 | a restored trunk receives one tick for its absence; the first frame's margins match a no-restart control within the tie band | resume with no tick |
| F-RIPEN | 1, 13 | a deadline crossing with no inbound frame still produces a verb row | walk only the event-touched set |
| F-EXTRACT | 2 | planted promises recovered at the tolerance; retractions close; a forwarded quote is one witness | offsets emitted by the model; a quote counted twice |
| F-SILENCE | 3 | a judgment without a row is fatal; no open obligation lacks a standing verb | a hold with no row |
| F-CONSERVE | 3, 4 | every frame lands in exactly one of: ingested, replayed, truncated-with-count, refused-stale, heard-not-judged, forming-skipped, echo-skipped, withheld-by-provider-then-replayed | drop one frame silently; count a replayed batch twice |
| F-REPLAY | 8 | a full replay of the spools reproduces the ledger digest bit-identically without re-running the model | a float accumulator; a re-run extractor |
| F-DETERMINISM | 3, 19 | two runs, two insertion orders, byte-identical plan hashes | walk in hash-map order |
| F-QUANTA | 19 | replay under a perturbed batch composition reproduces every verb row; rows that differ carry `tie` | compare raw logits and call the difference a pass |
| F-SALT | 19 | every lottery assignment is reproducible from the writ and unpredictable from the trunk | a system random generator |
| F-CHAIN | 3 | one flipped byte in a segment fails `verify`; a row rewritten with its hash recomputed fails the link check | a row-local verifier |
| F-INERT | §10 | with the switch `off`, every venue a producer is mounted in is byte-identical to FACTOR absent; with `shadow`, the hand receives no effect, canary included | an effect under `shadow` |
| F-INERT-BYTES | 11 | a planted frame on every lane containing an effect message, a verb name, a writ stanza and an organ answer produces a frame row and a verb row and nothing else | the seam parses a verb name out of frame text |
| F-BLIND | 11 | with the counterparty's frames removed, the check and guard margins never fall below the full read's | use the full read alone |
| F-STANDING | 11 | an obligation witnessed only by a party without standing never reaches DO at any rung | standing inferred from politeness |
| F-EGRESS | 5, 10 | a probe compiled into the kernel opens a socket by three routes, the socket library, a raw device control, and a loopback connect, and all three are refused by the OS; the hand's egress ledger equals the sum of its rows; no process in the kernel's tree holds a socket at any sample | a module-list check standing in for the OS refusal; an organ child that opens a socket |
| F-WINDOW | 4 | a windowed effect reversed inside its window leaves no trace in the world and a `reversed` row on the tape, against the provider actually wired | release before the window |
| F-ORDER | 4 | every `executed` row is preceded by its `staged` and `verb` rows; a failed effect leaves a `verb` row and a `warn` | execute then record |
| F-BUDGET | 13 | two thousand asks, room for ten, the rest hold on budget and nothing acts; the stratum is funded first | act because nobody was available |
| F-TERMINAL | 13 | an obligation past due with no license and no budget takes its safe terminal; `expired` never precedes an `asked` or a `hold(budget)` | hold silently |
| F-SELF | 12 | a lane whose producer dies opens a `health` obligation within one tick; a `health` obligation never reaches DO; a health discharge never writes an autostart entry; health never exceeds `self_share` | health at DO; an autostart |
| F-JURY | 7 | one dissenting family and the irreversible effect holds; a quorum of one family counted twice is refused; an approval bound to different effect bytes is refused | two judges of one lineage as two families |
| F-FAMILY | 7 | a planted case where two judges of the same lineage agree wrongly does not clear a two-family quorum | lineage ignored |
| F-CAP | 7 | an effect above the per-act, per-day or per-party cap never leaves; with the hand's own credential, raising the cap fails at the provider; a first-time payee always asks | a full-permission key |
| F-MONOTONE | 6 | the license fold cannot widen a band without a covering signed ratification row; a ratify row over the API is refused; a row with a seen nonce is refused | widen on grades alone |
| F-COVERED | 6 | every `executed` row at rung 3 or above is preceded by an unexpired ratify row covering its class, rung, band and, for a canary, its draw; no `executed` row in a class whose kappa read at or above one at that head | an executed row one revision after expiry |
| F-BOTH-SIDES | 6 | a band is not calibrated until both sides clear `n0`; an outcome forged from the hand's own receipt does not calibrate | license on act evidence only |
| F-WITNESS | 6 | a planted self-written close never licenses; an outcome from the lane the effect wrote to is a receipt | grade a calendar confirm from the calendar it wrote |
| F-PREDICT | 6 | every bet on the tape precedes its grade in horizon order; a re-fold reproduces every e-value bit-identically | a bet computed from the grade it reads |
| F-DETECT | 6 | a class good for 500 grades then degraded for 40 is demoted; a fixed-start process on the same tape is not | demotion by a fixed-start process |
| F-EXPIRY | 6 | a rung past its ratification's window drops one; classes ratified together do not expire in one cohort | permanent once approved |
| F-CANARY | 6 | under `live`, a rung-2 class acts on the lottery's fraction and no other instance; every canary effect is reversible and reverses cleanly | a canary on an irreversible effect; a canary with no covering row |
| F-FRONT | 6 | a planted distribution shift suspends the class before its expiry; a stationary stream does not | fronts read at the fold's cadence |
| F-DARK | 13 | an obligation with no recency, ripeness or expectation is judged within N periods | rank only what moved |
| F-OBSERVE | §24 | a staggered arm measures whether being shadowed changes the person's behaviour | assume it does not |
| F-ROLLBACK | 8 | folds re-derived to an earlier head match the folds stamped at that head; the rollback row is honoured as a fold instruction | a fold that reads past its head; a fold that re-applies a shadowed row |
| F-ROLLBACK-MONOTONE | 8 | a rollback never re-widens a band | restore yesterday's license |
| F-MOLT | 8 | a planted fact in the oldest band survives the fold at the family's ratio or the account prints `lossy` | silent truncation at the watermark |
| F-CONTRADICT | §13 | a planted typed disagreement is caught by the comparator, a planted prose disagreement by the inference head, neither by the other; a contested pair is never resolved | one head for both |
| F-DEGRADE | 11 | an obligation whose check evidence depended on an organ answering 3, 4, 5 or 6 never reaches DO | a missing organ as a clean check |
| F-REDACT | 10 | a brief is assembled by code from declared fields through the redactor; its bytes are on the tape | a brief assembled by the model |
| F-COMPILE | 9 | a ratified routine replays bit-identically against the tape it was compiled from; an out-of-domain instance falls back; a diverging routine suspends in real time | a routine that passes on a sample; a routine that extrapolates |
| F-PIN | 14 | a drifted serve byte, weight, quantization, schema map, runtime version, context parameter or environment variable refuses to boot | a supplied identity trusted unchecked |
| F-LAYOUT | §5 | `sizeof(Obligation) == 128`, every offset as pinned, no implicit padding | the v0.1 claim asserted |
| F-FRAME | §4 | 10,000 random strings round-trip; each is one line to every reader | an encoder that drops carriage returns |

---

## 22 · Milestones and gates

Each milestone ends in a dated receipt in `receipts/` and a gate that exits zero, or the milestone is not done.

- **M0 · The kernel boots.** Pins; the AppContainer launch with the card measured inside it; the sandbox mechanism on the header row; spools with the seven-field frame and STRICT escaping; the ring and the cursor; the tape with canonical JSON and the keyed chain; the ledger with the pinned layout and the stamp slots; `verify`; `about`. No model. Gate: F-LAYOUT, F-FRAME, F-CHAIN, F-CONSERVE without the heard bucket, F-REPLAY, F-DETERMINISM, F-PIN, F-EGRESS.
- **M1 · The judge.** v11 with its serve bytes byte-identical; the seat-to-role map; forks with `kv_unified`; quantized margins and the tie band; the seam and the writ with its signature; the floor and the twin in shadow; the switch; the budget passes. Gate: the planted battery; F-INERT, F-INERT-BYTES, F-BLIND, F-QUANTA, F-BUDGET, F-SILENCE, F-RESIDENT, F-RIPEN.
- **M2 · The extractor and the first lane.** The mailbox lane pulling as §4 says; structured maps for calendar and books; derived obligations with witnesses and standing; the ninety-day replay in shadow before any live frame; bars, bands, stratum and canary rates pinned before the first shadow row of a class is folded. Gate: F-EXTRACT, F-STANDING, F-CONSERVE full.
- **M3 · The hand.** The launcher's process tree; the pipe; the effect registry with five classes; the outbox with the release round trip and presence gating; the egress ledger covering producers; FACTOR's own address; the day-one acceptance: replay ninety days, every reversible discharge drafted and staged, the books reconciled, one class asked. Gate: F-WINDOW, F-ORDER, F-EGRESS full, the day-one receipt.
- **M4 · The ladder.** Grades with exogenous outcomes and the person's arm; the expectation fold; the two processes and the detector; the license fold with the monotone law; the stratum and its salt; the canary at rung 2; the console's `answered` and `ratify` rows; expiry. Gate: F-MONOTONE, F-BOTH-SIDES, F-WITNESS, F-PREDICT, F-DETECT, F-EXPIRY, F-CANARY, F-COVERED, F-SALT, F-TERMINAL.
- **M5 · The jury and the cap.** Families; role separation; digest binding; the cap provider with a restricted key; aggregate caps; the first-payee rule. Gate: F-JURY, F-FAMILY, F-CAP.
- **M6 · The folds.** Fronts; the contradiction index with both heads; kappa on measured baselines; the negative-space fold; the account with the number fence and the external witness. Gate: F-FRONT, F-CONTRADICT, F-DEGRADE, F-DARK, F-REDACT.
- **M7 · The compiler, the grower, rollback, the molt.** Gate: F-COMPILE, F-ROLLBACK, F-ROLLBACK-MONOTONE, F-MOLT, F-TICK.
- **M8 · Organs and surfaces.** The organ contract with network declarations; the tape of tapes; the stdio organ surface; the API's narrowing-only writes; the watchdog. Gate: an absent organ degrades with code 6 and the account says which; an organ child that opens a socket is refused; a widening ratify over the API is refused.
- **M9 · The tune.** `epoch`; goldens from the tape; the pin tuple; lineages; deployment as a widening. Gate: a regressing version refuses to load; F-OBSERVE's arm reports; the transfer bet's bar is printed.

---

## 23 · Layout

**The repository**

```
C:\FACTOR\
  BLUEPRINT.md            v0.1, amended by dated entries only
  BLUEPRINT_v0.2.md       this file, the design of record
  qc\                     the reviewer files and the synthesis
  launcher\               the sandbox launch; spawns the kernel, the hand, and read organs
  kernel\                 the judge, the ledger, the seam, the tape, the folds; one static binary
  hand\                   the valve, the outbox, the registry, the cap credential, effector organs
  console\                the operator's surface and key use
  lanes\                  producers: mail, mail-factor, calendar, files, books, chat, screen, console, self, health
  organs\                 adapters to organs at fixed paths; the contract and its conformance battery
  writ\                   the writ schema, the validator, examples, the class table
  tests\                  the falsifiers, each with its planted lie
  tools\                  verify, epoch, rollback, doctor, twin, spool-seal
  receipts\               dated receipts per milestone
```

**A FACTOR home**

```
<home>\
  writ.toml  writ.sig  writ.seq        the operator's; hashed on every header row
  switch  switch.sig  switch.seq       off | shadow | live | stop
  keys\                               the sealed machine secret; never the operator key
  weights\                            the weights file the pin names; a home without it boots the twin
  spools\<lane>\gen-000001.spool      per lane, per generation, self-chained
  spools\<lane>\cursor                the ingested offset, its chain value, the window length
  spools\<lane>\manifest.json         generation heads
  tape\seg-000001.jsonl               the record, keyed chain across segments, sealed
  tape\manifest.json                  a cache
  ledger\                             the state fold, memory-mapped, two stamp slots
  folds\                              grades, license, kappa, fronts, contradictions, routines, wants, stamped
  dossier\                            per-obligation side store, chained, per-party subkeys
  trunk\                              checkpoints, each a directory with a manifest
  outbox\                             the hand's private state; not an interface
  accounts\                           the weekly, signed
  heartbeat.json                      the pill; staleness past three beats is STALLED, fail loud
```

---

## 24 · Bets and open questions

- **[BET] The disposition transfers.** A restraint-tuned judge from the utterance radius judges obligations at parity or better after the first epoch, reproducing a flood cut of the order the family measured. Kill: shadow agreement in no band predicts outcome accuracy after ninety days.
- **[BET] Derived obligations are stable enough to license.** Kill: the extraction falsifier's recovery is below tolerance on real mail after the extractor's second version.
- **[BET] The person is a usable prior.** Kill: outcome-scored accuracy in a band does not correlate with shadow agreement in that band; then the brief returns as the mechanism.
- **[BET] Deskilling does not outrun the stratum.** Kill: kappa in a graduated class rises after graduation and no stratum size holds it under one; then the class reverts to rung 1 and graduation was a trap.
- **[BET] Observation does not poison the label.** Kill: F-OBSERVE's arm shows shadow agreement moving with awareness of the shadow; then calibration is replay-only.
- **[BET] Provenance families are independent.** Kill: on the stratum the two juror families err on the same instants above a pinned rate; then the jury degrades to a person's signature for that class.
- **[BET] Inverses restore.** Kill: a `reversed` row whose outcome shows the counterparty acted on the write; then the effect type is re-registered as windowed or irreversible the same day.
- **[BET] Compilation covers most of the mass.** Kill: fewer than half of licensed discharges in the first three wires are explained by a deterministic function after two hundred instances.
- **[OPEN] The exploration tax.** The canary, stratum, uniform and lottery rates have no receipt anywhere in the estate. They are the one set of numbers this program cannot borrow.
- **[OPEN] CUDA inside the container.** Measured at M0 on this box; the fallback is layered and the header says which stands.
- **[OPEN] The front detector's parameters,** per class, from the shadow tape.
- **[OPEN] The pressure field.** Deferred, because at one seat with a 44 ms probe everything can be shadowed and the ranking's real job is rationing asks and consults, which the budget passes do. Add it only when the walk is measured to miss ripeness.
- **[OPEN] A remote frame buffer** for a closed laptop: frames only, no judgment, egress printed. The vendor pull paths in §4 cover mail and calendar without it.
- **[OPEN] The captured-corpus kill** on the tune, and which instrument detects it first.
- **[OPEN] Whether two local judges from different vendors are independent enough to count as two families;** F-FAMILY measures it.

---

## 25 · Provenance of this revision

v0.2 was produced from seven reviews of v0.1 on 2026-09-08. Their reports and the adjudication ledger are in `qc/`. Where a reviewer supplied spec text, it was used with light editing; where reviewers disagreed, the synthesis says who won and why. The measured numbers in §19 are named with what they were taken on; none was taken on FACTOR. Nothing in this file is a measurement of FACTOR.

---

*Amendments are dated entries appended below this line. The file above is never edited in place.*

---

## Amendment 1 · 2026-09-08 · After the test scaffold was re-cut against this file

Source: `qc/O6_tests_v0.2.md`. The §5 record measures 128 bytes with no implicit padding on ctypes, MSVC and g++, and the frame, chain and canonical-JSON models pass with all planted lies caught; those parts of this file stand. Thirty-one underspecifications were found. Each is settled below; where a settlement changes a format, the affected test is named. Numbers refer to O6 §6.

**§5 · The record**

1. **The id hash.** `BLAKE2b-64` means BLAKE2b with `digest_size = 8`, which mixes the length into the parameter block and is not a truncation of the 256-bit digest. Unkeyed, because the extractor must mint the same id for the same claim on any machine that holds the same spools, and because keying would not stop an attacker who can send the same claim text. Collision stays `fatal`.
2. **The amount scale.** `amount_fix` is an integer count of micro-units, one millionth of `unit`, not 1/65536. A cent is exactly 10,000. Range ±9.2 trillion units. Rounding is round-half-even to the micro-unit, applied once at ingest, and the canonical claim hashes the micro-unit integer. Caps are compared in micro-units. The §5 comment and `check_layout.py`'s informational block change accordingly; the layout does not.
3. **Units.** `unit` values below 1000 are ISO 4217 numeric codes; the writ's `unit = "USD"` is mapped through the pinned ISO table to 840. Interned non-money codes live at 1000 and above in the class table; the validator refuses an interned code below 1000.
4. **The class table.** `writ.classes` is an append-only file beside the writ, signed with it, mapping class name to number. A number is never reused; a class the writ deletes keeps its number and is marked retired. An edit to the writ never renumbers a record.
5. **The seqlock.** The writer increments `seq` with release ordering before and after the mutation; the reader loads `seq` with acquire ordering before and after its copy. A reader that fails 64 retries reports `contended` and reads the tape instead. `seq` wrapping is harmless; only parity and equality are compared.
6. **Saturation.** Margins saturate at ±32767 and set flag bit 13, `SATURATED`, which the gate treats as a positive guard margin. The `uint16` counters saturate at 65535 and never wrap.
7. **The hot walk** touches both cache lines and the 5 ms readout budget assumes it. If the budget is missed, `cls`, `state` and `band` move onto line 0 beside `due_ns` by a versioned header change, not a silent edit.

**§4 · Lanes and the spool**

8. **The frame gains an eighth field.** `t_mono_ns · venue · lane · grain · rev · f · text · h`, where `f` is a small integer of frame flags: bit 0 `badenc`, bit 1 `truncated`, bit 2 `synthetic_rev`. The mark now has a home on the frame itself, which replay needs. `frame_roundtrip.py` moves to eight fields.
9. **`\xNN` semantics.** `NN ≤ 0x7F` names a code point; `NN ≥ 0x80` names a raw byte and is legal only on a frame with `badenc` set.
10. **`u64le(len)`** is the byte length of the body: fields one through seven with their tabs, escaped, excluding the tab before `h`, `h` itself, and the terminating newline.
11. **Spool personalization.** The spool chain is unkeyed and personalized with `FCTR-spool-v1`, so an unkeyed BLAKE2b elsewhere cannot verify as a spool line.
12. **The cursor's window** bounds a backwards re-read that recovers the frame at the cursor and its predecessor, so the chain value is recomputed in O(window) rather than O(file). A window shorter than two lines is refused. The cursor is `(generation, offset, h, window_len)`.
13. **The header** obeys §12's canonical JSON rules, integers as decimal strings included.
14. **Every field is capped:** `venue`, `lane` and `grain` at 64 encoded bytes, `text` at the header's cap. A line therefore has a bound.

**§12 · The tape**

15. **Personalization strings** are at most sixteen bytes and pinned: `FCTR-tape-v1`, `FCTR-dossier-v1`, `FCTR-ledger-v1`, `FCTR-ckpt-v1`, `FCTR-spool-v1`, `FCTR-fprint-v1`. The template in §12 that produced a seventeen-byte string is withdrawn.
16. **`ms`** is a key on the row object that the hashed body excludes; it is not a sidecar.
17. **64-bit fields as strings** is decided by declared width: every field declared 64-bit, `amount_fix`, `t_mono_ns`, `rev`, and every id, is a decimal string; `int16` margins and small counters are numbers.
18. **The torn tail is unfalsifiable by construction.** A valid last row whose hash fails is indistinguishable from a forged tail an attacker wants dropped; the verifier accepts the earlier head either way, and that is why the head has two witnesses. §12's torn rule now says so where it is stated. A complete row whose newline never reached the disk stays torn and does not advance the head. A broken link in the last position is a forgery, not a tear, and is `fatal`.
19. **The fingerprint chain**, which `verify --chain-only` verifies, is defined: at every segment close and every 4,096 rows the kernel writes a `fingerprint` row carrying the keyed head, the segment number and the row index; the fingerprints form their own unkeyed chain under `FCTR-fprint-v1`; the console publishes each fingerprint to the external witness; `--chain-only` verifies the fingerprint chain's internal consistency and its agreement with the witness's copy, and never recomputes a keyed `h`.
20. **Compaction** replaces a span with a signed `tombstone` row carrying the span's first `prev`, last `h`, row count and the operator's signature; the verifier accepts the tombstone as the link. Without it compaction would un-verify the tape.
21. **One kind list.** §12's list is the enum; it gains `expired`, `lapsed`, `graduated`, `demoted`, `terminal`, `repeat`, `fingerprint`, `tombstone`, `restart`. §8's events `compiled` and `grown` are the kinds `compile` and `grow`.
22. **The segment bound** is 64 MiB, checked before the append.
23. **The machine secret** is the value the TPM unseals, bound to the boot state and the kernel binary's hash. On a kernel upgrade, `factor reseal`, operator-signed, re-seals the same secret to the new binary's hash, so existing segments and keys survive. A secret that cannot be unsealed makes the tape verify-only until it is.

**§21 · Falsifiers**

24. Forty-five rows, and the brief that said forty-six was wrong. Two rows are added for the M8 gate, making forty-seven: **F-ORGAN-DEGRADE**, an absent organ degrades with code 6 and the account names it, planted lie a crash; **F-ORGAN-NET**, an organ child that opens a socket is refused by the sandbox, planted lie a declaration trusted without confinement. F-SELF is gated at M1, where the `health` lane ships.
25. **F-EGRESS at M0** is the three OS-refusal routes and the process-tree socket sample; the ledger sum joins at M3.
26. **Thresholds** named in the table, `n0`, the dark-quota period, `self_share`, the extraction tolerance, the tie band, and F-DETECT's 500 and 40, are declared in the writ's `[test]`, `[walk]` and class stanzas and printed on the account; a falsifier reads them from the writ it runs under.
27. **The law column**: a bare number is a clause of §1; a section reference is the section that states the property.

Files changed by this amendment: none in place. `frame_roundtrip.py` and `chain_check.py` are to be re-cut for the eighth field and the pinned personalization strings; `check_layout.py` for the micro-unit scale. The record layout is unchanged.

---

## Amendment 2 · 2026-09-08 · The sandbox law, measured

Source: `receipts/M0_SANDBOX_PROBE_2026-09-08.md`. §11's open question is closed on this machine, an RTX 4070 Ti SUPER on Windows 11 Pro 26100, with no administrator elevation and no installer.

- **Mechanism in force: `os-enforced`.** A zero-capability AppContainer profile created and applied by a launcher, with `PROCESS_CREATION_CHILD_PROCESS_RESTRICTED`, refuses the child's outbound socket with `WSAEACCES` (10013) and a live loopback connect with `WSAETIMEDOUT` (10060). The control outside the container connects. The fallback of a restricted token with an administrator-installed filter was not needed and was not exercised.
- **The pipe.** A named pipe created with `FILE_FLAG_FIRST_PIPE_INSTANCE` and `PIPE_REJECT_REMOTE_CLIENTS` whose descriptor names the package SID echoes from inside the container; a pipe with the default descriptor is refused with error 5. §11's pipe text stands as written.
- **The card.** `nvcuda.dll` loads, `cuInit`, context creation, a 64 MiB allocation and a host-device round trip succeed inside the container, and llama.cpp runs Qwen3 1.7B fully offloaded inside at 281.6 tokens per second against 279.4 outside, within noise. The GPU stack required no access grants of its own; the only grants were on FACTOR's binary, its DLL directory, the weights file and the output directory. §7's "measured at M0" clause is satisfied.
- **One residual, carried into F-EGRESS.** `NtCreateFile` on `\Device\Afd\Endpoint` opens inside the container while the raw `\Device\Afd` open is denied with `0xC0000022`. Opening the endpoint is not egress; the connect IOCTL meets the same package-keyed filter that refused the socket library. The probe did not drive the full connect IOCTL, so that route is established by inference. The kernel's compiled-in F-EGRESS probe must drive the `AFD_CONNECT` IOCTL itself and observe the refusal; until it does, the M0 receipt says `afd: inferred`.
- **Hygiene.** The profile was deleted and every granted access entry revoked, with zero residual entries on the five paths and nothing left under the packages directory. The launcher at M0 must do the same on every exit path, and a profile left behind is a `warn` on the next boot.

§11's paragraph "The sandbox" is read with this amendment: the phrase "is measured at M0" is now "was measured at M0, receipt above", and the layered fallback remains in the text for a machine where the measurement comes out differently.

---

## Amendment 3 · 2026-09-08 · Two findings from the re-cut tests

Source: `qc/O7_tests_amend1.md`. The eight-field frame, the pinned personalization strings, the fingerprint chain, the tombstone and the micro-unit scale all pass with every planted lie caught; the scaffold stands at forty-seven falsifiers. Two measured findings remain and are settled here.

1. **Amounts are parsed as decimal text.** Amendment 1 pinned round-half-even to the micro-unit but not the parse before it, and three of five tie cases land on different integers depending on whether the text passed through a binary double first. Since the micro-unit integer is hashed into a derived obligation's id, the parse is identity-bearing. Rule: an amount is parsed from its text as a decimal by digit arithmetic, scaled to micro-units, and rounded half-even on the decimal representation; a binary floating-point value never touches an amount anywhere in the kernel, the maps or the extractor. `check_layout.py`'s tie cases become the falsifier's fixtures, with the planted lie a parser that goes through a double.
2. **Compaction never removes a fingerprint row.** A tombstone may replace only rows strictly between two fingerprints; the fingerprints bounding the span stay on the tape, so the keyed chain and the fingerprint chain both verify after a lawful compaction and a keyless verifier cannot mistake it for a forgery. The tombstone itself is fingerprinted at the next interval. `chain_check.py`'s compaction test adds the case that motivated this: a span containing a fingerprint row must be refused by `factor compact`.

---

## Amendment 4 · 2026-09-08 · Amendment 3 made implementable

Source: `qc/O8_tests_amend3.md`, which folded Amendment 3 into the harnesses, proved both rules against nine negative controls, and listed thirteen things an implementer would still have to invent. Each is settled here. One settlement changes §5's identity rule and is marked.

**The amount**

1. **Grammar.** An amount text is an optional ASCII minus, one or more ASCII digits, and optionally an ASCII period followed by one or more ASCII digits. Nothing else: no plus, no exponent, no grouping separator, no surrounding space, no bare `.5`, no trailing `1.`, and no digit outside ASCII, because runtimes that accept Unicode digits give one amount two spellings. Anything else is a refused amount with the typed reason on a `refused` row.
2. **Rounding is on the whole discarded tail.** The phrase "at the seventh decimal place" in Amendment 3 is withdrawn. A discarded tail is a tie only when it is exactly a five followed by nothing but zeros; a tie rounds to the even micro-unit; anything else rounds by its value. Fixture 13 in `check_layout.py` is the case that separates the two readings.
3. **The parse is the ingest rounding, and it happens once.** No map, fold, cap comparison or serialization re-rounds an amount. F-REPLAY catches a second rounding, because the record's digest would move.
4. **Range.** A text whose micro-unit value does not fit `int64` is refused with a typed reason, never saturated, because a saturated amount would understate a cap breach silently. Saturation is for margins and counters only.
5. **Where the law binds.** The no-float rule binds the kernel, the maps, the extractor, the hand's cap comparison and every serialization. In the kernel the amount is a distinct integer type with no conversion to or from a floating-point type, so a float touching an amount fails to compile. Surfaces that only display an amount format it from the integer by decimal arithmetic too, since that is no harder.
6. **A source that supplies a number rather than text.** A producer's JSON reader carries the number's lexeme as text and never converts it; the lexeme is the amount text. A map over a source column stored as a binary float declares that column's `precision`, the producer formats the value at that precision, the frame carries flag bit 3, `lossy_amount`, and the record carries flag bit 14, `AMOUNT_LOSSY`. A lossy amount is compared against caps as written and the account counts lossy amounts per class, because a source that cannot state its own amounts exactly is a finding about the source.
7. **[§5 identity, changed] The derived id no longer hashes the amount.** A derived obligation's id is BLAKE2b-64 over party, kind, due, and the normalized statement. The amount is an attribute on the record and in the dossier, not identity. Two promises that differ only in amount differ in their statement text as well, so nothing is lost, and the parse stops being identity-bearing. The parse remains a law for the reasons above: the record's digest, the caps, and replay. Amendment 3's fixtures stay where O8 put them, as F-EXTRACT's and F-REPLAY's.

**Compaction**

8. **The verifier holds the rule, not only the writer.** `factor verify` and `factor verify --chain-only` both refuse a tape whose tombstone is not bracketed by a fingerprint on each side, or whose span removed a fingerprint. The writer's refusal is hygiene; the verifier's refusal is the law, because the one adversary compaction has is a holder of the operator key.
9. **The fingerprint body is pinned:** `{head, seg, row_orig}`, where `row_orig` is the row's index on the uncompacted tape. Compaction never renumbers. A verifier reconstructs position from `row_orig` by subtracting the counts of the tombstones before it, and a lawful compaction therefore changes nothing a fingerprint attests.
10. **A compaction is followed by a fingerprint at once,** before the tape is published, replicated or read by anyone but the compactor, in addition to the ordinary cadence. A tape is never published with an unfingerprinted tombstone.
11. **Tombstones are protected rows.** A span containing a tombstone is refused with the reason `contains-tombstone`, exactly as one containing a fingerprint is, so a second compaction can never erase the audit of the first.
12. **The operator's signature on a tombstone covers** the span's first `prev`, its last `h`, its count, and the heads of the two bracketing fingerprints, so the operator attests that the span was lawful and not only that it was removed.
13. **The witness's copy has a form:** one line per fingerprint, the fingerprint row's canonical JSON with the console's signature over it. Any store that can append and cannot rewrite qualifies as a witness: a transparency log, a second machine, the operator's device.

`chain_check.py` gains `contains-tombstone`, the bracket check in `verify` as well as in `--chain-only`, the pinned fingerprint body, and the signature over the bracketing heads; `check_layout.py` gains the range refusal and the lossy flag; the derived-id fixture in `F_EXTRACT.py` drops the amount from the canonical claim. Those are the next harness pass.

---

## Amendment 5 · 2026-09-08 · What TAPESTRY's QC found that FACTOR also had

Source: the TAPESTRY fork's seven-reviewer QC and its synthesis, `C:\TAPESTRY\qc\QC-SYNTHESIS_DECISIONS_v0.1-to-v0.2_2026-09-08_FABLE5-1.md`, read as relayed by the operator. Most of its findings FACTOR's own QC had already closed: the durable clock, the seam as a component, the 128-byte row, reversibility derived from the map, the jury bound to effect bytes, no floats, the socketless judge. Ten did not have a home here, or exposed a sentence of FACTOR's that was false. Each is settled below.

1. **The tape's durability primitive.** §12 never said it. A row that gates an effect is durable, `FlushFileBuffers` on its segment, before the hand releases that effect; rows that gate nothing are group-committed at the tick or at 4,096 rows, whichever first; the account prints the commit latency p99 against a budget, and no throughput target is stated, because a throughput target on the one thing that must never be dropped invites dropping it.
2. **Fork cost on a recurrent hybrid is paid per slot at context creation, not at fork.** §7's "deferred, not absent" is corrected: llama.cpp preallocates the recurrent state for every sequence slot when the context is created, 52.7 MB per slot on the 9B hybrid, and the fork-at-zero receipt reconciles with that only because the slot already existed. `n_seq_max` is pinned in the writ's `[kernel]` stanza, its recurrent state is a line in the VRAM budget of §19, and the number of concurrent forks is bounded by it. On a 16 GB card that is a few dozen slots, which is enough for one seat and is the reason it is enough.
3. **[OPEN, shared with TAPESTRY] The judge's architecture.** A recurrent hybrid with per-slot state and a sequence cap, against an attention-only judge with paged prefix caching, measured on this card before M1's tune and before TAPESTRY's R3, because the answer moves every sizing number by an order of magnitude and both designs borrow the same constant. One measurement serves both.
4. **LOOK, FETCH and CONSULT are bounded and graded.** A judge that keeps looking never acts and is never graded, which is the silent death with a receipt. Per obligation and revision, at most `look_max` LOOK or FETCH verbs and one CONSULT, `look_max` in the writ, default two; past the bound the verb is HOLD (thin-evidence) or ASK. At the obligation's horizon an obligation that was only looked at is graded as a hold.
5. **Delivery is at-least-once with an idempotency key the hand can recompute.** The key of a staged effect is the hash of its `staged` row; the hand persists it beside the effect in its private outbox; after a crash the hand rebuilds pending effects from the tape's `staged` rows and its own log, never re-sends one whose `executed` receipt is on the tape, and a duplicate key is refused and counted. The inverse of a sent message inside its window is the withheld send; outside the window it is a retraction or a compensation, never an undo, and the registry says which per effect type.
6. **The revision hierarchy for sources without a log sequence number.** A synthetic per-lane counter minted at append is the last resort, because a stale source row appended late receives a higher counter and overwrites. Order of preference, declared per map: the source's own log sequence number; a source-side modification stamp the map names as the revision column, compared only within that source and table; the synthetic counter, with the map saying so and the account counting the lane as `revision: synthetic`.
7. **Juror families are declared only in the signed writ.** The kernel cannot add, rename or merge a family; a family absent from the writ is not a juror; the writ's `[jury]` stanza carries each family's tuple and its key or endpoint, so quorum is not sybil-able from inside the box.
8. **Fork identity is content-addressed.** A fork's cache key is the hash of the rendered context bytes, the dossier, the neighbourhood and the precedents as rendered under the template pin, plus the judge pin, rather than the obligation id and revision alone, because the rendered context changes when a neighbour changes and the id does not. A fork whose rendered bytes are unchanged is reused; one whose bytes changed is rebuilt.
9. **Fold-emitted rows are outputs, re-derivable.** `grade`, `license`, `front`, `expect` and `fingerprint` rows are written by folds onto the tape, stamped with the head they were computed from; a replay recomputes them and `factor verify` compares. A fold reads earlier rows only, so a fold's own outputs never feed its inputs at the same head.
10. **Kappa at rung 1 is a forecast from shadow, so demotion is not absorbing.** A demoted class handles nothing, so its removed side is zero; kappa for a class at rung 1 is computed from its shadow rows, would-have-handled instances times the baseline against the stratum's review minutes, printed `forecast`, so the class can re-earn under the same number it was demoted under.

**One sentence of the synthesis corrected.** `qc/QC_SYNTHESIS_2026-09-08.md` §2 says the family's `verify_chain.py` keeps working on FACTOR's tape. It does not: FACTOR's chain is keyed, length-prefixed and computed over a canonical body, and only `factor verify` verifies it; the keyless mode verifies the fingerprint chain. What FACTOR shares with the family is the hash function, not the construction. The synthesis stands as written and this line is the correction beside it.

---

## Amendment 6 · 2026-09-08 · After the Amendment 4 harness pass

Source: `qc/O9_tests_amend4.md`. All thirteen items of Amendment 4 are now checks, green, with eighteen negative controls. Eleven ambiguities remain and are settled here. This is the last amendment written from a desk; what follows it is settled by a binary at M0.

**The amount**

1. **Canonical spelling.** An amount text with a leading zero before another digit is refused with reason `grammar`; the only lawful forms are those §12's canonical decimal already accepts. The claim text then has one spelling.
2. **A length bound before the arithmetic.** An amount text longer than 40 bytes is refused before any digit is read, since the widest lawful value is 26 bytes. The extractor's boundary is other people's bytes and it never builds an integer it has not bounded.
3. **A refused amount and the claim.** The obligation is minted without an amount: `amount_fix` is zero, flag bit 15, `AMOUNT_ABSENT`, is set, the `refused` row names the text and the reason, and an obligation with an absent amount is never compared against a cap as zero; for the cap it is treated as exceeding every cap, so it asks.
4. **"Per class" means the record's `cls`.** Lossy and absent amounts are counted per class on the account.
5. **Precision and the single rounding.** A map's declared precision is 0 to 6. When the producer formats at a precision below 6, the producer's formatting is the single rounding and the parser rounds nothing; the frame's `lossy_amount` bit records that the rounding happened upstream. A formatted text that leaves the range is refused by the parser as any text is, and the producer counts it.
6. **The flag map, published.** `flags` bits: 0 OWED_BY_ME · 1 OWED_TO_ME · 2 IRREVERSIBLE · 3 EXOGENOUS · 4 BLOCKED · 5 NEEDS_WORDS · 6 SHADOW · 7 CANARY · 8 PINNED · 9 COMPILED · 10 JURIED · 11 UNTRUSTED_ORIGIN · 12 DEGRADED · 13 SATURATED · 14 AMOUNT_LOSSY · 15 AMOUNT_ABSENT. Frame `f` bits: 0 badenc · 1 truncated · 2 synthetic_rev · 3 lossy_amount. No bit is free; a new flag is a header version.

**Compaction**

7. **Item 10 in a checkable form.** The last fingerprint on a published tape must carry a `row_orig` greater than the original index of every tombstone's last replaced row. A tape that fails this was published with a compaction no fingerprint attests, whether the compactor waited for the cadence or not.
8. **The bracketing heads are fields on the tombstone row,** inside its hashed body and inside the operator's signature, so a tombstone is checkable in isolation and a verifier never recomputes them from the tape.
9. **`fp_after` and `span_h` are two fields** even when they coincide, which is the common case; a verifier compares each to its own source and never derives one from the other.
10. **Per-segment verification.** Every segment header carries the cumulative tombstone count and the `row_orig` of its first row, so a verifier handed one segment reconstructs positions without the rest of the tape. A compaction never crosses a segment boundary; a span that would is refused with reason `crosses-segment`.
11. **Reason precedence and the witness.** When a span holds both, `contains-fingerprint` is reported before `contains-tombstone`, and both before `unbracketed`. The witness receives tombstone rows as well as fingerprint rows, each as its canonical JSON with the console's signature, so it can bound a compaction and see its count. The console's signing key is named in the signed writ, which is how a verifier comes to hold it.

The harness pass for this amendment is deferred to M0, where `factor verify` and `factor compact` are binaries and these rules are tested against them rather than against a model.
