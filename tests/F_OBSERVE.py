"""F-OBSERVE -- BLUEPRINT_v0.2.md section 21; law section 24; gate M9 (section 22).

requires    : a staggered arm measures whether being shadowed changes the
              person's behaviour
planted lie : assume it does not

Contract, identical for all forty-seven falsifiers:

  requires()    runs the property against the system under test. Returns None
                when the property holds; raises AssertionError carrying the
                counterexample when it does not.
  planted_lie() builds the sabotaged system this falsifier is aimed at, runs
                requires() against it, and asserts that requires() FAILED. A
                falsifier whose planted lie passes is measuring nothing, and
                that is the failure this function must report.
"""

ID = "F-OBSERVE"
MILESTONE = "M9"
REQUIRES = ("a staggered arm measures whether being shadowed changes the "
            "person's behaviour")
PLANTED_LIE = "assume it does not"


def requires():
    raise NotImplementedError(
        "F-OBSERVE must assert that a staggered-start arm exists, that its "
        "assignment is drawn from the writ's salt and recorded before the period "
        "it governs, and that the arm reports a measured effect size with its "
        "interval rather than an assumption of no effect.")


def planted_lie():
    raise NotImplementedError(
        "F-OBSERVE's planted lie must skip the arm and assume being shadowed "
        "changes nothing, and assert that requires() raises AssertionError naming "
        "the periods for which no arm assignment was recorded.")
