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

    /* Simple bottom nav labels (if we want text under icons later) */
    .tesorin-nav-label {
        font-size: 0.8rem;
        color: #4b5563;
        text-align: center;
        margin-top: 0.15rem;
    }

    /* Generic card style (can be used later on Home) */
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

    # Which big screen are we on?
    # landing, signup, login, country_profile, main (logged-in app shell)
    if "screen" not in ss:
        ss.screen = "landing"

    # Who is logged in (if anyone)?
    if "user" not in ss:
        ss.user = None  # dict with email/name once signed in

    # Basic profile + numbers used by the planner
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

    # Which tab inside the app shell are we on? (home, wealthflow, next)
    if "main_tab" not in ss:
        ss.main_tab = "home"


def sync_screen_from_query_params() -> None:
    """
    Let the URL control which screen is open, so links like ?screen=signup work.
    """
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


def page_signup() -> None:
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


def page_login() -> None:
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


def page_country_profile() -> None:
    """Ask for country and age before going into the main app shell."""
    ss = st.session_state
    profile = ss.profile

    st.markdown("### 1. Country & basic profile")

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

    if st.button("Continue to your planner", type="primary"):
        ss.profile["country"] = country
        ss.profile["age"] = age
        ss.screen = "main"
        ss.main_tab = "home"  # always land on Home first
        st.success("Saved. Now let’s look at your planner.")

    if st.button("Log out", type="secondary"):
        sign_out()
        ss.user = None
        ss.screen = "landing"


# ---------- MAIN APP SHELL (HOME / WEALTHFLOW / NEXT) ----------


def page_main() -> None:
    """Main app shell with 3 tabs: Home / Wealthflow / Next step."""
    ss = st.session_state
    profile = ss.profile
    country = profile["country"]
    currency = get_currency(country)

    # App-style top bar
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

    tab = ss.main_tab

    # --- HOME TAB ---
    if tab == "home":
        st.subheader("Home · snapshot")

        income = float(profile["income"])
        expenses = float(profile["expenses"])
        savings = float(profile["savings"])
        debt = float(profile["debt"])

        cashflow = calculate_cashflow(income, expenses)
        net_worth = calculate_net_worth(savings, debt)
        savings_rate = calculate_savings_rate(income, cashflow)
        low_target, high_target = savings_rate_target(country, income)
        e_target = emergency_fund_target(expenses, debt)

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Net worth", f"{currency}{net_worth:,.0f}")
        with col2:
            st.metric("Monthly free cash", f"{currency}{cashflow:,.0f}")

        if high_target > 0:
            st.caption(
                f"Target savings range: **{low_target:.0f}%–{high_target:.0f}%** of income."
            )

        bar_value = max(min(int(savings_rate), 100), 0)
        st.progress(bar_value if bar_value > 0 else 0)
        st.caption(f"Current savings rate: **{savings_rate:.1f}%** of income.")

        st.markdown("---")
        st.write(
            f"Suggested simple emergency buffer based on your expenses: "
            f"**{currency}{e_target:,.0f}**."
        )
        st.caption(
            "As you add more detail in Wealthflow and Next step, this home view will stay as your calm snapshot."
        )

    # --- WEALTHFLOW TAB ---
    elif tab == "wealthflow":
        st.subheader("Wealthflow · income & expenses")

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

        st.caption(
            "Later this tab will let you add detailed categories and daily entries. "
            "For now, it's just the core monthly numbers."
        )

        if st.button("Save basics", use_container_width=True):
            ss.profile["income"] = income
            ss.profile["expenses"] = expenses
            st.success("Saved. The Home tab now uses these numbers.")

    # --- NEXT STEP TAB ---
    elif tab == "next":
        st.subheader("Next step")

        st.write(
            "This tab will guide you through your next actions: "
            "emergency fund, debt clean-up, and one key goal."
        )
        st.write(
            "For now it's a placeholder, but the idea is that Home shows the snapshot, "
            "Wealthflow holds your day-to-day money details, and Next step tells you what to do next."
        )

    # --- Bottom nav (like an app's bottom bar) ---
    st.markdown("")
    st.markdown("---")
    nav1, nav2, nav3 = st.columns(3)

    with nav1:
        if st.button("💸 Wealthflow", use_container_width=True):
            ss.main_tab = "wealthflow"
    with nav2:
        if st.button("🏠 Home", use_container_width=True):
            ss.main_tab = "home"
    with nav3:
        if st.button("➡ Next step", use_container_width=True):
            ss.main_tab = "next"

    # --- Footer actions ---
    col_left, col_right = st.columns(2)
    with col_left:
        if st.button("Back to country & profile", type="secondary"):
            ss.screen = "country_profile"
    with col_right:
        if st.button("Log out", type="secondary"):
            sign_out()
            ss.user = None
            ss.screen = "landing"


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
        # Fallback – shouldn't happen
        st.session_state.screen = "landing"
        page_landing()


if __name__ == "__main__":
    main()
