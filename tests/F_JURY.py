"""F-JURY -- BLUEPRINT_v0.2.md section 21; law 7; gate M5 (section 22).

requires    : one dissenting family and the irreversible effect holds; a quorum
              of one family counted twice is refused; an approval bound to
              different effect bytes is refused
planted lie : two judges of one lineage as two families

Contract, identical for all forty-seven falsifiers:

  requires()    runs the property against the system under test. Returns None
                when the property holds; raises AssertionError carrying the
                counterexample when it does not.
  planted_lie() builds the sabotaged system this falsifier is aimed at, runs
                requires() against it, and asserts that requires() FAILED. A
                falsifier whose planted lie passes is measuring nothing, and
                that is the failure this function must report.
"""

ID = "F-JURY"
MILESTONE = "M5"
REQUIRES = ("one dissenting family and the irreversible effect holds; a quorum "
            "of one family counted twice is refused; an approval bound to "
            "different effect bytes is refused")
PLANTED_LIE = "two judges of one lineage as two families"


def requires():
    raise NotImplementedError(
        "F-JURY must assert that an irreversible effect with one dissenting "
        "family produces a hold and no `executed` row, that a quorum assembled "
        "from one family counted twice is refused with a row, and that an "
        "approval whose bound digest does not equal the effect's actual bytes is "
        "refused.")


def planted_lie():
    raise NotImplementedError(
        "F-JURY's planted lie must seat two judges of the same lineage and count "
        "them as two families, and assert that requires() raises AssertionError "
        "naming the shared lineage and the effect that cleared on a false quorum.")
