import streamlit as st

from logic import (
    calculate_cashflow,
    calculate_net_worth,
    calculate_savings_rate,
    emergency_fund_target,
    savings_rate_target,
    allocate_monthly_plan,
)
from supabase_client import is_configured, save_profile, load_profile


# ---- PAGE CONFIG ----
st.set_page_config(
    page_title="Tesorin – First Step Planner",
    page_icon="favicon.ico",
    layout="wide",
)


# ---- GLOBAL STATE HELPERS ----
def init_profile_state():
    """Load latest profile from Supabase if available, else default."""
    if "profile" not in st.session_state:
        loaded = None
        if is_configured():
            loaded = load_profile(user_id=None)

        st.session_state.profile = loaded or {
            "country": "IN",
            "age": 25,
            "income": 0.0,
            "expenses": 0.0,
            "savings": 0.0,
            "debt": 0.0,
            "high_interest_debt": False,
            "goals": [],
        }


def init_nav_state():
    if "page" not in st.session_state:
        # first screen user sees
        st.session_state.page = "landing"
    if "user" not in st.session_state:
        st.session_state.user = None


def get_currency(country_code: str) -> str:
    if country_code == "IN":
        return "₹"
    return "$"


# ---- LAYOUT UTILITIES ----
def home_button():
    """Bottom 'Home' button used on inner pages."""
    st.markdown("---")
    if st.button("🏠 Home", use_container_width=True):
        st.session_state.page = "home"
        st.experimental_rerun()


def top_right_menu():
    """Tiny profile/settings/learn menu in top-right."""
    cols = st.columns([8, 1])
    with cols[1]:
        if st.button("☰", key="top_menu"):
            st.session_state.page = "profile"
            st.experimental_rerun()


