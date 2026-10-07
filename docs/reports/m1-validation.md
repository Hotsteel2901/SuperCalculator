# Flutter and native validation report

Validation is recorded against the current `arena/37daed62-supercalculator` branch.
The local checkout does not contain a Flutter/Dart executable, so the Flutter checks
are intentionally executed in GitHub Actions rather than described as local results.

## Local checks

| Check | Result | Evidence |
|---|---|---|
| Feature manifest JSON parse | Pass | `python3 -m json.tool docs/migration/feature-manifest.json` |
| Golden-vector JSON parse | Pass | `python3 -m json.tool docs/migration/golden_vectors.json` |
| Preset JSON parse | Pass | `python3 -m json.tool flutter/assets/presets/function_presets.json` |
| Native ABI shared-library build | Pass | `./tool/build_native.sh` |
| Native ABI smoke test | Pass | scalar, array, invalid expression, derivative, integral, root and RK4 vectors |
| `git diff --check` | Pass | no whitespace errors |

The native command emits `supercalc_core smoke test passed` followed by
`Native core build complete.` The compiler is invoked with C11,
`-Wall -Wextra -Wpedantic`, `-O2` and `-fPIC`; no warning suppression is used.

## CI checks

GitHub Actions workflow **Flutter Next Era checks** uses Flutter stable `3.47.6`
and runs the following in `flutter/`:

- `flutter pub get`
- `flutter gen-l10n`
- `dart format lib test integration_test`
- `flutter analyze`
- `flutter test`
- `flutter build web --release`

The same run builds and links the native ABI smoke test with GCC. The successful
validation run is retained in the pull request checks for the branch; the workflow
also prints the installed Flutter and Dart versions so a future stable upgrade is
observable rather than assumed.

## Still requiring physical devices

The following are not claimed by CI alone and remain release gates:

- Android, iOS, Windows, Linux and macOS packaging/signing and dynamic-library loading;
- 60/120 Hz frame timing, memory/large CSV benchmarks and isolate profiling;
- screen-reader semantics on each target, large text, high contrast, keyboard,
  pointer, touch, stylus, rotation and foldable layouts;
- native FFI artifact parity against every platform ABI and a production WebAssembly
  artifact instead of the current Web Dart fallback.
