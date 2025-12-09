import streamlit as st

def main():
    st.title("Learn – Short Guides")
    st.caption("Very short, practical explanations. Later this becomes your mini-library.")

    st.markdown("### 1. Emergency fund")
    st.write(
        "- First goal is a small buffer so you don't panic-sell or go deeper into debt.\n"
        "- For now, we use a simple rule:\n"
        "  - If you have debt → aim for **1× monthly expenses**.\n"
        "  - If you have no debt → aim for **3× monthly expenses**."
    )

    st.markdown("### 2. Savings rate")
    st.write(
        "Your **savings rate** is the % of your income that turns into savings/investments.\n"
        "Tesorin suggests a target range based on your income band and country."
    )

    st.markdown("### 3. Monthly plan")
    st.write(
        "From your free cash each month, Tesorin splits money between:\n"
        "- Emergency buffer\n"
        "- Long-term investing\n"
        "- Debt payoff (more if the debt is high-interest)"
    )

    st.info("We can expand this page later with India- / Canada-specific examples.")

if __name__ == "__main__":
    main()
