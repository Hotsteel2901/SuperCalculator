cmake_minimum_required(VERSION 3.22.1)
project("supercalc")

add_library(calc_core SHARED
    calc_core.c
    calc_core_jni.c
)

target_link_libraries(calc_core
    m
    log
)
