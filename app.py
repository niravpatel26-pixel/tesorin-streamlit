import streamlit as st
from datetime import date

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

    /* Top-left wordmark + tagline on landing */
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

    /* In-app top bar for main planner */
    .tesorin-appbar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0 0 1.1rem;
    }

    .tesorin-appbar-left {
        display: flex;
        align-items: center;
        gap: 0.6rem;
    }

    .tesorin-app-icon {
        width: 32px;
        height: 32px;
        border-radius: 999px;
        background-color: #020617;
        color: #f9fafb;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        font-size: 0.9rem;
    }

    .tesorin-app-title {
        font-weight: 600;
        font-size: 0.95rem;
    }

    .tesorin-app-subtitle {
        font-size: 0.8rem;
        color: #6b7280;
    }

    /* Generic light card style (used in Wealthflow, etc.) */
    .tesorin-card {
        border-radius: 18px;
        padding: 1.1rem 1.2rem;
        background-color: #ffffff;
        border: 1px solid rgba(15, 23, 42, 0.04);
        box-shadow: 0 16px 40px -30px rgba(15, 23, 42, 0.55);
        margin-bottom: 1rem;
    }

    .tesorin-card h4 {
        margin-top: 0;
        margin-bottom: 0.5rem;
        font-size: 0.95rem;
        font-weight: 600;
    }

    /* ---------- DARK HOME CARD ---------- */

    .tesorin-home-card {
        border-radius: 24px;
        padding: 1.3rem 1.4rem;
        background: radial-gradient(circle at 0% 0%, #0b1220 0, #020617 50%, #020617 100%);
        color: #e5e7eb;
        box-shadow: 0 28px 60px -35px rgba(15, 23, 42, 0.95);
        border: 1px solid rgba(148, 163, 184, 0.35);
    }

    .tesorin-home-title {
        font-size: 0.9rem;
        font-weight: 600;
        color: #e5e7eb;
        margin-bottom: 0.35rem;
    }

    .tesorin-home-amount {
        font-size: 2rem;
        font-weight: 600;
        color: #f9fafb;
    }

    .tesorin-home-pill {
        display: inline-flex;
        align-items: center;
        padding: 0.1rem 0.65rem;
        border-radius: 999px;
        background-color: #16a34a;
        color: #022c22;
        font-size: 0.75rem;
        font-weight: 600;
        margin-left: 0.6rem;
    }

    .tesorin-home-subcopy {
        font-size: 0.8rem;
        color: #cbd5f5;
        margin-top: 0.5rem;
        margin-bottom: 1rem;
    }

    .tesorin-home-em-card {
        margin-top: 0.4rem;
        padding: 0.75rem 0.85rem;
        border-radius: 14px;
        background-color: rgba(15, 23, 42, 0.95);
        border: 1px solid rgba(148, 163, 184, 0.5);
    }

    .tesorin-home-em-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        font-size: 0.8rem;
        margin-bottom: 0.35rem;
    }

    .tesorin-home-em-label {
        color: #e5e7eb;
        font-weight: 500;
    }

    .tesorin-home-em-percent {
        color: #cbd5f5;
        font-size: 0.8rem;
    }

    .tesorin-home-em-track {
        width: 100%;
        height: 6px;
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
        margin-top: 0.9rem;
        font-size: 0.78rem;
        color: #e5e7eb;
        padding-left: 1.1rem;
    }

    .tesorin-home-bullets li {
        margin-bottom: 0.3rem;
    }

    /* ---- Goals inside the dark Home card ---- */

    .tesorin-home-goals-section {
        margin-top: 1.1rem;
        padding-top: 0.8rem;
        border-top: 1px solid rgba(148, 163, 184, 0.45);
    }

    .tesorin-goal-row {
        margin-top: 0.55rem;
    }

    .tesorin-goal-row-top {
        display: flex;
        justify-content: space-between;
        font-size: 0.8rem;
        color: #e5e7eb;
    }

    .tesorin-goal-name {
        font-weight: 500;
    }

    .tesorin-goal-percent {
        color: #cbd5f5;
        font-size: 0.78rem;
    }

    .tesorin-goal-track {
        width: 100%;
        height: 5px;
        border-radius: 999px;
        background-color: #020617;
        overflow: hidden;
        margin: 0.35rem 0 0.25rem;
    }

    .tesorin-goal-fill {
        height: 100%;
        border-radius: 999px;
        background: linear-gradient(to right, #22c55e, #a855f7);
    }

    .tesorin-goal-amounts {
        font-size: 0.75rem;
        color: #9ca3af;
    }

    /* ---------- WEALTHFLOW (WALLETS) ---------- */

    .tesorin-wallet-card {
        border-radius: 16px;
        padding: 0.9rem 1.0rem;
        background-color: #ffffff;
        border: 1px solid rgba(148, 163, 184, 0.35);
        box-shadow: 0 18px 40px -32px rgba(15, 23, 42, 0.5);
    }

    .tesorin-wallet-name {
        font-size: 0.9rem;
        font-weight: 600;
        color: #111827;
    }

    .tesorin-wallet-balance {
        font-size: 1.1rem;
        font-weight: 600;
        margin-top: 0.25rem;
    }

    .tesorin-wallet-meta {
        font-size: 0.75rem;
        color: #6b7280;
        margin-top: 0.25rem;
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ---------- SMALL HELPERS ----------

def get_currency(country_code: str) -> str:
    """Return currency symbol for a given country code."""
    if country_code == "IN":
        return "₹"
    return "$"


def init_state() -> None:
    """Initialise all keys in session_state that we use."""
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

    if "wallets" not in ss:
        ss.wallets = [
            {
                "id": "main",
                "name": "Household wallet",
                "transactions": [],
            }
        ]


def sync_screen_from_query_params() -> None:
    """Let the URL control which screen is open, so links like ?screen=signup work."""
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
    spacer_left, main, spacer_right = st.columns([0.5, 2, 0.5])

    with main:
        st.markdown(
            """
            <div class="tesorin-logo-word">Tesorin</div>
            <div class="tesorin-tagline">Start small. Plan big.</div>
            """,
            unsafe_allow_html=True,
        )

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
                st.experimental_rerun()
        with col2:
            if st.button("Log in", use_container_width=True):
                st.session_state.screen = "login"
                st.experimental_rerun()


def page_signup() -> None:
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

            st.session_state.user = {
                "email": email,
                "name": name or email.split("@")[0],
            }
            st.session_state.screen = "country_profile"
            st.experimental_rerun()

        st.markdown("")
        if st.button("Back to start", type="secondary"):
            st.session_state.screen = "landing"
            st.experimental_rerun()


def page_login() -> None:
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
            st.experimental_rerun()

        st.markdown("")
        if st.button("Back to start", type="secondary"):
            st.session_state.screen = "landing"
            st.experimental_rerun()


def page_country_profile() -> None:
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

    if st.button("Continue to your planner", type="primary"):
        ss.profile["country"] = country
        ss.profile["age"] = age
        ss.screen = "main"
        ss.main_tab = "home"
        st.experimental_rerun()

    if st.button("Log out", type="secondary"):
        sign_out()
        ss.user = None
        ss.screen = "landing"
        st.experimental_rerun()


# ---------- HOME TAB (inside main) ----------

def render_home_tab(currency: str) -> None:
    ss = st.session_state
    profile = ss.profile

    income = float(profile["income"])
    expenses = float(profile["expenses"])
    savings = float(profile["savings"])
    debt = float(profile["debt"])

    cashflow = calculate_cashflow(income, expenses)
    savings_rate = calculate_savings_rate(income, cashflow)
    low_target, high_target = savings_rate_target(profile["country"], income)
    e_target = emergency_fund_target(expenses, debt)

    # Prefer an explicit "Emergency fund" goal if one exists
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

    # Goals snapshot
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
    <div class="tesorin-home-card">
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


def page_main() -> None:
    ss = st.session_state
    profile = ss.profile
    country = profile["country"]
    currency = get_currency(country)

    # ---------- TOP APP BAR ----------
    st.markdown(
        """
        <div class="tesorin-appbar">
          <div class="tesorin-appbar-left">
            <div class="tesorin-app-icon">T</div>
            <div>
              <div class="tesorin-app-title">Tesorin</div>
              <div class="tesorin-app-subtitle">Wealthflow planner</div>
            </div>
          </div>
          <div class="tesorin-app-subtitle">Logged in</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Top-right navigation dropdown
    render_top_navbar(sign_out)

    tab = ss.main_tab

    if tab == "home":
        render_home_tab(currency)
    elif tab == "wealthflow":
        render_wealthflow_tab(currency)
    elif tab == "next":
        render_next_step_tab(currency)

    # bottom nav
    st.markdown("")
    st.markdown("---")
    nav1, nav2, nav3 = st.columns(3)

    with nav1:
        if st.button("💸 Wealthflow", use_container_width=True):
            ss.main_tab = "wealthflow"
            st.experimental_rerun()
    with nav2:
        if st.button("🏠 Home", use_container_width=True):
            ss.main_tab = "home"
            st.experimental_rerun()
    with nav3:
        if st.button("➡ Next step", use_container_width=True):
            ss.main_tab = "next"
            st.experimental_rerun()


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
