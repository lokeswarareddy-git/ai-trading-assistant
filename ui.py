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

    with st.form("trade_form"):   # ✅ IMPORTANT FIX
        side = st.selectbox("Side", ["BUY", "SELL"])
        submit = st.form_submit_button("Submit Trade")

        if submit:
            payload = {
                "side": side
            }

            res = requests.post(f"{API_URL}/trade", json=payload)

            if res.status_code == 200:
                st.success("Trade added!")
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