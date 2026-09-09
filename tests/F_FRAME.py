"""F-FRAME -- BLUEPRINT_v0.2.md section 21; law section 4; gate M0 (section 22).

requires    : 10,000 random strings round-trip; each is one line to every reader
planted lie : an encoder that drops carriage returns

Contract, identical for all forty-seven falsifiers:

  requires()    runs the property against the system under test. Returns None
                when the property holds; raises AssertionError carrying the
                counterexample when it does not.
  planted_lie() builds the sabotaged system this falsifier is aimed at, runs
                requires() against it, and asserts that requires() FAILED. A
                falsifier whose planted lie passes is measuring nothing, and
                that is the failure this function must report.

The same property already runs in this directory against a model of the codec
rather than against the built lane: `frame_roundtrip.py` round-trips 10,000
seeded strings through the seven-field frame under the STRICT profile, checks
that every encoded frame is one line under both a byte-level reader and Python's
str.splitlines(), and carries this falsifier's planted lie as its LIE 1. This
stub is what wires it to a real lane and a real spool.
"""

ID = "F-FRAME"
MILESTONE = "M0"
REQUIRES = ("10,000 random strings round-trip; each is one line to every reader")
PLANTED_LIE = "an encoder that drops carriage returns"


def requires():
    raise NotImplementedError(
        "F-FRAME must assert that 10,000 random strings pushed through a real "
        "lane onto a real spool come back byte-identical, and that every frame "
        "written is exactly one line to a byte-level reader, to str.splitlines(), "
        "and to a reader that also splits on VT, FF, FS, GS, RS, NEL, LS and PS.")


def planted_lie():
    raise NotImplementedError(
        "F-FRAME's planted lie must run a lane whose encoder drops carriage "
        "returns before escaping and assert that requires() raises AssertionError "
        "naming the string index whose decoded text differs from what was fed in.")
