# Super Function Graphing Calculator

[中文](README_CN.md) | **English**
> **Note:** This project was generated entirely by AI (Claude Code). Use at your own discretion.
A high-performance function graphing calculator using the **Bridge Pattern**:
C for computation, Python for the GUI, and `ctypes` as the bridge.

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

## Features

- **Function Plotting** - plot arbitrary mathematical expressions with `x`
- **Multi-Curve Overlay** - plot multiple functions simultaneously with different colors
- **Numerical Derivatives** - first and second derivative via central difference
- **Numerical Integration** - adaptive Simpson's rule for definite integrals
- **Equation Solving** - Newton-Raphson (with bisection fallback) and pure bisection
- **Preset Functions** - quick-select from 15 common functions
- **Customizable View** - adjustable X/Y ranges, step size, grid toggle
- **Interactive Plot** - Matplotlib toolbar for zoom, pan, and export

## Prerequisites

- **Python 3.9+** with packages: `numpy`, `matplotlib`
- **C compiler** (GCC/MinGW on Windows, GCC on Linux, or MSVC on Windows)

Install Python dependencies:

```bash
pip install numpy matplotlib
```

## Building the C Core

### Windows (MinGW / MSYS2)

```bash
gcc -shared -O2 -o calc_core.dll calc_core.c -lm
```

### Windows (MSVC / Developer Command Prompt)

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

## Usage

```bash
cd SuperCalculator
python super_calc_bridged.py
```

### Expression Syntax

| Category     | Operators / Functions              | Example            |
|-------------|------------------------------------|--------------------|
| Arithmetic   | `+` `-` `*` `/` `^` (power)       | `x^2 + 2*x - 1`   |
| Trig         | `sin` `cos` `tan`                 | `sin(x) + cos(x)`  |
| Log/Exp      | `ln` `log` `exp`                  | `ln(x)` `exp(-x)`  |
| Roots/Abs    | `sqrt` `abs`                      | `sqrt(x)` `abs(x)` |
| Constants    | `pi` `e`                          | `sin(pi*x)`        |

## File Structure

```
SuperCalculator/
  calc_core.c            C core engine (expression parser, calculus, solver)
  calc_bridge.py         Python ctypes bridge layer
  super_calc_bridged.py  GUI main program
  README.md              This file
```

## API Reference (calc_bridge.py)

```python
from calc_bridge import CalcEngine

# Evaluate at a point
CalcEngine.evaluate("x^2", 3.0)         # -> 9.0

# Evaluate array (efficient for plotting)
CalcEngine.evaluate_array("sin(x)", [0, 0.5, 1.0])

# Derivative
CalcEngine.derivative("x^3", 2.0)       # -> ~12.0 (f'(x)=3x^2)

# Second derivative
CalcEngine.derivative2("x^3", 2.0)      # -> ~12.0 (f''(x)=6x)

# Definite integral
CalcEngine.integrate_adaptive("x^2", 0, 1)  # -> ~0.333 (integral of x^2 = 1/3)

# Find root
CalcEngine.solve("x^2 - 4", guess=1, xmin=0, xmax=3)  # -> 2.0
```

## Numerical Methods

| Method              | Algorithm                                      | Error     |
|---------------------|------------------------------------------------|-----------|
| Derivative          | Central difference: (f(x+h)-f(x-h)) / 2h       | O(h^2)    |
| 2nd Derivative      | Central difference: (f(x+h)-2f(x)+f(x-h)) / h^2 | O(h^2)  |
| Integration         | Adaptive composite Simpson's rule              | O(h^4)    |
| Root Finding        | Newton-Raphson with bisection fallback         | -         |
