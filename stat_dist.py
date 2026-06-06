"""
Statistical Distribution Calculator for SuperCalculator.

Implements common probability distributions using only numpy (no scipy).
Supports:
  - Normal (Gaussian) distribution
  - Student's t-distribution
  - Chi-squared distribution
  - F-distribution
  - Binomial distribution
  - Poisson distribution

Each distribution provides:
  - PDF / PMF (probability density / mass function)
  - CDF (cumulative distribution function)
  - PPF (percent-point function / inverse CDF)
  - Random sampling (for visualization)
"""

import numpy as np
from typing import Tuple, Optional, Dict


# ---------------------------------------------------------------------------
#  Helper: Gamma and Beta functions via Lanczos approximation
# ---------------------------------------------------------------------------

def _gamma_lanczos(z: np.ndarray) -> np.ndarray:
    """Lanczos approximation for the Gamma function."""
    z = np.asarray(z, dtype=np.float64)
    # Reflection formula for z < 0.5
    mask = z < 0.5
    result = np.zeros_like(z)
    if np.any(mask):
        result[mask] = np.pi / (
            np.sin(np.pi * z[mask]) * _gamma_lanczos(1.0 - z[mask])
        )
    if np.any(~mask):
        zz = z[~mask] - 1.0
        g = 7
        c = np.array([
            0.99999999999980993, 676.5203681218851, -1259.1392167224028,
            771.32342877765313, -176.61502916214059, 12.507343278686905,
            -0.13857109526572012, 9.9843695780195716e-6, 1.5056327351493116e-7
        ])
        x = c[0]
        for k in range(1, len(c)):
            x += c[k] / (zz + k)
        t = zz + g + 0.5
        result[~mask] = np.sqrt(2 * np.pi) * (t ** (zz + 0.5)) * np.exp(-t) * x
    return result


def _gamma_scalar(z: float) -> float:
    """Scalar wrapper for _gamma_lanczos."""
    return float(_gamma_lanczos(np.array([z]))[0])


def _beta_inc_reg(a: float, b: float, x: float) -> float:
    """Regularized incomplete beta function I_x(a, b) via Gauss-Legendre quadrature."""
    if x <= 0.0:
        return 0.0
    if x >= 1.0:
        return 1.0
    # Use symmetry if x > (a+1)/(a+b+2)
    if x > (a + 1) / (a + b + 2):
        return 1.0 - _beta_inc_reg(b, a, 1.0 - x)
    lbeta = np.log(_gamma_scalar(a)) + np.log(_gamma_scalar(b)) - np.log(_gamma_scalar(a + b))

    # Use composite Simpson's rule with fixed steps (fast and accurate enough)
    n = 500  # number of subintervals (must be even)
    h = x / n
    # Simpson's rule: h/3 * (f(0) + 4*f(h) + 2*f(2h) + ... + 4*f((n-1)h) + f(x))
    def integrand(t):
        if t <= 0.0 or t >= 1.0:
            return 0.0
        return np.exp((a - 1) * np.log(t) + (b - 1) * np.log(1.0 - t) - lbeta)

    total = integrand(0.0) + integrand(x)
    for i in range(1, n):
        t = i * h
        if i % 2 == 0:
            total += 2.0 * integrand(t)
        else:
            total += 4.0 * integrand(t)
    result = h / 3.0 * total
    return max(0.0, min(1.0, result))


def _igamma(a: float, x: float) -> float:
    """Lower regularized incomplete gamma function P(a, x) via series."""
    if x < 0.0:
        return 0.0
    if x == 0.0:
        return 0.0
    if x < a + 1:
        # Series representation
        ap = a
        summation = 1.0 / a
        delta = summation
        for n in range(1, 300):
            ap += 1.0
            delta *= x / ap
            summation += delta
            if abs(delta) < abs(summation) * 1e-15:
                break
        return summation * np.exp(-x + a * np.log(x) - np.log(_gamma_scalar(a)))
    else:
        # Continued fraction
        b = x + 1.0 - a
        c = 1e30
        d = 1.0 / b
        h = d
        for i in range(1, 300):
            an = -i * (i - a)
            b += 2.0
            d = an * d + b
            if abs(d) < 1e-30:
                d = 1e-30
            c = b + an / c
            if abs(c) < 1e-30:
                c = 1e-30
            d = 1.0 / d
            delta = d * c
            h *= delta
            if abs(delta - 1.0) < 1e-10:
                break
        return 1.0 - h * np.exp(-x + a * np.log(x) - np.log(_gamma_scalar(a)))


