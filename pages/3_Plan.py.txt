import streamlit as st
from logic import allocate_monthly_plan


def main():
    st.title("Monthly Plan")

    if "profile" not in st.session_state:
        st.warning("Go to the Home page first and save a snapshot.")
        return

    profile = st.session_state.profile
    country = profile["country"]
    currency = "₹" if country == "IN" else "$"

    plan = allocate_monthly_plan(
        income=profile["income"],
        expenses=profile["expenses"],
        country=country,
        debt=profile["debt"],
        high_interest_debt=profile["high_interest_debt"],
    )

    cashflow = plan["cashflow"]
    rec = plan["recommended_saving"]

    st.write(f"Monthly cashflow after expenses: **{currency}{cashflow:,.0f}**")
    if rec <= 0:
        st.info("Right now, there isn't enough free cash to build a plan. Small changes in income/spending will help.")
        return

    st.write(f"Suggested monthly saving: **{currency}{rec:,.0f}**")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Emergency bucket", f"{currency}{plan['emergency']:,.0f}")
    with col2:
        st.metric("Investing bucket", f"{currency}{plan['investing']:,.0f}")
    with col3:
        st.metric("Debt bucket", f"{currency}{plan['debt']:,.0f}")

    st.markdown("### Visual split")
    st.bar_chart(
        {
            "Emergency": [plan["emergency"]],
            "Investing": [plan["investing"]],
            "Debt": [plan["debt"]],
        }
    )

    st.markdown("---")
    st.caption("This v0.1 plan is rule-based and simple. Over time, you can layer more CFA-style assumptions here.")


if __name__ == "__main__":
    main()
