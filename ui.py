import streamlit as st
import requests

API_URL = "https://ai-trading-assistant-2ji8.onrender.com"

st.set_page_config(page_title="Trading Journal", layout="wide")

st.title("📈 AI Trading Assistant")

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
        exit = st.number_input("Exit Price", min_value=0.0, step=0.01)

        qty = st.number_input("Quantity", min_value=1, step=1)

        strategy = st.text_input("Strategy (optional)")
        notes = st.text_area("Notes")

        submit = st.form_submit_button("Submit Trade")

        if submit:

            if not symbol:
                st.error("Symbol is required")
            else:
                payload = {
                    "symbol": symbol,
                    "side": side,
                    "entry_price": entry,
                    "exit_price": exit,
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
# 📊 VIEW TRADES
# ------------------------
if menu == "View Trades":
    st.header("Trades")

    if st.button("Load Trades"):
        with st.spinner("Loading trades..."):
            try:
                res = requests.get(f"{API_URL}/trades", timeout=10)

                if res.status_code == 200:
                    data = res.json()

                    if data:
                        st.dataframe(data)
                        st.write(f"Total Trades: {len(data)}")
                    else:
                        st.info("No trades found")

                else:
                    st.error(f"Failed to load trades (Status: {res.status_code})")

            except requests.exceptions.Timeout:
                st.error("Request timed out. Backend may be waking up (Render free tier).")

            except requests.exceptions.ConnectionError:
                st.error("Unable to connect to backend. Check API URL.")

            except Exception as e:
                st.error(f"Unexpected error: {str(e)}")
# ------------------------
# 📊 DASHBOARD (STATS)
# ------------------------
if menu == "Dashboard":

    st.header("📊 Trading Performance Dashboard")

    res = requests.get(f"{API_URL}/stats")

    if res.status_code == 200:
        stats = res.json()

        # --- KPI CARDS ---
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total Trades", stats["total_trades"])

        with col2:
            st.metric("Win Rate %", f"{stats['win_rate']}%")

        with col3:
            st.metric("Winning Trades", stats["winning_trades"])

        with col4:
            st.metric("Losing Trades", stats["losing_trades"])

        st.divider()

        # --- PnL SECTION ---
        pnl = stats["total_pnl"]

        if pnl >= 0:
            st.success(f"💰 Total PnL: +{pnl}")
        else:
            st.error(f"💸 Total PnL: {pnl}")

        # --- SIMPLE INSIGHT ---
        st.subheader("🧠 Insight")

        if stats["win_rate"] < 40:
            st.warning("⚠️ Low win rate — review your strategy discipline")

        elif pnl > 0:
            st.success("🔥 You are profitable — keep scaling your edge")

        else:
            st.info("📉 Focus on reducing losses first")

    else:
        st.error("Failed to load stats")