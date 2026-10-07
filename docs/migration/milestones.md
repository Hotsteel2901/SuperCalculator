# Migration milestones

| Milestone | Exit criteria | Current state |
|---|---|---|
| M0 inventory | Stable SDK baseline, feature IDs, rollback policy | Complete |
| M1 shell | Flutter shell, tokens, i18n, backend boundary, first vertical slice | Scaffolded; Flutter CI pending |
| M2 core bridge | C ABI parity vectors, native packaging, Wasm adapter | Planned |
| M3 P0/P1 features | Expression, plotting, calculus, equations, ODE, signals, history and custom functions | Planned |
| M4 P2 features | Advanced plots, data, statistics, probability, dense linear algebra and finance | Planned |
| M5 P3 features | Discrete tools, sparse matrices, units and calendar | Planned |
| M6 quality | Performance, accessibility, visual, compatibility and recovery reports | Planned |
| M7 release | Store/desktop/Web artifacts, CI/CD, signed release and legacy UI removal from release workflows | Planned |

A milestone is not accepted because a screen exists. It requires numerical golden
vectors, UI/integration tests, platform checks and a documented rollback point.
