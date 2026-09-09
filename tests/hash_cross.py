"""hash_cross.py -- the C hash against the Python model, byte for byte.

BLUEPRINT_v0.2.md section 12 pins the construction:

    K_chain = BLAKE2b-256( machine_secret, person = the pinned string )
    h       = BLAKE2b-256-keyed( K_tape ; prev_hex || u64le(len(body)) || body )

`tests/chain_check.py` and `tests/frame_roundtrip.py` compute that with Python's
`hashlib.blake2b`. `kernel/blake2b.c` computes it in C. Those two are the tape's
two readers, and a one-byte disagreement between them is a tape with two heads.
This file measures them against each other over a corpus and refuses to believe
the agreement until four planted lies have each been caught and each negative
control has failed.

    python C:/FACTOR/tests/hash_cross.py [path\\to\\factor.exe]

Exit 0 when every case agrees, every lie is caught, and every control fails.
Exit 1 otherwise.
"""

import hashlib
import os
import random
import subprocess
import sys

sys.dont_write_bytecode = True

PERSON = {
    "tape":    b"FCTR-tape-v1",
    "dossier": b"FCTR-dossier-v1",
    "ledger":  b"FCTR-ledger-v1",
    "ckpt":    b"FCTR-ckpt-v1",
    "spool":   b"FCTR-spool-v1",
    "fprint":  b"FCTR-fprint-v1",
}
CHAIN_ORDER = ("tape", "dossier", "ledger", "ckpt", "spool", "fprint")
GENESIS = "0" * 64
MACHINE_SECRET = bytes(range(32))       # tests/chain_check.py's fixture

# Lengths that cross every boundary the block-wise update has: the empty input,
# one byte, one short of a block, exactly a block, one over, and the same around
# two blocks. A hash that is right on random data and wrong on 128 bytes exactly
# is the classic BLAKE2b defect, because the last block is finalised differently.
EDGE_LENGTHS = (0, 1, 2, 63, 64, 65, 127, 128, 129, 130, 191, 192,
                255, 256, 257, 383, 384, 385)
DIGEST_SIZES = (1, 8, 16, 20, 28, 32, 48, 64)
KEY_LENGTHS = (0, 1, 16, 32, 63, 64)


def u64le(n):
    return int(n).to_bytes(8, "little", signed=False)


def hx(b):
    return b.hex() if b else "-"


def build_corpus(seed=20260909):
    """Every case is (outlen, person, key, message). Deterministic from the seed
    so a failure is reproducible from the printed seed alone."""
    rng = random.Random(seed)
    cases = []

    # 1. Every edge length, unkeyed and unpersonalized, at 32 bytes out.
    for n in EDGE_LENGTHS:
        cases.append((32, b"", b"", bytes(rng.randrange(256) for _ in range(n))))

    # 2. Every pinned personalization over the same message, so domain
    #    separation is measured on identical bytes rather than assumed.
    same = b"the same preimage, six chains"
    for nm in CHAIN_ORDER:
        cases.append((32, PERSON[nm], b"", same))
    cases.append((32, b"", b"", same))

    # 3. Every key length, at every digest size, over a block-crossing message.
    msg = bytes(rng.randrange(256) for _ in range(200))
    for klen in KEY_LENGTHS:
        key = bytes(rng.randrange(256) for _ in range(klen))
        for outlen in DIGEST_SIZES:
            cases.append((outlen, b"", key, msg))

    # 4. Keyed AND personalized together, which neither harness exercises and
    #    the parameter block gets wrong if key_length is written to the wrong
    #    byte.
    for nm in CHAIN_ORDER:
        for klen in (1, 32, 64):
            key = bytes(rng.randrange(256) for _ in range(klen))
            cases.append((32, PERSON[nm], key, msg))

    # 5. A keyed hash of the EMPTY message: the key block is then also the last
    #    block, which is the one place the finalisation flag is easy to misplace.
    for klen in (1, 32, 64):
        cases.append((32, b"", bytes(range(klen)), b""))
        cases.append((32, PERSON["tape"], bytes(range(klen)), b""))

    # 6. The exact preimages the two harnesses hash, so this file overlaps them
    #    rather than testing beside them.
    body = b"known-answer"
    pre = GENESIS.encode("ascii") + u64le(len(body)) + body
    cases.append((32, PERSON["spool"], b"", pre))
    cases.append((32, b"", b"", pre))
    for nm in CHAIN_ORDER:
        cases.append((32, PERSON[nm], b"", MACHINE_SECRET))   # the chain keys
    k_tape = hashlib.blake2b(MACHINE_SECRET, digest_size=32,
                             person=PERSON["tape"]).digest()
    cases.append((32, b"", k_tape, pre))                      # a tape row's h

    # 7. Random cases, so the corpus is not only the cases someone thought of.
    for _ in range(1200):
        outlen = rng.choice(DIGEST_SIZES)
        person = rng.choice([b""] + [PERSON[n] for n in CHAIN_ORDER])
        klen = rng.choice(KEY_LENGTHS)
        key = bytes(rng.randrange(256) for _ in range(klen))
        n = rng.randrange(0, 600)
        cases.append((outlen, person, key,
                      bytes(rng.randrange(256) for _ in range(n))))

    return cases


