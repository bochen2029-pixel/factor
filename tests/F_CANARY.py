"""F-CANARY -- BLUEPRINT_v0.2.md section 21; law 6; gate M4 (section 22).

requires    : under `live`, a rung-2 class acts on the lottery's fraction and no
              other instance; every canary effect is reversible and reverses
              cleanly
planted lie : a canary on an irreversible effect; a canary with no covering row

Contract, identical for all forty-seven falsifiers:

  requires()    runs the property against the system under test. Returns None
                when the property holds; raises AssertionError carrying the
                counterexample when it does not.
  planted_lie() builds the sabotaged system this falsifier is aimed at, runs
                requires() against it, and asserts that requires() FAILED. A
                falsifier whose planted lie passes is measuring nothing, and
                that is the failure this function must report.
"""

ID = "F-CANARY"
MILESTONE = "M4"
REQUIRES = ("under `live`, a rung-2 class acts on the lottery's fraction and no "
            "other instance; every canary effect is reversible and reverses "
            "cleanly")
PLANTED_LIE = ("a canary on an irreversible effect; a canary with no covering "
               "row")


def requires():
    raise NotImplementedError(
        "F-CANARY must assert that under `live` a rung-2 class acts on exactly "
        "the instances the writ's lottery drew and on no others, and that every "
        "canary effect carried a reversible class and reversed to a "
        "byte-identical venue when reversed.")


def planted_lie():
    raise NotImplementedError(
        "F-CANARY's planted lie must draw a canary on an effect whose class is "
        "IRREVERSIBLE and act with no covering ratify row, and assert that "
        "requires() raises AssertionError naming the irreversible effect drawn "
        "and the instance acted on outside the lottery.")
