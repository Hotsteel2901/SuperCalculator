"""
Probability Calculator for SuperCalculator.

Provides combinatorics, event probability, conditional probability,
Bayes' theorem, and binomial probability computations.
"""

import math
from typing import Optional, List, Dict


def factorial(n: int) -> Optional[float]:
    """Compute n! for non-negative integers."""
    if n < 0 or n != int(n):
        return None
    n = int(n)
    if n > 170:
        return float('inf')
    return float(math.factorial(n))


def combinations(n: int, r: int) -> Optional[float]:
    """Compute C(n, r) = n! / (r! * (n-r)!)"""
    if n < 0 or r < 0 or r != int(r) or n != int(n):
        return None
    n, r = int(n), int(r)
    if r > n:
        return 0.0
    return float(math.comb(n, r))


def permutations(n: int, r: int) -> Optional[float]:
    """Compute P(n, r) = n! / (n-r)!"""
    if n < 0 or r < 0 or r != int(r) or n != int(n):
        return None
    n, r = int(n), int(r)
    if r > n:
        return 0.0
    return float(math.perm(n, r))


def event_union(p_a: float, p_b: float, p_a_and_b: float = 0.0) -> Optional[float]:
    """Compute P(A ∪ B) = P(A) + P(B) - P(A ∩ B)."""
    if not (0 <= p_a <= 1 and 0 <= p_b <= 1 and 0 <= p_a_and_b <= 1):
        return None
    result = p_a + p_b - p_a_and_b
    return max(0.0, min(1.0, result))


def event_intersection(p_a: float, p_b: float, independent: bool = True,
                       p_b_given_a: Optional[float] = None) -> Optional[float]:
    """Compute P(A ∩ B).
    
    If independent: P(A ∩ B) = P(A) * P(B)
    If not independent: P(A ∩ B) = P(A) * P(B|A)
    """
    if not (0 <= p_a <= 1 and 0 <= p_b <= 1):
        return None
    if independent:
        return p_a * p_b
    else:
        if p_b_given_a is None or not (0 <= p_b_given_a <= 1):
            return None
        return p_a * p_b_given_a


def event_complement(p_a: float) -> Optional[float]:
    """Compute P(A') = 1 - P(A)."""
    if not (0 <= p_a <= 1):
        return None
    return 1.0 - p_a


def conditional_probability(p_a_and_b: float, p_b: float) -> Optional[float]:
    """Compute P(A|B) = P(A ∩ B) / P(B)."""
    if not (0 <= p_a_and_b <= 1 and 0 <= p_b <= 1):
        return None
    if p_b == 0:
        return None
    return p_a_and_b / p_b


def bayes_theorem(p_b_given_a: float, p_a: float, p_b: float) -> Optional[float]:
    """Compute P(A|B) = P(B|A) * P(A) / P(B) (Bayes' theorem)."""
    if not (0 <= p_b_given_a <= 1 and 0 <= p_a <= 1 and 0 <= p_b <= 1):
        return None
    if p_b == 0:
        return None
    return (p_b_given_a * p_a) / p_b


def bayes_theorem_full(p_b_given_a: float, p_a: float,
                       p_b_given_not_a: float) -> Optional[Dict[str, float]]:
    """Compute full Bayes' theorem with prior and evidence.
    
    Given:
        P(B|A), P(A), P(B|A')
    Computes:
        P(A|B) using total probability: P(B) = P(B|A)*P(A) + P(B|A')*P(A')
    
    Returns dict with:
        p_a, p_not_a, p_b, p_b_given_a, p_b_given_not_a,
        p_a_given_b, p_not_a_given_b
    """
    if not (0 <= p_b_given_a <= 1 and 0 <= p_a <= 1 and 0 <= p_b_given_not_a <= 1):
        return None
    p_not_a = 1.0 - p_a
    p_b = p_b_given_a * p_a + p_b_given_not_a * p_not_a
    if p_b == 0:
        return None
    p_a_given_b = (p_b_given_a * p_a) / p_b
    p_not_a_given_b = 1.0 - p_a_given_b
    return {
        'p_a': p_a,
        'p_not_a': p_not_a,
        'p_b': p_b,
        'p_b_given_a': p_b_given_a,
        'p_b_given_not_a': p_b_given_not_a,
        'p_a_given_b': p_a_given_b,
        'p_not_a_given_b': p_not_a_given_b,
    }


