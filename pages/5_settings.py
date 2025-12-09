import streamlit as st


def main():
    st.title("Settings")

    st.write("This is a simple placeholder for now.")

    if "profile" in st.session_state:
        st.json(st.session_state.profile, expanded=False)

    if st.button("Reset local data"):
        for key in ["profile"]:
            if key in st.session_state:
                del st.session_state[key]
        st.success("Local session reset. Go to Home to start fresh.")


if __name__ == "__main__":
    main()
