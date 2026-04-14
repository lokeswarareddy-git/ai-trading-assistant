import streamlit as st
import requests

API_URL = "https://ai-trading-assistant-2ji8.onrender.com"
st.cache_data.clear()
def safe_get(url, fallback):
    try:
        res = requests.get(url, timeout=10)

        if res.status_code == 200:
            return res.json()

        return fallback

    except:
        return fallback

st.set_page_config(page_title="Trading Journal", layout="wide")

st.title("📈 AI Trading Assistant")
st.caption("Track trades. Improve discipline. Build consistency.")

menu = st.sidebar.selectbox("Menu", ["Add Trade", "View Trades", "Dashboard"])

# ------------------------
# ➕ ADD TRADE
# ------------------------
if menu == "Add Trade":

    st.header("Add Trade")

    with st.form("trade_form"):

        symbol = st.text_input("Symbol (e.g. AAPL)")
        side = st.selectbox("Side", ["BUY", "SELL"])

        entry = st.number_input("Entry Price", min_value=0.0, step=0.01)
        exit = st.number_input("Exit Price (optional)", min_value=0.0, step=0.01)

        qty = st.number_input("Quantity", min_value=1, step=1)

        # strategy = st.text_input("Strategy (optional)")
        # notes = st.text_area("Notes")
        st.markdown("### 🧠 Trade Context")

        strategy = st.selectbox(
            "Strategy Tag",
            ["Scalping", "Day Trade", "Swing", "Breakout", "Reversal", "Other"]
        )

        notes = st.text_area(
            "Trade Reasoning",
            placeholder="Why did you take this trade? (setup, signal, emotion, news, etc.)"
        )
        submit = st.form_submit_button("Submit Trade")

        if submit:

            if not symbol:
                st.error("Symbol is required")
            else:
                payload = {
                    "symbol": symbol,
                    "side": side,
                    "entry_price": entry,
                    "exit_price": exit if exit > 0 else None,
                    "quantity": qty,
                    "strategy": strategy,
                    "notes": notes
                }

                res = requests.post(f"{API_URL}/trade", json=payload)

                if res.status_code == 200:
                    st.success("Trade added successfully!")
                    st.json(res.json())
                else:
                    st.error(res.text)

# ------------------------
# 📊 VIEW TRADES (IMPROVED)
# ------------------------
if menu == "View Trades":
    st.header("📊 Trades Overview")

    # ------------------------
    # SAFE SINGLE FETCH (prevents 429 spam)
    # ------------------------
    @st.cache_data(ttl=10)
    def get_trades():
        try:
            res = requests.get(f"{API_URL}/trades", timeout=10)

            if res.status_code == 200:
                return res.json()

            return []

        except:
            return []

    if st.button("🔄 Refresh Trades"):
        with st.spinner("Loading trades..."):

            data = get_trades()

            # ------------------------
            # EMPTY STATE
            # ------------------------
            if not data:
                st.info("No trades yet. Start adding trades 🚀")
                st.stop()

            # ------------------------
            # SPLIT DATA
            # ------------------------
            open_trades = [t for t in data if t.get("status") == "OPEN"]
            closed_trades = [t for t in data if t.get("status") == "CLOSED"]

            # ------------------------
            # SUMMARY METRICS
            # ------------------------
            st.markdown("### 📊 Quick Overview")

            c1, c2, c3 = st.columns(3)

            with c1:
                st.metric("Total Trades", len(data))

            with c2:
                st.metric("Open Positions", len(open_trades))

            with c3:
                st.metric("Closed Trades", len(closed_trades))

            st.divider()

            # ------------------------
            # 🟡 OPEN POSITIONS
            # ------------------------
            st.markdown("### 🟡 Open Positions")

            if open_trades:
                for t in open_trades:
                    t["status"] = "🟡 OPEN"

                st.dataframe(open_trades, use_container_width=True, hide_index=True)
            else:
                st.info("No open positions")

            st.divider()

            # ------------------------
            # 🟢 CLOSED TRADES
            # ------------------------
            st.markdown("### 🟢 Trade History")

            if closed_trades:
                for t in closed_trades:
                    t["status"] = "🟢 CLOSED"

                st.dataframe(closed_trades, use_container_width=True, hide_index=True)
            else:
                st.info("No closed trades yet")

    else:
        st.info("Click 'Refresh Trades' to load data")
# 📊 DASHBOARD (PREMIUM FINTECH UI)
# ------------------------
if menu == "Dashboard":

    st.header("📊 Trading Dashboard")

    res = requests.get(f"{API_URL}/stats")

    if res.status_code == 200:
        stats = res.json()

        # ------------------------
        # EMPTY STATE
        # ------------------------
        if stats["total_trades"] == 0:
            st.info("No trades yet. Start logging to build your performance analytics 📈")
            st.stop()

        # ------------------------
        # HEADER SUMMARY STRIP
        # ------------------------
        pnl = stats["total_pnl"]
        win_rate = stats["win_rate"]

        colA, colB, colC = st.columns([1, 1, 2])

        with colA:
            if pnl >= 0:
                st.success(f"💰 PnL: +${pnl:.2f}")
            else:
                st.error(f"💰 PnL: ${pnl:.2f}")

        with colB:
            st.metric("Win Rate", f"{win_rate:.2f}%")

        with colC:
            if win_rate > 50 and pnl > 0:
                st.success("🟢 Strong Edge Detected")
            elif win_rate < 40:
                st.warning("🟡 Performance Needs Review")
            else:
                st.info("🔵 Stable / Neutral Performance")

        st.divider()

        # ------------------------
        # KPI CARDS (FINTECH STYLE)
        # ------------------------
        st.markdown("### 📊 Key Performance Metrics")

        k1, k2, k3, k4 = st.columns(4)

        with k1:
            st.metric("Total Trades", stats["total_trades"])

        with k2:
            st.metric("Winning Trades", stats["winning_trades"])

        with k3:
            st.metric("Losing Trades", stats["losing_trades"])

        with k4:
            avg_pnl = pnl / stats["total_trades"] if stats["total_trades"] else 0
            st.metric("Avg PnL / Trade", f"${avg_pnl:.2f}")

        st.divider()

        # ------------------------
        # PERFORMANCE INSIGHT PANEL
        # ------------------------
        st.markdown("### 🧠 Performance Intelligence")

        insight_col1, insight_col2 = st.columns([2, 1])

        with insight_col1:

            if win_rate < 40:
                st.warning("""
                ⚠️ Weak Win Rate Detected

                - Review entry strategy
                - Avoid emotional trades
                - Focus on high-quality setups
                """)

            elif pnl > 0 and win_rate > 55:
                st.success("""
                🔥 Strong Trading Edge

                - Consistent profitability
                - Good discipline
                - Keep scaling position sizing carefully
                """)

            elif pnl > 0:
                st.info("""
                👍 Profitable but inconsistent

                - Improve trade selection
                - Focus on win rate improvement
                """)

            else:
                st.info("""
                📉 Early Stage Performance

                - Focus on capital preservation
                - Reduce losses first
                """)

        with insight_col2:
            st.markdown("#### 🧾 Quick Stats")

            st.write(f"Trades: **{stats['total_trades']}**")
            st.write(f"Win Rate: **{win_rate:.2f}%**")
            st.write(f"PnL: **${pnl:.2f}**")

    else:
        st.error("Failed to load stats")