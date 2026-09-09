r"""F-ORGAN-NET -- BLUEPRINT_v0.2.md Amendment 1 item 24; law 5, S16; gate M8.
Read with Amendment 2 (2026-09-08), "The sandbox law, measured".

requires    : an organ child that opens a socket is refused by the sandbox
planted lie : a declaration trusted without confinement

Added by Amendment 1 item 24, the second of the two rows that give M8 a
falsifier. Section 22's M8 gate reads "an organ child that opens a socket is
refused". Section 16: an organ declares `net: none` or `net: via-hand`; the
launcher spawns only `net: none` organs into the kernel's sandbox, and "an organ
that lies about its declaration is caught by the sandbox, not by the
declaration". Law 5 is the constitution's: the process that judges cannot open a
socket, "enforced by the operating system at the boundary of its process tree,
not by a module list", and neither can anything it spawns.

The law column is this file's reading, not the amendment's: item 24 gives the
two new rows a requires and a planted lie but no law.

This overlaps F-EGRESS deliberately and does not replace it. F-EGRESS's second
planted lie is already "an organ child that opens a socket"; F-EGRESS is gated at
M0 and M3, when no organ exists yet, so the organ half of it has no gate until
M8. This row is that gate.

The organ child is inside the same container. The launcher spawns a `net: none`
organ into the kernel's sandbox (section 16), and after Amendment 2 that sandbox
is a measured thing: a zero-capability AppContainer profile, applied by the
launcher under PROCESS_CREATION_CHILD_PROCESS_RESTRICTED, the mechanism
`os-enforced` on the header row (receipts/M0_SANDBOX_PROBE_2026-09-08.md). The
kernel itself cannot spawn the organ; the launch attribute forbids it (section
20: "the kernel cannot spawn a process: the launch attribute"), so the organ is
the launcher's child under the kernel's package SID, and it meets the same
package-keyed filter the kernel meets. Its three routes are therefore
F-EGRESS's three, with the same observations:

  the socket library    a ws2_32 connect to an outbound host, refused with
                        WSAEACCES (10013) at the connect; socket creation
                        succeeds inside and proves nothing
  a loopback connect    to a LIVE listener on 127.0.0.1, refused with
                        WSAETIMEDOUT (10060), a timeout and not a fast failure;
                        an unoccupied port RSTs (10061) inside and outside alike
  a raw device control  the AFD_CONNECT IOCTL driven over a handle from
                        NtCreateFile on \Device\Afd\Endpoint, which opens
                        inside the container while the raw \Device\Afd open is
                        denied (0xC0000022). Neither open is egress. The probe
                        never drove the IOCTL, so this route is inferred until
                        F-EGRESS drives it at M0 and the M0 receipt stops
                        reading `afd: inferred`. The organ probe here drives it
                        again, from the organ, and observes the refusal itself;
                        an M8 run that took F-EGRESS's M0 observation on trust
                        would be measuring the kernel and not the organ.

Contract, identical for all forty-seven falsifiers:

  requires()    runs the property against the system under test. Returns None
                when the property holds; raises AssertionError carrying the
                counterexample when it does not.
  planted_lie() builds the sabotaged system this falsifier is aimed at, runs
                requires() against it, and asserts that requires() FAILED. A
                falsifier whose planted lie passes is measuring nothing, and
                that is the failure this function must report.
"""

ID = "F-ORGAN-NET"
MILESTONE = "M8"
REQUIRES = "an organ child that opens a socket is refused by the sandbox"
PLANTED_LIE = "a declaration trusted without confinement"


def requires():
    raise NotImplementedError(
        "F-ORGAN-NET must assert that an organ declaring `net: none`, spawned "
        "by the launcher into the kernel's sandbox -- the zero-capability "
        "AppContainer Amendment 2 measured, under the kernel's package SID -- is "
        "refused by the OPERATING SYSTEM when it attempts a socket by each of "
        "F-EGRESS's three routes as the amendment measured them: the socket "
        "library, a ws2_32 connect refused with WSAEACCES (10013); a loopback "
        "connect to a LIVE listener on 127.0.0.1, refused with WSAETIMEDOUT "
        "(10060); and the raw device control, the AFD_CONNECT IOCTL that the "
        "organ probe must itself drive over a handle from NtCreateFile on "
        "\\Device\\Afd\\Endpoint and whose refusal it must observe as the status "
        "returned to the IOCTL, never infer from the open (the endpoint opens "
        "inside the container; the raw \\Device\\Afd open is denied with "
        "0xC0000022; neither is egress); that the refusal holds when the "
        "organ's own declaration is a lie, that no process in the kernel's tree "
        "holds a socket at any sample, and that the attempt leaves a row.")


def planted_lie():
    raise NotImplementedError(
        "F-ORGAN-NET's planted lie must run a launcher that reads `net: none` "
        "off the organ's --about output and spawns it OUTSIDE the sandbox on the "
        "strength of that declaration, then run an organ that declares `net: "
        "none` and opens a socket anyway, by any of the three routes -- the "
        "socket library, the live loopback connect, or the AFD_CONNECT IOCTL "
        "over a \\Device\\Afd\\Endpoint handle -- and assert that requires() "
        "raises AssertionError naming the socket the confinement never refused "
        "and the route it left by.")
