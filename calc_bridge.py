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

_lib.get_last_error.argtypes = []
_lib.get_last_error.restype = ctypes.c_char_p


def _isnan(x: float) -> bool:
    try:
        return _math.isnan(x)
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
        return None if _isnan(result) else result

    @staticmethod
    def evaluate_xy(expr: str, x: float, y: float) -> Optional[float]:
        """Evaluate expression f(x,y) at given x and y."""
        result = _lib.evaluate_xy(expr.encode("utf-8"), x, y)
        return None if _isnan(result) else result

    @staticmethod
    def evaluate_array(expr: str, xs: List[float]) -> List[Optional[float]]:
        """Evaluate expression at multiple x values (batched)."""
        n = len(xs)
        arr_x = (ctypes.c_double * n)(*xs)
        arr_y = (ctypes.c_double * n)()
        _lib.evaluate_array(expr.encode("utf-8"), arr_x, arr_y, n)
        return [None if _isnan(arr_y[i]) else arr_y[i] for i in range(n)]

    @staticmethod
    def derivative(expr: str, x: float, h: float = 1e-6) -> Optional[float]:
        """First derivative f'(x) via central difference."""
        result = _lib.derivative(expr.encode("utf-8"), x, h)
        return None if _isnan(result) else result

    @staticmethod
    def derivative2(expr: str, x: float, h: float = 1e-6) -> Optional[float]:
        """Second derivative f''(x) via central difference."""
        result = _lib.derivative2(expr.encode("utf-8"), x, h)
        return None if _isnan(result) else result

    @staticmethod
    def integrate(expr: str, a: float, b: float,
                  n: int = 1000) -> Optional[float]:
        """Definite integral over [a,b] using Simpson's rule (n must be even)."""
        result = _lib.integrate(expr.encode("utf-8"), a, b, n)
        return None if _isnan(result) else result

    @staticmethod
    def integrate_adaptive(expr: str, a: float, b: float,
                           tol: float = 1e-8) -> Optional[float]:
        """Definite integral with adaptive step refinement."""
        result = _lib.integrate_adaptive(expr.encode("utf-8"), a, b, tol)
        return None if _isnan(result) else result

    @staticmethod
    def solve(expr: str, guess: float = 0.0, xmin: float = -100.0,
              xmax: float = 100.0, tol: float = 1e-8,
              max_iter: int = 100) -> Optional[float]:
        """Solve f(x)=0 using Newton-Raphson with bisection fallback."""
        result = _lib.solve_equation(expr.encode("utf-8"),
                                     guess, xmin, xmax, tol, max_iter)
        return None if _isnan(result) else result

    @staticmethod
    def solve_bisection(expr: str, a: float, b: float,
                        tol: float = 1e-8,
                        max_iter: int = 200) -> Optional[float]:
        """Solve f(x)=0 using pure bisection (requires sign change on [a,b])."""
        result = _lib.solve_bisection(expr.encode("utf-8"), a, b, tol, max_iter)
        return None if _isnan(result) else result

    @staticmethod
    def find_minimum(expr: str, a: float, b: float,
                     tol: float = 1e-8,
                     max_iter: int = 200) -> Optional[float]:
        """Find a local minimum of f(x) on [a, b] using golden-section search."""
        result = _lib.find_minimum(expr.encode("utf-8"), a, b, tol, max_iter)
        return None if _isnan(result) else result

    @staticmethod
    def find_maximum(expr: str, a: float, b: float,
                     tol: float = 1e-8,
                     max_iter: int = 200) -> Optional[float]:
        """Find a local maximum of f(x) on [a, b] using golden-section search."""
        result = _lib.find_maximum(expr.encode("utf-8"), a, b, tol, max_iter)
        return None if _isnan(result) else result

    @staticmethod
    def get_last_error() -> str:
        """Return the last error message from the C core."""
        raw = _lib.get_last_error()
        return raw.decode("utf-8") if raw else ""

    @staticmethod
    def diff(expr: str, x: float, h: float = 1e-6) -> Optional[float]:
        return CalcEngine.derivative(expr, x, h)

    @staticmethod
    def integral(expr: str, a: float, b: float,
                 n: int = 1000) -> Optional[float]:
        """Definite integral over [a,b] using Simpson's rule (alias for integrate)."""
        return CalcEngine.integrate(expr, a, b, n)