def model(outlen, person, key, msg):
    """The Python model: what the harnesses compute, and what the tape means."""
    return hashlib.blake2b(msg, digest_size=outlen,
                           key=key, person=person).hexdigest()


def run_binary(exe, cases):
    lines = []
    for outlen, person, key, msg in cases:
        lines.append("%d %s %s %s" % (outlen, hx(person), hx(key), hx(msg)))
    stdin = ("\n".join(lines) + "\n").encode("ascii")
    proc = subprocess.run([exe, "hash", "--batch"], input=stdin,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out = proc.stdout.decode("ascii").split()
    return proc.returncode, out, proc.stderr.decode("utf-8", "replace")


# --------------------------------------------------------------- planted lies

def lie_no_person(outlen, person, key, msg):
    """A hash that ignores personalization. Amendment 1 item 11's whole point."""
    return hashlib.blake2b(msg, digest_size=outlen, key=key).hexdigest()


def lie_key_as_prefix(outlen, person, key, msg):
    """The key prepended to the message instead of BLAKE2b's keyed mode. This is
    the mistake a reimplementation makes when it reads `keyed` as `salted`."""
    return hashlib.blake2b(key + msg, digest_size=outlen,
                           person=person).hexdigest()


def lie_truncated_512(outlen, person, key, msg):
    """BLAKE2b-512 cut to outlen. digest_size is mixed into the parameter block,
    so truncation is a different function -- but it looks like one until it is
    measured."""
    return hashlib.blake2b(msg, digest_size=64, key=key,
                           person=person).hexdigest()[:2 * outlen]


def lie_person_left_padded(outlen, person, key, msg):
    """Personalization padded on the left instead of the right. Sixteen bytes
    either way, and a different function."""
    p = person
    if p:
        p = b"\x00" * (16 - len(p)) + p
    return hashlib.blake2b(msg, digest_size=outlen, key=key,
                           person=p).hexdigest()


LIES = (
    ("the person ignored", lie_no_person),
    ("the key as a prefix", lie_key_as_prefix),
    ("BLAKE2b-512 truncated", lie_truncated_512),
    ("the person left padded", lie_person_left_padded),
)


def main():
    exe = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "build", "bin",
        "factor.exe")
    exe = os.path.abspath(exe)

    print("=" * 78)
    print("FACTOR -- kernel/blake2b.c against Python hashlib, byte for byte")
    print("binary : %s" % exe)
    print("model  : hashlib.blake2b(msg, digest_size=n, key=k, person=p)")
    print("=" * 78)

    if not os.path.exists(exe):
        print("\nRESULT: FAIL -- no binary at that path. Run build.cmd first.")
        return 1

    seed = 20260909
    cases = build_corpus(seed)
    rc, got, err = run_binary(exe, cases)

    print("\n(0) THE CORPUS")
    print("    seed                   : %d (deterministic)" % seed)
    print("    cases                  : %d" % len(cases))
    print("    digest sizes           : %s" % (", ".join(map(str, DIGEST_SIZES))))
    print("    key lengths            : %s" % (", ".join(map(str, KEY_LENGTHS))))
    print("    personalizations       : %d pinned + none" % len(CHAIN_ORDER))
    print("    message lengths        : 0 to 600, every block edge included")

    fails = []

    if rc != 0:
        fails.append("the binary exited %d: %s" % (rc, err.strip()[:200]))
    if len(got) != len(cases):
        fails.append("the binary answered %d of %d cases"
                     % (len(got), len(cases)))

    print("\n(1) AGREEMENT")
    n_ok = 0
    first_bad = None
    for i, (outlen, person, key, msg) in enumerate(cases):
        if i >= len(got):
            break
        want = model(outlen, person, key, msg)
        if got[i] == want:
            n_ok += 1
        elif first_bad is None:
            first_bad = (i, outlen, person, key, msg, want, got[i])
    print("    C == Python            : %d of %d  %s"
          % (n_ok, len(cases), "PASS" if n_ok == len(cases) else "FAIL"))
    if first_bad is not None:
        i, outlen, person, key, msg, want, g = first_bad
        print("    first disagreement     : case %d" % i)
        print("      outlen %d  person %r  keylen %d  msglen %d"
              % (outlen, person, len(key), len(msg)))
        print("      python %s" % want)
        print("      c      %s" % g)
        fails.append("case %d disagrees" % i)

    print("\n(2) THE PLANTED LIES -- each must DIFFER from the binary")
    for name, lie in LIES:
        caught = 0
        for i, (outlen, person, key, msg) in enumerate(cases):
            if i >= len(got):
                break
            if lie(outlen, person, key, msg) != got[i]:
                caught += 1
        # A lie that never differs is a lie the corpus cannot see, which means
        # the corpus is proving nothing about that mechanism.
        ok = caught > 0
        print("    %-24s differs on %5d of %d cases  %s"
              % (name, caught, len(cases), "CAUGHT" if ok else "NOT CAUGHT"))
        if not ok:
            fails.append("the planted lie %r is invisible to this corpus" % name)

    print("\n(3) THE NEGATIVE CONTROLS -- the check must fail when the")
    print("    mechanism is removed")
    # Control A: corrupt ONE character of ONE answer and re-run block (1)'s
    # comparison over the corrupted transcript. If the agreement check is
    # measuring anything it must report exactly one disagreement, and it must
    # name the case that was corrupted. A checker that reports zero here is a
    # checker that would have accepted a wrong tape.
    control_a = "not run"
    if got and len(got) == len(cases):
        victim = len(got) // 2
        corrupted = list(got)
        ch = corrupted[victim][0]
        corrupted[victim] = ("1" if ch == "0" else "0") + corrupted[victim][1:]
        seen = []
        for i, (outlen, person, key, msg) in enumerate(cases):
            if model(outlen, person, key, msg) != corrupted[i]:
                seen.append(i)
        ok = (seen == [victim])
        control_a = ("%d disagreement(s), at case %s"
                     % (len(seen), seen if len(seen) < 4 else "many"))
        print("    A. one hex character of case %d flipped:" % victim)
        print("       the agreement check reports %s  %s"
              % (control_a, "PASS (it can fail)" if ok
                 else "FAIL (it cannot fail, so it was never checking)"))
        if not ok:
            fails.append("the agreement check did not catch a corrupted answer")
    else:
        print("    A. skipped: no usable transcript to corrupt")
        fails.append("negative control A could not run")

    # Control B: strip personalization from BOTH sides. The domain-separation
    # lie then becomes true, and the check that caught it must stop catching it.
    stripped = []
    for outlen, person, key, msg in cases:
        stripped.append((outlen, b"", key, msg))
    rc_b, got_b, err_b = run_binary(exe, stripped)
    b_caught = 0
    for i, (outlen, person, key, msg) in enumerate(stripped):
        if i >= len(got_b):
            break
        if lie_no_person(outlen, person, key, msg) != got_b[i]:
            b_caught += 1
    print("    B. person removed from both sides, the domain-separation lie")
    print("       is then the truth : %d of %d differ  %s"
          % (b_caught, len(stripped),
             "PASS (the check went blind, so it was the person it was seeing)"
             if b_caught == 0 else "FAIL (it still differs, so it was measuring "
             "something else)"))
    if rc_b != 0 or b_caught != 0:
        fails.append("negative control B did not go blind")

    print("\n(4) REFUSED PARAMETERS -- refused, never clamped")
    refusals = [
        ("outlen 0", "0 - - 00"),
        ("outlen 65", "65 - - 00"),
        ("key 65 bytes", "32 - %s 00" % ("aa" * 65)),
        ("person 17 bytes", "32 %s - 00" % ("bb" * 17)),
        ("odd hex digits", "32 - - 0"),
        ("three fields", "32 - -"),
    ]
    stdin = ("\n".join(r[1] for r in refusals) + "\n").encode("ascii")
    proc = subprocess.run([exe, "hash", "--batch"], input=stdin,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    answers = proc.stdout.decode("ascii").split()
    for i, (label, _) in enumerate(refusals):
        answer = answers[i] if i < len(answers) else "<missing>"
        ok = (answer == "REFUSED")
        print("    %-18s -> %-8s %s" % (label, answer, "PASS" if ok else "FAIL"))
        if not ok:
            fails.append("%s was not refused" % label)

    print("\n" + "=" * 78)
    if fails:
        print("RESULT: FAIL")
        for f in fails:
            print("  - %s" % f)
        print("=" * 78)
        return 1
    print("RESULT: PASS -- %d of %d cases agree byte for byte; 4 of 4 planted"
          % (n_ok, len(cases)))
    print("        lies caught; the agreement check caught a corrupted answer")
    print("        and went blind when the person was removed from both sides;")
    print("        6 of 6 refused parameters refused.")
    print("=" * 78)
    return 0


if __name__ == "__main__":
    sys.exit(main())
