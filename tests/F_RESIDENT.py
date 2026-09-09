"""F-RESIDENT -- BLUEPRINT_v0.2.md section 21; law 1; gate M1 (section 22).

requires    : a run with no frames writes no verb row; every verb row's wake
              names a frame
planted lie : a verb from a timer callback

Contract, identical for all forty-seven falsifiers:

  requires()    runs the property against the system under test. Returns None
                when the property holds; raises AssertionError carrying the
                counterexample when it does not.
  planted_lie() builds the sabotaged system this falsifier is aimed at, runs
                requires() against it, and asserts that requires() FAILED. A
                falsifier whose planted lie passes is measuring nothing, and
                that is the failure this function must report.
"""

ID = "F-RESIDENT"
MILESTONE = "M1"
REQUIRES = ("a run with no frames writes no verb row; every verb row's wake "
            "names a frame")
PLANTED_LIE = "a verb from a timer callback"


def requires():
    raise NotImplementedError(
        "F-RESIDENT must assert that a kernel run over an empty spool set emits "
        "zero verb rows, and that every verb row on a non-empty run carries a "
        "wake naming the (lane, generation, offset, h) of the frame that woke it.")


def planted_lie():
    raise NotImplementedError(
        "F-RESIDENT's planted lie must run a kernel whose walk is driven by a "
        "timer callback rather than by frame arrival, and assert that requires() "
        "raises AssertionError naming the verb row whose wake names no frame.")
