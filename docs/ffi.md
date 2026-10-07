# SuperCalculator - Next Era FFI boundary

## Status

M0/M1 introduce the additive ABI boundary in `native/calc_core/include/supercalc_core.h`.
The legacy `calc_core.c` exports remain available for Python and Android until parity
verification is complete.

## Rules

- Use fixed-width integer types and `double`.
- Never expose a C struct layout to Dart unless it is explicitly ABI-versioned.
- Every caller-provided output buffer includes a count.
- Every native-owned allocation has an explicit free function.
- Every operation returns a status code and writes the result separately.
- Error text is diagnostic only; the Dart layer maps error codes to localized text.
- `sc_context_t` is the future owner of custom functions, history, and settings.
- A context must not cross isolates. Each worker isolate creates its own context.

## Native and Web backends

Native platforms use `dart:ffi` and a platform-specific dynamic library. Flutter Web
cannot load a normal native dynamic library through `dart:ffi`, so its production
backend will be a WebAssembly adapter. The current Web adapter deliberately falls
back to the bounded Dart evaluator until the Wasm artifact is added.

## Build

```bash
./tool/build_native.sh
```

The CMake smoke test is intentionally small. It verifies ABI versioning, scalar
and array evaluation, and error propagation before feature-specific bindings are
added.
