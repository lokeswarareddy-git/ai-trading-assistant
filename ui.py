import streamlit as st
import requests
import time

API_URL = "https://ai-trading-assistant-2ji8.onrender.com"

st.set_page_config(page_title="Trading Journal", layout="wide")

st.title("📈 AI Trading Assistant")
st.caption("Track trades. Improve discipline. Build consistency.")

menu = st.sidebar.selectbox("Menu", ["Add Trade", "View Trades", "Dashboard"])

def get_cached_data(key, url, ttl=20):
    now = time.time()

    if "api_cache" not in st.session_state:
        st.session_state.api_cache = {}

    cache = st.session_state.api_cache

    # return cached
    if key in cache:
        data, ts = cache[key]
        if now - ts < ttl:
            return data

    # fetch fresh
    try:
        res = requests.get(url, timeout=10)
        if res.status_code == 200:
            data = res.json()

        elif res.status_code == 429:
            # IMPORTANT: avoid hammering backend
            time.sleep(2)
            return cache.get(key, ([], now))[0]

        else:
            data = [] if key == "trades" else {}
    except:
        data = [] if key == "trades" else {}

    cache[key] = (data, now)
    return data



# ------------------------
# ➕ ADD TRADE
# ------------------------
if menu == "Add Trade":

    st.header("➕ Add Trade")

    with st.form("trade_form", clear_on_submit=True):

        symbol = st.text_input("Symbol (e.g. AAPL)")
        side = st.selectbox("Side", ["BUY", "SELL"])

        col1, col2 = st.columns(2)

        with col1:
            entry = st.number_input("Entry Price", min_value=0.0, step=0.01)

        with col2:
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

    # ------------------------
    # OUTSIDE FORM (IMPORTANT FIX)
    # prevents double execution on rerun
    # ------------------------
    if submit:

        if not symbol:
            st.error("Symbol is required")
            st.stop()

        payload = {
            "symbol": symbol,
            "side": side,
            "entry_price": entry,
            "exit_price": exit_price if exit_price > 0 else None,
            "quantity": qty,
            "strategy": strategy,
            "notes": notes
        }

        # ------------------------
        # ANTI-DUPLICATE GUARD
        # ------------------------
        if "last_trade" not in st.session_state:
            st.session_state.last_trade = None

        if st.session_state.last_trade == payload:
            st.warning("⚠️ Duplicate trade prevented")
            st.stop()

        st.session_state.last_trade = payload

        # ------------------------
        # SAFE API CALL
        # ------------------------
        try:
            with st.spinner("Submitting trade..."):
                res = requests.post(
                    f"{API_URL}/trade",
                    json=payload,
                    timeout=10
                )

            if res.status_code == 200:
                st.success("✅ Trade added successfully!")
                st.json(res.json())

            elif res.status_code == 429:
                st.error("⚠️ Too many requests. Please wait 10–20 seconds.")

            else:
                st.error(f"❌ Error: {res.text}")

        except requests.exceptions.Timeout:
            st.error("⏳ Server timeout. Try again.")

        except requests.exceptions.ConnectionError:
            st.error("❌ Backend not reachable.")

        except Exception as e:
            st.error(f"Unexpected error: {str(e)}")

# ------------------------
# 📊 VIEW TRADES (CACHED + IMPROVED)
# ------------------------
if menu == "View Trades":

    st.header("📊 Trades Overview")

    # ------------------------
    # LOAD DATA (WITH CACHE)
    # ------------------------
    data = get_cached_data(
        key="trades",
        url=f"{API_URL}/trades",
        ttl=20
    )

    # ------------------------
    # HANDLE LOADING STATE
    # ------------------------
    if data is None:
        st.warning("⏳ Loading trades...")
        st.stop()

    if not data:
        st.info("No trades yet. Start adding trades 🚀")
        st.stop()

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
    # SUMMARY SECTION
    # ------------------------
    st.markdown("### 📊 Quick Overview")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Trades", len(data))

    with col2:
        st.metric("Open Positions", len(open_trades))

    with col3:
        st.metric("Closed Trades", len(closed_trades))

    st.divider()

    # ------------------------
    # 🟡 OPEN POSITIONS
    # ------------------------
    st.markdown("### 🟡 Open Positions")

    if open_trades:
        st.dataframe(
            open_trades,
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No open positions")

    st.divider()

    # ------------------------
    # 🟢 CLOSED TRADES
    # ------------------------
    st.markdown("### 🟢 Trade History")

    if closed_trades:
        st.dataframe(
            closed_trades,
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No closed trades yet")


# ------------------------
# 📊 DASHBOARD (STABLE + CACHED)
# ------------------------
if menu == "Dashboard":

    st.header("📊 Trading Dashboard")

    # ------------------------
    # GET DATA (CACHED)
    # ------------------------
    stats = get_cached_data("stats", f"{API_URL}/stats")

    # ------------------------
    # HANDLE EMPTY / FAIL STATE
    # ------------------------
    if not stats or not isinstance(stats, dict):
        st.error("❌ Failed to load stats. Please try again.")
        st.stop()

    total_trades = stats.get("total_trades", 0)

    # ------------------------
    # EMPTY STATE
    # ------------------------
    if total_trades == 0:
        st.info("No trades yet. Start logging to build your performance analytics 📈")
        st.stop()

    pnl = stats.get("total_pnl", 0)
    win_rate = stats.get("win_rate", 0)

    # ------------------------
    # HEADER SUMMARY STRIP
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
    # KPI CARDS
    # ------------------------
    st.markdown("### 📊 Key Performance Metrics")

    k1, k2, k3, k4 = st.columns(4)

    with k1:
        st.metric("Total Trades", total_trades)

    with k2:
        st.metric("Winning Trades", stats.get("winning_trades", 0))

    with k3:
        st.metric("Losing Trades", stats.get("losing_trades", 0))

    with k4:
        avg_pnl = pnl / total_trades if total_trades else 0
        st.metric("Avg PnL / Trade", f"${avg_pnl:.2f}")

    st.divider()

    # ------------------------
    # PERFORMANCE INSIGHTS
    # ------------------------
    st.markdown("### 🧠 Performance Intelligence")

    col1, col2 = st.columns([2, 1])

    with col1:

        if win_rate < 40:
            st.warning("""
            ⚠️ Weak Win Rate Detected

            - Review entry strategy
            - Avoid emotional trading
            - Focus on high-quality setups
            """)

        elif pnl > 0 and win_rate > 55:
            st.success("""
            🔥 Strong Trading Edge

            - Consistent profitability
            - Good discipline
            - Scale gradually
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

    with col2:
        st.markdown("#### 🧾 Quick Stats")

        st.write(f"Trades: **{total_trades}**")
        st.write(f"Win Rate: **{win_rate:.2f}%**")
        st.write(f"PnL: **${pnl:.2f}**")