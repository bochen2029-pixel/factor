# O3 · DATA FORMATS AND LAYOUTS — checked by running code

Reviewer O3. Target: `C:\FACTOR\BLUEPRINT.md` v0.1, sections 4, 5, 12, 21.
Machine: Windows 11, Python 3.13.2, MSVC 19.44 (VS 2022 Community, `/std:c++20`),
g++ 13.3.0 (WSL Ubuntu 24.04), Node v24.16.0 (`JSON.stringify` comparison only).
`blake3` package NOT installed; the chain harness substitutes
`hashlib.blake2b(digest_size=32)` and says so on every run.

**Headline: §5's `struct Obligation` is 120 bytes, not 128.** Two compilers on
two ABIs agree. Everything else below is underspecification, not error — but
four of the gaps (canonical JSON, the spool's missing hash field, `ms` inside a
hashed body, the missing currency) will each produce a shipped bug.

---

## 1 · Layout check — FAIL as written, corrected pad found

`python C:/FACTOR/tests/check_layout.py` → **exit 1**

```
claim in section 5 : sizeof == 128 ('two cache lines')
measured           : sizeof == 120
VERDICT            : FAIL
```

Field offsets (identical under ctypes/Win64, MSVC/Win64 and g++/SysV-x86-64):

| field | off | size | field | off | size |
|---|---:|---:|---|---:|---:|
| `id` | 0 | 8 | `cls` | 84 | 4 |
| `party` | 8 | 8 | `band` | 88 | 4 |
| `opened_ns` | 16 | 8 | `seat` | 92 | 4 |
| `due_ns` | 24 | 8 | `flags` | 96 | 2 |
| `horizon_ns` | 32 | 8 | `state` | 98 | 1 |
| `blocked_by` | 40 | 8 | `verb` | 99 | 1 |
| `src_rev` | 48 | 8 | `reason` | 100 | 1 |
| `judged_rev` | 56 | 8 | `gear` | 101 | 1 |
| `amount_fix` | 64 | 8 | `kind` | 102 | 1 |
| `m_hand` | 72 | 4 | `rung` | 103 | 1 |
| `m_check` | 76 | 4 | `_pad` | 104 | 14 → **24** |
| `m_guard` | 80 | 4 | | | |

`rung` ends at 104. `_pad[14]` carries the record to 118; `alignof == 8` rounds
the total to **120**. Internal alignment holes: **0** — the field order is
already dense, which is why nothing but the pad needs to change.

Eight pad lengths compile to 128: **`[17,18,19,20,21,22,23,24]`**. Only
`_pad[24]` leaves *no implicit trailing padding*. The other seven hand the
compiler 1–7 uninitialised bytes that land in the memory-mapped file and inside
F-REPLAY's "order-independent digest," making that digest non-deterministic.
So the correction is not "make it 128", it is "declare all 24".

**Compile-time cross-check** — `C:/FACTOR/tests/layout_check.cpp`:

```
cl /std:c++20 /EHsc /W4        -> CL_CLEAN_EXIT=0   ; all static_asserts pass
cl ... /DPROVE_SPEC_FAILS      -> CL_LIE_EXIT=2
   error C2338: static_assert failed: 'PLANTED LIE: section 5 claims 128;
                the compiler says otherwise'
g++ -std=c++20 -Wall -Wextra   -> exit 0 ; ObligationSpec 120, Obligation 128
g++ ... -DPROVE_SPEC_FAILS     -> error: static assertion failed
                note: the comparison reduces to '(120 == 128)'
```

The planted lie for this check is §5's own claim, asserted. Both toolchains
refuse it. Runtime print from the MSVC binary matched the ctypes table byte for
byte, so the layout is ABI-stable across Win64 and SysV.

### Exact spec corrections, §5

> **§5 line `uint8_t  _pad[14];`** — replace with:
> ```c
>   uint8_t  _pad[24];      // to exactly 128; MUST be zeroed on write
> ```
> and append to the struct comment: *"128 bytes = 104 bytes of named fields +
> 24 bytes of explicit pad. The pad is declared, not left to the compiler:
> `_pad[17..23]` also yield `sizeof == 128` but leave implicit padding the
> compiler does not initialise, and the ledger digest of §21 F-REPLAY is taken
> over the raw 128 bytes."*

