import streamlit as st


def main():
    st.title("Learn")

    st.write("Short, beginner-friendly guides will live here.")

    with st.expander("Basics · Emergency fund"):
        st.write(
            "Why a buffer matters, how many months to target, and how it fits with debt and investing."
        )

    with st.expander("Basics · Cashflow and savings rate"):
        st.write(
            "How much of your income you keep each month is more important than chasing hot returns."
        )

    with st.expander("India · SIP / PPF / NPS / ELSS"):
        st.write("Later: short explanations of each, with calm guidance.")

    with st.expander("Canada · TFSA / RRSP / credit score"):
        st.write("Later: tailored content for typical beginner questions.")


if __name__ == "__main__":
    main()