def binomial_probability(n: int, k: int, p: float) -> Optional[float]:
    """Compute P(X = k) for Binomial(n, p).
    
    P(X = k) = C(n, k) * p^k * (1-p)^(n-k)
    Uses log-space computation to avoid overflow for large n.
    """
    if n < 0 or k < 0 or k > n or n != int(n) or k != int(k):
        return None
    if not (0 <= p <= 1):
        return None
    n, k = int(n), int(k)
    if p == 0.0:
        return 1.0 if k == 0 else 0.0
    if p == 1.0:
        return 1.0 if k == n else 0.0
    # Use log-space for large n to avoid overflow
    if n > 170:
        log_result = (math.lgamma(n + 1) - math.lgamma(k + 1) - math.lgamma(n - k + 1)
                     + k * math.log(p) + (n - k) * math.log(1 - p))
        return math.exp(log_result)
    return float(math.comb(n, k)) * (p ** k) * ((1 - p) ** (n - k))


def binomial_cdf(n: int, k: int, p: float) -> Optional[float]:
    """Compute P(X <= k) for Binomial(n, p)."""
    if n < 0 or k < 0 or n != int(n) or k != int(k):
        return None
    if not (0 <= p <= 1):
        return None
    n, k = int(n), int(k)
    total = 0.0
    for i in range(min(k, n) + 1):
        pbm = binomial_probability(n, i, p)
        if pbm is not None:
            total += pbm
    return min(total, 1.0)


def binomial_mean(n: int, p: float) -> Optional[float]:
    """Compute E[X] = n*p for Binomial(n, p)."""
    if n < 0 or n != int(n) or not (0 <= p <= 1):
        return None
    return float(int(n)) * p


def binomial_variance(n: int, p: float) -> Optional[float]:
    """Compute Var(X) = n*p*(1-p) for Binomial(n, p)."""
    if n < 0 or n != int(n) or not (0 <= p <= 1):
        return None
    return float(int(n)) * p * (1 - p)


def poisson_probability(lam: float, k: int) -> Optional[float]:
    """Compute P(X = k) for Poisson distribution with rate lambda.
    
    P(X = k) = e^(-lambda) * lambda^k / k!
    Uses log-space computation to avoid overflow for large lambda or k.
    """
    if lam < 0 or k < 0 or k != int(k):
        return None
    k = int(k)
    if lam == 0:
        return 1.0 if k == 0 else 0.0
    if k == 0:
        return math.exp(-lam)
    # Use log-space to avoid overflow
    log_result = -lam + k * math.log(lam) - math.lgamma(k + 1)
    return math.exp(log_result)


def geometric_probability(p: float, k: int) -> Optional[float]:
    """Compute P(X = k) for Geometric distribution (first success on trial k).
    
    P(X = k) = (1-p)^(k-1) * p, for k = 1, 2, 3, ...
    """
    if k < 1 or k != int(k) or not (0 < p <= 1):
        return None
    k = int(k)
    return ((1 - p) ** (k - 1)) * p


def hypergeometric_probability(N: int, K: int, n: int, k: int) -> Optional[float]:
    """Compute P(X = k) for Hypergeometric distribution.
    
    Population N, K success states, sample n, k observed successes.
    P(X = k) = C(K,k) * C(N-K, n-k) / C(N,n)
    """
    if not all(x == int(x) and x >= 0 for x in [N, K, n, k]):
        return None
    _N, _K, _n, _k = int(N), int(K), int(n), int(k)
    if _K > _N or _n > _N or _k > min(_K, _n) or _k < max(0, _n - (_N - _K)):
        return 0.0
    # Use log-space for large N to avoid math.comb overflow
    if _N > 500:
        log_num = (math.lgamma(_K + 1) - math.lgamma(_k + 1) - math.lgamma(_K - _k + 1)
                   + math.lgamma(_N - _K + 1) - math.lgamma(_n - _k + 1) - math.lgamma(_N - _K - _n + _k + 1))
        log_den = math.lgamma(_N + 1) - math.lgamma(_n + 1) - math.lgamma(_N - _n + 1)
        return math.exp(log_num - log_den)
    return (math.comb(_K, _k) * math.comb(_N - _K, _n - _k)) / math.comb(_N, _n)


def expected_value(values: List[float], probabilities: List[float]) -> Optional[float]:
    """Compute E[X] = sum(x_i * p_i)."""
    if len(values) != len(probabilities) or len(values) == 0:
        return None
    if not all(0 <= p <= 1 for p in probabilities):
        return None
    total_p = sum(probabilities)
    if abs(total_p - 1.0) > 1e-6:
        return None
    return sum(v * p for v, p in zip(values, probabilities))


def variance_discrete(values: List[float], probabilities: List[float]) -> Optional[float]:
    """Compute Var(X) = E[X^2] - (E[X])^2."""
    ev = expected_value(values, probabilities)
    if ev is None:
        return None
    ev2 = expected_value([v ** 2 for v in values], probabilities)
    if ev2 is None:
        return None
    return max(0.0, ev2 - ev ** 2)
