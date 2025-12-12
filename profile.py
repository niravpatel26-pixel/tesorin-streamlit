import streamlit as st


def render_profile_page(profile: dict, first_time: bool = False):
    """
    Render the profile / KYC page.

    Args:
        profile: current profile dict from session_state.
        first_time: if True, button text is 'Save and continue to your planner'
                    and we tell app.py it's okay to auto-redirect to main.

    Returns:
        (updated_profile: dict, completed: bool)
    """
    # --- safe defaults from existing profile dict ---
    country = profile.get("country", "IN")
    age = int(profile.get("age", 25))
    income = float(profile.get("income", 0.0))
    expenses = float(profile.get("expenses", 0.0))
    savings = float(profile.get("savings", 0.0))
    debt = float(profile.get("debt", 0.0))
    high_interest_debt = bool(profile.get("high_interest_debt", False))

    goal_focus_default = profile.get("goal_focus", "Getting stable month to month")
    money_conf_default = profile.get(
        "money_confidence",
        "A bit unsure, but working on it",
    )

    country_index = 0 if country == "IN" else 1

    goal_focus_options = [
        "Getting stable month to month",
        "Building an emergency buffer",
        "Cleaning up costly debt",
        "Starting long-term investing",
        "Saving for a specific near-term goal",
    ]
    if goal_focus_default not in goal_focus_options:
        goal_focus_default = goal_focus_options[0]

    money_feeling_options = [
        "Very stressed",
        "A bit anxious",
        "Mostly okay",
        "Calm and organised",
    ]
    if money_conf_default not in money_feeling_options:
        money_conf_default = money_feeling_options[1]

    with st.form("profile_form", clear_on_submit=False):
        st.markdown("### Your money basics")
        st.caption(
            "This stays private. It just helps Tesorin tune the guidance to your situation."
        )

        col1, col2 = st.columns(2)

        with col1:
            country_display = st.selectbox(
                "Where do you mainly manage your money?",
                ["🇮🇳 India", "🇨🇦 Canada"],
                index=country_index,
            )

            age_val = st.slider("Age", min_value=18, max_value=70, value=age)

            income_val = st.number_input(
                "Approx. monthly take-home income",
                min_value=0.0,
                value=income,
                step=1000.0,
            )

            expenses_val = st.number_input(
                "Approx. monthly essential expenses",
                min_value=0.0,
                value=expenses,
                step=1000.0,
                help="Rent, groceries, utilities, EMIs, basic bills, etc.",
            )

        with col2:
            savings_val = st.number_input(
                "Cash savings / buffer right now",
                min_value=0.0,
                value=savings,
                step=1000.0,
            )

            debt_val = st.number_input(
                "Total debt (loans, cards, etc.)",
                min_value=0.0,
                value=debt,
                step=1000.0,
            )

            hi_debt_val = st.checkbox(
                "I have high-interest debt (credit cards, personal loans, etc.)",
                value=high_interest_debt,
            )

            goal_focus = st.selectbox(
                "Over the next 12 months, I care most about…",
                goal_focus_options,
                index=goal_focus_options.index(goal_focus_default),
            )

            money_feeling = st.selectbox(
                "Right now, money feels…",
                money_feeling_options,
                index=money_feeling_options.index(money_conf_default),
            )

        submit_label = (
            "Save and continue to your planner" if first_time else "Save profile"
        )
        submitted = st.form_submit_button(submit_label)

    updated_profile = dict(profile)

    if submitted:
        country_val = "IN" if "India" in country_display else "CA"

        updated_profile.update(
            {
                "country": country_val,
                "age": int(age_val),
                "income": float(income_val),
                "expenses": float(expenses_val),
                "savings": float(savings_val),
                "debt": float(debt_val),
                "high_interest_debt": bool(hi_debt_val),
                "goal_focus": goal_focus,
                "money_confidence": money_feeling,
            }
        )

        st.success("Profile saved.")

    # Tell caller whether it's okay to auto-redirect to main.
    completed = bool(submitted and first_time)
    return updated_profile, completed
