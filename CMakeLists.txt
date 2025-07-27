cmake_minimum_required(VERSION 3.14)
project(smufl_mapping LANGUAGES CXX)

# C++ settings
if(NOT CMAKE_CXX_STANDARD)
    set(CMAKE_CXX_STANDARD 23)
endif()

# Enforce at least C++17, allow higher if set by the parent
if(CMAKE_CXX_STANDARD LESS 17)
    message(FATAL_ERROR "Smufl_mapping requires at least C++17. Current: C++${CMAKE_CXX_STANDARD}")
endif()

set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

message(STATUS "Smufl_mapping C++ standard: ${CMAKE_CXX_STANDARD}")

find_package(Python3 REQUIRED COMPONENTS Interpreter)

# Generate auto headers
include(cmake/GenerateSmuflMaps.cmake)
generate_smuflmap_headers()
add_custom_target(generate_smuflmaps DEPENDS ${SMUFL_MAPPING_GENERATED_HEADERS})

# Library target
add_library(smufl_mapping STATIC
    src/smufl_mapping.cpp
    src/smufl_mapping.h
    ${SMUFL_MAPPING_GENERATED_HEADERS}
)

add_dependencies(smufl_mapping
    generate_smuflmaps
)

# Public headers are in src/
target_include_directories(smufl_mapping
    PUBLIC
        $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/src>
        $<INSTALL_INTERFACE:include>
)

# Compiler warnings (optional)
target_compile_features(smufl_mapping PUBLIC cxx_std_17)
target_compile_options(smufl_mapping PRIVATE
    $<$<CXX_COMPILER_ID:GNU,Clang>:-Wall -Wextra -pedantic>
    $<$<CXX_COMPILER_ID:MSVC>:/W4>
)

# === Testing ===
option(smufl_mapping_BUILD_TESTING "Build smufl_mapping unit tests" ON)

include(CTest)  # sets BUILD_TESTING

if(smufl_mapping_BUILD_TESTING)
    add_subdirectory(tests)
endif()
