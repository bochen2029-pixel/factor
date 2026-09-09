"""F-DETERMINISM -- BLUEPRINT_v0.2.md section 21; laws 3, 19; gate M0 (section 22).

requires    : two runs, two insertion orders, byte-identical plan hashes
planted lie : walk in hash-map order

Contract, identical for all forty-seven falsifiers:

  requires()    runs the property against the system under test. Returns None
                when the property holds; raises AssertionError carrying the
                counterexample when it does not.
  planted_lie() builds the sabotaged system this falsifier is aimed at, runs
                requires() against it, and asserts that requires() FAILED. A
                falsifier whose planted lie passes is measuring nothing, and
                that is the failure this function must report.
"""

ID = "F-DETERMINISM"
MILESTONE = "M0"
REQUIRES = "two runs, two insertion orders, byte-identical plan hashes"
PLANTED_LIE = "walk in hash-map order"


def requires():
    raise NotImplementedError(
        "F-DETERMINISM must assert that two runs over the same spools and writ, "
        "differing only in the order the obligations were inserted, produce "
        "byte-identical plan hashes as section 12 defines them -- over (id, "
        "judged_rev, verb, reason, flags, band, rung, the quantized margins, "
        "batch id, position) and excluding ms, prev and h.")


def planted_lie():
    raise NotImplementedError(
        "F-DETERMINISM's planted lie must run a walk that iterates the ripeness "
        "index in hash-map order rather than in (cls, due_ns) order, and assert "
        "that requires() raises AssertionError naming the two differing plan "
        "hashes and the first verb row at which they diverge.")
