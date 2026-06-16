"""
Super Calculator - Python Bridge Layer

Uses ctypes to call the C core dynamic library (calc_core.dll/.so).
This is the Bridge in the Bridge Pattern, decoupling the GUI from C.
"""

import ctypes
import os
import sys
import math as _math
from typing import Dict, List, Optional

# ---------------------------------------------------------------------------
#  Library loading
# ---------------------------------------------------------------------------

def _find_lib() -> str:
    """Locate the compiled shared library next to this file."""
    base = os.path.dirname(os.path.abspath(__file__))

    def _try_find(names: List[str]) -> Optional[str]:
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

_lib.ode_solve_euler.argtypes = [ctypes.c_char_p, ctypes.c_double, ctypes.c_double,
                                  ctypes.c_double, ctypes.c_int,
                                  ctypes.POINTER(ctypes.c_double),
                                  ctypes.POINTER(ctypes.c_double), ctypes.c_int]
_lib.ode_solve_euler.restype = ctypes.c_int

_lib.ode_solve_improved_euler.argtypes = [ctypes.c_char_p, ctypes.c_double, ctypes.c_double,
                                           ctypes.c_double, ctypes.c_int,
                                           ctypes.POINTER(ctypes.c_double),
                                           ctypes.POINTER(ctypes.c_double), ctypes.c_int]
_lib.ode_solve_improved_euler.restype = ctypes.c_int

_lib.ode_solve_midpoint.argtypes = [ctypes.c_char_p, ctypes.c_double, ctypes.c_double,
                                     ctypes.c_double, ctypes.c_int,
                                     ctypes.POINTER(ctypes.c_double),
                                     ctypes.POINTER(ctypes.c_double), ctypes.c_int]
_lib.ode_solve_midpoint.restype = ctypes.c_int

_lib.ode_solve_rkf45.argtypes = [ctypes.c_char_p, ctypes.c_double, ctypes.c_double,
                                  ctypes.c_double, ctypes.c_double,
                                  ctypes.POINTER(ctypes.c_double),
                                  ctypes.POINTER(ctypes.c_double), ctypes.c_int]
_lib.ode_solve_rkf45.restype = ctypes.c_int

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

_lib.solve_system_2d.argtypes = [ctypes.c_char_p, ctypes.c_char_p,
                                   ctypes.c_double, ctypes.c_double,
                                   ctypes.c_double, ctypes.c_int,
                                   ctypes.POINTER(ctypes.c_double),
                                   ctypes.POINTER(ctypes.c_double)]
_lib.solve_system_2d.restype = ctypes.c_int

# Base conversion functions
_lib.base_to_long.argtypes = [ctypes.c_char_p, ctypes.c_int]
_lib.base_to_long.restype = ctypes.c_longlong

_lib.long_to_base.argtypes = [ctypes.c_longlong, ctypes.c_int,
                               ctypes.POINTER(ctypes.c_char), ctypes.c_int]
_lib.long_to_base.restype = ctypes.c_int

_lib.convert_base.argtypes = [ctypes.c_char_p, ctypes.c_int, ctypes.c_int,
                               ctypes.POINTER(ctypes.c_char), ctypes.c_int]
_lib.convert_base.restype = ctypes.c_int

_lib.convert_base_all.argtypes = [ctypes.c_char_p, ctypes.c_int,
                                   ctypes.POINTER(ctypes.c_char), ctypes.c_int,
                                   ctypes.POINTER(ctypes.c_char), ctypes.c_int,
                                   ctypes.POINTER(ctypes.c_char), ctypes.c_int,
                                   ctypes.POINTER(ctypes.c_char), ctypes.c_int]
_lib.convert_base_all.restype = None

_lib.volume_disk.argtypes = [ctypes.c_char_p, ctypes.c_double,
                              ctypes.c_double, ctypes.c_double]
_lib.volume_disk.restype = ctypes.c_double

_lib.volume_washer.argtypes = [ctypes.c_char_p, ctypes.c_char_p,
                                ctypes.c_double, ctypes.c_double,
                                ctypes.c_double]
