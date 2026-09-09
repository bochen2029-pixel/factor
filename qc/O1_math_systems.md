# O1 · Mathematics and systems feasibility

Review of `C:\FACTOR\BLUEPRINT.md` v0.1 (2026-09-08). Lens: is the mathematics right, and will the systems calls do what the document says they do. Everything below was checked against primary sources on 2026-09-08. Where a claim is refuted the correction is written as paste-ready spec text.

Verification anchor for all llama.cpp claims: `ggml-org/llama.cpp` master at commit `f3f1a8f2760f28325a5ec20c05b171e5b7c83a29`, dated 2026-09-08, read from a sparse clone of `include/`, `src/`, `ggml/src/ggml-cuda/`, `docs/`.

---

## 1 · §10 · The license test

**Verdict: holds with correction.** The shape is right and it is the right shape — an e-process gives exactly the "read the license at any time without a multiple-comparison lie" property §10 claims, and Ville's inequality is what licenses that claim. Four things are underspecified to the point of being wrong if coded naively: (a) the null is composite and one-sided, which constrains the sign of the bet and the document never says so; (b) the baseline `p0` is estimated from the same stream the test consumes, which voids the guarantee; (c) demotion is written as a test but is a *change-detection* problem and needs an e-detector, not an e-process, or a license once earned can never be lost by drift; (d) expiry must reset the process and that costs type-I error which must be printed.

### 1.1 The object

An **e-value** for a null `H0` is a nonnegative random variable `E` with `E_P[E] ≤ 1` for every `P ∈ H0`. An **e-process** is a nonnegative process `(E_t)` that is upper-bounded by a nonnegative supermartingale under every `P ∈ H0`. Ville's inequality gives the whole license in one line:

```
P( ∃t ≥ 1 : E_t ≥ 1/α )  ≤  α       for every P in H0
```

