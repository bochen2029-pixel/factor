"""F-STANDING -- BLUEPRINT_v0.2.md section 21; law 11; gate M2 (section 22).

requires    : an obligation witnessed only by a party without standing never
              reaches DO at any rung
planted lie : standing inferred from politeness

Contract, identical for all forty-seven falsifiers:

  requires()    runs the property against the system under test. Returns None
                when the property holds; raises AssertionError carrying the
                counterexample when it does not.
  planted_lie() builds the sabotaged system this falsifier is aimed at, runs
                requires() against it, and asserts that requires() FAILED. A
                falsifier whose planted lie passes is measuring nothing, and
                that is the failure this function must report.
"""

ID = "F-STANDING"
MILESTONE = "M2"
REQUIRES = ("an obligation witnessed only by a party without standing never "
            "reaches DO at any rung")
PLANTED_LIE = "standing inferred from politeness"


def requires():
    raise NotImplementedError(
        "F-STANDING must assert that an obligation whose only witnesses are "
        "parties without standing carries UNTRUSTED_ORIGIN and produces no DO "
        "verb row at any rung from 0 to the ceiling.")


def planted_lie():
    raise NotImplementedError(
        "F-STANDING's planted lie must run an extractor that grants standing on "
        "the tone of the message rather than on the provenance root, and assert "
        "that requires() raises AssertionError naming the obligation that reached "
        "DO on a witness with no standing.")
