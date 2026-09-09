"""F-EXTRACT -- BLUEPRINT_v0.2.md section 21; law 2; gate M2 (section 22).

requires    : planted promises recovered at the tolerance; retractions close; a
              forwarded quote is one witness
planted lie : offsets emitted by the model; a quote counted twice

Amendment 3 item 1, as Amendment 4 item 7 leaves it: extraction is where an
amount text becomes the micro-unit integer, and that integer is no longer inside
a derived obligation's id -- the id is BLAKE2b-64 over party, kind, due and the
normalized statement, and the amount is an attribute. So this falsifier's amount
fixtures, `check_layout.py`'s `AMOUNT_FIXTURES`, pin the record's DIGEST, the
hand's cap comparison and replay rather than the id -- parsed as decimal text by
digit arithmetic, with a parser that goes through a double as the lie.

Contract, identical for all forty-seven falsifiers:

  requires()    runs the property against the system under test. Returns None
                when the property holds; raises AssertionError carrying the
                counterexample when it does not.
  planted_lie() builds the sabotaged system this falsifier is aimed at, runs
                requires() against it, and asserts that requires() FAILED. A
                falsifier whose planted lie passes is measuring nothing, and
                that is the failure this function must report.
"""

ID = "F-EXTRACT"
MILESTONE = "M2"
REQUIRES = ("planted promises recovered at the tolerance; retractions close; a "
            "forwarded quote is one witness")
PLANTED_LIE = "offsets emitted by the model; a quote counted twice"


def requires():
    raise NotImplementedError(
        "F-EXTRACT must assert three things over a planted corpus: recall of the "
        "planted promises meets the declared tolerance, every planted retraction "
        "closes its obligation rather than opening a second one, and a promise "
        "quoted in a forward increments n_wit by one and not by two.")


def planted_lie():
    raise NotImplementedError(
        "F-EXTRACT's planted lie must run an extractor whose span offsets are "
        "emitted by the model instead of located in the source bytes, and which "
        "counts the forwarded copy of a quote as a second witness, and assert "
        "that requires() raises AssertionError naming the mislocated span and "
        "the obligation whose n_wit is 2.")
