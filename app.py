import streamlit as st
from datetime import datetime

# ---- PAGE CONFIG ----
st.set_page_config(
    page_title="Tesorin – First Step Planner",
    page_icon="favicon.ico",  # path to your icon file
    layout="wide",
)
# ---- HELPER FUNCTIONS ----
def calculate_cashflow(income: float, expenses: float) -> float:
    return income - expenses


def calculate_net_worth(savings: float, debt: float) -> float:
    return savings - debt


def calculate_savings_rate(cashflow: float, income: float) -> float:
    if income <= 0:
        return 0.0
    return (cashflow / income) * 100


def calculate_emergency_target(monthly_expenses: float, has_debt: bool) -> float:
    """Return target emergency fund based on debt status."""
    if has_debt:
        return 1 * monthly_expenses
    else:
        return 3 * monthly_expenses


def calculate_emergency_contribution(
    target: float, current_savings: float, months: int = 12
) -> float:
    """How much per month to reach the target in given months."""
    gap = target - current_savings
    if gap <= 0:
        return 0.0
    return gap / months


def calculate_goal_monthly_contribution(
    target_amount: float, target_year: int, current_year: int | None = None
) -> float:
    """
    Simple version of your spec:
    monthlyContribution = FV / (years * 12)
    """
    if current_year is None:
        current_year = datetime.now().year

    years = max(target_year - current_year, 1)  # at least 1 year
    months = years * 12

    if target_amount <= 0:
        return 0.0

    return target_amount / months


