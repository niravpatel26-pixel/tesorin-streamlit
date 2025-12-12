import streamlit as st


def render_top_navbar(sign_out_callback) -> None:
    """Top-right Navigation dropdown with Profile + Logout."""
    ss = st.session_state

    # Empty column on the left so dropdown hugs right edge visually
    _, right_col = st.columns([5, 1])
    with right_col:
        with st.expander("Navigation ▾", expanded=False):
            if st.button("Profile", use_container_width=True, key="nav_profile"):
                ss.screen = "country_profile"
                ss.main_tab = "home"
                st.experimental_rerun()

            if st.button("Log out", use_container_width=True, key="nav_logout"):
                # Call back into app's sign_out so auth state is cleared there
                sign_out_callback()
                ss.user = None
                ss.screen = "landing"
                st.experimental_rerun()
