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
        """Definite integral over [a,b] using Simpson's rule (n must be even)."""
        result = _lib.integrate(expr.encode("utf-8"), a, b, n)
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
    def diff(expr: str, x: float, h: float = 1e-6) -> Optional[float]:
        return CalcEngine.derivative(expr, x, h)

    @staticmethod
    def integral(expr: str, a: float, b: float,
                 n: int = 1000) -> Optional[float]:
        """Definite integral over [a,b] using Simpson's rule (alias for integrate)."""
        return CalcEngine.integrate(expr, a, b, n)

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
