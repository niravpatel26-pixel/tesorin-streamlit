# app.py
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
    load_profile,
    sign_up,
    sign_in,
    sign_out,
)

# ---- PAGE CONFIG ----
st.set_page_config(
    page_title="Tesorin – First Step Planner",
    page_icon="favicon.ico",
    layout="wide",
)


# ---------- SMALL HELPERS ----------

def get_currency(country_code: str) -> str:
    if country_code == "IN":
        return "₹"
    return "$"


def init_state():
    """Ensure all the keys we use exist in session_state."""
    ss = st.session_state
    if "route" not in ss:
        ss.route = "landing"
    if "user" not in ss:
        ss.user = None
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


def go(route: str):
    """Simple navigation helper."""
    st.session_state.route = route
    st.experimental_rerun()


def auth_required():
    """If no user, send them to landing/login."""
    if st.session_state.user is None:
        go("landing")


def app_header(show_back_home: bool = False):
    """Top bar used on inner pages."""
    cols = st.columns([3, 1])
    with cols[0]:
        st.markdown("### Tesorin · First Step")
        st.caption("Your calm first step into serious money planning.")
    with cols[1]:
        if st.session_state.user:
            st.write(
                f"Signed in as **{st.session_state.user.get('name') or st.session_state.user.get('email')}**"
            )
            if st.button("Log out", key="logout_btn", use_container_width=True):
                sign_out()
                st.session_state.user = None
                go("landing")
        else:
            if st.button("Log in", key="header_login", use_container_width=True):
                go("login")


# ---------- SCREENS ----------

