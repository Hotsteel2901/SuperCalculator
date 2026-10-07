# SuperCalculator - Next Era architecture

## Direction

Flutter is the only production UI. The C numerical core is reused through a small,
versioned ABI. Python remains for build scripts, oracle tests and golden-vector
creation only.

## Layers

```text
Feature presentation
        │ Riverpod providers / go_router pages
Feature application and domain
        │ typed requests, results and failures
Repositories
        │ CalcBackend / persistence / export
Native or Web computation
        │ FFI on native, Wasm adapter on Web
C calculation core
```

The application is feature-first. Each feature owns its domain models, use cases,
data repository and presentation widgets. Shared design, error, export and backend
services live under `flutter/lib/core`.

## State management

Riverpod is the dependency-injection boundary. Native, Wasm, Dart fallback and fake
backends can be overridden in tests without changing widgets.

## Current vertical slices

The current workbench contains the shell, localization, Material 3 Expressive color
scheme, compiled Dart expression fallback, native FFI adapter boundary, history,
plot modes (function, parametric, polar and implicit), calculus, equations, ODE,
signals, statistics, data analysis, linear algebra and tools pages. Each page calls a
backend or deterministic fallback rather than being a static mock.

Native C ABI v2 is linked against the legacy core and its smoke vectors cover scalar,
array, invalid-expression, derivative, integral, root and RK4 behavior. When a target
platform has not packaged the shared library, the provider selects the bounded Dart
backend. Web currently uses that fallback; a production Wasm adapter remains a
separate release gate.
