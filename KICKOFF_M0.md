# FACTOR · KICKOFF · M0 · THE KERNEL BOOTS
### The first milestone, scoped to what a session can build and gate without a model

**2026-09-08.** Design of record: `BLUEPRINT_v0.2.md` with Amendment 1. This file is the build brief for M0 as §22 defines it: the kernel boots with no model, and the formats, the record, the chain, the sandbox and the verifier exist and pass their falsifiers. Everything here is buildable today. The one item that waits on a receipt is the sandbox mechanism, and the receipt is `receipts/M0_SANDBOX_PROBE_2026-09-08.md`, which decides whether the header row will say `os-enforced`, `wfp-installed`, or `lint-only`.

---

## 1 · What M0 delivers

| deliverable | binary or file | falsifiers it makes real |
|---|---|---|
| the launcher | `factor-launch.exe` | F-EGRESS, M0 form |
| the kernel, model-free | `factor.exe` | F-CONSERVE without the heard bucket, F-REPLAY, F-DETERMINISM, F-PIN |
| the spool reader and the frame codec | inside `factor.exe`; `factor spool-verify`, `factor spool-seal` | F-FRAME |
| the tape writer and verifier | inside `factor.exe`; `factor verify`, `factor verify --chain-only` | F-CHAIN |
| the ledger | inside `factor.exe`; `factor ledger-digest` | F-LAYOUT, F-REPLAY |
| the pins and the header row | `factor about` | F-PIN |
| the gate | `gate.cmd` | runs everything above and exits nonzero on any red |
| the receipt | `receipts/M0_<date>.md` | the numbers, with denominators |

Not in M0: the model, the seats, the seam, the hand, the console, any producer that touches a network. M0's only producer is the file lane and the console lane, both local.

---

## 2 · Toolchain and laws of the build

- **C++20, MSVC 2022 Community**, `/std:c++20 /W4 /WX /EHsc /MT`, static CRT, one exe per process, no package manager, no framework, no runtime dependency. `build.cmd` is the whole build. g++ under WSL compiles the same sources as a second opinion where the code is portable.
- **The module gate is in the build.** `build.cmd` runs `dumpbin /dependents` on `factor.exe` and fails if any of `ws2_32`, `mswsock`, `winhttp`, `wininet`, `urlmon`, `dnsapi` appears. It is a lint, and the header row says so; the fence is the sandbox.
- **Vendored, pinned, no dependencies:** BLAKE2b from the RFC 7693 reference implementation, CC0, with keyed mode and personalization; a canonical JSON writer and a strict reader for the row subset, written here, not vendored, because the canonical form is the contract; nothing else.
- **No heredocs, no content through a shell literal.** Files are authored with the editor tools; the build and the gate are batch files with real errorlevels.
- **Every number printed by a binary carries its denominator**, and every claim in the receipt names the command that produced it.
- **Documents are amended, never edited.** This file, the blueprint, and the receipts.

---

## 3 · Layout, M0 subset

```
C:\FACTOR\
  build.cmd                 configure and build every binary; runs the module gate
  gate.cmd                  the M0 gate: builds, runs the checks, runs the falsifiers, exits nonzero on red
  launcher\
    main.cpp                the AppContainer profile, the re-exec, the child policy, the pipe ACLs
    sandbox.cpp / .h        per the probe receipt: os-enforced, wfp-installed, or lint-only
  kernel\
    main.cpp                verbs: boot, about, verify, spool-verify, spool-seal, ledger-digest, selftest
    pins.cpp / .h           the tuple: serve bytes, weights, maps, runtime, context, environment
    blake2b.c / .h          vendored RFC 7693, keyed, personalized
    cjson.cpp / .h          canonical JSON writer and strict reader
    spool.cpp / .h          header, eight-field frames, STRICT escaping, self-chain, cursor, generations
    ring.cpp / .h           SPSC ring of frames with a byte arena
    tape.cpp / .h           rows, keyed chain, segments, torn-row rules, fingerprints, tombstones
    ledger.cpp / .h         the 128-byte record, mmap, stamp slots, indexes, digest by ascending id
    writ.cpp / .h           parse, validate, class table, signature check
    switch.cpp / .h         off | shadow | live | stop, signature and sequence
    pill.cpp / .h           heartbeat.json with the lane contract's fields
  tests\                    the Python models and the falsifier stubs; M0's falsifiers become real here
  receipts\                 dated
```

---

## 4 · The verbs `factor.exe` answers at M0

