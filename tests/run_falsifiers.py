"""run_falsifiers.py -- run the forty-seven falsifiers of BLUEPRINT_v0.2.md section 21.

Imports each F_<ID>.py stub, calls requires() and planted_lie(), and prints one
line per falsifier. Nothing here crashes on an unimplemented falsifier: a stub
that raises NotImplementedError is reported TODO and the run continues, which is
what makes this runnable from milestone M0 onward while the forty-seven fill in
one gate at a time.

Every falsifier is named EXPLICITLY in the table below, with the id section 21
gives it and the milestone gate section 22 puts it behind. Nothing is globbed.
Three things therefore fail loudly rather than silently:

  * a file that is deleted or renamed        -> MISSING
  * a module whose ID does not match its row -> ERROR (id mismatch)
  * a module whose MILESTONE does not match  -> ERROR (gate mismatch)

Status codes
  PASS     the function returned; the property holds / the lie was caught
  FAIL     it raised AssertionError; the property does not hold
  TODO     it raised NotImplementedError; the falsifier is still a stub
  ERROR    it raised something else, or the module disagrees with its row
  MISSING  the file is not there

Exit 0 when every falsifier is PASS or TODO. Exit 1 on any FAIL, ERROR or
MISSING -- a broken or absent falsifier is a build failure, an unwritten one is
not.

  python C:/FACTOR/tests/run_falsifiers.py
  python C:/FACTOR/tests/run_falsifiers.py --verbose
  python C:/FACTOR/tests/run_falsifiers.py --gate M0
"""

import importlib.util
import os
import sys

sys.dont_write_bytecode = True   # a spec repo keeps no __pycache__

HERE = os.path.dirname(os.path.abspath(__file__))

# The forty-seven, in section 21's table order, the two M8 rows last.
#   (module, section 21 id, section 22 gate)
#
# Gate notes, from section 22 verbatim and Amendment 1 item 24:
#   F-CONSERVE is gated at M0 "without the heard bucket" and again at M2 "full";
#   F-EGRESS   is gated at M0 and again at M3 "full". The earliest gate is the
#              one recorded, because that is the milestone the falsifier must
#              first exist for.
#   F-SELF     was named by no section 22 gate in v0.2 as published and was
#              recorded here as "none". Amendment 1 item 24 gates it at M1,
#              "where the `health` lane ships".
#   F-ORGAN-DEGRADE and F-ORGAN-NET are Amendment 1 item 24's two new rows, both
#              at M8, whose three gate conditions section 22 had stated only in
#              prose. Section 21's table in the file above still shows 45 rows;
#              the amendment is what makes it 47.
FALSIFIERS = [
    ("F_RESIDENT",          "F-RESIDENT",          "M1"),
    ("F_TICK",              "F-TICK",              "M7"),
    ("F_RIPEN",             "F-RIPEN",             "M1"),
    ("F_EXTRACT",           "F-EXTRACT",           "M2"),
    ("F_SILENCE",           "F-SILENCE",           "M1"),
    ("F_CONSERVE",          "F-CONSERVE",          "M0"),
    ("F_REPLAY",            "F-REPLAY",            "M0"),
    ("F_DETERMINISM",       "F-DETERMINISM",       "M0"),
    ("F_QUANTA",            "F-QUANTA",            "M1"),
    ("F_SALT",              "F-SALT",              "M4"),
    ("F_CHAIN",             "F-CHAIN",             "M0"),
    ("F_INERT",             "F-INERT",             "M1"),
    ("F_INERT_BYTES",       "F-INERT-BYTES",       "M1"),
    ("F_BLIND",             "F-BLIND",             "M1"),
    ("F_STANDING",          "F-STANDING",          "M2"),
    ("F_EGRESS",            "F-EGRESS",            "M0"),
    ("F_WINDOW",            "F-WINDOW",            "M3"),
    ("F_ORDER",             "F-ORDER",             "M3"),
    ("F_BUDGET",            "F-BUDGET",            "M1"),
    ("F_TERMINAL",          "F-TERMINAL",          "M4"),
    ("F_SELF",              "F-SELF",              "M1"),
    ("F_JURY",              "F-JURY",              "M5"),
    ("F_FAMILY",            "F-FAMILY",            "M5"),
    ("F_CAP",               "F-CAP",               "M5"),
    ("F_MONOTONE",          "F-MONOTONE",          "M4"),
    ("F_COVERED",           "F-COVERED",           "M4"),
    ("F_BOTH_SIDES",        "F-BOTH-SIDES",        "M4"),
    ("F_WITNESS",           "F-WITNESS",           "M4"),
    ("F_PREDICT",           "F-PREDICT",           "M4"),
    ("F_DETECT",            "F-DETECT",            "M4"),
    ("F_EXPIRY",            "F-EXPIRY",            "M4"),
    ("F_CANARY",            "F-CANARY",            "M4"),
    ("F_FRONT",             "F-FRONT",             "M6"),
    ("F_DARK",              "F-DARK",              "M6"),
    ("F_OBSERVE",           "F-OBSERVE",           "M9"),
    ("F_ROLLBACK",          "F-ROLLBACK",          "M7"),
    ("F_ROLLBACK_MONOTONE", "F-ROLLBACK-MONOTONE", "M7"),
    ("F_MOLT",              "F-MOLT",              "M7"),
    ("F_CONTRADICT",        "F-CONTRADICT",        "M6"),
    ("F_DEGRADE",           "F-DEGRADE",           "M6"),
    ("F_REDACT",            "F-REDACT",            "M6"),
    ("F_COMPILE",           "F-COMPILE",           "M7"),
    ("F_PIN",               "F-PIN",               "M0"),
    ("F_LAYOUT",            "F-LAYOUT",            "M0"),
    ("F_FRAME",             "F-FRAME",             "M0"),
    ("F_ORGAN_DEGRADE",     "F-ORGAN-DEGRADE",     "M8"),
    ("F_ORGAN_NET",         "F-ORGAN-NET",         "M8"),
]

