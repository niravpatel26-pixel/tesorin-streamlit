import streamlit as st
from datetime import date


def get_currency(country_code: str) -> str:
    if country_code == "IN":
        return "₹"
    return "$"


def get_wallet_by_id(wallets, wallet_id):
    for w in wallets:
        if w["id"] == wallet_id:
            return w
    return None


def compute_wallet_stats(wallet, start_date, end_date):
    txns = [
        t
        for t in wallet["transactions"]
        if start_date <= t["date"] <= end_date
    ]
    balance = sum(t["amount"] for t in txns)
    income = sum(t["amount"] for t in txns if t["amount"] > 0)
    expenses = sum(-t["amount"] for t in txns if t["amount"] < 0)
    change = balance
    return {
        "balance": balance,
        "income": income,
        "expenses": expenses,
        "change": change,
        "transactions": txns,
    }


def render_wealthflow_tab() -> None:
    ss = st.session_state
    profile = ss.profile
    country = profile["country"]
    currency = get_currency(country)

    st.subheader("Wealthflow · wallets & transactions")

    period_value = st.date_input("Period", value=ss.wealthflow_period)
    if isinstance(period_value, (list, tuple)) and len(period_value) == 2:
        start_date, end_date = period_value
    else:
        start_date = end_date = period_value
    ss.wealthflow_period = (start_date, end_date)

    wallets = ss.wallets
    wallet = get_wallet_by_id(wallets, ss.selected_wallet_id) or wallets[0]
    stats = compute_wallet_stats(wallet, start_date, end_date)

    if ss.wealthflow_view == "overview":
        col_wallet, col_buttons = st.columns([2, 1])
        with col_wallet:
            balance_color = "#16a34a" if stats["balance"] >= 0 else "#ef4444"
            wallet_html = f"""
            <div class="tesorin-wallet-card">
              <div class="tesorin-wallet-name">{wallet['name']}</div>
              <div class="tesorin-wallet-balance" style="color:{balance_color};">
                {currency}{stats['balance']:,.2f}
              </div>
              <div class="tesorin-wallet-meta">
                {len(stats['transactions'])} transactions in this period
              </div>
            </div>
            """
            st.markdown(wallet_html, unsafe_allow_html=True)
        with col_buttons:
            if st.button("Open wallet", use_container_width=True):
                ss.wealthflow_view = "wallet"
                st.rerun()

        st.markdown("")
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.metric("Current balance", f"{currency}{stats['balance']:,.2f}")
        with c2:
            st.metric("Period change", f"{currency}{stats['change']:,.2f}")
        with c3:
            st.metric("Period expenses", f"{currency}{-stats['expenses']:,.2f}")
        with c4:
            st.metric("Period income", f"{currency}{stats['income']:,.2f}")

        st.caption(
            "Later this view can show charts for changes over days/weeks and category donuts. "
            "For now it’s a simple snapshot."
        )

    else:
        if st.button("← Back to wallets", use_container_width=True):
            ss.wealthflow_view = "overview"
            st.rerun()

        st.markdown(f"#### {wallet['name']} · transactions")

        with st.form("add_transaction_form"):
            tx_date = st.date_input("Date", value=date.today())
            category = st.text_input("Category", value="General")
            note = st.text_input("Note", value="")
            amount = st.number_input(
                f"Amount ({currency}) – positive for income, negative for expense",
                value=0.0,
                step=100.0,
            )
            submitted = st.form_submit_button("Add transaction")

        if submitted:
            wallet["transactions"].append(
                {
                    "date": tx_date,
                    "category": category or "General",
                    "note": note or "",
                    "amount": float(amount),
                }
            )
            st.success("Transaction added.")
            stats = compute_wallet_stats(wallet, start_date, end_date)

        st.markdown("##### Transactions in this period")
        if stats["transactions"]:
            rows = [
                {
                    "Date": t["date"].strftime("%b %d, %Y"),
                    "Category": t["category"],
                    "Note": t["note"],
                    "Amount": f"{currency}{t['amount']:,.2f}",
                }
                for t in stats["transactions"]
            ]
            st.table(rows)
        else:
            st.caption("No transactions in this period yet.")
