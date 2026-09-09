"""F-ROLLBACK-MONOTONE -- BLUEPRINT_v0.2.md section 21; law 8; gate M7 (section 22).

requires    : a rollback never re-widens a band
planted lie : restore yesterday's license

Contract, identical for all forty-seven falsifiers:

  requires()    runs the property against the system under test. Returns None
                when the property holds; raises AssertionError carrying the
                counterexample when it does not.
  planted_lie() builds the sabotaged system this falsifier is aimed at, runs
                requires() against it, and asserts that requires() FAILED. A
                falsifier whose planted lie passes is measuring nothing, and
                that is the failure this function must report.
"""

ID = "F-ROLLBACK-MONOTONE"
MILESTONE = "M7"
REQUIRES = "a rollback never re-widens a band"
PLANTED_LIE = "restore yesterday's license"


def requires():
    raise NotImplementedError(
        "F-ROLLBACK-MONOTONE must assert that after a rollback to an earlier head, "
        "every class's band and rung are no wider than they were immediately "
        "before the rollback -- the license fold is one-way and rolling the tape "
        "back must not be a way to recover authority that was withdrawn.")


def planted_lie():
    raise NotImplementedError(
        "F-ROLLBACK-MONOTONE's planted lie must restore the license fold verbatim "
        "from the earlier head, re-widening a band that had since narrowed, and "
        "assert that requires() raises AssertionError naming the class and the two "
        "band indexes.")
