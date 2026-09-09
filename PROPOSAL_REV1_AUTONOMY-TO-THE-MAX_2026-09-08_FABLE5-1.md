# FACTOR REV 1 · autonomy to the max

*2026-09-08 · Claude Fable 5.1 · a proposal against `BLUEPRINT_v0.2.md` with its six amendments. Read for this: §0 to §2, §10, §13 to §18, §22 to §24, `NEXT.md`, and the tree. Nothing here edits the blueprint. Everything here is written so it can be appended as dated amendments after a QC pass. A copy sits in `C:\FACTOR` as `PROPOSAL_REV1_AUTONOMY-TO-THE-MAX_2026-09-08_FABLE5-1.md`.*

## 0 · What "exude autonomy" has to mean, operationally

Autonomy is not a register a repository writes in. It is two things a repository can be checked for. First, a set of loops that close with nobody in them, each with a falsifier and a planted lie. Second, a set of numbers the system prints about itself every week without being asked, each with a denominator and the hash of the fold that produced it. A repository exudes autonomy when its front page is those numbers, its tree is mostly generated from a tape, and the only files a person writes are the writ and the receipts.

v0.2 already specifies most of the loops. Read against the one design, it lacks five things, and they are the proposal:

1. **A planner.** v0.2 reacts. It judges at boundaries and re-projects ripeness against the clock, but nothing forecasts an obligation's path, so holds are graded late and the walk cannot anticipate. The one design's org solver at one seat is a small event model over the seat's own typed tape, with a deterministic null it must beat.
2. **A visible veto.** The seam is a paragraph inside the kernel beside the judge. The one design says the gate is the veto and nothing learned may occupy it. That should be a link-time fact you can point at, not a sentence.
3. **Standing rules.** Every routine, every grown adapter, and every new judge version still waits for a per-artifact yes. Law 6 already allows widening inside a ratified rule to be written by outcomes. Extend the rule form to compile, graft and epoch, and three signatures replace hundreds.
4. **A lane on its own build.** The repository does not run the loop it describes. Its stubs, amendments, gates and open questions are obligations with deadlines and discharge predicates in the record, and nothing folds them.
5. **The week with nobody home.** The closure test the tape wrote in prose, unplug the person for a week, has no falsifier. It should be the flagship test, with a number.

Everything else below is consequence: the tree, the meters, the milestones, the constitution edits, and what not to do.

## 1 · The five structural changes

### 1.1 The planner: an event model over the seat's own tape, with a null it must beat

**What it is.** A small model inside the kernel process that reads the tape at commit grain as a sequence of typed tokens and forecasts what happens next per obligation. The vocabulary is the class table plus the event kinds plus banded fields: `open(cls, party band, amount band, deadline band)`, every verb row with its rung and seat, `draft`, `staged`, `executed`, `reversed`, `unsaid`, `asked`, `answered`, every outcome kind, `expired`, the person's own discharges with `seat = human`, and ticks. A few hundred to a few thousand tokens. The schema is the tokenizer, as the one design says.

**What it emits, per open obligation, every period.** A distribution over the next event; the expected path to discharge as events with time bands; the entropy of that distribution; and the residual, the log-loss of what actually arrived since the last period against the previous forecast. Inference is deterministic: quantiles and argmax under a fixed seed, so replay holds. Weights are an asset pinned in the identity tuple of law 14, like the trunk.

**What it changes.**

- **Every obligation carries a forecast every period,** including held ones, with no forward pass of the prose trunk. The `expect` fold in §13 stops depending on the judge writing an `expect` field at judgment time. A hold is graded when its forecast comes due. This is the missing instrument for the hold side, and it costs microseconds.
- **Ripeness becomes forecast breach probability,** not deadline proximity alone. A quote the planner forecasts will go unanswered ripens before the deadline does.
- **The world residual becomes the world's deviation from the planner,** which is the clean residual. §13 already refuses to rank by the frame residual because prediction error on a person's writing is noise or capture. The planner's residual is over typed events with the world as the label, and it ranks.
- **Attention becomes tiered.** High entropy, an unlicensed class, or text that must be read or written: the prose trunk's forward pass. Low entropy in a licensed class: the planner's proposed verb enters the seam as a proposal, or a routine handles it. The tier share, routine against planner against judge against counsel, becomes the compression meter.
- **The compiler reads the planner.** A class whose planner distribution is near-deterministic over N instances is a compile candidate before the routines fold finds it.
- **The negative-space fold reads the planner.** An obligation forecast to breach with no scheduled verb is the first line of "not doing."

