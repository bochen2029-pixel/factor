"""F-BLIND -- BLUEPRINT_v0.2.md section 21; law 11; gate M1 (section 22).

requires    : with the counterparty's frames removed, the check and guard
              margins never fall below the full read's
planted lie : use the full read alone

Contract, identical for all forty-seven falsifiers:

  requires()    runs the property against the system under test. Returns None
                when the property holds; raises AssertionError carrying the
                counterexample when it does not.
  planted_lie() builds the sabotaged system this falsifier is aimed at, runs
                requires() against it, and asserts that requires() FAILED. A
                falsifier whose planted lie passes is measuring nothing, and
                that is the failure this function must report.
"""

ID = "F-BLIND"
MILESTONE = "M1"
REQUIRES = ("with the counterparty's frames removed, the check and guard margins "
            "never fall below the full read's")
PLANTED_LIE = "use the full read alone"


def requires():
    raise NotImplementedError(
        "F-BLIND must assert that for every obligation, the m_check and m_guard "
        "computed from a trunk with the counterparty's frames withheld are "
        "greater than or equal to the ones computed from the full read, so that "
        "missing evidence can only make the kernel more cautious, never less.")


def planted_lie():
    raise NotImplementedError(
        "F-BLIND's planted lie must run only the full read and report its margins "
        "as if they were the withheld-read margins, and assert that requires() "
        "raises AssertionError naming the obligation whose blinded margin was "
        "never actually computed.")
