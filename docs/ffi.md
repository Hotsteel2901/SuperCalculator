# SuperCalculator - Next Era FFI boundary

## Status

The additive ABI v2 boundary in `native/calc_core/include/supercalc_core.h` is
implemented and linked against the legacy `calc_core.c` exports. The smoke test
covers scalar, array, invalid-expression/error propagation, derivative, integral,
root and RK4 vectors. The expanded Flutter workbench keeps advanced operations behind
the same replaceable backend and uses the deterministic Dart/isolate implementation
where the C ABI does not yet expose a symbol.

## Rules

- Use fixed-width integer types and `double`.
- Never expose a C struct layout to Dart unless it is explicitly ABI-versioned.
- Every caller-provided output buffer includes a count.
- Every native-owned allocation has an explicit free function.
- Every operation returns a status code and writes the result separately.
- Error text is diagnostic only; the Dart layer maps error codes to localized text.
- `sc_context_t` is isolated to one Dart execution context and must not cross
  isolates. Each worker isolate uses the Dart backend unless a dedicated native
  context is created there.

## Packaged native libraries

The tagged platform workflow compiles ABI v2 as part of desktop bundles:

- Windows: `supercalc_core.dll` beside the runner executable;
- Linux: `libsupercalc_core.so` beside the bundle executable;
- macOS: `libsupercalc_core.dylib` under `Contents/Frameworks`;
- Android: arm64 `libsupercalc_core.so` under `jniLibs/arm64-v8a`.

`FfiCalcBackend` searches the executable directory and macOS Frameworks directory
before using the platform loader name. If loading fails or the platform is Web/iOS,
`createCalcBackend` safely selects the Dart fallback.

## Native and Web backends

Flutter Web cannot load a normal native dynamic library through `dart:ffi`, so the
current Web adapter uses the bounded Dart evaluator. A production WebAssembly adapter
can replace it without changing repositories or widgets; the compatibility report
must record parity before it becomes the default.

## Build

```bash
./tool/build_native.sh
```

The CMake smoke test is intentionally small. It verifies ABI versioning, scalar and
array evaluation, implicit multiplication and case-insensitive built-ins, finite-input
validation, invalid-expression status propagation, calculus, root and RK4 vectors.
The C core keeps compiled RPN programs in a bounded per-thread cache for repeated
scalar calls without changing the ABI. The installer workflow repeats the ABI
compilation on the target runner and includes checksums in tagged releases.
