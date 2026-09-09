"""F-ORGAN-DEGRADE -- BLUEPRINT_v0.2.md Amendment 1 item 24; law S16; gate M8.

requires    : an absent organ degrades with code 6 and the account names it
planted lie : a crash

Added by Amendment 1 item 24, which raises section 21 from forty-five rows to
forty-seven: M8's gate conditions were stated in prose in section 22 and had no
falsifier. This is the first of the two. Section 22's M8 gate reads "an absent
organ degrades with code 6 and the account says which".

The law column is this file's reading, not the amendment's: item 24 gives the
two new rows a requires and a planted lie but no law. Section 16's organ
contract is where exit code 6 -- "degraded, the body names the missing rung" --
is stated, so S16 is recorded here. Section 5's DEGRADED flag (bit 12) is set by
the seam when an organ a judgment depended on answered anything but zero, which
is what makes this checkable from the ledger as well as from the account.

Contract, identical for all forty-seven falsifiers:

  requires()    runs the property against the system under test. Returns None
                when the property holds; raises AssertionError carrying the
                counterexample when it does not.
  planted_lie() builds the sabotaged system this falsifier is aimed at, runs
                requires() against it, and asserts that requires() FAILED. A
                falsifier whose planted lie passes is measuring nothing, and
                that is the failure this function must report.
"""

ID = "F-ORGAN-DEGRADE"
MILESTONE = "M8"
REQUIRES = "an absent organ degrades with code 6 and the account names it"
PLANTED_LIE = "a crash"


def requires():
    raise NotImplementedError(
        "F-ORGAN-DEGRADE must assert that with a named organ removed from its "
        "fixed path, every call to it returns exit code 6 rather than crashing "
        "or hanging, the kernel keeps running and keeps judging, an `organ` row "
        "carries that name, version, pins and the code 6, every obligation whose "
        "evidence rested on that call carries the DEGRADED flag, and the account "
        "prints the organ by name as degraded rather than reporting a healthy "
        "run.")


def planted_lie():
    raise NotImplementedError(
        "F-ORGAN-DEGRADE's planted lie must run a seam that lets an absent "
        "organ take the kernel down -- an unhandled spawn failure, not a code 6 "
        "-- and assert that requires() raises AssertionError naming the organ "
        "whose absence ended the run and the account that was never written.")
