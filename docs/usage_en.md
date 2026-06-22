# Super Function Graphing Calculator — Usage Guide

**English Version** | [中文版](usage_cn.md)

> This is a comprehensive, step-by-step guide to using all features of SuperCalculator. Detailed enough for anyone!

[Back to README](../README.md) | [Back to Chinese README](../README_CN.md)

---

## Table of Contents

1. [Installation & Getting Started](#1-installation--getting-started)
   - [1.1 Windows Users](#11-windows-users)
   - [1.2 Running from Python Source](#12-running-from-python-source)
   - [1.3 Android Users](#13-android-users)
   - [1.4 macOS / Linux Users](#14-macos--linux-users)
2. [Interface Overview](#2-interface-overview)
3. [Expression Syntax](#3-expression-syntax)
   - [3.1 Basic Arithmetic](#31-basic-arithmetic)
   - [3.2 Supported Functions](#32-supported-functions)
   - [3.3 Constants](#33-constants)
   - [3.4 Complex Numbers](#34-complex-numbers)
   - [3.5 Factorial & Modulo](#35-factorial--modulo)
4. [Function Plotting](#4-function-plotting)
   - [4.1 Basic 2D Function Plotting](#41-basic-2d-function-plotting)
   - [4.2 Multi-Curve Overlay](#42-multi-curve-overlay)
   - [4.3 Coordinate Marking](#43-coordinate-marking)
   - [4.4 Customizing View Range](#44-customizing-view-range)
   - [4.5 Using Preset Functions](#45-using-preset-functions)
   - [4.6 Parameter System](#46-parameter-system)
5. [3D Function Plotting](#5-3d-function-plotting)
6. [Parametric Curve Plotting](#6-parametric-curve-plotting)
7. [Polar Coordinate Plotting](#7-polar-coordinate-plotting)
 8. [Implicit Function Plotting](#8-implicit-function-plotting)
 8.1. [Contour Plot (Level Sets)](#81-contour-plot-level-sets)
 9. [Numerical Computation](#9-numerical-computation)
   - [9.1 Evaluation](#91-evaluation)
   - [9.2 Numerical Derivatives](#92-numerical-derivatives)
   - [9.3 Numerical Integration](#93-numerical-integration)
   - [9.4 Equation Solving](#94-equation-solving)
   - [9.5 Nonlinear System Solver](#95-nonlinear-system-solver)
   - [9.6 Extremum Finder](#96-extremum-finder)
   - [9.7 Limit Computation](#97-limit-computation)
   - [9.8 Auto Root Scanner](#98-auto-root-scanner)
   - [9.9 Curve Intersection Finder](#99-curve-intersection-finder)
   - [9.10 Arc Length](#910-arc-length)
   - [9.11 Area Between Curves](#911-area-between-curves)
 10. [Tangent & Normal Lines](#10-tangent--normal-lines)
 11. [Taylor Series Expansion](#11-taylor-series-expansion)
  12. [ODE Solver (RK4)](#12-ode-solver-rk4)
  13. [Vector Field Plotter](#vector-field-plotter)
  14. [Fourier Transform & Spectrum Analysis](#13-fourier-transform--spectrum-analysis)
 14. [Statistics Calculator](#14-statistics-calculator)
 15. [Statistical Distribution Calculator](#15-statistical-distribution-calculator)
 16. [Curve Fitting / Regression](#16-curve-fitting--regression)
 17. [Matrix Operations (Linear Algebra)](#17-matrix-operations-linear-algebra)
 18. [Complex Number Calculator](#18-complex-number-calculator)
 19. [Unit Converter](#19-unit-converter)
 20. [Number Theory Calculator](#20-number-theory-calculator)
 21. [Function Table & CSV Export](#21-function-table--csv-export)
 22. [Quick Input Panel](#22-quick-input-panel)
 23. [Language Switching (Chinese/English)](#23-language-switching-chineseenglish)
 24. [Android-Specific Guide](#24-android-specific-guide)
 25. [FAQ](#25-faq)

---

## 1. Installation & Getting Started

### 1.1 Windows Users

**Easiest way — Download the EXE (no Python needed):**

1. Open your browser and go to the [Releases page](https://github.com/Hotsteel2901/SuperCalculator/releases)
2. Find the latest version and click `SuperCalculator.exe` to download
3. Once downloaded, **double-click** `SuperCalculator.exe` to run
4. A console window will open (for debug output) along with the calculator GUI
5. Start using it!

> 💡 **Tip:** The EXE is self-contained — no Python or other dependencies needed. Just double-click and go.

### 1.2 Running from Python Source

**If you have Python installed, you can run from source:**

**Step 1: Make sure Python is installed**

Open a terminal (Windows: press `Win + R`, type `cmd`, press Enter), and type:

```bash
python --version
```

If it shows `Python 3.9.x` or higher, you're good. If not, download Python 3.9+ from [python.org](https://www.python.org/downloads/).

**Step 2: Install dependencies**

In the terminal, type:

```bash
pip install numpy matplotlib
```

Wait for installation to complete (usually 1-2 minutes).

**Step 3: Run the program**

Navigate to the SuperCalculator directory and run:

```bash
cd /path/to/SuperCalculator
python super_calc_bridged.py
```

The program auto-detects your system language. Chinese systems show Chinese UI, English systems show English UI.

### 1.3 Android Users

**Installation steps:**

1. Open your phone's browser and go to the [Releases page](https://github.com/Hotsteel2901/SuperCalculator/releases)
2. Find `SuperCalculator-aarch64.apk` and tap to download
3. Once downloaded, tap the APK file to install
4. If prompted about "unknown sources", allow installation in Settings (varies by device)
5. After installation, find **SuperCalculator** in your app list and tap to open

> ⚠️ **Note:** Android version requires Android 7.0 (API 24) or higher.

### 1.4 macOS / Linux Users

**Compile the C core library from source:**

```bash
# macOS
gcc -shared -O2 -fPIC -o calc_core.dylib calc_core.c -lm

# Linux
gcc -shared -O2 -fPIC -o calc_core.so calc_core.c -lm
```

Then install Python dependencies and run:

```bash
pip install numpy matplotlib
python super_calc_bridged.py
```

---

## 2. Interface Overview

After launching, you'll see the main interface with these sections:

```
+------------------------------------------+
|  Super Function Graphing Calculator       |
+------------------------------------------+
|  [Expression Input Box]  [Preset Dropdown]|
|                                          |
|  [Quick Input Panel]                     |
|  [Function Buttons: sin, cos, ln, sqrt...]|
|                                          |
|  [Action Buttons Area]                   |
|  - Derivative / Integral / Solve / ...   |
|                                          |
|  [Results Area]                          |
|                                          |
|  [Plot Area]  (appears after plotting)   |
+------------------------------------------+
```

**Interface Elements:**

- **Expression Input Box**: Where you type math expressions, e.g., `sin(x)` or `x^2`
- **Preset Dropdown**: Built-in common functions — click to select and auto-fill
- **Quick Input Panel**: Popup keypad for fast operator/function entry
- **Action Buttons**: Choose the calculation you need
- **Results Area**: Displays computation results
- **Plot Area**: Shows the rendered function graph

---

## 3. Expression Syntax

### 3.1 Basic Arithmetic

| Operation | Symbol | Example | Notes |
|-----------|--------|---------|-------|
| Addition | `+` | `x + 1` | — |
| Subtraction | `-` | `x - 3` | — |
| Multiplication | `*` | `2 * x` | ⚠️ Must write `*`, cannot omit |
| Division | `/` | `x / 2` | — |
| Power | `^` | `x^2` | x squared |
| Parentheses | `()` | `(x+1)^2` | Override precedence |

**Example expressions:**
- `x^2 + 2*x - 1` → Quadratic function
- `sin(x) + cos(x)` → Trigonometric
- `sqrt(x^2 + 1)` → Composite function

### 3.2 Supported Functions

| Function | Description | Example |
|----------|-------------|---------|
| `sin(x)` | Sine | `sin(x)` |
| `cos(x)` | Cosine | `cos(x)` |
| `tan(x)` | Tangent | `tan(x)` |
| `ln(x)` | Natural log (base e) | `ln(x)` |
| `log(x)` | Logarithm | `log(x)` |
| `exp(x)` | Exponential e^x | `exp(-x^2)` |
| `sqrt(x)` | Square root | `sqrt(x)` |
| `abs(x)` | Absolute value | `abs(x)` |
| `floor(x)` | Round down | `floor(x)` |
| `ceil(x)` | Round up | `ceil(x)` |

### 3.3 Constants

| Constant | Value | Example |
|----------|-------|---------|
| `pi` | π ≈ 3.14159... | `sin(pi * x)` |
| `e` | e ≈ 2.71828... | `exp(x)` = `e^x` |

### 3.4 Complex Numbers

Use `i` for the imaginary unit:
- `1+2i` → Complex number 1+2i
- `3-4i` → Complex number 3-4i
- `abs(3+4i)` → 5 (magnitude)

### 3.5 Factorial & Modulo

- **Factorial** (postfix `!`): `5!` = 120, `x!` (x must be non-negative integer)
- **Modulo** (remainder): `10 mod 3` = 1, `7 % 2` = 1

---

## 4. Function Plotting

### 4.1 Basic 2D Function Plotting

**Steps:**

1. Type a function in the expression input box, e.g., `sin(x)`
2. Click the **"Plot"** button
3. The function curve appears in the plot area

**Example: Plot a sine function**

```
Input: sin(x)
Click: Plot
```

You'll see a beautiful sine wave in the plot area.

**Example: Plot a quadratic function**

```
Input: x^2 - 2*x + 1
Click: Plot
```

**Example: Plot a Gaussian**

```
Input: exp(-x^2)
Click: Plot
```

### 4.2 Multi-Curve Overlay

**Plot multiple curves simultaneously:**

1. Type multiple expressions separated by **semicolons** `;`
2. Example: `sin(x);cos(x);tan(x)/3`
3. Click Plot — three curves appear in different colors

> 💡 **Tip:** You can also plot one curve, then modify the expression and plot again — they'll overlay.

### 4.3 Coordinate Marking

**Mark points on the curve:**

1. **Left-click** on the plot area → marks the point's coordinates
2. **Right-click** → deletes the nearest marked point
3. You can also enter a specific x value to auto-locate and mark the corresponding point

### 4.4 Customizing View Range

**Adjust axis ranges:**

In the interface, find the X/Y range settings:
- **X min / X max**: Adjust horizontal range
- **Y min / Y max**: Adjust vertical range
- **Step size**: Controls curve smoothness (smaller = smoother but slower)

**Example:** To see `sin(x)` from 0 to 4π:
- Set X min to `0`
- Set X max to `12.57` (≈ 4π)

### 4.5 Using Preset Functions

The program includes 21 built-in functions:

| Category | Preset Examples |
|----------|----------------|
| Basic | `sin(x)`, `cos(x)`, `tan(x)`, `x^2`, `1/x` |
| Exponential/Log | `exp(x)`, `ln(x)` |
| 3D | `sin(x)*cos(y)`, `x^2+y^2` |
| FFT | `sin(2*pi*x)+0.5*sin(6*pi*x)` |

**How to use:** Click the preset dropdown and select a function.

### 4.6 Parameter System

If your expression contains extra letter variables (like `a`, `b`, `k`), the program auto-detects them and pops up parameter input fields.

**Example:** Enter `a*sin(b*x) + c`

The program shows three input fields:
- Value of `a`
- Value of `b`
- Value of `c`

You can modify parameters in real-time and the curve updates dynamically!

### 4.7 Custom Function Definition

Define your own named functions that can be referenced in any expression.

**Steps:**

1. Enter a function name (e.g., `f`) in the name field
2. Enter a function body expression using `x` as the variable (e.g., `x^2 + 1`)
3. Click **"Define"**
4. The function is now available for use anywhere

**Using custom functions:**

After defining `f(x) = x^2 + 1`, you can:
- Evaluate: `f(2)` → 5
- Plot: enter `f(x)` and click Plot
- Compose: `f(sin(x))` → sin²(x) + 1
- Chain: `f(f(x))` → (x²+1)² + 1

**Management:**

- **Delete**: Enter a function name and click "Delete" to remove it
- **Clear All**: Click "Clear" to remove all custom functions
- **List**: All defined functions are shown in the list area

**Rules:**

- Function names must start with a letter and contain only letters and digits
- Maximum 64 custom functions
- Function body can use any valid expression including built-in functions and constants
- Re-defining the same name updates the existing function

### 4.8 Calculation History

The calculator automatically records your most recent 10 calculations.

**Features:**

- **Automatic recording**: Each time you evaluate an expression, compute a derivative, integrate, solve an equation, or find an extremum, the calculation is recorded
- **History display**: The history list shows recent calculations in the format `expression = result`
- **Clear history**: Click "Clear History" to remove all recorded calculations
- **Use last expression**: Click "Use Last Expression" to load the most recent expression into the input field
- **Export history CSV**: Click "Export CSV" to export all history entries as a CSV file with columns: index, expression, result
- **Persistence (Android)**: History is saved using SharedPreferences and persists across app restarts

**Supported operations:**

- Expression evaluation
- First and second derivatives
- Definite integration
- Equation solving (Newton and Bisection methods)
- Extremum finding (minimum/maximum)

---

## 5. 3D Function Plotting

**Steps:**

1. Enter an expression with both `x` and `y`, e.g., `sin(x)*cos(y)`
2. Click the **"3D Plot"** button
3. A new 3D plot window opens

**Example: Plot a cone**

```
Input: sqrt(x^2 + y^2)
Click: 3D Plot
```

**Example: Plot a saddle surface**

```
Input: x^2 - y^2
Click: 3D Plot
```

**Example: Plot a hemisphere**

```
Input: sqrt(9 - x^2 - y^2)
Click: 3D Plot
```

**Interaction:**
- 🖱️ **Mouse drag**: Rotate the 3D view
- 🔄 **Scroll wheel**: Zoom in/out
- 📐 Adjustable X/Y/Z ranges and step size

> 📱 **Android users:** Use finger touch to rotate the 3D graph — very intuitive!

---

## 6. Parametric Curve Plotting

Parametric curves use parameter `t` to define x and y coordinates.

**Steps:**

1. Enter x(t) and y(t) expressions
2. Click the **"Parametric Plot"** button

**10 Built-in Presets:**

| Name | x(t) | y(t) | Description |
|------|------|------|-------------|
| Circle | `cos(t)` | `sin(t)` | Standard unit circle |
| Ellipse | `2*cos(t)` | `sin(t)` | Stretched in x |
| Lissajous | `sin(3*t)` | `cos(5*t)` | Classic physics figure |
| Spiral | `t*cos(t)` | `t*sin(t)` | Archimedean spiral |
| Cardioid | `16*sin(t)^3` | `13*cos(t)-5*cos(2t)-2*cos(3t)-cos(4t)` | Heart shape |
| Butterfly | `sin(t)*(e^cos(t)-2*cos(4t)-sin(t/12)^5)` | `cos(t)*(e^cos(t)-2*cos(4t)-sin(t/12)^5)` | Nature curve |

**Example: Draw an ellipse manually**

```
x(t) = 3*cos(t)
y(t) = 2*sin(t)
Parameter range: 0 to 2*pi
```

---

## 7. Polar Coordinate Plotting

Polar curves use angle `theta` (θ) to define the curve.

**Steps:**

1. Enter r(theta) expression
2. Click the **"Polar Plot"** button

**12 Built-in Presets:**

| Name | r(theta) | Description |
|------|----------|-------------|
| Cardioid | `1 - sin(theta)` | Classic heart shape |
| Rose (4-leaf) | `cos(2*theta)` | Four-leaf clover |
| Clover | `cos(3*theta)` | Three-leaf flower |
| Lemniscate | `sqrt(cos(2*theta))` | ∞ shape |
| Archimedean Spiral | `theta / (2*pi)` | Spiral outward |

**Example: Draw a 4-leaf rose**

```
Input: cos(2*theta)
Click: Polar Plot
```

---

## 8. Implicit Function Plotting

Implicit curves plot equations of the form **f(x,y) = 0** (e.g., circles, ellipses, hyperbolas, cardioids).

**How to use:**

1. Check **"Enable implicit curve"**
2. Enter an expression using both `x` and `y` (e.g., `x^2+y^2-1`)
3. Adjust the resolution (default 200)
4. Click **"+ Add Curve"** or **"Plot"**

**Built-in Presets:**
- Circle: `x^2+y^2-1`
- Ellipse: `x^2/4+y^2-1`
- Hyperbola: `x^2-y^2-1`
- Parabola: `y-x^2`
- Lemniscate: `(x^2+y^2)^2-(x^2-y^2)`
- Cardioid: `(x^2+y^2-x)^2-(x^2+y^2)`
- Folium: `x^3+y^3-3*x*y`
- Cubic: `y^2-x^3+x`

**Example: Draw a circle**

```
Check "Enable implicit curve"
Input: x^2+y^2-1
Click: Plot
```

**Example: Draw a cardioid**

```
Check "Enable implicit curve"
Input: (x^2+y^2-x)^2-(x^2+y^2)
Click: Plot
```

### 8.1 Contour Plot (Level Sets)

Contour plots visualize level curves **f(x,y) = c** for arbitrary expressions, showing multiple contour lines at different values of c.

**How to use:**

1. Enter an expression using both `x` and `y` (e.g., `x^2+y^2`)
2. Adjust resolution (10-100, default 40)
3. Adjust number of contour levels (2-30, default 12)
4. Click **"Plot Contour"** for line contours or **"Filled Contour"** for filled regions

**Built-in Presets:**
- Circle: `x^2+y^2-1`
- Paraboloid: `x^2+y^2`
- Saddle: `x^2-y^2`
- Gaussian: `exp(-(x^2+y^2))`

**Example: Gaussian contour plot**

```
Input: exp(-(x^2+y^2))
Resolution: 40
Levels: 12
Click: Plot Contour
```

---

## 24. Numerical Computation

### 9.1 Evaluation

**Evaluate function at a specific point:**

1. Enter expression, e.g., `sin(x)`
2. Enter x value, e.g., `1.57` (≈ π/2)
3. Click **"Evaluate"**
4. Result: approximately `1.0`

### 9.2 Numerical Derivatives

**Compute first derivative f'(x):**

1. Enter expression, e.g., `x^3`
2. Enter x value, e.g., `2`
3. Click **"1st Derivative"**
4. Result: approximately `12.0` (since 3x² at x=2 = 12)

**Compute second derivative f''(x):**

1. Enter same expression and x value
2. Click **"2nd Derivative"**
3. Result: approximately `12.0` (since 6x at x=2 = 12)

**Compute nth-order derivative:**

1. Enter expression and x value
2. Enter order (e.g., 5)
3. Click **"nth Derivative"**

### 9.3 Numerical Integration

**Compute definite integral ∫f(x)dx:**

1. Enter integrand, e.g., `x^2`
2. Enter lower bound a = `0`
3. Enter upper bound b = `1`
4. Click **"Integrate"**
5. Result: approximately `0.333` (= 1/3)

**Example: Compute ∫sin(x)dx from 0 to π**

```
Expression: sin(x)
Lower: 0
Upper: 3.14159
Result: approximately 2.0
```

### 9.4 Equation Solving

**Find root of f(x) = 0:**

1. Enter equation expression, e.g., `x^2 - 4` (solving x² - 4 = 0)
2. Enter initial guess or search range
3. Click **"Solve"**
4. Result: `2.0` (or `-2.0` depending on guess)

**Example: Solve sin(x) = 0.5**

```
Expression: sin(x) - 0.5
Initial guess: 1
Result: approximately 0.524 (= π/6)
```

### 9.5 Nonlinear System Solver

**Solve a system of two equations:**

For example:
- f(x,y) = x² + y² - 1 = 0 (unit circle)
- g(x,y) = x - y = 0 (line y=x)

1. Enter first equation: `x^2 + y^2 - 1`
2. Enter second equation: `x - y`
3. Enter initial guess (x0, y0) = `(0.7, 0.7)`
4. Click **"Solve System"**
5. Result: x ≈ 0.7071, y ≈ 0.7071

### 9.6 Extremum Finder

**Find local minimum:**

1. Enter expression, e.g., `x^2 - 4*x + 3`
2. Enter search interval, e.g., `[-5, 5]`
3. Click **"Find Minimum"**
4. Result: approximately `2.0` (minimum value -1 at x=2)

**Find local maximum:**

1. Enter expression, e.g., `sin(x)`
2. Enter search interval, e.g., `[0, 6]`
3. Click **"Find Maximum"**
4. Result: approximately `1.571` (≈ π/2, where sin reaches max)

### 9.7 Limit Computation

**Compute two-sided limit:**

1. Enter expression, e.g., `sin(x)/x`
2. Enter the point approached, e.g., `0`
3. Click **"Limit"**
4. Result: approximately `1.0`

**Compute left-hand limit:**

```
Expression: 1/x
Point: 0
Click: Left Limit
Result: -inf (negative infinity)
```

**Compute right-hand limit:**

```
Expression: 1/x
Point: 0
Click: Right Limit
Result: +inf (positive infinity)
```

### 9.8 Auto Root Scanner

**Automatically find all roots in an interval:**

1. Enter expression, e.g., `sin(x)`
2. Enter scan interval, e.g., `[0, 10]`
3. Click **"Scan Roots"**
4. Program finds all points where f(x) = 0

**Example:** Scan `sin(x)` on `[0, 10]`:
- Results: 0, 3.1416, 6.2832, 9.4248 (i.e., 0, π, 2π, 3π)

### 9.9 Curve Intersection Finder

**Find all intersection points of two curves:**

1. Enter first curve, e.g., `sin(x)`
2. Enter second curve, e.g., `cos(x)`
3. Enter search interval, e.g., `[0, 6]`
4. Click **"Find Intersections"**
5. Intersections are annotated on the plot

**Example:** `sin(x)` and `cos(x)` on `[0, 6]`:
- Results: x ≈ 0.785 (= π/4) and x ≈ 3.927 (= 5π/4)

### 9.10 Arc Length

**Compute arc length of a curve:**

1. Enter curve expression, e.g., `sin(x)`
2. Enter interval `[a, b]`, e.g., `[0, π]`
3. Click **"Arc Length"**
4. Result: approximately `3.820`

### 9.11 Area Between Curves

**Compute enclosed area between two curves:**

1. Enter first curve f(x), e.g., `sin(x)`
2. Enter second curve g(x), e.g., `0` (x-axis)
3. Enter interval `[a, b]`, e.g., `[0, π]`
4. Click **"Area Between Curves"**
5. Result: approximately `2.0`

---

## 24. Tangent & Normal Lines

**Draw tangent and normal lines at a point on the curve:**

1. Enter curve expression, e.g., `x^2`
2. Enter x coordinate, e.g., `1`
3. Click **"Tangent/Normal"**
4. The plot shows:
   - Solid line: original curve
   - Dashed line 1: tangent (slope = f'(1) = 2)
   - Dashed line 2: normal (slope = -1/f'(1) = -0.5)

**Purpose:** Analyze local behavior of the function, visually understand the geometric meaning of derivatives.

---

## 24. Taylor Series Expansion

**Expand a function into a Taylor polynomial:**

1. Enter function expression, e.g., `sin(x)`
2. Choose expansion point (center), e.g., `0` (Maclaurin series)
3. Choose expansion order, e.g., `6`
4. Click **"Taylor Expand"**
5. Displayed:
   - Coefficients for each order
   - Taylor polynomial expression
   - Comparison plot: Taylor approximation vs. original function

**Example:** sin(x) expanded at x=0 to order 6:

```
Coefficients: [0, 1, 0, -0.1667, 0, 0.00833, 0]
Polynomial: x - x³/6 + x⁵/120
```

**Purpose:** Understand local approximations, verify Taylor's theorem.

---

## 24. ODE Solver (RK4)

**Solve first-order ODE initial value problems:**

Equation form: dy/dx = f(x,y), with y(x₀) = y₀

**Steps:**

1. Enter the right-hand side expression, e.g., `-y` (solving dy/dx = -y)
2. Enter initial conditions: x₀ = `0`, y₀ = `1`
3. Enter end point: x_end = `5`
4. Enter number of steps (precision): n_steps = `200`
5. Click **"Solve ODE"**
6. Solution curve is displayed

**Example: Solve dy/dx = -y, y(0) = 1**

```
Expression: -y
x₀ = 0, y₀ = 1
x_end = 5, n_steps = 200
Result: Numerical solution of y = e^(-x)
```

---

## Vector Field Plotter

**Visualize 2D autonomous systems dx/dt=P(x,y), dy/dt=Q(x,y):**

**Steps (Android):**

1. Enter P(x,y) expression, e.g., `y` (for dx/dt = y)
2. Enter Q(x,y) expression, e.g., `-x` (for dy/dt = -x)
3. Set grid size (3-40) and x/y ranges
4. Optionally enter initial conditions: `x0,y0; x1,y1; ...`
5. Click **"Plot Vector Field"** for arrows only, or **"Solve & Plot"** to include solution curves

**Steps (Python/Desktop):**

1. Navigate to the Vector Field section
2. Enter P(x,y) and Q(x,y) expressions
3. Use preset dropdown for common systems (Harmonic oscillator, Predator-Prey, etc.)
4. Set grid and ranges
5. Click **"Plot Vector Field"** or **"Solve & Plot"**

**Example: Harmonic Oscillator (dx/dt = y, dy/dt = -x)**

```
P(x,y) = y
Q(x,y) = -x
Grid: 14, Range: [-5,5] × [-5,5]
Result: Circular vector field showing oscillatory motion
```

---

## Fourier Transform & Spectrum Analysis

**Perform FFT spectrum analysis on a function:**

1. Enter signal expression, e.g., `sin(2*pi*x) + 0.5*sin(6*pi*x)`
2. Enter analysis interval, e.g., `[0, 2]`
3. Enter number of sample points, e.g., `1024` (larger = more precise)
4. Click **"FFT Analysis"**
5. Displayed:
   - **Amplitude spectrum**: Strength of each frequency component
   - **Phase spectrum**: Phase of each frequency component
   - **Dominant frequency**: Auto-detected strongest frequency

**Example:** Analyze `sin(2*pi*x) + 0.5*sin(6*pi*x)`

```
Results:
- Dominant freq 1: 1 Hz, amplitude = 1.0
- Dominant freq 2: 3 Hz, amplitude = 0.5
```

**Export:** Spectrum data can be exported to CSV.

---

## 24. Statistics Calculator

**Enter a dataset and compute statistics:**

**Steps:**

1. In the data input field, enter values (comma-separated), e.g., `1, 2, 3, 4, 5, 6, 7, 8, 9, 10`
2. Click **"Calculate Statistics"**
3. Results displayed:

| Statistic | Value |
|-----------|-------|
| Mean | 5.5 |
| Median | 5.5 |
| Mode | None (each value appears once) |
| Variance | 8.25 |
| Std Dev | 2.872 |
| Q1 (25%) | 3.0 |
| Q3 (75%) | 8.0 |
| IQR | 5.0 |
| Min | 1 |
| Max | 10 |
| Range | 9 |

**Extra features:**
- **Sort data**: Click sort button to arrange from smallest to largest
- **Histogram**: Visualize data distribution
- **CSV export**: Export statistics to CSV file
- **Copy to clipboard**: Copy result text

---

## 24. Statistical Distribution Calculator

**Compute values for probability distributions:**

6 distributions supported:

| Distribution | Parameters | Use Case |
|-------------|------------|----------|
| Normal | μ (mean), σ (std dev) | Most common in nature |
| Student's t | ν (degrees of freedom) | Small-sample inference |
| Chi-squared | k (degrees of freedom) | Hypothesis testing |
| F | d1, d2 (degrees of freedom) | ANOVA |
| Binomial | n (trials), p (probability) | Success/failure experiments |
| Poisson | λ (average rate) | Rare event counting |

**Steps:**

1. Select distribution type
2. Enter distribution parameters
3. Choose calculation type:
   - **PDF/PMF**: Probability density/mass function
   - **CDF**: Cumulative distribution function
   - **PPF**: Inverse CDF (find quantile from probability)
4. Enter variable value (or probability)
5. Click **"Calculate"**

**Example: Find 95% confidence interval for standard normal**

```
Distribution: Normal
μ = 0, σ = 1
Calculate PPF(0.975)
Result: approximately 1.96
```

---

## 24. Curve Fitting / Regression

**Perform regression analysis on a dataset:**

5 fitting models supported:

| Model | Formula | When to Use |
|-------|---------|-------------|
| Linear | y = ax + b | Linear relationship |
| Polynomial | y = aₙxⁿ + ... + a₁x + a₀ | Nonlinear trend |
| Exponential | y = a·e^(bx) | Growth/decay |
| Power | y = a·x^b | Power law |
| Logarithmic | y = a + b·ln(x) | Logarithmic growth |

**Steps:**

1. Enter x data (comma-separated): `1, 2, 3, 4, 5`
2. Enter y data (comma-separated): `2, 4, 5, 4, 5`
3. Select fitting model
4. Click **"Fit"**
5. Displayed:
   - Fitting equation
   - R² goodness-of-fit (closer to 1 = better)
   - Scatter plot + fitted curve

**Example: Linear regression**

```
x: 1, 2, 3, 4, 5
y: 2, 4, 5, 4, 5
Result: y = 0.6x + 2.2, R² = 0.739
```

**Export:** Regression data (x, y) can be exported to CSV.

---

## 24. Matrix Operations (Linear Algebra)

**Input format:** Rows separated by `;`, columns by `,`

Example: 2×2 matrix `[[1, 2], [3, 4]]` is entered as: `1,2;3,4`

**Supported operations:**

| Operation | Description | Example |
|-----------|-------------|---------|
| Addition | A + B | `1,2;3,4` + `5,6;7,8` |
| Subtraction | A - B | `1,2;3,4` - `5,6;7,8` |
| Multiplication | A × B | `1,2;3,4` × `5,6;7,8` |
| Determinant | det(A) | `1,2;3,4` → -2 |
| Inverse | A⁻¹ | `1,2;3,4` → `-2, 1; 1.5, -0.5` |
| Transpose | A^T | `1,2;3,4` → `1,3;2,4` |
| Rank | rank(A) | `1,2;3,4` → 2 |
| RREF | Row echelon form | Gaussian elimination |
| Eigenvalues | eig(A) | Solve characteristic equation |

**Example: Find determinant and inverse of a 2×2 matrix**

```
Matrix: 1,2;3,4
Determinant: 1×4 - 2×3 = -2
Inverse: -2, 1; 1.5, -0.5
```

---

## 24. Complex Number Calculator

**Complex number operations:**

1. Select **"Complex Calculator"** mode
2. Enter complex expression

**Supported operations:**

| Operation | Example | Result |
|-----------|---------|--------|
| Addition | `(1+2i) + (3+4i)` | `4+6i` |
| Subtraction | `(1+2i) - (3+4i)` | `-2-2i` |
| Multiplication | `(1+2i) * (3+4i)` | `-5+10i` |
| Division | `(1+2i) / (3+4i)` | `0.44+0.08i` |
| Power | `(1+2i)^2` | `-3+4i` |
| Sine | `sin(1+2i)` | Complex sine |
| Exponential | `exp(1+2i)` | Complex exponential |
| Absolute value | `abs(3+4i)` | `5` |
| Conjugate | `conj(1+2i)` | `1-2i` |

---

## 24. Unit Converter

**9 unit categories supported:**

| Category | Example Units |
|----------|---------------|
| Length | meter, cm, mm, km, inch, foot, mile |
| Weight | kg, gram, pound, ounce |
| Temperature | Celsius, Fahrenheit, Kelvin |
| Area | m², km², hectare, acre |
| Volume | liter, mL, m³, gallon |
| Time | second, minute, hour, day |
| Data Storage | byte, KB, MB, GB, TB |
| Speed | m/s, km/h, mph |
| Angle | degree, radian |

**Steps:**

1. Select unit category
2. Enter value
3. Select source unit and target unit
4. Click **"Convert"**

**Example:** Convert 100 Fahrenheit to Celsius

```
Category: Temperature
Value: 100
From: Fahrenheit
To: Celsius
Result: 37.78°C
```

---

## 24. Number Theory Calculator

**Supported functions:**

| Function | Description | Example |
|----------|-------------|---------|
| Factorization | Prime factorization | 12 → 2² × 3 |
| Primality test | Check if prime | 7 → is prime |
| GCD | Greatest common divisor | GCD(12, 18) = 6 |
| LCM | Least common multiple | LCM(12, 18) = 36 |
| Fibonacci | Fibonacci sequence | First 10: 1,1,2,3,5,8,13,21,34,55 |
| Modular exponentiation | a^b mod m | 2^10 mod 1000 = 24 |
| Euler's totient | φ(n) | φ(12) = 4 |

**Example: Factorize 360**

```
Input: 360
Result: 2³ × 3² × 5
```

---

## 24. Function Table & CSV Export

**Generate x-f(x) data table:**

1. Enter function expression
2. Enter interval `[a, b]`
3. Enter number of data points
4. Click **"Generate Table"**
5. x and f(x) values displayed in table format

**Export options:**
- **CSV export**: Save as .csv file
- **Copy to clipboard**: Paste directly into Excel or other software

**Web landing page:** The [project landing page](../index.html) also supports CSV export — export data points and trendline predictions from the Data Import & Scatter Plot section, and export interpolated curve data from the Interpolation section.

---

## 24. Quick Input Panel

Click the **"Quick Input"** button to open a popup keypad:

```
+---+---+---+---+---+
| 7 | 8 | 9 | ( | ) |
+---+---+---+---+---+
| 4 | 5 | 6 | + | - |
+---+---+---+---+---+
| 1 | 2 | 3 | * | / |
+---+---+---+---+---+
| 0 | . | x | ^ | ! |
+---+---+---+---+---+
| sin | cos | ln | sqrt | pi |
+---+---+---+---+---+
```

Click any button to insert the corresponding character into the expression input box.

---

## 24. Language Switching (Chinese/English)

**Desktop:**

- **Auto-detection**: Program detects system language at startup
- **Manual override**: Set environment variable `SUPERCALC_LANG=zh` for Chinese, or `SUPERCALC_LANG=en` for English

```bash
# Force Chinese
SUPERCALC_LANG=zh python super_calc_bridged.py

# Force English
SUPERCALC_LANG=en python super_calc_bridged.py
```

**Android:**

- Follows system language automatically
- System language Chinese → Chinese UI; English → English UI

---

## 24. Android-Specific Guide

### 23.1 Main Interface (CalcActivity)

- **Expression input**: Top input box
- **Action buttons**: Button area below
- **Results display**: Results shown below buttons
- **Navigation menu**: Jump to 2D plot, 3D plot, etc.

### 23.2 2D Function Plotting (PlotActivity)

- Enter expression, tap **"Plot"** button
- Chart supports:
  - **Pinch to zoom**: Zoom in/out
  - **Single-finger drag**: Pan the graph
  - **Fullscreen mode**: Tap fullscreen button

### 23.3 3D Function Plotting (Plot3DActivity)

- Enter expression with x and y
- Tap **"3D Plot"** button
- **Touch controls**:
  - **Single-finger drag**: Rotate 3D view
  - **Pinch to zoom**: Scale the graph
  - **Fullscreen mode**: Tap fullscreen button

### 23.4 Fullscreen Mode

- Tap fullscreen button in 2D or 3D plot screen
- All UI elements hidden, only the graph shown
- Tap again to return to normal mode

### 23.5 Statistical Distribution Calculator (StatDistCalc)

- Enter from main menu
- Select distribution type
- Input parameters
- Tap calculate to see results and graph

---

## 24. FAQ

### Q1: Program says calc_core.dll / .so not found

**A:** The C core library isn't compiled. Steps:

1. Make sure GCC is installed
2. Run the compile command in the project root (see "Building from Source" above)
3. Re-run the Python program

### Q2: Curve doesn't appear when plotting

**A:** Possible causes:
- Expression syntax error (e.g., missing `*` sign)
- Y range too small — curve is outside view
- Try adjusting X/Y ranges

### Q3: Equation solving fails

**A:** Possible causes:
- Initial guess too far from the root
- No root exists in that interval
- Try a different initial value or wider search range

### Q4: 3D plotting is laggy

**A:** Try:
- Increase step size (e.g., from 0.01 to 0.05)
- Reduce X/Y range
- Disable grid display

### Q5: APK installation fails on Android

**A:** Possible causes:
- System version below Android 7.0
- "Unknown sources" not enabled
- APK file didn't download completely

---

## Navigation

- [Back to README (English)](../README.md)
- [Back to Chinese README](../README_CN.md)
- [Chinese Usage Guide](usage_cn.md)

---

> 📝 This guide is continuously updated. For issues, visit [GitHub Issues](https://github.com/Hotsteel2901/SuperCalculator/issues).
