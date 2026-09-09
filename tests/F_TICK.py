"""F-TICK -- BLUEPRINT_v0.2.md section 21; law 1; gate M7 (section 22).

requires    : a restored trunk receives one tick for its absence; the first
              frame's margins match a no-restart control within the tie band
planted lie : resume with no tick

Contract, identical for all forty-seven falsifiers:

  requires()    runs the property against the system under test. Returns None
                when the property holds; raises AssertionError carrying the
                counterexample when it does not.
  planted_lie() builds the sabotaged system this falsifier is aimed at, runs
                requires() against it, and asserts that requires() FAILED. A
                falsifier whose planted lie passes is measuring nothing, and
                that is the failure this function must report.
"""

ID = "F-TICK"
MILESTONE = "M7"
REQUIRES = ("a restored trunk receives one tick for its absence; the first "
            "frame's margins match a no-restart control within the tie band")
PLANTED_LIE = "resume with no tick"


def requires():
    raise NotImplementedError(
        "F-TICK must assert that a trunk restored from a checkpoint receives "
        "exactly one tick frame covering the whole absence before the next real "
        "frame, and that the three margins on that next frame differ from a "
        "control run that never restarted by no more than the tie band.")


def planted_lie():
    raise NotImplementedError(
        "F-TICK's planted lie must restore a trunk with the absence tick "
        "suppressed and assert that requires() raises AssertionError naming "
        "either the missing tick or the margin that moved outside the tie band.")