# ---------------------------------------------------------------------------
#  Normal Distribution N(mu, sigma^2)
# ---------------------------------------------------------------------------

class NormalDist:
    """Normal (Gaussian) distribution with parameters mu and sigma."""

    def __init__(self, mu: float = 0.0, sigma: float = 1.0):
        self.mu = float(mu)
        self.sigma = float(abs(sigma))
        if self.sigma == 0:
            raise ValueError("sigma must be positive")

    def pdf(self, x) -> np.ndarray:
        x = np.asarray(x, dtype=np.float64)
        z = (x - self.mu) / self.sigma
        return np.exp(-0.5 * z * z) / (self.sigma * np.sqrt(2 * np.pi))

    def cdf(self, x) -> np.ndarray:
        x = np.asarray(x, dtype=np.float64)
        z = (x - self.mu) / (self.sigma * np.sqrt(2))
        return 0.5 * (1.0 + np.vectorize(lambda t: _erf_approx(t))(z))

    def ppf(self, q) -> float:
        q = float(q)
        if q <= 0 or q >= 1:
            raise ValueError("q must be in (0, 1)")
        return self.mu + self.sigma * np.sqrt(2) * _erfinv_approx(2 * q - 1)

    def sample(self, n: int = 1) -> np.ndarray:
        return np.random.normal(self.mu, self.sigma, n)

    def mean(self) -> float:
        return self.mu

    def var(self) -> float:
        return self.sigma ** 2

    def std(self) -> float:
        return self.sigma


def _erf_approx(x: float) -> float:
    """Approximation of erf(x) using Abramowitz & Stegun."""
    sign = 1 if x >= 0 else -1
    x = abs(x)
    t = 1.0 / (1.0 + 0.3275911 * x)
    poly = t * (0.254829592 + t * (-0.284496736 + t * (1.421413741 + t * (-1.453152027 + t * 1.061405429))))
    return sign * (1.0 - poly * np.exp(-x * x))


def _erfinv_approx(y: float) -> float:
    """Inverse erf using rational approximation (Abramowitz & Stegun 26.2.23)."""
    # For small range, use Newton's method with erf approximation
    if y < -1 or y > 1:
        raise ValueError("y must be in [-1, 1]")
    if abs(y) < 1e-10:
        return y * np.sqrt(np.pi) / 2.0
    # Initial guess
    a = 0.147
    ln = np.log(1 - y * y)
    s = np.sign(y)
    t = 2.0 / (np.pi * a) + ln / 2.0
    result = s * np.sqrt(np.sqrt(t * t - ln / a) - t)
    # Newton refinement
    for _ in range(5):
        e = _erf_approx(result) - y
        de = 2.0 / np.sqrt(np.pi) * np.exp(-result * result)
        result -= e / de
    return result


# ---------------------------------------------------------------------------
#  Student's t-distribution
# ---------------------------------------------------------------------------

