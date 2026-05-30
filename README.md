# Super Function Graphing Calculator

[![Build Windows EXE](https://github.com/Hotsteel2901/SuperCalculator/actions/workflows/build-windows-exe.yml/badge.svg)](https://github.com/Hotsteel2901/SuperCalculator/actions/workflows/build-windows-exe.yml)

[![Build Android APK](https://github.com/Hotsteel2901/SuperCalculator/actions/workflows/build-android-apk.yml/badge.svg)](https://github.com/Hotsteel2901/SuperCalculator/actions/workflows/build-android-apk.yml)

[中文](README_CN.md) | **English**
A high-performance function graphing calculator using the **Bridge Pattern**:
C for computation, Python for the GUI, and `ctypes` as the bridge.

Also includes an **Android APK** build (aarch64) with a Material Design 3 UI.

## Architecture

```
+---------------------------------+
|  super_calc_bridged.py          |  Tkinter + Matplotlib GUI
|  (Abstraction)                  |
+---------------------------------+
|  calc_bridge.py                 |  ctypes bridge layer
|  (Bridge)                       |
+---------------------------------+
|  calc_core.dll / .so            |  C dynamic library
|  (Implementation)               |
+---------------------------------+
```

The bridge layer auto-detects platform and CPU architecture at load time, selecting the correct binary from the available pre-compiled options.

## Features

- **Function Plotting** — plot arbitrary mathematical expressions with `x`
- **3D Function Plotting** — plot surfaces for expressions with both `x` and `y`
- **Parametric Curve Plotting** — plot curves defined as x(t) and y(t), with 10 built-in presets (circle, ellipse, Lissajous, spiral, cardioid, heart, etc.)
- **Multi-Curve Overlay** — plot multiple functions simultaneously with different colors
- **Numerical Derivatives** — first and second derivative via central difference
- **Numerical Integration** — adaptive Simpson's rule for definite integrals
- **Equation Solving** — Newton-Raphson (with bisection fallback) and pure bisection
- **Extremum Finder** — golden-section search for local minima and maxima on an interval
- **Limit Computation** — left-hand, right-hand, and two-sided limits via Richardson extrapolation
 - **Auto Root Scanner** — automatically scan an interval for all roots of f(x)=0, sign-change detection plus bisection refinement
 - **Curve Intersection Finder** — find all intersection points between any two 2D curves with sign-change detection and bisection refinement, results annotated on the plot
 - **Tangent & Normal Lines** — draw tangent and normal lines at any point on a 2D curve, visualized with dashed lines and labeled on the plot
 - **Arc Length** — approximate the arc length of a curve over any interval using adaptive chord summation
  - **Fourier Transform & Spectrum Analysis** — FFT amplitude and phase spectrum for any function, with dominant-frequency detection and CSV export
  - **Preset Functions** — quick-select from 21 common functions (including 3D and FFT presets) plus 10 parametric presets
  - **Parameter System** — auto-detects extra parameters (e.g., `a`, `b`) and provides live input fields
  - **Coordinate Marking** — left-click to mark points, right-click to delete the nearest marked point, or enter an x value to auto-locate
 - **Quick Input Panel** — popup keypad for fast insertion of operators, functions, and constants
 - **Factorial Support** — postfix `!` operator for non-negative integers
 - **Customizable View** — adjustable X/Y/Z ranges, step size, grid toggle
 - **Interactive Plot** — Matplotlib toolbar for zoom, pan, and export
  - **Function Table & CSV Export** — generate a data table of x and f(x) over any interval, then export to CSV or copy to clipboard
  - **FFT Spectrum Export** — export frequency, amplitude and phase data to CSV for external analysis
 - **Windows EXE** — standalone executable, no Python installation required
 - **Android App** — standalone APK with Material Design 3 UI and JNI bridge, now including 3D surface plotting with touch rotation and parametric curve support

## Pre-compiled Binaries

Pre-compiled binaries are available in the [Releases](https://github.com/Hotsteel2901/SuperCalculator/releases).

| Platform | Architecture | Binary | Pre-compiled |
|----------|-------------|--------|:---:|
| Windows | x64 | `calc_core.dll` / `SuperCalculator.exe` | Yes |
| Linux | x86_64 | `calc_core_x86_64.so` | Yes |
| Linux | ARM64 | `calc_core_aarch64.so` | Yes |
| macOS | x86_64 / ARM64 | `calc_core.dylib` | Rebuild from source |
| Android | ARM64 | `SuperCalculator-*.apk` | Yes (via workflow) |

## Quick Start

### Windows (EXE — no Python needed)

Download `SuperCalculator.exe` from the [Releases](https://github.com/Hotsteel2901/SuperCalculator/releases) page and double-click to run. The console window is kept for output and debugging.

### Python Source

```bash
pip install numpy matplotlib
python super_calc_bridged.py
```

## Prerequisites

- **Python 3.9+** with packages: `numpy`, `matplotlib`
- **C compiler** for rebuilding from source (GCC/MinGW on Windows, GCC on Linux)

## Building from Source

### Windows (MinGW-w64 / MSYS2)

```bash
gcc -shared -O2 -o calc_core.dll calc_core.c -lm
```

### Windows (MSVC)

```bash
cl /LD /O2 calc_core.c /Fe:calc_core.dll
```

### Linux

```bash
gcc -shared -O2 -fPIC -o calc_core.so calc_core.c -lm
```

### macOS

```bash
gcc -shared -O2 -fPIC -o calc_core.dylib calc_core.c -lm
```

## Expression Syntax

| Category     | Operators / Functions              | Example            |
|-------------|------------------------------------|--------------------|
| Arithmetic   | `+` `-` `*` `/` `^` (power)       | `x^2 + 2*x - 1`   |
| Trig         | `sin` `cos` `tan`                 | `sin(x) + cos(x)`  |
| Log/Exp      | `ln` `log` `exp`                  | `ln(x)` `exp(-x)`  |
| Roots/Abs    | `sqrt` `abs`                      | `sqrt(x)` `abs(x)` |
| Factorial    | `!` (postfix)                      | `x!` `5!`          |
| Constants    | `pi` `e`                          | `sin(pi*x)`        |

## File Structure

```
SuperCalculator/
  calc_core.c              C core engine (expression parser, calculus, solver)
  calc_bridge.py           Python ctypes bridge layer (multi-arch detection)
  super_calc_bridged.py    GUI main program (Tkinter + Matplotlib)
  SuperCalculator.ico      Windows EXE icon
  SuperCalculator.spec     PyInstaller spec for Windows EXE build
  android/                 Android project (Gradle + JNI + M3 UI)
  .github/workflows/       CI: multi-platform build + Android APK + Windows EXE
  README.md                This file
  README_CN.md             Chinese documentation
  index.html               Project landing page
```

## What's New

- **Limit Computation** — compute left-hand, right-hand, and two-sided limits using Richardson extrapolation for high accuracy. Available on both desktop (Python) and Android (JNI).
- **Parametric Curve Plotting** — plot curves defined as x(t) and y(t) with 10 built-in presets (circle, ellipse, Lissajous, spiral, cardioid, heart, trefoil knot, butterfly curve, star). Available on both desktop (Python) and Android (JNI).
- **Fourier Transform & Spectrum Analysis** — FFT amplitude and phase spectrum computation with dominant-frequency detection and CSV export. Available on both desktop (Python) and Android (DFT implementation).
- **21 Preset Functions** — now includes dedicated FFT demonstration expressions for instant spectrum analysis.

## CI / CD

GitHub Actions workflows are available (manual trigger):

| Workflow | Purpose | Release Push |
|----------|---------|:---:|
| `Build All Platforms` | Win x64 DLL, Linux x86_64, Linux ARM64 | Optional |
| `Build Android APK` | Android aarch64 APK | No |
| `Build Windows EXE` | Standalone Windows executable with icon | Optional |

## API Reference

```python
from calc_bridge import CalcEngine

# Evaluate at a point
CalcEngine.evaluate("x^2", 3.0)         # -> 9.0

# Evaluate f(x,y) at a point
CalcEngine.evaluate_xy("x^2+y^2", 3.0, 4.0)  # -> 25.0

# Evaluate array (efficient for plotting)
CalcEngine.evaluate_array("sin(x)", [0, 0.5, 1.0])

# Derivative
CalcEngine.derivative("x^3", 2.0)       # -> ~12.0 (f'(x)=3x^2)

# Second derivative
CalcEngine.derivative2("x^3", 2.0)      # -> ~12.0 (f''(x)=6x)

# Definite integral
CalcEngine.integrate_adaptive("x^2", 0, 1)  # -> ~0.333

# Find root
CalcEngine.solve("x^2 - 4", guess=1, xmin=0, xmax=3)  # -> 2.0

# Find extremum
CalcEngine.find_minimum("x^2", -5, 5)   # -> ~0.0
CalcEngine.find_maximum("sin(x)", 0, 6) # -> ~1.571

# Limit computation
CalcEngine.limit("sin(x)/x", 0)          # -> ~1.0
CalcEngine.limit_left("1/x", 0)          # -> -inf
CalcEngine.limit_right("1/x", 0)         # -> +inf

# Curve intersection (compute difference and solve)
# Example: intersection of sin(x) and cos(x) in [0, pi]
# Use solve_bisection on the difference expression
CalcEngine.solve_bisection("(sin(x))-(cos(x))", 0, 3.14)  # -> ~0.785

# Arc length
CalcEngine.arc_length("sin(x)", 0, 3.141592653589793)  # -> ~3.820

# Parametric curve evaluation
spec = CalcEngine.evaluate_parametric("cos(t)", "sin(t)", 0, 2*pi, 500)
# spec['xs'] -> list of x-values
# spec['ys'] -> list of y-values
# spec['ts'] -> list of t-values

# FFT Spectrum
spec = CalcEngine.fft_spectrum("sin(2*pi*x)+0.5*sin(6*pi*x)", 0, 2, 1024)
# spec['freqs'] -> list of frequencies
# spec['amps']  -> list of amplitudes
# spec['phases']-> list of phases (radians)
```

## Numerical Methods

| Method              | Algorithm                                      | Error     |
|---------------------|------------------------------------------------|-----------|
| Derivative          | Central difference: (f(x+h)-f(x-h)) / 2h       | O(h^2)    |
| 2nd Derivative      | Central difference: (f(x+h)-2f(x)+f(x-h)) / h^2 | O(h^2)  |
| Integration         | Adaptive composite Simpson's rule              | O(h^4)    |
| Root Finding        | Newton-Raphson with bisection fallback         | —         |
| Extremum Finder     | Golden-section search                          | Linear    |
| Limit               | Richardson extrapolation                       | O(h^2k)   |