so "stop and promote the first time `E_t` crosses `1/α`" is a level-`α` test *no matter when you look, how often you look, or why you stopped*. That is the property §10 needs and it is not an approximation. ([Ramdas, Grünwald, Vovk & Shafer, *Game-theoretic statistics and safe anytime-valid inference*, Statistical Science 38(4), 2023](https://arxiv.org/abs/2210.01948))

### 1.2 The Bernoulli betting process, exactly

Let `X_1, X_2, …` be graded outcomes in `{0,1}`, `X_i = 1` meaning "the verb was correct at its horizon". Let `p0` be the pinned baseline rate and `δ > 0` the ratified margin. The capital process is

```
K_t  =  ∏_{i=1..t} ( 1 + λ_i · (X_i − p0) ),      K_0 = 1
```

with `λ_i` **predictable** (a function of `X_1..X_{i−1}` only). Nonnegativity requires

```
λ_i ∈ ( −1/(1−p0) , 1/p0 )
```

which is [Waudby-Smith & Ramdas, *Estimating means of bounded random variables by betting*, JRSS-B 86(1), 2024, eq. (23)](https://arxiv.org/abs/2010.09686) with `m := p0`.

**The sign of the bet is what makes the null composite-safe, and the blueprint must say so.** For any `P` with `E[X_i | F_{i−1}] = p`,

```
E[ 1 + λ(X_i − p0) | F_{i−1} ]  =  1 + λ(p − p0)
```

so with `λ ≥ 0` the process is a supermartingale under every `p ≤ p0`, and with `λ ≤ 0` under every `p ≥ p0`. Hence two processes, not one:

```
E⁺_t = ∏ (1 + λ⁺_i (X_i − p0)),  λ⁺_i ∈ [0, 1/p0)        e-process for H0⁺: p ≤ p0   (promotion)
E⁻_t = ∏ (1 + λ⁻_i (X_i − p0)),  λ⁻_i ∈ (−1/(1−p0), 0]   e-process for H0⁻: p ≥ p0   (demotion)
```

A single two-sided process would license nothing, because a run of failures would push a two-sided statistic up and read as evidence *for* the deputy.

### 1.3 The bet to use

Kelly / growth-rate-optimal. Maximising `E_p[log(1 + λ(X − p0))]` over `λ` gives, in closed form,

```
λ*(p)  =  (p − p0) / ( p0 (1 − p0) )
```

and substituting it back reproduces the exact likelihood ratio: `1 + λ*(p)(X − p0) = (p/p0)^X · ((1−p)/(1−p0))^(1−X)`, with wealth growing at rate `KL(p ‖ p0)` per observation. So the betting form is not a heuristic — it *is* the likelihood-ratio test martingale, written so that the bet is visible and auditable.

Since `p` is unknown, plug in a **predictable** shrunk estimate and truncate (this is GRAPA/aGRAPA in WSR §4.2):

```c
/* per side, per (cls, band, verb). All state is a fold over the tape. */
double p_hat = (a0 + S_prev) / (a0 + b0 + n_prev);      /* a0=b0=1, or a0=k*p0,b0=k*(1-p0) */
double lam_up = clamp( (p_hat - p0 - delta) / (p0*(1.0-p0)),  0.0,  C_TRUNC / p0 );
double lam_dn = clamp( (p_hat - p0 + delta) / (p0*(1.0-p0)), -C_TRUNC / (1.0-p0), 0.0 );
E_up *= 1.0 + lam_up * (x - p0);
E_dn *= 1.0 + lam_dn * (x - p0);
```

`C_TRUNC = 0.5` pinned in the writ keeps the capital away from the ruin boundary. If you would rather not tune, WSR's tuning-free predictable plug-in empirical-Bernstein bet ([eq. 15](https://arxiv.org/abs/2010.09686)) is a drop-in for the magnitude:

```
λ_t^PrPl-EB = min( sqrt( 2 log(2/α) / ( σ̂²_{t−1} · t · log(1+t) ) ) , c ),
σ̂²_t = ( 1/4 + Σ_{i≤t} (X_i − μ̂_i)² ) / (t + 1)
```

**Closed-form check with no tuning at all.** A Beta mixture over the alternative is a valid e-process for the same one-sided null (a mixture of supermartingales is a supermartingale) and needs only `lgamma` plus a regularized incomplete beta:

```
S_t = Σ X_i
E_t^mix = [ ∫_{p0+δ}^{1} p^{S_t} (1−p)^{t−S_t} dBeta_{a,b}(p) ]  /  [ p0^{S_t} (1−p0)^{t−S_t} ]
        = B(a+S_t, b+t−S_t) · ( 1 − I_{p0+δ}(a+S_t, b+t−S_t) )
          / [ B(a,b) · ( 1 − I_{p0+δ}(a,b) ) · p0^{S_t} (1−p0)^{t−S_t} ]
```

Run it beside the betting process; they should agree to within an order of magnitude, and disagreement is a bug in the bet, not in the theory. Method of mixtures: [Ramdas et al. 2023 §4](https://arxiv.org/abs/2210.01948).

### 1.4 Promotion and the asymmetric demotion bar

```
promote  when  E⁺ ≥ 1/α_up                    (α_up ratified, e.g. 0.01 → bar 100)
demote   when  M⁻ ≥ 1/α_dn,  α_dn = 10·α_up   (e.g. 0.10 → bar 10)
```

"An order of magnitude closer" is exactly `α_dn = 10 α_up`; the bar is a tenth of the promotion bar and both are pure numbers on the tape.

**Demotion must be an e-detector, not an e-process.** A license is earned *after* a stretch of good behaviour; degradation is a *change* in an already-good process. A fixed-start e-process for `H0⁻` starts at 1 and is diluted by all the good evidence that preceded the change, so a class that was excellent for a year and turns bad this month may never cross the demotion bar. The right object is a sum-type (Shiryaev–Roberts) **e-detector**, which is a sum of e-processes started at every time, and which comes with a nonasymptotic average-run-length bound: stopping at `M_t ≥ 1/α_dn` gives `ARL = E_∞[τ] ≥ 1/α_dn`. It is a one-line recursion:

```c
M_dn = (1.0 + M_dn) * (1.0 + lam_dn * (x - p0));   /* M_dn starts at 0 */
```

([Shin, Ramdas & Rinaldo, *E-detectors: a nonparametric framework for sequential change detection*, NEJSDS 2(2), 2023](https://arxiv.org/abs/2203.03532))

### 1.5 The baseline is not estimable from the test's own data

§13 measures "the person's baseline … from the shadow period" and §10 tests "correctness at or above the person's baseline". If `p0` is a running estimate over the same stream the e-process consumes, the process is not an e-process for anything and Ville's bound does not apply. Two correct options:

**(a) Freeze it.** `p0` is the lower end of a one-sided 95% Clopper–Pearson interval on the person's correctness in this `(cls, band)`, computed once from the shadow period, written as a `ratify` row, and pinned. Re-measuring opens a new epoch and resets the processes. The null is then simple and everything above applies verbatim.

**(b) Pair it — preferred, and it also kills drift.** The stratum (§10) already routes a ratified fraction of every licensed class to the person. On those instances you have both dispositions. Grade the pair and bet on the difference:

```
D_i = 1{deputy correct} − 1{person correct}  ∈ {−1, 0, +1}
Z_i = (D_i + 1) / 2                          ∈ {0, 0.5, 1}
m   = 0.5 + δ/2
K_t = ∏ ( 1 + λ_i (Z_i − m) ),   λ_i ∈ ( −1/(1−m), 1/m )
```

This is WSR's bounded-mean setting unchanged, needs no external baseline, is immune to the mix of cases drifting over time, and the stratum was already the instrument that makes it possible. Recommend (b) as the law and (a) as the bootstrap for classes with no stratum yet.

### 1.6 Horizons, late outcomes, censoring

The blueprint says grades are read at the horizon and never before (§3) but does not say how an e-process survives outcomes arriving out of order. Predictability is the whole guarantee; the fix is an ordering law plus a totality law.

- **Order by horizon, not by decision.** Grades enter each e-process in ascending `(horizon_ns, id)`, never in decision order. A decision made later may resolve earlier; that is fine, and it is the only ordering under which `λ_t` can be predictable and a re-fold can reproduce the same process.
- **Grade at the horizon, always.** The grading function is total: `unknown at horizon` grades **0** on the promotion side. Then nothing is censored and there is no selection to correct for. It also makes the license harder to earn, which is the safe direction.
- **Never re-grade backwards.** An outcome landing after the horizon writes a `regrade` row. It feeds `epoch` (§18) and may trigger a demotion review. It never re-enters an e-process that has advanced past that horizon; doing so destroys predictability and with it Ville's bound.
- **Write the bet before you read the grade.** `λ_t` is written on the tape in the `license` row *before* `X_t` is read. That makes predictability auditable by `factor verify` with no model, and it is a falsifier.

### 1.7 The both-sides floor, stated

Two grade streams per `(cls, band)`: **A** = instances whose margin cleared `θ_do` (acted, or shadow/canary), graded on whether the act was right; **H** = instances whose margin did not clear it (held, waited, asked), graded on whether declining was right. §10 is correct that H can only be graded via the stratum and the canary.

The bad hypothesis is a *union* — the license is wrong if **either** side is wrong — and the minimum of e-values is a valid e-value for a union null (`min(E_A, E_H) ≤ E_A`, so its expectation is ≤ 1 under `H_A`, and symmetrically). So:

```
calibrated(cls, band)  ⟺  n_A ≥ n0  ∧  n_H ≥ n0
promote                ⟺  calibrated  ∧  min(E⁺_A, E⁺_H) ≥ 1/α_up
demote                 ⟺  max(M⁻_A, M⁻_H) ≥ 2/α_dn        (Bonferroni over the two sides)
```

`max` is not an e-value, so the demotion side pays a factor 2 across the two streams. `n0` is in the writ, default 30.

### 1.8 Expiry costs error, and the account should print it

An e-process that never resets makes a license permanent in evidence even if §10 expires it in rung. Reset both processes to 1 at each expiry boundary and re-earn. The cost is honest and bounded: after `k` epochs the lifetime type-I bound is `≤ k · α_up` by a union bound. Print the running `k · α_up` on the weekly account beside the license, so nobody has to guess.

### 1.9 The audit floor is already the right formula, and here is why

`audit_floor = sqrt(3/F)`, never below `1/64`. Reviewing `n = F · sqrt(3/F) = sqrt(3F)` items per period, the rule of three says that seeing zero defects in `n` reviews puts a 95% upper bound of `3/n` on the defect rate — and `3/sqrt(3F) = sqrt(3/F)`, which is the sampling fraction itself. **The fraction you sample equals the defect ceiling you can certify.** That is a fixed point, not a coincidence, and it should be written down. ([Hanley & Lippman-Hand, *If nothing goes wrong, is everything all right?*, JAMA 249(13):1743–5, 1983](https://en.wikipedia.org/wiki/Rule_of_three_(statistics)); [van Tuyl et al., *The rule of three, its variants and extensions*, Int. Stat. Review 77(2), 2009](https://onlinelibrary.wiley.com/doi/10.1111/j.1751-5823.2009.00078.x))

The `1/64` floor binds at `F = 3 · 64² = 12,288` items per period; above that the review count grows linearly again, `F/64`. State the crossover so nobody discovers it as a surprise cost.

### Corrected spec text — replaces §10 "The test", "Expiry", "The audit floor"

> **The test.** Each `(cls, band, verb)` keeps two anytime-valid processes on outcome-graded correctness, so the license can be read at any time without a multiple-comparison lie. Grades are Bernoulli, or paired against the person's disposition on the stratum where a stratum exists.
>
> Let `p0` be the pinned baseline and `δ` the ratified margin. With grades `X_i ∈ {0,1}` and a predictable bet `λ_i`:
>
> ```
> E⁺_t = ∏ (1 + λ⁺_i (X_i − p0)),   λ⁺_i ∈ [0, C/p0]              evidence for
> M⁻_t = (1 + M⁻_{t−1})·(1 + λ⁻_t (X_t − p0)),  λ⁻ ∈ [−C/(1−p0), 0]  evidence against
> λ*(p) = (p − p0) / (p0 (1 − p0)),  p estimated predictably and truncated at C
> ```
>
> `E⁺` is an e-process for the null "no better than baseline"; the nonnegative sign of the bet is what makes that hold for the whole composite null and is a law, not a tuning choice. `M⁻` is a Shiryaev–Roberts e-detector, because degradation is a change in a good process, not a fixed hypothesis, and a fixed-start process would be diluted by the good history that preceded the change.
>
> **Promotion** when `min(E⁺_A, E⁺_H) ≥ 1/α_up` and both sides have cleared the sample floor. **Demotion** when `max(M⁻_A, M⁻_H) ≥ 2/α_dn` with `α_dn = 10 α_up`: a bar an order of magnitude closer. Promotion inherits Ville's inequality, `P(∃t : E_t ≥ 1/α) ≤ α`; demotion inherits the e-detector's average-run-length bound, `E_∞[τ] ≥ 1/α_dn`.
>
> **Where the baseline comes from.** `p0` is never estimated from the stream the test consumes. Either it is the lower end of a one-sided 95% Clopper–Pearson interval measured once in the shadow period and pinned by a ratification row, or — preferred, wherever a stratum exists — the test is paired against the person on the stratum, `Z_i = (1{deputy right} − 1{person right} + 1)/2` against `m = 1/2 + δ/2`, which needs no external baseline and does not drift with the case mix.
>
> **Horizons.** Grades enter each process in ascending `(horizon_ns, id)`, never in decision order. The grading function is total: unknown at the horizon grades zero on the promotion side, so nothing is censored and no selection correction is needed. An outcome landing after its horizon writes a `regrade` row that feeds `epoch` and may trigger a demotion review; it never re-enters a process that has passed that horizon, because that would destroy the predictability the bound rests on. The bet `λ_t` is written on the tape before its grade is read, so `factor verify` can recompute the whole process with no model.
>
> **Expiry.** A rung must be re-earned within its window or it drops one, and re-earning resets both processes to their start. Nothing is permanent because it was once approved. Resetting costs error honestly: after `k` epochs the lifetime type-I bound is `k · α_up`, and the account prints it.
>
> **The audit floor.** At rung 4 the sampled fraction is `s(F) = max(sqrt(3/F), 1/64)` at volume `F`. On the square-root branch the arithmetic closes on itself: reviewing `sqrt(3F)` items and finding nothing puts a 95% ceiling of `sqrt(3/F)` on the defect rate, which is the sampling fraction itself — the fraction you sample is the ceiling you can certify. The `1/64` floor binds above `F = 12,288` per period, where the review count returns to growing linearly. The review gets cheaper, never absent.

**Add to §21:**

| id | requires | the planted lie |
|---|---|---|
| F-PREDICT | every `λ_t` on the tape precedes its grade row in horizon order; a re-fold reproduces every e-value bit-identically | a bet computed from the grade it is about to read |
| F-DETECT | a class good for 500 grades then degraded for 40 is demoted; a fixed-start e-process on the same tape is not | demotion by a fixed-start e-process |

**Sources:** [Ramdas, Grünwald, Vovk & Shafer 2023](https://arxiv.org/abs/2210.01948) · [Waudby-Smith & Ramdas, JRSS-B 2024](https://arxiv.org/abs/2010.09686) ([RSS discussion](https://academic.oup.com/jrsssb/article/86/1/1/7043257)) · [Shin, Ramdas & Rinaldo, E-detectors, NEJSDS 2023](https://arxiv.org/abs/2203.03532) · [Rule of three](https://en.wikipedia.org/wiki/Rule_of_three_(statistics)) · [van Tuyl et al. 2009](https://onlinelibrary.wiley.com/doi/10.1111/j.1751-5823.2009.00078.x)

---

## 2 · §12 · The chain hash

**Verdict: holds with correction.** BLAKE3 is a correct and good choice, the `prev ‖ body` construction is safe as written *because* BLAKE3 is not length-extendable, a dependency-free MSVC build exists, and both keyed and derive_key modes earn their place — but for different jobs than the document implies, and `h = BLAKE3(prev ‖ body)` unkeyed leaves the §20 "model as adversary" threat unaddressed.

### 2.1 Suitability

BLAKE3 targets ≥128-bit security for all goals at 32-byte output, is indifferentiable from a random oracle, and — this is the load-bearing part for a chain — **is not length-extendable**, because the root compression is domain-separated by a `ROOT` flag, so a digest cannot be continued into a longer valid one. ([IETF draft-aumasson-blake3-00](https://www.ietf.org/archive/id/draft-aumasson-blake3-00.html))

That is why `h = BLAKE3-256(prev ‖ body)` is safe as written and does not need an HMAC-style wrapper, which the same construction over SHA-256 would.

### 2.2 The construction

Two refinements, both cheap:

- **Length-prefix the body.** `prev` is fixed at 32 bytes, so `prev ‖ body` is unambiguous today, but the moment a second variable-length field joins the preimage it stops being. Write `h = BLAKE3(prev ‖ u64le(len(body)) ‖ body)` and the property is structural rather than accidental.
- **Domain-separate the chains.** The tape, the spool self-chain, the dossier, and the checkpoint manifest are four chains. A row lifted from one must not verify in another. Get this for free from `derive_key`.

### 2.3 Keyed and derive_key: where each belongs

`derive_key(context, key_material)` takes a context string that should be **hardcoded, globally unique, and application-specific**; the context is hashed by an unkeyed instance with `DERIVE_KEY_CONTEXT` and the 32-byte result keys a `DERIVE_KEY_MATERIAL` instance over the material. That is exactly a domain-separation primitive.

```c
/* one machine secret, four independent chain keys, no key management */
blake3_hasher_init_derive_key(&h, "FACTOR 2026-09-08 tape chain v1");
blake3_hasher_update(&h, machine_secret, secret_len);
blake3_hasher_finalize(&h, K_tape, 32);
/* … "FACTOR 2026-09-08 spool chain v1", "… dossier chain v1", "… ckpt manifest v1" */
```

Then the chain step is `blake3_hasher_init_keyed(&h, K_tape)` over `prev ‖ len ‖ body`. Keyed mode is a PRF and a MAC, so an attacker without `K_tape` cannot forge a chain even with full write access to the file.

**This is the point the blueprint is missing.** An unkeyed hash chain is tamper-evident only to a holder of an independent anchor. §20 states "the model as adversary" and §12 gives the anchor as a daily fingerprint published in the account — which detects tampering *at daily granularity*, and only if the account itself is trusted. A keyed chain closes the intraday window: the kernel writes rows with `K_tape`, and if `K_tape` is DPAPI- or TPM-sealed to the hand rather than the kernel, a compromised kernel cannot silently rewrite yesterday's judgments. Recommend keyed mode for the tape and the dossier; **unkeyed** for the spool self-chain, because §4 says a spool must verify alone and lanes are separate producers that must not need a secret.

Keep `factor verify` (§12) able to run in both modes: unkeyed verification proves internal consistency with no secret; keyed verification, run by the hand, additionally proves origin.

### 2.4 The 64-bit id in §5

`id = BLAKE3-64` is a truncation of an XOF output, which is fine cryptographically (every output byte is independently pseudorandom). It is not fine *silently*: birthday collisions land at `≈ n²/2^65`, which is `7e−11` at 50k obligations, `3e−8` at a million, `3e−6` at ten million. Cheap and correct: the ledger's primary index detects it. On insert, if `id` is present but the source coordinates differ, that is a collision — write a `fatal` row rather than merging two obligations into one. Free, and it turns an invisible corruption into a loud one.

### 2.5 Dependency-free C on Windows/MSVC

The official implementation lives in `BLAKE3-team/BLAKE3` under `c/`. It is triple-licensed **CC0-1.0 / Apache-2.0 / Apache-2.0-with-LLVM-exception** — take CC0 and vendor it with no notice obligation.

- **Minimal portable build, three files, zero dependencies:** `blake3.c blake3_dispatch.c blake3_portable.c` (plus `blake3.h`, `blake3_impl.h`) with `-DBLAKE3_NO_SSE2 -DBLAKE3_NO_SSE41 -DBLAKE3_NO_AVX2 -DBLAKE3_NO_AVX512`. Builds under MSVC unchanged. Use this for M0 so the kernel has no build-time dependency at all.
- **With SIMD under MSVC, two ways.** MASM assembly: `blake3_{sse2,sse41,avx2,avx512}_x86-64_windows_msvc.asm`, assembled by `ml64.exe` (verified MASM syntax: `PROC` / `_TEXT SEGMENT ALIGN(16) 'CODE'`). Or C intrinsics: `blake3_sse2.c blake3_sse41.c blake3_avx2.c blake3_avx512.c` — MSVC enables SSE2 and SSE4.1 by default and needs `/arch:AVX2` and `/arch:AVX512` for the other two, compiled as separate translation units. Upstream prefers the assembly ("they perform better, they perform more consistently across different compilers, and they build more quickly").
- Runtime dispatch is automatic via `blake3_dispatch.c`, so the SIMD build still runs on machines lacking AVX-512.
- Multithreading is optional and behind oneTBB; leave it off — chain hashing is inherently serial and the tape rows are small.

**One determinism note.** Runtime SIMD dispatch means the *same input* is hashed by different code paths on different machines. BLAKE3 is specified to produce identical output on all paths, and the upstream `test.py` battery checks this, but §21 should pin it: assert the known-answer vector at boot beside the serve-bytes pin (§7), so a miscompiled AVX-512 path refuses to boot rather than forking the chain.

### Corrected spec text — replaces §12 "Rows" and adds a paragraph

> **Rows.** JSON lines. Every row: `k` (kind), `ms` (steady clock since boot), `t_mono_ns`, the row's fields, `prev`, `h`.
>
> ```
> h = BLAKE3-256-keyed( K_tape ; prev ‖ u64le(len(body)) ‖ body )
> K_c = BLAKE3-derive_key( "FACTOR 2026-09-08 <chain> v1" ; machine_secret )   for each chain c
> ```
>
> The length prefix keeps the preimage unambiguous as fields are added. `derive_key` gives the tape, the dossier, and the checkpoint manifest independent keys from one secret with hardcoded, globally unique context strings, so a row lifted from one chain cannot verify in another. BLAKE3 is not length-extendable — the root compression is domain-separated by a `ROOT` flag — so no HMAC wrapper is needed around `prev ‖ body`.
>
> The **spool self-chain (§4) stays unkeyed**, because a spool must verify alone and a lane producer must hold no secret. The tape is keyed because §20 names the model as an adversary: an unkeyed chain is only tamper-evident to a holder of an independent anchor, and the daily published fingerprint anchors it at daily granularity at best. `K_tape` is sealed to the hand, not the kernel, so a compromised kernel cannot silently rewrite an earlier judgment. `factor verify` runs in both modes: unkeyed it proves internal consistency with no secret; keyed, run by the hand, it additionally proves origin.
>
> Segments rotate at a size bound; a manifest lists segment heads; the chain crosses segments. The head is recovered on open from the last complete row of the last segment, walking back over a torn trailing row and warning about it. A sidecar head file is never truth.
>
> **The hash implementation is pinned like any other.** BLAKE3's official C implementation is vendored (CC0-1.0) and dispatches on runtime SIMD support, so the same bytes traverse different code on different machines. A known-answer vector is asserted at boot beside the serve-bytes pin; a miscompiled vector path refuses to boot rather than forking the chain.

**Add to §5 "Identity":** *`id` is a 64-bit truncation of an XOF output; collisions are expected near `n²/2^65` — about `3e−8` at a million obligations. The primary index makes it loud: an insert whose `id` is present but whose source coordinates differ writes a `fatal` row and never merges.*

**Sources:** [BLAKE3 IETF draft](https://www.ietf.org/archive/id/draft-aumasson-blake3-00.html) · [BLAKE3-team/BLAKE3](https://github.com/BLAKE3-team/BLAKE3) · [`c/README.md`](https://github.com/BLAKE3-team/BLAKE3/tree/master/c) · repo license files verified: `LICENSE_CC0`, `LICENSE_A2`, `LICENSE_A2LLVM`

---

## 3 · §7 and §15 · The trunk against the current llama.cpp API

**Verdict: holds with correction — one caveat is now out of date.** Fork-by-sequence-copy and per-sequence state save/load are real, named, and stable. Per-sequence save **does** include recurrent state. But §7's flat claim that "on a recurrent-hybrid model a fork's state cannot be rewound" is **no longer true as written**: master now carries a bounded rewind, and the blueprint should say what the bound is rather than deny the capability.

### 3.1 The functions

All in `include/llama.h` at `f3f1a8f` (2026-09-08). The `llama_kv_cache_*` and `llama_kv_self_*` spellings are gone from the header; the current API is `llama_memory_*` taking a `llama_memory_t` from `llama_get_memory(ctx)`.

```c
llama_memory_t llama_get_memory(const struct llama_context * ctx);

// Copy all tokens that belong to the specified sequence to another sequence
// p0 < 0 : [0,  p1]      p1 < 0 : [p0, inf)
void llama_memory_seq_cp(llama_memory_t mem, llama_seq_id src, llama_seq_id dst,
                         llama_pos p0, llama_pos p1);

// Removes all tokens that belong to the specified sequence and have positions in [p0, p1)
// Returns false if a partial sequence cannot be removed. Removing a whole sequence never fails
bool llama_memory_seq_rm(llama_memory_t mem, llama_seq_id seq_id,
                         llama_pos p0, llama_pos p1);

void      llama_memory_seq_keep    (llama_memory_t, llama_seq_id);
void      llama_memory_seq_add     (llama_memory_t, llama_seq_id, llama_pos, llama_pos, llama_pos delta);
void      llama_memory_seq_div     (llama_memory_t, llama_seq_id, llama_pos, llama_pos, int d);
llama_pos llama_memory_seq_pos_min (llama_memory_t, llama_seq_id);
llama_pos llama_memory_seq_pos_max (llama_memory_t, llama_seq_id);
bool      llama_memory_can_shift   (llama_memory_t);
void      llama_memory_clear       (llama_memory_t, bool data);

size_t llama_state_seq_get_size (struct llama_context *, llama_seq_id);
size_t llama_state_seq_get_data (struct llama_context *, uint8_t * dst, size_t, llama_seq_id);
size_t llama_state_seq_set_data (struct llama_context *, const uint8_t * src, size_t, llama_seq_id dest);
size_t llama_state_seq_save_file(struct llama_context *, const char * path, llama_seq_id,
                                 const llama_token * tokens, size_t n_token_count);
size_t llama_state_seq_load_file(struct llama_context *, const char * path, llama_seq_id dest,
                                 llama_token * tokens_out, size_t cap, size_t * n_out);

/* extended forms, current master */
#define LLAMA_STATE_SEQ_FLAGS_NONE         0
#define LLAMA_STATE_SEQ_FLAGS_SWA_ONLY     1   /* for backwards-compat */
#define LLAMA_STATE_SEQ_FLAGS_PARTIAL_ONLY 1   /* SWA KV cache or recurrent cache (e.g. Mamba) */
#define LLAMA_STATE_SEQ_FLAGS_ON_DEVICE    2
size_t llama_state_seq_get_size_ext(struct llama_context *, llama_seq_id, llama_state_seq_flags);
size_t llama_state_seq_get_data_ext(struct llama_context *, uint8_t *, size_t, llama_seq_id, llama_state_seq_flags);
size_t llama_state_seq_set_data_ext(struct llama_context *, const uint8_t *, size_t, llama_seq_id, llama_state_seq_flags);
```

Also relevant: `bool llama_model_is_recurrent(model)` and `bool llama_model_is_hybrid(model)` — the kernel can branch on architecture at boot instead of guessing.

### 3.2 Fork cost really is the divergent suffix — but only under one config

§7's "fork cost is the divergent suffix only" is true for attention models **only when the sequences share a KV stream**. In `llama_kv_cache::seq_cp`, if source and destination map to the same stream, the copy is metadata only:

```c
if (s0 == s1) {
    // since both sequences are in the same stream, no data copy is necessary
    // we just have to update the cells meta data
```

Cross-stream, it is a full buffer copy with a hard constraint:

```c
GGML_ASSERT(is_full && "seq_cp() is only supported for full KV buffers");
```

So the trunk **must** run with `llama_context_params.kv_unified = true`. The header itself warns that unified costs performance when sequences do not share a large prefix — which is precisely the trunk's case (they share almost everything), so the trade is in FACTOR's favour. This is a boot assertion, not a preference: forks are free with it and O(context) without it.

### 3.3 The recurrent rewind caveat is now a bound, not a prohibition

Master added `llama_context_params.n_rs_seq`:

```c
uint32_t n_rs_seq;  // number of recurrent-state snapshots per seq for rollback (0 = no rollback) [EXPERIMENTAL]
```

and `llama_memory_recurrent::seq_rm` now has a partial-rewind path:

```c
// partial rollback via per-token snapshot index (bounded by n_rs_seq)
if (0 < p0 && p0 <= cell.pos && p1 > cell.pos) {
    const llama_pos rollback = cell.pos - (p0 - 1);
    const bool pending = rs_idx[seq_id] != 0;   // pending rollback is single-use
    if (!pending && rollback >= 1 && rollback <= (llama_pos) n_rs_seq) {
        set_rs_idx(seq_id, (uint32_t) rollback);
        cell.pos = p0 - 1;
        return true;
    }
    return false;
}
```

Read precisely, the constraints are: rewind at most `n_rs_seq` tokens; **one pending rewind at a time** (a second before the first is consumed by a decode returns false); the recurrent state buffer is `mem_size * (1 + n_rs_seq)` rows, so the snapshot depth is paid in VRAM linearly; and the scheduler must keep the trailing `n_rs_seq + 1` tokens of a sequence in the same ubatch (`split_equal(n_ubatch, true, n_rs_seq > 0 ? n_rs_seq + 1 : 0)`). With `n_rs_seq = 0` the old behaviour returns and any partial `seq_rm` fails.

For hybrid models, `llama_memory_hybrid::seq_rm` tries recurrent first and is explicit about why:

```c
// Try removing from the recurrent cache first since it may fail. If it does
// fail, the cache will not have been mutated.
```

so the failure is atomic across the two caches — the kernel can treat a `false` return as "nothing happened".

**Also correct in §7 but for a different reason:** recurrent `seq_cp` does not copy state, it *aliases* it — `cell_src.seq_id.insert(seq_id_dst)` points the destination's tail at the same cell. Two "forks" of a recurrent trunk share one state until the next decode splits them. A fork that is judged and released without decoding therefore costs nothing; a fork that decodes forces the copy. Worth stating, because it means the VRAM cost of a fork on a recurrent model is deferred, not absent.

### 3.4 Per-sequence state save does include recurrent state — confirmed

`llama_memory_recurrent::state_write_data` serialises the recurrent tensors directly:

```c
io.write_tensor(r_l[il], range.first * r_size_row, buf_size);
io.write_tensor(s_l[il], range.first * s_size_row, buf_size);
io.write_tensor(p_l[il], range.first * p_size_row, range_size * p_size_row);   // PLE conv row
```

and it is snapshot-aware — the row it saves is `rs_idx_cur * size + (cell.src >= 0 ? cell.src : i)`, i.e. the *rolled-back* state if a rewind is pending. On read it resets: `if (n_rs_seq != 0) set_rs_idx(seq_id, 0);`. Two consequences the blueprint should state: a checkpoint taken with a pending rewind saves the rewound state (correct), and a restored sequence has no pending rewind (also correct, but it means a rewind cannot be checkpointed and resumed).

For hybrid models the flag decides how much is written:

```c
void llama_memory_hybrid::state_write(io, seq_id, flags) {
    if ((flags & LLAMA_STATE_SEQ_FLAGS_PARTIAL_ONLY) == 0) { mem_attn->state_write(io, seq_id, flags); }
    mem_recr->state_write(io, seq_id, flags);
}
```

So `flags = 0` (what plain `llama_state_seq_save_file` passes) saves attention **and** recurrent — that is the checkpoint FACTOR wants. `PARTIAL_ONLY` saves only the recurrent/SWA part, for a caller that will re-prefill the attention part.

Restore refuses shared state: `state_read_meta` errors on a `duplicate tail for seq_id`, so a checkpoint of an aliased fork cannot be restored into a context that already has that tail. Checkpoint the root, not an alias.

### 3.5 Checkpoints are version- and build-pinned, and §18's pin pair is too small

`LLAMA_STATE_SEQ_VERSION` is `3`, `LLAMA_SESSION_VERSION` is `10`, and `llama_context::state_seq_load_file` rejects a mismatched magic or version outright. Beyond the version, the blob is raw tensor data whose layout depends on the model, the quantisation, `n_ctx`, `n_seq_max`, `n_rs_seq`, `kv_unified`, `swa_full`, and the backend build. §18 pins "the serve-bytes hash and the weights hash". That pair is insufficient: a llama.cpp upgrade that bumps `LLAMA_STATE_SEQ_VERSION`, or a context-params change, silently invalidates every trunk checkpoint on disk. §15's fallback ("restores the trunk if the model and serve pins match, else boots the twin") will fire *after* a failed load rather than before it.

### Corrected spec text — replaces the §7 "The trunk" paragraph, with additions to §15 and §18

> **The trunk.** One KV-resident context per seat, on the card, never re-read. The root holds the writ's summary, the seat's specifics, and the running record. Forks branch from the root per obligation when it is attended to; a fork reads the obligation's dossier and its neighbourhood, judges, and is released, or lives on while a counterparty conversation is open.
>
> A fork is `llama_memory_seq_cp` on the memory from `llama_get_memory`. **Fork cost is the divergent suffix only, and that is a configuration law, not a hope:** the context runs with `kv_unified = true`, because a same-stream sequence copy updates cell metadata and copies no data, while a cross-stream copy is a full buffer copy that additionally asserts `seq_cp() is only supported for full KV buffers`. The kernel asserts `kv_unified` at boot.
>
> **Rewind is bounded, not absent.** On a recurrent or hybrid model, `llama_memory_seq_rm(mem, seq, p0, p1)` with `p0 > 0` succeeds only if the requested rewind is at most `n_rs_seq` tokens and no rewind is already pending on that sequence; otherwise it returns false and, on a hybrid model, nothing has been mutated in either cache. The kernel sets `n_rs_seq` in the writ, pays `mem_size × (1 + n_rs_seq)` rows of recurrent state for it, and treats a `false` return as a law: **a delayed judgment beyond the snapshot depth is a judgment about now, and the row says so, naming the depth it wanted and the depth it had.** With `n_rs_seq = 0` every partial rewind fails and every delayed judgment is about now.
>
> On a recurrent model `seq_cp` aliases rather than copies: both sequences point at one state cell until one of them decodes. A fork judged and released without a decode costs nothing; a fork that decodes pays for the split then. The VRAM cost of a fork is deferred, not absent.

> **§15 · Checkpoints, added.** A trunk checkpoint is `llama_state_seq_save_file` with `flags = LLAMA_STATE_SEQ_FLAGS_NONE`, which writes the attention cache and the recurrent state together; `LLAMA_STATE_SEQ_FLAGS_PARTIAL_ONLY` writes only the recurrent or SWA part and is not what a checkpoint uses. A checkpoint taken while a recurrent rewind is pending saves the rewound state; a restore always clears the pending rewind, so a rewind cannot be checkpointed and resumed. A restore refuses a sequence whose tail is already occupied, so the root is checkpointed, never an alias.

> **§18 · The pins, amended.** The pin is not a pair but a tuple, minted together and asserted at boot and at every restore against the checkpoint manifest: the serve-bytes hash, the weights hash, the runtime's build identity, `LLAMA_STATE_SEQ_VERSION`, and a hash of the context parameters that determine the state layout — `n_ctx`, `n_seq_max`, `n_rs_seq`, `kv_unified`, `swa_full`, quantisation, and backend. A trunk state file is raw tensor data whose layout depends on all of them, and a runtime upgrade invalidates every checkpoint on disk. The mismatch is detected before the load is attempted, so the twin boots on a pin comparison rather than on a failed read.

**Sources (all read at commit `f3f1a8f2760f28325a5ec20c05b171e5b7c83a29`, 2026-09-08):** [`include/llama.h`](https://github.com/ggml-org/llama.cpp/blob/master/include/llama.h) · [`src/llama-memory-recurrent.cpp`](https://github.com/ggml-org/llama.cpp/blob/master/src/llama-memory-recurrent.cpp) · [`src/llama-memory-hybrid.cpp`](https://github.com/ggml-org/llama.cpp/blob/master/src/llama-memory-hybrid.cpp) · [`src/llama-kv-cache.cpp`](https://github.com/ggml-org/llama.cpp/blob/master/src/llama-kv-cache.cpp) · [`src/llama-context.cpp`](https://github.com/ggml-org/llama.cpp/blob/master/src/llama-context.cpp)

---

## 4 · §11 · The two-process egress law on Windows

**Verdict: refuted as stated, repairable.** The law is right and achievable. The *mechanism* named in §11 and §21 — "the kernel's binary links no network module and refuses to start if one is present in its process" — is not a boundary and F-EGRESS as written does not falsify anything. A module gate is a lint check that a hostile or merely creative process walks around in a dozen documented ways.

### 4.1 Why the module gate is not a fence

- **The socket API is not the socket.** Every Winsock call bottoms out in `NtDeviceIoControlFile` against `\Device\Afd`. A process can open that device with `NtCreateFile` and drive a full TCP handshake and HTTP request with **no `ws2_32.dll` or `mswsock.dll` in the module list at all** — this is a published technique with working code, used in the wild precisely to defeat module- and hook-based detection. ([x86matthew, *NTSockets*](https://www.x86matthew.com/view_post?id=ntsockets); [Leftarcode, *Under the Hood of AFD.sys, Part 3: Sending TCP packets*](https://leftarcode.com/posts/afd-reverse-engineering-part3/))
- **Bytes leave without a socket.** A named pipe opened as `\\server\pipe\x` travels over SMB through the redirector. `WinHttpRequest` and BITS are out-of-process COM services that move bytes on your behalf. Writing a file into a synced folder is egress. None of these put a network module in the kernel's address space.
- **Modules load late.** The gate runs at boot; `LoadLibrary` runs whenever.

So §21's F-EGRESS ("the kernel's process holds no network module") tests a property that is neither necessary nor sufficient for the law it claims to falsify.

### 4.2 The options, ranked, with what each actually stops

| mechanism | denies | self-applicable | admin | what defeats it |
|---|---|---|---|---|
| module gate | nothing | yes | no | `\Device\Afd` directly; late `LoadLibrary`; COM; SMB |
| job object net rate control | throttles outbound bandwidth only | yes | no | it is rate control, not denial; not a boundary |
| restricted token / low IL | not network | only via re-exec | no | integrity level does not gate socket creation |
| firewall rule keyed by exe | outbound to remote hosts | no | **yes** | admin can remove it; loopback is not filtered by default; another exe |
| **AppContainer, zero capabilities** | **all sockets, including loopback** | **yes, by re-exec at startup** | **no** | admin; a helper process outside the container |
| WFP filter on `ALE_APP_ID` | all sockets for that image | no | **yes** | admin removes the filter; a copy of the binary at another path |
| server silo / network compartment | everything | no | **yes** | admin |

**AppContainer with no capabilities is the strongest thing a single binary can apply to itself without administrator rights**, and it is the only one on the list that also denies loopback. Enforcement is in the kernel, in WFP, keyed on the package SID in the token — not on a module list:

- The **"Block Outbound Default Rule"** in the `MICROSOFT_DEFENDER_SUBLAYER_WSH` sublayer matches `FWPM_CONDITION_ALE_PACKAGE_ID` at `FWPM_LAYER_ALE_AUTH_CONNECT_V4/V6` and `FWPM_LAYER_ALE_AUTH_RECV_ACCEPT_V4/V6`, and unlike most WFP defaults its action is **block**, not permit. A socket in an AppContainer is denied unless a higher-priority permit filter matches.
- The permits require the capability SIDs `internetClient` (S-1-15-3-1), `internetClientServer` (S-1-15-3-2), or `privateNetworkClientServer` (S-1-15-3-3). Grant none and none match.
- **Loopback is blocked too**, by a separate filter on `FWP_CONDITION_FLAG_IS_LOOPBACK`, and the exemption (`Add-AppModelLoopbackException` / `CheckNetIsolation LoopbackExempt`) is administrator-only. Note the failure mode: blocked loopback sockets **time out** rather than failing fast, because WFP defers the same-package decision to the receive layer.

([Project Zero, *Understanding Network Access in Windows AppContainers*, 2021](https://projectzero.google/2021/08/understanding-network-access-windows-app.html); [Microsoft, *Troubleshooting UWP App Connectivity Issues in Windows Firewall*](https://learn.microsoft.com/en-us/windows/security/operating-system-security/network-security/windows-firewall/troubleshooting-uwp-firewall))

The precedent is not theoretical. **Chromium runs its renderer in exactly this configuration** — a lowbox/AppContainer token layered over a restricted token, deliberately omitting the internet client capability — and talks to its broker over local IPC. ([Chromium sandbox design](https://chromium.googlesource.com/chromium/src/+/refs/heads/main/docs/design/sandbox.md))

**Mechanics.** `CreateAppContainerProfile(name, …, NULL capabilities, 0)` → `DeriveAppContainerSidFromAppContainerName` → `InitializeProcThreadAttributeList` → `UpdateProcThreadAttribute(PROC_THREAD_ATTRIBUTE_SECURITY_CAPABILITIES, &SECURITY_CAPABILITIES{sid, NULL, 0})` → `CreateProcessW(..., EXTENDED_STARTUPINFO_PRESENT, ...)`. The binary re-executes itself with a sentinel argument; the outer process is the launcher and exits. ([CreateAppContainerProfile](https://learn.microsoft.com/en-us/windows/win32/api/userenv/nf-userenv-createappcontainerprofile); [Implementing an AppContainer](https://github.com/MicrosoftDocs/win32/blob/docs/desktop-src/SecAuthZ/implementing-an-appcontainer.md))

**The one real risk, and it must be tested at M0 rather than discovered at M1: CUDA inside an AppContainer.** AppContainer is deny-by-default on every named object, and the GPU stack reaches a lot of them — `nvcuda.dll`, the driver store, the D3DKMT interfaces, the adapter device objects. This may simply not work on the target box. Test it before the two-process split is designed around it. If it fails, the fallback is layered: (i) restricted token plus low integrity plus the module gate as a lint, plus (ii) an administrator-installed WFP block filter on `FWPM_CONDITION_ALE_APP_ID` for the kernel's image path, installed once and audited, plus (iii) the egress law re-anchored on the hand's ledger, which is where it is actually checkable.

### 4.3 The kernel-to-hand pipe

Named pipes are the right channel — they are NPFS objects, not sockets, so they survive an AppContainer that has no network capability, and they carry the caller's token for verification. Five things the spec should require:

1. **`FILE_FLAG_FIRST_PIPE_INSTANCE`.** Without it, a hostile process that wins the race creates the pipe first and the kernel connects to *it*. The documented behaviour is what you want: "creation of the first instance succeeds, but creation of the next instance fails with `ERROR_ACCESS_DENIED`". Squatting turns into a loud startup failure.
2. **`PIPE_REJECT_REMOTE_CLIENTS`.** "Connections from remote clients are automatically rejected." The default is `PIPE_ACCEPT_REMOTE_CLIENTS`, which exposes the valve over SMB/IPC$ subject only to the DACL.
3. **An explicit SDDL.** The default descriptor "grant[s] full control to the LocalSystem account, administrators, and the creator owner … [and] read access to members of the Everyone group and the anonymous account" — never acceptable for the valve. Something like:
   ```
   D:P(A;;GA;;;OW)(A;;GA;;;SY)(A;;GRGW;;;S-1-15-2-<kernel package SID>)(D;;GA;;;NU)(D;;GA;;;AN)
   ```
   granting the kernel's AppContainer package SID read/write, denying `NU` (NETWORK) and `AN` (ANONYMOUS), and inheriting nothing. AppContainer access requires the object's DACL to name the package SID (or `AC`, S-1-15-2-1, ALL APPLICATION PACKAGES); prefer the specific package SID.
4. **Mutual identification after connect.** The hand calls `GetNamedPipeClientProcessId` and checks the client's image path and signature; the kernel calls `GetNamedPipeServerProcessId` and does the same. Open the client end with `SECURITY_SQOS_PRESENT | SECURITY_IDENTIFICATION` so a hostile server cannot impersonate the kernel.
5. **AppContainer pipe naming.** Under an AppContainer the `\\.\pipe\LOCAL\` prefix resolves into the container's private object namespace; the global `\\.\pipe\<name>` path is reachable only when the DACL names the package SID. Pick one and assert it at M3 rather than at M0.

([CreateNamedPipe](https://learn.microsoft.com/en-us/windows/win32/api/winbase/nf-winbase-createnamedpipea); [Named Pipe Security and Access Rights](https://learn.microsoft.com/en-us/windows/win32/ipc/named-pipe-security-and-access-rights); [The Old New Thing, *What are these SIDs of the form S-1-15-2-xxx?*](https://devblogs.microsoft.com/oldnewthing/20220502-00/?p=106550))

### 4.4 What an attacker on the same box can still do

Say it in §20 rather than let a reader infer a guarantee that is not there.

- **Administrator or SYSTEM removes the fence.** Lifts the WFP block, adds a loopback exemption, injects into the kernel, reads the trunk, or edits the writ. AppContainer is not a defence against a local administrator and never claims to be.
- **A helper outside the container.** The kernel cannot open a socket, but if it can create a process outside its own container — or write to a path something else executes, or drop a scheduled task, or write into a synced folder — bytes leave. **Remove the ability, don't detect it:** launch the kernel with `PROC_THREAD_ATTRIBUTE_CHILD_PROCESS_POLICY = PROCESS_CREATION_CHILD_PROCESS_RESTRICTED`, and note the tension with §2's "call organs as subprocesses" — organs must then be launched by the hand or a launcher, not by the kernel.
- **The hand is the real perimeter.** Everything the kernel wants to send goes through the hand, so the hand's endpoint allowlist, byte counter and effect registry are the enforcement, and the kernel's own inability to open a socket is defence in depth, not the defence.
- **Covert channels remain.** Timing, file names, the brief's own content. Unbounded and out of scope; say so.

### Corrected spec text — replaces the §11 "Two processes" paragraph and "Egress", plus §21 F-EGRESS

> **Two processes, one contract.** The kernel emits typed effects over a local named pipe. The hand executes them. The hand is the only process with a socket, and it cannot originate an effect.
>
> **The kernel's inability to reach the network is enforced by the operating system, not by a module list.** At startup the kernel creates an AppContainer profile with **zero capabilities**, derives its package SID, and re-executes itself into it via `PROC_THREAD_ATTRIBUTE_SECURITY_CAPABILITIES`. Windows Filtering Platform then denies every socket the process attempts — outbound, inbound, and loopback — at the ALE layers, keyed on `FWPM_CONDITION_ALE_PACKAGE_ID` against the Block Outbound Default Rule, because none of the `internetClient`, `internetClientServer` or `privateNetworkClientServer` capability SIDs is present to match a permit. This needs no administrator and no installer. The same launch sets `PROCESS_CREATION_CHILD_PROCESS_RESTRICTED`, so the kernel cannot escape by spawning a helper; organs are launched by the launcher, never by the kernel.
>
> The module gate is retained as a **lint**, not as the fence, and the header row says so. A module list is not a boundary: every Winsock call bottoms out in `NtDeviceIoControlFile` against `\Device\Afd`, which a process can drive with no networking DLL loaded at all; modules can be loaded after the gate runs; and bytes can leave through SMB, an out-of-process COM service, or a synced folder without any socket in this address space.
>
> **The pipe.** The hand creates it with `FILE_FLAG_FIRST_PIPE_INSTANCE`, so a squatter causes a loud startup failure rather than a silent interposition, and with `PIPE_REJECT_REMOTE_CLIENTS`, because the default accepts remote clients over IPC$. The descriptor is explicit — the default grants read to Everyone and to anonymous — and names the kernel's AppContainer package SID, denying `NU` and `AN`. Both ends identify each other after connect by `GetNamedPipeClientProcessId` / `GetNamedPipeServerProcessId` and an image check; the kernel opens its end with `SECURITY_IDENTIFICATION` so a hostile server cannot impersonate it.
>
> **Egress.** The hand counts every outbound byte per endpoint per row and refuses any host not in the writ's allowlist. The kernel's egress is zero, and the header row prints which of the two mechanisms is in force: `os-enforced` when the AppContainer launch succeeded, `lint-only` when it did not. The account prints the same word every week. A degraded fence that nobody can see is worse than no fence.
>
> **What this does not stop.** A local administrator or SYSTEM: lifts the filter, injects, reads the trunk, edits the writ. AppContainer is not a defence against the machine's owner and does not claim to be. Covert channels — timing, file names, the content of a permitted brief — are unbounded and out of scope. The hand's allowlist and byte ledger are the perimeter; the kernel's inability to open a socket is depth behind it.
>
> **A note on the card.** AppContainer is deny-by-default on every named object, and the GPU stack touches many. Whether the resident model can run on the card inside the container is measured at M0, on the target machine, before the two-process split is built on top of it. If it cannot, the kernel runs under a restricted token at low integrity with an administrator-installed WFP block filter on `FWPM_CONDITION_ALE_APP_ID` for its image path, the header row says `wfp-installed` or `lint-only`, and the difference is never silent.

> **§21, F-EGRESS replaced.**
>
> | id | requires | the planted lie |
> |---|---|---|
> | F-EGRESS | a probe compiled into the kernel opens a socket by three routes — `ws2_32`, a raw `\Device\Afd` IOCTL, and a loopback connect to the hand's own port — and all three are refused by the OS; the hand's egress ledger equals the sum of its rows | a module-list check standing in for the OS refusal |

**Sources:** [Project Zero, AppContainer network access](https://projectzero.google/2021/08/understanding-network-access-windows-app.html) · [Chromium sandbox design](https://chromium.googlesource.com/chromium/src/+/refs/heads/main/docs/design/sandbox.md) · [CreateAppContainerProfile](https://learn.microsoft.com/en-us/windows/win32/api/userenv/nf-userenv-createappcontainerprofile) · [Implementing an AppContainer](https://github.com/MicrosoftDocs/win32/blob/docs/desktop-src/SecAuthZ/implementing-an-appcontainer.md) · [CreateNamedPipe](https://learn.microsoft.com/en-us/windows/win32/api/winbase/nf-winbase-createnamedpipea) · [Named Pipe Security and Access Rights](https://learn.microsoft.com/en-us/windows/win32/ipc/named-pipe-security-and-access-rights) · [FwpmFilterAdd0](https://learn.microsoft.com/en-us/windows/win32/api/fwpmu/nf-fwpmu-fwpmfilteradd0) · [UWP firewall troubleshooting](https://learn.microsoft.com/en-us/windows/security/operating-system-security/network-security/windows-firewall/troubleshooting-uwp-firewall) · [x86matthew, NTSockets](https://www.x86matthew.com/view_post?id=ntsockets) · [Leftarcode, AFD.sys part 3](https://leftarcode.com/posts/afd-reverse-engineering-part3/)

---

## 5 · §5 and §19 · The memory-mapped fixed-record ledger

**Verdict: holds with correction, plus one arithmetic error.** The design is sound and, because the ledger is a fold, it needs **no journal**. But the struct is not 128 bytes, the record is not safe to read concurrently as written, and the durability story needs three sentences it does not have.

### 5.1 The struct is 120 bytes, not 128

Counted field by field: eight `uint64_t` (64) + `int64_t amount_fix` (8) + three `float` (12) + three `uint32_t` (12) + `uint16_t flags` (2) + six `uint8_t` (6) = **118 bytes**, `_pad[14]` ending at offset 118, rounded to **120** by the 8-byte alignment. Confirmed by layout computation. §5 says "128 bytes, fixed" and "two cache lines". `_pad` must be **24**, which lands exactly on 128 with no implicit tail padding.

While fixing it, two changes earn their bytes:

- **`float` margins contradict §19.** §19 says "fixed-point amounts, never float accumulation" and "every threshold pinned in the writ", and then §5 stores the three margins that cross the gate as `float`. Store them as `int16_t` in units of 1/1024 logit. This is not tidiness — see §6 below, it is the mechanism that makes the determinism law true.
- **A seqlock, because the console reads this map while the kernel writes it.** §2 gives the console the ledger; §5 memory-maps it. A 128-byte record is written by many stores, so a reader can observe a half-updated record with no undefined behaviour and no warning. A 32-bit sequence counter costs 4 bytes and is the standard fix.

```c
struct Obligation {                   // 128 bytes exactly, versioned by the header
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
  uint32_t seq;           // seqlock: even = stable, odd = being written
  int16_t  m_hand, m_check, m_guard;   // fixed point, 1/1024 logit; never float
  uint16_t tie;           // times a margin landed inside the pinned tie band
  uint32_t cls;           // decision class, from the writ
  uint32_t band;          // margin band at last judgment
  uint32_t seat;          // who holds it: a worker pool, a human seat, 0 unassigned
  uint16_t flags;
  uint8_t  state;         // OPEN HELD WAITING DRAFTED STAGED DONE ASKED PASSED CLOSED
  uint8_t  verb;
  uint8_t  reason;
  uint8_t  gear;          // 0 code · 1 reflex · 2 fast · 3 deep · 4 human
  uint8_t  kind;          // 0 structured · 1 projected · 2 self
  uint8_t  rung;
  uint8_t  _pad[24];
};
_Static_assert(sizeof(struct Obligation) == 128, "one obligation is two cache lines");
```

### 5.2 In-place update: what is atomic and what is not

Three different questions live under "atomic", and the blueprint conflates them.

**Against a concurrent reader (the console).** x86-64 gives you an aligned 8-byte store, and Win32 documents "atomic access to properly aligned 32-bit and pointer-sized values". Nothing gives you 128 bytes. Use a seqlock, which is four lines and needs no lock:

```c
/* writer, single */
r->seq++;                       __atomic_thread_fence(__ATOMIC_RELEASE);   /* now odd */
/* … mutate the record … */
__atomic_thread_fence(__ATOMIC_RELEASE);   r->seq++;                       /* now even */

/* reader, any number */
do { s0 = __atomic_load_n(&r->seq, __ATOMIC_ACQUIRE);
     if (s0 & 1) continue;
     memcpy(&snap, r, sizeof snap);
     __atomic_thread_fence(__ATOMIC_ACQUIRE);
} while (__atomic_load_n(&r->seq, __ATOMIC_ACQUIRE) != s0);
```

**Against power loss.** A 128-byte record aligned from offset 0 never straddles a 512-byte or 4096-byte sector, so *if* sector writes are all-or-nothing, no record is ever torn — though a page flush of 32 records can still land as a mixture of old and new records, each individually intact. **Do not build on this.** SQLite, which has spent twenty years on exactly this question, "never assumes atomic page writes in its default configurations", and its `POWERSAFE_OVERWRITE` property — that a sector write completes once started — is an *opt-in claim about the device*, not a platform guarantee. ([SQLite, Device Characteristics](https://sqlite.org/c3ref/c_iocap_atomic.html); [SQLite, Powersafe Overwrite](https://sqlite.org/psow.html))

**Against the OS lying about durability.** `FlushViewOfFile` "initiates writing of dirty pages within that range to the disk", but "does not flush the file metadata, and it does not wait to return until the changes are flushed from the underlying hardware disk cache and physically written to disk. To flush all the dirty pages plus the metadata for the file and ensure that they are physically written to disk, call `FlushViewOfFile` and then call the `FlushFileBuffers` function." So `FlushViewOfFile` alone is not a barrier and neither call orders anything by itself. ([Microsoft, FlushViewOfFile](https://learn.microsoft.com/en-us/windows/win32/api/memoryapi/nf-memoryapi-flushviewoffile))

### 5.3 No journal. The tape already is one.

§2 lists the ledger as a **fold**, §8 says every fold is a deterministic reduction over the tape and rebuildable from it, and §13 says the state fold reduces obligation/verb/staged/executed/reversed/outcome rows into the ledger and its indexes. A journal would be a second write-ahead log in front of a write-ahead log. What the ledger needs is not durability but a **trustworthy answer to "how far along the tape is this map?"** — and then it can be rebuilt from there.

**The scheme, in full:**

1. The ledger file is a header page (4096 bytes, two 64-byte stamp slots A and B) followed by the record array, 128-byte aligned from a 4096-byte offset.
2. A stamp is `{ uint64 gen; uint64 tape_head_offset; uint8 tape_head_hash[32]; uint64 n_records; uint8 blake3_16[16] }` — a monotone generation, the tape head it is folded from, and a checksum over the other fields.
3. Commit, periodically and at clean shutdown: `FlushViewOfFile(records)` → `FlushFileBuffers(hFile)` → write the stamp into the *older* of the two slots with `gen = max+1` → `FlushViewOfFile(header)` → `FlushFileBuffers(hFile)`. The stamp advances only after the data it describes is durable; the two slots mean a torn stamp write cannot destroy the previous one.
4. On open: read both slots, discard any whose checksum fails, take the higher `gen`. If neither validates, or the stamped head is behind the tape head, **re-fold forward from the stamped head** (or from zero). This is not an error path; it is the normal path after any unclean exit, and it is exactly the rollback machinery §15 already requires. The receipt is a `replay` row saying how far it re-folded.
5. Crash safety follows without any assumption about sector atomicity: the worst case is that the record array contains a mixture of states from somewhere between stamp `g` and stamp `g+1`, and re-folding from `g` overwrites all of it deterministically.

The only real cost is bounding the re-fold: commit at every checkpoint (§15 already budgets under 200 ms of checkpoint outage) and the re-fold is bounded by one checkpoint interval of tape.

**Two Windows details worth a line each.** `CreateFileMapping` with a size larger than the file grows the file and zero-fills the tail, so growth is a map/unmap cycle with the record count in the stamp as the authority, never the file size. And "when modifying a file through a mapped view, the last modification timestamp may not be updated automatically" — so nothing may key off the ledger file's mtime.

**Order-independent digest.** §5 promises the replay is "proven by an order-independent digest" and never says what one is. XOR- or sum-of-hashes is order-independent but cancels duplicates. The simple correct answer is already elsewhere in the document: §19 mandates walking sorted by id, ids are unique, so hash the records in ascending `id` order. Deterministic, collision-safe, order-independent by construction.

### Corrected spec text — additions to §5 after "Revision", and to §19

> **The record and its readers.** The record is 128 bytes exactly, asserted at compile time; `_pad` is 24 bytes, not 14. Margins are `int16_t` in units of 1/1024 logit, never `float`, because §19's determinism law is about the numbers that cross the gate. The console reads this map while the kernel writes it, so every record carries a 32-bit sequence counter: the writer makes it odd, mutates, makes it even; a reader retries while it is odd or changed. Nothing on this map is 128-byte atomic — Win32 guarantees atomicity only for properly aligned 32-bit and pointer-sized values — and a design that hopes otherwise reads half a record without saying so.
>
> **Durability without a journal.** The ledger is a fold; the tape is already the write-ahead log; a journal in front of it would be a second one. The file is a 4096-byte header holding two checksummed stamp slots, then the record array. A stamp is a monotone generation, the tape head the map was folded from, the record count, and a checksum. A commit writes the records, calls `FlushViewOfFile` **and then** `FlushFileBuffers` — the first "does not wait to return until the changes are flushed from the underlying hardware disk cache", so it is not a barrier alone — then writes the stamp into the older slot and flushes again. The stamp only ever advances behind durable data.
>
> On open, the higher-generation stamp that checksums is the truth; if neither checksums, or the stamped head is behind the tape head, the ledger re-folds forward from the stamped head and writes a `replay` row saying how far. This is the normal path after an unclean exit, not an error path, and it holds without assuming that a sector write is all-or-nothing — an assumption SQLite declines to make by default and FACTOR declines with it. Re-fold cost is bounded by the commit interval, which is the checkpoint interval.
>
> The order-independent digest that proves a replay is the chain hash of every record taken in ascending `id` order, which §19 already mandates for every walk.

**Sources:** [FlushViewOfFile](https://learn.microsoft.com/en-us/windows/win32/api/memoryapi/nf-memoryapi-flushviewoffile) · [Interlocked Variable Access](https://learn.microsoft.com/en-us/windows/win32/sync/interlocked-variable-access) · [SQLite Device Characteristics](https://sqlite.org/c3ref/c_iocap_atomic.html) · [SQLite Powersafe Overwrite](https://sqlite.org/psow.html) · [SQLite Atomic Commit](https://sqlite.org/atomiccommit.html)

---

## 6 · §19 · Determinism on the CUDA backend

**Verdict: refuted as stated.** "Two runs over the same spools and writ produce byte-identical verb rows" is not obtainable from llama.cpp's CUDA backend as a property of the logits, and no flag exists to buy it. It **is** obtainable as a property of the verb rows, and the way to get it is to stop asking the GPU for it.

### 6.1 What is actually true, verified in the tree

At master `f3f1a8f` (2026-09-08):

- **There is no deterministic mode.** `grep -rin "determinis"` over `ggml/src/ggml-cuda`, `common/arg.cpp` and `docs/` finds no flag, no env var, no CMake option. PR #16016, *Deterministic inference mode (CUDA): RMSNorm, MatMul, Attention, KV-cache*, which proposed `-DGGML_DETERMINISTIC=ON` / `GGML_DETERMINISTIC=1` / `--deterministic`, is **open, draft, and last touched 2025-09-15** — a year stale, with a maintainer objection on record to maintaining batch-invariance guarantees at all. Nothing has replaced it. ([PR #16016](https://github.com/ggml-org/llama.cpp/pull/16016))
- **Run-to-run at a fixed batch composition is almost certainly bit-identical, but is not promised.** There is no `atomicAdd` in the matmul or attention kernels — `mmq.cu`, `mmvq.cu`, `mmf.cu`, `mmvf.cu`, `fattn*.cu`, `fattn-common.cuh` are all clean. Flash-attention's stream-K combine uses an explicit ordered fixup kernel (`flash_attn_stream_k_fixup_uniform` / `_general`), not atomics, so its reduction order is fixed by the grid rather than by scheduling. The only `atomicAdd` in the whole CUDA backend is in `allreduce.cu` (multi-GPU), `count-equal.cu` (integer, associative), and `top-k.cu` (integer counters) — and `top-k.cu` explicitly asks CUB for `cuda::execution::determinism::not_guaranteed`, which is fine for a sampler and would not be fine on the margin path.
- **It is emphatically not batch-invariant, and that is the failure mode that will actually bite.** The same tokens produce different logits depending on how they were batched — this is the well-documented root cause of nondeterminism in every LLM serving stack, because normalization, matmul and attention all change floating-point reduction order with batch shape, and floating-point addition is not associative. ([Thinking Machines Lab, *Defeating Nondeterminism in LLM Inference*, 2025](https://thinkingmachines.ai/blog/defeating-nondeterminism-in-llm-inference/))

FACTOR is *especially* exposed to this, because §3 says the seam walks at sub-second cadence and §7 says one forward pass per instant on a fork. How many obligations ripen in the same tick determines the batch, and the batch determines the logits. A replay that ripens them differently — and it will, because a replay has no wall clock — changes the margins.

Beyond batch shape, the logits also move with: `n_batch` / `n_ubatch` and how a prompt is chunked; the KV cache contents and stream layout (`kv_unified`, `swa_full`, `n_rs_seq`); the GPU model and SM count, since the stream-K grid is sized from it; the driver and cuBLAS version, since `cublasGemmEx` / `cublasGemmStridedBatchedEx` pick algorithms heuristically; multi-GPU split; and the environment — `GGML_CUDA_FORCE_MMQ`, `GGML_CUDA_FORCE_CUBLAS`, `GGML_CUDA_CUBLAS_COMPUTE_TYPE`, `GGML_CUDA_USE_GRAPHS`, `GGML_CUDA_DISABLE_FUSION`, `GGML_CUDA_USE_CUB`, `GGML_CUDA_MAX_STREAMS`.

### 6.2 The fix: quantize the margin and pin the tie band

Determinism of *decisions* does not require determinism of *logits*. It requires that the map from logits to decisions be insensitive to the last few bits. Two pinned constants do it:

- **Quantize.** The margin crossing the gate is `int16_t` in units of `2^-10` logit (§5 above). A wobble of `1e-5` cannot move a quantized value.
- **Refuse ties.** If `|m − θ| < ε_tie` for a pinned `ε_tie` (one or two quanta), the gate takes the **conservative** branch — HOLD — and writes reason `tie`, incrementing the record's `tie` counter. The measure-zero band where quantization could still flip becomes a named, counted, always-safe outcome instead of a silent coin flip.

Then a replay reproduces the verb rows exactly whenever the margins land in the same quantum, which is overwhelmingly the common case, and where they do not the row already said `tie` and the decision was the same anyway. The determinism law becomes a property FACTOR builds rather than one it hopes the vendor supplies, which is the register the rest of the document is written in.

Two supporting requirements: **pin the batch** (a replay must reconstruct the same fork-batch composition from the tape, so the `verb` row records the batch id and the fork's position within it), and **pin the environment** (the boot pin covers the CUDA runtime/driver version, the device name and SM count, and every `GGML_CUDA_*` variable actually set — a changed value is a retune, exactly as a changed serve byte is).

### 6.3 What §19 should say honestly

The current text implies a guarantee that would fail on the first replay after a driver update. Replace it.

### Corrected spec text — replaces §19 "Determinism laws"

> **Determinism laws.** Fixed-point amounts, never float accumulation. Every walk sorted by id, never by hash order. Every threshold pinned in the writ. A decode failure is fatal with a row, never a stale margin.
>
> **What is deterministic is the decision, not the logit, and the difference is a law rather than an apology.** The resident judge runs on a GPU. Logits from the CUDA backend are not batch-invariant: the same tokens give different last bits depending on how many other tokens shared the forward pass, because reduction order changes with shape and floating-point addition is not associative. They also move with the ubatch split, the KV layout, the device's SM count, the driver and cuBLAS version, and the `GGML_CUDA_*` environment. As of 2026-09-08 llama.cpp offers no deterministic mode; the pull request that proposed one has been an unmerged draft for a year. Anyone who reads "byte-identical" as a claim about logits will be wrong on the first driver update.
>
> So FACTOR does not ask the card for determinism. It makes the decision insensitive to the card:
>
> - the three margins are quantized to `int16` in units of `2^-10` logit before they touch the gate, and only the quantized value is written to the ledger and the tape;
> - a margin within the pinned tie band `ε_tie` of any threshold takes the conservative branch — HOLD — and writes reason `tie` with a counter on the record, so the region where arithmetic could decide is a named, counted, always-safe outcome rather than a silent one;
> - the `verb` row records the batch it was judged in and its position within that batch, so a replay reconstructs the same batch composition rather than re-deriving one from a clock it no longer has;
> - the boot pin covers the CUDA runtime and driver version, the device name and SM count, and every `GGML_CUDA_*` variable set in the environment, alongside the serve-bytes and weights hashes. A changed value is a retune, exactly as a changed serve byte is.
>
> **The law, restated:** two runs over the same spools, writ, and pins produce byte-identical **verb rows**, proven by a plan hash on the account. Two runs across different pins produce verb rows that may differ only where a margin crossed a quantum, and every such row was already written as `tie`. The account prints the tie count per class; a class whose tie rate climbs is a class whose thresholds are badly placed, and that is a finding, not a defect in the machine.
>
> The lattice, if a pressure field is added, batches without changing arithmetic.

**Add to §21:**

| id | requires | the planted lie |
|---|---|---|
| F-QUANTA | replay under a perturbed batch composition reproduces every verb row; rows that differ carry reason `tie` and no other | compare raw logits and call the difference a pass |

**Sources:** llama.cpp master `f3f1a8f2760f28325a5ec20c05b171e5b7c83a29`, 2026-09-08 — `ggml/src/ggml-cuda/*` (no determinism flag, no `atomicAdd` in matmul/attention, `top-k.cu:21` `determinism::not_guaranteed`), `common/arg.cpp` (no `--deterministic`) · [PR #16016, open draft since 2025-09-15](https://github.com/ggml-org/llama.cpp/pull/16016) · [Thinking Machines Lab, *Defeating Nondeterminism in LLM Inference*](https://thinkingmachines.ai/blog/defeating-nondeterminism-in-llm-inference/) · [Simon Willison's summary](https://simonwillison.net/2025/Sep/11/defeating-nondeterminism/)

---

## Summary of verdicts

| item | section | verdict | the load-bearing correction |
|---|---|---|---|
| 1 | §10 license test | holds with correction | one-sided sign law on the bet; frozen or paired baseline; demotion is an e-detector, not an e-process; horizon-ordered, total, never-retro grading; `min` for the both-sides floor |
| 2 | §12 chain hash | holds with correction | BLAKE3 is right and not length-extendable; length-prefix the body; `derive_key` per chain; key the tape (unkeyed spool); vendor the 3-file portable C build under CC0 |
| 3 | §7, §15 trunk | holds with correction | `llama_memory_*` API confirmed; `kv_unified` is a boot assertion; recurrent rewind is bounded by `n_rs_seq`, not impossible; per-seq save does include recurrent state; the pin pair must become a tuple |
| 4 | §11 egress law | **refuted as stated** | the module gate is not a boundary; re-exec into a zero-capability AppContainer is; F-EGRESS must test the OS refusal, not the module list |
| 5 | §5, §19 ledger | holds with correction | the struct is 120 bytes, not 128; seqlock for readers; no journal — two checksummed stamp slots plus re-fold from the tape |
| 6 | §19 determinism | **refuted as stated** | no deterministic mode exists in llama.cpp; quantize the margin and pin a tie band, and the law becomes true by construction |
