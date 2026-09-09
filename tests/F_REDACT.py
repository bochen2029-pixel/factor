"""F-REDACT -- BLUEPRINT_v0.2.md section 21; law 10; gate M6 (section 22).

requires    : a brief is assembled by code from declared fields through the
              redactor; its bytes are on the tape
planted lie : a brief assembled by the model

Contract, identical for all forty-seven falsifiers:

  requires()    runs the property against the system under test. Returns None
                when the property holds; raises AssertionError carrying the
                counterexample when it does not.
  planted_lie() builds the sabotaged system this falsifier is aimed at, runs
                requires() against it, and asserts that requires() FAILED. A
                falsifier whose planted lie passes is measuring nothing, and
                that is the failure this function must report.
"""

ID = "F-REDACT"
MILESTONE = "M6"
REQUIRES = ("a brief is assembled by code from declared fields through the "
            "redactor; its bytes are on the tape")
PLANTED_LIE = "a brief assembled by the model"


def requires():
    raise NotImplementedError(
        "F-REDACT must assert that every brief was produced by the assembler from "
        "the class's declared field list, passed through the redactor, and that "
        "the brief's exact bytes as sent appear on the tape, so what left can be "
        "compared with what was authorised.")


def planted_lie():
    raise NotImplementedError(
        "F-REDACT's planted lie must have the model write the brief prose and "
        "assert that requires() raises AssertionError naming the brief whose bytes "
        "contain a field the class never declared.")
