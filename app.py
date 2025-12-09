import streamlit as st
from logic import (
    calculate_cashflow,
    calculate_net_worth,
    calculate_savings_rate,
    emergency_fund_target,
    savings_rate_target,
    allocate_monthly_plan,
)
from supabase_client import is_configured, save_profile  # for later use


# ---- PAGE CONFIG ----
st.set_page_config(
    page_title="Tesorin – First Step Planner",
    page_icon="favicon.ico",  # path to your icon file
    layout="wide",
)


def get_currency(country_code: str) -> str:
    if country_code == "IN":
        return "₹"
    return "$"


def init_state():
    if "profile" not in st.session_state:
        st.session_state.profile = {
            "country": "IN",
            "age": 25,
            "income": 0.0,
            "expenses": 0.0,
            "savings": 0.0,
            "debt": 0.0,
            "high_interest_debt": False,
            "goals": [],
        }


def main():
    init_state()

    st.markdown(
        """
        ### Tesorin · First Step

        **Build your first serious money plan** with a calm, simple view of
        your cashflow, safety buffer and goals.
        """,
    )
    st.caption(
        "This is your v0.1 planner – focused on basic inputs, emergency fund and simple monthly allocations."
    )

    with st.container():
        left, right = st.columns([3, 2])

        with left:
            st.subheader("1. Basic profile & cashflow")

            # Country selector with flags
            country_display = st.selectbox(
                "Where do you manage your money?",
                 ["🇮🇳 India", "🇨🇦 Canada"],
            )

# Map the selected label to internal country code
           if "India" in country_display:
            country = "IN"
           else:
            country = "CA"

            currency = get_currency(country)


            currency = get_currency(country)

            age = st.slider("Age", min_value=18, max_value=60, value=25)

            income = st.number_input(
                f"Monthly income ({currency})",
                min_value=0.0,
                step=1000.0,
            )
            expenses = st.number_input(
                f"Monthly expenses ({currency})",
                min_value=0.0,
                step=1000.0,
            )
            savings = st.number_input(
                f"Current savings ({currency})",
                min_value=0.0,
                step=1000.0,
            )
            debt = st.number_input(
                f"Current debt ({currency})",
                min_value=0.0,
                step=1000.0,
            )

            high_interest_debt = st.checkbox(
                "My main debt is high-interest (credit cards, >12–15%)", value=False
            )

            st.markdown("### 2. Top goals (you can refine on the Goals page)")
            goals = st.multiselect(
                "What are your top goals right now?",
                [
                    "Emergency fund",
                    "House",
                    "Car",
                    "Travel",
                    "Education",
                    "Wedding",
                    "Retirement",
                ],
            )

            if st.button("Save this as my current snapshot"):
                st.session_state.profile = {
                    "country": country,
                    "age": age,
                    "income": income,
                    "expenses": expenses,
                    "savings": savings,
                    "debt": debt,
                    "high_interest_debt": high_interest_debt,
                    "goals": goals,
                }

                # later: push to Supabase if configured
                if is_configured():
                    save_profile(st.session_state.profile)

                st.success("Snapshot saved. Other pages now use these numbers.")

        with right:
            st.subheader("Quick snapshot")

            profile = st.session_state.profile
            # use live values if user is editing now
            country = country if "country" in locals() else profile["country"]
            currency = get_currency(country)
            income = income if "income" in locals() else profile["income"]
            expenses = expenses if "expenses" in locals() else profile["expenses"]
            savings = savings if "savings" in locals() else profile["savings"]
            debt = debt if "debt" in locals() else profile["debt"]

            cashflow = calculate_cashflow(income, expenses)
            net_worth = calculate_net_worth(savings, debt)
            savings_rate = calculate_savings_rate(income, cashflow)

            c1, c2 = st.columns(2)
            with c1:
                st.metric(
                    "Net worth",
                    f"{currency}{net_worth:,.0f}",
                )
            with c2:
                st.metric(
                    "Monthly free cash",
                    f"{currency}{cashflow:,.0f}",
                )

            low_target, high_target = savings_rate_target(country, income)
            if high_target > 0:
                st.caption(
                    f"Target savings range for you: **{low_target:.0f}%–{high_target:.0f}%** of income."
                )

            bar_value = max(min(int(savings_rate), 100), 0)
            st.progress(bar_value if bar_value > 0 else 0)
            st.caption(f"Current savings rate: **{savings_rate:.1f}%** of income.")

            st.markdown("---")
            st.markdown("### Emergency fund (v0.1 rule)")

            e_target = emergency_fund_target(expenses, debt)
            e_gap = max(e_target - savings, 0)
            monthly_fill = e_gap / 12 if e_gap > 0 else 0

            st.write(
                f"Suggested safety buffer: **{currency}{e_target:,.0f}** "
                f"(based on your monthly expenses)."
            )
            if e_gap > 0:
                st.write(
                    f"If you put around **{currency}{monthly_fill:,.0f} per month** aside for a year, "
                    "you’d fully fund this buffer."
                )
            else:
                st.success("Your current savings already cover this simple buffer rule.")

            # Simple chart of a recommended monthly allocation
            st.markdown("### Example monthly allocation")
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
                    f"Recommended monthly saving (target vs. cashflow): **{currency}{rec:,.0f}**"
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
                    "Cashflow is not positive yet. Small fixes on income/spending will make the plan more useful."
                )

    st.markdown("---")
    st.caption(
        "Use the sidebar to explore the Dashboard, Goals, Plan, Learn, and Settings pages based on this snapshot."
    )


if __name__ == "__main__":
    main()