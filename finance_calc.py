"""
Finance Calculator for SuperCalculator.

Provides loan, compound interest, investment (NPV/IRR), and depreciation computations.
"""

import math
from typing import Optional, List, Dict, Tuple


def loan_monthly_payment(principal: float, annual_rate: float,
                         months: int) -> Optional[float]:
    """Compute monthly payment for an amortizing loan.

    Parameters
    ----------
    principal : float
        Loan amount (must be > 0).
    annual_rate : float
        Annual interest rate as a percentage (e.g. 5.0 for 5%).
    months : int
        Total number of payment months (must be > 0).

    Returns
    -------
    float or None
        Monthly payment amount, or None on invalid input.
    """
    if principal <= 0 or months <= 0 or annual_rate < 0:
        return None
    if annual_rate == 0:
        return principal / months
    r = annual_rate / 100.0 / 12.0
    factor = (1 + r) ** months
    return principal * r * factor / (factor - 1)


def loan_total_payment(principal: float, annual_rate: float,
                       months: int) -> Optional[float]:
    """Compute total amount paid over the life of the loan."""
    pmt = loan_monthly_payment(principal, annual_rate, months)
    if pmt is None:
        return None
    return pmt * months


def loan_total_interest(principal: float, annual_rate: float,
                        months: int) -> Optional[float]:
    """Compute total interest paid over the life of the loan."""
    total = loan_total_payment(principal, annual_rate, months)
    if total is None:
        return None
    return total - principal


def loan_amortization_schedule(principal: float, annual_rate: float,
                               months: int) -> Optional[List[Dict[str, float]]]:
    """Generate a month-by-month amortization schedule.

    Returns a list of dicts, each with keys:
        month, payment, interest, principal_paid, balance
    """
    if principal <= 0 or months <= 0:
        return None
    pmt = loan_monthly_payment(principal, annual_rate, months)
    if pmt is None:
        return None
    r = annual_rate / 100.0 / 12.0
    schedule = []
    balance = principal
    for m in range(1, months + 1):
        interest = balance * r
        if m == months:
            principal_paid = balance
            payment = principal_paid + interest
        else:
            payment = pmt
            principal_paid = payment - interest
        balance -= principal_paid
        if balance < 0:
            balance = 0.0
        schedule.append({
            'month': m,
            'payment': payment,
            'interest': interest,
            'principal_paid': principal_paid,
            'balance': balance,
        })
    return schedule


def compound_future_value(present_value: float, annual_rate: float,
                          years: float,
                          compounds_per_year: int = 1) -> Optional[float]:
    """Compute future value with compound interest.

    FV = PV * (1 + r/n)^(n*t)
    """
    if present_value <= 0 or years < 0 or compounds_per_year <= 0:
        return None
    r = annual_rate / 100.0
    n = compounds_per_year
    t = years
    return present_value * (1 + r / n) ** (n * t)


def compound_present_value(future_value: float, annual_rate: float,
                           years: float,
                           compounds_per_year: int = 1) -> Optional[float]:
    """Compute present value given a future value with compound interest."""
    if future_value <= 0 or years < 0 or compounds_per_year <= 0:
        return None
    r = annual_rate / 100.0
    n = compounds_per_year
    t = years
    denominator = (1 + r / n) ** (n * t)
    if denominator == 0:
        return None
    return future_value / denominator


def continuous_compound_fv(present_value: float, annual_rate: float,
                           years: float) -> Optional[float]:
    """Compute future value with continuous compounding: FV = PV * e^(r*t)."""
    if present_value <= 0 or years < 0:
        return None
    r = annual_rate / 100.0
    return present_value * math.exp(r * years)


def continuous_compound_pv(future_value: float, annual_rate: float,
                           years: float) -> Optional[float]:
    """Compute present value with continuous compounding."""
    if future_value <= 0 or years < 0:
        return None
    r = annual_rate / 100.0
    return future_value * math.exp(-r * years)


def effective_annual_rate(nominal_rate: float,
                          compounds_per_year: int = 1) -> Optional[float]:
    """Compute effective annual rate from nominal rate.

    EAR = (1 + r/n)^n - 1
    """
    if compounds_per_year <= 0:
        return None
    r = nominal_rate / 100.0
    n = compounds_per_year
    return ((1 + r / n) ** n - 1) * 100.0


def npv(rate: float, cashflows: List[float]) -> Optional[float]:
    """Compute Net Present Value.

    NPV = sum(CF_t / (1+r)^t) for t=0..n-1

    Parameters
    ----------
    rate : float
        Discount rate as a percentage (e.g. 10.0 for 10%).
    cashflows : list of float
        Cash flows starting at t=0.
    """
    if not cashflows:
        return None
    r = rate / 100.0
    return sum(cf / (1 + r) ** t for t, cf in enumerate(cashflows))


