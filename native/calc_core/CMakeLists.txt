cmake_minimum_required(VERSION 3.22)
project(supercalc_core LANGUAGES C)

set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

get_filename_component(LEGACY_CORE_SOURCE
    "${CMAKE_CURRENT_SOURCE_DIR}/../../calc_core.c"
    ABSOLUTE)

add_library(supercalc_core SHARED
    "${LEGACY_CORE_SOURCE}"
    src/supercalc_core.c
)

target_compile_definitions(supercalc_core PRIVATE SUPERCALC_CORE_BUILD)
target_include_directories(supercalc_core PUBLIC include)
if(MSVC)
  target_compile_options(supercalc_core PRIVATE /W4 /O2)
else()
  target_compile_options(supercalc_core PRIVATE -Wall -Wextra -Wpedantic -O2)
endif()

if(NOT WIN32)
  target_link_libraries(supercalc_core PRIVATE m)
endif()

set_target_properties(supercalc_core PROPERTIES
    OUTPUT_NAME "supercalc_core"
)

enable_testing()
add_executable(supercalc_core_smoke tests/smoke_test.c)
target_include_directories(supercalc_core_smoke PRIVATE include)
target_link_libraries(supercalc_core_smoke PRIVATE supercalc_core)
add_test(NAME supercalc_core_smoke COMMAND supercalc_core_smoke)
