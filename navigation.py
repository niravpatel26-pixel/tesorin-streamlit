import streamlit as st

from supabase_client import sign_out


def render_app_header_and_nav(subtitle: str = "Wealthflow planner") -> None:
    """Top app bar with app name and a small navigation dropdown on the right."""
    ss = st.session_state

    # Main header bar
    st.markdown(
        f"""
        <div class="tesorin-appbar">
          <div class="tesorin-appbar-left">
            <div class="tesorin-app-icon">T</div>
            <div>
              <div class="tesorin-app-title">Tesorin</div>
              <div class="tesorin-app-subtitle">{subtitle}</div>
            </div>
          </div>
          <div class="tesorin-app-subtitle">
            {ss.user.get("name", ss.user["email"]) if ss.get("user") else "Logged out"}
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Align the dropdown to the top-right using columns
    top_left, top_right = st.columns([5, 1])
    with top_right:
        with st.expander("Navigation ▾", expanded=False):
            if st.button("Profile & basics", use_container_width=True, key="nav_profile"):
                ss.screen = "profile"
                ss.main_tab = "home"
                st.rerun()

            if st.button("Log out", use_container_width=True, key="nav_logout"):
                sign_out()
                ss.user = None
                ss.screen = "landing"
                st.rerun()
