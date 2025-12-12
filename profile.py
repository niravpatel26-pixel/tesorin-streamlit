# profile.py
import streamlit as st


def render_profile_page(profile: dict, first_time: bool = False):
    """
    Render the profile / KYC page.

    Returns:
        (updated_profile: dict, completed: bool)

    completed = True  → caller (app.py) should send user back to the main app.
    """

    st.markdown("### Your basic profile")

    # ---- Defaults from existing profile ----
    country_code = profile.get("country", "IN")
    country_default = "🇮🇳 India" if country_code == "IN" else "🇨🇦 Canada"

    age_default = int(profile.get("age", 25))
    income_default = float(profile.get("income", 0.0))
    expenses_default = float(profile.get("expenses", 0.0))
    savings_default = float(profile.get("savings", 0.0))
    debt_default = float(profile.get("debt", 0.0))
    high_interest_default = bool(profile.get("high_interest_debt", False))

    employment_default = profile.get("employment_status", "Full-time employment")
    household_default = int(profile.get("household_size", 1))
    dependents_default = int(profile.get("dependents", 0))

    focus_default = profile.get(
        "primary_focus", "Build or pad my emergency fund"
    )
    risk_default = int(profile.get("risk_comfort", 3))
    feeling_default = profile.get("money_feeling", "Mostly stressed")

    job_options = [
        "Full-time employment",
        "Part-time / contract",
        "Business / self-employed",
        "Student",
        "Between jobs",
        "Other",
    ]
    if employment_default in job_options:
        job_index = job_options.index(employment_default)
    else:
        job_index = 0

    focus_options = [
        "Build or pad my emergency fund",
        "Clean up high-interest debt",
        "Get started with long-term investing",
        "Stay on top of monthly cashflow",
        "Save for a specific purchase",
    ]
    if focus_default in focus_options:
        focus_index = focus_options.index(focus_default)
    else:
        focus_index = 0

    feeling_options = [
        "Mostly stressed",
        "Mostly okay",
        "Mostly confident",
        "I avoid thinking about it",
    ]
    if feeling_default in feeling_options:
        feeling_index = feeling_options.index(feeling_default)
    else:
        feeling_index = 0

    col1, col2 = st.columns(2)

    # ---- Form ----
    with st.form("profile_form", clear_on_submit=False):
        with col1:
            country_display = st.selectbox(
                "Where do you manage your money?",
                ["🇮🇳 India", "🇨🇦 Canada"],
                index=0 if "India" in country_default else 1,
            )

            age = st.slider(
                "Age",
                min_value=18,
                max_value=65,
                value=age_default,
            )

            employment_status = st.selectbox(
                "Work situation",
                job_options,
                index=job_index,
            )

            household_size = st.number_input(
                "How many people in your household (including you)?",
                min_value=1,
                max_value=10,
                value=household_default,
            )

            dependents = st.number_input(
                "How many people fully/mostly rely on your income?",
                min_value=0,
                max_value=10,
                value=dependents_default,
            )

        with col2:
            monthly_income = st.number_input(
                "Average monthly income (after tax)",
                min_value=0.0,
                step=1000.0,
                value=income_default,
            )

            monthly_essentials = st.number_input(
                "Average monthly essential spending (rent, food, basics)",
                min_value=0.0,
                step=500.0,
                value=expenses_default,
            )

            savings = st.number_input(
                "Cash savings right now",
                min_value=0.0,
                step=1000.0,
                value=savings_default,
            )

            debt = st.number_input(
                "Total debt (loans, cards, etc.)",
                min_value=0.0,
                step=1000.0,
                value=debt_default,
            )

            high_interest = st.checkbox(
                "I have high-interest debt (credit cards, payday loans, etc.)",
                value=high_interest_default,
            )

        st.markdown("---")

        primary_focus = st.selectbox(
            "Right now, what feels most important?",
            focus_options,
            index=focus_index,
        )

        risk_comfort = st.slider(
            "How comfortable are you with your money moving up and down?",
            min_value=1,
            max_value=5,
            value=risk_default,
            help="1 = I really dislike seeing any drops. 5 = I'm okay with ups and downs for long-term growth.",
        )

        money_feeling = st.selectbox(
            "When you think about money, you mostly feel…",
            feeling_options,
            index=feeling_index,
        )

        button_label = (
            "Save and continue to your planner" if first_time else "Save profile"
        )
        save_clicked = st.form_submit_button(button_label)

    # If nothing was clicked, stay on this page
    if not save_clicked:
        return profile, False

    # ---- Build updated profile ----
    new_country_code = "IN" if "India" in country_display else "CA"

    updated_profile = {
        **profile,
        "country": new_country_code,
        "age": int(age),
        "income": float(monthly_income),
        "expenses": float(monthly_essentials),
        "savings": float(savings),
        "debt": float(debt),
        "high_interest_debt": bool(high_interest),
        "employment_status": employment_status,
        "household_size": int(household_size),
        "dependents": int(dependents),
        "primary_focus": primary_focus,
        "risk_comfort": int(risk_comfort),
        "money_feeling": money_feeling,
    }

    # IMPORTANT:
    # Any time the user clicks "Save profile",
    # treat it as completed so app.py sends them back to the main dashboard.
    return updated_profile, True