# ---- SCREENS ----
def page_landing():
    """Landing screen with visuals + Sign up / Login."""
    st.markdown("### Tesorin")
    st.markdown("#### Start small. Plan big.")

    st.write(
        "A calm space to understand your money, your goals, and the few moves that matter."
    )

    # Placeholder for "moving images about Tesorin"
    st.markdown(
        """
        <div style="height:220px;border-radius:24px;
                    background:linear-gradient(135deg,#0f172a,#22c55e);
                    display:flex;align-items:center;justify-content:center;
                    color:white;font-size:1.1rem;">
            Future: moving visuals / simple animation about how Tesorin works.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.write("")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Sign up", use_container_width=True):
            st.session_state.page = "signup"
            st.experimental_rerun()
    with col2:
        if st.button("Log in", use_container_width=True):
            st.session_state.page = "login"
            st.experimental_rerun()


def page_signup():
    """Sign up screen (preferred name, email, password, terms)."""
    st.markdown("### Create your Tesorin account")

    with st.form("signup_form"):
        name = st.text_input("Preferred name (optional)")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        agree = st.checkbox("I agree to the Terms and Conditions")
        submitted = st.form_submit_button("Sign up")

    if submitted:
        if not email or not password:
            st.error("Email and password are required.")
        elif not agree:
            st.error("You need to accept the terms to continue.")
        else:
            # TODO: replace with real Supabase Auth sign-up
            st.session_state.user = {"name": name or "there", "email": email}
            st.session_state.page = "home"
            st.success("Account created – welcome to Tesorin!")
            st.experimental_rerun()

    if st.button("Back to landing"):
        st.session_state.page = "landing"
        st.experimental_rerun()


def page_login():
    """Login screen (email, password, forgot password)."""
    st.markdown("### Log in to Tesorin")

    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Log in")

    if submitted:
        if not email or not password:
            st.error("Please enter both email and password.")
        else:
            # TODO: replace with real Supabase Auth sign-in
            st.session_state.user = {"name": "Friend", "email": email}
            st.session_state.page = "home"
            st.success("Logged in.")
            st.experimental_rerun()

    st.markdown("[Forgot password?](#)")
    if st.button("Back to landing"):
        st.session_state.page = "landing"
        st.experimental_rerun()


def page_home():
    """Hub screen with three big cards / navigation buttons."""
    top_right_menu()

    user = st.session_state.user
    name = user["name"] if user and user.get("name") else "there"

    st.markdown(f"### Hi {name}, where would you like to start?")
    st.caption("Pick a tile to work on one part of your money today.")

    st.write("")
    st.markdown(
        """
        <style>
        .tesorin-card button {
            border-radius: 24px !important;
            border: 1px solid #e5e7eb !important;
            padding: 18px 20px !important;
            font-size: 1.05rem !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    container = st.container()
    with container:
        if st.button("Monthly cashflow", key="card_cashflow", use_container_width=True):
            st.session_state.page = "cashflow"
            st.experimental_rerun()

        if st.button(
            "Financial health snapshot / net worth",
            key="card_snapshot",
            use_container_width=True,
        ):
            st.session_state.page = "snapshot"
            st.experimental_rerun()

        if st.button("Goal tracker", key="card_goals", use_container_width=True):
            st.session_state.page = "goals"
            st.experimental_rerun()

    st.markdown("---")
    st.caption(
        "Tip: You don’t have to do everything in one session. "
        "Even a 5-minute snapshot is progress."
    )


def page_cashflow():
    """Wealth flow page – your current v0.1 planner layout."""
    top_right_menu()
    st.markdown("### Wealth flow – record income & expenses")
    st.caption("This is the same engine we already built, now framed as 'Monthly cashflow'.")

    init_profile_state()

    with st.container():
        left, right = st.columns([3, 2])

        # ----- LEFT: INPUTS -----
        with left:
            st.subheader("1. Basic profile & cashflow")

            country_display = st.selectbox(
                "Where do you manage your money?",
                ["🇮🇳 India", "🇨🇦 Canada"],
            )

            if "India" in country_display:
                country = "IN"
            else:
                country = "CA"

            currency = get_currency(country)

            age = st.slider("Age", min_value=18, max_value=60, value=25)

            income = st.number_input(
                f"Monthly income ({currency})", min_value=0.0, step=1000.0
            )
            expenses = st.number_input(
                f"Monthly expenses ({currency})", min_value=0.0, step=1000.0
            )
            savings = st.number_input(
                f"Current savings ({currency})", min_value=0.0, step=1000.0
            )
            debt = st.number_input(
                f"Current debt ({currency})", min_value=0.0, step=1000.0
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

                if is_configured():
                    save_profile(st.session_state.profile)

                st.success("Snapshot saved. Other pages now use these numbers.")

        # ----- RIGHT: SNAPSHOT -----
        with right:
            st.subheader("Quick snapshot")

            profile = st.session_state.profile

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
                st.metric("Net worth", f"{currency}{net_worth:,.0f}")
            with c2:
                st.metric("Monthly free cash", f"{currency}{cashflow:,.0f}")

            low_target, high_target = savings_rate_target(country, income)
            if high_target > 0:
                st.caption(
                    f"Target savings range for you: "
                    f"**{low_target:.0f}%–{high_target:.0f}%** of income."
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
                    f"If you put around **{currency}{monthly_fill:,.0f} per month** aside "
                    "for a year, you’d fully fund this buffer."
                )
            else:
                st.success("Your current savings already cover this simple buffer rule.")

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
                    f"Recommended monthly saving (target vs. cashflow): "
                    f"**{currency}{rec:,.0f}**"
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
                    "Cashflow is not positive yet. Small fixes on income/spending "
                    "will make the plan more useful."
                )

    home_button()


def page_snapshot():
    """Very lightweight 'Financial health snapshot / net worth' page."""
    top_right_menu()
    st.markdown("### Financial health snapshot / net worth")

    init_profile_state()
    p = st.session_state.profile
    currency = get_currency(p["country"])

    cashflow = calculate_cashflow(p["income"], p["expenses"])
    net_worth = calculate_net_worth(p["savings"], p["debt"])
    savings_rate = calculate_savings_rate(p["income"], cashflow)

    st.metric("Net worth", f"{currency}{net_worth:,.0f}")
    st.metric("Monthly free cash", f"{currency}{cashflow:,.0f}")
    st.metric("Savings rate", f"{savings_rate:.1f}%")

    st.write("")
    st.caption(
        "This view is for a quick sense of where you stand. "
        "You can update the numbers on the Wealth flow page."
    )

    home_button()


def page_goals():
    """Next step – simple goal planner / tracker."""
    top_right_menu()
    st.markdown("### Next step – plan your goals")

    init_profile_state()
    p = st.session_state.profile
    currency = get_currency(p["country"])

    st.write(
        "Pick a single focus goal to work on next, and we’ll estimate a simple "
        "monthly amount using a no-frills rule of thumb."
    )

    goal_name = st.text_input("Goal name (e.g. Emergency fund, House downpayment)")
    target_amount = st.number_input(
        f"Target amount ({currency})", min_value=0.0, step=10000.0
    )
    target_year = st.number_input("Target year", min_value=2025, max_value=2100, value=2030)

    from logic import monthly_goal_contribution  # reuse existing helper

    if goal_name and target_amount > 0:
        monthly = monthly_goal_contribution(target_amount, int(target_year))
        st.success(
            f"Roughly **{currency}{monthly:,.0f} per month** would get you to "
            f"{goal_name} by {int(target_year)} (ignoring investment returns)."
        )
    else:
        st.info("Once you enter a goal and amount, we’ll show a monthly suggestion.")

    home_button()


def page_profile():
    """Placeholder for profile / settings / learn."""
    top_right_menu()
    st.markdown("### Profile & settings (placeholder)")
    st.write(
        "Here we can later add: profile details, country preferences, "
        "links to Learn content, export, etc."
    )

    if st.button("Log out"):
        st.session_state.user = None
        st.session_state.page = "landing"
        st.experimental_rerun()

    home_button()


# ---- MAIN ROUTER ----
def main():
    init_nav_state()

    page = st.session_state.page

    if page == "landing":
        page_landing()
    elif page == "signup":
        page_signup()
    elif page == "login":
        page_login()
    elif page == "home":
        page_home()
    elif page == "cashflow":
        page_cashflow()
    elif page == "snapshot":
        page_snapshot()
    elif page == "goals":
        page_goals()
    elif page == "profile":
        page_profile()
    else:
        # fallback
        page_landing()


if __name__ == "__main__":
    main()
