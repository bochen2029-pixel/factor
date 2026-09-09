"""F-SILENCE -- BLUEPRINT_v0.2.md section 21; law 3; gate M1 (section 22).

requires    : a judgment without a row is fatal; no open obligation lacks a
              standing verb
planted lie : a hold with no row

Contract, identical for all forty-seven falsifiers:

  requires()    runs the property against the system under test. Returns None
                when the property holds; raises AssertionError carrying the
                counterexample when it does not.
  planted_lie() builds the sabotaged system this falsifier is aimed at, runs
                requires() against it, and asserts that requires() FAILED. A
                falsifier whose planted lie passes is measuring nothing, and
                that is the failure this function must report.
"""

ID = "F-SILENCE"
MILESTONE = "M1"
REQUIRES = ("a judgment without a row is fatal; no open obligation lacks a "
            "standing verb")
PLANTED_LIE = "a hold with no row"


def requires():
    raise NotImplementedError(
        "F-SILENCE must assert that every judgment the kernel computed is "
        "represented by a verb row on the tape -- a judgment with no row is a "
        "fatal, not a warn -- and that at the end of every period no obligation "
        "in a contributing state is without a standing verb.")


def planted_lie():
    raise NotImplementedError(
        "F-SILENCE's planted lie must run a kernel that decides HOLD on one "
        "obligation and writes no row for it, and assert that requires() raises "
        "AssertionError naming that obligation id and the period it fell silent in.")
