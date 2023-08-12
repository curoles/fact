cmake_minimum_required(VERSION 3.22)

# Top level CMake script for building FACT project.
# Author: Igor Lesik 2023

project(SMARTARR
    VERSION 0.1.0
    DESCRIPTION "Knowledge DB"
    LANGUAGES C CXX #ASM
)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

set(C_WARN_FLAGS  "-Wall -Wextra -Werror")
set(C_BUILD_FLAGS  "-fpic -pipe")
set(C_OPT_FLAGS   "-march=native -ftree-vectorize -fprefetch-loop-arrays")

set(CMAKE_CXX_FLAGS "-O3 ${C_WARN_FLAGS} ${C_OPT_FLAGS} ${C_BUILD_FLAGS}")
set(CMAKE_CXX_FLAGS_DEBUG "-O2 -g ${C_WARN_FLAGS} ${C_OPT_FLAGS} ${C_BUILD_FLAGS}")
set(CMAKE_CXX_FLAGS_RELWITHDEBINFO "-O3 -g -flto ${C_WARN_FLAGS} ${C_OPT_FLAGS} ${C_BUILD_FLAGS}")
set(CMAKE_CXX_FLAGS_RELEASE "-O3 -flto -DNDEBUG ${C_WARN_FLAGS} ${C_OPT_FLAGS} ${C_BUILD_FLAGS}")

# Install inside the build directory.
set(CMAKE_INSTALL_PREFIX ${CMAKE_BINARY_DIR}/install)

include_directories(.)
include_directories(${PROJECT_SOURCE_DIR}/third-party)
include(tools/external/rapidyaml.cmake)
include(tools/external/termcolor.cmake)
include(tools/external/cli11.cmake)
include(tools/external/inja.cmake)

set(FILE_FIRST_LINE "# DO NOT EDIT! THIS FILE IS AUTO GENERATED!")
set(FILE_LAST_LINE "# END OF FILE. DO NOT EDIT")
configure_file(fact/facts.yml.in ${PROJECT_SOURCE_DIR}/fact/facts.yml @ONLY)
set(FILE_FIRST_LINE "R\"(")
set(FILE_LAST_LINE ")\"")
configure_file(fact/facts.yml.in ${PROJECT_SOURCE_DIR}/fact/cpp-raw-string-facts.yml @ONLY)
unset(FILE_FIRST_LINE)
unset(FILE_LAST_LINE)

add_subdirectory(tools)