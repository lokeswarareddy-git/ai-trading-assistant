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