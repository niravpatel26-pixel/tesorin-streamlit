import streamlit as st
from logic import (
    calculate_cashflow,
    calculate_net_worth,
    calculate_savings_rate,
    emergency_fund_target,
    allocate_monthly_plan,
)


st.set_page_config(layout="wide")


def main():
    st.title("Dashboard")

    if "profile" not in st.session_state:
        st.warning("Go to the Home page first and save a snapshot.")
        return

    profile = st.session_state.profile
    country = profile["country"]
    currency = "₹" if country == "IN" else "$"

    income = profile["income"]
    expenses = profile["expenses"]
    savings = profile["savings"]
    debt = profile["debt"]
    high_interest_debt = profile["high_interest_debt"]

    cashflow = calculate_cashflow(income, expenses)
    net_worth = calculate_net_worth(savings, debt)
    savings_rate = calculate_savings_rate(income, cashflow)
    e_target = emergency_fund_target(expenses, debt)
    plan = allocate_monthly_plan(
        income, expenses, country, debt, high_interest_debt
    )

    top, bottom = st.columns([2, 3])

    with top:
        st.subheader("Snapshot")
        st.metric("Net worth", f"{currency}{net_worth:,.0f}")
        st.metric("Monthly free cash", f"{currency}{cashflow:,.0f}")
        st.metric("Savings rate", f"{savings_rate:.1f}%")

        st.subheader("Emergency fund")
        st.write(f"Target: **{currency}{e_target:,.0f}**")

    with bottom:
        st.subheader("Monthly plan overview")
        if plan["recommended_saving"] > 0:
            st.write(f"Recommended monthly saving: **{currency}{plan['recommended_saving']:,.0f}**")

            st.bar_chart(
                {
                    "Emergency": [plan["emergency"]],
                    "Investing": [plan["investing"]],
                    "Debt": [plan["debt"]],
                }
            )
        else:
            st.info("No positive cashflow – Dashboard will become more useful once cashflow is positive.")


if __name__ == "__main__":
    main()
