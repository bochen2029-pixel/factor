"""cjson_cross.py -- kernel/cjson.cpp against the Python model, byte for byte.

The model is not a reimplementation: this file imports `canon` and
`DECLARED_WIDTH` from `tests/chain_check.py`, which is the function the tape's
rows are hashed over in the harness. If the C writer and that function disagree
by one byte, the tape has two heads, and section 12 records the measurement that
makes this concrete -- the same value serialises as `1e+16` in one language and
`10000000000000000` in another.

What is measured:

  1. every canonical document the model produces is accepted by the C reader and
     re-emitted by the C writer as exactly the same bytes;
  2. every non-canonical spelling of the same document is refused;
  3. four planted lies, each a plausible canonicaliser, each caught;
  4. two negative controls, each of which must make a check stop working.

    python C:/FACTOR/tests/cjson_cross.py [path\\to\\factor.exe]
"""

import json
import os
import random
import subprocess
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import chain_check as model      # the harness's own canonical form

WIDE = ("uint64", "int64")


def build_corpus(seed=20260909):
    rng = random.Random(seed)
    cases = []

    # 1. Rows of every kind the tape declares, with values at their edges.
    cases.append({
        "k": "verb", "ms": 12, "t_mono_ns": "18446744073709551615",
        "id": "0", "judged_rev": "1", "verb": "HOLD", "reason": "margin",
        "flags": 65535, "band": 4294967295, "rung": 255,
        "m_hand": -32768, "m_check": 32767, "m_guard": 0,
        "batch": "9007199254740993", "pos": 0,
    })
    cases.append({
        "k": "frame", "ms": 0, "t_mono_ns": "1", "lane": "files-root",
        "generation": "1", "offset": "0", "frame_h": "ab" * 32,
    })
    cases.append({
        "k": "fingerprint", "ms": 3, "head": "cd" * 32, "seg": "7",
        "row_orig": "4096", "fp_prev": "00" * 32, "fp_h": "11" * 32,
    })
    cases.append({
        "k": "tombstone", "ms": 9, "span_prev": "22" * 32, "span_h": "33" * 32,
        "count": "128", "fp_before": "44" * 32, "fp_after": "55" * 32,
        "sig": "66" * 32,
    })

    # 2. Strings that break a lazy escaper. Every C0 control, the two-character
    #    escapes, DEL, the line separators that are not LF, and non-ASCII --
    #    which section 12 says is NOT escaped, so an ensure_ascii writer is a
    #    different function.
    controls = "".join(chr(c) for c in range(0x20))
    cases.append({"lane": controls})
    cases.append({"lane": "quote\" backslash\\ del\x7f"})
    cases.append({"lane": "caf\u00e9 \u65e5\u672c\u8a9e \U0001f600"})
    cases.append({"lane": "\u0085 \u2028 \u2029"})
    cases.append({"lane": ""})

    # 3. Nesting, arrays, the three literals.
    cases.append({"a": [], "b": {}, "c": None, "d": True, "e": False})
    cases.append({"a": [1, [2, [3, {"deep": "yes"}]]], "z": {"y": {"x": 0}}})

    # 4. Key order that is not insertion order, including keys that differ only
    #    by case, so byte order and any locale-aware order come apart.
    cases.append({"b": 1, "A": 2, "a": 3, "B": 4, "_": 5, "~": 6, "0": 7})

    # 5. Every narrow width at both ends of its range.
    for key, width in sorted(model.DECLARED_WIDTH.items()):
        if width in WIDE:
            cases.append({key: "0"})
            cases.append({key: "-1" if width == "int64" else "1"})
            cases.append({key: "9223372036854775807"})
        else:
            lo, hi = model.WIDTH_RANGE[width]
            cases.append({key: lo})
            cases.append({key: hi})

    # 6. Random rows, so the corpus is not only the cases someone thought of.
    alphabet = "abcdeABCDE_0129~ \u00e9\u65e5"
    for _ in range(400):
        obj = {}
        for _ in range(rng.randrange(1, 7)):
            key = "".join(rng.choice(alphabet) for _ in range(rng.randrange(1, 6)))
            kind = rng.randrange(4)
            if kind == 0:
                obj[key] = rng.randrange(-(2 ** 52), 2 ** 52)
            elif kind == 1:
                obj[key] = "".join(rng.choice(alphabet + "\n\t\"\\\x01")
                                   for _ in range(rng.randrange(0, 12)))
            elif kind == 2:
                obj[key] = rng.choice([None, True, False])
            else:
                obj[key] = [rng.randrange(0, 100) for _ in range(rng.randrange(0, 4))]
        # A random key may collide with a declared-width name; give it a value
        # of the right shape rather than dropping the case.
        for key in list(obj):
            w = model.DECLARED_WIDTH.get(key)
            if w in WIDE:
                obj[key] = str(rng.randrange(0, 2 ** 63))
            elif w is not None:
                lo, hi = model.WIDTH_RANGE[w]
                obj[key] = rng.randrange(lo, hi + 1)
        cases.append(obj)

    return cases


