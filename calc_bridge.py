"""
Super Calculator - Python Bridge Layer

Uses ctypes to call the C core dynamic library (calc_core.dll/.so).
This is the Bridge in the Bridge Pattern, decoupling the GUI from C.
"""

import ctypes
import os
import sys
import math as _math
from typing import List, Optional

# ---------------------------------------------------------------------------
#  Library loading
# ---------------------------------------------------------------------------

def _find_lib() -> str:
    """Locate the compiled shared library next to this file."""
    base = os.path.dirname(os.path.abspath(__file__))

    def _try_find(names):
        for n in names:
            p = os.path.join(base, n)
            if os.path.exists(p):
                return p
        return None

    if sys.platform == "win32":
        names = ["calc_core.dll"]
    elif sys.platform == "darwin":
        import platform
        arch = platform.machine()
        if arch in ("x86_64", "AMD64"):
            names = ["calc_core_x86_64.dylib", "calc_core.dylib"]
        elif arch in ("aarch64", "arm64"):
            names = ["calc_core_aarch64.dylib", "calc_core_arm64.dylib", "calc_core.dylib"]
        else:
            names = ["calc_core.dylib"]
    else:
        import platform
        arch = platform.machine()
        if arch in ("x86_64", "AMD64"):
            names = ["calc_core_x86_64.so", "calc_core.so"]
        elif arch in ("aarch64", "arm64"):
            names = ["calc_core_aarch64.so", "calc_core.so"]
        else:
            names = ["calc_core.so"]

    path = _try_find(names)
    if path is None:
        raise FileNotFoundError(
            f"C library not found. Searched for: {', '.join(names)}\n"
            f"Compile it first: gcc -shared -O2 -fPIC -o calc_core.so calc_core.c -lm"
        )
    return path

try:
    _lib = ctypes.CDLL(_find_lib())
except Exception as e:
    raise RuntimeError(f"Failed to load C core library: {e}") from e

# ---------------------------------------------------------------------------
#  Function signatures
# ---------------------------------------------------------------------------

_lib.evaluate.argtypes = [ctypes.c_char_p, ctypes.c_double]
_lib.evaluate.restype = ctypes.c_double

_lib.evaluate_xy.argtypes = [ctypes.c_char_p, ctypes.c_double, ctypes.c_double]
_lib.evaluate_xy.restype = ctypes.c_double

_lib.evaluate_array.argtypes = [ctypes.c_char_p,
                                 ctypes.POINTER(ctypes.c_double),
                                 ctypes.POINTER(ctypes.c_double),
                                 ctypes.c_int]
_lib.evaluate_array.restype = None

_lib.evaluate_xy_array.argtypes = [ctypes.c_char_p,
                                     ctypes.POINTER(ctypes.c_double),
                                     ctypes.POINTER(ctypes.c_double),
                                     ctypes.POINTER(ctypes.c_double),
                                     ctypes.c_int]
_lib.evaluate_xy_array.restype = None

_lib.derivative.argtypes = [ctypes.c_char_p, ctypes.c_double, ctypes.c_double]
_lib.derivative.restype = ctypes.c_double

_lib.derivative2.argtypes = [ctypes.c_char_p, ctypes.c_double, ctypes.c_double]
_lib.derivative2.restype = ctypes.c_double

_lib.integrate.argtypes = [ctypes.c_char_p, ctypes.c_double, ctypes.c_double, ctypes.c_int]
_lib.integrate.restype = ctypes.c_double

_lib.integrate_adaptive.argtypes = [ctypes.c_char_p, ctypes.c_double,
                                     ctypes.c_double, ctypes.c_double]
_lib.integrate_adaptive.restype = ctypes.c_double

_lib.solve_equation.argtypes = [ctypes.c_char_p, ctypes.c_double, ctypes.c_double,
                                 ctypes.c_double, ctypes.c_double, ctypes.c_int]
_lib.solve_equation.restype = ctypes.c_double

