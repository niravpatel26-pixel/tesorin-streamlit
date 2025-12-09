import streamlit as st
from datetime import datetime

st.set_page_config(
    page_title="Tesorin – First Step Planner",
    page_icon="💸",
    layout="wide",
)
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
        ["IN India", "CA Canada"],
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
    )
    expenses = st.number_input(
        f"Monthly expenses ({currency_symbol})",
        min_value=0.0,
        step=1000.0,
    )
    savings = st.number_input(
        f"Current savings ({currency_symbol})",
        min_value=0.0,
        step=1000.0,
    )
    debt = st.number_input(
        f"Current debt ({currency_symbol})",
        min_value=0.0,
        step=1000.0,
    )

    st.markdown("### Goals (pick up to 3)")
    selected_goals = st.multiselect(
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

# 2) RIGHT SIDE: summary cards using your existing logic
with right:
    st.subheader("2. Quick snapshot")

    # --- reuse your existing helper functions here ---
    cashflow = income - expenses
    net_worth = savings - debt
    savings_rate = (cashflow / income * 100) if income > 0 else 0

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

    st.progress(min(max(int((savings_rate)), 0), 100))
    st.caption(f"Approx. savings rate: **{savings_rate:.1f}%** of income")

    st.markdown("---")
    st.markdown("### Emergency fund suggestion (v0.1)")

    # simple emergency-fund logic (you can replace with your existing function)
    if debt > 0:
        emergency_target = 1 * expenses
    else:
        emergency_target = 3 * expenses

    emergency_gap = max(emergency_target - savings, 0)
    monthly_suggestion = emergency_gap / 12 if emergency_gap > 0 else 0

    st.write(
        f"Target safety buffer: **{currency_symbol}{emergency_target:,.0f}** "
        f"(based on your monthly expenses)."
    )
    if emergency_gap > 0:
        st.write(
            f"If you set aside about **{currency_symbol}{monthly_suggestion:,.0f} per month** "
            "for the next 12 months, you’d fully fund this buffer."
        )
    else:
        st.write("Nice – your current savings already cover this simple safety buffer rule.")


# --- Country selection (for later logic) ---


country_display = st.selectbox("Where do you manage your money?", ["🇮🇳 India", "🇨🇦 Canada"])

if "India" in country_display:
    country_code = "IN"
    currency_symbol = "₹"
else:
    country_code = "CA"
    currency_symbol = "$"

st.write(f"Country code in use: {country_code}")

def calculate_cashflow(income, expenses):
    return income - expenses

def calculate_net_worth(savings, debt):
    return savings - debt

def calculate_savings_rate(cashflow, income):
    if income <= 0:
        return 0.0
    return (cashflow / income) * 100

def calculate_emergency_target(monthly_expenses, has_debt):
    """Return target emergency fund based on debt status."""
    if has_debt:
        return 1 * monthly_expenses
    else:
        return 3 * monthly_expenses

def calculate_emergency_contribution(target, current_savings, months=12):
    """How much per month to reach the target in given months."""
   gap = target - current_savings
    if gap <= 0:
        return 0.0
    return gap / months

def calculate_goal_monthly_contribution(target_amount, target_year, current_year=None):
    """
    Simple version of your spec:
    monthlyContribution = FV / (years * 12)
    """
    if current_year is None:
        current_year = datetime.now().year


    # years until goal (at least 1 to avoid division by zero)


    years = max(target_year - current_year, 1)
    months = years * 12

    if target_amount <= 0:
        return 0.0

    return target_amount / months

st.subheader("Cashflow Calculator")

income = st.number_input(f"Monthly income ({currency_symbol})", min_value=0.0)
expenses = st.number_input(f"Monthly expenses ({currency_symbol})", min_value=0.0)
savings = st.number_input(f"Current savings ({currency_symbol})", min_value=0.0)
debt = st.number_input(f"Current debt ({currency_symbol})", min_value=0.0)

st.subheader("Goals (pick up to 3)")

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


# Enforce max 3 (softly)


if len(selected_goals) > 3:
    st.warning("You can pick up to 3 goals. Please deselect some.")
# Store per-goal target & year
goal_data = {}

if selected_goals:
    st.markdown("#### Set targets for your goals")

    current_year = datetime.now().year

    for goal in selected_goals[:3]:
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

        goal_data[goal] = {"target": target, "year": int(year)}


if st.button("Calculate"):
    cashflow = calculate_cashflow(income, expenses)
    net_worth = calculate_net_worth(savings, debt)
    savings_rate = calculate_savings_rate(cashflow, income)

st.markdown("---")
st.subheader("3. Goal-by-goal breakdown")

if not selected_goals:
    st.info("Pick at least one goal on the left to see a simple breakdown.")
else:
    # here you paste your existing per-goal logic
    ...

    # Emergency fund logic


    has_debt = debt > 0
    emergency_target = calculate_emergency_target(expenses, has_debt)
    # for now, treat all savings as emergency savings
    emergency_monthly = calculate_emergency_contribution(emergency_target, savings, months=12)

    st.markdown("### Results")

    # Cashflow message


    if cashflow > 0:
        st.success(f"Monthly surplus: {currency_symbol}{cashflow:,.0f}")
    elif cashflow == 0:
        st.info("You are breaking even.")
    else:
        st.error(f"Monthly deficit: {currency_symbol}{cashflow:,.0f}")

    # Emergency fund section


    st.markdown("#### Emergency fund")
    st.write(f"Target emergency fund: {currency_symbol}{emergency_target:,.0f}")
    st.write(
        f"Suggested monthly contribution (next 12 months): "
        f"{currency_symbol}{emergency_monthly:,.0f}"
    )

    # Goals overview

        # Goals overview + contributions
    st.markdown("#### Goals overview")

    if not selected_goals:
        st.write("You haven't selected any goals yet.")
    else:
        current_year = datetime.now().year
        for goal in selected_goals[:3]:
            data = goal_data.get(goal, {"target": 0.0, "year": current_year})
            target = data["target"]
            year = data["year"]
            monthly = calculate_goal_monthly_contribution(target, year, current_year)

            if target <= 0:
                st.write(f"{goal}: no target set yet.")
            else:
                st.write(
                    f"{goal}: target {currency_symbol}{target:,.0f} by {year} → "
                    f"save about {currency_symbol}{monthly:,.0f} per month"
                )

   
    
   
