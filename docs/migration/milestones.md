# Migration milestones

The migration is incremental: each milestone leaves the legacy entry points intact,
records a rollback point, and is accepted only with numerical vectors plus the
platform checks that apply to that slice.

| Milestone | Exit criteria | Current state |
|---|---|---|
| M0 inventory | Stable SDK baseline, feature IDs, priority matrix, rollback policy | Complete |
| M1 shell | Flutter shell, M3 Expressive tokens, i18n, backend boundary and responsive navigation | Complete; CI verified |
| M2 core bridge | Versioned C ABI, scalar/array/error/derivative/integration/root/RK4 vectors, native smoke test | Complete for the published ABI slice |
| M3 first workbench | Plot modes, calculus, equations, ODE, signals, statistics, data, matrix and tools vertical slices | Complete as partial slices; long-tail parity remains in the manifest |
| M4 parity expansion | Custom functions, complex, distributions, probability, advanced plot modes, exports and persistence | Planned; no legacy capability is removed |
| M5 platform packaging | Generated Android/iOS/Windows/Linux/macOS projects, native artifacts, Web fallback/Wasm adapter | Bootstrap scripts and Web build are present; target packaging is next |
| M6 quality | Device frame/memory benchmarks, accessibility matrix, visual regression and recovery drills | Reports and test hooks present; device measurements pending |
| M7 release | Store/desktop/Web artifacts, CI/CD, signed release and removal of legacy UI from release workflows | Planned after parity sign-off |

## Current acceptance evidence

- `./tool/build_native.sh` compiles the legacy C implementation plus ABI v2 with
  `-Wall -Wextra -Wpedantic` and runs `supercalc_core smoke test passed`.
- GitHub Actions workflow `Flutter Next Era checks` runs Flutter stable `3.47.6`
  with `pub get`, localization generation, formatting, analyzer, tests and a Web
  release build; the native job runs the same ABI smoke test.
- `docs/migration/golden_vectors.json` is the seed contract for future backend
  parity. The Flutter tests add deterministic vectors for the current Dart fallback.

A status of `partial` means a usable feature slice exists, not that every legacy
sub-option is complete. The full legacy inventory remains in
`docs/migration/feature-manifest.json` and the original README files.
