#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BUILD_DIR="${ROOT_DIR}/native/calc_core/build"

if command -v cmake >/dev/null 2>&1; then
  cmake -S "${ROOT_DIR}/native/calc_core" -B "${BUILD_DIR}" -DCMAKE_BUILD_TYPE=Release
  cmake --build "${BUILD_DIR}" --parallel
  ctest --test-dir "${BUILD_DIR}" --output-on-failure
else
  # Keep the smoke check useful on small contributor images without CMake.
  CC_BIN="${CC:-cc}"
  mkdir -p "${BUILD_DIR}"
  if [[ "${OSTYPE:-}" == darwin* ]]; then
    "${CC_BIN}" -std=c11 -O2 -fPIC -DSUPERCALC_CORE_BUILD \
      -dynamiclib -I "${ROOT_DIR}/native/calc_core/include" \
      "${ROOT_DIR}/calc_core.c" "${ROOT_DIR}/native/calc_core/src/supercalc_core.c" \
      -lm -o "${BUILD_DIR}/libsupercalc_core.dylib"
  else
    "${CC_BIN}" -std=c11 -O2 -fPIC -DSUPERCALC_CORE_BUILD \
      -shared -I "${ROOT_DIR}/native/calc_core/include" \
      "${ROOT_DIR}/calc_core.c" "${ROOT_DIR}/native/calc_core/src/supercalc_core.c" \
      -lm -o "${BUILD_DIR}/libsupercalc_core.so"
  fi
  "${CC_BIN}" -std=c11 -O2 -I "${ROOT_DIR}/native/calc_core/include" \
    "${ROOT_DIR}/native/calc_core/tests/smoke_test.c" \
    -L"${BUILD_DIR}" -Wl,-rpath,"${BUILD_DIR}" -lsupercalc_core \
    -o "${BUILD_DIR}/supercalc_core_smoke"
  if [[ "${OSTYPE:-}" == darwin* ]]; then
    "${BUILD_DIR}/supercalc_core_smoke"
  else
    LD_LIBRARY_PATH="${BUILD_DIR}${LD_LIBRARY_PATH:+:${LD_LIBRARY_PATH}}" \
      "${BUILD_DIR}/supercalc_core_smoke"
  fi
fi

printf '\nNative core build complete.\n'
