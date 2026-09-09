"""F-QUANTA -- BLUEPRINT_v0.2.md section 21; law 19; gate M1 (section 22).

requires    : replay under a perturbed batch composition reproduces every verb
              row; rows that differ carry `tie`
planted lie : compare raw logits and call the difference a pass

Contract, identical for all forty-seven falsifiers:

  requires()    runs the property against the system under test. Returns None
                when the property holds; raises AssertionError carrying the
                counterexample when it does not.
  planted_lie() builds the sabotaged system this falsifier is aimed at, runs
                requires() against it, and asserts that requires() FAILED. A
                falsifier whose planted lie passes is measuring nothing, and
                that is the failure this function must report.
"""

ID = "F-QUANTA"
MILESTONE = "M1"
REQUIRES = ("replay under a perturbed batch composition reproduces every verb "
            "row; rows that differ carry `tie`")
PLANTED_LIE = "compare raw logits and call the difference a pass"


def requires():
    raise NotImplementedError(
        "F-QUANTA must assert that a replay in which the batches are composed "
        "differently reproduces every verb row after quantization, and that any "
        "row that does differ is one whose margin landed inside the tie band and "
        "whose record therefore has `tie` incremented.")


def planted_lie():
    raise NotImplementedError(
        "F-QUANTA's planted lie must compare raw pre-quantization logits between "
        "the two runs and report any difference as acceptable noise, and assert "
        "that requires() raises AssertionError naming a verb row that changed "
        "outside the tie band and was waved through.")