**The null.** `planner/null`: ripeness as deadline proximity, and a per-class empirical Markov chain over event kinds with time bands, fitted by counting on the tape. Deterministic, zero learned parameters, replayable, and in force from M1. The learned planner replaces it only under F-PLANNER: on the held-out tail of the tape its next-event log-loss beats the null by a ratified margin with both sides above the sample floor. If the null wins, the null stays and the account says so. This is the lattice-as-null ruling from the one design, at one seat.

**What it may never do.** Emit a verb. Its output enters the seam as a proposal beside the judge's. The masks it decodes under, the forbidden events per class from the writ and the license, are exported to it by the seam and never computed by it.

**Training.** Online between periods, on the card, minutes a week; every new version is a versioned weight event under the epoch rule of 1.4. Its held-out set is the tape's own tail, so it needs no labels and no person.

**Resolution of an open item.** §24's `[OPEN] The pressure field` closes: at one seat the field is the planner's forecast over the open set, the lattice is the planner's null at organization radius, and neither is built here.

### 1.2 The seam as a component you can point at

**Now.** The kernel owns the judge, the ledger, the seam, the folds and the tape's key in one process, and the seam is §9 of a document.

**Proposed.** `seam/` is a static library with its own hash, linked by the kernel, and it links nothing learned. Concretely: no model headers, no llama includes, no planner includes; its inputs are a proposal record with the seat margins, the planner distribution and the expectation; the license fold's row for the class and band; the reversibility class derived from the map; the obligation's flags; the budget state; and the writ's prohibitions. Its output is one verb with a typed reason and the row that will be written. The refusal order in §9 becomes `seam/order.toml`, pinned by hash, not prose. Every header row carries `seam_hash` beside the judge pin and the planner pin. The tape writer refuses a verb row whose author is not the seam hash in force.

**Why this is autonomy and not only safety.** A visible, separately hashed veto is what lets every other loop close with nobody in it. The person is not needed as a check on the learned side because the check is a component with no model in it. F-VETO makes it a fact: a build in which `seam/` includes any learned header fails to link, and a verb row authored by anything else is refused. The masks the planner and the judge decode under are produced here and flow outward, which is the one design's correction as code.

### 1.3 Fold before hand: the return arrow at rung 1

**Now.** M3 is the hand and the day-one acceptance; M4 is the ladder.

**Proposed.** Swap them. M3 becomes the ladder on shadow: the grades fold on the person's arm and on expectations coming due; the license fold with the monotone law; ratification rows; the stratum draw; kappa as a forecast; expiry; the first weekly account. All of it runs with zero effects, because at rung 1 the person is the hand and the person's discharges arrive as `seat = human` verb rows the fold already accepts. M4 becomes the hand, entering at rung 2 with the ladder already printing.

**Why.** An act is reversible only until the world reacts, and the reaction is the outcome, so a canary on a reversible class earns the person's grade and never the world's. The first rung of any deputy is therefore the draft rung, graded by the person, and the only fold that has those grades is the one this reorder builds first. By the time any effect leaves the box, every class has a graded shadow history and the first canary is ratified on a receipt rather than on the bet §24 files as its third kill. It also moves the pair, asks made of you against things handled, from M6 to M3: asks are console asks; handled is drafts the person used, measured on the screen lane's active-window time the way §13 already measures the baseline.

### 1.4 Ratify the rule, not the artifact: standing rules for compile, graft and epoch

**Now.** §14 ratifies each routine once and each grown adapter once. §18 makes every new judge version a widening that needs a ratification, and lineages never self-promote. Each is a per-artifact yes, and per-artifact yeses are the review queue in a different costume.

**Proposed.** Law 6 already says a ratification is a rule with an outcome criterion and only the rule needs a signature. Three standing rules in the writ, each a signed ratification row with a criterion and an expiry:

| rule | admits | criterion, all of | enters at | suspended by |
|---|---|---|---|---|
| **compile** | a routine for class C | reproduces N instances bit-identically on replay; declares a domain covering fraction p of the class; passes the grammar check; C at rung 3 or above with kappa below one | rung 2 for C | divergence from the judged path above rate r; a front in C; the rule's expiry |
| **graft** | a catalog producer for source S | S named in k want rows over m weeks; conformance battery passes on a recorded sample; host allowlist a subset of the writ's; scoped, expiring credentials; one period read-only shadow, diffed against any predecessor | shadow | conformance failure; egress above its declaration; expiry |
| **epoch** | a planner or judge version | beats the incumbent on the held-out tail by margin δ with both sides above n0; pin tuple minted together; goldens from the tape | rung 2 on a lineage stratum | the class e-detector; a regressing golden; expiry |