class StudentTDist:
    """Student's t-distribution with nu degrees of freedom."""

    def __init__(self, nu: float = 1.0):
        self.nu = float(nu)
        if self.nu <= 0:
            raise ValueError("nu must be positive")

    def pdf(self, x) -> np.ndarray:
        x = np.asarray(x, dtype=np.float64)
        nu = self.nu
        coeff = _gamma_scalar((nu + 1) / 2) / \
                (np.sqrt(nu * np.pi) * _gamma_scalar(nu / 2))
        return coeff * (1.0 + x * x / nu) ** (-(nu + 1) / 2)

    def cdf(self, x) -> np.ndarray:
        x = np.asarray(x, dtype=np.float64)
        result = np.zeros_like(x)
        for i, xi in enumerate(np.nditer(x)):
            xi_val = float(xi)
            if xi_val < -15:
                result.flat[i] = 0.0
            elif xi_val > 15:
                result.flat[i] = 1.0
            else:
                # Use symmetry: CDF(x) = 0.5 + integral from 0 to x of PDF(t) dt
                n = 1000
                if abs(xi_val) < 1e-15:
                    result.flat[i] = 0.5
                elif xi_val > 0:
                    h = xi_val / n
                    total = 0.0
                    for j in range(n):
                        t = j * h
                        total += float(self.pdf(np.array([t]))[0])
                    total += float(self.pdf(np.array([xi_val]))[0]) / 2.0
                    total -= float(self.pdf(np.array([0.0]))[0]) / 2.0
                    result.flat[i] = 0.5 + total * h
                else:
                    # CDF(x) = 1 - CDF(-x) for x < 0
                    h = -xi_val / n
                    total = 0.0
                    for j in range(n):
                        t = -j * h
                        total += float(self.pdf(np.array([t]))[0])
                    total += float(self.pdf(np.array([-xi_val]))[0]) / 2.0
                    total -= float(self.pdf(np.array([0.0]))[0]) / 2.0
                    result.flat[i] = 0.5 - total * h
        return result

    def ppf(self, q) -> float:
        q = float(q)
        if q <= 0 or q >= 1:
            raise ValueError("q must be in (0, 1)")
        # Use bisection with CDF
        lo, hi = -100.0, 100.0
        for _ in range(100):
            mid = (lo + hi) / 2.0
            if float(self.cdf(mid)) < q:
                lo = mid
            else:
                hi = mid
        return (lo + hi) / 2.0

    def mean(self) -> float:
        if self.nu > 1:
            return 0.0
        raise ValueError("mean undefined for nu <= 1")

    def var(self) -> float:
        if self.nu > 2:
            return self.nu / (self.nu - 2)
        raise ValueError("variance undefined for nu <= 2")


# ---------------------------------------------------------------------------
#  Chi-squared distribution
# ---------------------------------------------------------------------------

class ChiSquaredDist:
    """Chi-squared distribution with k degrees of freedom."""

    def __init__(self, k: float = 1.0):
        self.k = float(k)
        if self.k <= 0:
            raise ValueError("k must be positive")

    def pdf(self, x) -> np.ndarray:
        x = np.asarray(x, dtype=np.float64)
        k = self.k
        result = np.zeros_like(x)
        mask = x > 0
        xm = x[mask]
        log_pdf = (k / 2 - 1) * np.log(xm) - xm / 2 - \
                  (k / 2) * np.log(2) - np.log(_gamma_scalar(k / 2))
        result[mask] = np.exp(log_pdf)
        return result

    def cdf(self, x) -> np.ndarray:
        x = np.asarray(x, dtype=np.float64)
        result = np.zeros_like(x)
        for i, xi in enumerate(np.nditer(x)):
            xi_val = float(xi)
            if xi_val <= 0:
                result.flat[i] = 0.0
            else:
                result.flat[i] = _igamma(self.k / 2, xi_val / 2)
        return result

    def ppf(self, q) -> float:
        q = float(q)
        if q <= 0 or q >= 1:
            raise ValueError("q must be in (0, 1)")
        lo, hi = 0.0, 1.0
        while float(self.cdf(hi)) < q:
            hi *= 2
        for _ in range(100):
            mid = (lo + hi) / 2.0
            if float(self.cdf(mid)) < q:
                lo = mid
            else:
                hi = mid
        return (lo + hi) / 2.0

    def mean(self) -> float:
        return self.k

    def var(self) -> float:
        return 2 * self.k


# ---------------------------------------------------------------------------
#  F-distribution
# ---------------------------------------------------------------------------

class FDist:
    """F-distribution with d1 and d2 degrees of freedom."""

    def __init__(self, d1: float = 1.0, d2: float = 1.0):
        self.d1 = float(d1)
        self.d2 = float(d2)
        if self.d1 <= 0 or self.d2 <= 0:
            raise ValueError("d1 and d2 must be positive")

    def pdf(self, x) -> np.ndarray:
        x = np.asarray(x, dtype=np.float64)
        d1, d2 = self.d1, self.d2
        result = np.zeros_like(x)
        mask = x > 0
        xm = x[mask]
        log_pdf = (d1 / 2) * np.log(d1) + (d2 / 2) * np.log(d2) + \
                  ((d1 / 2) - 1) * np.log(xm) - \
                  ((d1 + d2) / 2) * np.log(d1 * xm + d2) + \
                  np.log(_gamma_scalar((d1 + d2) / 2)) - \
                  np.log(_gamma_scalar(d1 / 2)) - \
                  np.log(_gamma_scalar(d2 / 2))
        result[mask] = np.exp(log_pdf)
        return result

    def cdf(self, x) -> np.ndarray:
        x = np.asarray(x, dtype=np.float64)
        result = np.zeros_like(x)
        for i, xi in enumerate(np.nditer(x)):
            xi_val = float(xi)
            if xi_val <= 0:
                result.flat[i] = 0.0
            else:
                z = self.d1 * xi_val / (self.d1 * xi_val + self.d2)
                result.flat[i] = _beta_inc_reg(self.d1 / 2, self.d2 / 2, z)
        return result

    def ppf(self, q) -> float:
        q = float(q)
        if q <= 0 or q >= 1:
            raise ValueError("q must be in (0, 1)")
        lo, hi = 0.001, 1.0
        while float(self.cdf(hi)) < q:
            hi *= 2
        for _ in range(100):
            mid = (lo + hi) / 2.0
            if float(self.cdf(mid)) < q:
                lo = mid
            else:
                hi = mid
        return (lo + hi) / 2.0

    def mean(self) -> float:
        if self.d2 > 2:
            return self.d2 / (self.d2 - 2)
        raise ValueError("mean undefined for d2 <= 2")


