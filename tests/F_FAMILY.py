"""F-FAMILY -- BLUEPRINT_v0.2.md section 21; law 7; gate M5 (section 22).

requires    : a planted case where two judges of the same lineage agree wrongly
              does not clear a two-family quorum
planted lie : lineage ignored

Contract, identical for all forty-seven falsifiers:

  requires()    runs the property against the system under test. Returns None
                when the property holds; raises AssertionError carrying the
                counterexample when it does not.
  planted_lie() builds the sabotaged system this falsifier is aimed at, runs
                requires() against it, and asserts that requires() FAILED. A
                falsifier whose planted lie passes is measuring nothing, and
                that is the failure this function must report.
"""

ID = "F-FAMILY"
MILESTONE = "M5"
REQUIRES = ("a planted case where two judges of the same lineage agree wrongly "
            "does not clear a two-family quorum")
PLANTED_LIE = "lineage ignored"


def requires():
    raise NotImplementedError(
        "F-FAMILY must assert that a planted case chosen so that two judges "
        "sharing a lineage make the same wrong call does not satisfy the "
        "two-family quorum, because the quorum counts distinct lineages and not "
        "distinct processes.")


def planted_lie():
    raise NotImplementedError(
        "F-FAMILY's planted lie must run a quorum check that ignores lineage and "
        "counts judges, and assert that requires() raises AssertionError naming "
        "the planted case and the lineage both judges shared.")