_lib.solve_bisection.argtypes = [ctypes.c_char_p, ctypes.c_double, ctypes.c_double,
                                   ctypes.c_double, ctypes.c_int]
_lib.solve_bisection.restype = ctypes.c_double

_lib.find_minimum.argtypes = [ctypes.c_char_p, ctypes.c_double, ctypes.c_double,
                               ctypes.c_double, ctypes.c_int]
_lib.find_minimum.restype = ctypes.c_double

_lib.find_maximum.argtypes = [ctypes.c_char_p, ctypes.c_double, ctypes.c_double,
                               ctypes.c_double, ctypes.c_int]
_lib.find_maximum.restype = ctypes.c_double

_lib.limit_left.argtypes = [ctypes.c_char_p, ctypes.c_double, ctypes.c_int]
_lib.limit_left.restype = ctypes.c_double

_lib.limit_right.argtypes = [ctypes.c_char_p, ctypes.c_double, ctypes.c_int]
_lib.limit_right.restype = ctypes.c_double

_lib.limit.argtypes = [ctypes.c_char_p, ctypes.c_double, ctypes.c_double, ctypes.c_int]
_lib.limit.restype = ctypes.c_double

_lib.get_last_error.argtypes = []
_lib.get_last_error.restype = ctypes.c_char_p

_lib.nth_derivative.argtypes = [ctypes.c_char_p, ctypes.c_double, ctypes.c_int, ctypes.c_double]
_lib.nth_derivative.restype = ctypes.c_double

_lib.taylor_coefficients.argtypes = [ctypes.c_char_p, ctypes.c_double, ctypes.c_int,
                                       ctypes.POINTER(ctypes.c_double), ctypes.c_int]
_lib.taylor_coefficients.restype = ctypes.c_int

_lib.ode_solve_rk4.argtypes = [ctypes.c_char_p, ctypes.c_double, ctypes.c_double,
                                 ctypes.c_double, ctypes.c_int,
                                 ctypes.POINTER(ctypes.c_double),
                                 ctypes.POINTER(ctypes.c_double), ctypes.c_int]
_lib.ode_solve_rk4.restype = ctypes.c_int

# Complex number functions
_lib.complex_evaluate.argtypes = [ctypes.c_char_p, ctypes.c_double, ctypes.c_double,
                                   ctypes.POINTER(ctypes.c_double),
                                   ctypes.POINTER(ctypes.c_double)]
_lib.complex_evaluate.restype = None

_lib.complex_add_values.argtypes = [ctypes.c_double, ctypes.c_double,
                                     ctypes.c_double, ctypes.c_double,
                                     ctypes.POINTER(ctypes.c_double),
                                     ctypes.POINTER(ctypes.c_double)]
_lib.complex_add_values.restype = None

_lib.complex_sub_values.argtypes = [ctypes.c_double, ctypes.c_double,
                                     ctypes.c_double, ctypes.c_double,
                                     ctypes.POINTER(ctypes.c_double),
                                     ctypes.POINTER(ctypes.c_double)]
_lib.complex_sub_values.restype = None

_lib.complex_mul_values.argtypes = [ctypes.c_double, ctypes.c_double,
                                     ctypes.c_double, ctypes.c_double,
                                     ctypes.POINTER(ctypes.c_double),
                                     ctypes.POINTER(ctypes.c_double)]
_lib.complex_mul_values.restype = None

_lib.complex_div_values.argtypes = [ctypes.c_double, ctypes.c_double,
                                     ctypes.c_double, ctypes.c_double,
                                     ctypes.POINTER(ctypes.c_double),
                                     ctypes.POINTER(ctypes.c_double)]
_lib.complex_div_values.restype = None

_lib.complex_pow_values.argtypes = [ctypes.c_double, ctypes.c_double,
                                     ctypes.c_double, ctypes.c_double,
                                     ctypes.POINTER(ctypes.c_double),
                                     ctypes.POINTER(ctypes.c_double)]
_lib.complex_pow_values.restype = None

