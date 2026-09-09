"""F-RIPEN -- BLUEPRINT_v0.2.md section 21; laws 1, 13; gate M1 (section 22).

requires    : a deadline crossing with no inbound frame still produces a verb row
planted lie : walk only the event-touched set

Contract, identical for all forty-seven falsifiers:

  requires()    runs the property against the system under test. Returns None
                when the property holds; raises AssertionError carrying the
                counterexample when it does not.
  planted_lie() builds the sabotaged system this falsifier is aimed at, runs
                requires() against it, and asserts that requires() FAILED. A
                falsifier whose planted lie passes is measuring nothing, and
                that is the failure this function must report.
"""

ID = "F-RIPEN"
MILESTONE = "M1"
REQUIRES = ("a deadline crossing with no inbound frame still produces a verb row")
PLANTED_LIE = "walk only the event-touched set"


def requires():
    raise NotImplementedError(
        "F-RIPEN must assert that an obligation whose due_ns is crossed during a "
        "period in which no frame touched that obligation still produces a verb "
        "row for it in that period, sourced from the ripeness walk rather than "
        "from an arrival.")


def planted_lie():
    raise NotImplementedError(
        "F-RIPEN's planted lie must run a walk restricted to the set of "
        "obligations touched by the period's frames and assert that requires() "
        "raises AssertionError naming the ripe obligation that produced no row.")
