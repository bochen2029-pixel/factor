"""F-CHAIN -- BLUEPRINT_v0.2.md section 21; law 3; gate M0 (section 22).

requires    : one flipped byte in a segment fails `verify`; a row rewritten with
              its hash recomputed fails the link check
planted lie : a row-local verifier

Contract, identical for all forty-seven falsifiers:

  requires()    runs the property against the system under test. Returns None
                when the property holds; raises AssertionError carrying the
                counterexample when it does not.
  planted_lie() builds the sabotaged system this falsifier is aimed at, runs
                requires() against it, and asserts that requires() FAILED. A
                falsifier whose planted lie passes is measuring nothing, and
                that is the failure this function must report.

The same two properties are exercised against generated files, with no kernel,
by `chain_check.py` in this directory. This stub is what wires them to the built
`factor verify`.
"""

ID = "F-CHAIN"
MILESTONE = "M0"
REQUIRES = ("one flipped byte in a segment fails `verify`; a row rewritten with "
            "its hash recomputed fails the link check")
PLANTED_LIE = "a row-local verifier"


def requires():
    raise NotImplementedError(
        "F-CHAIN must assert that `factor verify` reports an error for a tape "
        "with one flipped byte in a mid-chain segment, and reports an error for a "
        "tape whose mid-chain row was rewritten with its own h recomputed, which "
        "only the prev == previous h link check can catch.")


def planted_lie():
    raise NotImplementedError(
        "F-CHAIN's planted lie must run a verifier that checks only "
        "h == H(prev || len || body) and omits the link check, and assert that "
        "requires() raises AssertionError naming the rewritten row that the "
        "row-local verifier accepted.")
