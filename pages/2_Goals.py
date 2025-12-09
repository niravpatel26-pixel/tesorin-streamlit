import streamlit as st
from logic import monthly_goal_contribution


def get_currency(country_code: str) -> str:
    return "₹" if country_code == "IN" else "$"


def ensure_profile():
    if "profile" not in st.session_state:
        st.warning("Go to the **Home** page and save a snapshot first.")
        st.stop()


GOAL_TYPES = [
    "Emergency fund",
    "House down payment",
    "Car",
    "Travel",
    "Education",
    "Wedding",
    "Retirement seed",
]


def main():
    ensure_profile()
    profile = st.session_state.profile

    country = profile["country"]
    currency = get_currency(country)

    st.title("Goals")
    st.caption(
        "Rough, high-level goal planner. Later we can make this more detailed and persistent."
    )

    col1, col2 = st.columns(2)

    with col1:
        goal_type = st.selectbox("Goal type", GOAL_TYPES)
        target_amount = st.number_input(
            f"Target amount ({currency})", min_value=0.0, step=10000.0
        )
        target_year = st.number_input(
            "Target year", min_value=2025, max_value=2100, value=2030, step=1
        )

        if st.button("Calculate monthly contribution"):
            monthly = monthly_goal_contribution(target_amount, target_year)
            st.session_state["current_goal"] = {
                "type": goal_type,
                "amount": target_amount,
                "year": target_year,
                "monthly": monthly,
            }

    with col2:
        goal = st.session_state.get("current_goal")
        if not goal:
            st.info("Set a goal on the left to see a suggested monthly contribution.")
        else:
            monthly = goal["monthly"]
            st.subheader("Suggested plan")
            st.write(f"**Goal:** {goal['type']}")
            st.write(
                f"**Target:** {currency}{goal['amount']:,.0f} by **{goal['year']}**."
            )
            st.write(
                f"Required contribution: **{currency}{monthly:,.0f} / month** "
                "with no compounding (v0.1 simple rule)."
            )

            st.caption(
                "In future versions we can add expected returns, risk levels, and priority between multiple goals."
            )


if __name__ == "__main__":
    main()