_lib.complex_sin_value.argtypes = [ctypes.c_double, ctypes.c_double,
                                    ctypes.POINTER(ctypes.c_double),
                                    ctypes.POINTER(ctypes.c_double)]
_lib.complex_sin_value.restype = None

_lib.complex_cos_value.argtypes = [ctypes.c_double, ctypes.c_double,
                                    ctypes.POINTER(ctypes.c_double),
                                    ctypes.POINTER(ctypes.c_double)]
_lib.complex_cos_value.restype = None

_lib.complex_tan_value.argtypes = [ctypes.c_double, ctypes.c_double,
                                    ctypes.POINTER(ctypes.c_double),
                                    ctypes.POINTER(ctypes.c_double)]
_lib.complex_tan_value.restype = None

_lib.complex_exp_value.argtypes = [ctypes.c_double, ctypes.c_double,
                                    ctypes.POINTER(ctypes.c_double),
                                    ctypes.POINTER(ctypes.c_double)]
_lib.complex_exp_value.restype = None

_lib.complex_ln_value.argtypes = [ctypes.c_double, ctypes.c_double,
                                   ctypes.POINTER(ctypes.c_double),
                                   ctypes.POINTER(ctypes.c_double)]
_lib.complex_ln_value.restype = None

_lib.complex_sqrt_value.argtypes = [ctypes.c_double, ctypes.c_double,
                                     ctypes.POINTER(ctypes.c_double),
                                     ctypes.POINTER(ctypes.c_double)]
_lib.complex_sqrt_value.restype = None

_lib.complex_abs_value.argtypes = [ctypes.c_double, ctypes.c_double]
_lib.complex_abs_value.restype = ctypes.c_double

_lib.complex_conj_value.argtypes = [ctypes.c_double, ctypes.c_double,
                                     ctypes.POINTER(ctypes.c_double),
                                     ctypes.POINTER(ctypes.c_double)]
_lib.complex_conj_value.restype = None

_lib.complex_array_evaluate.argtypes = [ctypes.c_char_p,
                                          ctypes.POINTER(ctypes.c_double),
                                          ctypes.POINTER(ctypes.c_double),
                                          ctypes.POINTER(ctypes.c_double),
                                          ctypes.POINTER(ctypes.c_double),
                                          ctypes.c_int]
_lib.complex_array_evaluate.restype = None

_lib.area_between_curves.argtypes = [ctypes.c_char_p, ctypes.c_char_p,
                                      ctypes.c_double, ctypes.c_double,
                                      ctypes.c_double]
_lib.area_between_curves.restype = ctypes.c_double


def _is_invalid(x: float) -> bool:
    try:
        return _math.isnan(x) or _math.isinf(x)
    except Exception:
        return x != x


