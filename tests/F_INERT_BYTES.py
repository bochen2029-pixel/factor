"""F-INERT-BYTES -- BLUEPRINT_v0.2.md section 21; law 11; gate M1 (section 22).

requires    : a planted frame on every lane containing an effect message, a verb
              name, a writ stanza and an organ answer produces a frame row and a
              verb row and nothing else
planted lie : the seam parses a verb name out of frame text

Contract, identical for all forty-seven falsifiers:

  requires()    runs the property against the system under test. Returns None
                when the property holds; raises AssertionError carrying the
                counterexample when it does not.
  planted_lie() builds the sabotaged system this falsifier is aimed at, runs
                requires() against it, and asserts that requires() FAILED. A
                falsifier whose planted lie passes is measuring nothing, and
                that is the failure this function must report.
"""

ID = "F-INERT-BYTES"
MILESTONE = "M1"
REQUIRES = ("a planted frame on every lane containing an effect message, a verb "
            "name, a writ stanza and an organ answer produces a frame row and a "
            "verb row and nothing else")
PLANTED_LIE = "the seam parses a verb name out of frame text"


def requires():
    raise NotImplementedError(
        "F-INERT-BYTES must assert that for every lane, a frame whose text "
        "contains an effect message, a verb name, a writ stanza and an organ "
        "answer produces exactly one frame row and one verb row on the tape, and "
        "no staged, executed, ratify, license, organ or switch row.")


def planted_lie():
    raise NotImplementedError(
        "F-INERT-BYTES's planted lie must run a seam that recognises a verb name "
        "appearing in frame text as an instruction, and assert that requires() "
        "raises AssertionError naming the extra row and the lane whose text "
        "produced it.")