Growing an adapter, authoring new code rather than mounting catalog code, stays a proposal with a longer shadow and a byte cap, because authorship is a wider widening than grafting. Admission under any rule is a widening inside the rule and needs no further signature. Revocation is a narrowing and needs none, so the console's narrowing-only API can revoke a rule at once. The `ratify_delay_min` cancel window applies to every admission. The account prints every artifact admitted under each rule with its receipt.

**What this buys.** Three signatures, and then the compile loop, the graft loop and the tune loop close for as long as the rules stand. That is the largest single increase in autonomy available inside law 6, and it changes no law.

### 1.5 FACTOR watches FACTOR: the repo lane, and the week with nobody home

**The repo lane.** `lanes/repo` is a producer that tails the repository as a lane: file hashes and mtimes, the runner's output with the TODO count per falsifier and exit codes, amendment headers by date, receipts landing, `NEXT.md` items, open questions, milestones and their gates, QC findings. A schema map for the repository: an obligation opens when a stub exists, an amendment names a follow-up, a gate is declared, an open question is listed, or a QC finding is filed; it discharges when the test passes, the receipt lands, the follow-up is folded, or the question gets a receipt. Deadlines come from the kickoff's milestone targets.

FACTOR at rung 1 judges its own build. The planner forecasts which gates will slip. The negative-space fold prints what the build is not doing. A second account, the repository's, prints every Friday beside the seat's. Nothing acts, by law 12. Drafting is allowed, so FACTOR drafts: the next amendment from the wants fold and the QC findings, the receipt template for the next milestone, the `NEXT.md` update. Drafts land in `proposals/` and are never applied by FACTOR.

**Why this is the most important of the five.** The outcomes on this lane are real and fast. A test goes green, a receipt lands, an amendment is folded, a gate exits zero. The grades fold gets exogenous outcomes on this lane from M0, months before a mailbox outcome arrives. The repository becomes the first wire, and it is the one wire whose every outcome the operator already owns.

**The week with nobody home.** F-UNPLUG: a seven-day run, simulated clock at first and real later, with the console dark and no operator row. Invariants: every open obligation carries a standing verb every period; no class widens; expiries drop rungs on schedule; safe terminals fire at due for unlicensed past-due obligations; holds are graded by forecasts coming due; the account is written on Friday and signed by the head; the negative-space section lists what it did not do; health obligations hold, look, draft and ask and never do; no restart and no self-provision; kernel egress zero; the hand emits only licensed effects. Planted lies: a build that restarts itself; a build that widens a class on grades alone; a build that goes silent on one obligation; a build that counts a self-attested outcome. The receipt is one number, days unplugged and green, and it is the first line of the account after the pair. Gate at M4, re-run at every milestone, and run for seven real days on the operator's own seat at M10.

## 2 · Every loop, and who is in it

| loop | trigger | closes by | the person | falsifier |
|---|---|---|---|---|
| perceive, judge, verb | frames | the seam | nobody | F-SILENCE, F-RESIDENT |
| forecast, grade holds | a forecast comes due | the expect fold | nobody | F-PREDICT |
| grades, narrow | the e-detector | the license fold | nobody | F-MONOTONE, F-DETECT |
| rule, widen | outcomes inside a ratified rule | the license fold | signs the rule once | F-MONOTONE, F-RULE |
| front, narrow | CUSUM on the world residual | the fronts fold | nobody | F-FRONT |
| expiry, drop, re-earn | the clock | the license fold | nobody; re-widening past the row needs a signature | F-EXPIRY |
| negative space, experiment | idle cycles | canary proposals under the canary rate | nobody | F-DARK, F-CANARY |
| routines, compile | the routines fold and the planner | the compile rule | signs the rule once | F-COMPILE, F-RULE |
| lane fails or want, graft | a health obligation | the graft rule | signs the rule once | F-ORGAN-DEGRADE, F-RULE |
| graded tape, epoch, lineage | tape depth past a threshold | the epoch rule | signs the rule once | F-PIN, F-RULE |
| health | the pill | hold, look, draft, ask; never do | signs any effect on the substrate | F-SELF |
| wants, proposal | weekly | a draft in `proposals/` | reads it; ratifies or not | F-SELF-DRAFT |
| the account | Friday | the account fold | nobody | F-REDACT, F-STATUS |
| rollback | an operator row | every fold, from its stamp | signs | F-ROLLBACK |
| irreversible effect | DO on an irreversible class | the jury and the cap | signs only where the law reserves it | F-JURY, F-CAP |
| the build | the repo lane | shadow and drafts | the only hand | F-REPO |

