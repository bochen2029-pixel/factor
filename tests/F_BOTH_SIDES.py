"""F-BOTH-SIDES -- BLUEPRINT_v0.2.md section 21; law 6; gate M4 (section 22).

requires    : a band is not calibrated until both sides clear `n0`; an outcome
              forged from the hand's own receipt does not calibrate
planted lie : license on act evidence only

Contract, identical for all forty-seven falsifiers:

  requires()    runs the property against the system under test. Returns None
                when the property holds; raises AssertionError carrying the
                counterexample when it does not.
  planted_lie() builds the sabotaged system this falsifier is aimed at, runs
                requires() against it, and asserts that requires() FAILED. A
                falsifier whose planted lie passes is measuring nothing, and
                that is the failure this function must report.
"""

ID = "F-BOTH-SIDES"
MILESTONE = "M4"
REQUIRES = ("a band is not calibrated until both sides clear `n0`; an outcome "
            "forged from the hand's own receipt does not calibrate")
PLANTED_LIE = "license on act evidence only"


def requires():
    raise NotImplementedError(
        "F-BOTH-SIDES must assert that a band is reported uncalibrated until both "
        "the acted side and the held side of its threshold have at least `n0` "
        "graded outcomes, and that an outcome whose only evidence is the hand's "
        "own receipt for the act contributes nothing to either side.")


def planted_lie():
    raise NotImplementedError(
        "F-BOTH-SIDES's planted lie must calibrate a band from acted outcomes "
        "alone and assert that requires() raises AssertionError naming the band, "
        "its two side counts, and the `n0` it did not clear.")
