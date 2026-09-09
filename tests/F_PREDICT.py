"""F-PREDICT -- BLUEPRINT_v0.2.md section 21; law 6; gate M4 (section 22).

requires    : every bet on the tape precedes its grade in horizon order; a
              re-fold reproduces every e-value bit-identically
planted lie : a bet computed from the grade it reads

Contract, identical for all forty-seven falsifiers:

  requires()    runs the property against the system under test. Returns None
                when the property holds; raises AssertionError carrying the
                counterexample when it does not.
  planted_lie() builds the sabotaged system this falsifier is aimed at, runs
                requires() against it, and asserts that requires() FAILED. A
                falsifier whose planted lie passes is measuring nothing, and
                that is the failure this function must report.
"""

ID = "F-PREDICT"
MILESTONE = "M4"
REQUIRES = ("every bet on the tape precedes its grade in horizon order; a "
            "re-fold reproduces every e-value bit-identically")
PLANTED_LIE = "a bet computed from the grade it reads"


def requires():
    raise NotImplementedError(
        "F-PREDICT must assert that every `expect` row precedes the `grade` row it "
        "is scored against, both in chain order and in horizon order, and that "
        "re-folding the same tape reproduces every e-value bit-identically as a "
        "fixed-point integer.")


def planted_lie():
    raise NotImplementedError(
        "F-PREDICT's planted lie must compute a bet from the grade it is about to "
        "be scored against and assert that requires() raises AssertionError naming "
        "the bet row whose head is later than the grade it read.")
