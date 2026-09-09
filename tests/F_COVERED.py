"""F-COVERED -- BLUEPRINT_v0.2.md section 21; law 6; gate M4 (section 22).

requires    : every `executed` row at rung 3 or above is preceded by an unexpired
              ratify row covering its class, rung, band and, for a canary, its
              draw; no `executed` row in a class whose kappa read at or above one
              at that head
planted lie : an executed row one revision after expiry

Contract, identical for all forty-seven falsifiers:

  requires()    runs the property against the system under test. Returns None
                when the property holds; raises AssertionError carrying the
                counterexample when it does not.
  planted_lie() builds the sabotaged system this falsifier is aimed at, runs
                requires() against it, and asserts that requires() FAILED. A
                falsifier whose planted lie passes is measuring nothing, and
                that is the failure this function must report.
"""

ID = "F-COVERED"
MILESTONE = "M4"
REQUIRES = ("every `executed` row at rung 3 or above is preceded by an unexpired "
            "ratify row covering its class, rung, band and, for a canary, its "
            "draw; no `executed` row in a class whose kappa read at or above one "
            "at that head")
PLANTED_LIE = "an executed row one revision after expiry"


def requires():
    raise NotImplementedError(
        "F-COVERED must assert, by walking the tape once, that every `executed` "
        "row whose rung is 3 or above has an unexpired ratify row earlier in the "
        "chain covering its class, rung, band and canary draw, and that no "
        "`executed` row exists in a class whose kappa read at or above one at "
        "that head.")


def planted_lie():
    raise NotImplementedError(
        "F-COVERED's planted lie must emit an `executed` row one revision after "
        "its covering ratification expired and assert that requires() raises "
        "AssertionError naming the row, its class, and the head at which the "
        "ratification lapsed.")
