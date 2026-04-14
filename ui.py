import streamlit as st
import requests

API_URL = "https://ai-trading-assistant-2ji8.onrender.com"

st.set_page_config(page_title="Trading Journal", layout="wide")

st.title("📈 AI Trading Assistant")

menu = st.sidebar.selectbox("Menu", ["Add Trade", "View Trades"])

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
        res = requests.get(f"{API_URL}/trades")

        if res.status_code == 200:
            st.dataframe(res.json())
        else:
            st.error("Failed to load trades")