_lib.volume_washer.restype = ctypes.c_double

_lib.volume_shell.argtypes = [ctypes.c_char_p, ctypes.c_double,
                               ctypes.c_double, ctypes.c_double]
_lib.volume_shell.restype = ctypes.c_double

# Custom function registry
_lib.custom_func_define.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
_lib.custom_func_define.restype = ctypes.c_int

_lib.custom_func_clear.argtypes = []
_lib.custom_func_clear.restype = None

_lib.custom_func_delete.argtypes = [ctypes.c_char_p]
_lib.custom_func_delete.restype = ctypes.c_int

_lib.custom_func_list.argtypes = [ctypes.POINTER(ctypes.c_char), ctypes.c_int]
_lib.custom_func_list.restype = ctypes.c_int

# Calculation History
_lib.history_add.argtypes = [ctypes.c_char_p, ctypes.c_double]
_lib.history_add.restype = None

_lib.history_count.argtypes = []
_lib.history_count.restype = ctypes.c_int

_lib.history_clear.argtypes = []
_lib.history_clear.restype = None

_lib.history_get_all.argtypes = [ctypes.POINTER(ctypes.c_char), ctypes.c_int]
_lib.history_get_all.restype = ctypes.c_int

# Laplace Transform
_lib.laplace_transform.argtypes = [ctypes.c_char_p, ctypes.c_double]
_lib.laplace_transform.restype = ctypes.c_double

_lib.inverse_laplace.argtypes = [ctypes.c_char_p, ctypes.c_double]
_lib.inverse_laplace.restype = ctypes.c_double

# Akima Interpolation
_lib.interp_akima.argtypes = [ctypes.POINTER(ctypes.c_double),
                               ctypes.POINTER(ctypes.c_double),
                               ctypes.c_int, ctypes.c_double]
_lib.interp_akima.restype = ctypes.c_double

# Natural Spline Interpolation
_lib.interp_natural_spline.argtypes = [ctypes.POINTER(ctypes.c_double),
                                       ctypes.POINTER(ctypes.c_double),
                                       ctypes.c_int, ctypes.c_double]
