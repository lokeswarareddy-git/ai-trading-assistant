import streamlit as st
import requests
import time

API_URL = "https://ai-trading-assistant-2ji8.onrender.com"

st.set_page_config(page_title="Trading Journal AI", layout="wide")

st.title("📈 AI Trading Assistant")
st.caption("Track trades. Learn patterns. Improve discipline.")

# ------------------------
# AUTH STATE
# ------------------------
if "user_id" not in st.session_state:
    st.session_state.user_id = None

if "email" not in st.session_state:
    st.session_state.email = None

# ------------------------
# MENU
# ------------------------
menu = st.sidebar.selectbox(
    "Menu",
    ["Login", "Add Trade", "View Trades", "Dashboard"]
)

# ------------------------
# CACHE
# ------------------------
def get_cached_data(key, url, ttl=20):
    now = time.time()

    if "api_cache" not in st.session_state:
        st.session_state.api_cache = {}

    cache = st.session_state.api_cache

    if key in cache:
        data, ts = cache[key]
        if now - ts < ttl:
            return data

    try:
        res = requests.get(url, timeout=10)

        if res.status_code == 200:
            data = res.json()
        else:
            data = [] if key == "trades" else {}

    except:
        data = [] if key == "trades" else {}

    cache[key] = (data, now)
    return data


# =========================================================
# LOGIN
# =========================================================
if menu == "Login":

    st.header("🔐 Login")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        res = requests.post(f"{API_URL}/login", json={
            "email": email,
            "password": password
        })

        if res.status_code == 200:
            data = res.json()
            st.session_state.user_id = data["user_id"]
            st.session_state.email = data["email"]
            st.success("Login successful")
            st.rerun()
        else:
            st.error(res.text)

# ------------------------
# AUTH GUARD
# ------------------------
if menu != "Login" and not st.session_state.user_id:
    st.warning("Please login first")
    st.stop()


# =========================================================
# 🧠 AI INSIGHTS ENGINE (FRONTEND LOGIC)
# =========================================================
def generate_insights(trades):
    if not trades:
        return ["No trades to analyze"]

    insights = []

    closed = [t for t in trades if t.get("status") == "CLOSED"]
    open_trades = [t for t in trades if t.get("status") == "OPEN"]

    pnl = sum(t.get("pnl") or 0 for t in closed)

    wins = len([t for t in closed if (t.get("pnl") or 0) > 0])
    losses = len([t for t in closed if (t.get("pnl") or 0) <= 0])

    win_rate = (wins / len(closed) * 100) if closed else 0

    # ------------------------
    # CORE INSIGHTS
    # ------------------------
    if win_rate < 40:
        insights.append("⚠️ Low win rate — you may be overtrading or entering low-quality setups")

    if pnl < 0:
        insights.append("📉 Negative PnL — focus on capital preservation first")

    if len(open_trades) > 5:
        insights.append("⚠️ Too many open trades — risk exposure is high")

    if win_rate > 55 and pnl > 0:
        insights.append("🔥 Strong strategy detected — consider scaling gradually")

    # strategy clustering
    strategies = {}
    for t in closed:
        s = t.get("strategy", "Unknown")
        strategies[s] = strategies.get(s, 0) + (t.get("pnl") or 0)

    if strategies:
        best = max(strategies, key=strategies.get)
        worst = min(strategies, key=strategies.get)

        insights.append(f"🏆 Best strategy: {best}")
        insights.append(f"❌ Weak strategy: {worst}")

    return insights


# =========================================================
# ➕ ADD TRADE
# =========================================================
if menu == "Add Trade":

    st.header("➕ Add Trade")

    with st.form("trade_form", clear_on_submit=True):

        symbol = st.text_input("Symbol")
        side = st.selectbox("Side", ["BUY", "SELL"])

        col1, col2 = st.columns(2)

        with col1:
            entry = st.number_input("Entry Price", min_value=0.0)

        with col2:
            exit_price = st.number_input("Exit Price", min_value=0.0)

        qty = st.number_input("Quantity", min_value=1)

        strategy = st.selectbox(
            "Strategy",
            ["Scalping", "Day Trade", "Swing", "Breakout", "Reversal"]
        )

        notes = st.text_area("Notes")

        submit = st.form_submit_button("Submit")

    if submit:

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
            res = requests.post(
                f"{API_URL}/trade",
                params={"user_id": st.session_state.user_id},
                json=payload
            )

            if res.status_code == 200:
                st.success("Trade added")
            else:
                st.error(res.text)

        except Exception as e:
            st.error(str(e))


# =========================================================
# 📊 VIEW TRADES
# =========================================================
if menu == "View Trades":

    st.header("📊 Trades")

    data = get_cached_data(
        "trades",
        f"{API_URL}/trades?user_id={st.session_state.user_id}"
    )

    if not data:
        st.info("No trades yet")
        st.stop()

    open_trades = [t for t in data if t.get("status") == "OPEN"]
    closed_trades = [t for t in data if t.get("status") == "CLOSED"]

    st.metric("Total Trades", len(data))
    st.metric("Open", len(open_trades))
    st.metric("Closed", len(closed_trades))

    st.divider()

    st.subheader("Open Trades")
    st.dataframe(open_trades)

    st.subheader("Closed Trades")
    st.dataframe(closed_trades)


# =========================================================
# 🧠 DASHBOARD + AI INSIGHTS
# =========================================================
if menu == "Dashboard":

    st.header("📊 AI Dashboard")

    data = get_cached_data(
        "trades",
        f"{API_URL}/trades?user_id={st.session_state.user_id}"
    )

    stats = get_cached_data(
        "stats",
        f"{API_URL}/stats?user_id={st.session_state.user_id}"
    )

    if not data:
        st.info("No trades yet")
        st.stop()

    pnl = stats.get("total_pnl", 0)
    win_rate = stats.get("win_rate", 0)

    # ------------------------
    # KPI
    # ------------------------
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("PnL", f"${pnl:.2f}")

    with col2:
        st.metric("Win Rate", f"{win_rate:.2f}%")

    with col3:
        st.metric("Trades", len(data))

    st.divider()

    # ------------------------
    # AI INSIGHTS SECTION
    # ------------------------
    st.subheader("🧠 AI Insights")

    insights = generate_insights(data)

    for i in insights:
        st.info(i)

    st.divider()

    # ------------------------
    # PERFORMANCE INTERPRETATION
    # ------------------------
    st.subheader("📈 What this means")

    if win_rate < 40:
        st.warning("Your system is not stable yet — reduce trade frequency and refine entries")

    elif pnl > 0 and win_rate > 55:
        st.success("You have a working edge — focus on scaling and consistency")

    else:
        st.info("You are in development phase — focus on discipline and journaling quality")