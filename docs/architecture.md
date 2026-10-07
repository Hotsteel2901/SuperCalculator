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

## Current vertical slice

M1 contains a working application shell, localization, Material 3 Expressive color
scheme, a bounded Dart expression evaluator, a native FFI adapter, and a 2D plot
preview. The native adapter falls back safely when the shared library has not yet
been packaged by the platform build.
