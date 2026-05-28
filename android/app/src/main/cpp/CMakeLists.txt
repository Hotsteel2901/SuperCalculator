cmake_minimum_required(VERSION 3.22.1)
project("supercalc")

add_library(calc_core SHARED
    ../../../../../calc_core.c
    calc_core_jni.c
)

target_compile_options(calc_core PRIVATE
    -Wall -Wextra -O2 -Wno-unused-parameter
)

target_link_libraries(calc_core
    m
)
