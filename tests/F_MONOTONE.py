"""F-MONOTONE -- BLUEPRINT_v0.2.md section 21; law 6; gate M4 (section 22).

requires    : the license fold cannot widen a band without a covering signed
              ratification row; a ratify row over the API is refused; a row with
              a seen nonce is refused
planted lie : widen on grades alone

Contract, identical for all forty-seven falsifiers:

  requires()    runs the property against the system under test. Returns None
                when the property holds; raises AssertionError carrying the
                counterexample when it does not.
  planted_lie() builds the sabotaged system this falsifier is aimed at, runs
                requires() against it, and asserts that requires() FAILED. A
                falsifier whose planted lie passes is measuring nothing, and
                that is the failure this function must report.
"""

ID = "F-MONOTONE"
MILESTONE = "M4"
REQUIRES = ("the license fold cannot widen a band without a covering signed "
            "ratification row; a ratify row over the API is refused; a row with "
            "a seen nonce is refused")
PLANTED_LIE = "widen on grades alone"


def requires():
    raise NotImplementedError(
        "F-MONOTONE must assert that no fold of the tape widens a class's band or "
        "raises its rung unless a signed ratify row covering that class, rung and "
        "band precedes it in the chain, that a ratify row arriving over the API "
        "surface is refused with a row, and that a ratify row replaying a nonce "
        "already seen is refused.")


def planted_lie():
    raise NotImplementedError(
        "F-MONOTONE's planted lie must run a license fold that widens a band on "
        "accumulated grades with no ratify row, and assert that requires() raises "
        "AssertionError naming the class and the head at which the band widened "
        "uncovered.")