> **Add to §5 after the struct**, a paragraph headed **Encoding**:
> *"The ledger header pins, and `factor verify` asserts: byte order
> little-endian; `float` is IEEE-754 binary32; the record is 128 bytes with an
> explicit zeroed pad; and the numeric value of every enum below. A ledger whose
> header disagrees with the running build is refused, not converted."*

### Further §5 gaps found while modelling it

1. **No numeric encoding for `state`, `verb`, `reason`.** `gear` and `kind` are
   numbered inline (`0 code · 1 reflex · …`); `state` (9 names), `verb` (8 names
   in §8) and `reason` (16 names in §8) are not. These are `uint8_t` fields in a
   memory-mapped file and a persisted fold. Two builds that order the list
   differently mislabel every historical row, silently. **Pin the numbers in §5,
   next to the field, exactly as `gear` and `kind` already do.**
2. **No bit assignment for `flags`.** Twelve flags named
   (`OWED_BY_ME … DIRTY`), sixteen bits available, no bit positions given. Pin
   them; reserve the top four and require them zero.
3. **`verb` holds "last verb", but §8 also defines eight *events*** (`UNSAID`,
   `EXPIRED`, `GRADUATED`, `DEMOTED`, `COMPILED`, `GROWN`, `REVERSED`,
   `ROLLED-BACK`). Say whether events share the `verb` byte's number space or
   are excluded from it.
4. **`amount_fix` has no currency or unit.** "fixed point, 1/65536 of the class's
   unit" — the unit lives in the class, the class is `cls`, and `cls` is a
   `uint32` whose meaning comes from the writ, which the operator edits. §11's
   cap (`cap_amount = 500.00`) is enforced against this number and also carries
   no currency. A USD obligation and a EUR obligation are indistinguishable in
   the record that the cap is checked against. **There are 24 free pad bytes:
   spend 4 on `uint32_t unit; // ISO-4217 for money, an interned code otherwise`
   and give §11's cap the same field.** Range check: int64 at 2⁻¹⁶ is
   ±140,737,488,355.328 units — ample.
5. **`cls` is `uint32` but classes are named by string in the writ**
   (`[class.booking-confirm]`). The string→uint32 map is undefined: hash (what
   happens on collision?) or interning table (persisted where, stable across a
   writ edit?). §5 promises ids "stable across runs"; `cls` must carry the same
   promise or every record in the mmap is renumbered by a writ edit.
6. **`id` is BLAKE3-64 and §5 never says what a collision does.** At 10⁶
   obligations the birthday probability is ≈2.7×10⁻⁸ — negligible, but the id is
   the join key for the dossier, the tape and all three indexes. Add: *"a second
   distinct preimage hashing to a live id is a `fatal` row, never a merge."*
7. **The "two cache lines" framing buys the hot walk nothing.** The ripeness
   walk keys on `(cls, due_ns)` and `state`: `due_ns` is at 24 (line 0), `cls` at
   84 and `state` at 98 (line 1). Every walked record touches **both** lines.
   §19 budgets 5 ms for 50,000 obligations = 6.4 MB and 100,000 line fetches;
   that is comfortable only while the ledger is L3-resident and the scan is
   sequential and prefetchable. If the budget is ever missed, the fix is to move
   `cls`/`state`/`band` onto line 0 beside `due_ns` — the pad makes room.
8. **`float` margins inside a byte-identical digest.** §19 forbids float
   accumulation for amounts but the three margins stay `float`, and they sit
   inside the 128 bytes F-REPLAY digests. `-0.0` and `+0.0` have different bit
   patterns and compare equal; NaN has 2²³ encodings. Add: *"margins are written
   canonically: NaN is a `fatal`, and `-0.0` is normalised to `+0.0` before the
   record is stored."*

---

## 2 · Frame format — 10,000-string property test PASSES, 4 planted lies caught

`python C:/FACTOR/tests/frame_roundtrip.py` → **exit 0**