# ---------------------------------------------------------------------------
#  Binomial distribution
# ---------------------------------------------------------------------------

class BinomialDist:
    """Binomial distribution B(n, p)."""

    def __init__(self, n: int = 10, p: float = 0.5):
        self.n = int(n)
        self.p = float(p)
        if self.n < 0 or not (0 <= self.p <= 1):
            raise ValueError("n must be non-negative and p in [0, 1]")

    def pmf(self, k) -> np.ndarray:
        k = np.asarray(k, dtype=np.float64)
        result = np.zeros_like(k)
        for i, ki in enumerate(np.nditer(k)):
            ki_val = int(round(float(ki)))
            if 0 <= ki_val <= self.n:
                log_pmf = (np.log(_gamma_scalar(self.n + 1)) -
                           np.log(_gamma_scalar(ki_val + 1)) -
                           np.log(_gamma_scalar(self.n - ki_val + 1)) +
                           ki_val * np.log(self.p) +
                           (self.n - ki_val) * np.log(1 - self.p))
                result.flat[i] = np.exp(log_pmf)
        return result

    def cdf(self, x) -> np.ndarray:
        x = np.asarray(x, dtype=np.float64)
        result = np.zeros_like(x)
        for i, xi in enumerate(np.nditer(x)):
            xi_val = int(np.floor(float(xi)))
            if xi_val < 0:
                result.flat[i] = 0.0
            elif xi_val >= self.n:
                result.flat[i] = 1.0
            else:
                total = 0.0
                for k in range(xi_val + 1):
                    total += float(self.pmf(k))
                result.flat[i] = min(total, 1.0)
        return result

    def ppf(self, q) -> int:
        q = float(q)
        if q <= 0:
            return 0
        if q >= 1:
            return self.n
        total = 0.0
        for k in range(self.n + 1):
            total += float(self.pmf(k))
            if total >= q:
                return k
        return self.n

    def mean(self) -> float:
        return self.n * self.p

    def var(self) -> float:
        return self.n * self.p * (1 - self.p)


# ---------------------------------------------------------------------------
#  Poisson distribution
# ---------------------------------------------------------------------------

class PoissonDist:
    """Poisson distribution Poisson(lambda)."""

    def __init__(self, lam: float = 1.0):
        self.lam = float(lam)
        if self.lam < 0:
            raise ValueError("lambda must be non-negative")

    def pmf(self, k) -> np.ndarray:
        k = np.asarray(k, dtype=np.float64)
        result = np.zeros_like(k)
        for i, ki in enumerate(np.nditer(k)):
            ki_val = int(round(float(ki)))
            if ki_val >= 0:
                log_pmf = ki_val * np.log(self.lam) - self.lam - \
                          np.log(_gamma_scalar(ki_val + 1))
                result.flat[i] = np.exp(log_pmf)
        return result

    def cdf(self, x) -> np.ndarray:
        x = np.asarray(x, dtype=np.float64)
        result = np.zeros_like(x)
        for i, xi in enumerate(np.nditer(x)):
            xi_val = int(np.floor(float(xi)))
            if xi_val < 0:
                result.flat[i] = 0.0
            else:
                total = 0.0
                for k in range(xi_val + 1):
                    total += float(self.pmf(k))
                result.flat[i] = min(total, 1.0)
        return result

    def ppf(self, q) -> int:
        q = float(q)
        if q <= 0:
            return 0
        total = 0.0
        k = 0
        while True:
            total += float(self.pmf(k))
            if total >= q:
                return k
            k += 1
            if k > 1000:
                return k

    def mean(self) -> float:
        return self.lam

    def var(self) -> float:
        return self.lam


