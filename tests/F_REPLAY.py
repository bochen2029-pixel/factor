"""F-REPLAY -- BLUEPRINT_v0.2.md section 21; law 8; gate M0 (section 22).

requires    : a full replay of the spools reproduces the ledger digest
              bit-identically without re-running the model
planted lie : a float accumulator; a re-run extractor

Contract, identical for all forty-seven falsifiers:

  requires()    runs the property against the system under test. Returns None
                when the property holds; raises AssertionError carrying the
                counterexample when it does not.
  planted_lie() builds the sabotaged system this falsifier is aimed at, runs
                requires() against it, and asserts that requires() FAILED. A
                falsifier whose planted lie passes is measuring nothing, and
                that is the failure this function must report.
"""

ID = "F-REPLAY"
MILESTONE = "M0"
REQUIRES = ("a full replay of the spools reproduces the ledger digest "
            "bit-identically without re-running the model")
PLANTED_LIE = "a float accumulator; a re-run extractor"


def requires():
    raise NotImplementedError(
        "F-REPLAY must assert that the chain hash of every 128-byte record taken "
        "in ascending id order after a full replay from the spools equals the "
        "digest of the original run, byte for byte, with the model never invoked "
        "during the replay.")


def planted_lie():
    raise NotImplementedError(
        "F-REPLAY's planted lie must run a replay that accumulates amounts in a "
        "float and re-runs the extractor over the source text, and assert that "
        "requires() raises AssertionError naming the first record id whose bytes "
        "differ and the byte offset within the record.")