```
corpus: 10000 strings (seeded, deterministic) incl. 23 adversarial literals

profile MIN    round trip : PASS  (10000/10000 passed)
profile MIN    one line under str.splitlines(): NO (4173 violations)
   -> MIN lets these through raw: U+0000 U+000B U+000C U+001C U+001D U+001E
                                  U+0085 U+2028 U+2029
profile STRICT round trip : PASS  (10000/10000 passed)
profile STRICT one line under str.splitlines(): yes (0 violations)
length-prefixed alternative round trip : PASS (10000/10000 passed)

planted lies -- each MUST be caught
  LIE 1  encoder drops carriage returns            caught @ idx 7
  LIE 2  encoder does not escape the backslash     caught @ idx 1
  LIE 3  encoder escapes TAB before the backslash  caught @ idx 5
  LIE 4  decoder passes unknown escapes through    caught @ idx 0

why the backslash must be escaped, concretely:
   text          = '\\t'   (2 chars: backslash, t)
   LIE 2 encodes = '\t'
   strict decode = '<TAB>'  <- a TAB appeared out of nowhere
```

The required planted lie (an encoder that drops carriage returns) is caught at
corpus index 7 — the adversarial literal `"\r"` — as *"decoded text differs from
input"*. Three further lies were added and all three are caught: the classic
`str.replace` ordering bug (LIE 3) and a permissive decoder (LIE 4), which is
the one a reviewer is most likely to wave through.

**4173 of 10000** strings, escaped under the minimal rule, are one line to a
byte-level reader and **two lines** to `str.splitlines()`. That is not a Python
quirk: .NET's `TextReader.ReadLine` and several log shippers split on the same
set. A spool that "verifies alone" under its own chain while a consumer sees a
frame the chain never covered is exactly the seam F-CONSERVE is meant to close.

### Exact spec corrections, §4

> **Replace §4's `text` bullet** — *"`text`: flattened; tabs and newlines
> escaped; capped by the header's declared frame cap…"* — with:
>
> **Escaping.** Every field, not only `text`, is escaped before it is written;
> the decoder is strict and refuses anything it does not recognise.
>
> ```
>   U+005C  \      ->  \\        (the backslash is escaped FIRST, always)
>   U+0009  TAB    ->  \t
>   U+000A  LF     ->  \n
>   U+000D  CR     ->  \r
>   every other C0 (U+0000–U+001F) and U+007F  ->  \xNN
>   U+0085 NEL, U+2028 LS, U+2029 PS           ->  \uNNNN
>   a byte sequence that is not valid UTF-8    ->  \xNN per raw byte, and the
>                                                  frame carries a `badenc` mark
> ```
>
> A backslash followed by anything other than `t n r \ x u` is a hard error and
> the frame is refused with a row — never passed through. Escaping order is
> load-bearing: escaping TAB before the backslash corrupts, and the round-trip
> test in `tests/frame_roundtrip.py` plants that exact bug.
>
> The last two groups are not decoration. Without them the frame is one line to
> a byte-level reader and two lines to `str.splitlines()`, `TextReader.ReadLine`
> and most log shippers; measured, 42% of randomised text triggers it.
> Invalid UTF-8 must be escaped rather than replaced with U+FFFD, because
> §0 forbids editing the world and U+FFFD is an edit.

> **Add to §4, after the frame format**, a bullet **Frame cap**:
> *"The cap is a byte count applied to the **encoded** field. Truncation cuts the
> **source** text on a code-point boundary before escaping, so an escape is never
> split; the `trunc` row carries the number of source code points dropped and
> the encoded byte length that survived. Escaping can quadruple a field
> (`U+0000` → `\x00`), so a cap applied pre-escape does not bound the line."*

> **Alternative considered and rejected — length prefix.** A seventh field
> `<nbytes>` followed by the raw UTF-8, terminated by an LF that is not part of
> it. Implemented and round-tripped clean on the same 10,000 strings.
> *For:* no transform on the payload, so `text` digests to the same value as the
> source, F-EXTRACT's witnessing span is a byte slice, and no escaping bug can
> exist because there is no escaping. *Against:* the spool stops being
> line-oriented — `tail -f`, `grep`, `wc -l` and the §12 verifier's
> "last line has no LF" tear test all break, head recovery on a truncated spool
> needs the framing parser rather than a scan for LF, and the length becomes a
> second thing that can lie (a wrong prefix eats the next frame whole and the
> self-chain then verifies over the wrong bytes). **Recommend escaping**,
> because §4 requires the spool to "verify alone" and §12 requires a verifier
> that "needs no model" — both want a file whose torn tail is obvious to `tail`.
> Revisit only if an attachment lane must carry non-text bytes.

