import streamlit as st
import requests

API_URL = "https://ai-trading-assistant-2ji8.onrender.com"

st.set_page_config(page_title="Trading Journal", layout="wide")

st.title("📈 AI Trading Assistant")

menu = st.sidebar.selectbox("Menu", ["Add Trade", "View Trades"])

# ------------------------
# ➕ ADD TRADE (FORM ALWAYS VISIBLE WHEN SELECTED)
# ------------------------
if menu == "Add Trade":

    st.header("Add Trade")

    # ✅ FORM MUST WRAP EVERYTHING
    with st.form("trade_form"):

        side = st.selectbox("Side", ["BUY", "SELL"])
        submit = st.form_submit_button("Submit Trade")

        # ⚠️ Inputs must be OUTSIDE submit condition
        entry = st.number_input("Entry Price", value=0.0)
        exit = st.number_input("Exit Price", value=0.0)
        qty = st.number_input("Quantity", value=1, step=1)
        notes = st.text_area("Notes")

        if submit:
            payload = {
                "side": side,
                "entry_price": entry,
                "exit_price": exit,
                "quantity": qty,
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