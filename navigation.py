import streamlit as st
from supabase_client import sign_out


def render_top_navbar() -> None:
    """Top-right Navigation dropdown with Profile + Logout."""
    ss = st.session_state

    _, right_col = st.columns([5, 1])
    with right_col:
        with st.expander("Navigation ▾", expanded=False):
            if st.button("Profile", use_container_width=True, key="nav_profile"):
                ss.screen = "country_profile"
                ss.main_tab = "home"
                st.rerun()

            if st.button("Log out", use_container_width=True, key="nav_logout"):
                sign_out()
                ss.user = None
                ss.screen = "landing"
                st.rerun()
