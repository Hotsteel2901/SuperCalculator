# M1 validation report

Date: 2026-10-07

## Executed in this checkout

| Check | Result | Notes |
|---|---|---|
| Feature manifest JSON parse | Pass | `python3 -m json.tool` |
| Preset JSON parse | Pass | `python3 -m json.tool` |
| Native ABI shared-library build | Pass | Direct GCC fallback because CMake is not installed |
| Native ABI smoke test | Pass | scalar, array, error and ABI-version checks |
| `flutter pub get` | Not run | Flutter/Dart executable is not installed in this environment |
| `flutter gen-l10n` | Not run | Same toolchain limitation |
| `flutter analyze` | Not run | Same toolchain limitation |
| Flutter unit/integration tests | Not run | Same toolchain limitation |
| Frame, memory and package benchmarks | Not run | Require Flutter devices/CI |
| Screen reader and large-text checks | Not run | Require Flutter devices/CI |

The native compiler emitted warnings from the legacy `calc_core.c` implementation;
they are pre-existing and do not fail the ABI smoke test. They are recorded for the
native parity hardening milestone rather than hidden by warning suppression.
