# SuperCalculator - Next Era

SuperCalculator is being migrated to one null-safe Flutter application with a
replaceable calculation backend. The product name, window title, about text and
package metadata are **SuperCalculator - Next Era**.

> **Migration truth:** the Flutter workbench is the only new UI. The complete
> legacy inventory is tracked in
> [`docs/migration/feature-manifest.json`](docs/migration/feature-manifest.json).
> `implemented`, `partial` and `planned` are intentional, verifiable states; a
> legacy capability is never silently counted as migrated.

## What is delivered in the Flutter workbench

- Material 3 Expressive-compatible theme tokens, light/dark themes, reduced-motion
  handling, responsive NavigationRail/NavigationBar layouts and English/Simplified
  Chinese localization.
- Riverpod state management, go_router navigation and a `CalcBackend` contract.
  Native `dart:ffi` is preferred when the ABI library is present; Web and unsupported
  targets use the deterministic Dart fallback.
- Expression evaluation, function and multi-curve plots, parametric/polar/implicit
  sampling, surface/contour/direction/vector previews, calculus, equations, ODE
  methods (Euler, Improved-Euler/Heun, Midpoint, RK4 and RKF45), FFT/convolution,
  statistics with histogram, regression/interpolation, dense matrix tools, complex
  numbers, distributions, number theory, base/unit conversion, finance, custom
  functions, function tables and session history.
- Numerical golden vectors, boundary/error handling, native C ABI smoke tests and
  GitHub Actions checks for formatting, analysis, tests and Web release builds.

A feature may still be marked `partial` when the core calculation exists but a
legacy preset, export format, interactive 3D renderer or platform package is not
complete. See the manifest for the exact acceptance boundary.

## Quick start

```bash
cd flutter
flutter pub get
flutter gen-l10n
flutter run -d chrome
flutter analyze
flutter test
```

The checked-in CI workflow verifies the Flutter stable baseline and runs the same
format/analyze/test/Web-build gates. The local environment used for this migration
may not contain the Flutter executable; in that case use the GitHub Actions workflow
rather than claiming a local Flutter result.

Build and smoke-test the retained C core from the repository root:

```bash
./tool/build_native.sh
```

The script builds the versioned C ABI v2 library and exercises scalar, array, error,
calculus, root and RK4 vectors. Native artifacts are optional for Web development;
the backend falls back without changing the feature contract.

## Architecture

```text
Feature pages
  └── Riverpod controllers + go_router
        └── CalcBackend (replaceable contract)
              ├── dart:ffi → C ABI v2 shared library
              └── Dart AST/isolate fallback → Web and unsupported targets
```

Heavy fallback work crosses `ComputationDispatcher`; plot sampling is capped,
non-finite values create gaps, and rendering is isolated in `CustomPainter`. The
Flutter app does not use Python Tkinter or Matplotlib as a primary UI. Python files
remain only as legacy references, scripts or parity/build tooling during the
rollback window.

## Feature parity and original functionality

The original README and usage guides remain part of the inventory. Every item is
assigned an ID, priority, legacy source and status in the manifest:

- plotting: function, multi-curve, parametric, polar, implicit, surface, contour,
  direction and vector fields;
- calculus and equations: derivatives, integration, limits, Taylor, arc length,
  area/volume, roots, systems, extrema, intersections and tangent/normal tools;
- ODE and signals: five ODE methods, direction fields, FFT/spectrum and convolution;
- data and statistics: descriptive statistics, histogram, five regression models,
  six interpolation choices and CSV/TSV-style text input;
- linear algebra: dense operations, RREF/rank/eigenvalue support and sparse
  COO/SpMV/conjugate-gradient workflows;
- advanced tools: complex arithmetic, six distributions, number theory, base and
  bitwise operations, nine unit categories, finance and custom functions;
- app workflows: function tables, copyable CSV, quick presets, history and i18n;
- platform/release: Android, iOS, Windows, Linux, macOS and Web gates.

The Flutter UI is the migration target. The old Python/Android/Web entry points are
kept as rollback/parity references until parity sign-off; no new feature should be
implemented in a second UI.

## Verification and release documentation

- [`docs/migration/golden_vectors.json`](docs/migration/golden_vectors.json) —
  cross-backend numerical contract.
- [`docs/reports/m1-validation.md`](docs/reports/m1-validation.md) — CI/native
  validation and explicitly unmeasured device gates.
- [`docs/performance.md`](docs/performance.md) — frame, isolate, memory and sampling
  targets; no physical-device numbers are invented.
- [`docs/compatibility.md`](docs/compatibility.md) — target-platform matrix and FFI
  packaging gates.
- [`docs/accessibility.md`](docs/accessibility.md) — keyboard, pointer/touch/stylus,
  large text, reduced motion and screen-reader acceptance matrix.
- [`docs/design-system.md`](docs/design-system.md) and [`docs/ffi.md`](docs/ffi.md) —
  M3 Expressive tokens/components and native boundary details.
- [`docs/release-notes.md`](docs/release-notes.md) — current increment and known gaps.

## Safe migration and rollback

Each migration increment is additive and should be reversible. The C core, legacy
sources, ABI smoke script and feature manifest remain available while Flutter is
validated. If a Flutter route or backend adapter must be reverted, remove that
routing/adapter change and keep the previous entry point; do not delete the legacy
calculation implementation. See [`docs/rollback.md`](docs/rollback.md).

## License and contributions

Keep numerical changes covered by deterministic vectors, validate finite/error
boundaries, and document any new dependency or platform assumption before merging.
