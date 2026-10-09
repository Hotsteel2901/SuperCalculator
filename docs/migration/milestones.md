# Migration milestones

The migration is incremental: each milestone leaves a rollback point, records the
legacy inventory, and is accepted only with numerical vectors plus applicable platform
checks.

| Milestone | Exit criteria | Current state |
|---|---|---|
| M0 inventory | Stable SDK baseline, feature IDs, priority matrix and rollback policy | Complete |
| M1 shell | Flutter shell, M3 Expressive tokens, i18n, backend boundary and responsive navigation | Complete; CI verified |
| M2 core bridge | Versioned C ABI, scalar/array/error/calculus/root/RK4 vectors and native smoke test | Complete for the published ABI slice |
| M3 workbench | Plot, calculus, equations, ODE, signals, statistics, data, matrix and tools vertical slices | Complete as usable vertical slices; remaining sub-capabilities stay explicit |
| M4 parity expansion | Custom functions, complex, distributions, probability/calendar, sparse tools, multi-curve, tables, histogram and advanced plot slices | Complete; all 34 manifest capabilities are implemented and covered by deterministic vectors or CI |
| M5 platform packaging | Generated Android/iOS/Windows/Linux/macOS projects, native artifacts and Web fallback/Wasm decision | Workflow and unsigned artifact contract are CI-verified; signing and physical-device qualification remain release gates |
| M6 quality | Device frame/memory benchmarks, accessibility matrix, visual regression and recovery drills | Reports and deterministic vectors present; device measurements pending |
| M7 release | Store/desktop/Web artifacts, CI/CD, signed release and legacy UI removal from release workflows | Planned after parity sign-off |

## Current acceptance evidence

- `./tool/build_native.sh` compiles the retained C implementation plus ABI v2 with
  `-Wall -Wextra -Wpedantic` and runs the native smoke vectors.
- `.github/workflows/flutter-next-era.yml` runs the stable Flutter baseline with pub
  get, localization generation, formatting, analyzer, tests and a Web release build;
  the native job runs the ABI smoke test and the platform-contract job checks every
  Android/iOS/Windows/Linux/macOS/Web artifact declaration and explicit unsigned
  signing boundary in the release workflow.
- `docs/migration/golden_vectors.json` is the cross-backend numerical contract. The
  Flutter tests cover expression sampling, calculus, plotting, equations, ODE methods,
  spectrum/convolution, stats, regression/interpolation, distributions, complex/number
  theory, matrices, bitwise, finance, history codecs, presets and unit conversions.
- `docs/migration/feature-manifest.json` is the parity status authority. All current
  capabilities are implemented; release-qualification gates are recorded separately
  in `verificationNotes.knownGaps`. A `planned` item is not claimed as migrated.