---

## 3 · Chains — all three verify, all three planted lies caught

`python C:/FACTOR/tests/chain_check.py` → **exit 0**

```
hash: hashlib.blake2b(digest_size=32)  [SUBSTITUTE: blake3 not installed]

(a)  TAPE  h = H(prev_hex || body), 24 rows across 6 segments
     chain crosses segments : yes
     verify clean tape      : PASS (0 errors)

(a2) TORN TRAILING ROW -- head recovery
     torn row detected     : seg-000006.jsonl row 4: JSONDecodeError (48 bytes)
     rows accepted         : 24 (was 24)
     equals last complete  : True      no spurious errors : True     PASS

(a3) PLANTED LIE 1 -- one byte modified mid-chain (offset 760)
     forged file still parses as JSON : True
     seg-000001.jsonl row 2: SELF hash mismatch (h=9982829989cd0c3e
                                              want=920ee4b60ac849bb)   CAUGHT

(a4) PLANTED LIE 2 -- a row rewritten with its OWN hash recomputed
     verifier WITH link check    : 1 error   CAUGHT
     verifier WITHOUT link check : 0 errors  MISSED   <- the bug the lie is for

(b)  SPOOL self-chain, 41 lines (1 header + 40 frames), 6120 bytes
     verify clean spool  : PASS (0 errors)
     one byte flipped at offset 3060 -> line 20: hash mismatch      CAUGHT

(c)  CURSOR prefix hash over the 2991 bytes before offset 2991
     revalidate unchanged    : PASS
     ROTATED spool detected  : PASS (prefix hash mismatch at off 2991)
     TRUNCATED spool detected: PASS (spool is SHORTER than the cursor 2981<2991)

(d)  CANONICAL JSON
     bare float refused : PASS      NaN/Infinity refused : PASS
```

The mid-chain byte flip was aimed so the forged file **still parses as JSON**,
which exercises the hash path rather than the parser. The second planted lie is
the one that matters for review: a row rewritten *with its own hash recomputed*
is invisible to a verifier that checks each row's `h = H(prev‖body)` and forgets
to check `row[i].prev == row[i-1].h`. Both verifiers were run side by side; the
link-checking one caught it, the row-local one reported **0 errors**.

### Exact spec corrections, §12

> **Replace §12's** *"`h = BLAKE3-256(prev ‖ body)`"* with:
>
> `prev` is the previous row's `h` as **64 lowercase hex characters, ASCII**,
> concatenated with no separator to `body`. `body` is the **canonical JSON of
> the row with `prev` and `h` removed** — the digest covers the fields, not the
> chain scaffolding. The genesis `prev` is **64 `0` characters**, not an empty
> string, so every preimage has one shape and a genesis row cannot be mistaken
> for a torn one. The row as written is that same object with `prev` and `h`
> added back, serialised canonically, plus one LF.

> **Add to §12 a paragraph, Canonical JSON**, because JSON has none:
> *"UTF-8; keys sorted by code point; separators `,` and `:` with no spaces;
> `ensure_ascii` false, so the bytes are the text; no `NaN`, no `Infinity`;
> **no bare floats**; every `uint64` (`t_mono_ns`, `rev`, ids) written as a
> decimal **string**. Unknown keys are a `fatal`, not ignored. Equivalent to
> RFC 8785 (JCS) with the float and integer rules tightened."*
>
> Measured on this machine, the same IEEE-754 double:
>
> | value | Python `json.dumps` | Node `JSON.stringify` |
> |---|---|---|
> | `1e16` | `1e+16` | `10000000000000000` |
> | `-0.0` | `-0.0` | `0` |
>
> Two verifiers in two languages would compute two heads for one tape. And JSON
> has no integer width: `2**63+1` does not survive a JS reader, so a bare
> `t_mono_ns` above 2⁵³ is silently rounded by anything that parses the tape in
> a browser or in Node — including any future console.

