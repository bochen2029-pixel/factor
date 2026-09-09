"""F-EXPIRY -- BLUEPRINT_v0.2.md section 21; law 6; gate M4 (section 22).

requires    : a rung past its ratification's window drops one; classes ratified
              together do not expire in one cohort
planted lie : permanent once approved

Contract, identical for all forty-seven falsifiers:

  requires()    runs the property against the system under test. Returns None
                when the property holds; raises AssertionError carrying the
                counterexample when it does not.
  planted_lie() builds the sabotaged system this falsifier is aimed at, runs
                requires() against it, and asserts that requires() FAILED. A
                falsifier whose planted lie passes is measuring nothing, and
                that is the failure this function must report.
"""

ID = "F-EXPIRY"
MILESTONE = "M4"
REQUIRES = ("a rung past its ratification's window drops one; classes ratified "
            "together do not expire in one cohort")
PLANTED_LIE = "permanent once approved"


def requires():
    raise NotImplementedError(
        "F-EXPIRY must assert that a class whose ratification window has elapsed "
        "drops exactly one rung at the next fold, and that classes ratified in "
        "the same batch have their expiries spread so they do not all fall due at "
        "one head and strand the operator with a cohort to re-ratify at once.")


def planted_lie():
    raise NotImplementedError(
        "F-EXPIRY's planted lie must treat a ratification as permanent once "
        "approved and assert that requires() raises AssertionError naming the "
        "class still at its old rung and the head at which its window closed.")
