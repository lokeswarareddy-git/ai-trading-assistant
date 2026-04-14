import streamlit as st
import requests

API_URL = "https://ai-trading-assistant-2ji8.onrender.com"

st.set_page_config(page_title="Trading Journal", layout="wide")

st.title("📈 AI Trading Assistant")
st.caption("Track trades. Improve discipline. Build consistency.")

menu = st.sidebar.selectbox("Menu", ["Add Trade", "View Trades", "Dashboard"])


# =========================================================
# 🚀 CACHED API CALLS (IMPORTANT FIX FOR 429 ISSUE)
# =========================================================
@st.cache_data(ttl=10)
def get_trades():
    return requests.get(f"{API_URL}/trades", timeout=10).json()


@st.cache_data(ttl=10)
def get_stats():
    return requests.get(f"{API_URL}/stats", timeout=10).json()


# =========================================================
# ➕ ADD TRADE
# =========================================================
if menu == "Add Trade":

    st.header("Add Trade")

    with st.form("trade_form"):

        symbol = st.text_input("Symbol (e.g. AAPL)")
        side = st.selectbox("Side", ["BUY", "SELL"])

        entry = st.number_input("Entry Price", min_value=0.0, step=0.01)
        exit_price = st.number_input("Exit Price (optional)", min_value=0.0, step=0.01)

        qty = st.number_input("Quantity", min_value=1, step=1)

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
                    "exit_price": exit_price if exit_price > 0 else None,
                    "quantity": qty,
                    "strategy": strategy,
                    "notes": notes
                }

                try:
                    res = requests.post(f"{API_URL}/trade", json=payload, timeout=10)

                    if res.status_code == 200:
                        st.success("Trade added successfully!")
                        st.cache_data.clear()  # 🔥 refresh cache after submit
                    else:
                        st.error(res.text)

                except Exception as e:
                    st.error(f"Error: {str(e)}")


# =========================================================
# 📊 VIEW TRADES
# =========================================================
if menu == "View Trades":

    st.header("📊 Trades Overview")

    try:
        data = get_trades()

        if not data:
            st.info("No trades yet. Start adding trades 🚀")
            st.stop()

        open_trades = [t for t in data if t.get("status") == "OPEN"]
        closed_trades = [t for t in data if t.get("status") == "CLOSED"]

        # ------------------------
        # SUMMARY
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
        # OPEN TRADES
        # ------------------------
        st.markdown("### 🟡 Open Positions")

        if open_trades:
            st.dataframe(open_trades, use_container_width=True, hide_index=True)
        else:
            st.info("No open positions")

        st.divider()

        # ------------------------
        # CLOSED TRADES
        # ------------------------
        st.markdown("### 🟢 Trade History")

        if closed_trades:
            st.dataframe(closed_trades, use_container_width=True, hide_index=True)
        else:
            st.info("No closed trades yet")

    except requests.exceptions.Timeout:
        st.error("⏳ Server is waking up. Try again in a few seconds.")

    except requests.exceptions.ConnectionError:
        st.error("❌ Backend not reachable. Check API URL.")

    except Exception as e:
        st.error(f"Unexpected error: {str(e)}")


# =========================================================
# 📊 DASHBOARD
# =========================================================
if menu == "Dashboard":

    st.header("📊 Trading Dashboard")

    try:
        stats = get_stats()

        if not stats or stats.get("total_trades", 0) == 0:
            st.info("No trades yet. Start logging to build your performance analytics 📈")
            st.stop()

        pnl = stats["total_pnl"]
        win_rate = stats["win_rate"]

        # ------------------------
        # HEADER STRIP
        # ------------------------
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
        # KPIs
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
            avg_pnl = pnl / stats["total_trades"]
            st.metric("Avg PnL / Trade", f"${avg_pnl:.2f}")

        st.divider()

        # ------------------------
        # INSIGHTS
        # ------------------------
        st.markdown("### 🧠 Performance Intelligence")

        if win_rate < 40:
            st.warning("""
            ⚠️ Weak Win Rate Detected
            - Review entry strategy
            - Avoid emotional trades
            - Focus on quality setups
            """)

        elif pnl > 0 and win_rate > 55:
            st.success("""
            🔥 Strong Trading Edge
            - Consistent profitability
            - Good discipline
            - Scale carefully
            """)

        elif pnl > 0:
            st.info("""
            👍 Profitable but inconsistent
            - Improve trade selection
            - Increase win rate
            """)

        else:
            st.info("""
            📉 Early Stage Performance
            - Focus on capital preservation
            - Reduce losses first
            """)

        st.markdown("#### 🧾 Quick Stats")

        st.write(f"Trades: **{stats['total_trades']}**")
        st.write(f"Win Rate: **{win_rate:.2f}%**")
        st.write(f"PnL: **${pnl:.2f}**")

    except Exception as e:
        st.error(f"Failed to load stats: {str(e)}")