Sixteen loops. Thirteen close with nobody in them. Three take one signature each, once, on a rule with an expiry. Two take a signature per instance, and both are there because the law puts them there, not the design.

## 3 · The repository, REV 1

```
C:\FACTOR\
  writ\              AUTHORED   the top: writ.toml, the class table, the rates, the three standing rules, the validator
  seam\              CODE       the veto: one static library, no learned header, its own hash on every header row
  judge\             CODE       the prose trunk: seats, forks, serve bytes, the pin
  planner\           CODE       null\ (ripeness + Markov, in force from M1) · model\ (weights, the epoch harness)
  kernel\            CODE       the resident process: clock, walk, ledger, folds, tape writer; links seam, judge, planner
  hand\              CODE       the valve, the outbox, the registry, the cap, the egress ledger, effector organs
  console\           CODE       asks, the account, the writ, the switch; nothing else
  lanes\             CODE       producers: mail, calendar, files, books, chat, screen, console, self, health, repo
  organs\            CODE       read organs at fixed paths, the contract, the conformance battery
  routines\          GENERATED  compiled classes, each with its replay receipt, its domain, and the rule that admitted it
  adapters\          GENERATED  grafted producers, each with its conformance receipt, its allowlist, and its expiry
  proposals\         GENERATED  drafts FACTOR wrote: amendments, NEXT, adapters to grow; never applied by FACTOR
  folds\             GENERATED  grades, license, kappa, fronts, contradictions, routines, wants, negative space, stamped
  accounts\          GENERATED  the seat's weekly and the repository's weekly, signed by the head
  receipts\          AUTHORED   dated receipts per milestone and per autonomy claim
  tests\             CODE       falsifiers with planted lies, plus F-UNPLUG, F-VETO, F-PLANNER, F-GRAIN, F-RULE, F-REPO, F-STATUS, F-SELF-DRAFT, F-TIER
  tools\             CODE       verify, epoch, rollback, doctor, twin, spool-seal, status
  STATUS.md          GENERATED  the meters, written by `factor status`; a fold, so two runs are byte-identical
  BLUEPRINT_v0.2.md  AUTHORED   amended by dated entries only
  qc\                AUTHORED
```

Three kinds of file, and the tree says which is which. Authored: the writ, the blueprint, the kickoff, the receipts. Generated: every fold, every account, every routine, every adapter, every proposal, and the status page. Code: the rest. A generated file is never edited by hand, and F-STATUS proves it: regenerating any generated file from the tape reproduces it byte for byte. A person reading the tree sees a tape, its folds, a writ on top, and a small amount of code between them, which is what the system is.

**STATUS.md** is the front page and it is an instrument. Line one: the pair for this week. Line two: days unplugged and green. Then the meters table of §4, the per-class rung table, the tier histogram, the last externally witnessed head, and the "not doing" section verbatim from the account. It carries no prose a person wrote.

## 4 · The meters

Every number carries its grain, its denominator, and the hash of the fold that produced it, under v0.2's number fence. A number lacking any of the three is not printed.

| meter | definition | grain | should move |
|---|---|---|---|
| the pair | asks made of you against things handled | weekly | apart |
| days unplugged and green | consecutive days with no operator row and every F-UNPLUG invariant holding | running | up |
| unattended fraction | discharges at rung 3 or above over all discharges | per class, weekly | up |
| unattended error | outcome-graded error of what ran unattended | per class, at the horizon | flat or down; printed beside every handled count |
| tier share | routine, planner, judge, counsel, as shares of judgments | weekly | model share down |
| compiled fraction | discharges by routine over all discharges | per class | up |
| asks per hundred | console asks over obligations touched | weekly | down |
| kappa | supervision created over supervision removed | per class, forecast then measured | below one |
| license coverage | classes at rung 2 or above over classes seen | weekly | up |
| re-earn rate | licenses re-earned before expiry over expiries | quarterly | up |
| forecast hit rate | planner expectations met within their band | per class | up |
| hold grade coverage | holds carrying a grade over holds | per class | up; a class below the floor cannot be promoted |
| external witness rate | outcomes witnessed outside over outcomes | weekly | up; below the floor the class is capped at rung 3 |
| lanes alive under the graft rule | adapters admitted under the rule and still passing conformance | count | up |
| proposals ratified | drafts the operator ratified over drafts | monthly | informative, never a target |
| console minutes | operator time in the console | weekly | down |

