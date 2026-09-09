# FACTOR

A resident deputy for one seat: it reads the seat's streams, derives every obligation in
them, and discharges the ones it has earned a license to discharge, class by class,
recording every judgment and every hold with its margin on a hash-chained tape.

The shape is fixed and it is the point of the repository:

- a **learned side** that proposes and never disposes;
- a **deterministic seam** — the governor — that alone authors verbs;
- a **writ** on top that only a person writes;
- and the **world outside**, which is the only grader.

The hard problem is not doing the wrong thing. It is not doing things. A deputy dies
silently: missed actions, breached deadlines, opportunities never opened. Most of the
design exists to make silence visible on the tape and to grade it.

A *factor*, in the mercantile sense, is the commissioned agent who transacts on a
principal's behalf within a mandate and is answerable for every transaction. The name is
the specification.

---

## The governor

The judge returns a float. The gate returns a verb. Nothing learned may occupy the gate,
because a veto has to be unarguable and a learned veto can be argued with by its own
outputs. For a warrant obligation the gate returns before it reads the margin at all.
Pressure enters the gate as an additive term and never touches the judge.

Nine verbs, closed: `HOLD LOOK FETCH WAIT DRAFT DO ASK CONSULT PASS`, each with a reason
from a closed numbered set. One verb row per judgment, and a standing verb with its margin
on every open obligation at every instant. Never silence. A decision made by omission
leaves a row.

The license is earned per class and band, expires, and is monotone: the world narrows it on
evidence with no signature, and only a signed ratification widens it — where a ratification
is a *rule with an outcome criterion*, so widening inside the rule is written by outcomes
and only the rule needs a signature.

Fourteen laws are listed in [`BLUEPRINT_v0.2.md`](BLUEPRINT_v0.2.md) §1. Each is a property
the system has by construction, checked by at least one falsifier, not a policy in a
document.

---

## Status, with denominators

Nothing is built. This repository is a design of record, an executable reading of it, and
one measurement.

| | count | state |
|---|---:|---|
| falsifiers specified, each with a planted lie | 47 | stubs |
| falsifier functions (`requires`, `planted_lie`) | 94 of 94 | `TODO` |
| format harnesses running against Python models | 3 of 3 | green |
| the record checked at compile time (MSVC, g++) | 1 of 1 | green, planted lie refuses to compile |
| milestone receipts | 1 of 10 | M0 sandbox probe |
| kernel, launcher, seam, hand, console, lanes | 0 | not started |

The falsifier scaffold exits 0 while a falsifier is unwritten and 1 on any `FAIL`, `ERROR`
or `MISSING`. An unwritten falsifier is not a build failure; a broken or absent one is.

```bash
python tests/run_falsifiers.py            # 94 TODO, exit 0
python tests/run_falsifiers.py --gate M0  # 16 TODO, exit 0
python tests/check_layout.py              # the 128-byte record + the decimal amount parser
python tests/frame_roundtrip.py           # the 8-field frame, STRICT escaping, 10,000 strings
python tests/chain_check.py               # the keyed tape chain, fingerprints, tombstones
tests/msvc_check.cmd                      # the record at compile time, and its planted lie
```

A check that cannot fail is not a check. Every harness here carries planted lies it must
catch — 2 on the layout side, 5 on the frame side, 7 on the chain side — and every new rule
was made to fail before it was believed, with the negative controls recorded in
[`qc/O9_tests_amend4.md`](qc/O9_tests_amend4.md).

---

## The one measurement

[`receipts/M0_SANDBOX_PROBE_2026-09-08.md`](receipts/M0_SANDBOX_PROBE_2026-09-08.md), on a
Windows 11 box with an RTX 4070 Ti SUPER, no administrator and no installer:

- A zero-capability **AppContainer** refuses the child's outbound socket with `WSAEACCES`
  (10013) and a live loopback connect with `WSAETIMEDOUT` (10060). The unconfined control
  connects.
- **CUDA runs inside it at full speed.** Qwen3 1.7B fully offloaded: 281.65 ± 9.73 t/s
  inside against 279.38 ± 4.96 t/s outside — within noise. The GPU stack needed no
  capability grant of its own.
- One residual: `NtCreateFile` on `\Device\Afd\Endpoint` opens inside the container while
  the raw `\Device\Afd` open is denied (`0xC0000022`). The `AFD_CONNECT` IOCTL was not
  driven, so that route reads **inferred** until the compiled-in probe drives it.

So the sandbox law is `os-enforced` on this machine: the process that judges cannot open a
socket, and the operating system says so rather than a module list. The module list is kept
as a lint and the header row says which is which.

`probe/` holds the reference launcher and probe sources this rests on.

---

## Reading order

1. [`CLAUDE.md`](CLAUDE.md) — the rules, and the precedence when documents disagree.
2. [`KICKOFF_M0.md`](KICKOFF_M0.md) with its Amendment 1 — the build brief for the first
   milestone.
3. [`BLUEPRINT_v0.2.md`](BLUEPRINT_v0.2.md) — 25 sections and six amendments, the design of
   record.
4. [`HANDOFF_FOR-THE-IMPLEMENTING-SESSION_2026-09-08_FABLE5-1.md`](HANDOFF_FOR-THE-IMPLEMENTING-SESSION_2026-09-08_FABLE5-1.md)
   — written for a machine session starting blind, and the shortest route into the whole
   thing.
5. [`tests/README.md`](tests/README.md) — the 47 falsifiers and what each planted lie is.
6. [`qc/`](qc/) — seven reviews, their adjudication, and four harness passes.

**Precedence.** A receipt beats any document. `BLUEPRINT_v0.2.md` is the design of record
and its latest dated amendment beats the section it amends; amendments are appended, never
edited in place. `KICKOFF_M0.md` beats the blueprint on M0 specifics. `qc/` holds findings,
adopted only where an amendment says so. `PROPOSAL_REV1_*` is a proposal, not design of
record. `BLUEPRINT.md` is v0.1, superseded, kept because a planted lie needs something
false to assert. `tests/` is the executable reading of the spec: if a test and the spec
disagree, that is a finding, and neither changes silently.

---

## Layout

```
BLUEPRINT_v0.2.md     the design of record, with six dated amendments
BLUEPRINT.md          v0.1, superseded, referenced by one planted lie
KICKOFF_M0.md         the build brief for M0, with Amendment 1
HANDOFF_*.md          orientation for the implementing session
PROPOSAL_REV1_*.md    a proposal, not design of record
NEXT.md               the standing order of work
qc/                   the reviews, the adjudication, four harness passes
tests/                47 falsifiers, 3 Python models, the compile-time record check
receipts/             dated receipts; every claim with its command and exit code
probe/                the reference AppContainer launcher and egress probe
DWG-003_*.svg         the headquarters, exploded
```

---

## What this repository will not do

FACTOR never restarts itself, provisions, copies itself, creates an account, obtains a
credential, resists a stop, or writes anything that causes it to be run later. Its own
health opens obligations that may hold, look, draft or ask, and may never do. Every effect
on its own substrate requires an operator signature. That is law 12, and none of the
proposals in this repository touches it.

## Held back

Three files in the working tree are not published, and [`.gitignore`](.gitignore) says why:
two organization-radius documents derived from a third party's material and a named
organization's clinical workflow, and one review whose citations are line references into
private session transcripts. Everything they contributed to the design is in
`BLUEPRINT_v0.2.md` and its amendments, which are here in full.

## License

MIT. See [`LICENSE`](LICENSE).