GATE_ORDER = ["M0", "M1", "M2", "M3", "M4", "M5", "M6", "M7", "M8", "M9", "none"]


def load(modname):
    path = os.path.join(HERE, modname + ".py")
    if not os.path.exists(path):
        return None, "file not found: %s" % path
    spec = importlib.util.spec_from_file_location(modname, path)
    mod = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(mod)
    except Exception as e:                                   # noqa: BLE001
        return None, "import failed: %s: %s" % (type(e).__name__, e)
    return mod, None


def call(mod, fname):
    """Return (status, detail)."""
    fn = getattr(mod, fname, None)
    if fn is None:
        return "ERROR", "no %s() in the module" % fname
    try:
        fn()
        return "PASS", ""
    except NotImplementedError as e:
        return "TODO", str(e)
    except AssertionError as e:
        return "FAIL", str(e) or "assertion failed with no message"
    except Exception as e:                                   # noqa: BLE001
        return "ERROR", "%s: %s" % (type(e).__name__, e)


def main(argv):
    verbose = "--verbose" in argv or "-v" in argv
    want_gate = None
    if "--gate" in argv:
        i = argv.index("--gate")
        if i + 1 < len(argv):
            want_gate = argv[i + 1]

    selected = [f for f in FALSIFIERS if want_gate is None or f[2] == want_gate]

    print("=" * 78)
    print("FACTOR BLUEPRINT_v0.2 section 21 as amended -- falsifier battery")
    print("%d falsifiers in section 21, each with a planted lie%s"
          % (len(FALSIFIERS),
             "" if want_gate is None else ("; showing gate %s only" % want_gate)))
    print("=" * 78)
    print()
    print("  %-22s %-5s %-9s %-9s %s"
          % ("falsifier", "gate", "requires", "lie", "id"))
    print("  " + "-" * 74)

    tally = {}
    bad = 0
    details = []
    per_gate = {}
    for modname, want_id, want_gate_row in selected:
        per_gate.setdefault(want_gate_row, []).append(want_id)
        mod, err = load(modname)
        if mod is None:
            print("  %-22s %-5s %-9s %-9s %s"
                  % (modname, want_gate_row, "MISSING", "MISSING", want_id))
            print("      %s" % err)
            tally["MISSING"] = tally.get("MISSING", 0) + 2
            bad += 2
            continue

        fid = getattr(mod, "ID", None)
        gate = getattr(mod, "MILESTONE", None)
        row_problems = []
        if fid != want_id:
            row_problems.append("ID is %r, section 21 says %r" % (fid, want_id))
        if gate != want_gate_row:
            row_problems.append("MILESTONE is %r, section 22 says %r"
                                % (gate, want_gate_row))
        for const in ("REQUIRES", "PLANTED_LIE"):
            if not getattr(mod, const, None):
                row_problems.append("%s is missing or empty" % const)
        if row_problems:
            print("  %-22s %-5s %-9s %-9s %s"
                  % (modname, gate or "?", "ERROR", "ERROR", fid or "?"))
            for p in row_problems:
                print("      %s" % p)
            tally["ERROR"] = tally.get("ERROR", 0) + 2
            bad += 2
            continue

        s_req, d_req = call(mod, "requires")
        s_lie, d_lie = call(mod, "planted_lie")
        for s in (s_req, s_lie):
            tally[s] = tally.get(s, 0) + 1
            if s in ("FAIL", "ERROR", "MISSING"):
                bad += 1
        print("  %-22s %-5s %-9s %-9s %s"
              % (modname, gate, s_req, s_lie, fid))
        if d_req:
            details.append((fid, "requires", s_req, d_req))
        if d_lie:
            details.append((fid, "planted_lie", s_lie, d_lie))

    print("  " + "-" * 74)
    print("  " + "   ".join("%s %d" % (k, v) for k, v in sorted(tally.items())))

    if want_gate is None:
        print()
        print("  by section 22 gate")
        for g in GATE_ORDER:
            if g in per_gate:
                print("    %-5s %2d   %s"
                      % (g, len(per_gate[g]), " ".join(sorted(per_gate[g]))))

    if verbose and details:
        print()
        print("what each unwritten falsifier still has to assert")
        print("-" * 78)
        for fid, fname, status, msg in details:
            print("  [%s] %s.%s" % (status, fid, fname))
            for line in _wrap(msg, 72):
                print("      " + line)

    print()
    n_todo = tally.get("TODO", 0)
    if bad:
        print("RESULT: %d falsifier function(s) FAILED, ERRORED or are MISSING" % bad)
    else:
        print("RESULT: scaffold intact -- %d of %d functions are stubs (TODO), "
              "%d implemented and passing"
              % (n_todo, 2 * len(selected), tally.get("PASS", 0)))
    if not verbose:
        print("        run with --verbose to print what each stub must assert")
    print("=" * 78)
    return 1 if bad else 0


def _wrap(text, width):
    words = " ".join(text.split()).split(" ")
    lines, cur = [], ""
    for w in words:
        if cur and len(cur) + 1 + len(w) > width:
            lines.append(cur)
            cur = w
        else:
            cur = w if not cur else cur + " " + w
    if cur:
        lines.append(cur)
    return lines


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