# ---------------------------------------------------------------------------
#  Distribution registry
# ---------------------------------------------------------------------------

DISTRIBUTIONS = {
    "normal": {
        "name_en": "Normal (Gaussian)",
        "name_zh": "正态分布（高斯）",
        "params": [("mu", "Mean (μ)", "μ", 0.0), ("sigma", "Std Dev (σ)", "σ", 1.0)],
        "class": NormalDist,
        "pdf_label_en": "PDF",
        "pdf_label_zh": "概率密度函数",
    },
    "t": {
        "name_en": "Student's t",
        "name_zh": "学生 t 分布",
        "params": [("nu", "Degrees of Freedom (ν)", "ν", 5.0)],
        "class": StudentTDist,
        "pdf_label_en": "PDF",
        "pdf_label_zh": "概率密度函数",
    },
    "chi2": {
        "name_en": "Chi-squared",
        "name_zh": "卡方分布",
        "params": [("k", "Degrees of Freedom (k)", "k", 3.0)],
        "class": ChiSquaredDist,
        "pdf_label_en": "PDF",
        "pdf_label_zh": "概率密度函数",
    },
    "f": {
        "name_en": "F-distribution",
        "name_zh": "F 分布",
        "params": [("d1", "df1 (ν₁)", "ν₁", 5.0), ("d2", "df2 (ν₂)", "ν₂", 10.0)],
        "class": FDist,
        "pdf_label_en": "PDF",
        "pdf_label_zh": "概率密度函数",
    },
    "binomial": {
        "name_en": "Binomial",
        "name_zh": "二项分布",
        "params": [("n", "Number of Trials (n)", "n", 20), ("p", "Probability (p)", "p", 0.5)],
        "class": BinomialDist,
        "pdf_label_en": "PMF",
        "pdf_label_zh": "概率质量函数",
    },
    "poisson": {
        "name_en": "Poisson",
        "name_zh": "泊松分布",
        "params": [("lam", "Rate (λ)", "λ", 5.0)],
        "class": PoissonDist,
        "pdf_label_en": "PMF",
        "pdf_label_zh": "概率质量函数",
    },
}


def create_distribution(name: str, **params):
    """Create a distribution instance by name."""
    if name not in DISTRIBUTIONS:
        raise ValueError(f"Unknown distribution: {name}")
    dist_info = DISTRIBUTIONS[name]
    dist_class = dist_info["class"]
    return dist_class(**params)


def get_distribution_names(lang: str = "en") -> list:
    """Get list of distribution names for display."""
    return [(k, v[f"name_{lang}"] if f"name_{lang}" in v else v["name_en"])
            for k, v in DISTRIBUTIONS.items()]


def get_pdf_x_range(dist_name: str, params: dict, n_points: int = 500) -> np.ndarray:
    """Get appropriate x-range for plotting a distribution's PDF/PMF."""
    dist = create_distribution(dist_name, **params)
    if dist_name == "normal":
        mu, sigma = params.get("mu", 0), abs(params.get("sigma", 1))
        return np.linspace(mu - 4 * sigma, mu + 4 * sigma, n_points)
    elif dist_name == "t":
        nu = params.get("nu", 5)
        return np.linspace(-6, 6, n_points)
    elif dist_name == "chi2":
        k = params.get("k", 3)
        return np.linspace(0, max(k + 4 * np.sqrt(2 * k), 1), n_points)
    elif dist_name == "f":
        d1, d2 = params.get("d1", 5), params.get("d2", 10)
        return np.linspace(0.01, min(d2 / max(d2 - 2, 0.1) + 3, 10), n_points)
    elif dist_name == "binomial":
        n = params.get("n", 20)
        return np.arange(0, n + 1, dtype=np.float64)
    elif dist_name == "poisson":
        lam = params.get("lam", 5)
        return np.arange(0, int(lam + 4 * np.sqrt(lam)) + 1, dtype=np.float64)
    else:
        return np.linspace(-5, 5, n_points)
