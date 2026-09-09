"""F-LAYOUT -- BLUEPRINT_v0.2.md section 21; law section 5; gate M0 (section 22).

requires    : `sizeof(Obligation) == 128`, every offset as pinned, no implicit
              padding
planted lie : the v0.1 claim asserted

Contract, identical for all forty-seven falsifiers:

  requires()    runs the property against the system under test. Returns None
                when the property holds; raises AssertionError carrying the
                counterexample when it does not.
  planted_lie() builds the sabotaged system this falsifier is aimed at, runs
                requires() against it, and asserts that requires() FAILED. A
                falsifier whose planted lie passes is measuring nothing, and
                that is the failure this function must report.

Both properties already run in this directory against a model of the record
rather than against the built kernel: `check_layout.py` (ctypes) and
`layout_check.cpp` (compile-time static_asserts, whose -DPROVE_SPEC_FAILS build
is this falsifier's planted lie and must fail to compile). This stub is what
wires them to the kernel binary and to the ledger header it writes.
"""

ID = "F-LAYOUT"
MILESTONE = "M0"
REQUIRES = ("`sizeof(Obligation) == 128`, every offset as pinned, no implicit "
            "padding")
PLANTED_LIE = "the v0.1 claim asserted"


def requires():
    raise NotImplementedError(
        "F-LAYOUT must assert against the built kernel that its record is 128 "
        "bytes with alignof 8, that every field sits at the offset section 5 "
        "pins, that the sum of the declared field sizes equals 128 so no implicit "
        "padding exists anywhere, and that the ledger header it writes states the "
        "same size, byte order and enum numbering.")


def planted_lie():
    raise NotImplementedError(
        "F-LAYOUT's planted lie must assert the v0.1 record layout -- float "
        "margins, no release_ns, seq, n_wit, n_wait, tie or unit, and _pad[14] -- "
        "against the kernel, and assert that requires() raises AssertionError; the "
        "compile-time form of the same lie is layout_check.cpp built with "
        "-DPROVE_SPEC_FAILS, which must not compile.")
