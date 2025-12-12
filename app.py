import streamlit as st
from datetime import date

from profile import render_profile_page  # ready for when you wire it in

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

from wealthflow import render_wealthflow_tab
from nextstep import render_next_step_tab
from navigation import render_top_navbar

# ---------- PAGE CONFIG ----------

st.set_page_config(
    page_title="Tesorin – First Step Planner",
    page_icon="favicon.ico",
    layout="wide",
)

CUSTOM_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;500;600&display=swap');

    /* App background + base text */
    .stApp {
        background: radial-gradient(circle at 0% 0%, #dbeafe 0, #f5f7fb 40%, #e5e7eb 100%);
        color: #0f172a;
        font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }

    .block-container {
        max-width: 960px;
        margin: 0 auto;
        padding-top: 2.5rem;
        padding-bottom: 3rem;
    }

    /* Brand header: logo + wordmark + tagline (all pages) */
    .tesorin-brand-header {
        display: flex;
        align-items: center;
        gap: 0.7rem;
        margin-top: 0.4rem;
        margin-bottom: 1.4rem;
    }

    .tesorin-brand-logo {
        width: 40px;
        height: 40px;
        border-radius: 16px;
        background: #ffffff;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 18px 60px -26px rgba(15, 23, 42, 0.55);
    }

    .tesorin-brand-logo-img {
        max-width: 24px;
        max-height: 24px;
        display: block;
    }

    .tesorin-brand-name {
        font-family: "Cormorant Garamond", "Times New Roman", serif;
        font-size: 1.1rem;
        letter-spacing: 0.32em;
        text-transform: uppercase;
        color: #020617;
    }

    .tesorin-brand-tagline {
        font-size: 0.9rem;
        color: #6b7280;
        margin-top: 0.05rem;
    }

    /* Generic dark card (hero + home main card) */
    .tesorin-dark-card {
        border-radius: 30px;
        padding: 1.8rem 1.9rem 1.9rem;
        background: radial-gradient(circle at 0% 0%, #111827 0, #020617 55%, #020617 100%);
        color: #e5e7eb;
        box-shadow:
          0 26px 80px -45px rgba(15, 23, 42, 0.95),
          0 0 0 1px rgba(148, 163, 184, 0.4);
        border: 1px solid rgba(148, 163, 184, 0.4);
    }

    /* Landing hero text */
    .tesorin-hero-title {
        font-family: "Cormorant Garamond", "Times New Roman", serif;
        font-size: 2.3rem;
        line-height: 1.1;
        margin-bottom: 0.7rem;
    }

    .tesorin-hero-body {
        font-size: 0.95rem;
        color: #cbd5f5;
        max-width: 32rem;
    }

    /* Home main card pieces */
    .tesorin-home-title {
        font-size: 0.9rem;
        font-weight: 500;
        color: #cbd5f5;
    }

    .tesorin-home-amount {
        font-size: 2.1rem;
        font-weight: 600;
        color: #f9fafb;
    }

    .tesorin-home-pill {
        display: inline-flex;
        align-items: center;
        padding: 0.15rem 0.75rem;
        border-radius: 999px;
        background-color: #16a34a;
        color: #022c22;
        font-size: 0.8rem;
        font-weight: 600;
        margin-left: 0.55rem;
    }

    .tesorin-home-subcopy {
        font-size: 0.8rem;
        color: #cbd5f5;
        margin-top: 0.4rem;
        margin-bottom: 0.9rem;
    }

    .tesorin-home-em-card {
        margin-top: 0.6rem;
        padding: 0.85rem 0.95rem;
        border-radius: 18px;
        background-color: rgba(15, 23, 42, 0.98);
        border: 1px solid rgba(148, 163, 184, 0.65);
    }

    .tesorin-home-em-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        font-size: 0.78rem;
        margin-bottom: 0.4rem;
    }

    .tesorin-home-em-label {
        color: #e5e7eb;
        font-weight: 500;
    }

    .tesorin-home-em-percent {
        color: #cbd5f5;
        font-size: 0.78rem;
    }

    .tesorin-home-em-track {
        width: 100%;
        height: 7px;
        border-radius: 999px;
        background-color: #020617;
        overflow: hidden;
        margin-bottom: 0.4rem;
    }

    .tesorin-home-em-fill {
        height: 100%;
        border-radius: 999px;
        background: linear-gradient(to right, #38bdf8, #22c55e);
    }

    .tesorin-home-em-copy {
        font-size: 0.78rem;
        color: #9ca3af;
    }

    .tesorin-home-bullets {
        margin-top: 1.0rem;
        font-size: 0.78rem;
        color: #e5e7eb;
        padding-left: 1.1rem;
    }

    .tesorin-home-bullets li {
        margin-bottom: 0.35rem;
    }

    .tesorin-home-goals-section {
        margin-top: 0.9rem;
        padding-top: 0.8rem;
        border-top: 1px dashed rgba(148, 163, 184, 0.6);
    }

    .tesorin-goal-row {
        margin-top: 0.45rem;
    }

    .tesorin-goal-row-top {
        display: flex;
        justify-content: space-between;
        font-size: 0.78rem;
        color: #e5e7eb;
    }

    .tesorin-goal-name {
        font-weight: 500;
    }

    .tesorin-goal-percent {
        color: #cbd5f5;
    }

    .tesorin-goal-track {
        width: 100%;
        height: 5px;
        border-radius: 999px;
        background-color: #020617;
        overflow: hidden;
        margin: 0.3rem 0 0.2rem;
    }

    .tesorin-goal-fill {
        height: 100%;
        border-radius: 999px;
        background: linear-gradient(to right, #22c55e, #0ea5e9);
    }

    .tesorin-goal-amounts {
        font-size: 0.74rem;
        color: #9ca3af;
    }

    /* In-app small subtitle (above tabs) */
    .tesorin-app-subtitle {
        font-size: 0.85rem;
        color: #6b7280;
        margin-bottom: 0.4rem;
    }

    /* Global button theming */
    div.stButton > button {
        border-radius: 999px;
        border: 1px solid rgba(148, 163, 184, 0.6);
        background: #ffffff;
        color: #0f172a;
        font-size: 0.85rem;
        padding: 0.45rem 1.4rem;
        font-weight: 500;
        box-shadow: 0 10px 25px -18px rgba(15, 23, 42, 0.8);
    }

    div.stButton > button:hover {
        border-color: #0ea5e9;
        background: #eff6ff;
        color: #0f172a;
    }
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ---------- SMALL HELPERS ----------


def render_brand_header() -> None:
    """Brand logo + TESORIN wordmark shown on every page."""
    st.markdown(
        """
        <div class="tesorin-brand-header">
          <div class="tesorin-brand-logo">
            <img src="favicon.png" alt="Tesorin logo" class="tesorin-brand-logo-img" />
          </div>
          <div>
            <div class="tesorin-brand-name">TESORIN</div>
            <div class="tesorin-brand-tagline">Start small. Plan big.</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def get_currency(country_code: str) -> str:
    if country_code == "IN":
        return "₹"
    return "$"


def init_state() -> None:
    ss = st.session_state

    if "screen" not in ss:
        ss.screen = "landing"

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

    if "main_tab" not in ss:
        ss.main_tab = "home"

    if "wallets" not in ss:
        ss.wallets = [
            {
                "id": "main",
                "name": "Household wallet",
                "transactions": [],
            }
        ]

    if "wealthflow_view" not in ss:
        ss.wealthflow_view = "overview"

    if "selected_wallet_id" not in ss:
        ss.selected_wallet_id = "main"

    if "wealthflow_period" not in ss:
        today = date.today()
        start = today.replace(day=1)
        ss.wealthflow_period = (start, today)

    if "next_step" not in ss:
        ss.next_step = {
            "primary_goal": None,
            "timeframe": None,
            "why": "",
            "risk": 3,
            "monthly_amount": 0.0,
            "nickname": "",
            "target_amount": 0.0,
        }

    if "goal_plans" not in ss:
        ss.goal_plans = []


def sync_screen_from_query_params() -> None:
    params = st.experimental_get_query_params()
    raw = params.get("screen")
    if not raw:
        return
    screen_from_url = raw[0]
    valid = {"landing", "signup", "login", "country_profile", "main"}
    if screen_from_url in valid:
        st.session_state.screen = screen_from_url


# ---------- SCREENS ----------

def page_landing() -> None:
    render_brand_header()

    left, main, right = st.columns([0.6, 2, 0.6])
    with main:
        st.markdown(
            """
            <div class="tesorin-dark-card">
              <div class="tesorin-hero-title">
                Build your first serious money plan.
              </div>
              <div class="tesorin-hero-body">
                A calm place to see your cashflow, buffer, and goals —
                without trading screens or product noise.
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("")  # spacer

        c1, c2 = st.columns(2)
        with c1:
            if st.button("Sign up", key="landing_signup", use_container_width=True):
                st.session_state.screen = "signup"
                st.rerun()
        with c2:
            if st.button("Log in", key="landing_login", use_container_width=True):
                st.session_state.screen = "login"
                st.rerun()

        st.caption(
            "No credit card required · Built for beginners taking money seriously for the first time."
        )


def page_signup() -> None:
    render_brand_header()

    spacer_left, main, spacer_right = st.columns([1, 2, 1])
    with main:
        st.markdown("### Sign up")

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

            st.session_state.user = {
                "email": email,
                "name": name or email.split("@")[0],
            }
            # After sign-up, still go via basic profile / country page
            st.session_state.screen = "country_profile"
            st.rerun()

        st.markdown("")
        if st.button("Back to start"):
            st.session_state.screen = "landing"
            st.rerun()


def page_login() -> None:
    render_brand_header()

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
            # After login, go straight to main app (no profile/country screen)
            st.session_state.screen = "main"
            st.session_state.main_tab = "home"
            st.rerun()

        st.markdown("")
        if st.button("Back to start"):
            st.session_state.screen = "landing"
            st.rerun()


def page_country_profile() -> None:
    render_brand_header()

    ss = st.session_state
    profile = ss.profile

    st.markdown("### 1. Country & basic profile")

    if ss.user:
        st.caption(f"Signed in as **{ss.user.get('name', ss.user['email'])}**")

    country_display = st.selectbox(
        "Where do you manage your money?",
        ["🇮🇳 India", "🇨🇦 Canada"],
        index=0 if profile["country"] == "IN" else 1,
    )

    country = "IN" if "India" in country_display else "CA"

    age = st.slider("Age", min_value=18, max_value=60, value=profile["age"])

    if st.button("Continue to your planner"):
        ss.profile["country"] = country
        ss.profile["age"] = age
        ss.screen = "main"
        ss.main_tab = "home"
        st.rerun()

    if st.button("Log out"):
        sign_out()
        ss.user = None
        ss.screen = "landing"
        st.rerun()


def render_home_tab() -> None:
    ss = st.session_state
    profile = ss.profile
    country = profile["country"]
    currency = get_currency(country)

    income = float(profile["income"])
    expenses = float(profile["expenses"])
    savings = float(profile["savings"])
    debt = float(profile["debt"])

    cashflow = calculate_cashflow(income, expenses)
    savings_rate = calculate_savings_rate(income, cashflow)
    low_target, high_target = savings_rate_target(country, income)
    e_target = emergency_fund_target(expenses, debt)

    emergency_goal = None
    for g in ss.goal_plans:
        name = g.get("name", "").lower()
        kind = g.get("kind", "").lower()
        if "emergency" in name or "emergency" in kind:
            emergency_goal = g
            break

    if emergency_goal and emergency_goal.get("target", 0) > 0:
        em_target = float(emergency_goal["target"])
        em_saved = float(emergency_goal.get("saved", 0.0))
        em_ratio = max(0.0, min(1.0, em_saved / em_target))
    else:
        if e_target > 0:
            em_ratio = max(0.0, min(1.0, savings / e_target))
        else:
            em_ratio = 0.0
        em_target = float(e_target)
        em_saved = float(savings)

    em_percent = em_ratio * 100
    cashflow_display = cashflow if cashflow > 0 else 0.0

    goals_html = ""
    if ss.goal_plans:
        rows = ""
        for goal in ss.goal_plans[:3]:
            target = float(goal.get("target", 0.0) or 0.0)
            saved = float(goal.get("saved", 0.0) or 0.0)
            if target > 0:
                pct = int(min(100, max(0, saved / target * 100)))
                amounts_text = f"{currency}{saved:,.0f} / {currency}{target:,.0f}"
            else:
                pct = 0
                amounts_text = f"{currency}{saved:,.0f} saved"

            rows += (
                '<div class="tesorin-goal-row">'
                '  <div class="tesorin-goal-row-top">'
                f'    <span class="tesorin-goal-name">{goal["name"]}</span>'
                f'    <span class="tesorin-goal-percent">{pct}%</span>'
                "  </div>"
                '  <div class="tesorin-goal-track">'
                f'    <div class="tesorin-goal-fill" style="width:{pct}%;"></div>'
                "  </div>"
                f'  <div class="tesorin-goal-amounts">{amounts_text}</div>'
                "</div>"
            )

        goals_html = (
            '<div class="tesorin-home-goals-section">'
            '  <div class="tesorin-home-title" style="margin-bottom:0.25rem;">'
            '    Goals snapshot'
            "  </div>"
            f"{rows}"
            "</div>"
        )

    home_html = f"""
    <div class="tesorin-dark-card">
      <div class="tesorin-home-title">Monthly cash flow after expenses</div>
      <div>
        <span class="tesorin-home-amount">{currency}{cashflow_display:,.0f}</span>
        <span class="tesorin-home-pill">to work with</span>
      </div>
      <div class="tesorin-home-subcopy">
        Tesorin suggests how much to save, invest, and keep aside so you’re not guessing every month.
      </div>

      <div class="tesorin-home-em-card">
        <div class="tesorin-home-em-header">
          <span class="tesorin-home-em-label">Emergency fund</span>
          <span class="tesorin-home-em-percent">{em_percent:.0f}% funded</span>
        </div>
        <div class="tesorin-home-em-track">
          <div class="tesorin-home-em-fill" style="width: {em_percent:.0f}%;"></div>
        </div>
        <div class="tesorin-home-em-copy">
          Track key goals — safety buffer, debt payoff, and long-term investing — in one calm view.
          <br />
          Current buffer: {currency}{em_saved:,.0f} / {currency}{em_target:,.0f}
        </div>
      </div>

      <ul class="tesorin-home-bullets">
        <li>Clear priorities: safety first, then debt, then long-term wealth.</li>
        <li>Built for people taking money seriously for the first time.</li>
        <li>Designed for beginners — no trading screen, no product push, just planning.</li>
      </ul>

      {goals_html}
    </div>
    """
    st.markdown(home_html, unsafe_allow_html=True)


# ---------- MAIN APP SHELL ----------

def page_main() -> None:
    ss = st.session_state

    # Global Tesorin header (logo + tagline)
    render_brand_header()

    # Top-right navigation (Profile / Log out)
    render_top_navbar()

    tab = ss.main_tab

    if tab == "home":
        render_home_tab()
    elif tab == "wealthflow":
        render_wealthflow_tab()
    elif tab == "next":
        render_next_step_tab()

    # Bottom tab navigation
    st.markdown("")
    st.markdown("---")
    nav1, nav2, nav3 = st.columns(3)

    with nav1:
        if st.button("💸 Wealthflow", use_container_width=True):
            ss.main_tab = "wealthflow"
            st.rerun()
    with nav2:
        if st.button("🏠 Home", use_container_width=True):
            ss.main_tab = "home"
            st.rerun()
    with nav3:
        if st.button("➡ Next step", use_container_width=True):
            ss.main_tab = "next"
            st.rerun()


# ---------- MAIN ROUTER ----------

def main() -> None:
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
    elif screen == "main":
        page_main()
    else:
        st.session_state.screen = "landing"
        page_landing()


if __name__ == "__main__":
    main()
