"""F-COMPILE -- BLUEPRINT_v0.2.md section 21; law 9; gate M7 (section 22).

requires    : a ratified routine replays bit-identically against the tape it was
              compiled from; an out-of-domain instance falls back; a diverging
              routine suspends in real time
planted lie : a routine that passes on a sample; a routine that extrapolates

Contract, identical for all forty-seven falsifiers:

  requires()    runs the property against the system under test. Returns None
                when the property holds; raises AssertionError carrying the
                counterexample when it does not.
  planted_lie() builds the sabotaged system this falsifier is aimed at, runs
                requires() against it, and asserts that requires() FAILED. A
                falsifier whose planted lie passes is measuring nothing, and
                that is the failure this function must report.
"""

ID = "F-COMPILE"
MILESTONE = "M7"
REQUIRES = ("a ratified routine replays bit-identically against the tape it was "
            "compiled from; an out-of-domain instance falls back; a diverging "
            "routine suspends in real time")
PLANTED_LIE = ("a routine that passes on a sample; a routine that extrapolates")


def requires():
    raise NotImplementedError(
        "F-COMPILE must assert that a ratified routine reproduces every verb row "
        "of the tape it was compiled from, not a sample of them, that an instance "
        "outside the routine's declared domain falls back to the judge instead of "
        "being answered, and that a routine whose live output diverges is "
        "suspended within the period the divergence appears in.")


def planted_lie():
    raise NotImplementedError(
        "F-COMPILE's planted lie must accept a routine validated on a sample of "
        "the tape and allowed to extrapolate past its domain, and assert that "
        "requires() raises AssertionError naming the row it got wrong and the "
        "out-of-domain instance it answered anyway.")