- `factor about` prints the header row as JSON: the pin tuple with each member's hash and source, the module gate result, the sandbox mechanism in force, the record layout version, the hash known-answer vector result, the build id.
- `factor boot --home <dir>` opens the home, verifies the writ and switch signatures and sequences, opens or re-folds the ledger from its stamp, opens the spools at their cursors, takes the mark, appends the `hdr` row, and runs the model-free loop: every frame is ingested onto the tape as a `frame` row and into the structured extractor, every structured obligation is opened, updated or closed, and the ledger is folded. With no model there are no verbs; the loop proves conservation and replay.
- `factor verify --home <dir>` walks the tape two-way with the key, checks every frame reference against its spool, and prints the head; `--chain-only` verifies the fingerprint chain without the key.
- `factor spool-verify <spool>` verifies a spool alone, unkeyed. `factor spool-seal <lane>` is operator-signed and starts a generation.
- `factor ledger-digest --home <dir>` prints the chain hash of every record in ascending id order, the record count, and the stamp it was folded from.
- `factor selftest` runs the compiled-in checks: the layout static asserts at runtime, the frame codec round trip on the pinned corpus, the chain on a generated tape with the three planted lies, canonical JSON on the pinned vectors, the hash known-answer vector.

---

## 5 · The gate, in order

1. `build.cmd` exits 0 and the module gate passes.
2. `factor selftest` exits 0.
3. `python tests/run_falsifiers.py --gate M0` exits 0 with every M0 falsifier implemented and passing, and every planted lie caught. At M0 these are real, not stubs: F-LAYOUT, F-FRAME, F-CHAIN, F-CONSERVE without the heard bucket, F-REPLAY, F-DETERMINISM, F-PIN, F-EGRESS in its M0 form.
4. F-REPLAY's proof: boot on the planted spools, record the ledger digest, delete the ledger, boot again, digest identical; then boot with the spools' frames delivered in a different interleaving across lanes, digest identical.
5. F-DETERMINISM's proof at M0: two boots over the same spools produce byte-identical `frame` and `obligation` rows in the plan-hash projection.
6. F-EGRESS's M0 form: the probe compiled into the kernel tries the three socket routes inside the launched sandbox and all three are refused; a socket sample over the process tree finds none.
7. The receipt is written with every number and its command, and the gate's own exit code.

---

## 6 · Decisions taken for M0 that later milestones inherit

- The kernel's verbs are subcommands of one binary so the pins are asserted once, in one place, before anything else runs.
- The ring holds frames, not bytes; the arena is separate; both sizes are in the writ's `[kernel]` stanza, which M0 adds to the schema with `ring_slots`, `arena_mib`, `segment_mib = 64`, `fingerprint_every = 4096`.
- The planted spools for the falsifiers live in `tests/spools/` and are generated by a script with a pinned seed, so the corpus is reproducible and the lies are planted by code.
- The structured extractor at M0 covers the file lane's map only; the mailbox and books maps arrive with M2.

---

## 7 · What would stop M0

The probe finding that the card cannot be reached inside the container and that the administrator-installed filter is not acceptable either. Then the header says `lint-only`, the design's sandbox law is downgraded in a dated amendment, and the hand's ledger becomes the perimeter as O1 §4.4 describes. That is a design decision for the operator, not for the build.

---
*The tape, as always, is the proof. M0's tape is the first one.*

---

## Amendment 1 · 2026-09-08 · The sandbox is decided, and the build follows the house convention

**The sandbox.** The probe receipt at `receipts/M0_SANDBOX_PROBE_2026-09-08.md` and Amendment 2 of the blueprint settle §7 of this file: the launcher builds the zero-capability AppContainer path as the primary and only mechanism on this box, the header row says `os-enforced`, and the fallback in `launcher/sandbox.cpp` is kept as code that reports rather than a path that is exercised. The probe's `launcher.exe` and `probe.exe` under `probe/` are the reference for the attributes, the SDDL and the cleanup; the M0 launcher lifts them, and the kernel's F-EGRESS probe adds the `AFD_CONNECT` IOCTL the probe left to inference. Every exit path of the launcher deletes the profile and revokes the grants, and a profile found on boot is a `warn`.

**The build.** §2 of this file said raw `cl` in a batch file. The operator's native CUDA projects on this machine, `C:\backrooms`, `C:\Booster_Lander_Simulator` and `C:\connectome\native`, share one house convention, and M1 links llama.cpp with CUDA, so M0 adopts it now rather than migrating later: CMake 3.28 with Ninja from the VS 2022 developer environment and `CMakePresets.json`; static MSVC runtime through `CMAKE_MSVC_RUNTIME_LIBRARY`; `/W4 /WX /permissive- /EHsc /utf-8` on FACTOR's own code with third-party headers as external at warning level zero; CTest enabled and the falsifiers registered as tests; deterministic output under `build/bin`; CUDA enabled conditionally through `check_language` so a machine without a toolkit builds the model-free kernel cleanly; CUDA architectures 89, 90 and 120 when it is enabled. `build.cmd` becomes the wrapper that runs the preset and then the module gate with `dumpbin /dependents`. The one static binary per process, the module gate and the vendored, dependency-free BLAKE2b and canonical JSON stand as written.

**WSL.** The operator's WSL Ubuntu holds the fine-tuning environment, reachable as `peek train`. M9's `factor epoch` exports the training set to a path WSL can read and the tune runs there; nothing at M0 depends on it, and g++ under the same WSL remains the second-opinion compiler for the portable sources.