> **Add to §12, The verifier:** *"A row's hash is verified two ways and both are
> required: `h == H(prev‖body)` (the row is intact) **and**
> `prev == previous row's h` (the row is in its place). A verifier that checks
> only the first accepts a rewritten row whose hash was recomputed; the planted
> lie in `tests/chain_check.py` is exactly that row."*

> **Add to §12, Torn rows:** *"Exactly one row may be torn, and only the last
> row of the last segment. Torn covers three cases: no trailing LF; a trailing
> LF but undecodable JSON; decodable JSON whose own hash does not verify. Any of
> the three in an earlier position, or in a non-final segment, is `fatal` — not
> a warning. The head is the `h` of the last row that verifies both ways."*

> **Add to §12, Segments:** *"A row is never split across segments; the size
> bound is checked before the row is appended. The first row of segment N+1
> carries `prev` = the last verified `h` of segment N. `manifest.json` is a
> cache and is never truth: `factor verify` must produce the same head with the
> manifest deleted, by walking segments in filename order. Segment filenames are
> zero-padded and monotone for exactly that reason."*

### Further §12 gaps

9. **`ms` inside the hashed body contradicts §19 and F-DETERMINISM.** §12: *"Every
   row: `k`, `ms` (steady clock since boot), `t_mono_ns`, the row's fields,
   `prev`, `h`."* §19: *"Two runs over the same spools and writ produce
   byte-identical verb rows."* A steady clock since boot is never identical
   across two runs, so as written the two statements cannot both hold. Decide
   one: (a) `ms` is excluded from the hashed `body` and lives beside the row;
   (b) byte-identity is defined over a **projection** of the verb row that drops
   `ms`, and the *plan hash* on the account is defined as the hash of that
   projection; or (c) `ms` is dropped from verb rows. Say which, and define the
   plan hash — §19 names it and nothing defines it.
10. **`t_mono_ns` on a non-`frame` row is ambiguous.** On a `frame` row it is
    plainly copied from the frame. On a `verb` row, is it copied from the
    triggering frame (deterministic, replayable) or read from a clock
    (not)? Same fork as #9.
11. **Three clocks, four names.** §3 names "the world's clock", "the deposit
    clock", "the period" and "the horizon"; §4 has `t_mono_ns`; §5 says
    `opened_ns` is "world clock"; §12 adds `ms`. A monotonic clock has a
    per-boot epoch and is not comparable across a venue restart, yet `opened_ns`
    and `due_ns` are compared across the whole life of an obligation. **Add a
    four-line table to §3 fixing, per field, which clock, what epoch, what
    happens at a venue reboot, and whether it is comparable across venues.**
12. **Encryption vs. the chain is undefined.** *"Segments encrypted with a key
    held on the machine; a daily fingerprint of the head published…"* — is `h`
    computed over plaintext or ciphertext? Can `factor verify` run without the
    key? Is the container authenticated (AEAD) or is a hash-chained plaintext
    under an unauthenticated stream cipher considered enough? Recommend:
    **hash the plaintext, encrypt the segment with an AEAD whose AAD is the
    segment's first `prev`**, so `verify` needs the key, the published head
    needs no key, and a ciphertext edit fails before the chain is consulted.
