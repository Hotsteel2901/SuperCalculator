# SuperCalculator - Next Era release notes

## Current migration increment

This increment keeps the migration additive and rollback-safe while making the Flutter
workbench the only new UI. The feature manifest and golden vectors are the release
source of truth.

### Delivered in this increment

- Added a multi-curve overlay mode using semicolon/newline-separated expressions.
- Added selectable ODE methods: Euler, Improved-Euler/Heun, Midpoint, RK4 and RKF45;
  non-RK4 methods use the Dart backend when the C ABI only exposes RK4.
- Added deterministic function-table generation with copyable CSV output and range/
  row validation.
- Added a responsive statistics histogram with accessible bin summaries.
- Added complex, distribution, probability/calendar, number-theory, finance,
  custom-function, dense-matrix and sparse-COO workbench slices behind the
  replaceable backend contract.
- Added boundary/golden vectors for ODE convergence, function tables, regression and
  distribution edge cases.
- Updated English/Chinese README, feature manifest and migration reports to distinguish
  implemented vertical slices from remaining parity work.

### Explicitly not claimed

Best-effort persistent history storage, complete preset verification, full interactive 3D
rendering, production per-platform FFI packaging/signing, WebAssembly packaging,
physical-device performance measurements and screen-reader certification remain release
gates. A
lightweight 2D projection is used for surface/field previews until the interactive
renderer is selected.

### Verification

The checked-in CI workflow runs the stable Flutter baseline, localization generation,
formatting, analyzer, Flutter tests, Web release build and native ABI smoke tests.
The latest successful CI evidence is recorded in the migration validation report; a
local checkout without Flutter must not be described as locally verified.

### Rollback

The legacy C/Python/Android/Web sources and native ABI smoke scripts remain intact.
Revert only the affected Flutter route, adapter or feature commit if a migration slice
fails; do not delete the legacy implementation. See `docs/rollback.md`.
