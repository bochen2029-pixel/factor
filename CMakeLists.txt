# FACTOR -- the build.
#
# KICKOFF_M0.md Amendment 1 is the law here: CMake with Ninja from the VS 2022
# developer environment, CMakePresets.json, a static MSVC runtime,
# /W4 /WX /permissive- /EHsc /utf-8 on FACTOR's own code with third-party
# headers external at warning zero, CTest with the falsifiers registered,
# output under build/bin, CUDA conditional through check_language so a machine
# without a toolkit builds the model-free kernel cleanly, architectures 89, 90
# and 120 when it is enabled.
#
# One static binary per process. No package manager. No framework. No runtime
# dependency. Vendored and pinned only.

cmake_minimum_required(VERSION 3.28)

project(FACTOR
        VERSION 0.2.0
        DESCRIPTION "FACTOR - a resident deputy for one seat"
        LANGUAGES C CXX)

# --------------------------------------------------------------------------
# CUDA, conditionally. M0 is model-free and compiles no CUDA; the plumbing is
# here so that M1's llama.cpp link does not migrate the build.
# --------------------------------------------------------------------------
include(CheckLanguage)
check_language(CUDA)
if(CMAKE_CUDA_COMPILER)
  enable_language(CUDA)
  set(CMAKE_CUDA_ARCHITECTURES 89 90 120)
  set(FACTOR_HAVE_CUDA ON)
  message(STATUS "FACTOR: CUDA found, architectures 89 90 120")
else()
  set(FACTOR_HAVE_CUDA OFF)
  message(STATUS "FACTOR: no CUDA toolkit; the model-free kernel builds without it")
endif()

# --------------------------------------------------------------------------
# Languages and the runtime.
# --------------------------------------------------------------------------
set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Static CRT: one binary per process, nothing to ship beside it.
set(CMAKE_MSVC_RUNTIME_LIBRARY "MultiThreaded$<$<CONFIG:Debug>:Debug>")

# Deterministic output location. The gate reads build/bin.
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/bin")
set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/lib")
foreach(cfg IN ITEMS DEBUG RELEASE RELWITHDEBINFO MINSIZEREL)
  set(CMAKE_RUNTIME_OUTPUT_DIRECTORY_${cfg} "${CMAKE_BINARY_DIR}/bin")
  set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY_${cfg} "${CMAKE_BINARY_DIR}/lib")
endforeach()

# --------------------------------------------------------------------------
# Warnings. FACTOR's own code compiles at /W4 /WX. Nothing here is a warning
# we intend to carry: a warning is a finding.
# --------------------------------------------------------------------------
add_library(factor_warnings INTERFACE)
if(MSVC)
  target_compile_options(factor_warnings INTERFACE
    /W4 /WX /utf-8
    $<$<COMPILE_LANGUAGE:CXX>:/permissive->
    $<$<COMPILE_LANGUAGE:CXX>:/EHsc>
    # Deterministic: no __DATE__/__TIME__ leaking into a binary the pins cover.
    /wd4711            # 'function selected for automatic inline expansion'
  )
  # Third-party headers, when any arrive, are external at warning zero.
  target_compile_options(factor_warnings INTERFACE
    /external:W0 /external:anglebrackets)
else()
  target_compile_options(factor_warnings INTERFACE
    -Wall -Wextra -Wpedantic -Werror -Wconversion -Wshadow)
endif()

# --------------------------------------------------------------------------
# The build id. Every binary answers `--about` and the header row carries this.
# No configure timestamp and no __DATE__ / __TIME__ anywhere: two builds of the
# same source must produce the same header row, or the pin covers a clock.
# --------------------------------------------------------------------------
set(FACTOR_BUILD_ID "${PROJECT_VERSION}+${CMAKE_CXX_COMPILER_ID}${CMAKE_CXX_COMPILER_VERSION}")

# --------------------------------------------------------------------------
# The vendored hash. Defined here, above both subdirectories, because the seam
# and the kernel both link it and neither owns it. It is C, not C++: RFC 7693's
# construction with the full BLAKE2 parameter block for key and person.
# --------------------------------------------------------------------------
add_library(blake2b STATIC
  kernel/blake2b.c
  kernel/blake2b.h
)
target_include_directories(blake2b PUBLIC "${CMAKE_CURRENT_SOURCE_DIR}/kernel")
target_link_libraries(blake2b PRIVATE factor_warnings)

add_subdirectory(seam)
add_subdirectory(kernel)

# --------------------------------------------------------------------------
# CTest. The falsifier runner and the three format models are the tests; the
# runner exits 0 while a falsifier is a stub and 1 on any FAIL, ERROR or
# MISSING, which is exactly the property a build should carry.
# --------------------------------------------------------------------------
enable_testing()

find_package(Python3 COMPONENTS Interpreter)
if(Python3_FOUND)
  add_test(NAME falsifiers_M0
           COMMAND ${Python3_EXECUTABLE}
                   "${CMAKE_SOURCE_DIR}/tests/run_falsifiers.py" --gate M0)
  add_test(NAME falsifiers_all
           COMMAND ${Python3_EXECUTABLE}
                   "${CMAKE_SOURCE_DIR}/tests/run_falsifiers.py")
  add_test(NAME model_layout
           COMMAND ${Python3_EXECUTABLE} "${CMAKE_SOURCE_DIR}/tests/check_layout.py")
  add_test(NAME model_frame
           COMMAND ${Python3_EXECUTABLE} "${CMAKE_SOURCE_DIR}/tests/frame_roundtrip.py")
  add_test(NAME model_chain
           COMMAND ${Python3_EXECUTABLE} "${CMAKE_SOURCE_DIR}/tests/chain_check.py")
  add_test(NAME hash_cross
           COMMAND ${Python3_EXECUTABLE} "${CMAKE_SOURCE_DIR}/tests/hash_cross.py"
                   "$<TARGET_FILE:factor>")
  add_test(NAME cjson_cross
           COMMAND ${Python3_EXECUTABLE} "${CMAKE_SOURCE_DIR}/tests/cjson_cross.py"
                   "$<TARGET_FILE:factor>")
else()
  message(WARNING "FACTOR: no Python3 interpreter found; the falsifiers are not registered")
endif()

add_test(NAME factor_selftest COMMAND factor selftest)
