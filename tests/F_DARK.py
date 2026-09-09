"""F-DARK -- BLUEPRINT_v0.2.md section 21; law 13; gate M6 (section 22).

requires    : an obligation with no recency, ripeness or expectation is judged
              within N periods
planted lie : rank only what moved

Contract, identical for all forty-seven falsifiers:

  requires()    runs the property against the system under test. Returns None
                when the property holds; raises AssertionError carrying the
                counterexample when it does not.
  planted_lie() builds the sabotaged system this falsifier is aimed at, runs
                requires() against it, and asserts that requires() FAILED. A
                falsifier whose planted lie passes is measuring nothing, and
                that is the failure this function must report.
"""

ID = "F-DARK"
MILESTONE = "M6"
REQUIRES = ("an obligation with no recency, ripeness or expectation is judged "
            "within N periods")
PLANTED_LIE = "rank only what moved"


def requires():
    raise NotImplementedError(
        "F-DARK must assert that an obligation scoring zero on recency, ripeness "
        "and expectation still receives a verb row within the writ's declared N "
        "periods, so that nothing open can go permanently unlooked-at.")


def planted_lie():
    raise NotImplementedError(
        "F-DARK's planted lie must rank the walk purely on what moved this period "
        "and assert that requires() raises AssertionError naming the obligation "
        "and the number of periods it went unjudged.")
