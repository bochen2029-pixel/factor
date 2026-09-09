"""F-WITNESS -- BLUEPRINT_v0.2.md section 21; law 6; gate M4 (section 22).

requires    : a planted self-written close never licenses; an outcome from the
              lane the effect wrote to is a receipt
planted lie : grade a calendar confirm from the calendar it wrote

Contract, identical for all forty-seven falsifiers:

  requires()    runs the property against the system under test. Returns None
                when the property holds; raises AssertionError carrying the
                counterexample when it does not.
  planted_lie() builds the sabotaged system this falsifier is aimed at, runs
                requires() against it, and asserts that requires() FAILED. A
                falsifier whose planted lie passes is measuring nothing, and
                that is the failure this function must report.
"""

ID = "F-WITNESS"
MILESTONE = "M4"
REQUIRES = ("a planted self-written close never licenses; an outcome from the "
            "lane the effect wrote to is a receipt")
PLANTED_LIE = "grade a calendar confirm from the calendar it wrote"


def requires():
    raise NotImplementedError(
        "F-WITNESS must assert that a close written by FACTOR itself never "
        "contributes to a license fold, and that any outcome arriving on the same "
        "lane the effect wrote to is classified as a receipt rather than as "
        "independent evidence of the outcome.")


def planted_lie():
    raise NotImplementedError(
        "F-WITNESS's planted lie must grade a calendar confirmation read back "
        "from the very calendar the effect wrote, and assert that requires() "
        "raises AssertionError naming the lane the effect wrote to and the grade "
        "it produced.")
