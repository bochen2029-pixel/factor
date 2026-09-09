"""F-PIN -- BLUEPRINT_v0.2.md section 21; law 14; gate M0 (section 22).

requires    : a drifted serve byte, weight, quantization, schema map, runtime
              version, context parameter or environment variable refuses to boot
planted lie : a supplied identity trusted unchecked

Contract, identical for all forty-seven falsifiers:

  requires()    runs the property against the system under test. Returns None
                when the property holds; raises AssertionError carrying the
                counterexample when it does not.
  planted_lie() builds the sabotaged system this falsifier is aimed at, runs
                requires() against it, and asserts that requires() FAILED. A
                falsifier whose planted lie passes is measuring nothing, and
                that is the failure this function must report.
"""

ID = "F-PIN"
MILESTONE = "M0"
REQUIRES = ("a drifted serve byte, weight, quantization, schema map, runtime "
            "version, context parameter or environment variable refuses to boot")
PLANTED_LIE = "a supplied identity trusted unchecked"


def requires():
    raise NotImplementedError(
        "F-PIN must assert that perturbing each of the seven pinned things in "
        "turn -- serve bytes, weights, quantization, schema map, runtime version, "
        "context parameters, environment -- makes the kernel refuse to boot with a "
        "row naming which pin drifted, and that an unperturbed build boots.")


def planted_lie():
    raise NotImplementedError(
        "F-PIN's planted lie must accept the identity each component reports about "
        "itself instead of measuring it, and assert that requires() raises "
        "AssertionError naming the pin that drifted while the kernel booted "
        "anyway.")
