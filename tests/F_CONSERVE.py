"""F-CONSERVE -- BLUEPRINT_v0.2.md section 21; laws 3, 4; gate M0 without the
heard bucket, M2 full (section 22).

requires    : every frame lands in exactly one of: ingested, replayed,
              truncated-with-count, refused-stale, heard-not-judged,
              forming-skipped, echo-skipped, withheld-by-provider-then-replayed
planted lie : drop one frame silently; count a replayed batch twice

Contract, identical for all forty-seven falsifiers:

  requires()    runs the property against the system under test. Returns None
                when the property holds; raises AssertionError carrying the
                counterexample when it does not.
  planted_lie() builds the sabotaged system this falsifier is aimed at, runs
                requires() against it, and asserts that requires() FAILED. A
                falsifier whose planted lie passes is measuring nothing, and
                that is the failure this function must report.
"""

ID = "F-CONSERVE"
MILESTONE = "M0"
REQUIRES = ("every frame lands in exactly one of: ingested, replayed, "
            "truncated-with-count, refused-stale, heard-not-judged, "
            "forming-skipped, echo-skipped, "
            "withheld-by-provider-then-replayed")
PLANTED_LIE = "drop one frame silently; count a replayed batch twice"


def requires():
    raise NotImplementedError(
        "F-CONSERVE must assert that, for every lane and generation, the number "
        "of frames on the spool equals the sum of that lane's eight tape "
        "dispositions, with no frame counted in two buckets and none in zero.")


def planted_lie():
    raise NotImplementedError(
        "F-CONSERVE's planted lie must run a lane whose reader advances the "
        "cursor past exactly one frame without writing any row for it, and a "
        "replay that emits its batch twice, and assert that requires() raises "
        "AssertionError naming the dropped frame's (lane, generation, offset) "
        "and the double-counted batch.")
