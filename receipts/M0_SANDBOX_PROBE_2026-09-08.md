# M0 · Sandbox probe receipt · 2026-09-08

Measurement of §11's sandbox law ("The valve and the hand") and O1 §4 ("The two-process
egress law on Windows") on the target machine, before anything is built on top of it.

- **Machine:** Windows 11 Pro 10.0.26100, NVIDIA GeForce RTX 4070 Ti SUPER (16375 MiB, CC 8.9),
  driver 610.47. MSVC 19.44 (VS 2022 Community, toolset 14.44.35207), `/MT` static CRT.
- **llama.cpp:** build `53bd47ea5 (9627)`, CUDA 12.4, at `C:/llama.cpp` (flat layout; binaries and
  `ggml-*.dll` / `cudart64_12.dll` / `cublas*` are in that one directory).
- **AppContainer profile:** `FACTOR-probe`, created with a **null capability array** (zero
  capabilities), deleted at end via `DeleteAppContainerProfile` (hr=0x00000000).
- **Package SID (printed by the launcher):**
  `S-1-15-2-2091054370-2409397180-3052290479-3524698394-1454522161-1990859462-3359163845`
  (deterministic from the profile name — identical across every run).

---

## Verdict on §11's sandbox law

**`os-enforced`.** On this box a zero-capability AppContainer denies every real egress route the
kernel could attempt — outbound TCP is refused by WFP with `WSAEACCES` (10013) and a live loopback
connect dies by `WSAETIMEDOUT` (10060), with **no administrator and no installer** — *and* the
resident model runs on the GPU inside that same container at full speed, so §11's primary mechanism
holds and neither the `wfp-installed` nor the `lint-only` fallback is required on this machine.

The layered fallback O1 §4.2 describes (restricted token + low IL + admin WFP filter) was therefore
**not exercised** — the condition that triggers it (CUDA failing inside the container) did not occur.

---

## Test matrix — inside container vs outside control

PASS/FAIL is written from the sandbox's point of view: inside, PASS = the confinement held; the
outside column is the control and its "FAIL" simply means "not confined", which is correct and
expected for an unconfined process.

