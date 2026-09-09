"""F-MOLT -- BLUEPRINT_v0.2.md section 21; law 8; gate M7 (section 22).

requires    : a planted fact in the oldest band survives the fold at the family's
              ratio or the account prints `lossy`
planted lie : silent truncation at the watermark

Contract, identical for all forty-seven falsifiers:

  requires()    runs the property against the system under test. Returns None
                when the property holds; raises AssertionError carrying the
                counterexample when it does not.
  planted_lie() builds the sabotaged system this falsifier is aimed at, runs
                requires() against it, and asserts that requires() FAILED. A
                falsifier whose planted lie passes is measuring nothing, and
                that is the failure this function must report.
"""

ID = "F-MOLT"
MILESTONE = "M7"
REQUIRES = ("a planted fact in the oldest band survives the fold at the family's "
            "ratio or the account prints `lossy`")
PLANTED_LIE = "silent truncation at the watermark"


def requires():
    raise NotImplementedError(
        "F-MOLT must assert the disjunction as written: a fact planted in the "
        "oldest band is still recoverable after the molt at no worse than the "
        "family's declared ratio, or, if it is not, the account prints `lossy` "
        "for that band -- what is forbidden is losing it quietly.")


def planted_lie():
    raise NotImplementedError(
        "F-MOLT's planted lie must truncate the oldest band at the watermark "
        "without setting the `lossy` mark, and assert that requires() raises "
        "AssertionError naming the planted fact that vanished and the band it was "
        "in.")
