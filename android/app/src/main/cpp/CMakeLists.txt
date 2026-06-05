cmake_minimum_required(VERSION 3.22.1)
project("supercalc")

# calc_core.c is located at the repository root
# From android/app/src/main/cpp/ -> ../../../../../calc_core.c
get_filename_component(CALC_CORE_SOURCE "${CMAKE_CURRENT_SOURCE_DIR}/../../../../../calc_core.c" ABSOLUTE)

add_library(calc_core SHARED
    ${CALC_CORE_SOURCE}
    calc_core_jni.c
)

target_compile_options(calc_core PRIVATE
    -Wall -Wextra -O2 -Wno-unused-parameter
)

target_link_libraries(calc_core
    m
)
