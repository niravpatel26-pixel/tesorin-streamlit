# profile.py
import streamlit as st

from supabase_client import sign_out  # in case you want a logout button here too


def _get_currency(country_code: str) -> str:
    if country_code == "IN":
        return "₹"
    return "$"


def render_profile_page() -> None:
    """
    Collect basic 'who you are' + money snapshot and store it in st.session_state.profile.
    This page is shown immediately after sign-up / log-in, and can also be reached
    from the Navigation menu.
    """
    ss = st.session_state

    # Ensure profile dict exists
    if "profile" not in ss:
        ss.profile = {
            "country": "IN",
            "age": 25,
            "employment_status": "Salaried",
            "dependents": 0,
            "income": 0.0,
            "expenses": 0.0,
            "savings": 0.0,
            "debt": 0.0,
            "high_interest_debt": False,
            "goals": [],
        }

    profile = ss.profile

    # --- Page heading (matches your theme) ---
    st.markdown(
        """
        <div class="tesorin-logo-word">TESORIN</div>
        <div class="tesorin-tagline">Start small. Plan big.</div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="tesorin-dark-card">
          <div class="tesorin-dark-heading">Profile & money snapshot</div>
          <p class="tesorin-auth-subtitle" style="margin-bottom:0.5rem;">
            A few basics so Tesorin can suggest realistic buffers and next steps.
            You can change these anytime.
          </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("")  # spacer

    # --- Form ---
    # Country affects currency label
    current_country = profile.get("country", "IN")
    current_currency = _get_currency(current_country)

    with st.form("profile_form", clear_on_submit=False):
        col_left, col_right = st.columns(2)

        # ----- Left: You -----
        with col_left:
            country_display = st.selectbox(
                "Where do you manage your money?",
                ["🇮🇳 India", "🇨🇦 Canada"],
                index=0 if current_country == "IN" else 1,
            )
            country = "IN" if "India" in country_display else "CA"
            currency = _get_currency(country)

            age = st.slider(
                "Age",
                min_value=18,
                max_value=70,
                value=int(profile.get("age", 25)),
            )

            employment_status = st.selectbox(
                "Which best describes you?",
                [
                    "Salaried",
                    "Self-employed / business",
                    "Student",
                    "Homemaker",
                    "Between jobs",
                    "Retired",
                ],
                index=0,
            )

            dependents = st.number_input(
                "People who financially depend on you",
                min_value=0,
                max_value=10,
                step=1,
                value=int(profile.get("dependents", 0)),
            )

        # ----- Right: Money snapshot -----
        with col_right:
            income = st.number_input(
                f"Approx. monthly take-home income ({currency})",
                min_value=0.0,
                step=1000.0,
                value=float(profile.get("income", 0.0)),
            )

            expenses = st.number_input(
                f"Approx. monthly essential expenses ({currency})",
                help="Rent, groceries, loans, utilities – the stuff you must pay.",
                min_value=0.0,
                step=1000.0,
                value=float(profile.get("expenses", 0.0)),
            )

            savings = st.number_input(
                f"Cash savings / buffer right now ({currency})",
                help="Money in bank / liquid savings that you could use within a few days.",
                min_value=0.0,
                step=1000.0,
                value=float(profile.get("savings", 0.0)),
            )

            debt = st.number_input(
                f"Total debt that currently worries you ({currency})",
                help="Include credit cards, personal loans, BNPL etc.",
                min_value=0.0,
                step=1000.0,
                value=float(profile.get("debt", 0.0)),
            )

            high_interest_debt = st.checkbox(
                "Some of this is high-interest (like credit cards / BNPL)",
                value=bool(profile.get("high_interest_debt", False)),
            )

        st.markdown("")  # small gap

        col_save, col_skip = st.columns([2, 1])
        with col_save:
            save_clicked = st.form_submit_button("Save profile and continue")
        with col_skip:
            skip_clicked = st.form_submit_button("Skip for now")

    # --- Handle form actions ---
    if save_clicked:
        ss.profile.update(
            {
                "country": country,
                "age": int(age),
                "employment_status": employment_status,
                "dependents": int(dependents),
                "income": float(income),
                "expenses": float(expenses),
                "savings": float(savings),
                "debt": float(debt),
                "high_interest_debt": bool(high_interest_debt),
            }
        )
        # Optionally: persist to Supabase here once you're ready
        # if is_configured():
        #     save_profile(ss.user, ss.profile)

        ss.screen = "main"
        ss.main_tab = "home"
        st.success("Profile saved. Your planner is ready.")
        st.rerun()

    if skip_clicked:
        ss.screen = "main"
        ss.main_tab = "home"
        st.rerun()
