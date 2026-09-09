"""F-FRONT -- BLUEPRINT_v0.2.md section 21; law 6; gate M6 (section 22).

requires    : a planted distribution shift suspends the class before its expiry;
              a stationary stream does not
planted lie : fronts read at the fold's cadence

Contract, identical for all forty-seven falsifiers:

  requires()    runs the property against the system under test. Returns None
                when the property holds; raises AssertionError carrying the
                counterexample when it does not.
  planted_lie() builds the sabotaged system this falsifier is aimed at, runs
                requires() against it, and asserts that requires() FAILED. A
                falsifier whose planted lie passes is measuring nothing, and
                that is the failure this function must report.
"""

ID = "F-FRONT"
MILESTONE = "M6"
REQUIRES = ("a planted distribution shift suspends the class before its expiry; "
            "a stationary stream does not")
PLANTED_LIE = "fronts read at the fold's cadence"


def requires():
    raise NotImplementedError(
        "F-FRONT must assert both arms: a stream carrying a planted distribution "
        "shift suspends the affected class strictly before that class's "
        "ratification expiry, and a stationary stream of the same length and rate "
        "produces no suspension at all.")


def planted_lie():
    raise NotImplementedError(
        "F-FRONT's planted lie must read the front only at the fold's cadence, so "
        "the shift is seen late, and assert that requires() raises AssertionError "
        "naming the head at which the shift began and the later head at which the "
        "class was suspended.")
