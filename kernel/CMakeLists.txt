# The kernel. One static binary per process; every verb is a subcommand of it so
# the pins are asserted once, in one place, before anything else runs
# (KICKOFF_M0.md section 6).
#
# The kernel links no network module. `ws2_32`, `mswsock`, `winhttp`, `wininet`,
# `urlmon` and `dnsapi` are absent by construction and build.cmd's module gate
# checks it with dumpbin /dependents. The gate is a lint; the fence is the
# sandbox, measured in receipts/M0_SANDBOX_PROBE_2026-09-08.md.

add_executable(factor
  main.cpp
  cjson.cpp
  cjson.h
)

target_link_libraries(factor PRIVATE factor_warnings blake2b seam)

target_compile_definitions(factor PRIVATE
  FACTOR_BUILD_ID="${FACTOR_BUILD_ID}"
  WIN32_LEAN_AND_MEAN
  NOMINMAX
)
