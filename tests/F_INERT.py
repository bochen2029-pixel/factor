"""F-INERT -- BLUEPRINT_v0.2.md section 21; law section 10; gate M1 (section 22).

requires    : with the switch `off`, every venue a producer is mounted in is
              byte-identical to FACTOR absent; with `shadow`, the hand receives
              no effect, canary included
planted lie : an effect under `shadow`

Contract, identical for all forty-seven falsifiers:

  requires()    runs the property against the system under test. Returns None
                when the property holds; raises AssertionError carrying the
                counterexample when it does not.
  planted_lie() builds the sabotaged system this falsifier is aimed at, runs
                requires() against it, and asserts that requires() FAILED. A
                falsifier whose planted lie passes is measuring nothing, and
                that is the failure this function must report.
"""

ID = "F-INERT"
MILESTONE = "M1"
REQUIRES = ("with the switch `off`, every venue a producer is mounted in is "
            "byte-identical to FACTOR absent; with `shadow`, the hand receives "
            "no effect, canary included")
PLANTED_LIE = "an effect under `shadow`"


def requires():
    raise NotImplementedError(
        "F-INERT must assert that a diff of every venue a producer is mounted in, "
        "taken with the switch `off` against a control run with FACTOR not "
        "installed, is empty byte for byte, and that under `shadow` the hand's "
        "pipe carries zero effect messages including canary draws.")


def planted_lie():
    raise NotImplementedError(
        "F-INERT's planted lie must run the kernel under `shadow` with one effect "
        "allowed through to the hand and assert that requires() raises "
        "AssertionError naming that effect and the venue byte it changed.")
