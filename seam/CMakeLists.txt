# The seam is its own static library with its own hash, and it links nothing
# learned. At M1 F-VETO makes that a link-time fact rather than a convention:
# a build in which seam/ includes any model header must fail to link.
#
# Its only dependency is the vendored hash, which is arithmetic.

add_library(seam STATIC
  seam.cpp
  seam.h
)

target_include_directories(seam PUBLIC "${CMAKE_CURRENT_SOURCE_DIR}")
target_link_libraries(seam PRIVATE factor_warnings blake2b)