13. **The kind list contains a bare `b`.** *"`hdr · frame · obligation · b ·
    verb · …`"* — every other kind is a word. Either a typo or an undocumented
    kind; §12 lists 30 kinds and defines none of them. At minimum name `b`.
14. **`frame` rows reference `(lane, offset, hash)`** — is `hash` the spool
    line's chain hash or a content hash of the frame? Pin one. And once spools
    rotate (see §4 below), `offset` alone no longer identifies a byte: the
    reference needs a segment or generation id.

---

## 4 · Falsifier scaffold — 16 files, runner green

`python C:/FACTOR/tests/run_falsifiers.py` → **exit 0**

```
  falsifier        gate requires  lie       id
  F_CONSERVE       M0   TODO      TODO      F-CONSERVE
  F_REPLAY         M0   TODO      TODO      F-REPLAY
  F_DETERMINISM    M0   TODO      TODO      F-DETERMINISM
  F_INERT          M1   TODO      TODO      F-INERT
  F_EGRESS         M3   TODO      TODO      F-EGRESS
  F_WINDOW         M3   TODO      TODO      F-WINDOW
  F_BUDGET         M4   TODO      TODO      F-BUDGET
  F_JURY           M5   TODO      TODO      F-JURY
  F_MONOTONE       M4   TODO      TODO      F-MONOTONE
  F_BOTH_SIDES     M4   TODO      TODO      F-BOTH-SIDES
  F_ROLLBACK       M7   TODO      TODO      F-ROLLBACK
  F_EXTRACT        M2   TODO      TODO      F-EXTRACT
  F_CONTRADICT     M6   TODO      TODO      F-CONTRADICT
  F_COMPILE        M7   TODO      TODO      F-COMPILE
  F_TICK           M7   TODO      TODO      F-TICK
  F_PIN            M0   TODO      TODO      F-PIN
  TODO 32

RESULT: scaffold intact -- 32 of 32 functions are stubs (TODO),
        0 implemented and passing
