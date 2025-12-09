import streamlit as st
from datetime import datetime

st.title("Tesorin - First Step")
st.write("This is your first custom streamlit app.")


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

    # Emergency fund section


    st.markdown("#### Emergency fund")
    st.write(f"Target emergency fund: {currency_symbol}{emergency_target:,.0f}")
    st.write(f"Suggested monthly contribution (next 12 months): {currency_symbol}{emergency_monthly:,.0f}")
    
    st.markdown("#### Goals overview")

    if not selected_goals:
        st.write("You haven't selected any goals yet.")
    else:
        st.write("Your current top goals:")
        for goal in selected_goals[:3]:
            st.write(f"• {goal}")

