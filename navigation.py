# navigation.py
import streamlit as st
from supabase_client import sign_out


def render_top_navbar() -> None:
    """Top-right Navigation ▾ menu used on the main app pages."""
    ss = st.session_state

    # columns just to right-align the expander a bit
    col_left, col_right = st.columns([5, 1])
    with col_right:
        with st.expander("Navigation ▾", expanded=False):
            # ---- Profile button ----
            if st.button("Profile", key="nav_profile", use_container_width=True):
                # Go to the profile/KYC page
                ss.screen = "country_profile"
                # don't touch main_tab here; profile page will redirect back to main
                st.rerun()

            # ---- Log out button ----
            if st.button("Log out", key="nav_logout", use_container_width=True):
                sign_out()
                ss.user = None
                ss.screen = "landing"
                ss.main_tab = "home"
                st.rerun()
