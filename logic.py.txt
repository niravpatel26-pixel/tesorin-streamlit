# logic.py
from datetime import datetime


def calculate_cashflow(income: float, expenses: float) -> float:
    return income - expenses


def calculate_net_worth(savings: float, debt: float) -> float:
    return savings - debt


def calculate_savings_rate(income: float, cashflow: float) -> float:
    if income <= 0:
        return 0.0
    return (cashflow / income) * 100


def emergency_fund_target(expenses: float, debt: float) -> float:
    """
    v0.1 rule:
    - If debt > 0 → target = 1× monthly expenses
    - Else → target = 3× monthly expenses
    """
    if expenses <= 0:
        return 0.0
    if debt > 0:
        return 1 * expenses
    return 3 * expenses


def savings_rate_target(country: str, income: float) -> tuple[float, float]:
    """
    Returns (low, high) target savings rate in % based on income and country.
    country: "IN" or "CA"
    """
    if income <= 0:
        return (0.0, 0.0)

    if country == "IN":
        if income < 30000:
            return (10, 15)
        elif income < 60000:
            return (15, 25)
        else:
            return (25, 40)
    else:  # Canada or others
        if income < 3000:
            return (10, 15)
        elif income < 6000:
            return (15, 25)
        else:
            return (25, 35)


def debt_priority_share(country: str, high_interest_debt: bool) -> float:
    """
    Portion of monthly savings to allocate to debt (0-1).
    """
    if high_interest_debt:
        return 0.4  # prioritise debt
    return 0.2      # normal


def monthly_goal_contribution(target_amount: float, target_year: int) -> float:
    """
    Simple FV / (years * 12) rule (no compounding).
    """
    current_year = datetime.now().year
    years = max(target_year - current_year, 1)
    months = years * 12
    if months <= 0:
        return target_amount
    return target_amount / months


def allocate_monthly_plan(
    income: float,
    expenses: float,
    country: str,
    debt: float,
    high_interest_debt: bool,
) -> dict:
    """
    Returns recommended monthly savings amount + breakdown:
    {
      "cashflow": ...,
      "recommended_saving": ...,
      "emergency": ...,
      "investing": ...,
      "debt": ...
    }
    """
    cashflow = calculate_cashflow(income, expenses)
    if cashflow <= 0:
        return {
            "cashflow": cashflow,
            "recommended_saving": 0.0,
            "emergency": 0.0,
            "investing": 0.0,
            "debt": 0.0,
        }

    low, high = savings_rate_target(country, income)
    target_rate = (low + high) / 2 if high > 0 else 0.0
    target_saving = income * (target_rate / 100.0)
    recommended_saving = min(cashflow, target_saving)

    # Base split
    emergency_share = 0.4
    investing_share = 0.3
    debt_share = 0.3

    # Adjust for debt / no debt
    if debt <= 0:
        investing_share += debt_share
        debt_share = 0.0
    else:
        if high_interest_debt:
            debt_share = 0.4
            emergency_share = 0.3
            investing_share = 0.3

    emergency_amount = recommended_saving * emergency_share
    investing_amount = recommended_saving * investing_share
    debt_amount = recommended_saving * debt_share

    return {
        "cashflow": cashflow,
        "recommended_saving": recommended_saving,
        "emergency": emergency_amount,
        "investing": investing_amount,
        "debt": debt_amount,
    }