def irr(cashflows: List[float], guess: float = 10.0,
        tol: float = 1e-10, max_iter: int = 200) -> Optional[float]:
    """Compute Internal Rate of Return using Newton-Raphson.

    Returns the rate (as a percentage) that makes NPV = 0.
    """
    if not cashflows or len(cashflows) < 2:
        return None
    r = guess / 100.0
    for _ in range(max_iter):
        pv = sum(cf / (1 + r) ** t for t, cf in enumerate(cashflows))
        dpv = sum(-t * cf / (1 + r) ** (t + 1)
                  for t, cf in enumerate(cashflows))
        if abs(dpv) < 1e-18:
            break
        r_new = r - pv / dpv
        if abs(r_new - r) < tol:
            return r_new * 100.0
        r = r_new
    return r * 100.0 if abs(
        sum(cf / (1 + r) ** t for t, cf in enumerate(cashflows))) < 1e-6 else None


def depreciation_straight_line(cost: float, salvage: float,
                               life_years: int) -> Optional[Dict[str, float]]:
    """Straight-line depreciation.

    Returns dict with annual_depreciation, monthly_depreciation.
    """
    if cost <= 0 or salvage < 0 or life_years <= 0 or salvage > cost:
        return None
    annual = (cost - salvage) / life_years
    return {
        'annual_depreciation': annual,
        'monthly_depreciation': annual / 12.0,
    }


def depreciation_double_declining(cost: float, salvage: float,
                                  life_years: int) -> Optional[List[Dict[str, float]]]:
    """Double-declining balance depreciation schedule.

    Returns list of dicts with year, depreciation, accumulated, book_value.
    """
    if cost <= 0 or salvage < 0 or life_years <= 0 or salvage > cost:
        return None
    rate = 2.0 / life_years
    book = cost
    accumulated = 0.0
    schedule = []
    for y in range(1, life_years + 1):
        dep = book * rate
        if book - dep < salvage:
            dep = book - salvage
        accumulated += dep
        book -= dep
        if book < salvage:
            book = salvage
        schedule.append({
            'year': y,
            'depreciation': dep,
            'accumulated': accumulated,
            'book_value': book,
        })
        if book <= salvage:
            break
    return schedule


def bond_price(face_value: float, coupon_rate: float, yield_rate: float,
               years: int, coupons_per_year: int = 2) -> Optional[float]:
    """Compute bond price.

    Price = sum(C/(1+y/m)^t) + F/(1+y/m)^(m*n)
    """
    if face_value <= 0 or years <= 0 or coupons_per_year <= 0:
        return None
    m = coupons_per_year
    c = face_value * coupon_rate / 100.0 / m
    y = yield_rate / 100.0 / m
    n = int(years * m)
    pv_coupons = sum(c / (1 + y) ** t for t in range(1, n + 1))
    pv_face = face_value / (1 + y) ** n
    return pv_coupons + pv_face


def bond_yield(face_value: float, coupon_rate: float, price: float,
               years: int, coupons_per_year: int = 2,
               guess: float = 5.0) -> Optional[float]:
    """Compute yield to maturity using Newton-Raphson (as percentage)."""
    if face_value <= 0 or price <= 0 or years <= 0 or coupons_per_year <= 0:
        return None
    m = coupons_per_year
    c = face_value * coupon_rate / 100.0 / m
    r = guess / 100.0 / m
    for _ in range(200):
        n = int(years * m)
        pv = sum(c / (1 + r) ** t for t in range(1, n + 1)) + \
            face_value / (1 + r) ** n
        dpv = sum(-t * c / (1 + r) ** (t + 1)
                  for t in range(1, n + 1)) + \
            -n * face_value / (1 + r) ** (n + 1)
        if abs(dpv) < 1e-18:
            break
        r_new = r - (pv - price) / dpv
        if abs(r_new - r) < 1e-12:
            return r_new * m * 100.0
        r = r_new
    # Recompute pv with final r for accurate check
    n = int(years * m)
    pv_final = sum(c / (1 + r) ** t for t in range(1, n + 1)) + \
        face_value / (1 + r) ** n
    return r * m * 100.0 if abs(pv_final - price) < 0.01 else None


def retirement_savings(monthly_contribution: float, annual_rate: float,
                       years: int,
                       current_savings: float = 0.0) -> Optional[Dict[str, float]]:
    """Compute retirement savings with monthly contributions.

    FV = PV*(1+r)^n + PMT*((1+r)^n - 1)/r
    """
    if monthly_contribution < 0 or years <= 0:
        return None
    r = annual_rate / 100.0 / 12.0
    n = int(years * 12)
    if r == 0:
        total = current_savings + monthly_contribution * n
        return {
            'future_value': total,
            'total_contributions': current_savings + monthly_contribution * n,
            'total_interest': 0.0,
        }
    factor = (1 + r) ** n
    fv = current_savings * factor + monthly_contribution * (factor - 1) / r
    total_contributions = current_savings + monthly_contribution * n
    return {
        'future_value': fv,
        'total_contributions': total_contributions,
        'total_interest': fv - total_contributions,
    }
