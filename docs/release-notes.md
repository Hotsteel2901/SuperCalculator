# SuperCalculator - Next Era release notes

## Current migration increment

This increment delivers a working Flutter workbench beside the legacy entry points.
It is not presented as full legacy parity; the feature manifest is the source of
truth for every remaining capability.

### Delivered

- Flutter stable project with null safety, Material 3 Expressive theming, responsive
  NavigationRail/NavigationBar shell, go_router and Riverpod dependency injection.
- English and Simplified Chinese localization with generated-compatible sources.
- Native ABI v2 header, FFI adapter boundary, Web/Dart fallback and portable native
  build/smoke scripts.
- Compiled Dart expression evaluator with scalar/array/XY-array sampling, derivatives,
  adaptive Simpson integration, Newton plus bracketed bisection roots, RK4, DFT
  spectrum, statistics, linear regression, matrix operations, base and unit conversion.
- Plot modes for function, parametric, polar and implicit previews, plus accessible
  summaries and finite-gap handling.
- Vertical-slice pages for calculus, equations, ODE, signals, data analysis,
  statistics, linear algebra, tools and session-scoped calculation history.
- Deterministic Dart vectors, native C vectors and CI for localization, formatting,
  analyzer, tests and Web release build.

### Explicitly not yet claimed

Full legacy parity still includes custom functions, complex arithmetic, all advanced
plot/contour/vector-field modes, distributions/probability, finance, number theory,
sparse matrices, calendar tools, complete export/persistence, per-platform native
packaging and device accessibility/performance evidence. These remain tracked as
planned or partial rather than silently removed.

### Rollback

The legacy Python/Android/Web sources and C exports remain in the repository. A
rollback can remove the Flutter routing entry point and continue using the previous
entry points while the ABI and migration vectors remain available. See
`docs/rollback.md`.
