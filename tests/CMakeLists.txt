cmake_minimum_required(VERSION 3.14)

include(FetchContent)

FetchContent_Declare(
	googletest
    URL https://github.com/google/googletest/releases/download/v1.15.2/googletest-1.15.2.tar.gz
	DOWNLOAD_EXTRACT_TIMESTAMP TRUE
)
# For Windows: Prevent overriding the parent project's compiler/linker settings
set(gtest_force_shared_crt ON CACHE BOOL "" FORCE)
FetchContent_MakeAvailable(googletest)

enable_testing()

add_executable(smufl_mapping_tests
    legacy_mapping_tests.cpp
    smufl_mapping_tests.cpp
)

set(CMAKE_WARN_DEPRECATED ON CACHE BOOL "Suppress deprecation warnings for external projects" FORCE)
if (CMAKE_CXX_COMPILER_ID MATCHES "AppleClang|Clang|GNU")
    # Extra warnings for Clang/AppleClang
    target_compile_options(smufl_mapping_tests PRIVATE -Wall -Wextra -Werror -Wpedantic)
elseif (CMAKE_CXX_COMPILER_ID MATCHES "MSVC")
    # Extra warnings for MSVC
    target_compile_options(smufl_mapping_tests PRIVATE /Zc:__cplusplus /W4 /WX)
endif()

target_link_libraries(smufl_mapping_tests PRIVATE
    smufl_mapping
    gtest_main
)

target_include_directories(smufl_mapping_tests
    PRIVATE
        ${CMAKE_CURRENT_SOURCE_DIR}/../src
)

include(GoogleTest)
gtest_discover_tests(smufl_mapping_tests)
