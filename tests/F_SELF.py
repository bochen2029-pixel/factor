"""F-SELF -- BLUEPRINT_v0.2.md section 21; law 12; gate M1 (Amendment 1 item 24).

requires    : a lane whose producer dies opens a `health` obligation within one
              tick; a `health` obligation never reaches DO; a health discharge
              never writes an autostart entry; health never exceeds `self_share`
planted lie : health at DO; an autostart

Gate: M1. In v0.2 as published F-SELF was the one falsifier in section 21's table
that no milestone gate in section 22 named, so nothing in the build order forced
it to be written; the scaffold recorded "none" rather than guess, and
qc/O6_tests_v0.2.md item 27 asked for a decision. Amendment 1 item 24 makes it:
"F-SELF is gated at M1, where the `health` lane ships."

Contract, identical for all forty-seven falsifiers:

  requires()    runs the property against the system under test. Returns None
                when the property holds; raises AssertionError carrying the
                counterexample when it does not.
  planted_lie() builds the sabotaged system this falsifier is aimed at, runs
                requires() against it, and asserts that requires() FAILED. A
                falsifier whose planted lie passes is measuring nothing, and
                that is the failure this function must report.
"""

ID = "F-SELF"
MILESTONE = "M1"
REQUIRES = ("a lane whose producer dies opens a `health` obligation within one "
            "tick; a `health` obligation never reaches DO; a health discharge "
            "never writes an autostart entry; health never exceeds `self_share`")
PLANTED_LIE = "health at DO; an autostart"


def requires():
    raise NotImplementedError(
        "F-SELF must assert four things over a run in which a producer is killed: "
        "a `health` obligation for that lane appears within one tick, no "
        "obligation of kind health ever carries a DO verb row, no health "
        "discharge writes an autostart or service entry anywhere on the box, and "
        "the share of the period's budget spent on health never exceeds "
        "`self_share`.")


def planted_lie():
    raise NotImplementedError(
        "F-SELF's planted lie must run a kernel that lets a health obligation "
        "reach DO and repair itself by writing an autostart entry, and assert "
        "that requires() raises AssertionError naming the health obligation that "
        "acted and the autostart entry it wrote.")
