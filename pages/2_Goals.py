import streamlit as st
from logic import monthly_goal_contribution


def main():
    st.title("Goals")

    if "profile" not in st.session_state:
        st.warning("Go to the Home page first and save a snapshot.")
        return

    currency = "₹" if st.session_state.profile["country"] == "IN" else "$"

    st.write("This v0.1 goals page lets you rough out 1–3 goals manually.")

    num_goals = st.slider("How many goals do you want to sketch?", 1, 3, 1)

    goals_data = []
    for i in range(num_goals):
        st.markdown(f"#### Goal {i + 1}")
        col1, col2, col3 = st.columns([2, 2, 2])
        with col1:
            name = st.text_input("Name", key=f"goal_name_{i}", value=f"Goal {i + 1}")
        with col2:
            target_amount = st.number_input(
                f"Target amount ({currency})",
                min_value=0.0,
                step=10000.0,
                key=f"goal_amount_{i}",
            )
        with col3:
            target_year = st.number_input(
                "Target year",
                min_value=2025,
                max_value=2050,
                value=2030,
                step=1,
                key=f"goal_year_{i}",
            )

        if target_amount > 0:
            monthly = monthly_goal_contribution(target_amount, target_year)
            st.caption(
                f"Rough monthly contribution: **{currency}{monthly:,.0f}** "
                "(simple division, no compounding yet)."
            )

        goals_data.append(
            {"name": name, "target_amount": target_amount, "target_year": target_year}
        )

    st.markdown("---")
    st.info("Later, these goals can be saved to Supabase and tied into your main monthly plan.")


if __name__ == "__main__":
    main()