def run_batch(exe, lines):
    stdin = ("\n".join(lines) + "\n").encode("utf-8")
    proc = subprocess.run([exe, "cjson", "--batch"], input=stdin,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # NOT str.splitlines(). Python splits it on U+0085, U+2028 and U+2029 as
    # well as LF, and canonical JSON carries all three RAW -- section 12 forbids
    # escaping non-ASCII. A harness that used splitlines() here would desync its
    # whole transcript on the first document containing a line separator and
    # report the codec as broken. This is the same set frame_roundtrip.py calls
    # EXTRA_SPLITTERS, measured here rather than assumed.
    text = proc.stdout.decode("utf-8")
    out = [ln[:-1] if ln.endswith("\r") else ln for ln in text.split("\n")]
    if out and out[-1] == "":
        out.pop()
    return proc.returncode, out, proc.stderr.decode("utf-8", "replace")


# --------------------------------------------------------------- planted lies

def lie_sorted_casefold(obj):
    """Keys sorted case-insensitively. Reads the same to a person and orders
    {'A':_, 'a':_} the other way, which is a different hash."""
    items = sorted(obj.items(), key=lambda kv: kv[0].lower())
    return ("{" + ",".join(json.dumps(k, ensure_ascii=False) + ":" +
                           json.dumps(v, ensure_ascii=False,
                                      separators=(",", ":"), sort_keys=True)
                           for k, v in items) + "}")


def lie_pretty_separators(obj):
    """The library default, `, ` and `: `. One space, one different tape."""
    return json.dumps(obj, sort_keys=True, ensure_ascii=False)


def lie_ensure_ascii(obj):
    """Non-ASCII escaped to \\uXXXX. Section 12 forbids exactly this."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True)


def lie_wide_as_number(obj):
    """Every 64-bit field written as a bare JSON number. This is the defect
    Amendment 1 item 17 exists to prevent, and it is invisible until a value
    passes 2**53."""
    out = {}
    for k, v in obj.items():
        if model.DECLARED_WIDTH.get(k) in WIDE and isinstance(v, str):
            out[k] = int(v)
        else:
            out[k] = v
    return json.dumps(out, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False)


LIES = (
    ("keys sorted case-insensitively", lie_sorted_casefold),
    ("`, ` and `: ` separators", lie_pretty_separators),
    ("non-ASCII escaped", lie_ensure_ascii),
    ("64-bit fields as numbers", lie_wide_as_number),
)


def main():
    exe = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "build", "bin",
        "factor.exe")
    exe = os.path.abspath(exe)

    print("=" * 78)
    print("FACTOR -- kernel/cjson.cpp against tests/chain_check.py's canon()")
    print("binary : %s" % exe)
    print("model  : chain_check.canon(), imported, not reimplemented")
    print("=" * 78)

    if not os.path.exists(exe):
        print("\nRESULT: FAIL -- no binary at that path. Run build.cmd first.")
        return 1

    fails = []
    cases = build_corpus()
    canonical = [model.canon(c).decode("utf-8") for c in cases]

    print("\n(0) THE CORPUS")
    print("    cases                  : %d" % len(cases))
    print("    every declared width   : %d fields, both ends of each range"
          % len(model.DECLARED_WIDTH))
    print("    every C0 control, DEL, U+0085, U+2028, U+2029, non-ASCII")

    rc, got, err = run_batch(exe, canonical)
    if rc != 0:
        fails.append("the binary exited %d: %s" % (rc, err.strip()[:200]))

    print("\n(1) THE MODEL'S BYTES SURVIVE THE C READER AND WRITER")
    n_ok = 0
    first_bad = None
    for i, want in enumerate(canonical):
        answer = got[i] if i < len(got) else "<missing>"
        if answer == "OK " + want:
            n_ok += 1
        elif first_bad is None:
            first_bad = (i, want, answer)
    print("    parse then write == the model : %d of %d  %s"
          % (n_ok, len(canonical), "PASS" if n_ok == len(canonical) else "FAIL"))
    if first_bad is not None:
        i, want, answer = first_bad
        print("    first disagreement, case %d" % i)
        print("      model  %s" % want[:160])
        print("      binary %s" % answer[:160])
        fails.append("case %d disagrees" % i)

    print("\n(2) NON-CANONICAL SPELLINGS ARE REFUSED")
    variants = [
        ("unsorted keys",          '{"b":1,"a":2}'),
        ("a duplicate key",        '{"a":1,"a":2}'),
        ("a space after a colon",  '{"a": 1}'),
        ("a space after a comma",  '{"a":1, "b":2}'),
        ("a leading space",        ' {"a":1}'),
        ("a trailing newline byte",'{"a":1} '),
        ("a fraction",             '{"a":1.0}'),
        ("an exponent",            '{"a":1e3}'),
        ("a leading zero",         '{"a":01}'),
        ("a plus sign",            '{"a":+1}'),
        ("NaN",                    '{"a":NaN}'),
        ("Infinity",               '{"a":Infinity}'),
        ("a needless \\u escape",  '{"a":"\\u0041"}'),
        ("an escaped solidus",     '{"a":"\\/"}'),
        ("an uppercase \\u",       '{"a":"\\u000A"}'),
        ("a raw control byte",     '{"a":"\x01"}'),
        ("64-bit as a number",     '{"t_mono_ns":12}'),
        ("64-bit with a leading 0",'{"t_mono_ns":"012"}'),
        ("int16 as a string",      '{"m_hand":"1"}'),
        ("int16 out of range",     '{"m_hand":32768}'),
        ("a bare int above 2**53", '{"a":9007199254740992}'),
        ("single quotes",          "{'a':1}"),
        ("a trailing comma",       '{"a":1,}'),
        ("an unquoted key",        '{a:1}'),
    ]
    rc2, got2, _ = run_batch(exe, [v[1] for v in variants])
    for i, (label, text) in enumerate(variants):
        answer = got2[i] if i < len(got2) else "<missing>"
        ok = answer.startswith("REFUSED")
        print("    %-26s %s" % (label, "REFUSED" if ok else "ACCEPTED  <-- FAIL"))
        if not ok:
            fails.append("%s was not refused" % label)

    print("\n(3) THE PLANTED LIES -- each must be refused or differ")
    for name, lie in LIES:
        texts = []
        applicable = []
        for i, case in enumerate(cases):
            try:
                t = lie(case)
            except (TypeError, ValueError):
                continue
            if t != canonical[i]:
                texts.append(t)
                applicable.append(i)
        if not texts:
            print("    %-32s no case distinguishes it  <-- FAIL" % name)
            fails.append("the planted lie %r is invisible to this corpus" % name)
            continue
        rc3, got3, _ = run_batch(exe, texts)
        caught = 0
        for j in range(len(texts)):
            answer = got3[j] if j < len(got3) else "<missing>"
            # Caught means: refused outright, or accepted but re-emitted as
            # different bytes -- either way the lie does not survive as canon.
            if answer.startswith("REFUSED") or answer.startswith("DRIFT"):
                caught += 1
        ok = (caught == len(texts))
        print("    %-32s %d of %d caught  %s"
              % (name, caught, len(texts), "CAUGHT" if ok else "NOT CAUGHT"))
        if not ok:
            fails.append("the planted lie %r survived %d times"
                         % (name, len(texts) - caught))

    print("\n(4) THE NEGATIVE CONTROLS")
    # A: corrupt one expected answer; block (1)'s comparison must find exactly
    # one disagreement and name it.
    if got and len(got) == len(canonical):
        victim = len(got) // 3
        corrupted = list(got)
        corrupted[victim] = corrupted[victim] + "x"
        seen = [i for i in range(len(canonical))
                if corrupted[i] != "OK " + canonical[i]]
        ok = (seen == [victim])
        print("    A. one answer corrupted -> the comparison reports %s  %s"
              % (seen if len(seen) < 4 else "many",
                 "PASS (it can fail)" if ok else "FAIL (it cannot fail)"))
        if not ok:
            fails.append("the agreement check did not catch a corrupted answer")
    else:
        fails.append("negative control A could not run")

    # B: the refusal battery, re-run with the refusal requirement inverted. If
    # the binary refused everything unconditionally, block (2) would pass for
    # the wrong reason -- so feed it documents that MUST be accepted and check
    # it does not refuse them.
    must_accept = canonical[:50]
    rc4, got4, _ = run_batch(exe, must_accept)
    wrongly_refused = sum(1 for a in got4 if a.startswith("REFUSED"))
    ok = (wrongly_refused == 0)
    print("    B. 50 canonical documents fed to the refusing reader:")
    print("       %d refused  %s"
          % (wrongly_refused,
             "PASS (it refuses spellings, not everything)" if ok
             else "FAIL (it refuses indiscriminately, so block 2 proved nothing)"))
    if not ok:
        fails.append("the reader refuses canonical documents")

    print("\n" + "=" * 78)
    if fails:
        print("RESULT: FAIL")
        for f in fails:
            print("  - %s" % f)
        print("=" * 78)
        return 1
    print("RESULT: PASS -- %d of %d canonical documents survive the C reader"
          % (n_ok, len(canonical)))
    print("        and writer unchanged; %d of %d non-canonical spellings"
          % (len(variants), len(variants)))
    print("        refused; 4 of 4 planted lies caught; 2 of 2 controls held.")
    print("=" * 78)
    return 0


if __name__ == "__main__":
    sys.exit(main())
