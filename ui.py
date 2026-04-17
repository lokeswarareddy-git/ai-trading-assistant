import streamlit as st
import requests
import time

API_URL = "https://ai-trading-assistant-2ji8.onrender.com"

st.set_page_config(page_title="Trading Journal", layout="wide")

st.title("📈 AI Trading Assistant")
st.caption("Track trades. Improve discipline. Build consistency.")

# ------------------------
# 🔐 AUTH STATE
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
# LOGOUT
# ------------------------
if st.session_state.user_id:
    st.sidebar.success(f"Logged in: {st.session_state.email}")

    if st.sidebar.button("Logout"):
        st.session_state.user_id = None
        st.session_state.email = None
        st.rerun()


# ------------------------
# CACHE HELPER
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

        elif res.status_code == 429:
            time.sleep(2)
            return cache.get(key, ([], now))[0]

        else:
            data = [] if key == "trades" else {}

    except:
        data = [] if key == "trades" else {}

    cache[key] = (data, now)
    return data


# =========================================================
# 🔐 LOGIN / SIGNUP (IMPROVED)
# =========================================================
if menu == "Login":

    st.header("🔐 Account Access")

    tab1, tab2 = st.tabs(["Login", "Signup"])

    # ------------------------
    # LOGIN
    # ------------------------
    with tab1:

        email_login = st.text_input("Email", key="login_email")
        password_login = st.text_input("Password", type="password", key="login_pass")

        if st.button("Login"):

            if not email_login or not password_login:
                st.warning("Please fill all fields")
            else:
                res = requests.post(
                    f"{API_URL}/login",
                    json={"email": email_login, "password": password_login}
                )

                if res.status_code == 200:
                    data = res.json()

                    st.session_state.user_id = data["user_id"]
                    st.session_state.email = email_login
                    st.session_state.logged_in = True

                    st.success(f"Welcome {email_login} 🚀")
                    st.rerun()
                else:
                    st.error("Invalid credentials")

    # ------------------------
    # SIGNUP
    # ------------------------
    with tab2:

        email_signup = st.text_input("Email", key="signup_email")
        password_signup = st.text_input("Password", type="password", key="signup_pass")

        if st.button("Signup"):

            if not email_signup or not password_signup:
                st.warning("Please fill all fields")
            else:
                res = requests.post(
                    f"{API_URL}/signup",
                    json={"email": email_signup, "password": password_signup}
                )

                if res.status_code == 200:
                    st.success("Signup successful. Please login.")
                else:
                    st.error(res.text)
# =========================================================
# 🚨 AUTH GUARD
# =========================================================
if menu != "Login" and not st.session_state.user_id:
    st.warning("Please login first")
    st.stop()


# =========================================================
# ➕ ADD TRADE
# =========================================================
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

        notes = st.text_area("Trade Reasoning")

        submit = st.form_submit_button("Submit Trade")

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

        if "last_trade" not in st.session_state:
            st.session_state.last_trade = None

        if st.session_state.last_trade == payload:
            st.warning("Duplicate trade prevented")
            st.stop()

        st.session_state.last_trade = payload

        try:
            with st.spinner("Submitting trade..."):
                res = requests.post(
                    f"{API_URL}/trade",
                    params={"user_id": st.session_state.user_id},
                    json=payload,
                    timeout=10
                )

            if res.status_code == 200:
                st.success("Trade added successfully")
                st.json(res.json())

            else:
                st.error(res.text)

        except Exception as e:
            st.error(str(e))


# =========================================================
# 📊 VIEW TRADES
# =========================================================
if menu == "View Trades":

    st.header("📊 Trades Overview")

    if "toast" in st.session_state:
        st.success(st.session_state.toast)
        st.session_state.toast = None

    data = get_cached_data(
        "trades",
        f"{API_URL}/trades?user_id={st.session_state.user_id}",
        ttl=20
    )

    if not data:
        st.info("No trades yet 🚀")
        st.stop()

    open_trades = [t for t in data if t.get("status") == "OPEN"]
    closed_trades = [t for t in data if t.get("status") == "CLOSED"]

    st.metric("Total Trades", len(data))
    st.metric("Open", len(open_trades))
    st.metric("Closed", len(closed_trades))

    st.divider()

    st.subheader("🟡 Open Trades")
    st.dataframe(open_trades, use_container_width=True)

    trade_ids = [t["id"] for t in open_trades]

    if trade_ids:

        selected_id = st.selectbox("Select Trade", trade_ids)

        trade = next(t for t in open_trades if t["id"] == selected_id)

        notes = st.text_area("Notes", trade.get("notes") or "")
        strategy = st.text_input("Strategy", trade.get("strategy") or "")
        entry = st.number_input("Entry", value=float(trade.get("entry_price") or 0))
        qty = st.number_input("Qty", value=int(trade.get("quantity") or 1))

        if st.button("Update Trade"):

            res = requests.put(
                f"{API_URL}/trade/{selected_id}",
                json={
                    "notes": notes,
                    "strategy": strategy,
                    "entry_price": entry,
                    "quantity": qty
                }
            )

            if res.status_code == 200:
                st.session_state.toast = "Trade updated"
                st.rerun()

        exit_price = st.number_input("Exit Price", value=0.0)

        if st.button("Close Trade"):

            res = requests.post(
                f"{API_URL}/trade/{selected_id}/close",
                json={"exit_price": exit_price}
            )

            if res.status_code == 200:
                st.session_state.toast = "Trade closed"
                st.rerun()

    st.divider()

    st.subheader("🟢 Closed Trades")
    st.dataframe(closed_trades, use_container_width=True)


# =========================================================
# 📊 DASHBOARD
# =========================================================
if menu == "Dashboard":

    st.header("📊 Trading Dashboard")

    stats = get_cached_data("stats", f"{API_URL}/stats?user_id={st.session_state.user_id}")

    if not stats:
        st.info("No stats available")
        st.stop()

    pnl = stats.get("total_pnl", 0)
    win_rate = stats.get("win_rate", 0)

    st.metric("PnL", pnl)
    st.metric("Win Rate", f"{win_rate}%")

    st.metric("Total Trades", stats.get("total_trades", 0))