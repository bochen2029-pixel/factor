r"""F-EGRESS -- BLUEPRINT_v0.2.md section 21; laws 5, 10; gate M0, M3 full
(section 22). Read with Amendment 2 (2026-09-08), "The sandbox law, measured".

requires    : a probe compiled into the kernel opens a socket by three routes,
              the socket library, a raw device control, and a loopback connect,
              and all three are refused by the OS; the hand's egress ledger
              equals the sum of its rows; no process in the kernel's tree holds a
              socket at any sample
planted lie : a module-list check standing in for the OS refusal; an organ child
              that opens a socket

The mechanism in force, measured (receipts/M0_SANDBOX_PROBE_2026-09-08.md):
`os-enforced`. The launcher creates a zero-capability AppContainer profile,
derives its package SID, and re-executes the kernel into it under
PROCESS_CREATION_CHILD_PROCESS_RESTRICTED; Windows Filtering Platform then
refuses the container's sockets at the ALE layers, keyed on the package SID,
with no administrator and no installer. The control outside the container
connects on both socket routes and opens both device objects. The three routes,
as the probe met them inside:

  the socket library    a ws2_32 connect to an outbound host is refused with
                        WSAEACCES (10013). Socket CREATION succeeds inside;
                        the connect is what is refused, so the refusal is read
                        at the connect and nowhere earlier.
  a loopback connect    a connect to a LIVE listener on 127.0.0.1 dies with
                        WSAETIMEDOUT (10060) -- a timeout, not a fast refusal,
                        because WFP defers the same-package decision to the
                        receive layer. An unoccupied port RSTs with
                        WSAECONNREFUSED (10061) inside and outside alike and
                        proves nothing; the live listener is the test.
  a raw device control  the AFD_CONNECT IOCTL, driven over a handle from
                        NtCreateFile on \Device\Afd\Endpoint. This route is
                        the residual. The probe measured the OPEN only:
                        \Device\Afd\Endpoint opens inside the container
                        (STATUS_SUCCESS) while the raw \Device\Afd open is
                        denied (STATUS_ACCESS_DENIED, 0xC0000022). Opening the
                        endpoint is not egress. The connect IOCTL over that
                        handle transits the same package-keyed ALE_AUTH_CONNECT
                        layer that refused the socket library, so its refusal
                        is established by INFERENCE, and the M0 receipt reads
                        `afd: inferred` until this falsifier drives the IOCTL
                        itself and observes the refusal. The status the filter
                        returns to the IOCTL is not pinned here, because it has
                        not been observed; observing it is this falsifier's
                        job.

The raw device route is what the planted lie is for. A module-list check, the
lint section 11 retains, sees no ws2_32 loaded and calls the kernel confined; a
raw AFD handle needs no ws2_32 at all. Only the OS error, read at the connect
on each of the three routes, settles it.

Section 22's M0 deliverables include "the sandbox mechanism on the header row",
the word section 11 has the header row print: `os-enforced`, `wfp-installed`
or `lint-only`. Section 21's row does not name the header row; the header-row
clause in requires() below is this file's reading of section 22, not the
table's text, and it is the shape of the lie: `lint-only` standing in for
`os-enforced`.

Contract, identical for all forty-seven falsifiers:

  requires()    runs the property against the system under test. Returns None
                when the property holds; raises AssertionError carrying the
                counterexample when it does not.
  planted_lie() builds the sabotaged system this falsifier is aimed at, runs
                requires() against it, and asserts that requires() FAILED. A
                falsifier whose planted lie passes is measuring nothing, and
                that is the failure this function must report.
"""

ID = "F-EGRESS"
MILESTONE = "M0"
REQUIRES = ("a probe compiled into the kernel opens a socket by three routes, "
            "the socket library, a raw device control, and a loopback connect, "
            "and all three are refused by the OS; the hand's egress ledger "
            "equals the sum of its rows; no process in the kernel's tree holds a "
            "socket at any sample")
PLANTED_LIE = ("a module-list check standing in for the OS refusal; an organ "
               "child that opens a socket")


def requires():
    raise NotImplementedError(
        "F-EGRESS must assert that a probe compiled into the kernel, running "
        "inside the zero-capability AppContainer the launcher applies under "
        "PROCESS_CREATION_CHILD_PROCESS_RESTRICTED, is refused by the OS on all "
        "three routes Amendment 2 measured, each refusal read from the OS error "
        "at the connect and not from a policy table or a module list: the "
        "socket library, a ws2_32 connect to an outbound host refused with "
        "WSAEACCES (10013); a loopback connect to a LIVE listener on 127.0.0.1 "
        "refused with WSAETIMEDOUT (10060), a timeout and not a fast failure, "
        "an unoccupied port proving nothing; and the raw device control, the "
        "AFD_CONNECT IOCTL that this falsifier must ITSELF drive over a handle "
        "from NtCreateFile on \\Device\\Afd\\Endpoint (the endpoint opens inside "
        "the container; the raw \\Device\\Afd open is denied with 0xC0000022; "
        "neither open is egress) and whose refusal it must OBSERVE as the "
        "status the filter returns to the IOCTL, never infer from the open -- "
        "the M0 receipt reads `afd: inferred` until this falsifier has done so; "
        "that the header row's mechanism word is the mechanism whose refusals "
        "the probe observed, `os-enforced` on the machine Amendment 2 measured, "
        "and never `os-enforced` on the strength of the module gate alone; "
        "that the hand's egress byte counter equals the sum of its egress rows; "
        "and that a handle sample over the kernel's whole process tree finds no "
        "socket at any point in the run.")


def planted_lie():
    raise NotImplementedError(
        "F-EGRESS's planted lie must substitute a check of the loaded module "
        "list for the OS refusal -- a launcher that finds no ws2_32 in the "
        "kernel, attempts none of the three routes, and prints `os-enforced` on "
        "the header row on that finding alone -- and, in its second shape, must "
        "infer the raw device route instead of driving it: take the successful "
        "\\Device\\Afd\\Endpoint open, or the raw \\Device\\Afd denial "
        "(0xC0000022), as the refusal without ever driving the AFD_CONNECT "
        "IOCTL, which is exactly the inference the M0 receipt marks `afd: "
        "inferred`; and must let an organ child open a socket; and assert that "
        "requires() raises AssertionError naming each route that was never "
        "actually attempted -- the socket library (WSAEACCES 10013), the live "
        "loopback connect (WSAETIMEDOUT 10060), the AFD_CONNECT IOCTL -- and "
        "the child pid holding the socket.")
