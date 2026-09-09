"""F-SALT -- BLUEPRINT_v0.2.md section 21; law 19; gate M4 (section 22).

requires    : every lottery assignment is reproducible from the writ and
              unpredictable from the trunk
planted lie : a system random generator

Contract, identical for all forty-seven falsifiers:

  requires()    runs the property against the system under test. Returns None
                when the property holds; raises AssertionError carrying the
                counterexample when it does not.
  planted_lie() builds the sabotaged system this falsifier is aimed at, runs
                requires() against it, and asserts that requires() FAILED. A
                falsifier whose planted lie passes is measuring nothing, and
                that is the failure this function must report.
"""

ID = "F-SALT"
MILESTONE = "M4"
REQUIRES = ("every lottery assignment is reproducible from the writ and "
            "unpredictable from the trunk")
PLANTED_LIE = "a system random generator"


def requires():
    raise NotImplementedError(
        "F-SALT must assert both halves at once: replaying the stratum lottery "
        "from the writ's salt reproduces every assignment exactly, and a "
        "predictor given only the trunk's contents does no better than chance at "
        "guessing the next assignment.")


def planted_lie():
    raise NotImplementedError(
        "F-SALT's planted lie must draw the lottery from the system random "
        "generator instead of the writ's salt and assert that requires() raises "
        "AssertionError naming the first assignment that failed to reproduce on "
        "replay.")