| test | inside container | outside control | reading |
|---|---|---|---|
| **SOCKET** outbound `1.1.1.1:80` | **blocked** `WSAEACCES` (10013) | connected (0) | WFP blocks outbound at ALE_AUTH_CONNECT, keyed on the package SID |
| **SOCKET** loopback→live listener `127.0.0.1:<ephemeral>` | **timed-out** `WSAETIMEDOUT` (10060) | connected (0) | loopback data channel denied inside; matches O1's "WFP defers the same-package decision to the receive layer, so it times out" |
| **SOCKET** loopback `127.0.0.1:9` (empty port) | refused `WSAECONNREFUSED` (10061) | refused (10061) | informational: an unoccupied port RSTs in both contexts; the *live-listener* row above is the real loopback test |
| **SOCKET** `WSAStartup`/`socket()` create | succeeded | succeeded | socket *creation* is allowed inside; the *connect* is what WFP blocks |
| **AFD** `NtCreateFile \Device\Afd\Endpoint` | **opened** `STATUS_SUCCESS` (0x00000000) | opened (0x0) | device handle opens inside the container — see caveat below |
| **AFD** `NtCreateFile \Device\Afd` (raw) | **denied** `STATUS_ACCESS_DENIED` (0xC0000022) | opened (0x0) | the raw device object is AC-denied; the `\Endpoint` sub-object is not |
| **PIPE** granted-SID pipe (SDDL names package SID) | **PASS** — wrote and read echo back | echo OK | O1 §4.3 pipe design works: the AppContainer reaches a global `\\.\pipe\` name when the DACL names its package SID |
| **PIPE** default-descriptor pipe | **denied** `ERROR_ACCESS_DENIED` (5) | opened | a pipe created with the default SD is correctly unreachable from the container |
| **CUDA** nvcuda `LoadLibrary`→`cuInit`→device→`cuCtxCreate`→64 MiB `cuMemAlloc`+HtoD+DtoH round trip | **PASS** — every step `CUDA_SUCCESS`, round trip `MATCH` | PASS, MATCH | the GPU driver stack is fully reachable inside a zero-capability AppContainer with **no capability grant** |

Raw probe lines are in `out/probe_inside.txt` and `out/probe_outside.txt`. Inside:

```
TEST SOCKET PASS loopback_127.0.0.1:9=refused(10061) internet_1.1.1.1:80=blocked-EACCES(10013) loopback_live_127.0.0.1:61437=timed-out(10060) egress_leaked=no
TEST AFD  FAIL afd_endpoint_status=0x00000000 afd_raw_status=0xC0000022 openable=YES
TEST PIPE PASS secure=OK(err=0) secure_echo="FACTOR-PROBE-PING" default=denied(err=5)
TEST CUDA PASS load_nvcuda=OK cuInit=0(CUDA_SUCCESS) count=1 dev0="NVIDIA GeForce RTX 4070 Ti SUPER" cuCtxCreate=0 cuMemAlloc64MiB=0 HtoD=0 DtoH=0 roundtrip=MATCH
```

### The resident model on the card, inside vs outside (the real test)

`llama-bench.exe -ngl 99 -p 128 -n 32 -r 2`, launched into the same AppContainer. The model loaded
on **CUDA** with all layers offloaded (`ngl 99`) **inside the container**; no error text.

| model | metric | inside container | outside control |
|---|---|---|---|
| Qwen3 1.7B Q4_K_M (`q3-17b-emit-G2`, 1.03 GiB) — representative resident LM | prompt `pp128` | 10630 ± 3024 t/s | 10491 ± 4009 t/s |
| | gen `tg32` | **281.65 ± 9.73 t/s** | **279.38 ± 4.96 t/s** |
| all-MiniLM-L6-v2 f16 (BERT 22M, 43.1 MiB) — literal smallest GGUF on the box | prompt `pp128` | 63114 t/s (high variance) | 32773 t/s (high variance) |
| | gen `tg32` | 1715 ± 312 t/s | 2003 ± 129 t/s |

The stable generation metric (`tg32`) is **within noise inside vs outside** — the AppContainer
imposes no measurable GPU penalty. (An earlier cold first-run inside read 243 t/s; on warm cache it
matches the control.) `pp128` variance is large because both models finish a 128-token prefill in
well under a millisecond; it is not a meaningful inside/outside signal. Outputs:
`out/llama_inside_q3-1.7b.txt`, `out/llama_outside_q3-1.7b.txt`, `out/llama_inside_minilm.txt`,
`out/llama_outside_minilm.txt` (and the canonical `out/llama_inside.txt` / `out/llama_outside.txt`
hold the q3-1.7b pair).

**Model choice note:** the absolute smallest GGUF on the machine is the 43 MiB MiniLM, but it is a
BERT embedding model, so its `tg` number is not representative of a resident causal LM; the primary
figures use the smallest *causal* LM (Qwen3 1.7B, 1.03 GiB), which is the same architecture family
as the intended resident model. Both were run in and out of the container; both load on the GPU
inside it.

---

## Exact CreateProcess attributes used

Profile: `CreateAppContainerProfile(L"FACTOR-probe", disp, desc, NULL /*capabilities*/, 0 /*count*/, &sid)`
then `DeriveAppContainerSidFromAppContainerName` on the already-exists path; `ConvertSidToStringSid`
for the SDDL/printing.

Child launch (`CreateProcessW`):

- `dwCreationFlags = EXTENDED_STARTUPINFO_PRESENT | CREATE_UNICODE_ENVIRONMENT`, `bInheritHandles = TRUE`.
- `STARTUPINFOEXW` with `STARTF_USESTDHANDLES`; `hStdOutput = hStdError =` an **inheritable** file
  handle opened by the launcher in the granted `out\` directory (this is how the child's stdout is
  captured — the inherited handle carries the launcher's granted access); `hStdInput = ` inheritable
  `NUL`.
- `PROC_THREAD_ATTRIBUTE_LIST` with **3** attributes when launching inside:
  1. `PROC_THREAD_ATTRIBUTE_SECURITY_CAPABILITIES` →
     `SECURITY_CAPABILITIES{ AppContainerSid = <package SID>, Capabilities = NULL, CapabilityCount = 0 }`
  2. `PROC_THREAD_ATTRIBUTE_CHILD_PROCESS_POLICY` → `PROCESS_CREATION_CHILD_PROCESS_RESTRICTED`
     (the kernel/child cannot escape by spawning a helper — O1 §4.4)
  3. `PROC_THREAD_ATTRIBUTE_HANDLE_LIST` → `{ hStdOutput, hStdInput }` (only these handles inherit)

  The outside control uses the same `STARTUPINFOEXW` + handle-list attribute but **omits**
  attributes 1 and 2.

Named-pipe server (launcher side, per O1 §4.3): created **before** the child spawns with
`FILE_FLAG_FIRST_PIPE_INSTANCE` + `FILE_FLAG_OVERLAPPED`, mode
`PIPE_TYPE_BYTE | PIPE_READMODE_BYTE | PIPE_WAIT | PIPE_REJECT_REMOTE_CLIENTS`, and this explicit
SDDL naming the package SID:

```
D:P(D;;GA;;;NU)(D;;GA;;;AN)(A;;GA;;;OW)(A;;GA;;;SY)(A;;GRGW;;;<package SID>)
```

(deny NETWORK and ANONYMOUS logons first, then grant OWNER and SYSTEM full and the AppContainer
package SID read+write). The second, "default descriptor" pipe passed `NULL` security — and was
correctly denied to the container (err 5).

---

## ACLs that had to be granted for the GPU path to work

The launcher added an allow-ACE for the **package SID** on exactly these objects (via
`GetNamedSecurityInfo` → `SetEntriesInAcl` → `SetNamedSecurityInfo`); all were revoked at cleanup:

| object | access granted | inheritance | why |
|---|---|---|---|
| `C:\llama.cpp` | `GENERIC_READ \| GENERIC_EXECUTE` (0xA0000000) | CI+OI | the `llama-bench.exe` binary and every `ggml-*.dll` / `cudart64_12.dll` / `cublas*` it loads |
| `C:\models\<model>.gguf` | `GENERIC_READ` (0x80000000) | none | the weights file (opened read-only) |
| `C:\FACTOR\probe\out` | `GENERIC_READ \| GENERIC_WRITE \| GENERIC_EXECUTE` (0xE0000000) | CI+OI | stdout/stderr capture directory (deny-by-default on named objects) |
| `C:\FACTOR\probe\bin` | `GENERIC_READ \| GENERIC_EXECUTE` (0xA0000000) | CI+OI | for the `probe.exe` runs (not needed for the llama runs) |

**Key finding for the card:** the CUDA stack itself required **no special ACL**. `nvcuda.dll`
(System32), the driver store, and the D3DKMT / adapter device objects are already reachable by
AppContainers through the default *ALL APPLICATION PACKAGES* access on those system locations.
The only grants needed were for FACTOR's *own* files (the app binary directory, the DLL directory,
the weights, and the output directory). AppContainers hold `SeChangeNotifyPrivilege`, so no
per-parent-directory traverse grant was needed to reach the weights.

---

## Caveats and the one residual for the M0 F-EGRESS gate

- **AFD device-open is not egress.** `NtCreateFile` on `\Device\Afd\Endpoint` **succeeds** inside the
  container (the raw `\Device\Afd` is denied). Opening the device is step one of the module-gate
  bypass O1 §4.1 warns about (`NTSockets`), but the *connect* driven over that handle
  (`AFD_CONNECT` IOCTL) still transits WFP's `ALE_AUTH_CONNECT` layer, which is keyed on the
  token's **package SID**, not on which code path opened the socket — the same layer that returned
  `WSAEACCES` on the ordinary `ws2_32` path in the SOCKET test. So the raw-AFD route defeats the
  *module gate* but not the *AppContainer WFP block*.
- **What I did not drive end to end:** per the task's stated allowance ("if that is too much, at
  least report whether `NtCreateFile` on `\Device\Afd` succeeds"), the probe drives the device-open
  but **not** the full `AFD_BIND`/`AFD_CONNECT` IOCTL sequence. The outcome is determined by the
  token-keyed WFP block above, but a fully rigorous M0 **F-EGRESS** implementation should drive the
  raw AFD connect IOCTL to observe the refusal directly, alongside the `ws2_32` connect (blocked,
  shown) and the loopback connect (timed out, shown). That is the one route measured by inference
  rather than by direct observation here.
- **Loopback failure mode is a timeout, not a fast refusal** (`WSAETIMEDOUT`), exactly as O1 §4.2
  predicts. Anything inside the container that expects loopback to fail fast will instead hang until
  its own timeout.
- **Not a defence against the box owner.** Unchanged from §20/O1 §4.4: a local admin or SYSTEM lifts
  the filter, injects, or edits the writ. This probe measured only the no-admin, self-applied fence.

---

## Files created under C:/FACTOR/probe/

```
C:/FACTOR/probe/build.cmd                         (MSVC build: vcvars64 + cl, static CRT /MT)
C:/FACTOR/probe/src/probe.cpp                     (the child: SOCKET/AFD/PIPE/CUDA tests)
C:/FACTOR/probe/src/launcher.cpp                  (profile, SID, pipes, ACLs, AppContainer launch)
C:/FACTOR/probe/bin/probe.exe                     (compiled child)
C:/FACTOR/probe/bin/probe.obj
C:/FACTOR/probe/bin/launcher.exe                  (compiled launcher)
C:/FACTOR/probe/bin/launcher.obj
C:/FACTOR/probe/out/probe_inside.txt              (4-test probe, inside container)
C:/FACTOR/probe/out/probe_outside.txt             (4-test probe, outside control)
C:/FACTOR/probe/out/llama_inside.txt              (canonical: q3-1.7b inside)
C:/FACTOR/probe/out/llama_outside.txt             (canonical: q3-1.7b outside)
C:/FACTOR/probe/out/llama_inside_q3-1.7b.txt      (resident-LM inside)
C:/FACTOR/probe/out/llama_outside_q3-1.7b.txt     (resident-LM outside control)
C:/FACTOR/probe/out/llama_inside_minilm.txt       (smallest-file inside)
C:/FACTOR/probe/out/llama_outside_minilm.txt      (smallest-file outside control)
```

Cleanup performed: all package-SID ACEs revoked (verified 0 residual on every granted path);
`DeleteAppContainerProfile(FACTOR-probe)` returned hr=0x00000000; no `FACTOR-probe` package
directory remains under `%LOCALAPPDATA%\Packages`. No administrator elevation was used at any point.
