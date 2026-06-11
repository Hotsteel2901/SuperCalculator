# Super Function Graphing Calculator

> A high-performance function graphing calculator using the **Bridge Pattern**:
C for computation, Python for the GUI, and `ctypes` as the bridge.

[![Build Windows EXE](https://github.com/Hotsteel2901/SuperCalculator/actions/workflows/build-windows-exe.yml/badge.svg)](https://github.com/Hotsteel2901/SuperCalculator/actions/workflows/build-windows-exe.yml)

[![Build Android APK](https://github.com/Hotsteel2901/SuperCalculator/actions/workflows/build-android-apk.yml/badge.svg)](https://github.com/Hotsteel2901/SuperCalculator/actions/workflows/build-android-apk.yml)

[中文](README_CN.md) | **English**

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
- **Polar Coordinate Plotting** — plot curves defined as r(theta), with 12 built-in presets (cardioid, rose curves, clover, spiral, lemniscate, etc.)
- **Implicit Function Plotting** — plot implicit equations of the form f(x,y)=0 (e.g., circles, ellipses, hyperbolas, cardioids, lemniscates, folium of Descartes) using contour-based rendering with 8 built-in presets and adjustable resolution
- **Multi-Curve Overlay** — plot multiple functions simultaneously with different colors
- **Numerical Derivatives** — first and second derivative via central difference
- **Numerical Integration** — adaptive Simpson's rule for definite integrals
- **Equation Solving** — Newton-Raphson (with bisection fallback) and pure bisection
- **Nonlinear System Solver (2D)** — solve systems of two equations f(x,y)=0, g(x,y)=0 using Newton's method for systems with numerical Jacobian, available on both desktop (Python) and Android (JNI)
- **Extremum Finder** — golden-section search for local minima and maxima on an interval
- **Limit Computation** — left-hand, right-hand, and two-sided limits via Richardson extrapolation
 - **Auto Root Scanner** — automatically scan an interval for all roots of f(x)=0, sign-change detection plus bisection refinement
 - **Curve Intersection Finder** — find all intersection points between any two 2D curves with sign-change detection and bisection refinement, results annotated on the plot
 - **Tangent & Normal Lines** — draw tangent and normal lines at any point on a 2D curve, visualized with dashed lines and labeled on the plot
 - **Arc Length** — approximate the arc length of a curve over any interval using adaptive chord summation
  - **Area Between Curves** — compute the enclosed area between any two curves f(x) and g(x) over [a,b] using adaptive Simpson's rule
  - **Fourier Transform & Spectrum Analysis** — FFT amplitude and phase spectrum for any function, with dominant-frequency detection and CSV export
  - **Taylor Series Expansion** — expand any function into a Taylor polynomial at an arbitrary point, with configurable order, coefficient display, and comparison plot of Taylor vs. original
  - **ODE Solver (RK4)** — solve first-order ODEs dy/dx = f(x,y) with initial conditions using 4th-order Runge-Kutta method, with solution plotting
  - **Statistics Calculator** — compute mean, median, mode, variance, standard deviation, quartiles (Q1/Q3/IQR), min, max, range; supports data sorting, histogram visualization, and CSV export
  - **Matrix Operations (Linear Algebra)** — perform matrix addition, subtraction, multiplication, determinant, inverse, transpose, rank, RREF, and eigenvalue computation on matrices up to any size; input format: rows separated by `;`, columns by `,` (e.g., `1,2;3,4` for a 2×2 matrix)
  - **Preset Functions** — quick-select from 21 common functions (including 3D and FFT presets) plus 10 parametric presets
  - **Parameter System** — auto-detects extra parameters (e.g., `a`, `b`) and provides live input fields
  - **Coordinate Marking** — left-click to mark points, right-click to delete the nearest marked point, or enter an x value to auto-locate
 - **Quick Input Panel** — popup keypad for fast insertion of operators, functions, and constants
 - **Factorial Support** — postfix `!` operator for non-negative integers
 - **Rounding & Modulo** — `floor(x)`, `ceil(x)` functions and `mod` (or `%`) operator for integer division remainders
 - **Customizable View** — adjustable X/Y/Z ranges, step size, grid toggle
 - **Interactive Plot** — Matplotlib toolbar for zoom, pan, and export
  - **Function Table & CSV Export** — generate a data table of x and f(x) over any interval, then export to CSV or copy to clipboard
  - **FFT Spectrum Export** — export frequency, amplitude and phase data to CSV for external analysis
  - **Complex Number Calculator** — perform complex arithmetic (+, -, *, /, ^), trigonometric functions (sin, cos, tan), exponential, logarithm, square root, absolute value, and conjugate. Available on both desktop (Python) and Android (JNI).
  - **Unit Converter** — convert between different units of measurement including Length, Weight, Temperature, Area, Volume, Time, Data Storage, Speed, and Angle. Supports 9 unit categories with comprehensive conversion factors.
   - **Curve Fitting / Regression** — fit data to various models: Linear (y=ax+b), Polynomial (configurable degree), Exponential (y=ae^(bx)), Power (y=ax^b), and Logarithmic (y=a+b·ln(x)). Displays equation, R² goodness-of-fit, and scatter + fitted curve plot. Available on both desktop (Python/numpy) and Android (Java).
   - **CSV Data Import & Scatter Plot** — import CSV/TSV data files with configurable delimiters (comma, tab, semicolon, space) and column selection. Plot data as scatter, line, or bar charts. Fit trendlines (Linear, Quadratic, Exponential) with R² goodness-of-fit display. Export plots as PNG. Available on desktop (Python) and Android (Java). Interactive demo on the project landing page.
   - **Statistical Distribution Calculator** — compute PDF/PMF, CDF, and PPF (inverse CDF) for 6 common distributions: Normal (Gaussian), Student's t, Chi-squared, F, Binomial, and Poisson. Includes distribution plotting and parameter comparison visualization. Available on both desktop (Python) and Android (Java).
   - **Number Theory Calculator** — perform integer factorization, primality testing (trial division), GCD/LCM computation, Fibonacci sequence generation, modular exponentiation (fast binary exponentiation), and Euler's totient function φ(n). Available on both desktop (Python) and Android (Java).
   - **Base Number Converter** — convert numbers between binary (2), octal (8), decimal (10), hexadecimal (16), and any base from 2 to 36. Supports both single-base conversion and simultaneous display of all common bases. Interactive demo available on the project landing page. Available on both desktop (Python) and Android (Java).
   - **Bitwise Operations Calculator** — perform bitwise AND, OR, XOR, NOT, left shift (<<), and right shift (>>) operations with configurable bit width (8/16/32). Real-time display of results in binary, octal, decimal, and hexadecimal. Interactive binary bit grid on the web landing page. Available on both desktop (Python) and Android (Java).
   - **Perpetual Calendar** — look up the day of the week for any date (YYYY-MM-DD), calculate the exact number of days between two dates, and add or subtract a given number of days from a date. Supports dates from year 1 to 9999. Available on both desktop (Python) and Android (Java).
   - **Probability Calculator** — compute combinations C(n,r), permutations P(n,r), event probabilities (union, intersection, complement), conditional probability P(A|B), Bayes' theorem, and binomial distribution P(X=k). Available on both desktop (Python) and Android (Java).
   - **Finance Calculator** — loan amortization (monthly payment, total interest), compound interest (FV/PV), NPV/IRR analysis, straight-line & double-declining depreciation, bond pricing, and retirement savings projection. Available on desktop (Python), Android (Java), and web landing page interactive demo.
   - **Volume of Revolution Calculator** — compute volumes of solids of revolution using three methods: Disk (V = π∫[f(x)]²dx), Washer (V = π∫([f(x)]²-[g(x)]²)dx), and Shell (V = 2π∫x·f(x)dx). Includes preset examples (sphere, cone, cylinder, torus). Available on desktop (Python), Android (Java), and web landing page interactive demo.
   - **Windows EXE** — standalone executable, no Python installation required
 - **Android App** — standalone APK with Material Design 3 UI and JNI bridge, now including 3D surface plotting with touch rotation and parametric curve support
 - **Chinese Language Support** — full Chinese (zh-CN) localization for both desktop (Python) and Android. Desktop auto-detects system locale or accepts `SUPERCALC_LANG=zh` env var. Android follows system language automatically.

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

## 📖 Usage Guide

**New to SuperCalculator?** Check out our detailed step-by-step usage tutorials:

- **[English Usage Guide](docs/usage_en.md)** — Comprehensive tutorial covering all features, from installation to advanced usage
- **[中文使用教程](docs/usage_cn.md)** — 保姆级详细教程，涵盖所有功能的使用方法

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
| Modulo       | `mod` `%` (remainder)              | `10 mod 3`, `7%2`  |
| Rounding     | `floor` `ceil`                     | `floor(x)` `ceil(x)` |
| Trig         | `sin` `cos` `tan`                 | `sin(x) + cos(x)`  |
| Log/Exp      | `ln` `log` `exp`                  | `ln(x)` `exp(-x)`  |
| Roots/Abs    | `sqrt` `abs`                      | `sqrt(x)` `abs(x)` |
| Factorial    | `!` (postfix)                      | `x!` `5!`          |
| Constants    | `pi` `e`                          | `sin(pi*x)`        |
| Complex      | `i` (imaginary unit)              | `1+2i`, `3-4i`     |

## File Structure

```
SuperCalculator/
  calc_core.c              C core engine (expression parser, calculus, solver)
  calc_bridge.py           Python ctypes bridge layer (multi-arch detection)
  super_calc_bridged.py    GUI main program (Tkinter + Matplotlib)
  locale_strings.py        i18n module (English + Chinese, auto locale detection)
  stat_dist.py             Statistical distribution calculator (Normal, t, Chi2, F, Binomial, Poisson)
  probability_calc.py      Probability calculator (combinations, permutations, Bayes, binomial)
  SuperCalculator.ico      Windows EXE icon
  SuperCalculator.spec     PyInstaller spec for Windows EXE build
  android/                 Android project (Gradle + JNI + M3 UI)
  .github/workflows/       CI: multi-platform build + Android APK + Windows EXE
  README.md                This file
  README_CN.md             Chinese documentation
  index.html               Project landing page
```

## What's New

- **Probability Calculator** — compute combinations C(n,r), permutations P(n,r), event probabilities (union P(A∪B), intersection P(A∩B), complement P(A')), conditional probability P(A|B), Bayes' theorem with full posterior calculation, and binomial distribution P(X=k) with mean/variance. Interactive demo on the project landing page. Available on both desktop (Python) and Android (Java).
- **Bitwise Operations Calculator** — perform bitwise AND, OR, XOR, NOT, left shift (<<), and right shift (>>) operations with configurable bit width (8/16/32). Real-time multi-base result display (binary, octal, decimal, hex). Interactive binary bit grid on the web landing page. Available on both desktop (Python) and Android (Java).
- **Base Number Converter** — convert numbers between binary, octal, decimal, and hexadecimal with support for any base from 2 to 36. Features simultaneous multi-base display, negative number support, and an interactive web demo. Available on both desktop (Python) and Android (Java).
- **Perpetual Calendar** — look up the day of the week for any date, calculate the exact number of days between two dates, and add or subtract days from a date. Supports dates from year 1 to 9999. Available on both desktop (Python) and Android (Java).
- **Statistical Distribution Calculator** — compute PDF/PMF, CDF, and PPF (inverse CDF) for 6 common probability distributions: Normal (Gaussian), Student's t, Chi-squared, F, Binomial, and Poisson. Features parameterized input, distribution plotting, and multi-parameter comparison visualization. Available on both desktop (Python) and Android (Java).
- **Chinese Language Support** — full Chinese (zh-CN) localization for both desktop and Android. Desktop uses `locale_strings.py` with auto locale detection (`SUPERCALC_LANG` env var or system locale). Android uses standard `values-zh-rCN/` string resources and follows system language. All UI labels, buttons, error messages, and dialog texts are translated.
- **Curve Fitting / Regression** — fit data to Linear, Polynomial, Exponential, Power, and Logarithmic models with R² goodness-of-fit. Scatter + curve plot visualization. Available on both desktop (Python/numpy) and Android (Java).
- **CSV Data Import & Scatter Plot** — import CSV/TSV data files with configurable delimiters (comma, tab, semicolon, space) and column selection. Plot data as scatter, line, or bar charts. Fit trendlines (Linear, Quadratic, Exponential) with R² goodness-of-fit display. Export plots as PNG. Available on both desktop (Python) and Android (Java). Interactive demo on the project landing page.
- **Nonlinear System Solver (2D)** — solve systems of two nonlinear equations f(x,y)=0, g(x,y)=0 using Newton's method for systems with numerical Jacobian via Cramer's rule. Available on both desktop (Python) and Android (JNI).
- **Area Between Curves** — compute the enclosed area between any two curves f(x) and g(x) over an interval [a,b] using adaptive Simpson's rule. Available on both desktop (Python) and Android (JNI).
- **Complex Number Calculator** — perform complex arithmetic (+, -, *, /, ^), trigonometric functions (sin, cos, tan), exponential, logarithm, square root, absolute value, and conjugate. Input format: `a+bi` (e.g., `1+2i`, `3-4i`). Available on both desktop (Python) and Android (JNI).
- **Matrix Operations (Linear Algebra)** — perform matrix addition, subtraction, multiplication, determinant, inverse, transpose, rank, RREF, and eigenvalue computation. Input format: rows separated by `;`, columns by `,` (e.g., `1,2;3,4`). Available on both desktop (Python/numpy) and Android (Java).
- **ODE Solver (RK4)** — solve first-order ODEs dy/dx = f(x,y) with initial conditions using 4th-order Runge-Kutta method. Supports custom step count, solution data output, and plotting. Available on both desktop (Python) and Android (JNI).
- **Taylor Series Expansion** — expand any function into a Taylor polynomial at an arbitrary expansion point with configurable order. Displays coefficients, the polynomial expression, and a comparison plot of Taylor vs. original function. Available on both desktop (Python) and Android (JNI).
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

# Area between curves
CalcEngine.area_between_curves("sin(x)", "0", 0, 3.141592653589793)  # -> 2.0
CalcEngine.area_between_curves("x^2", "x", 0, 1)  # -> ~0.1667

# Nonlinear system solver (2D)
result = CalcEngine.solve_system_2d("x^2+y^2-1", "x-y", x0=0.7, y0=0.7)
# result -> {'x': 0.7071..., 'y': 0.7071...} (intersection of unit circle and y=x)

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

# Taylor Series
coeffs = CalcEngine.taylor_coefficients("sin(x)", 0, 6)  # c_k = f^(k)(0)/k!
# coeffs -> [0, 1, 0, -0.1667, 0, 0.00833, 0]

# Evaluate Taylor polynomial at a point
taylor_val = CalcEngine.taylor_evaluate("sin(x)", 0, 0.5, 8)  # ~0.4794

# nth-order derivative
d5 = CalcEngine.nth_derivative("sin(x)", 1.0, 5)  # 5th derivative of sin at x=1

# ODE Solver (RK4)
result = CalcEngine.ode_solve_rk4("-y", x0=0, y0=1, x_end=5, n_steps=200)
# result['xs'] -> list of x values
# result['ys'] -> list of y values

# Complex Number Operations
z1 = complex(1, 2)  # 1+2i
z2 = complex(3, 4)  # 3+4i
result = CalcEngine.complex_add(z1, z2)  # (4+6j)
result = CalcEngine.complex_mul(z1, z2)  # (-5+10j)
result = CalcEngine.complex_sin(z1)      # sin(1+2i)
result = CalcEngine.complex_exp(z1)      # exp(1+2i)
result = CalcEngine.complex_abs(z1)      # |1+2i| = 2.236...
result = CalcEngine.complex_conj(z1)     # conj(1+2i) = (1-2j)

# Matrix Operations (using numpy directly)
import numpy as np
A = np.array([[1, 2], [3, 4]])
B = np.array([[5, 6], [7, 8]])
A + B              # Matrix addition
A - B              # Matrix subtraction
A @ B              # Matrix multiplication
np.linalg.det(A)   # Determinant
np.linalg.inv(A)   # Inverse
A.T                # Transpose
np.linalg.matrix_rank(A)  # Rank
np.linalg.eig(A)   # Eigenvalues and eigenvectors

# Curve Fitting / Regression
result = CalcEngine.linear_regression([1,2,3,4,5], [2,4,5,4,5])
# result -> {'slope': ..., 'intercept': ..., 'r_squared': ..., 'equation': '...', 'xs_fit': [...], 'ys_fit': [...]}

result = CalcEngine.polynomial_regression(xs, ys, degree=3)
# result -> {'coeffs': [...], 'r_squared': ..., 'equation': '...', 'xs_fit': [...], 'ys_fit': [...]}

result = CalcEngine.exponential_regression(xs, ys)
# result -> {'a': ..., 'b': ..., 'r_squared': ..., 'equation': '...', 'xs_fit': [...], 'ys_fit': [...]}

result = CalcEngine.power_regression(xs, ys)
# result -> {'a': ..., 'b': ..., 'r_squared': ..., 'equation': '...', 'xs_fit': [...], 'ys_fit': [...]}

result = CalcEngine.logarithmic_regression(xs, ys)
# result -> {'a': ..., 'b': ..., 'r_squared': ..., 'equation': '...', 'xs_fit': [...], 'ys_fit': [...]}

# Base Number Conversion
result = CalcEngine.convert_base("FF", 16, 10)    # -> "255"
result = CalcEngine.convert_base("255", 10, 2)     # -> "11111111"
result = CalcEngine.convert_base_all("255", 10)     # -> {'bin': '11111111', 'oct': '377', 'dec': '255', 'hex': 'FF'}
value = CalcEngine.base_to_long("FF", 16)           # -> 255
result = CalcEngine.long_to_base(255, 16)           # -> "FF"

# Statistical Distribution Calculator
from stat_dist import create_distribution, DISTRIBUTIONS

# Normal distribution
dist = create_distribution("normal", mu=0, sigma=1)
dist.pdf(0.5)      # -> ~0.352
dist.cdf(1.96)     # -> ~0.975
dist.ppf(0.975)    # -> ~1.96

# Student's t-distribution
dist = create_distribution("t", nu=5)
dist.pdf(0.0)      # -> ~0.3796
dist.cdf(2.0)      # -> ~0.944

# Chi-squared distribution
dist = create_distribution("chi2", k=3)
dist.pdf(1.0)      # -> ~0.242
dist.cdf(6.25)     # -> ~0.90

# F-distribution
dist = create_distribution("f", d1=5, d2=10)
dist.pdf(1.0)      # -> ~0.348
dist.cdf(2.0)      # -> ~0.84

# Binomial distribution
dist = create_distribution("binomial", n=20, p=0.5)
dist.pmf(10)       # -> ~0.176
dist.cdf(10)       # -> ~0.588

# Poisson distribution
dist = create_distribution("poisson", lam=5)
dist.pmf(3)        # -> ~0.140
dist.cdf(5)        # -> ~0.616
```

## Numerical Methods

| Method              | Algorithm                                      | Error     |
|---------------------|------------------------------------------------|-----------|
| Derivative          | Central difference: (f(x+h)-f(x-h)) / 2h       | O(h^2)    |
| 2nd Derivative      | Central difference: (f(x+h)-2f(x)+f(x-h)) / h^2 | O(h^2)  |
| nth Derivative      | Recursive central differences                   | O(h^2)    |
| Taylor Coefficients | nth derivative / k! via recursive central diff  | O(h^2)    |
| Integration         | Adaptive composite Simpson's rule              | O(h^4)    |
| Root Finding        | Newton-Raphson with bisection fallback         | —         |
| System Solver (2D)  | Newton's method for systems (numerical Jacobian, Cramer's rule) | —  |
| Extremum Finder     | Golden-section search                          | Linear    |
| Limit               | Richardson extrapolation                       | O(h^2k)   |
| ODE Solver          | 4th-order Runge-Kutta (RK4)                    | O(h^4)    |
| Linear Regression   | Least squares (closed-form)                    | —         |
| Polynomial Regression | Least squares (normal equations / Vandermonde) | —       |
| Exponential/Power/Log Regression | Linearized least squares       | —         |
