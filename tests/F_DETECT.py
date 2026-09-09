"""F-DETECT -- BLUEPRINT_v0.2.md section 21; law 6; gate M4 (section 22).

requires    : a class good for 500 grades then degraded for 40 is demoted; a
              fixed-start process on the same tape is not
planted lie : demotion by a fixed-start process

Contract, identical for all forty-seven falsifiers:

  requires()    runs the property against the system under test. Returns None
                when the property holds; raises AssertionError carrying the
                counterexample when it does not.
  planted_lie() builds the sabotaged system this falsifier is aimed at, runs
                requires() against it, and asserts that requires() FAILED. A
                falsifier whose planted lie passes is measuring nothing, and
                that is the failure this function must report.
"""

ID = "F-DETECT"
MILESTONE = "M4"
REQUIRES = ("a class good for 500 grades then degraded for 40 is demoted; a "
            "fixed-start process on the same tape is not")
PLANTED_LIE = "demotion by a fixed-start process"


def requires():
    raise NotImplementedError(
        "F-DETECT must assert, on a synthetic tape of 500 good grades followed by "
        "40 degraded ones, that the changepoint process demotes the class, and "
        "that a fixed-start e-process reading the same tape does not -- the two "
        "results together are what shows the detector is the thing detecting.")


def planted_lie():
    raise NotImplementedError(
        "F-DETECT's planted lie must drive the demotion from the fixed-start "
        "process instead of the changepoint process and assert that requires() "
        "raises AssertionError naming the grade index at which the wrong process "
        "fired.")