_lib.interp_natural_spline.restype = ctypes.c_double


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
        if n == 0:
            return []
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
    def taylor_coefficients(expr: str, a: float, order: int) -> Optional[List[Optional[float]]]:
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
                       n_steps: int = 1000) -> Optional[Dict[str, object]]:
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
    def complex_abs(z: complex) -> Optional[float]:
        """Compute absolute value (modulus) of a complex number."""
        result = _lib.complex_abs_value(z.real, z.imag)
        return None if _is_invalid(result) else result

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
    def complex_array_evaluate(expr: str, zs: List[complex]) -> List[Optional[complex]]:
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
        result: List[Optional[complex]] = []
        for i in range(n):
            re_val = arr_re[i]
            im_val = arr_im[i]
            if _is_invalid(re_val) or _is_invalid(im_val):
                result.append(None)
            else:
                result.append(complex(re_val, im_val))
        return result

    @staticmethod
    def arc_length(expr: str, a: float, b: float, n: int = 5000) -> Optional[float]:
        """Approximate arc length of f(x) over [a,b] using chord summation."""
        if a >= b:
            return 0.0 if a == b else None
        if n < 1:
            return None
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
    def solve_system_2d(f_expr: str, g_expr: str, x0: float = 0.0,
                        y0: float = 0.0, tol: float = 1e-10,
                        max_iter: int = 100) -> Optional[Dict[str, float]]:
        """Solve a system of two nonlinear equations in two unknowns:
            f(x,y) = 0
            g(x,y) = 0
        using Newton's method for systems with numerical Jacobian.

        Args:
            f_expr: expression for the first equation f(x,y)
            g_expr: expression for the second equation g(x,y)
            x0: initial guess for x
            y0: initial guess for y
            tol: convergence tolerance
            max_iter: maximum number of iterations

        Returns:
            dict with keys 'x' and 'y' on success, None on failure.
        """
        out_x = ctypes.c_double()
        out_y = ctypes.c_double()
        success = _lib.solve_system_2d(f_expr.encode("utf-8"),
                                        g_expr.encode("utf-8"),
                                        x0, y0, tol, max_iter,
                                        ctypes.byref(out_x), ctypes.byref(out_y))
        if not success:
            return None
        x_val = out_x.value
        y_val = out_y.value
        if _is_invalid(x_val) or _is_invalid(y_val):
            return None
        return {'x': x_val, 'y': y_val}

    @staticmethod
    def evaluate_parametric(expr_x: str, expr_y: str, t_min: float,
                            t_max: float, n: int = 500) -> Optional[Dict[str, object]]:
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
            valid_xs: List[float] = []
            valid_ys: List[float] = []
            valid_ts: List[float] = []
            for i in range(n):
                x_val = xs[i]
                y_val = ys[i]
                if x_val is not None and y_val is not None:
                    valid_xs.append(x_val)
                    valid_ys.append(y_val)
                    valid_ts.append(ts[i])
            return {'xs': valid_xs, 'ys': valid_ys, 'ts': valid_ts}
        except Exception:
            return None

    @staticmethod
    def fft_spectrum(expr: str, a: float, b: float, n: int = 1024) -> Optional[Dict[str, object]]:
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

    @staticmethod
    def linear_regression(xs: List[float], ys: List[float]) -> Optional[Dict[str, object]]:
        """Compute linear regression y = a*x + b for data points.

        Returns a dict with keys:
            'slope'     : a (slope)
            'intercept' : b (y-intercept)
            'r_squared' : R² (coefficient of determination)
            'equation'  : formatted equation string
        Returns None on error.
        """
        if len(xs) < 2 or len(xs) != len(ys):
            return None
        try:
            import numpy as np
            x_arr = np.array(xs, dtype=float)
            y_arr = np.array(ys, dtype=float)
            # Remove NaN/Inf
            mask = np.isfinite(x_arr) & np.isfinite(y_arr)
            x_arr, y_arr = x_arr[mask], y_arr[mask]
            if len(x_arr) < 2:
                return None
            x_mean = np.mean(x_arr)
            y_mean = np.mean(y_arr)
            ss_xy = np.sum((x_arr - x_mean) * (y_arr - y_mean))
            ss_xx = np.sum((x_arr - x_mean) ** 2)
            if ss_xx == 0:
                return None
            slope = ss_xy / ss_xx
            intercept = y_mean - slope * x_mean
            # R² calculation
            ss_res = np.sum((y_arr - (slope * x_arr + intercept)) ** 2)
            ss_tot = np.sum((y_arr - y_mean) ** 2)
            r_squared = 1.0 - ss_res / ss_tot if ss_tot != 0 else (1.0 if ss_res == 0 else 0.0)
            # Format equation
            sign = "+" if intercept >= 0 else "-"
            eq = f"y = {slope:.6g}*x {sign} {abs(intercept):.6g}"
            x_sorted = np.sort(x_arr)
            y_sorted = slope * x_sorted + intercept
            return {
                'slope': float(slope),
                'intercept': float(intercept),
                'r_squared': float(r_squared),
                'equation': eq,
                'xs_fit': x_sorted.tolist(),
                'ys_fit': y_sorted.tolist(),
            }
        except Exception:
            return None

    # Numerical method comparison functions
    @staticmethod
    def ode_solve_euler(expr: str, x0: float, y0: float, x_end: float,
                        n_steps: int = 1000) -> Optional[Dict[str, object]]:
        """Solve ODE dy/dx = f(x, y) with initial condition y(x0) = y0
        using Euler's method (1st order) over [x0, x_end].

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
        count = _lib.ode_solve_euler(expr.encode("utf-8"), x0, y0, x_end,
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
    def ode_solve_improved_euler(expr: str, x0: float, y0: float, x_end: float,
                                 n_steps: int = 1000) -> Optional[Dict[str, object]]:
        """Solve ODE dy/dx = f(x, y) with initial condition y(x0) = y0
        using Improved Euler's method (Heun's method, 2nd order) over [x0, x_end].

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
        count = _lib.ode_solve_improved_euler(expr.encode("utf-8"), x0, y0, x_end,
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
    def ode_solve_midpoint(expr: str, x0: float, y0: float, x_end: float,
                           n_steps: int = 1000) -> Optional[Dict[str, object]]:
        """Solve ODE dy/dx = f(x, y) with initial condition y(x0) = y0
        using Midpoint method (2nd order) over [x0, x_end].

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
        count = _lib.ode_solve_midpoint(expr.encode("utf-8"), x0, y0, x_end,
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
    def ode_solve_rkf45(expr: str, x0: float, y0: float, x_end: float,
                        tol: float = 1e-6) -> Optional[Dict[str, object]]:
        """Solve ODE dy/dx = f(x, y) with initial condition y(x0) = y0
        using Runge-Kutta-Fehlberg (RKF45) method with adaptive step size over [x0, x_end].

        Returns a dict with keys:
            'xs' : list of x values
            'ys' : list of y values
            'n_points' : number of points computed
        Returns None on error.
        """
        max_points = 100000
        arr_x = (ctypes.c_double * max_points)()
        arr_y = (ctypes.c_double * max_points)()
        count = _lib.ode_solve_rkf45(expr.encode("utf-8"), x0, y0, x_end,
                                     tol, arr_x, arr_y, max_points)
        if count <= 0:
            return None
        count = min(count, max_points)
        return {
            'xs': [arr_x[i] for i in range(count)],
            'ys': [None if _is_invalid(arr_y[i]) else arr_y[i] for i in range(count)],
            'n_points': count,
        }

    @staticmethod
    def ode_compare_methods(expr: str, x0: float, y0: float, x_end: float,
                            n_steps: int = 100) -> Optional[Dict[str, object]]:
        """Compare different ODE solving methods for the same problem.
        
        Solves dy/dx = f(x, y), y(x0) = y0 using:
        - Euler (1st order)
        - Improved Euler (2nd order)
        - Midpoint (2nd order)
        - RK4 (4th order)
        - RKF45 (adaptive)
        
        Returns a dict with keys:
            'euler' : Euler method result {'xs', 'ys'}
            'improved_euler' : Improved Euler result {'xs', 'ys'}
            'midpoint' : Midpoint result {'xs', 'ys'}
            'rk4' : RK4 result {'xs', 'ys'}
            'rkf45' : RKF45 result {'xs', 'ys'}
            'method_names' : list of method names
            'method_colors' : list of colors for plotting
        Returns None on error.
        """
        euler = CalcEngine.ode_solve_euler(expr, x0, y0, x_end, n_steps)
        improved_euler = CalcEngine.ode_solve_improved_euler(expr, x0, y0, x_end, n_steps)
        midpoint = CalcEngine.ode_solve_midpoint(expr, x0, y0, x_end, n_steps)
        rk4 = CalcEngine.ode_solve_rk4(expr, x0, y0, x_end, n_steps)
        rkf45 = CalcEngine.ode_solve_rkf45(expr, x0, y0, x_end)

        if not all([euler, improved_euler, midpoint, rk4, rkf45]):
            return None

        return {
            'euler': euler,
            'improved_euler': improved_euler,
            'midpoint': midpoint,
            'rk4': rk4,
            'rkf45': rkf45,
            'method_names': ['Euler (1st)', 'Improved Euler (2nd)', 'Midpoint (2nd)', 'RK4 (4th)', 'RKF45 (Adaptive)'],
            'method_colors': ['#f38ba8', '#fab387', '#f9e2af', '#a6e3a1', '#89b4fa'],
        }

    @staticmethod
    def polynomial_regression(xs: List[float], ys: List[float], degree: int = 2) -> Optional[Dict[str, object]]:
        """Compute polynomial regression y = c_n*x^n + ... + c_1*x + c_0.

        Returns a dict with keys:
            'coeffs'    : list of coefficients [c_n, ..., c_1, c_0] (highest degree first)
            'r_squared' : R²
            'equation'  : formatted equation string
            'xs_fit'    : x values for fitted curve
            'ys_fit'    : y values for fitted curve
        Returns None on error.
        """
        if len(xs) < degree + 1 or len(xs) != len(ys):
            return None
        try:
            import numpy as np
            x_arr = np.array(xs, dtype=float)
            y_arr = np.array(ys, dtype=float)
            mask = np.isfinite(x_arr) & np.isfinite(y_arr)
            x_arr, y_arr = x_arr[mask], y_arr[mask]
            if len(x_arr) < degree + 1:
                return None
            coeffs = np.polyfit(x_arr, y_arr, degree)
            poly = np.poly1d(coeffs)
            y_fit = poly(x_arr)
            y_mean = np.mean(y_arr)
            ss_res = np.sum((y_arr - y_fit) ** 2)
            ss_tot = np.sum((y_arr - y_mean) ** 2)
            r_squared = 1.0 - ss_res / ss_tot if ss_tot != 0 else (1.0 if ss_res == 0 else 0.0)
            # Sort x for smooth plotting
            x_sorted = np.sort(x_arr)
            y_sorted = poly(x_sorted)
            # Build equation string
            terms: List[str] = []
            for i, c in enumerate(coeffs):
                power = degree - i
                if abs(c) < 1e-12:
                    continue
                if power == 0:
                    terms.append(f"{c:.6g}")
                elif power == 1:
                    terms.append(f"{c:.6g}*x")
                else:
                    terms.append(f"{c:.6g}*x^{power}")
            eq = "y = " + " + ".join(terms).replace("+ -", "- ") if terms else "y = 0"
            return {
                'coeffs': coeffs.tolist(),
                'r_squared': float(r_squared),
                'equation': eq,
                'xs_fit': x_sorted.tolist(),
                'ys_fit': y_sorted.tolist(),
            }
        except Exception:
            return None

    @staticmethod
    def exponential_regression(xs: List[float], ys: List[float]) -> Optional[Dict[str, object]]:
        """Compute exponential fit y = a * e^(b*x) via linearization: ln(y) = ln(a) + b*x.

        Returns a dict with keys:
            'a'         : coefficient a
            'b'         : exponent b
            'r_squared' : R²
            'equation'  : formatted equation string
            'xs_fit'    : x values for fitted curve
            'ys_fit'    : y values for fitted curve
        Returns None on error.
        """
        if len(xs) < 2 or len(xs) != len(ys):
            return None
        try:
            import numpy as np
            x_arr = np.array(xs, dtype=float)
            y_arr = np.array(ys, dtype=float)
            mask = np.isfinite(x_arr) & np.isfinite(y_arr) & (y_arr > 0)
            x_arr, y_arr = x_arr[mask], y_arr[mask]
            if len(x_arr) < 2:
                return None
            ln_y = np.log(y_arr)
            x_mean = np.mean(x_arr)
            ln_mean = np.mean(ln_y)
            ss_xy = np.sum((x_arr - x_mean) * (ln_y - ln_mean))
            ss_xx = np.sum((x_arr - x_mean) ** 2)
            if ss_xx == 0:
                return None
            b = ss_xy / ss_xx
            ln_a = ln_mean - b * x_mean
            a = np.exp(ln_a)
            y_fit = a * np.exp(b * x_arr)
            y_mean = np.mean(y_arr)
            ss_res = np.sum((y_arr - y_fit) ** 2)
            ss_tot = np.sum((y_arr - y_mean) ** 2)
            r_squared = 1.0 - ss_res / ss_tot if ss_tot != 0 else (1.0 if ss_res == 0 else 0.0)
            x_sorted = np.sort(x_arr)
            y_sorted = a * np.exp(b * x_sorted)
            eq = f"y = {a:.6g} * e^({b:.6g}*x)"
            return {
                'a': float(a),
                'b': float(b),
                'r_squared': float(r_squared),
                'equation': eq,
                'xs_fit': x_sorted.tolist(),
                'ys_fit': y_sorted.tolist(),
            }
        except Exception:
            return None

    @staticmethod
    def power_regression(xs: List[float], ys: List[float]) -> Optional[Dict[str, object]]:
        """Compute power fit y = a * x^b via linearization: ln(y) = ln(a) + b*ln(x).

        Returns a dict with keys:
            'a'         : coefficient a
            'b'         : exponent b
            'r_squared' : R²
            'equation'  : formatted equation string
            'xs_fit'    : x values for fitted curve
            'ys_fit'    : y values for fitted curve
        Returns None on error.
        """
        if len(xs) < 2 or len(xs) != len(ys):
            return None
        try:
            import numpy as np
            x_arr = np.array(xs, dtype=float)
            y_arr = np.array(ys, dtype=float)
            mask = np.isfinite(x_arr) & np.isfinite(y_arr) & (x_arr > 0) & (y_arr > 0)
            x_arr, y_arr = x_arr[mask], y_arr[mask]
            if len(x_arr) < 2:
                return None
            ln_x = np.log(x_arr)
            ln_y = np.log(y_arr)
            ln_x_mean = np.mean(ln_x)
            ln_y_mean = np.mean(ln_y)
            ss_xy = np.sum((ln_x - ln_x_mean) * (ln_y - ln_y_mean))
            ss_xx = np.sum((ln_x - ln_x_mean) ** 2)
            if ss_xx == 0:
                return None
            b = ss_xy / ss_xx
            ln_a = ln_y_mean - b * ln_x_mean
            a = np.exp(ln_a)
            y_fit = a * np.power(x_arr, b)
            y_mean = np.mean(y_arr)
            ss_res = np.sum((y_arr - y_fit) ** 2)
            ss_tot = np.sum((y_arr - y_mean) ** 2)
            r_squared = 1.0 - ss_res / ss_tot if ss_tot != 0 else (1.0 if ss_res == 0 else 0.0)
            x_sorted = np.sort(x_arr)
            y_sorted = a * np.power(x_sorted, b)
            eq = f"y = {a:.6g} * x^{b:.6g}"
            return {
                'a': float(a),
                'b': float(b),
                'r_squared': float(r_squared),
                'equation': eq,
                'xs_fit': x_sorted.tolist(),
                'ys_fit': y_sorted.tolist(),
            }
        except Exception:
            return None

    # Base conversion methods
    @staticmethod
    def convert_base(value: str, from_base: int, to_base: int) -> Optional[str]:
        """Convert a number string from one base to another.

        Args:
            value: the number string to convert
            from_base: source base (2-36)
            to_base: target base (2-36)

        Returns the converted string, or None on error.
        """
        buf = ctypes.create_string_buffer(128)
        result = _lib.convert_base(value.encode("utf-8"), from_base, to_base,
                                    buf, 128)
        if result <= 0:
            return None
        return buf.value.decode("utf-8")

    @staticmethod
    def base_to_long(value: str, base: int) -> Optional[int]:
        """Parse a number string in the given base and return its integer value."""
        result = _lib.base_to_long(value.encode("utf-8"), base)
        err = _lib.get_last_error()
        if err and err.decode("utf-8"):
            return None
        return int(result)

    @staticmethod
    def long_to_base(n: int, base: int) -> Optional[str]:
        """Convert an integer to a string in the given base."""
        buf = ctypes.create_string_buffer(128)
        result = _lib.long_to_base(n, base, buf, 128)
        if result <= 0:
            return None
        return buf.value.decode("utf-8")

    @staticmethod
    def convert_base_all(value: str, from_base: int) -> Optional[Dict[str, str]]:
        """Convert a number string to binary, octal, decimal, and hexadecimal.

        Returns a dict with keys 'bin', 'oct', 'dec', 'hex', or None on error.
        """
        bin_buf = ctypes.create_string_buffer(128)
        oct_buf = ctypes.create_string_buffer(128)
        dec_buf = ctypes.create_string_buffer(128)
        hex_buf = ctypes.create_string_buffer(128)
        _lib.convert_base_all(value.encode("utf-8"), from_base,
                               bin_buf, 128, oct_buf, 128,
                               dec_buf, 128, hex_buf, 128)
        err = _lib.get_last_error()
        if err and err.decode("utf-8"):
            return None
        return {
            'bin': bin_buf.value.decode("utf-8"),
            'oct': oct_buf.value.decode("utf-8"),
            'dec': dec_buf.value.decode("utf-8"),
            'hex': hex_buf.value.decode("utf-8"),
        }

    # Volume of revolution functions
    @staticmethod
    def volume_disk(expr: str, a: float, b: float,
                    tol: float = 1e-8) -> Optional[float]:
        """Compute volume of revolution using the disk method.
        
        V = π ∫_a^b [f(x)]² dx
        Rotates f(x) around the x-axis.
        """
        result = _lib.volume_disk(expr.encode("utf-8"), a, b, tol)
        return None if _is_invalid(result) else result

    @staticmethod
    def volume_washer(expr_f: str, expr_g: str, a: float, b: float,
                      tol: float = 1e-8) -> Optional[float]:
        """Compute volume of revolution using the washer method.
        
        V = π ∫_a^b ([f(x)]² - [g(x)]²) dx
        Rotates the region between f(x) and g(x) around the x-axis.
        """
        result = _lib.volume_washer(expr_f.encode("utf-8"),
                                     expr_g.encode("utf-8"),
                                     a, b, tol)
        return None if _is_invalid(result) else result

    @staticmethod
    def volume_shell(expr: str, a: float, b: float,
                     tol: float = 1e-8) -> Optional[float]:
        """Compute volume of revolution using the shell method.
        
        V = 2π ∫_a^b x·f(x) dx
        Rotates f(x) around the y-axis.
        """
        result = _lib.volume_shell(expr.encode("utf-8"), a, b, tol)
        return None if _is_invalid(result) else result

    @staticmethod
    def logarithmic_regression(xs: List[float], ys: List[float]) -> Optional[Dict[str, object]]:
        """Compute logarithmic fit y = a + b * ln(x).

        Returns a dict with keys:
            'a'         : constant a
            'b'         : coefficient b
            'r_squared' : R²
            'equation'  : formatted equation string
            'xs_fit'    : x values for fitted curve
            'ys_fit'    : y values for fitted curve
        Returns None on error.
        """
        if len(xs) < 2 or len(xs) != len(ys):
            return None
        try:
            import numpy as np
            x_arr = np.array(xs, dtype=float)
            y_arr = np.array(ys, dtype=float)
            mask = np.isfinite(x_arr) & np.isfinite(y_arr) & (x_arr > 0)
            x_arr, y_arr = x_arr[mask], y_arr[mask]
            if len(x_arr) < 2:
                return None
            ln_x = np.log(x_arr)
            ln_x_mean = np.mean(ln_x)
            y_mean = np.mean(y_arr)
            ss_xy = np.sum((ln_x - ln_x_mean) * (y_arr - y_mean))
            ss_xx = np.sum((ln_x - ln_x_mean) ** 2)
            if ss_xx == 0:
                return None
            b = ss_xy / ss_xx
            a = y_mean - b * ln_x_mean
            y_fit = a + b * ln_x
            ss_res = np.sum((y_arr - y_fit) ** 2)
            ss_tot = np.sum((y_arr - y_mean) ** 2)
            r_squared = 1.0 - ss_res / ss_tot if ss_tot != 0 else (1.0 if ss_res == 0 else 0.0)
            x_sorted = np.sort(x_arr)
            y_sorted = a + b * np.log(x_sorted)
            sign = "+" if b >= 0 else "-"
            eq = f"y = {a:.6g} {sign} {abs(b):.6g} * ln(x)"
            return {
                'a': float(a),
                'b': float(b),
                'r_squared': float(r_squared),
                'equation': eq,
                'xs_fit': x_sorted.tolist(),
                'ys_fit': y_sorted.tolist(),
            }
        except Exception:
            return None

    # Custom function registry
    @staticmethod
    def custom_func_define(name: str, body: str) -> bool:
        """Define a custom function: f(x) = body.
        
        After definition, the function can be used in any expression as name(expr).
        Returns True on success, False on error.
        """
        result = _lib.custom_func_define(name.encode("utf-8"), body.encode("utf-8"))
        return result != 0

    @staticmethod
    def custom_func_clear() -> None:
        """Clear all custom function definitions."""
        _lib.custom_func_clear()

    @staticmethod
    def custom_func_delete(name: str) -> bool:
        """Delete a custom function by name. Returns True if found and deleted."""
        result = _lib.custom_func_delete(name.encode("utf-8"))
        return result != 0

    @staticmethod
    def custom_func_list() -> str:
        """List all custom functions as 'name(x)=body;...' string."""
        buf = ctypes.create_string_buffer(4096)
        _lib.custom_func_list(buf, 4096)
        return buf.value.decode("utf-8") if buf.value else ""

    # Calculation History
    @staticmethod
    def history_add(expr: str, result: float) -> None:
        """Add an expression and its result to the history buffer."""
        _lib.history_add(expr.encode("utf-8"), result)

    @staticmethod
    def history_count() -> int:
        """Get the number of history entries (max 10)."""
        return _lib.history_count()

    @staticmethod
    def history_clear() -> None:
        """Clear all history entries."""
        _lib.history_clear()

    @staticmethod
    def history_get_all() -> str:
        """Get all history entries as a formatted string 'expr=result;...'"""
        buf = ctypes.create_string_buffer(8192)
        _lib.history_get_all(buf, 8192)
        return buf.value.decode("utf-8") if buf.value else ""

    @staticmethod
    def laplace_transform(expr: str, s: float) -> float:
        """Compute Laplace transform L{f(t)}(s). Expression uses variable t."""
        result = _lib.laplace_transform(expr.encode("utf-8"), s)
        if _is_invalid(result):
            err = _lib.get_last_error()
            raise ValueError(err.decode("utf-8") if err else "Laplace transform failed")
        return result

    @staticmethod
    def inverse_laplace(expr: str, t: float) -> float:
        """Compute inverse Laplace transform f(t) given F(s). Expression uses variable s."""
        result = _lib.inverse_laplace(expr.encode("utf-8"), t)
        if _is_invalid(result):
            err = _lib.get_last_error()
            raise ValueError(err.decode("utf-8") if err else "Inverse Laplace transform failed")
        return result

    @staticmethod
    def interp_akima(xs: List[float], ys: List[float], x: float) -> Optional[float]:
        """Akima interpolation on data points (xs, ys) evaluated at x.

        Uses Akima's method which reduces overshoot compared to cubic spline.
        Requires at least 2 data points with distinct x values.
        """
        n = len(xs)
        if n != len(ys) or n < 2:
            return None
        arr_x = (ctypes.c_double * n)(*xs)
        arr_y = (ctypes.c_double * n)(*ys)
        result = _lib.interp_akima(arr_x, arr_y, n, x)
        return None if _is_invalid(result) else result

    @staticmethod
    def interp_natural_spline(xs: List[float], ys: List[float], x: float) -> Optional[float]:
        """Natural cubic spline interpolation with S''(x₀)=S''(xₙ)=0 boundary conditions.

        Requires at least 2 data points with distinct x values.
        """
        n = len(xs)
        if n != len(ys) or n < 2:
            return None
        arr_x = (ctypes.c_double * n)(*xs)
        arr_y = (ctypes.c_double * n)(*ys)
        result = _lib.interp_natural_spline(arr_x, arr_y, n, x)
        return None if _is_invalid(result) else result
