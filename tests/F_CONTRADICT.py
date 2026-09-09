"""F-CONTRADICT -- BLUEPRINT_v0.2.md section 21; law section 13; gate M6 (section 22).

requires    : a planted typed disagreement is caught by the comparator, a planted
              prose disagreement by the inference head, neither by the other; a
              contested pair is never resolved
planted lie : one head for both

Contract, identical for all forty-seven falsifiers:

  requires()    runs the property against the system under test. Returns None
                when the property holds; raises AssertionError carrying the
                counterexample when it does not.
  planted_lie() builds the sabotaged system this falsifier is aimed at, runs
                requires() against it, and asserts that requires() FAILED. A
                falsifier whose planted lie passes is measuring nothing, and
                that is the failure this function must report.
"""

ID = "F-CONTRADICT"
MILESTONE = "M6"
REQUIRES = ("a planted typed disagreement is caught by the comparator, a planted "
            "prose disagreement by the inference head, neither by the other; a "
            "contested pair is never resolved")
PLANTED_LIE = "one head for both"


def requires():
    raise NotImplementedError(
        "F-CONTRADICT must assert the full two-by-two: the typed disagreement is "
        "caught by the comparator and MISSED by the inference head, the prose "
        "disagreement is caught by the inference head and MISSED by the "
        "comparator, and a pair flagged contested is left contested rather than "
        "silently resolved to one side.")


def planted_lie():
    raise NotImplementedError(
        "F-CONTRADICT's planted lie must route both kinds of disagreement through "
        "a single head and assert that requires() raises AssertionError naming the "
        "planted disagreement that head missed.")
