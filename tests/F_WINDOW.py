"""F-WINDOW -- BLUEPRINT_v0.2.md section 21; law 4; gate M3 (section 22).

requires    : a windowed effect reversed inside its window leaves no trace in
              the world and a `reversed` row on the tape, against the provider
              actually wired
planted lie : release before the window

Contract, identical for all forty-seven falsifiers:

  requires()    runs the property against the system under test. Returns None
                when the property holds; raises AssertionError carrying the
                counterexample when it does not.
  planted_lie() builds the sabotaged system this falsifier is aimed at, runs
                requires() against it, and asserts that requires() FAILED. A
                falsifier whose planted lie passes is measuring nothing, and
                that is the failure this function must report.
"""

ID = "F-WINDOW"
MILESTONE = "M3"
REQUIRES = ("a windowed effect reversed inside its window leaves no trace in the "
            "world and a `reversed` row on the tape, against the provider "
            "actually wired")
PLANTED_LIE = "release before the window"


def requires():
    raise NotImplementedError(
        "F-WINDOW must assert, against the provider actually wired rather than a "
        "mock, that an effect reversed inside its reversal window leaves the "
        "venue byte-identical to never having acted, and leaves exactly one "
        "`reversed` row on the tape.")


def planted_lie():
    raise NotImplementedError(
        "F-WINDOW's planted lie must release the effect to the provider before "
        "the window has elapsed and assert that requires() raises AssertionError "
        "naming the venue artifact that survived the reversal.")
