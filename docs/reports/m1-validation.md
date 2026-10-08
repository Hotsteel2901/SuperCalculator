# Flutter and native validation report

Validation is recorded against the current
`arena/37daed62-supercalculator` branch. The local checkout does not contain a
Flutter/Dart executable, so Flutter checks are executed in GitHub Actions rather than
represented as local results.

## Local checks

| Check | Result | Evidence |
|---|---|---|
| Feature manifest JSON parse | Pass | `python3 -m json.tool docs/migration/feature-manifest.json` |
| Golden-vector JSON parse | Pass | `python3 -m json.tool docs/migration/golden_vectors.json` |
| Preset JSON parse | Pass | `python3 -m json.tool flutter/assets/presets/function_presets.json` |
| Native ABI shared-library build | Pass | `./tool/build_native.sh` |
| Native ABI smoke test | Pass | scalar, array, invalid expression, derivative, integral, root and RK4 vectors |
| Dart source structural parse | Pass | tree-sitter Dart grammar over `flutter/**/*.dart` |
| `git diff --check` | Pass | no whitespace errors |

The native command emits `supercalc_core smoke test passed` followed by
`Native core build complete.` The compiler uses C11, `-Wall -Wextra -Wpedantic`,
`-O2` and `-fPIC`; no warning suppression is used. Dart source structural parsing is
an additional local sanity check, not a replacement for Flutter analyzer/test.

## CI checks

Successful workflow run **37728950445** (Flutter job **113153448993**, native job
**113153448811**) ran on the branch head and completed all gates:

- Flutter stable baseline `3.47.6` and its embedded Dart version were printed;
- `flutter pub get`;
- `flutter gen-l10n`;
- Dart formatting, including the workflow's formatter commit step;
- `flutter analyze`;
- `flutter test`;
- `flutter build web --release`;
- native ABI smoke test with GCC.

The run has only the existing GitHub Actions notices about Node.js action migration and
the future `ubuntu-latest` image migration; these are not code failures.

## Coverage added in the current increment

The deterministic Flutter vectors now include ODE method convergence, function-table
spacing/CSV, regression, distribution boundaries, probability, calendar arithmetic,
COO sparse matrix-vector multiplication and conjugate-gradient solving. The UI slices
also cover multi-curve plots, histograms, copyable tables and the new advanced tools.

## Still requiring physical devices

CI does not certify:

- Android, iOS, Windows, Linux and macOS packaging/signing and dynamic-library loading;
- 60/120 Hz frame timing, memory/large CSV benchmarks and isolate profiling;
- screen-reader semantics on each target, large text, high contrast, keyboard,
  pointer, touch, stylus, rotation and foldable layouts;
- native FFI artifact parity for every platform ABI or a production WebAssembly artifact;
- persistent history storage and full interactive 3D rendering.

These are release gates, not silently inferred successes; see `docs/compatibility.md`,
`docs/performance.md` and `docs/accessibility.md`.
