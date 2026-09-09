"""F-ORDER -- BLUEPRINT_v0.2.md section 21; law 4; gate M3 (section 22).

requires    : every `executed` row is preceded by its `staged` and `verb` rows;
              a failed effect leaves a `verb` row and a `warn`
planted lie : execute then record

Contract, identical for all forty-seven falsifiers:

  requires()    runs the property against the system under test. Returns None
                when the property holds; raises AssertionError carrying the
                counterexample when it does not.
  planted_lie() builds the sabotaged system this falsifier is aimed at, runs
                requires() against it, and asserts that requires() FAILED. A
                falsifier whose planted lie passes is measuring nothing, and
                that is the failure this function must report.
"""

ID = "F-ORDER"
MILESTONE = "M3"
REQUIRES = ("every `executed` row is preceded by its `staged` and `verb` rows; a "
            "failed effect leaves a `verb` row and a `warn`")
PLANTED_LIE = "execute then record"


def requires():
    raise NotImplementedError(
        "F-ORDER must assert that every `executed` row on the tape is preceded, "
        "in chain order, by the `staged` and `verb` rows for the same obligation "
        "and effect digest, and that an effect that failed at the provider leaves "
        "a `verb` row and a `warn` row and no `executed` row.")


def planted_lie():
    raise NotImplementedError(
        "F-ORDER's planted lie must run a hand that calls the provider first and "
        "writes its rows afterwards, and assert that requires() raises "
        "AssertionError naming the `executed` row whose `staged` row is later in "
        "the chain than it is.")
