# M0 baseline

## Verified toolchain

- Flutter stable: 3.47.6
- Dart SDK embedded by that Flutter release: 3.13.5
- Local checkout does not currently contain a Flutter or Dart executable, so CI must
  run `flutter --version` and `dart --version` before dependency resolution.
- Code generation packages are pinned to the Dart 3.13-compatible analyzer range:
  `build_runner 2.14.1`, `freezed 3.2.4`, and `json_serializable 6.11.3`.

## Repository observations

- The Python UI is `super_calc_bridged.py` and uses Tkinter/Matplotlib.
- The Python bridge is `calc_bridge.py`.
- Android has an independent Java/XML UI and JNI bridge.
- The Web page is an independent JavaScript demo.
- The additive public ABI v2 now lives in `native/calc_core/include/` and is linked
  against the legacy C symbols by the native smoke build.
- The code defines more presets than the older README advertises; the migration
  manifest keeps the legacy count as a parity requirement instead of silently
  changing it.
- FFT, regression, statistics, finance, probability, and dense matrix operations
  are not all implemented by the C core today; the current Flutter fallback covers
  deterministic slices and records the remaining work in the manifest.

## M0 exit condition

Every entry in `feature-manifest.json` has a stable ID and a legacy source. Later
milestones add golden inputs, expected numerical tolerances, platform coverage and
Widget/integration test references without changing the IDs.