def page_landing():
    init_state()

    st.markdown(
        """
        <style>
        .tesorin-hero {
            padding: 60px 0 40px 0;
            text-align: center;
        }
        .tesorin-hero h1 {
            font-size: 42px;
            margin-bottom: 10px;
        }
        .tesorin-hero p {
            color: #6b7280;
            font-size: 15px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    with st.container():
        st.markdown('<div class="tesorin-hero">', unsafe_allow_html=True)
        st.markdown("#### Tesorin · First Step")
        st.markdown("## Build your first serious money plan — calmly.")
        st.markdown(
            "A simple starting point to understand your **cashflow**, "
            "**safety buffer**, and **goals** without trading screens or noise."
        )
        st.markdown("</div>", unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        if st.button("Sign up", use_container_width=True):
            go("signup")
    with c2:
        if st.button("Log in", use_container_width=True):
            go("login")

    st.markdown("---")
    st.caption(
        "No real investing or bank connections yet – this is an early planning preview."
    )


def page_signup():
    init_state()

    app_header()

    st.markdown("## Create your Tesorin account")
    st.write("Start with a simple login. You can use a nickname if you like.")

    with st.form("signup_form"):
        name = st.text_input("Preferred name (optional)")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        agree = st.checkbox(
            "I understand this is an early beta and not financial advice.", value=True
        )
        submitted = st.form_submit_button("Sign up")

    if submitted:
        if not email or not password:
            st.error("Email and password are required.")
        elif not agree:
            st.error("Please accept the beta notice to continue.")
        else:
            ok, msg = sign_up(email, password, name)
            if not ok:
                st.error(msg or "Sign up failed.")
            else:
                st.success("Account created. You're now signed in.")
                st.session_state.user = {"email": email, "name": name}
                go("country")

    st.write("Already have an account?")
    if st.button("Go to Log in", key="go_login_from_signup"):
        go("login")


def page_login():
    init_state()
    app_header()

    st.markdown("## Welcome back")
    st.write("Log in to continue your Tesorin plan.")

    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Log in")

    if submitted:
        if not email or not password:
            st.error("Email and password are required.")
        else:
            ok, user_or_msg = sign_in(email, password)
            if not ok:
                st.error(user_or_msg or "Login failed.")
            else:
                st.session_state.user = user_or_msg
                # later: load profile from Supabase if configured
                if is_configured():
                    loaded = load_profile(email)
                    if loaded:
                        st.session_state.profile = loaded
                go("dashboard")

    if st.button("Forgot password? (placeholder)", key="forgot"):
        st.info(
            "In a future version this will send a reset email. For now, use any password you like – "
            "auth is still local-only."
        )

    st.write("New to Tesorin?")
    if st.button("Go to Sign up", key="go_signup_from_login"):
        go("signup")


def page_country():
    init_state()
    auth_required()
    app_header(show_back_home=True)

    st.markdown("## Step 1 · Choose your primary country")
    st.write("This helps set default currencies and savings ranges.")

    country_display = st.selectbox(
        "Where do you manage your money?",
        ["🇮🇳 India", "🇨🇦 Canada"],
    )

    if "India" in country_display:
        country = "IN"
    else:
        country = "CA"

    st.session_state.profile["country"] = country

    if st.button("Next: Basic profile", use_container_width=True):
        go("profile")


def page_profile():
    init_state()
    auth_required()
    app_header(show_back_home=True)

    profile = st.session_state.profile
    country = profile["country"]
    currency = get_currency(country)

    st.markdown("## Step 2 · Basic profile & cashflow")
    st.write("Approximate numbers are fine – this is a planning tool, not a tax return.")

    age = st.slider("Age", min_value=18, max_value=60, value=profile["age"])
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
        value=profile["high_interest_debt"],
    )

    if st.button("Next: Goals", use_container_width=True):
        profile.update(
            {
                "age": age,
                "income": income,
                "expenses": expenses,
                "savings": savings,
                "debt": debt,
                "high_interest_debt": high_interest_debt,
            }
        )
        st.session_state.profile = profile
        if is_configured():
            save_profile(profile)
        go("goals")


def page_goals():
    init_state()
    auth_required()
    app_header(show_back_home=True)

    profile = st.session_state.profile

    st.markdown("## Step 3 · Goals")
    st.write(
        "Pick what matters most right now. You can refine these later in the Goals view."
    )

    goals = st.multiselect(
        "Top goals (pick up to 3 for now)",
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

    if st.button("Finish setup and go to dashboard", use_container_width=True):
        profile["goals"] = goals
        st.session_state.profile = profile
        if is_configured():
            save_profile(profile)
        go("dashboard")


def page_dashboard():
    init_state()
    auth_required()
    app_header()

    profile = st.session_state.profile
    country = profile["country"]
    currency = get_currency(country)

    income = profile["income"]
    expenses = profile["expenses"]
    savings = profile["savings"]
    debt = profile["debt"]
    high_interest_debt = profile["high_interest_debt"]

    cashflow = calculate_cashflow(income, expenses)
    net_worth = calculate_net_worth(savings, debt)
    savings_rate = calculate_savings_rate(income, cashflow)
    low_target, high_target = savings_rate_target(country, income)

    st.markdown("## Home")

    # Main three cards
    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown("#### Monthly cashflow")
        st.metric("Cash after expenses", f"{currency}{cashflow:,.0f}")
        st.caption("Income minus your monthly expenses.")

    with c2:
        st.markdown("#### Financial health snapshot")
        st.metric("Net worth", f"{currency}{net_worth:,.0f}")
        if high_target > 0:
            st.caption(
                f"Target savings range: **{low_target:.0f}%–{high_target:.0f}%** of income."
            )
        st.caption(f"Current savings rate: **{savings_rate:.1f}%** of income.")

    with c3:
        st.markdown("#### Goal tracker")
        goals = profile.get("goals") or []
        if goals:
            st.write("Current focus:")
            for g in goals[:3]:
                st.write(f"• {g}")
        else:
            st.caption("No goals selected yet – add some to make the plan meaningful.")

    st.markdown("---")

    # Emergency fund + plan preview
    left, right = st.columns(2)

    with left:
        st.markdown("### Emergency fund")
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

    with right:
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
                    "Debt payoff": [plan["debt"]],
                }
            )
        else:
            st.info(
                "Cashflow is not positive yet. Small fixes on income/spending will make the plan more useful."
            )

    st.markdown("---")

    # Bottom nav (simple buttons that change route)
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("Wealth flow", use_container_width=True):
            go("wealth_flow")
    with c2:
        if st.button("Plan details", use_container_width=True):
            go("plan")
    with c3:
        if st.button("Settings", use_container_width=True):
            go("settings")


def page_wealth_flow():
    init_state()
    auth_required()
    app_header(show_back_home=True)

    profile = st.session_state.profile
    country = profile["country"]
    currency = get_currency(country)

    st.markdown("## Wealth flow")
    st.write("A simple place to review and tweak your income and expenses.")

    col1, col2 = st.columns(2)
    with col1:
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

    with col2:
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

    if st.button("Save changes", use_container_width=True):
        profile.update(
            {
                "income": income,
                "expenses": expenses,
                "savings": savings,
                "debt": debt,
            }
        )
        st.session_state.profile = profile
        if is_configured():
            save_profile(profile)
        st.success("Wealth flow updated.")
    if st.button("Back to dashboard", use_container_width=True):
        go("dashboard")


def page_plan():
    init_state()
    auth_required()
    app_header(show_back_home=True)

    profile = st.session_state.profile
    country = profile["country"]
    currency = get_currency(country)

    st.markdown("## Next step plan")

    income = profile["income"]
    expenses = profile["expenses"]
    savings = profile["savings"]
    debt = profile["debt"]
    high_interest_debt = profile["high_interest_debt"]

    cashflow = calculate_cashflow(income, expenses)
    plan = allocate_monthly_plan(
        income=income,
        expenses=expenses,
        country=country,
        debt=debt,
        high_interest_debt=high_interest_debt,
    )

    st.write(
        f"Each month you have **{currency}{cashflow:,.0f}** after expenses. "
        "Here’s a calm suggestion for where it might go:"
    )

    st.table(
        {
            "Bucket": ["Emergency buffer", "Investing", "Debt payoff"],
            "Suggested monthly amount": [
                f"{currency}{plan['emergency']:,.0f}",
                f"{currency}{plan['investing']:,.0f}",
                f"{currency}{plan['debt']:,.0f}",
            ],
        }
    )

    st.caption(
        "These are simple rules of thumb, not personal financial advice. "
        "You’ll tune them over time as your situation changes."
    )

    if st.button("Back to dashboard", use_container_width=True):
        go("dashboard")


def page_settings():
    init_state()
    auth_required()
    app_header(show_back_home=True)

    st.markdown("## Settings & profile")

    profile = st.session_state.profile

    st.write("You can tweak a few basics here. More settings will come later.")

    name = st.text_input(
        "Display name",
        value=(st.session_state.user or {}).get("name", ""),
    )
    goals = st.multiselect(
        "Goals",
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

    if st.button("Save settings", use_container_width=True):
        st.session_state.user["name"] = name
        profile["goals"] = goals
        st.session_state.profile = profile
        if is_configured():
            save_profile(profile)
        st.success("Settings saved.")

    if st.button("Back to dashboard", use_container_width=True):
        go("dashboard")


# ---------- ROUTER ----------

def main():
    init_state()

    route = st.session_state.route

    if route == "landing":
        page_landing()
    elif route == "signup":
        page_signup()
    elif route == "login":
        page_login()
    elif route == "country":
        page_country()
    elif route == "profile":
        page_profile()
    elif route == "goals":
        page_goals()
    elif route == "dashboard":
        page_dashboard()
    elif route == "wealth_flow":
        page_wealth_flow()
    elif route == "plan":
        page_plan()
    elif route == "settings":
        page_settings()
    else:
        # fallback
        page_landing()


if __name__ == "__main__":
    main()
