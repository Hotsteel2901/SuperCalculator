cmake_minimum_required(VERSION 3.22.1)
project("supercalc")

# calc_core.c lives at the project root; reference it via relative path
# so local builds work without needing to copy the file first.
add_library(calc_core SHARED
    ../../../../../calc_core.c
    calc_core_jni.c
)

target_link_libraries(calc_core
    m
    log
)