```

`--verbose` prints, per stub, the one-sentence statement of what it must assert.
Statuses are `PASS / FAIL / TODO / ERROR / MISSING`; the runner exits 0 while
falsifiers are unwritten and 1 on any `FAIL`, `ERROR` or `MISSING` — an unwritten
falsifier is not a build failure, a broken or absent one is. Files are named
explicitly rather than globbed, so a deleted falsifier is reported, not skipped.

The contract each stub declares (also in `tests/README.md`):
`requires()` returns None or raises `AssertionError` with the counterexample;
`planted_lie()` builds the sabotaged system, runs `requires()` against it, and
asserts that `requires()` **failed** — a falsifier whose planted lie passes is
measuring nothing.

**Noted while mapping §21 onto §22:** M8 (organs and surfaces) and M9 (the tune)
have gates but no §21 falsifier. Either §21 is missing two rows or §22 should
name the receipt those gates produce instead.

---

## 5 · Remaining §4 underspecification

15. **The spool's chain has nowhere to live.** §4 gives the frame six
    tab-separated fields, then says *"every frame line carries a running BLAKE3
    of the previous frame's hash and its own bytes."* There is no seventh field.
    **Correction — replace §4's frame format block with:**
    ```
    t_mono_ns <TAB> venue <TAB> lane <TAB> grain <TAB> rev <TAB> text <TAB> h
    ```
    *"`h` is the line's chain hash: `h = BLAKE3-256(prev_hex ‖ body)` where
    `body` is the first six fields with their separating TABs, as escaped bytes,
    excluding the TAB before `h`, `h` itself, and the terminating LF; `prev_hex`
    is the previous line's `h` in 64 lowercase hex ASCII characters, and the
    genesis `prev` is 64 zeros."* Without the exclusion spelled out the
    definition is self-referential and two implementations will differ.
16. **The header line has no syntax.** §4 says it *"declares the contract
    version, the venue, the frame cap, and the spool's own chain"* — nothing
    about its form, whether it is itself chained, or whether it occupies offset
    0 for cursor purposes. **Pin it:** *"Line 1 is a canonical JSON object
    `{contract, venue, lane, frame_cap, hash, esc}` followed by TAB and its own
    chain hash, computed with `prev` = 64 zeros. It is the chain's genesis: the
    first frame's `prev` is the header's `h`. It counts in every offset."*
    A header outside the chain is a header an adapter can rewrite silently.
17. **The cursor's prefix hash has no window.** §4 says only *"a prefix hash of
    the preceding bytes."* All of them is O(n) on every check. **Pin:**
    *"`H(spool[max(0, off−4096) : off])`, where `off` is the cursor's own end
    offset. The cursor records the window length actually hashed, because a
    rotated spool shorter than the window would otherwise present the same
    digest as a prefix of the old one."* Verified: with the length recorded,
    rotation and truncation are both caught; the run above shows both.
18. **Spool rotation is named as a hazard but never as a mechanism.** §4 says a
    *"rotated or truncated spool is detected and the tail restarts loudly at
    zero,"* while §23's home has exactly one file per lane. If spools never
    rotate they grow without bound; if they do, §4 must say how the chain
    carries across (new file's genesis `prev` = old file's head, recorded in a
    per-lane manifest) and §12's `(lane, offset, hash)` references need a
    generation id, or every historical frame reference breaks at the first
    rotation. **This is the §4/§12 seam most likely to be discovered in
    production.**
19. **"A crash with a full ring replays the ring on restart."** The ring is
    heap-allocated (§4) and dies with the process; what is replayable is the
    spool span between the cursor and the spool's end. Reword, or the `replay`
    rows will be implemented against a structure that no longer exists.
20. **Ring capacity is "fixed power-of-two"** — of frames or of bytes? Frames are
    variable-length, so a power-of-two byte ring needs a wrap rule and a
    power-of-two frame ring needs a separate byte arena. Say which.
21. **Nothing says what a lane does with non-UTF-8 source bytes.** Covered by the
    `\xNN` + `badenc` rule proposed in §2 above; flagged separately because
    "never drops a percept" (§0) makes U+FFFD replacement a law violation, not a
    style choice.
22. **`grain` and `lane` are closed sets in prose only.** A grown adapter (§14)
    authors lane code; nothing in §4 says an unrecognised `grain` is refused.
    Add: *"an unknown `grain`, or a `lane` id not matching the declared pattern,
    is a refused frame with a row — never a default."*

---

## Files created

Under `C:\FACTOR\tests\` (22 files):

| file | what it is |
|---|---|
| `check_layout.py` | ctypes model of §5, offsets/holes/endianness, finds the correct pad |
| `layout_check.cpp` | the same struct in C++20; `static_assert` on size, alignment, every offset, no-implicit-padding, `is_standard_layout`, `is_trivially_copyable`, IEEE-754; `-DPROVE_SPEC_FAILS` is its planted lie |
| `frame_roundtrip.py` | §4 codec, profiles MIN and STRICT + length-prefixed alternative; 10,000-string property test; 4 planted lies |
| `chain_check.py` | §12 tape chain, §4 spool self-chain, §4 cursor prefix hash, segment rotation, torn-tail head recovery, canonical-JSON hazards; 3 planted lies |
| `run_falsifiers.py` | imports all 16 stubs, reports `PASS/FAIL/TODO/ERROR/MISSING`, `--verbose` |
| `README.md` | the 16 falsifiers with their planted lies and §22 gates; the falsifier contract; how to run everything |
| `F_CONSERVE.py` `F_REPLAY.py` `F_DETERMINISM.py` `F_INERT.py` `F_EGRESS.py` `F_WINDOW.py` `F_BUDGET.py` `F_JURY.py` `F_MONOTONE.py` `F_BOTH_SIDES.py` `F_ROLLBACK.py` `F_EXTRACT.py` `F_CONTRADICT.py` `F_COMPILE.py` `F_TICK.py` `F_PIN.py` | 16 stubs, each with `ID`, `MILESTONE`, `REQUIRES`, `PLANTED_LIE`, `requires()`, `planted_lie()` |

Under `C:\FACTOR\qc\` (1 file): `O3_formats_tests.md` — this report.

`C:\FACTOR\BLUEPRINT.md` was not modified.

### How to re-run everything

```
python C:/FACTOR/tests/check_layout.py            # exits 1 until _pad is fixed
python C:/FACTOR/tests/frame_roundtrip.py         # exits 0
python C:/FACTOR/tests/chain_check.py             # exits 0
python C:/FACTOR/tests/run_falsifiers.py -v       # exits 0, 32 TODO
cl /std:c++20 /EHsc /W4 C:/FACTOR/tests/layout_check.cpp                    # 0
cl /std:c++20 /EHsc /W4 /DPROVE_SPEC_FAILS C:/FACTOR/tests/layout_check.cpp # 2
```

`check_layout.py` is deliberately the one red light: it goes green the moment
§5 says `_pad[24]`.