class CalcEngine:
    """Bridge wrapper around the C core library.

    Usage:
        engine = CalcEngine()
        y = engine.evaluate("sin(x) + x^2", 3.14)
        d = engine.derivative("x^3", 2.0)
        i = engine.integrate("x^2", 0, 1)
        root = engine.solve("x^2 - 4", guess=1, xmin=0, xmax=3)
    """

    @staticmethod
    def evaluate(expr: str, x: float) -> Optional[float]:
        """Evaluate expression f(x) at a given x."""
        result = _lib.evaluate(expr.encode("utf-8"), x)
        return None if _is_invalid(result) else result

    @staticmethod
    def evaluate_xy(expr: str, x: float, y: float) -> Optional[float]:
        """Evaluate expression f(x,y) at given x and y."""
        result = _lib.evaluate_xy(expr.encode("utf-8"), x, y)
        return None if _is_invalid(result) else result

    @staticmethod
    def evaluate_array(expr: str, xs: List[float]) -> List[Optional[float]]:
        """Evaluate expression at multiple x values (batched)."""
        n = len(xs)
        arr_x = (ctypes.c_double * n)(*xs)
        arr_y = (ctypes.c_double * n)()
        _lib.evaluate_array(expr.encode("utf-8"), arr_x, arr_y, n)
        return [None if _is_invalid(arr_y[i]) else arr_y[i] for i in range(n)]

    @staticmethod
    def evaluate_xy_array(expr: str, xs: List[float], ys: List[float]) -> List[Optional[float]]:
        """Evaluate expression f(x,y) at multiple (x,y) points (batched).

        xs and ys must have the same length. Returns a list of the same length
        where each element is f(xs[i], ys[i]) or None if evaluation failed.
        """
        n = len(xs)
        if n != len(ys):
            raise ValueError("xs and ys must have the same length")
        if n == 0:
            return []
        arr_x = (ctypes.c_double * n)(*xs)
        arr_y = (ctypes.c_double * n)(*ys)
        arr_z = (ctypes.c_double * n)()
        _lib.evaluate_xy_array(expr.encode("utf-8"), arr_x, arr_y, arr_z, n)
        return [None if _is_invalid(arr_z[i]) else arr_z[i] for i in range(n)]

    @staticmethod
    def derivative(expr: str, x: float, h: float = 1e-6) -> Optional[float]:
        """First derivative f'(x) via central difference."""
        result = _lib.derivative(expr.encode("utf-8"), x, h)
        return None if _is_invalid(result) else result

    @staticmethod
    def derivative2(expr: str, x: float, h: float = 1e-6) -> Optional[float]:
        """Second derivative f''(x) via central difference."""
        result = _lib.derivative2(expr.encode("utf-8"), x, h)
        return None if _is_invalid(result) else result

    @staticmethod
    def integrate(expr: str, a: float, b: float,
                  n: int = 1000) -> Optional[float]:
        """Definite integral over [a,b] using adaptive Simpson's rule.

        Note: n parameter is kept for API compatibility but not used.
        Uses adaptive integration for better accuracy and consistency with Android.
        """
        result = _lib.integrate_adaptive(expr.encode("utf-8"), a, b, 1e-8)
        return None if _is_invalid(result) else result

    @staticmethod
    def integrate_adaptive(expr: str, a: float, b: float,
                           tol: float = 1e-8) -> Optional[float]:
        """Definite integral with adaptive step refinement."""
        result = _lib.integrate_adaptive(expr.encode("utf-8"), a, b, tol)
        return None if _is_invalid(result) else result

    @staticmethod
    def solve(expr: str, guess: float = 0.0, xmin: float = -100.0,
              xmax: float = 100.0, tol: float = 1e-8,
              max_iter: int = 100) -> Optional[float]:
        """Solve f(x)=0 using Newton-Raphson with bisection fallback."""
        result = _lib.solve_equation(expr.encode("utf-8"),
                                     guess, xmin, xmax, tol, max_iter)
        return None if _is_invalid(result) else result

    @staticmethod
    def solve_bisection(expr: str, a: float, b: float,
                        tol: float = 1e-8,
                        max_iter: int = 200) -> Optional[float]:
        """Solve f(x)=0 using pure bisection (requires sign change on [a,b])."""
        result = _lib.solve_bisection(expr.encode("utf-8"), a, b, tol, max_iter)
        return None if _is_invalid(result) else result

    @staticmethod
    def find_minimum(expr: str, a: float, b: float,
                     tol: float = 1e-8,
                     max_iter: int = 200) -> Optional[float]:
        """Find a local minimum of f(x) on [a, b] using golden-section search."""
        result = _lib.find_minimum(expr.encode("utf-8"), a, b, tol, max_iter)
        return None if _is_invalid(result) else result

    @staticmethod
    def find_maximum(expr: str, a: float, b: float,
                     tol: float = 1e-8,
                     max_iter: int = 200) -> Optional[float]:
        """Find a local maximum of f(x) on [a, b] using golden-section search."""
        result = _lib.find_maximum(expr.encode("utf-8"), a, b, tol, max_iter)
        return None if _is_invalid(result) else result

    @staticmethod
    def limit_left(expr: str, a: float, max_level: int = 10) -> Optional[float]:
        """Compute left-hand limit: lim(x→a⁻) f(x) using Richardson extrapolation."""
        result = _lib.limit_left(expr.encode("utf-8"), a, max_level)
        return None if _is_invalid(result) else result

    @staticmethod
    def limit_right(expr: str, a: float, max_level: int = 10) -> Optional[float]:
        """Compute right-hand limit: lim(x→a⁺) f(x) using Richardson extrapolation."""
        result = _lib.limit_right(expr.encode("utf-8"), a, max_level)
        return None if _is_invalid(result) else result

    @staticmethod
    def limit(expr: str, a: float, tol: float = 1e-8,
              max_level: int = 10) -> Optional[float]:
        """Compute two-sided limit: lim(x→a) f(x).

        Returns the limit if left and right limits agree within tol.
        Returns None if the limit does not exist.
        """
        result = _lib.limit(expr.encode("utf-8"), a, tol, max_level)
        return None if _is_invalid(result) else result

    @staticmethod
    def get_last_error() -> str:
        """Return the last error message from the C core."""
        raw = _lib.get_last_error()
        return raw.decode("utf-8") if raw else ""

    @staticmethod
    def nth_derivative(expr: str, x: float, n: int, h: float = 1e-5) -> Optional[float]:
        """Compute the nth-order derivative of f(x) at x using central differences."""
        result = _lib.nth_derivative(expr.encode("utf-8"), x, n, h)
        return None if _is_invalid(result) else result

    @staticmethod
    def taylor_coefficients(expr: str, a: float, order: int) -> Optional[List[float]]:
        """Compute Taylor series coefficients c_k = f^(k)(a)/k! for k=0..order.

        Returns a list of (order+1) coefficients, or None on error.
        """
        if order < 0 or order > 20:
            return None
        n = order + 1
        arr = (ctypes.c_double * n)()
        count = _lib.taylor_coefficients(expr.encode("utf-8"), a, order, arr, n)
        if count <= 0:
            return None
        count = min(count, n)
        return [None if _is_invalid(arr[i]) else arr[i] for i in range(count)]

    @staticmethod
    def taylor_evaluate(expr: str, a: float, x: float, order: int) -> Optional[float]:
        """Evaluate the Taylor polynomial of f(x) expanded at point a, evaluated at x."""
        coeffs = CalcEngine.taylor_coefficients(expr, a, order)
        if coeffs is None:
            return None
        dx = x - a
        result = 0.0
        dx_power = 1.0
        for c in coeffs:
            if c is None:
                return None
            result += c * dx_power
            dx_power *= dx
        return result

    @staticmethod
    def ode_solve_rk4(expr: str, x0: float, y0: float, x_end: float,
                       n_steps: int = 1000):
        """Solve ODE dy/dx = f(x, y) with initial condition y(x0) = y0
        using 4th-order Runge-Kutta method over [x0, x_end].

        Returns a dict with keys:
            'xs' : list of x values
            'ys' : list of y values
            'n_steps' : number of steps used
        Returns None on error.
        """
        if n_steps < 1:
            return None
        max_out = n_steps + 1
        arr_x = (ctypes.c_double * max_out)()
        arr_y = (ctypes.c_double * max_out)()
        count = _lib.ode_solve_rk4(expr.encode("utf-8"), x0, y0, x_end,
                                     n_steps, arr_x, arr_y, max_out)
        if count <= 0:
            return None
        count = min(count, max_out)
        return {
            'xs': [arr_x[i] for i in range(count)],
            'ys': [None if _is_invalid(arr_y[i]) else arr_y[i] for i in range(count)],
            'n_steps': n_steps,
        }

    @staticmethod
    def diff(expr: str, x: float, h: float = 1e-6) -> Optional[float]:
        return CalcEngine.derivative(expr, x, h)

    @staticmethod
    def integral(expr: str, a: float, b: float,
                 n: int = 1000) -> Optional[float]:
        """Definite integral over [a,b] using Simpson's rule (alias for integrate)."""
        return CalcEngine.integrate(expr, a, b, n)

    # Complex number methods
    @staticmethod
    def complex_evaluate(expr: str, x: float, y: float = 0.0):
        """Evaluate expression at complex point x+iy.
        
        Returns a complex number or None on error.
        """
        out_re = ctypes.c_double()
        out_im = ctypes.c_double()
        _lib.complex_evaluate(expr.encode("utf-8"), x, y,
                              ctypes.byref(out_re), ctypes.byref(out_im))
        re_val = out_re.value
        im_val = out_im.value
        if _is_invalid(re_val) or _is_invalid(im_val):
            return None
        return complex(re_val, im_val)

    @staticmethod
    def complex_add(z1: complex, z2: complex) -> complex:
        """Add two complex numbers."""
        out_re = ctypes.c_double()
        out_im = ctypes.c_double()
        _lib.complex_add_values(z1.real, z1.imag, z2.real, z2.imag,
                                ctypes.byref(out_re), ctypes.byref(out_im))
        re_val = out_re.value
        im_val = out_im.value
        if _is_invalid(re_val) or _is_invalid(im_val):
            return complex(float('nan'), float('nan'))
        return complex(re_val, im_val)

    @staticmethod
    def complex_sub(z1: complex, z2: complex) -> complex:
        """Subtract two complex numbers."""
        out_re = ctypes.c_double()
        out_im = ctypes.c_double()
        _lib.complex_sub_values(z1.real, z1.imag, z2.real, z2.imag,
                                ctypes.byref(out_re), ctypes.byref(out_im))
        re_val = out_re.value
        im_val = out_im.value
        if _is_invalid(re_val) or _is_invalid(im_val):
            return complex(float('nan'), float('nan'))
        return complex(re_val, im_val)

    @staticmethod
    def complex_mul(z1: complex, z2: complex) -> complex:
        """Multiply two complex numbers."""
        out_re = ctypes.c_double()
        out_im = ctypes.c_double()
        _lib.complex_mul_values(z1.real, z1.imag, z2.real, z2.imag,
                                ctypes.byref(out_re), ctypes.byref(out_im))
        re_val = out_re.value
        im_val = out_im.value
        if _is_invalid(re_val) or _is_invalid(im_val):
            return complex(float('nan'), float('nan'))
        return complex(re_val, im_val)

    @staticmethod
    def complex_div(z1: complex, z2: complex) -> complex:
        """Divide two complex numbers."""
        out_re = ctypes.c_double()
        out_im = ctypes.c_double()
        _lib.complex_div_values(z1.real, z1.imag, z2.real, z2.imag,
                                ctypes.byref(out_re), ctypes.byref(out_im))
        re_val = out_re.value
        im_val = out_im.value
        if _is_invalid(re_val) or _is_invalid(im_val):
            return complex(float('nan'), float('nan'))
        return complex(re_val, im_val)

    @staticmethod
    def complex_pow(z1: complex, z2: complex) -> complex:
        """Raise a complex number to a power."""
        out_re = ctypes.c_double()
        out_im = ctypes.c_double()
        _lib.complex_pow_values(z1.real, z1.imag, z2.real, z2.imag,
                                ctypes.byref(out_re), ctypes.byref(out_im))
        re_val = out_re.value
        im_val = out_im.value
        if _is_invalid(re_val) or _is_invalid(im_val):
            return complex(float('nan'), float('nan'))
        return complex(re_val, im_val)

    @staticmethod
    def complex_sin(z: complex) -> complex:
        """Compute sine of a complex number."""
        out_re = ctypes.c_double()
        out_im = ctypes.c_double()
        _lib.complex_sin_value(z.real, z.imag,
                               ctypes.byref(out_re), ctypes.byref(out_im))
        re_val = out_re.value
        im_val = out_im.value
        if _is_invalid(re_val) or _is_invalid(im_val):
            return complex(float('nan'), float('nan'))
        return complex(re_val, im_val)

    @staticmethod
    def complex_cos(z: complex) -> complex:
        """Compute cosine of a complex number."""
        out_re = ctypes.c_double()
        out_im = ctypes.c_double()
        _lib.complex_cos_value(z.real, z.imag,
                               ctypes.byref(out_re), ctypes.byref(out_im))
        re_val = out_re.value
        im_val = out_im.value
        if _is_invalid(re_val) or _is_invalid(im_val):
            return complex(float('nan'), float('nan'))
        return complex(re_val, im_val)

    @staticmethod
    def complex_tan(z: complex) -> complex:
        """Compute tangent of a complex number."""
        out_re = ctypes.c_double()
        out_im = ctypes.c_double()
        _lib.complex_tan_value(z.real, z.imag,
                               ctypes.byref(out_re), ctypes.byref(out_im))
        re_val = out_re.value
        im_val = out_im.value
        if _is_invalid(re_val) or _is_invalid(im_val):
            return complex(float('nan'), float('nan'))
        return complex(re_val, im_val)

    @staticmethod
    def complex_exp(z: complex) -> complex:
        """Compute exponential of a complex number."""
        out_re = ctypes.c_double()
        out_im = ctypes.c_double()
        _lib.complex_exp_value(z.real, z.imag,
                               ctypes.byref(out_re), ctypes.byref(out_im))
        re_val = out_re.value
        im_val = out_im.value
        if _is_invalid(re_val) or _is_invalid(im_val):
            return complex(float('nan'), float('nan'))
        return complex(re_val, im_val)

    @staticmethod
    def complex_ln(z: complex) -> complex:
        """Compute natural logarithm of a complex number."""
        out_re = ctypes.c_double()
        out_im = ctypes.c_double()
        _lib.complex_ln_value(z.real, z.imag,
                              ctypes.byref(out_re), ctypes.byref(out_im))
        re_val = out_re.value
        im_val = out_im.value
        if _is_invalid(re_val) or _is_invalid(im_val):
            return complex(float('nan'), float('nan'))
        return complex(re_val, im_val)

    @staticmethod
    def complex_sqrt(z: complex) -> complex:
        """Compute square root of a complex number."""
        out_re = ctypes.c_double()
        out_im = ctypes.c_double()
        _lib.complex_sqrt_value(z.real, z.imag,
                                ctypes.byref(out_re), ctypes.byref(out_im))
        re_val = out_re.value
        im_val = out_im.value
        if _is_invalid(re_val) or _is_invalid(im_val):
            return complex(float('nan'), float('nan'))
        return complex(re_val, im_val)

    @staticmethod
    def complex_abs(z: complex) -> float:
        """Compute absolute value (modulus) of a complex number."""
        return _lib.complex_abs_value(z.real, z.imag)

    @staticmethod
    def complex_conj(z: complex) -> complex:
        """Compute complex conjugate."""
        out_re = ctypes.c_double()
        out_im = ctypes.c_double()
        _lib.complex_conj_value(z.real, z.imag,
                                ctypes.byref(out_re), ctypes.byref(out_im))
        re_val = out_re.value
        im_val = out_im.value
        if _is_invalid(re_val) or _is_invalid(im_val):
            return complex(float('nan'), float('nan'))
        return complex(re_val, im_val)

    @staticmethod
    def complex_array_evaluate(expr: str, zs: List[complex]):
        """Evaluate expression at multiple complex points.
        
        Returns a list of complex numbers.
        """
        n = len(zs)
        if n == 0:
            return []
        arr_x = (ctypes.c_double * n)(*[z.real for z in zs])
        arr_y = (ctypes.c_double * n)(*[z.imag for z in zs])
        arr_re = (ctypes.c_double * n)()
        arr_im = (ctypes.c_double * n)()
        _lib.complex_array_evaluate(expr.encode("utf-8"), arr_x, arr_y,
                                    arr_re, arr_im, n)
        return [complex(arr_re[i], arr_im[i]) for i in range(n)]

    @staticmethod
    def arc_length(expr: str, a: float, b: float, n: int = 5000) -> Optional[float]:
        """Approximate arc length of f(x) over [a,b] using chord summation."""
        if a >= b:
            return 0.0 if a == b else None
        try:
            import math as _math
            h = (b - a) / n
            xs = [a + i * h for i in range(n + 1)]
            ys = CalcEngine.evaluate_array(expr, xs)
            length = 0.0
            for i in range(n):
                y1 = ys[i]
                y2 = ys[i + 1]
                if y1 is None or y2 is None:
                    continue
                dy = y2 - y1
                length += _math.sqrt(h * h + dy * dy)
            return length
        except Exception:
            return None

    @staticmethod
    def area_between_curves(expr_f: str, expr_g: str, a: float, b: float,
                            tol: float = 1e-8) -> Optional[float]:
        """Compute the area between two curves f(x) and g(x) over [a,b].

        Returns integral_a^b |f(x) - g(x)| dx using adaptive Simpson's rule.
        """
        result = _lib.area_between_curves(expr_f.encode("utf-8"),
                                           expr_g.encode("utf-8"),
                                           a, b, tol)
        return None if _is_invalid(result) else result

    @staticmethod
    def evaluate_parametric(expr_x: str, expr_y: str, t_min: float,
                            t_max: float, n: int = 500):
        """Evaluate parametric curve x(t), y(t) over [t_min, t_max].

        Returns a dict with keys:
            'xs' : list of x-values
            'ys' : list of y-values
            'ts' : list of t-values
        Returns None on error.

        Note: internally substitutes t -> x for the C core engine.
        """
        if t_min >= t_max or n < 2:
            return None
        try:
            ts = [t_min + (t_max - t_min) * i / (n - 1) for i in range(n)]
            # C core only supports 'x' and 'y' as variables.
            # Replace 't' with 'x' in parametric expressions for evaluation.
            import re as _re
            x_expr_sub = _re.sub(r'\bt\b', 'x', expr_x)
            y_expr_sub = _re.sub(r'\bt\b', 'x', expr_y)
            xs = CalcEngine.evaluate_array(x_expr_sub, ts)
            ys = CalcEngine.evaluate_array(y_expr_sub, ts)
            valid_xs = []
            valid_ys = []
            valid_ts = []
            for i in range(n):
                if xs[i] is not None and ys[i] is not None:
                    valid_xs.append(xs[i])
                    valid_ys.append(ys[i])
                    valid_ts.append(ts[i])
            return {'xs': valid_xs, 'ys': valid_ys, 'ts': valid_ts}
        except Exception:
            return None

    @staticmethod
    def fft_spectrum(expr: str, a: float, b: float, n: int = 1024):
        """Compute FFT amplitude and phase spectrum for f(x) over [a,b].

        Returns a dict with keys:
            'freqs'  : list of positive frequencies (Hz, assuming unit spacing)
            'amps'   : list of amplitudes
            'phases' : list of phases (radians)
            'xs'     : sample x values
            'ys'     : sample y values (real)
        Returns None on error.
        """
        if a >= b or n < 2:
            return None
        try:
            import numpy as np
            xs = np.linspace(a, b, n, endpoint=False)
            ys = CalcEngine.evaluate_array(expr, xs.tolist())
            y_arr = np.array([0.0 if y is None or _is_invalid(y) else float(y)
                              for y in ys])
            # Remove DC offset (mean) for cleaner spectrum
            y_arr = y_arr - np.mean(y_arr)
            Y = np.fft.rfft(y_arr)
            freqs = np.fft.rfftfreq(n, d=(b - a) / n)
            amps = np.abs(Y) * (2.0 / n)
            # Fix DC component scaling (and Nyquist for even n)
            if len(amps) > 0:
                amps[0] = amps[0] / 2.0
            if n % 2 == 0 and len(amps) > 1:
                amps[-1] = amps[-1] / 2.0
            phases = np.angle(Y)
            return {
                'freqs': freqs.tolist(),
                'amps': amps.tolist(),
                'phases': phases.tolist(),
                'xs': xs.tolist(),
                'ys': y_arr.tolist(),
            }
        except Exception:
            return None
