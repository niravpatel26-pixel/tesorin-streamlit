import streamlit as st

from logic import (
    calculate_cashflow,
    calculate_net_worth,
    calculate_savings_rate,
    emergency_fund_target,
    savings_rate_target,
    allocate_monthly_plan,
)

from supabase_client import (
    is_configured,
    save_profile,
    sign_up,
    sign_in,
    sign_out,
)

# ---------- PAGE CONFIG ----------

st.set_page_config(
    page_title="Tesorin – First Step Planner",
    page_icon="favicon.ico",
    layout="wide",
)

# ---------- BASIC THEME / GLOBAL STYLING ----------

CUSTOM_CSS = """
<style>
    /* Import a Caslon-like serif font for the hero heading */
    @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;500;600&display=swap');


    /* App background + base text */
    .stApp {
        background-color: #F5F7FB;
        color: #0f172a;
        font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }

    /* Center column width */
    .block-container {
        max-width: 960px;
        margin: 0 auto;
        padding-top: 2.5rem;
        padding-bottom: 3rem;
    }

    /* Top-left wordmark + tagline */
    .tesorin-logo-word {
        font-weight: 600;
        letter-spacing: 0.04em;
        font-size: 0.9rem;
        text-transform: uppercase;
    }

    .tesorin-tagline {
        font-size: 0.85rem;
        color: #6b7280;
        margin-top: 0.15rem;
        margin-bottom: 1.4rem;
    }

        /* Big hero heading in Caslon-like serif */
    .tesorin-hero-heading {
        font-family: "Adobe Caslon Pro", "Cormorant Garamond", "Times New Roman", serif;
        font-size: 2.7rem;
        line-height: 1.1;
        font-weight: 500;
        letter-spacing: 0.01em;
        margin: 0.5rem 0 1.75rem;
    }

    .tesorin-hero-heading strong {
        color: #16a34a;   /* calm green accent */
        font-weight: 600;
    }


    /* The pill-shaped hero card */
    .tesorin-hero-card {
        border-radius: 999px;
        padding: 1.1rem 1.75rem;
        background: #f4fef8;
        border: 1px solid rgba(15, 23, 42, 0.06);
        box-shadow: 0 22px 40px -30px rgba(15, 23, 42, 0.55);
    }


    }

</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# ---------- SMALL HELPERS ----------


def get_currency(country_code):
    """Return currency symbol for a given country code."""
    if country_code == "IN":
        return "₹"
    return "$"


def init_state():
    """Initialise all keys in session_state that we use."""
    ss = st.session_state

    if "screen" not in ss:
        ss.screen = "landing"  # landing, signup, login, country_profile, wealthflow

    if "user" not in ss:
        ss.user = None  # dict with email/name once signed in

    if "profile" not in ss:
        ss.profile = {
            "country": "IN",
            "age": 25,
            "income": 0.0,
            "expenses": 0.0,
            "savings": 0.0,
            "debt": 0.0,
            "high_interest_debt": False,
            "goals": [],
        }

def sync_screen_from_query_params():
    """
    Let the URL control which screen is open, so links like ?screen=signup work.
    """
    params = st.experimental_get_query_params()
    raw = params.get("screen")
    if not raw:
        return

    screen_from_url = raw[0]
    valid = {"landing", "signup", "login", "country_profile", "wealthflow"}
    if screen_from_url in valid:
        st.session_state.screen = screen_from_url

# ---------- SCREENS ----------


def page_landing():
    """First screen: simple hero + Sign up / Log in buttons."""
    spacer_left, main, spacer_right = st.columns([0.5, 2, 0.5])

    with main:
        # Logo + tagline
        st.markdown(
            """
            <div class="tesorin-logo-word">Tesorin</div>
            <div class="tesorin-tagline">Start small. Plan big.</div>
            """,
            unsafe_allow_html=True,
        )

        # Caslon-style hero heading
        st.markdown(
            """
            <h1 class="tesorin-hero-heading">
              Build your first <strong>serious money plan.</strong>
            </h1>
            """,
            unsafe_allow_html=True,
        )

        st.caption("Get started by creating an account or logging in.")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Sign up", use_container_width=True):
                st.session_state.screen = "signup"
        with col2:
            if st.button("Log in", use_container_width=True):
                st.session_state.screen = "login"


def page_signup():
    """Sign-up form: name (optional), email, password, terms."""

    spacer_left, main, spacer_right = st.columns([1, 2, 1])
    with main:
        st.markdown("### Create your Tesorin account")

        with st.form("signup_form", clear_on_submit=False):
            name = st.text_input("Preferred name (optional)")
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            agree = st.checkbox("I agree to the terms and conditions")

            submitted = st.form_submit_button("Sign up")

        if submitted:
            if not email or not password:
                st.error("Email and password are required.")
                return

            if not agree:
                st.error("Please agree to the terms to continue.")
                return

            ok, err = sign_up(email, password, name=name or None)
            if not ok:
                st.error(err or "Could not sign up right now.")
                return

            # Fake user object, real app would use returned Supabase user
            st.session_state.user = {"email": email, "name": name or email.split("@")[0]}
            st.session_state.screen = "country_profile"
            st.success("Account created. Let’s set your country and basic profile.")

        st.markdown("")
        if st.button("Back to start", type="secondary"):
            st.session_state.screen = "landing"


def page_login():
    """Log-in form: email, password."""

    spacer_left, main, spacer_right = st.columns([1, 2, 1])
    with main:
        st.markdown("### Welcome back")

        with st.form("login_form", clear_on_submit=False):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Log in")

        if submitted:
            if not email or not password:
                st.error("Email and password are required.")
                return

            ok, user_or_error = sign_in(email, password)
            if not ok:
                st.error(user_or_error or "Login failed.")
                return

            st.session_state.user = user_or_error
            st.session_state.screen = "country_profile"
            st.success("Logged in. Let’s confirm your country & profile.")

        st.markdown("")
        if st.button("Back to start", type="secondary"):
            st.session_state.screen = "landing"


def page_country_profile():
    """Ask for country and age before going into wealthflow."""
    st.markdown("### 1. Country & basic profile")

    ss = st.session_state
    profile = ss.profile

    # Show who is logged in
    if ss.user:
        st.caption(f"Signed in as **{ss.user.get('name', ss.user['email'])}**")

    country_display = st.selectbox(
        "Where do you manage your money?",
        ["🇮🇳 India", "🇨🇦 Canada"],
        index=0 if profile["country"] == "IN" else 1,
    )

    if "India" in country_display:
        country = "IN"
    else:
        country = "CA"

    age = st.slider("Age", min_value=18, max_value=60, value=profile["age"])

    if st.button("Continue to Wealth Flow", type="primary"):
        ss.profile["country"] = country
        ss.profile["age"] = age
        ss.screen = "wealthflow"
        st.success("Saved. Now let’s look at your cashflow and goals.")

    if st.button("Log out", type="secondary"):
        sign_out()
        ss.user = None
        ss.screen = "landing"


def page_wealthflow():
    """Main planner screen – inputs on the left, 3 cards on the right."""

    ss = st.session_state
    profile = ss.profile
    country = profile["country"]
    currency = get_currency(country)

    st.markdown("### Tesorin · Wealthflow")
    st.caption(
        "This v0.1 planner focuses on your cashflow, a simple emergency buffer, "
        "and a first pass at how to split your monthly surplus."
    )

    with st.container():
        left, right = st.columns([3, 2])

        # ---- LEFT: inputs ----
        with left:
            st.subheader("Money coming in and going out")

            income = st.number_input(
                f"Monthly income ({currency})",
                min_value=0.0,
                step=1000.0,
                value=float(profile["income"]),
            )
            expenses = st.number_input(
                f"Monthly expenses ({currency})",
                min_value=0.0,
                step=1000.0,
                value=float(profile["expenses"]),
            )
            savings = st.number_input(
                f"Current savings ({currency})",
                min_value=0.0,
                step=1000.0,
                value=float(profile["savings"]),
            )
            debt = st.number_input(
                f"Current debt ({currency})",
                min_value=0.0,
                step=1000.0,
                value=float(profile["debt"]),
            )

            high_interest_debt = st.checkbox(
                "My main debt is high-interest (credit cards, >12–15%)",
                value=bool(profile["high_interest_debt"]),
            )

            st.markdown("### Top goals (you can refine later)")
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
                default=profile.get("goals", []),
            )

            if st.button("Save this as my current snapshot", use_container_width=True):
                ss.profile.update(
                    {
                        "income": income,
                        "expenses": expenses,
                        "savings": savings,
                        "debt": debt,
                        "high_interest_debt": high_interest_debt,
                        "goals": goals,
                    }
                )

                # (Optional) later send to Supabase
                if is_configured():
                    save_profile(ss.profile)

                st.success("Snapshot saved. The numbers on the right are now updated.")

        # ---- RIGHT: three 'cards' ----
        with right:
            # Core calculations (used by all three sections)
            cashflow = calculate_cashflow(income, expenses)
            net_worth = calculate_net_worth(savings, debt)
            savings_rate = calculate_savings_rate(income, cashflow)
            low_target, high_target = savings_rate_target(country, income)

            e_target = emergency_fund_target(expenses, debt)
            e_gap = max(e_target - savings, 0)
            monthly_fill = e_gap / 12 if e_gap > 0 else 0

            plan = allocate_monthly_plan(
                income=income,
                expenses=expenses,
                country=country,
                debt=debt,
                high_interest_debt=high_interest_debt,
            )
            rec = plan["recommended_saving"]

            # --- Card 1: Financial health snapshot ---
            with st.container():
                st.markdown("#### Financial health snapshot")

                c1, c2 = st.columns(2)
                with c1:
                    st.metric("Net worth", f"{currency}{net_worth:,.0f}")
                with c2:
                    st.metric("Monthly free cash", f"{currency}{cashflow:,.0f}")

                if high_target > 0:
                    st.caption(
                        f"Target savings range: **{low_target:.0f}%–{high_target:.0f}%** of income."
                    )

                bar_value = max(min(int(savings_rate), 100), 0)
                st.progress(bar_value if bar_value > 0 else 0)
                st.caption(f"Current savings rate: **{savings_rate:.1f}%** of income.")

            st.markdown("")  # spacing

            # --- Card 2: Monthly cashflow +/- ---
            with st.container():
                st.markdown("#### Monthly cashflow +/-")

                if cashflow > 0:
                    st.success(
                        f"After your current expenses, you have about **{currency}{cashflow:,.0f}** "
                        f"left each month to put toward safety and goals."
                    )
                elif cashflow < 0:
                    st.error(
                        f"Right now you’re short about **{currency}{abs(cashflow):,.0f}** each month. "
                        "Even small changes on income or spending will make this planner more powerful."
                    )
                else:
                    st.info(
                        "You’re roughly breaking even each month. "
                        "A small surplus will help you fund an emergency cushion and goals."
                    )

                if e_gap > 0:
                    st.caption(
                        f"Suggested safety buffer: **{currency}{e_target:,.0f}**. "
                        f"At roughly **{currency}{monthly_fill:,.0f} per month** you’d build this in about a year."
                    )
                else:
                    st.caption(
                        "Your current savings already cover this simple emergency buffer rule."
                    )

            st.markdown("")  # spacing

            # --- Card 3: Long & short term you ---
            with st.container():
                st.markdown("#### Long & short term you")

                if goals:
                    goals_list = ", ".join(goals)
                    st.write(f"Top goals you’ve picked: **{goals_list}**.")
                else:
                    st.write("You haven’t picked any specific goals yet.")

                if rec > 0:
                    st.caption(
                        f"Based on your numbers, a reasonable target for monthly saving is "
                        f"around **{currency}{rec:,.0f}** split across safety, investing, and debt."
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
                        "Once your monthly cashflow is positive, this section will show "
                        "how to split that surplus between safety, investing, and debt."
                    )

    st.markdown("---")
    col_left, col_right = st.columns([1, 1])
    with col_left:
        if st.button("Back to country & profile", type="secondary"):
            st.session_state.screen = "country_profile"

    with col_right:
        if st.button("Log out", type="secondary"):
            sign_out()
            st.session_state.user = None
            st.session_state.screen = "landing"

    st.caption(
        "Later, these sections can become their own tabs – Dashboard, Goals, Plan – "
        "but for now everything lives in this Wealthflow view."
    )


# ---------- MAIN ROUTER ----------


def main():
    init_state()
    sync_screen_from_query_params()
    screen = st.session_state.screen

    if screen == "landing":
        page_landing()
    elif screen == "signup":
        page_signup()
    elif screen == "login":
        page_login()
    elif screen == "country_profile":
        page_country_profile()
    elif screen == "wealthflow":
        page_wealthflow()
    else:
        # Fallback – shouldn't happen
        st.session_state.screen = "landing"
        page_landing()


if __name__ == "__main__":
    main()

