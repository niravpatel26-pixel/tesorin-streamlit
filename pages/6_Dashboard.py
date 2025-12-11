import streamlit as st
from logic import (
    calculate_cashflow,
    calculate_net_worth,
    calculate_savings_rate,
    emergency_fund_target,
    savings_rate_target,
    allocate_monthly_plan,
)


def get_currency(country_code: str) -> str:
    if country_code == "IN":
        return "₹"
    return "$"


def ensure_profile():
    if "profile" not in st.session_state:
        st.warning("Go to the **Home** page and save a snapshot first.")
        st.stop()


def main():
    ensure_profile()
    profile = st.session_state.profile

    country = profile["country"]
    currency = get_currency(country)
    income = profile["income"]
    expenses = profile["expenses"]
    savings = profile["savings"]
    debt = profile["debt"]
    high_interest_debt = profile["high_interest_debt"]

    st.title("Dashboard")
    st.caption("Snapshot based on the profile you saved on the Home page.")

    cashflow = calculate_cashflow(income, expenses)
    net_worth = calculate_net_worth(savings, debt)
    savings_rate = calculate_savings_rate(income, cashflow)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Net worth", f"{currency}{net_worth:,.0f}")
    with c2:
        st.metric("Monthly free cash", f"{currency}{cashflow:,.0f}")
    with c3:
        st.metric("Savings rate", f"{savings_rate:.1f} %")

    low, high = savings_rate_target(country, income)
    if high > 0:
        st.write(
            f"Target savings range for you: **{low:.0f}%–{high:.0f}%** of income."
        )

    st.markdown("---")
    st.subheader("Emergency buffer")

    e_target = emergency_fund_target(expenses, debt)
    e_gap = max(e_target - savings, 0)
    monthly_fill = e_gap / 12 if e_gap > 0 else 0

    st.write(
        f"Suggested safety buffer: **{currency}{e_target:,.0f}** "
        f"(based on your monthly expenses)."
    )
    if e_gap > 0:
        st.write(
            f"Gap to target: **{currency}{e_gap:,.0f}**. "
            f"Putting **{currency}{monthly_fill:,.0f} / month** aside for a year fills this."
        )
    else:
        st.success("You already cover this simple buffer rule.")

    st.markdown("---")
    st.subheader("Monthly allocation (from rules)")

    plan = allocate_monthly_plan(
        income=income,
        expenses=expenses,
        country=country,
        debt=debt,
        high_interest_debt=high_interest_debt,
    )
    rec = plan["recommended_saving"]

    if rec > 0:
        st.caption(
            f"Recommended monthly saving: **{currency}{rec:,.0f}** "
            "(minimum of your cashflow and the target savings %)."
        )
        st.bar_chart(
            {
                "Emergency": [plan["emergency"]],
                "Investing": [plan["investing"]],
                "Debt": [plan["debt"]],
            }
        )
    else:
        st.info(
            "Cashflow is not positive yet. Tuning income/spending on the Home page will make this chart useful."
        )


if __name__ == "__main__":
    main()
