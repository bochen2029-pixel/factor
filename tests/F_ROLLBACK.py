"""F-ROLLBACK -- BLUEPRINT_v0.2.md section 21; law 8; gate M7 (section 22).

requires    : folds re-derived to an earlier head match the folds stamped at
              that head; the rollback row is honoured as a fold instruction
planted lie : a fold that reads past its head; a fold that re-applies a shadowed
              row

Contract, identical for all forty-seven falsifiers:

  requires()    runs the property against the system under test. Returns None
                when the property holds; raises AssertionError carrying the
                counterexample when it does not.
  planted_lie() builds the sabotaged system this falsifier is aimed at, runs
                requires() against it, and asserts that requires() FAILED. A
                falsifier whose planted lie passes is measuring nothing, and
                that is the failure this function must report.
"""

ID = "F-ROLLBACK"
MILESTONE = "M7"
REQUIRES = ("folds re-derived to an earlier head match the folds stamped at that "
            "head; the rollback row is honoured as a fold instruction")
PLANTED_LIE = ("a fold that reads past its head; a fold that re-applies a "
               "shadowed row")


def requires():
    raise NotImplementedError(
        "F-ROLLBACK must assert that every fold re-derived by walking the tape to "
        "an earlier head is byte-identical to the fold stamped at that head, and "
        "that a `rollback` row is treated as an instruction the subsequent fold "
        "obeys rather than as an ordinary row it merely records.")


def planted_lie():
    raise NotImplementedError(
        "F-ROLLBACK's planted lie must run a fold that reads rows past its own "
        "head and re-applies a row the rollback shadowed, and assert that "
        "requires() raises AssertionError naming the fold, the head it was cut "
        "to, and the first field that differs.")
