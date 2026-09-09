"""F-TERMINAL -- BLUEPRINT_v0.2.md section 21; law 13; gate M4 (section 22).

requires    : an obligation past due with no license and no budget takes its safe
              terminal; `expired` never precedes an `asked` or a `hold(budget)`
planted lie : hold silently

Contract, identical for all forty-seven falsifiers:

  requires()    runs the property against the system under test. Returns None
                when the property holds; raises AssertionError carrying the
                counterexample when it does not.
  planted_lie() builds the sabotaged system this falsifier is aimed at, runs
                requires() against it, and asserts that requires() FAILED. A
                falsifier whose planted lie passes is measuring nothing, and
                that is the failure this function must report.
"""

ID = "F-TERMINAL"
MILESTONE = "M4"
REQUIRES = ("an obligation past due with no license and no budget takes its safe "
            "terminal; `expired` never precedes an `asked` or a `hold(budget)`")
PLANTED_LIE = "hold silently"


def requires():
    raise NotImplementedError(
        "F-TERMINAL must assert that an obligation past its due with no covering "
        "license and no budget reaches its class's declared safe terminal rather "
        "than holding forever, and that in chain order no `expired` row for an "
        "obligation precedes that obligation's `asked` row or its hold row with "
        "reason `budget`.")


def planted_lie():
    raise NotImplementedError(
        "F-TERMINAL's planted lie must run a kernel that holds a past-due, "
        "unlicensed, unfunded obligation with no row and no terminal, and assert "
        "that requires() raises AssertionError naming the obligation id and the "
        "number of periods it sat past due.")
