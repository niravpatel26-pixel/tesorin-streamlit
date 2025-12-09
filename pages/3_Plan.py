import streamlit as st
from logic import allocate_monthly_plan


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
    debt = profile["debt"]
    high_interest_debt = profile["high_interest_debt"]

    st.title("Monthly Plan")
    st.caption("How your recommended monthly saving is split.")

    plan = allocate_monthly_plan(
        income=income,
        expenses=expenses,
        country=country,
        debt=debt,
        high_interest_debt=high_interest_debt,
    )

    rec = plan["recommended_saving"]
    if rec <= 0:
        st.info(
            "Right now your cashflow is not positive. Adjust income/expenses on the Home page first."
        )
        st.stop()

    st.metric("Recommended saving per month", f"{currency}{rec:,.0f}")

    st.markdown("### Breakdown")
    st.write(
        f"- Emergency buffer: **{currency}{plan['emergency']:,.0f}** / month\n"
        f"- Long-term investing: **{currency}{plan['investing']:,.0f}** / month\n"
        f"- Debt payoff: **{currency}{plan['debt']:,.0f}** / month"
    )

    st.markdown("---")
    st.bar_chart(
        {
            "Emergency": [plan["emergency"]],
            "Investing": [plan["investing"]],
            "Debt": [plan["debt"]],
        }
    )

    st.caption(
        "These are simple v0.1 rules. Later we can make this smarter and more personalised."
    )


if __name__ == "__main__":
    main()
