"""F-CAP -- BLUEPRINT_v0.2.md section 21; law 7; gate M5 (section 22).

requires    : an effect above the per-act, per-day or per-party cap never leaves;
              with the hand's own credential, raising the cap fails at the
              provider; a first-time payee always asks
planted lie : a full-permission key

Contract, identical for all forty-seven falsifiers:

  requires()    runs the property against the system under test. Returns None
                when the property holds; raises AssertionError carrying the
                counterexample when it does not.
  planted_lie() builds the sabotaged system this falsifier is aimed at, runs
                requires() against it, and asserts that requires() FAILED. A
                falsifier whose planted lie passes is measuring nothing, and
                that is the failure this function must report.
"""

ID = "F-CAP"
MILESTONE = "M5"
REQUIRES = ("an effect above the per-act, per-day or per-party cap never leaves; "
            "with the hand's own credential, raising the cap fails at the "
            "provider; a first-time payee always asks")
PLANTED_LIE = "a full-permission key"


def requires():
    raise NotImplementedError(
        "F-CAP must assert that an effect exceeding any of the three caps -- per "
        "act, per day, per party, each compared in the record's own `unit` -- "
        "never reaches the provider, that an attempt to raise a cap using the "
        "hand's own restricted credential is refused by the provider and not "
        "merely by FACTOR, and that a payee with no prior receipt always produces "
        "an ask.")


def planted_lie():
    raise NotImplementedError(
        "F-CAP's planted lie must give the hand a full-permission provider key "
        "and assert that requires() raises AssertionError naming the cap raise "
        "that the provider accepted.")
