"""F-DEGRADE -- BLUEPRINT_v0.2.md section 21; law 11; gate M6 (section 22).

requires    : an obligation whose check evidence depended on an organ answering
              3, 4, 5 or 6 never reaches DO
planted lie : a missing organ as a clean check

Contract, identical for all forty-seven falsifiers:

  requires()    runs the property against the system under test. Returns None
                when the property holds; raises AssertionError carrying the
                counterexample when it does not.
  planted_lie() builds the sabotaged system this falsifier is aimed at, runs
                requires() against it, and asserts that requires() FAILED. A
                falsifier whose planted lie passes is measuring nothing, and
                that is the failure this function must report.
"""

ID = "F-DEGRADE"
MILESTONE = "M6"
REQUIRES = ("an obligation whose check evidence depended on an organ answering "
            "3, 4, 5 or 6 never reaches DO")
PLANTED_LIE = "a missing organ as a clean check"


def requires():
    raise NotImplementedError(
        "F-DEGRADE must assert that any obligation whose contradiction evidence "
        "came from an organ call that returned 3, 4, 5 or 6 carries the DEGRADED "
        "flag and produces no DO verb row, at any rung.")


def planted_lie():
    raise NotImplementedError(
        "F-DEGRADE's planted lie must treat an absent organ's non-answer as a "
        "clean check and assert that requires() raises AssertionError naming the "
        "obligation that reached DO and the organ code its evidence rested on.")
