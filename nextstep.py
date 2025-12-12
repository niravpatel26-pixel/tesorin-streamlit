import streamlit as st
from logic import (
    calculate_cashflow,
    emergency_fund_target,
)


def get_currency(country_code: str) -> str:
    if country_code == "IN":
        return "₹"
    return "$"


def render_next_step_tab() -> None:
    ss = st.session_state
    profile = ss.profile
    country = profile["country"]
    currency = get_currency(country)

    st.subheader("Next step · shape your first plan")

    ns = ss.get("next_step", {})
    ss.next_step = ns

    income = float(profile["income"])
    expenses = float(profile["expenses"])
    savings = float(profile["savings"])
    debt = float(profile["debt"])

    cashflow = calculate_cashflow(income, expenses)

    if cashflow > 0:
        st.caption(
            f"Right now it looks like you have about {currency}{cashflow:,.0f} "
            "left after expenses each month. Let’s decide what to do with that."
        )
    elif cashflow < 0:
        st.caption(
            f"Right now you’re short about {currency}{abs(cashflow):,.0f} each month. "
            "That’s okay – these questions will still help you see a direction."
        )
    else:
        st.caption(
            "You’re roughly breaking even. These questions will help you see what to focus on first."
        )

    e_target_for_default = emergency_fund_target(expenses, debt)

    primary_goal_options = [
        "Build or top up my emergency fund",
        "Clean up high-interest debt",
        "Start long-term investing",
        "Save for a specific purchase",
        "I’m not sure yet",
    ]

    def _goal_index() -> int:
        ns_local = st.session_state.get("next_step", {})
        g = ns_local.get("primary_goal")
        if g in primary_goal_options:
            return primary_goal_options.index(g)
        return 0

    timeframe_options = [
        "Next 3 months",
        "Next 6–12 months",
        "Next 2–3 years",
        "More than 3 years",
    ]

    def _time_index() -> int:
        ns_local = st.session_state.get("next_step", {})
        t = ns_local.get("timeframe")
        if t in timeframe_options:
            return timeframe_options.index(t)
        return 1

    with st.form("next_step_form", clear_on_submit=False):
        primary_goal = st.selectbox(
            "What feels like your top priority right now?",
            primary_goal_options,
            index=_goal_index(),
        )

        timeframe = st.selectbox(
            "When would you like to feel real progress on this?",
            timeframe_options,
            index=_time_index(),
        )

        default_name = ns.get("nickname", "")
        if not default_name:
            lower = primary_goal.lower()
            if "emergency fund" in lower:
                default_name = "Emergency fund"
            elif "debt" in lower:
                default_name = "Debt payoff"
            elif "investing" in lower:
                default_name = "Long-term investing"
            elif "specific purchase" in lower:
                default_name = "Big purchase"

        goal_name = st.text_input(
            "Give this goal a short name",
            value=default_name,
            placeholder="Example: Starter emergency fund, Car downpayment, etc.",
        )

        why = st.text_area(
            "In one or two sentences, why does this matter to you?",
            value=ns.get("why", ""),
            placeholder="Example: I want a 3-month buffer so I can change jobs without panic.",
        )

        target_default = ns.get("target_amount", 0.0)
        if target_default == 0 and "emergency fund" in primary_goal.lower():
            target_default = float(e_target_for_default)

        target_amount = st.number_input(
            f"Rough target amount for this goal ({currency})",
            min_value=0.0,
            step=1000.0,
            value=float(target_default),
        )

        risk = st.slider(
            "How comfortable are you with your investments moving up and down?",
            min_value=1,
            max_value=5,
            value=int(ns.get("risk", 3)),
            help="1 = I hate seeing any drops. 5 = I’m okay with swings for long-term growth.",
        )

        default_monthly = ns.get("monthly_amount", max(cashflow, 0))
        if default_monthly < 0:
            default_monthly = 0.0

        monthly_amount = st.number_input(
            f"If things go right, how much could you put toward this goal each month? ({currency})",
            min_value=0.0,
            step=100.0,
            value=float(default_monthly),
        )

        submitted = st.form_submit_button("Save answers and see next steps")

    if submitted:
        ns.update(
            {
                "primary_goal": primary_goal,
                "timeframe": timeframe,
                "why": why,
                "risk": int(risk),
                "monthly_amount": float(monthly_amount),
                "nickname": goal_name,
                "target_amount": float(target_amount),
            }
        )
        ss.next_step = ns
        st.success("Saved. Scroll down for a simple next-step plan.")

    if ns.get("primary_goal"):
        st.markdown("### Your simple next-step plan")

        goal = ns["primary_goal"]
        monthly = ns.get("monthly_amount", 0.0)
        if monthly <= 0 and cashflow > 0:
            monthly = max(cashflow * 0.3, 0)

        target = ns.get("target_amount", 0.0)
        if target == 0 and "emergency fund" in goal.lower():
            target = float(e_target_for_default)

        e_target = emergency_fund_target(expenses, debt=debt)
        gap = max(e_target - savings, 0)
        months_to_buffer = gap / monthly if monthly > 0 else None

        if "emergency fund" in goal.lower():
            st.write(
                f"**Focus:** build a simple emergency fund of about "
                f"**{currency}{e_target:,.0f}**."
            )
            lines = [
                f"- Aim to send **{currency}{monthly:,.0f} per month** into a separate high-safety account.",
            ]
            if months_to_buffer:
                lines.append(
                    f"- At that pace, you’d reach this buffer in roughly **{months_to_buffer:.1f} months**."
                )
            lines.extend(
                [
                    "- Keep investments very low-risk until this buffer is in place.",
                    "- Revisit this tab once the buffer is at least 50–75% funded.",
                ]
            )
            st.markdown("\n".join(lines))

        elif "debt" in goal.lower():
            st.write(
                "**Focus:** clean up high-interest debt while keeping a small safety cushion."
            )
            st.markdown(
                f"- Choose a fixed payment of **{currency}{monthly:,.0f} per month** toward your highest-interest debt.\n"
                "- Keep a mini-buffer of ~1 month of expenses in cash before making extra payments.\n"
                "- Each month, log payments in Wealthflow so you can see your balance trend down.\n"
                "- When high-interest debt is gone, redirect this same amount into investing."
            )

        elif "investing" in goal.lower():
            st.write("**Focus:** start a calm, automatic investing habit.")
            st.markdown(
                f"- Pick a realistic starting amount, e.g. **{currency}{monthly:,.0f} per month**.\n"
                "- Use a simple diversified fund rather than chasing single stocks.\n"
                "- Set a rule: you only review this plan once per quarter, not every market headline.\n"
                "- Track your overall invested balance in Tesorin, not day-to-day price moves."
            )

        elif "specific purchase" in goal.lower():
            st.write("**Focus:** save for a specific purchase without breaking your basics.")
            st.markdown(
                f"- Target amount for this goal: **{currency}{target:,.0f}**.\n"
                f"- With **{currency}{monthly:,.0f} per month**, estimate how many months it would take and compare to your timeframe.\n"
                "- Keep this pot separate from your emergency fund.\n"
                "- If the timeline feels too long, either lower the target or raise the monthly amount once cashflow improves."
            )

        else:
            st.write("**Focus:** get the basics solid before picking a specific goal.")
            st.markdown(
                "- First, make sure your monthly cashflow is positive (Wealthflow tab).\n"
                "- Build at least 1 month of essential expenses as a starter buffer.\n"
                "- Then come back here and pick either emergency fund, debt, or long-term investing as your first focus."
            )

        st.markdown("#### Next 7 days")
        st.markdown(
            "- Write down your current balances: cash, debt, and any investments.\n"
            "- Decide where your emergency buffer or goal savings will live (which account).\n"
            "- If you’re comfortable, set up an automatic monthly transfer for the amount you chose."
        )

        st.markdown("#### Next 30–90 days")
        st.markdown(
            "- Track at least one month of real spending in the Wealthflow tab.\n"
            "- Adjust your monthly goal amount if it feels too tight or too easy.\n"
            "- Revisit this tab in a month to see if your focus still feels right."
        )

        create_clicked = st.button("Add this as a tracked goal")

        if create_clicked:
            name = ns.get("nickname") or goal
            target = ns.get("target_amount", 0.0)
            if target == 0 and "emergency fund" in goal.lower():
                target = float(e_target)

            monthly_target = monthly
            existing = next(
                (g for g in ss.goal_plans if g["name"] == name), None
            )
            if existing:
                existing.update(
                    {
                        "target": target,
                        "monthly_target": monthly_target,
                        "timeframe": ns["timeframe"],
                        "why": ns["why"],
                        "kind": goal,
                    }
                )
                st.success(f"Updated tracked goal: {name}")
            else:
                new_goal = {
                    "id": f"g{len(ss.goal_plans)+1}",
                    "name": name,
                    "kind": goal,
                    "target": target,
                    "saved": 0.0,
                    "monthly_target": monthly_target,
                    "timeframe": ns["timeframe"],
                    "why": ns["why"],
                }
                ss.goal_plans.append(new_goal)
                if name not in ss.profile["goals"]:
                    ss.profile["goals"].append(name)
                st.success(f"Added new tracked goal: {name}")

    if ss.goal_plans:
        st.markdown("### Track progress on your goals")

        emergency_goal = next(
            (
                g
                for g in ss.goal_plans
                if "emergency" in g.get("name", "").lower()
                or "emergency" in g.get("kind", "").lower()
            ),
            None,
        )

        if emergency_goal:
            st.markdown("#### Emergency fund")

            target = emergency_goal.get("target", 0.0) or 0.0
            saved = emergency_goal.get("saved", 0.0) or 0.0
            if target > 0:
                pct = int(min(100, max(0, saved / target * 100)))
                caption_text = (
                    f"{currency}{saved:,.0f} / {currency}{target:,.0f} "
                    f"({pct}% complete)"
                )
            else:
                pct = 0
            caption_text = f"{currency}{saved:,.0f} saved so far"

            st.caption(caption_text)
            st.progress(pct)

            add_em = st.number_input(
                f"Add amount to Emergency fund ({currency})",
                min_value=0.0,
                step=100.0,
                key="goal_add_emergency",
            )
            if st.button("Add to Emergency fund", key="goal_btn_emergency"):
                emergency_goal["saved"] += float(add_em)
                st.success("Emergency fund updated.")

            st.markdown("---")

        st.markdown("#### Other goals")

        for idx, goal in enumerate(ss.goal_plans):
            if emergency_goal is not None and goal is emergency_goal:
                continue

            target = goal.get("target", 0.0) or 0.0
            saved = goal.get("saved", 0.0) or 0.0
            if target > 0:
                pct = int(min(100, max(0, saved / target * 100)))
            else:
                pct = 0

            st.caption(
                f"**{goal['name']}** — {currency}{saved:,.0f}"
                + (
                    f" / {currency}{target:,.0f} ({pct}% complete)"
                    if target > 0
                    else ""
                )
            )
            st.progress(pct)

            add_amount = st.number_input(
                f"Add amount to '{goal['name']}' ({currency})",
                min_value=0.0,
                step=100.0,
                key=f"goal_add_{idx}",
            )
            if st.button("Add", key=f"goal_btn_{idx}"):
                goal["saved"] += float(add_amount)
                st.success("Goal updated.")
