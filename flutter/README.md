# SuperCalculator - Next Era Flutter app

This directory is the production UI migration source. It uses null-safe Flutter,
Material 3 Expressive, Riverpod, go_router and a replaceable calculation backend.
The legacy Python/Android/Web entry points remain beside it only for rollback and
parity comparison; they are not the new primary UI.

## Local setup

1. Install the stable Flutter SDK recorded in `../docs/migration/toolchain.md`.
2. Run `flutter pub get` and `flutter gen-l10n`.
3. Run `flutter run -d chrome` or select a native device.
4. Run `flutter analyze` and `flutter test`.
5. From the repository root, run `./tool/build_native.sh` to verify the C ABI.

The native shared library is optional at development time. If it is not available,
Riverpod selects the bounded, compiled Dart fallback. Native platforms use the FFI
adapter when a platform artifact is present; Web currently uses the Dart fallback
until the Wasm adapter is packaged.

## Feature slices

The app currently exposes plotting, calculus, equations, ODE, signals, data analysis,
statistics, linear algebra, tools and session history. The manifest in
`../docs/migration/feature-manifest.json` distinguishes implemented, partial,
scaffolded and planned legacy capabilities. A partial page is an executable vertical
slice with boundary/error handling, not a claim that every legacy sub-option is done.

Platform folders can be generated for a target release with
`../tool/bootstrap_flutter_platforms.sh`. They are intentionally not required for
Web CI and are not committed as proof of native packaging or signing.