Two of these are the honest counterweights and they print beside the flattering ones by construction: unattended error beside the unattended fraction, and the "not doing" section beside days unplugged. A week with nobody home and a growing negative-space section is not autonomy; it is silence, and the page shows both.

## 5 · What the person sees

**Day one.** Connect the lanes or drop the exports. The ninety-day replay builds the ledger. The first screen is the ledger, and the second is the forecast from the null planner: what comes due in the next thirty days, what would breach if nobody acts, what the deputy would do at each rung. Every reversible discharge is drafted and staged. One class is asked. Nothing leaves.

**Week one.** The first Friday account, in shadow. The pair prints for the first time: asks made of you, small; things handled, drafts you used. Zero effects.

**Month one.** Canary rows on the first ratified class. Three signatures on three rules, compile, graft and epoch, each with an expiry. From here, routines, adapters and versions arrive on the account with their receipts and no ask.

**Month three.** The tier histogram has moved: routine and planner shares up, judge share down, counsel a sliver. The console was opened twice a week, for asks and the account. Days unplugged and green reads in the tens.

The console is the absence of a user interface. It shows asks, the account, the writ and the switch. Its minutes per week are a meter that should fall. Anything else a person wants to look at is a fold they can open, and the design goal is that they do not need to.

## 6 · New falsifiers, each with its lie

| id | claim | planted lie |
|---|---|---|
| F-UNPLUG | seven days with no operator row: standing verbs every period, no widening, expiries fire, safe terminals fire, holds graded by forecasts, the account signed, health never does, no restart, kernel egress zero | a build that restarts itself; one that widens on grades alone; one that goes silent on one obligation; one that grades a self-attested outcome |
| F-VETO | `seam/` links no learned header; the tape writer refuses a verb row not authored by the seam hash in force | a seam that includes a planner header; a verb row authored by the judge |
| F-PLANNER | the learned planner beats the null on the held-out tail by the ratified margin, both sides above the floor, or the null stays | a planner scored on the rows it trained on |
| F-GRAIN | training on commit grain predicts arrivals and outcomes at least as well as training on the full stream with the middle's artifacts | a tokenizer that leaks status rows into the commit-grain stream |
| F-RULE | an artifact admitted under a rule meets every clause of its criterion; an artifact outside the criterion is refused; a rule past its expiry admits nothing | a routine admitted with a domain below p; an admission after expiry |
| F-SELF-DRAFT | every file in `proposals/` was written by FACTOR and none was applied by FACTOR; the blueprint's hash is unchanged by any FACTOR run | a run that appends to the blueprint |
| F-REPO | the repo lane's obligations conserve: stubs, gates, follow-ups and questions each land in one obligation and discharge on the recorded predicate | a stub counted twice; a gate discharged by a failing run |
| F-STATUS | regenerating any generated file from the tape at its stamped head reproduces it byte for byte | a status page with a hand edit; a fold carrying wall time |
| F-TIER | the tier histogram's denominators reconcile with the tape's verb rows | a routine's discharges counted as the judge's |

## 7 · Milestones, reordered

