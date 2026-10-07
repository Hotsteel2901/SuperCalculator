# Performance and resource report

## Implemented safeguards

- The Dart expression fallback compiles an expression into an AST once and reuses it
  for array sampling, numerical derivatives, adaptive Simpson integration, root
  solving and RK4.
- Native ABI v2 array and repeated-sampling paths reuse compiled RPN in the C core.
- Plot previews cap sample counts, preserve non-finite gaps, and repaint only the
  chart surface through a dedicated `CustomPainter`.
- The backend is asynchronous at the UI boundary, so the native library can be
  moved to an isolate without changing feature widgets. Large calculations should
  use the isolate adapter before release; the current small preview paths remain
  bounded for responsive interaction.
- The app-owned design tokens keep spacing, minimum plot height and control density
  consistent across compact and expanded layouts.

## Release measurements still required

No physical-device benchmark is claimed in this repository because the local checkout
has no Flutter SDK or target devices. The release gate must record, per representative
case:

- build and raster frame timing at 60 Hz and, when available, 120 Hz;
- time to first frame and time from submit to result;
- peak memory for 10k/100k plot samples, matrices and CSV imports;
- native versus Dart fallback latency and package size;
- isolate startup and cancellation latency.

Targets are a stable 60 fps core experience, best-effort 120 fps on high-refresh
hardware, no unbounded UI-isolate work, and graceful cancellation/error reporting.
The benchmark output belongs in `docs/reports/` and must include device, OS, Flutter,
Dart, build mode and sample size.
