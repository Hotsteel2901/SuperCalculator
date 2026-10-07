# Compatibility matrix and release gates

| Target | Current migration state | Native backend state | Release gate |
|---|---|---|---|
| Web | CI `flutter build web --release` passes | bounded Dart fallback; Wasm artifact not packaged | browser matrix, WebAssembly parity, keyboard/reader audit |
| Android | Flutter source and platform bootstrap script present | ABI artifact packaging/signing not yet automated | min SDK, arm64/armv7/x64 as supported, rotation, TalkBack |
| iOS | Flutter source and platform bootstrap script present | framework/dylib packaging and signing not yet automated | simulator/device build, arm64, VoiceOver, entitlements |
| Windows | Flutter source and platform bootstrap script present | DLL packaging not yet automated | x64/arm64 decision, MSVC/MinGW ABI check, Narrator |
| Linux | Flutter source and platform bootstrap script present | `.so` packaging not yet automated | x64 package, GTK/desktop integration, screen reader |
| macOS | Flutter source and platform bootstrap script present | dylib/framework packaging not yet automated | Intel/Apple Silicon decision, hardened runtime, VoiceOver |

The checked-in source is deliberately platform-neutral. Run
`./tool/bootstrap_flutter_platforms.sh` from the repository root with a supported
Flutter SDK to generate missing platform folders; generated folders are not treated
as proof that native artifacts are packaged. The manual/tag-triggered
`.github/workflows/flutter-platform-builds.yml` workflow generates the target folder
on its runner and produces Web, Android debug, Linux, Windows, macOS and unsigned iOS
artifacts. It does not claim store signing or native FFI packaging parity.

Product-visible naming is `SuperCalculator - Next Era`. The legacy Android application
ID remains `com.supercalc` in the migration plan so a future signed APK can preserve
upgrade compatibility; it must be confirmed against the shipped legacy manifest before
an actual store release.

Every release must record Flutter/Dart versions, OS and architecture, minimum SDK,
dynamic-library loading result, light/dark and large-text behavior, keyboard/pointer/
touch/stylus input, rotation/foldable layout behavior and assistive-technology results.