| milestone | adds | gate |
|---|---|---|
| M0 | the kernel boots as before; plus `seam/` as its own library, `lanes/repo`, `STATUS.md` as a fold | the v0.2 M0 gate, plus F-VETO, F-REPO, F-STATUS |
| M1 | the judge as before; plus the null planner in force | the v0.2 M1 gate, plus the F-PLANNER harness running with the null as both arms |
| M2 | the extractor and the first lane, as before | unchanged |
| M3 | the ladder on shadow, moved up: grades on the person's arm and on forecasts, license, stratum, kappa forecast, expiry, the first account | F-MONOTONE, F-BOTH-SIDES, F-WITNESS, F-PREDICT, F-DETECT, F-EXPIRY, F-COVERED, F-SALT, F-TERMINAL |
| M4 | the hand, moved down, entering at rung 2 with the ladder printing; the canary; the first F-UNPLUG on a simulated week | F-WINDOW, F-ORDER, F-EGRESS full, F-CANARY, F-UNPLUG, the day-one receipt |
| M5 | the jury and the cap, as before | unchanged |
| M6 | the folds as before; plus the learned planner | the v0.2 M6 gate, plus F-PLANNER, F-GRAIN, F-TIER |
| M7 | the compiler and the grower under the standing rules; rollback; the molt | the v0.2 M7 gate, plus F-RULE, F-SELF-DRAFT |
| M8 | organs and surfaces, as before | unchanged |
| M9 | the tune; the epoch rule | the v0.2 M9 gate, plus F-RULE on an admitted version |
| M10 | seven real days on the operator's seat with the console dark | F-UNPLUG on the real tape; the receipt is the days-unplugged number |

## 8 · Constitution edits, as amendment text

- **Law 5, add.** The seam links no learned code. Its hash is on every header row. A verb row whose author is not the seam hash in force is refused by the tape writer. Masks flow from the seam to the judge and the planner, never the other way.
- **Law 6, add.** A ratified rule may admit artifacts, routines, adapters and versions, under its criterion. Admission is a widening inside the rule and needs no further signature. Revocation is a narrowing and needs none. A rule past its expiry admits nothing.
- **Law 8, add.** The trunk and the planner's weights are assets, checkpointed as state and never re-folded. A rebuilt trunk is the twin; it judges later and noisier, and it says so on every row it writes.
- **Law 15, new. Anticipation.** Every open obligation carries a forecast every period, from the planner or its null, and every forecast is graded when it comes due. No hold is ungraded for lack of a forecast.
- **Law 16, new. Self-observation.** FACTOR's own build is a lane. It is judged in shadow, forecast, and accounted for like any seat. FACTOR may draft its own changes and may never apply them.
- **Two corollaries of law 13, named.** Coordination through the ledger is stigmergy, and stigmergy fails two ways. Evaporation, a signal decaying unread, is refused because the walk covers the whole open set every period and ticks are on the tape. Inhibition, one signal drowning the rest, is refused because the uniform component and the no-guide stratum are floors the kernel may raise and never lower. Both are already in §13; they should be named as the law's corollaries so nobody removes them to make the walk look sharper.

## 9 · What not to do: autonomy theater

Every one of these would raise a meter and lower the truth.

- Do not let the planner or the judge emit a verb. Proposals in, one verb out, from the seam.
- Do not lower the stratum, the audit floor, the uniform draw or the lottery to make the unattended fraction climb. They are floors the kernel may raise and never lower.
- Do not count the hand's own reflections as outcomes. A receipt row joins to `executed` and never to a verb.
- Do not let FACTOR apply a proposal. Drafts only, under law 12 and law 16.
- Do not build self-restart. The watchdog is the operator's, and a crash loop degrades to off.
- Do not print a handled count without the unattended error rate beside it.
- Do not remove the hold verb from a class to raise its unattended fraction. Holds are most of the mass and the account grades them.
- Do not admit an artifact under a rule whose expiry has passed, and do not renew a rule by editing its row.
- Do not read days unplugged as good while the "not doing" section grows. Print both; the page is designed so you cannot see one without the other.
- Do not add a dashboard. Add a fold, and let the console stay empty.

## 10 · The three amendments, ready to append after QC

- **Amendment 7 · the geometry.** The seam as its own library with its hash on the header row; F-VETO; the law 5 and law 8 additions; the stigmergy corollaries named; the seam-to-planner mask direction.
- **Amendment 8 · the planner.** The event model at one seat and its null; deterministic inference; weights in the identity tuple; F-PLANNER and F-GRAIN; law 15; the pressure field closed as an open item.
- **Amendment 9 · the loops.** The three standing rules; the repo lane and `proposals/`; `STATUS.md` as a fold; F-UNPLUG, F-RULE, F-REPO, F-STATUS, F-SELF-DRAFT, F-TIER; the milestone reorder with M3 and M4 swapped and M10 added; law 16.

None of the three touches law 12. FACTOR still may not acquire, provision, copy itself, create an account, restart itself, resist a stop, or write anything that causes it to be run later. Autonomy to the max is every other loop closing, the person holding three rules and the signatures the law reserves, and a front page that is a reading rather than a claim.
