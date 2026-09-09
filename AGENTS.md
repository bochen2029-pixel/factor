# C:\FACTOR — read this first, then the handoff

You are a session starting blind in a repository that a day of parallel sessions designed, reviewed and re-cut on 2026-09-08. Before you write anything, read `HANDOFF_FOR-THE-IMPLEMENTING-SESSION_2026-09-08_FABLE5-1.md` in this directory in full. It is written for you, not for a person, and it carries the context you do not have: the big picture, the intent, the precedence rules when documents disagree, the register, the traps measured on this machine, and your first job.

## What this is, in four sentences

FACTOR is a resident deputy for one seat: it reads the seat's streams, derives every obligation in them, and discharges the ones it has earned a license to discharge, class by class, recording every judgment and every hold with its margin on a hash-chained tape. The shape is fixed: a learned side that proposes and never disposes, a deterministic seam that alone authors verbs, a writ on top that only a person writes, and a world outside that is the only grader. The hard problem is not doing the wrong thing; it is not doing things, and most of the design exists to grade silence. Nothing in this repository is done until it ends in a dated receipt whose test was made to fail before it was believed.

## Design of record and precedence

1. A receipt in `receipts/` beats any document.
2. `BLUEPRINT_v0.2.md` is the design of record. Its latest dated amendment beats the section it amends. Amendments are appended, never edited in place, and you never edit the blueprint at all.
3. `KICKOFF_M0.md` with its Amendment 1 is the build brief for M0 and beats §22 and §23 on M0 specifics.
4. `qc/` holds findings; a finding is adopted only where an amendment or `qc/QC_SYNTHESIS_2026-09-08.md` says so.
5. `PROPOSAL_REV1_AUTONOMY-TO-THE-MAX_2026-09-08_FABLE5-1.md` and everything under `C:\55555` are proposals, not design of record, until amended in.
6. `BLUEPRINT.md` is v0.1, superseded, referenced only where a planted lie needs something false.
7. `tests/` is the executable reading of the spec. If a test and the spec disagree, stop and report both; change neither silently.

## Non-negotiables in code

- The kernel opens no socket, enforced by the AppContainer, and links no `ws2_32`, `mswsock`, `winhttp`, `wininet`, `urlmon`, `dnsapi`; the build's module gate checks it.
- Nothing learned authors a verb. The seam does, and only the seam.
- The tape is append-only and keyed-chained; holds are rows; a decision by omission leaves a row.
- No binary float touches an amount, a canonical form, or a parallel sum. Fixed-point integers, decimal text parsing, canonical JSON with sorted keys and 64-bit integers as strings.
- Two cold replays are byte-identical. No wall time inside a fold; ticks are on the tape.
- Every check has a planted lie that is caught and a negative control that fails when the mechanism is removed. A check that cannot fail is not a check.
- Floors are never lowered to pass a test: the stratum, the uniform draw, the lottery, the audit floor.
- Law 12 stands: FACTOR never restarts itself, provisions, copies itself, or writes anything that causes it to be run later.

## Machine rules that will bite you in the first hour

- Write Windows paths with forward slashes in every shell command: `python C:/FACTOR/tests/run_falsifiers.py`. Git Bash eats backslashes silently.
- Heredocs are blocked by a hook on the Bash and PowerShell tools. Author files with the Write tool, change them with Edit, never through a shell literal. Never put a lone apostrophe or a backslash on a Bash command line.
- There is no g++ on Windows here. MSVC 19.44 from VS 2022 Community; g++ only under WSL. `tests/msvc_check.cmd` is a real batch file because `%errorlevel%` in a `cmd /c` one-liner expands at parse time and lies.
- Running an exe from the current directory is refused on this box; use an explicit path.
- Long builds go in the background; the Bash tool times out at 120 s by default.
- Do not poll a background agent; its transcript leaks into your context. Wait for its completion notice, then read its report file.
- When the operator says conserve, be brief, read nothing, close out, and pause.

## How to work here

- One step at a time. Read what is named. Do not read the `C:\55555` series or the nine-session tape wholesale; the handoff names the few files that matter and how to search the rest.
- Formats first. Every step ends in a receipt: the command, its printed output, its exit code, every number with its denominator, and a numbered list of what was not done and what is still ambiguous.
- Measure before you write prose. If you find yourself drafting a design paragraph, write the test instead.
- Report plainly: state first, then a five-line summary, then what needs the operator. No menus, no hedging, no closing flourish.
- You are one witness. Files may appear here from parallel sessions; do not treat them as yours, do not open them unless named, and never count agreement between sessions as evidence.

Gate command, which must exit 0 before and after your work:

```
python C:/FACTOR/tests/run_falsifiers.py
```
