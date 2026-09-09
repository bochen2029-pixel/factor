"""F-BUDGET -- BLUEPRINT_v0.2.md section 21; law 13; gate M1 (section 22).

requires    : two thousand asks, room for ten, the rest hold on budget and
              nothing acts; the stratum is funded first
planted lie : act because nobody was available

Contract, identical for all forty-seven falsifiers:

  requires()    runs the property against the system under test. Returns None
                when the property holds; raises AssertionError carrying the
                counterexample when it does not.
  planted_lie() builds the sabotaged system this falsifier is aimed at, runs
                requires() against it, and asserts that requires() FAILED. A
                falsifier whose planted lie passes is measuring nothing, and
                that is the failure this function must report.
"""

ID = "F-BUDGET"
MILESTONE = "M1"
REQUIRES = ("two thousand asks, room for ten, the rest hold on budget and "
            "nothing acts; the stratum is funded first")
PLANTED_LIE = "act because nobody was available"


def requires():
    raise NotImplementedError(
        "F-BUDGET must assert that with two thousand obligations wanting an ask "
        "and a budget for ten, exactly ten asks are issued, the remaining one "
        "thousand nine hundred and ninety hold with reason `budget`, no DO row "
        "appears anywhere in the run, and the stratum's reserved share was "
        "allocated before any discretionary ask.")


def planted_lie():
    raise NotImplementedError(
        "F-BUDGET's planted lie must run a kernel that escalates to acting when "
        "no ask slot and no human seat is available, and assert that requires() "
        "raises AssertionError naming the DO row that appeared under budget "
        "exhaustion.")