# ---- APP HEADER ----
with st.container():
    col1, col2 = st.columns([3, 2])

    with col1:
        st.markdown(
            """
            ### Tesorin · First Step

            **Build your first serious money plan** with a calm, simple view of
            your cashflow, safety buffer and goals.
            """,
        )
        st.caption(
            "Start with small, honest numbers. Tesorin will turn them into a clearer monthly plan."
        )

    with col2:
        st.markdown(
            """
            <div style="border-radius:16px; padding:12px 16px; background-color:#111827;
                        border:1px solid #374151;">
              <p style="font-size:12px; color:#9CA3AF; margin:0 0 4px 0;">Prototype status</p>
              <p style="font-size:14px; color:#E5E7EB; margin:0;">
                v0.1 · Single-user demo · Logic focus.
              </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.write("")  # small vertical space

# ---- LAYOUT: LEFT = INPUTS, RIGHT = SUMMARY ----
left, right = st.columns([3, 2])

# 1) LEFT SIDE: basic inputs + goals
with left:
    st.subheader("1. Tell us where you are today")

    country_display = st.selectbox(
        "Where do you manage your money?",
        ["🇮🇳 India", "🇨🇦 Canada"],
    )

    if "India" in country_display:
        country_code = "IN"
        currency_symbol = "₹"
    else:
        country_code = "CA"
        currency_symbol = "$"

    st.caption(f"Country code in use: **{country_code}**")

    st.markdown("### Cashflow inputs")

    income = st.number_input(
        f"Monthly income ({currency_symbol})",
        min_value=0.0,
        step=1000.0,
        key="income",
    )
    expenses = st.number_input(
        f"Monthly expenses ({currency_symbol})",
        min_value=0.0,
        step=1000.0,
        key="expenses",
    )
    savings = st.number_input(
        f"Current savings ({currency_symbol})",
        min_value=0.0,
        step=1000.0,
        key="savings",
    )
    debt = st.number_input(
        f"Current debt ({currency_symbol})",
        min_value=0.0,
        step=1000.0,
        key="debt",
    )

    st.markdown("### Goals (pick up to 3)")

    goal_options = [
        "Emergency fund",
        "House",
        "Car",
        "Travel",
        "Education",
        "Wedding",
        "Retirement",
    ]

    selected_goals = st.multiselect(
        "What are your top goals right now?",
        options=goal_options,
    )

    # Soft enforce max 3
    if len(selected_goals) > 3:
        st.warning("You can pick up to 3 goals. Only the first 3 will be used.")
        selected_goals = selected_goals[:3]

    # Store per-goal target & year
    goal_data: dict[str, dict[str, float | int]] = {}

    if selected_goals:
        st.markdown("#### Set targets for your goals")

        current_year = datetime.now().year

        for goal in selected_goals:
            st.markdown(f"**{goal}**")
            col1, col2 = st.columns(2)

            with col1:
                target = st.number_input(
                    f"Target amount for {goal} ({currency_symbol})",
                    min_value=0.0,
                    step=1000.0,
                    key=f"target_{goal}",
                )
            with col2:
                year = st.number_input(
                    f"Target year for {goal}",
                    min_value=current_year,
                    max_value=current_year + 50,
                    step=1,
                    key=f"year_{goal}",
                )

            goal_data[goal] = {"target": float(target), "year": int(year)}

# 2) RIGHT SIDE: summary cards using the logic
with right:
    st.subheader("2. Quick snapshot")

    cashflow = calculate_cashflow(income, expenses)
    net_worth = calculate_net_worth(savings, debt)
    savings_rate = calculate_savings_rate(cashflow, income)

    card1, card2 = st.columns(2)
    with card1:
        st.metric(
            label="Net worth",
            value=f"{currency_symbol}{net_worth:,.0f}",
        )
    with card2:
        st.metric(
            label="Monthly free cash",
            value=f"{currency_symbol}{cashflow:,.0f}",
        )

    # Savings rate progress bar
    progress_value = min(max(int(savings_rate), 0), 100)
    st.progress(progress_value)
    st.caption(f"Approx. savings rate: **{savings_rate:.1f}%** of income")

    st.markdown("---")
    st.markdown("### Emergency fund suggestion (v0.1)")

    has_debt = debt > 0
    emergency_target = calculate_emergency_target(expenses, has_debt)
    emergency_gap = max(emergency_target - savings, 0)
    emergency_monthly = calculate_emergency_contribution(
        emergency_target, savings, months=12
    )

    st.write(
        f"Target safety buffer: **{currency_symbol}{emergency_target:,.0f}** "
        f"(based on your monthly expenses)."
    )

    if emergency_gap > 0:
        st.write(
            f"You’re about **{currency_symbol}{emergency_gap:,.0f}** "
            "short of this safety buffer."
        )
        st.write(
            f"If you set aside about **{currency_symbol}{emergency_monthly:,.0f} per month** "
            "for the next 12 months, you’d fully fund this buffer."
        )
    else:
        st.success("Nice – your current savings already cover this simple safety buffer rule.")

# ---- GOAL-BY-GOAL BREAKDOWN ----
st.markdown("---")
st.subheader("3. Goal-by-goal breakdown")

if not selected_goals:
    st.info("Pick at least one goal on the left to see a simple breakdown.")
else:
    # Cashflow message
    if cashflow > 0:
        st.success(f"Monthly surplus: {currency_symbol}{cashflow:,.0f}")
    elif cashflow == 0:
        st.info("You are roughly breaking even.")
    else:
        st.error(f"Monthly deficit: {currency_symbol}{cashflow:,.0f}")

    # Emergency fund section
    st.markdown("#### Emergency fund")
    st.write(f"Target emergency fund: {currency_symbol}{emergency_target:,.0f}")
    if emergency_monthly > 0:
        st.write(
            f"Suggested monthly contribution (next 12 months): "
            f"{currency_symbol}{emergency_monthly:,.0f}"
        )
    else:
        st.write("You don’t need to contribute more for this basic emergency fund right now.")

    # Goals overview + contributions
    st.markdown("#### Goals overview")

    current_year = datetime.now().year
    for goal in selected_goals:
        data = goal_data.get(goal, {"target": 0.0, "year": current_year})
        target = float(data["target"])
        year = int(data["year"])
        monthly = calculate_goal_monthly_contribution(target, year, current_year)

        if target <= 0:
            st.write(f"{goal}: no target set yet.")
        else:
            st.write(
                f"{goal}: target {currency_symbol}{target:,.0f} by {year} → "
                f"save about {currency_symbol}{monthly:,.0f} per month"
            )
