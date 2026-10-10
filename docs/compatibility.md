# Compatibility matrix and release gates

The platform workflow `.github/workflows/flutter-platform-builds.yml` builds a release
artifact for every requested target. It is manual-only; select a `next-era-v*` tag
when dispatching it if the final GitHub Release publication job should run.

| Target | Workflow artifact | Native backend | Signing/installation note |
|---|---|---|---|
| Web | `SuperCalculator-Next-Era-web.tar.gz` | Dart fallback; WebAssembly remains an optional future adapter | Extract to any static host; base href must match deployment path |
| Android | universal/split APKs and release app bundle | arm64 ABI is built into `jniLibs`; other ABIs use Dart fallback | Current manual workflow outputs are unsigned; production keystore integration must be enabled before store publication |
| iOS | `SuperCalculator-Next-Era-ios-unsigned.ipa` | Dart fallback unless a signed native framework is supplied | Unsigned Payload must be re-signed with an Apple team/profile before install |
| Windows | portable ZIP and Inno Setup installer | `supercalc_core.dll` is colocated with the runner | Install the generated setup EXE or extract the portable ZIP |
| Linux | x64 tarball and amd64 `.deb` | `libsupercalc_core.so` is colocated with the bundle | Install with `dpkg -i` or extract the tarball |
| macOS | hosted-runner-architecture app ZIP and DMG | `libsupercalc_core.dylib` is placed in the app Frameworks directory | The artifacts are not universal, signed, or notarized; use Gatekeeper approval or a protected signing workflow |

## Flutter plotting interaction parity

The 2D Flutter plot preview and full-screen plot share the same data-space
viewport on Android, iOS, desktop and Web. Dragging pans the coordinate ranges,
pinch/trackpad scaling zooms around the gesture focal point, and a mouse wheel
zooms around its pointer. Grid lines and numeric ticks are regenerated from the
visible ranges on every update rather than translating a finite grid bitmap, so
panning never leaves a partial grid behind. The fullscreen action carries the
current axis ranges forward; reset returns to the standard `[-10, 10]` axes.

## Workflow behavior

1. Every job generates only its own Flutter platform folder with the pinned stable
   SDK, so missing generated folders do not hide source compilation failures.
2. Each desktop job compiles the versioned C ABI v2 and places the library beside the
   application. The IO backend searches the executable and macOS Frameworks paths
   before falling back to its library name.
3. Android builds the arm64 shared library with the hosted Android NDK and packages
   universal plus split release APKs and an app bundle. The current workflow does not
   consume production signing secrets; add a protected keystore-signing step and a
   release `key.properties` policy before store publication.
4. iOS produces a correctly shaped unsigned IPA because Apple signing credentials are
   private release infrastructure. A signed IPA must be built in a protected workflow.
5. The tag release job downloads every artifact, writes `SHA256SUMS` across nested
   artifact paths, and publishes all packages as one GitHub Release.

## Product identity

The visible product name is `SuperCalculator - Next Era`. The package/org baseline is
`com.supercalc` and `supercalculator_next_era`; confirm the legacy Android application
ID before the first store upgrade so an existing installation is not orphaned.

## Required release gates

Record Flutter/Dart versions, OS and architecture, minimum SDK, dynamic-library load
result, light/dark and large-text behavior, keyboard/pointer/touch/stylus input,
rotation/foldable behavior, install/upgrade/uninstall behavior and assistive-technology
results for each signed release. CI artifacts are build evidence, not store-signing
or physical-device certification.
