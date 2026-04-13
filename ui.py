import streamlit as st
import requests
API_URL = "https://ai-trading-assistant-2ji8.onrender.com/"
st.set_page_config(page_title="Trading Journal", layout="wide")

st.title("📈 AI Trading Assistant")

# ------------------------
# ➕ ADD TRADE SECTION
# ------------------------
st.header("Add Trade")

symbol = st.text_input("Symbol")
entry = st.number_input("Entry Price")
exit = st.number_input("Exit Price")
qty = st.number_input("Quantity", step=1)
strategy = st.text_input("Strategy")
notes = st.text_area("Notes")

if st.button("Submit Trade"):
    payload = {
        "symbol": symbol,
        "entry_price": entry,
        "exit_price": exit,
        "quantity": qty,
        "strategy": strategy,
        "notes": notes
    }

    res = requests.post(f"{API_URL}/trade", json=payload)
    st.write("STATUS:", res.status_code)
    st.write("RESPONSE:", res.text)
    if res.status_code == 200:
        st.success("Trade added successfully!")
        st.json(res.json())
    else:
        st.error("Failed to add trade")

# ------------------------
# 📊 VIEW TRADES
# ------------------------
st.header("All Trades")

if st.button("Load Trades"):
    res = requests.get(f"{API_URL}/trades")

    if res.status_code == 200:
        trades = res.json()
        st.dataframe(trades)
    else:
        st.error("Failed to fetch trades")